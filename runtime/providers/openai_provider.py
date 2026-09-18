import time

from openai import OpenAI

from .base import (
    DeepResearchProvider,
    ResearchResult,
)


def to_plain_dict(value):
    """
    Convert OpenAI SDK objects into plain
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
    message_id=None,
):
    """
    Normalize OpenAI URL citation annotations
    into a provider-independent dictionary.
    """

    data = (
        to_plain_dict(annotation)
        or {}
    )

    # Some API shapes expose citation fields
    # directly, while others nest them under
    # `url_citation`.
    nested = data.get(
        "url_citation"
    )

    if isinstance(
        nested,
        dict
    ):
        citation_data = nested
    else:
        citation_data = data

    url = citation_data.get(
        "url"
    )

    if not url:
        return None

    return {
        "type": (
            data.get("type")
            or "url_citation"
        ),
        "url": url,
        "title": citation_data.get(
            "title"
        ),
        "start_index": citation_data.get(
            "start_index"
        ),
        "end_index": citation_data.get(
            "end_index"
        ),
        "message_id": message_id,
    }


def normalize_source(
    source,
    origin=None,
):
    """
    Normalize source metadata returned by
    OpenAI web search calls.
    """

    data = (
        to_plain_dict(source)
        or {}
    )

    url = data.get(
        "url"
    )

    if not url:
        return None

    normalized = {
        "url": url,
        "title": data.get(
            "title"
        ),
    }

    if origin:
        normalized[
            "origin"
        ] = origin

    return normalized


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


class OpenAIDeepResearchProvider(
    DeepResearchProvider
):

    provider_name = "openai"

    def run(
        self,
        prompt
    ) -> ResearchResult:

        model = self.config.get(
            "model",
            self.config.get(
                "default_model",
                "o4-mini-deep-research"
            )
        )

        poll_interval = self.config.get(
            "poll_interval_seconds",
            10
        )

        client = OpenAI(
            api_key=self.api_key
        )

        try:

            print(
                f"Using OpenAI model: {model}"
            )

            response = client.responses.create(
                model=model,
                input=prompt,
                background=True,
                tools=[
                    {
                        "type":
                        "web_search_preview"
                    }
                ],
                include=[
                    "web_search_call.action.sources"
                ],
            )

            while response.status in {
                "queued",
                "in_progress"
            }:

                time.sleep(
                    poll_interval
                )

                response = (
    client
    .responses
    .retrieve(
        response.id,
        include=[
            "web_search_call.action.sources"
        ],
    )
)

            if (
                response.status
                != "completed"
            ):
                raise RuntimeError(
                    "OpenAI Deep Research "
                    f"ended with status: "
                    f"{response.status}"
                )

            report = getattr(
                response,
                "output_text",
                None
            )

            if not report:
                raise RuntimeError(
                    "OpenAI returned an "
                    "empty research report."
                )

            citations = []
            sources = []
            research_steps = []

            for item in (
                getattr(
                    response,
                    "output",
                    []
                )
                or []
            ):

                item_type = getattr(
                    item,
                    "type",
                    None
                )

                # Final answer and its
                # inline citations.
                if (
                    item_type
                    == "message"
                ):

                    message_id = getattr(
                        item,
                        "id",
                        None
                    )

                    for content in (
                        getattr(
                            item,
                            "content",
                            []
                        )
                        or []
                    ):

                        if (
                            getattr(
                                content,
                                "type",
                                None
                            )
                            != "output_text"
                        ):
                            continue

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
                                    message_id=(
                                        message_id
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

                # Web-search activity and
                # source metadata.
                elif (
                    item_type
                    == "web_search_call"
                ):

                    action = getattr(
                        item,
                        "action",
                        None
                    )

                    action_data = (
                        to_plain_dict(
                            action
                        )
                        or {}
                    )

                    research_steps.append(
                        {
                            "type":
                                "web_search_call",
                            "id":
                                getattr(
                                    item,
                                    "id",
                                    None
                                ),
                            "status":
                                getattr(
                                    item,
                                    "status",
                                    None
                                ),
                            "action":
                                action_data,
                        }
                    )

                    for source in (
                        action_data.get(
                            "sources",
                            []
                        )
                        or []
                    ):

                        normalized_source = (
                            normalize_source(
                                source,
                                origin=(
                                    "web_search"
                                ),
                            )
                        )

                        if normalized_source:
                            sources.append(
                                normalized_source
                            )

                # Preserve basic metadata for
                # other tool calls if present.
                else:

                    if item_type and (
                        item_type.endswith(
                            "_call"
                        )
                    ):
                        research_steps.append(
                            {
                                "type":
                                    item_type,
                                "id":
                                    getattr(
                                        item,
                                        "id",
                                        None
                                    ),
                                "status":
                                    getattr(
                                        item,
                                        "status",
                                        None
                                    ),
                            }
                        )

            sources = (
                deduplicate_sources(
                    sources
                )
            )

            usage = to_plain_dict(
                getattr(
                    response,
                    "usage",
                    None
                )
            )

            metadata = {
                "response_id": getattr(
                    response,
                    "id",
                    None
                ),
                "model": getattr(
                    response,
                    "model",
                    model
                ),
                "status": getattr(
                    response,
                    "status",
                    None
                ),
                "usage": (
                    usage
                    or {}
                ),
                "research_steps":
                    research_steps,
            }

            return ResearchResult(
                text=report,
                provider=(
                    self.provider_name
                ),
                citations=citations,
                sources=sources,
                metadata=metadata,
            )

        except Exception as exc:

            raise RuntimeError(
                "OpenAI Deep Research "
                f"failed: {exc}"
            ) from exc
