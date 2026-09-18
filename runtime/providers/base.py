from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchResult:
    """
    Standardized result returned by all
    Deep Research providers.
    """

    text: str
    provider: str

    citations: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    sources: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError(
                "Research result text "
                "cannot be empty."
            )


class DeepResearchProvider(ABC):
    """
    Base interface for all Deep Research providers.
    """

    provider_name = "base"

    def __init__(
        self,
        api_key,
        config=None
    ):
        if not api_key or not api_key.strip():
            raise ValueError(
                "API key cannot be empty."
            )

        self.api_key = api_key.strip()
        self.config = config or {}

    @abstractmethod
    def run(
        self,
        prompt
    ) -> ResearchResult:
        """
        Execute a Deep Research task and return
        a standardized ResearchResult.
        """
        raise NotImplementedError
