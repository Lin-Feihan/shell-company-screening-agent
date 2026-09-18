from openai import OpenAI

from .base import (
    DeepResearchProvider,
    ResearchResult,
)


OPENAI_DEEP_RESEARCH_MODELS = {
    "openai/o4-mini-deep-research",
    "openai/o3-deep-research",
}


def to_plain_dict(value):
    """
    Convert OpenAI-compatible SDK objects into
    plain Python dictionaries where possible.
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
    Normalize OpenRouter URL citation annotations
    into a provider-independent dictionary.
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

    annotation_type = (
        data.get("type")
        or citation_data.get("type")
    )

    url = citation_data.get(
        "url"
    )

    if not url:
        return None

    return {
        "type": (
            annotation_type
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
        "content": citation_data.get(
            "content"
        ),
        "message_id": message_id,
    }


def deduplicate_sources(
    sources
):
    """
    Deduplicate sources by URL while preserving
    richer metadata from later entries.
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
            "content",
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


def extract_response_citations(
    response
):
    """
    Extract citations and sources from a
    Responses API-style OpenRouter response.
    """

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
                                "content":
                                    citation.get(
                                        "content"
                                    ),
                                "origin":
                                    "citation",
                            }
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

    return (
        citations,
        sources,
        research_steps,
    )


def extract_chat_citations(
    response
):
    """
    Extract citations from a Chat Completions
    style OpenRouter response.
    """

    citations = []
    sources = []

    response_data = (
        to_plain_dict(
            response
        )
        or {}
    )

    choices = (
        response_data.get(
            "choices",
            []
        )
        or []
    )

    if not choices:
        return (
            citations,
            sources,
        )

    message = (
        choices[0].get(
            "message",
            {}
        )
        or {}
    )

    annotations = (
        message.get(
            "annotations",
            []
        )
        or []
    )

    for annotation in annotations:

        citation = (
            normalize_url_citation(
                annotation
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
                    "content":
                        citation.get(
                            "content"
                        ),
                    "origin":
                        "citation",
                }
            )

    # Some provider-specific responses may expose
    # citations or search results at the top level.
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
                "content":
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
                    "content":
                        citation.get(
                            "content"
                        ),
                    "origin":
                        "citation",
                }
            )

    for result in (
        response_data.get(
            "search_results",
            []
        )
        or []
    ):

        if not isinstance(
            result,
            dict
        ):
            continue

        url = result.get(
            "url"
        )

        if not url:
            continue

        sources.append(
            {
                "url": url,
                "title": result.get(
                    "title"
                ),
                "content": (
                    result.get("snippet")
                    or result.get(
                        "content"
                    )
                ),
                "origin":
                    "search_results",
            }
        )

    return (
        citations,
        sources,
    )


def deduplicate_citations(
    citations
):
    """
    Deduplicate citations by URL and text span.
    """

    unique = []
    keys = set()

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

        if key in keys:
            continue

        keys.add(
            key
        )

        unique.append(
            citation
        )

    return unique


class OpenRouterDeepResearchProvider(
    DeepResearchProvider
):

    provider_name = "openrouter"

    def run(
        self,
        prompt
    ) -> ResearchResult:

        model = self.config.get(
            "model",
            self.config.get(
                "default_model",
                "openai/o4-mini-deep-research"
            )
        )

        client = OpenAI(
            api_key=self.api_key,
            base_url=(
                "https://openrouter.ai/api/v1"
            ),
            timeout=3600,
        )

        try:

            print(
                f"Using OpenRouter model: "
                f"{model}"
            )

            citations = []
            sources = []
            research_steps = []
            usage = {}
            response_id = None
            status = None

            # OpenAI Deep Research models use
            # the Responses API path.
            if (
                model
                in OPENAI_DEEP_RESEARCH_MODELS
            ):

                response = (
                    client
                    .responses
                    .create(
                        model=model,
                        input=prompt,
                    )
                )

                report = getattr(
                    response,
                    "output_text",
                    None
                )

                (
                    citations,
                    sources,
                    research_steps,
                ) = (
                    extract_response_citations(
                        response
                    )
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

                response_id = getattr(
                    response,
                    "id",
                    None
                )

                status = getattr(
                    response,
                    "status",
                    None
                )

            # Other OpenRouter models, such as
            # Perplexity Sonar Deep Research,
            # use Chat Completions here.
            else:

                response = (
                    client
                    .chat
                    .completions
                    .create(
                        model=model,
                        messages=[
                            {
                                "role":
                                    "user",
                                "content":
                                    prompt,
                            }
                        ],
                    )
                )

                if not response.choices:
                    raise RuntimeError(
                        "OpenRouter returned "
                        "no choices."
                    )

                report = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                (
                    citations,
                    sources,
                ) = extract_chat_citations(
                    response
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

                response_id = getattr(
                    response,
                    "id",
                    None
                )

            if not report:
                raise RuntimeError(
                    "OpenRouter returned an "
                    "empty research report."
                )

            citations = (
                deduplicate_citations(
                    citations
                )
            )

            sources = (
                deduplicate_sources(
                    sources
                )
            )

            metadata = {
                "response_id":
                    response_id,
                "model":
                    model,
                "status":
                    status,
                "usage":
                    usage,
                "research_steps":
                    research_steps,
                "api_path": (
                    "responses"
                    if model
                    in OPENAI_DEEP_RESEARCH_MODELS
                    else
                    "chat_completions"
                ),
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
                "OpenRouter Deep Research "
                f"failed: {exc}"
            ) from exc
