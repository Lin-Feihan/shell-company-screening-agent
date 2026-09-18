import time

from google import genai

from .base import (
    DeepResearchProvider,
    ResearchResult,
)


def to_plain_dict(value):
    """
    Convert Gemini SDK objects into plain
    Python dictionaries where possible.
    """

    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "to_dict"):
        return value.to_dict()

    return None


def normalize_url_citation(
    annotation,
    step_id=None,
    content_index=None,
):
    """
    Normalize Gemini URL citation annotations
    into a provider-independent dictionary.
    """

    data = (
        to_plain_dict(annotation)
        or {}
    )

    annotation_type = (
        data.get("type")
        or getattr(
            annotation,
            "type",
            None
        )
    )

    if (
        annotation_type
        != "url_citation"
    ):
        return None

    url = (
    data.get("url")
    or data.get("uri")
    or getattr(
        annotation,
        "url",
        None
    )
    or getattr(
        annotation,
        "uri",
        None
    )
)

    if not url:
        return None

    return {
        "type": "url_citation",
        "url": url,
        "title": (
            data.get("title")
            or getattr(
                annotation,
                "title",
                None
            )
        ),
        "start_index": (
            data.get("start_index")
            if "start_index" in data
            else getattr(
                annotation,
                "start_index",
                None
            )
        ),
        "end_index": (
            data.get("end_index")
            if "end_index" in data
            else getattr(
                annotation,
                "end_index",
                None
            )
        ),
        "step_id": step_id,
        "content_index":
            content_index,
    }


def deduplicate_sources(
    sources
):
    """
    Deduplicate sources by URL while preserving
    the first non-empty title and origin.
    """

    by_url = {}

    for source in sources:
        if not source:
            continue

        url = source.get(
            "url"
        )

        if not url:
            continue

        if url not in by_url:
            by_url[url] = (
                source.copy()
            )
            continue

        existing = by_url[
            url
        ]

        if (
            not existing.get("title")
            and source.get("title")
        ):
            existing[
                "title"
            ] = source[
                "title"
            ]

        if (
            not existing.get("origin")
            and source.get("origin")
        ):
            existing[
                "origin"
            ] = source[
                "origin"
            ]

    return list(
        by_url.values()
    )


class GeminiDeepResearchProvider(
    DeepResearchProvider
):

    provider_name = "gemini"

    def run(
        self,
        prompt
    ) -> ResearchResult:

        agent = self.config.get(
            "agent",
            "deep-research-preview-04-2026"
        )

        poll_interval = self.config.get(
            "poll_interval_seconds",
            10
        )

        client = genai.Client(
            api_key=self.api_key
        )

        try:

            print(
                f"Using Gemini agent: "
                f"{agent}"
            )

            interaction = (
                client
                .interactions
                .create(
                    input=prompt,
                    agent=agent,
                    background=True,
                )
            )

            while True:

                interaction = (
                    client
                    .interactions
                    .get(
                        interaction.id
                    )
                )

                if (
                    interaction.status
                    == "completed"
                ):
                    break

                if (
                    interaction.status
                    == "failed"
                ):

                    errors = (
                        getattr(
                            interaction,
                            "errors",
                            None
                        )
                        or getattr(
                            interaction,
                            "error",
                            None
                        )
                    )

                    raise RuntimeError(
                        "Gemini Deep Research "
                        f"failed: {errors}"
                    )

                time.sleep(
                    poll_interval
                )

            report = getattr(
                interaction,
                "output_text",
                None
            )

            steps = (
                getattr(
                    interaction,
                    "steps",
                    []
                )
                or []
            )

            citations = []
            sources = []
            research_steps = []

            # Find the last model-output step.
            # Citations on the final report are
            # attached to its text content blocks.
            final_model_step = None

            for step in steps:

                step_type = getattr(
                    step,
                    "type",
                    None
                )

                research_steps.append(
                    {
                        "type":
                            step_type,
                        "id":
                            getattr(
                                step,
                                "id",
                                None
                            ),
                        "status":
                            getattr(
                                step,
                                "status",
                                None
                            ),
                    }
                )

                if (
                    step_type
                    == "model_output"
                ):
                    final_model_step = (
                        step
                    )

            fallback_text = []

            if final_model_step:

                step_id = getattr(
                    final_model_step,
                    "id",
                    None
                )

                for content_index, content in enumerate(
                    getattr(
                        final_model_step,
                        "content",
                        []
                    )
                    or []
                ):

                    content_type = getattr(
                        content,
                        "type",
                        None
                    )

                    if (
                        content_type
                        != "text"
                    ):
                        continue

                    text = getattr(
                        content,
                        "text",
                        None
                    )

                    if text:
                        fallback_text.append(
                            text
                        )

                    for annotation in (
                        getattr(
                            content,
                            "annotations",
                            []
                        )
                        or []
                    ):

                        citation = (
                            normalize_url_citation(
                                annotation,
                                step_id=(
                                    step_id
                                ),
                                content_index=(
                                    content_index
                                ),
                            )
                        )

                        if citation:
                            citations.append(
                                citation
                            )

                            sources.append(
                                {
                                    "url":
                                        citation[
                                            "url"
                                        ],
                                    "title":
                                        citation.get(
                                            "title"
                                        ),
                                    "origin":
                                        "citation",
                                }
                            )

            # Fallback in case output_text is
            # unavailable in the SDK response.
            if (
                not report
                and fallback_text
            ):
                report = "\n\n".join(
                    fallback_text
                )

            if not report:
                raise RuntimeError(
                    "Gemini returned an "
                    "empty research report."
                )

            sources = (
                deduplicate_sources(
                    sources
                )
            )

            # Deduplicate citations by URL and
            # attributed text position.
            unique_citations = []
            citation_keys = set()

            for citation in citations:

                key = (
                    citation.get("url"),
                    citation.get(
                        "step_id"
                    ),
                    citation.get(
                        "content_index"
                    ),
                    citation.get(
                        "start_index"
                    ),
                    citation.get(
                        "end_index"
                    ),
                )

                if key in citation_keys:
                    continue

                citation_keys.add(
                    key
                )

                unique_citations.append(
                    citation
                )

            usage = (
                to_plain_dict(
                    getattr(
                        interaction,
                        "usage",
                        None
                    )
                )
                or {}
            )

            metadata = {
                "interaction_id": getattr(
                    interaction,
                    "id",
                    None
                ),
                "agent": agent,
                "status": getattr(
                    interaction,
                    "status",
                    None
                ),
                "usage": usage,
                "research_steps":
                    research_steps,
            }

            return ResearchResult(
                text=report,
                provider=(
                    self.provider_name
                ),
                citations=(
                    unique_citations
                ),
                sources=sources,
                metadata=metadata,
            )

        except Exception as exc:

            raise RuntimeError(
                "Gemini Deep Research "
                f"failed: {exc}"
            ) from exc
