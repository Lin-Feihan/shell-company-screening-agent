from .openai_provider import (
    OpenAIDeepResearchProvider
)
from .gemini_provider import (
    GeminiDeepResearchProvider
)
from .perplexity_provider import (
    PerplexityDeepResearchProvider
)


PROVIDER_MAP = {
    "openai": OpenAIDeepResearchProvider,
    "gemini": GeminiDeepResearchProvider,
    "perplexity": PerplexityDeepResearchProvider,
}


def get_provider(
    provider_name,
    api_key,
    config=None
):
    name = provider_name.strip().lower()

    provider_class = PROVIDER_MAP.get(name)

    if provider_class is None:
        raise ValueError(
            f"Unsupported provider: {provider_name}"
        )

    return provider_class(
        api_key=api_key,
        config=config or {},
    )
