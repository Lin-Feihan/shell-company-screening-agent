from abc import ABC, abstractmethod


class DeepResearchProvider(ABC):
    """
    Base interface for all Deep Research providers.
    """

    provider_name = "base"

    def __init__(self, api_key, config=None):
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty.")

        self.api_key = api_key.strip()
        self.config = config or {}

    @abstractmethod
    def run(self, prompt):
        """
        Execute a Deep Research task and return
        the final report as plain text / Markdown.
        """
        raise NotImplementedError
