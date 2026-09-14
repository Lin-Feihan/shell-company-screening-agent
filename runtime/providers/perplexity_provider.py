from perplexity import Perplexity

from .base import DeepResearchProvider


class PerplexityDeepResearchProvider(
    DeepResearchProvider
):

    provider_name = "perplexity"

    def run(self, prompt):
        preset = self.config.get(
            "preset",
            "deep-research"
        )

        client = Perplexity(
            api_key=self.api_key
        )

        try:
            response = client.responses.create(
                preset=preset,
                input=prompt,
            )

            report = response.output_text

            if not report:
                raise RuntimeError(
                    "Perplexity returned an empty report."
                )

            return report

        except Exception as exc:
            raise RuntimeError(
                f"Perplexity Deep Research failed: {exc}"
            ) from exc
