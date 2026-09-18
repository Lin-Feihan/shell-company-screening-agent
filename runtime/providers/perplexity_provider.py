import httpx

from perplexity import Perplexity

from .base import (
    DeepResearchProvider,
    ResearchResult,
)


def to_plain_dict(value):
    """
    Convert Perplexity SDK objects into plain
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
    Normalize Perplexity URL citation annotations.
    """

    data = (
        to_plain_dict(annotation)
        or {}
    )

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


def normalize_search_result(
    result,
    origin=None,
):
    """
    Normalize Perplexity search-result metadata.
    """

    data = (
        to_plain_dict(result)
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
        "date": (
            data.get("date")
            or data.get(
                "published_at"
            )
            or data.get(
                "publishedAt"
            )
        ),
        "snippet": (
            data.get("snippet")
            or data.get(
                "description"
            )
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
    useful metadata from richer entries.
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

        for key in [
            "title",
            "date",
            "snippet",
            "origin",
        ]:
            if (
                not existing.get(key)
                and source.get(key)
            ):
                existing[key] = (
                    source[key]
                )

    return list(
        by_url.values()
    )


class PerplexityDeepResearchProvider(
    DeepResearchProvider
):

    provider_name = "perplexity"

    def run(
        self,
        prompt
    ) -> ResearchResult:

        preset = self.config.get(
            "preset",
            "deep-research"
        )

        timeout = self.config.get(
            "timeout_seconds",
            3600
        )

        max_retries = self.config.get(
            "max_retries",
            3
        )

        client = Perplexity(
            api_key=self.api_key,
            timeout=httpx.Timeout(
                timeout
            ),
            max_retries=max_retries,
        )

        try:

            print(
                "Using Perplexity "
                f"preset: {preset}"
            )

            response = (
                client.responses.create(
                    preset=preset,
                    input=prompt,
                )
            )

            report = getattr(
                response,
                "output_text",
                None
            )

            citations = []
            sources = []
            research_steps = []
            fallback_text = []

            # Parse Responses-style output.
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

                        content_type = getattr(
                            content,
                            "type",
                            None
                        )

                        if (
                            content_type
                            == "output_text"
                        ):

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

                elif item_type in {
                    "search_results",
                    "web_search_call",
                }:

                    item_data = (
                        to_plain_dict(
                            item
                        )
                        or {}
                    )

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

                    result_items = (
                        item_data.get(
                            "results"
                        )
                        or item_data.get(
                            "search_results"
                        )
                        or []
                    )

                    for result in (
                        result_items
                    ):
                        source = (
                            normalize_search_result(
                                result,
                                origin=(
                                    item_type
                                ),
                            )
                        )

                        if source:
                            sources.append(
                                source
                            )

                elif item_type:

                    if (
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

            # Fall back to text blocks if the SDK
            # did not expose output_text.
            if (
                not report
                and fallback_text
            ):
                report = "\n\n".join(
                    fallback_text
                )

            response_data = (
                to_plain_dict(
                    response
                )
                or {}
            )

            # Some Perplexity response shapes also
            # expose citations at the top level.
            for citation_item in (
                response_data.get(
                    "citations",
                    []
                )
                or []
            ):

                if isinstance(
                    citation_item,
                    str
                ):
                    citation = {
                        "type":
                            "url_citation",
                        "url":
                            citation_item,
                        "title":
                            None,
                        "start_index":
                            None,
                        "end_index":
                            None,
                        "message_id":
                            None,
                    }

                else:
                    citation = (
                        normalize_url_citation(
                            citation_item
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

            # Some Perplexity response shapes expose
            # rich search results at the top level.
            for result in (
                response_data.get(
                    "search_results",
                    []
                )
                or []
            ):

                source = (
                    normalize_search_result(
                        result,
                        origin=(
                            "search_results"
                        ),
                    )
                )

                if source:
                    sources.append(
                        source
                    )

            if not report:
                raise RuntimeError(
                    "Perplexity returned an "
                    "empty research report."
                )

            sources = (
                deduplicate_sources(
                    sources
                )
            )

            # Deduplicate citations by URL and
            # text position where available.
            unique_citations = []
            citation_keys = set()

            for citation in citations:

                key = (
                    citation.get("url"),
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
                        response,
                        "usage",
                        None
                    )
                )
                or {}
            )

            metadata = {
                "response_id": getattr(
                    response,
                    "id",
                    None
                ),
                "status": getattr(
                    response,
                    "status",
                    None
                ),
                "preset": preset,
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
                "Perplexity Deep Research "
                f"failed: {exc}"
            ) from exc