import time

from google import genai

from .base import DeepResearchProvider


class GeminiDeepResearchProvider(DeepResearchProvider):

    provider_name = "gemini"

    def run(self, prompt):
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
            interaction = client.interactions.create(
                input=prompt,
                agent=agent,
                background=True,
            )

            while True:
                interaction = client.interactions.get(
                    interaction.id
                )

                if interaction.status == "completed":

    report = getattr(
        interaction,
        "output_text",
        None
    )

    if not report:
        report = (
            interaction
            .steps[-1]
            .content[0]
            .text
        )

    if not report:
        raise RuntimeError(
            "Gemini returned an empty report."
        )

    return report

                if interaction.status == "failed":
                    raise RuntimeError(
                        f"Gemini Deep Research failed: "
                        f"{interaction.error}"
                    )

                time.sleep(poll_interval)

        except Exception as exc:
            raise RuntimeError(
                f"Gemini Deep Research failed: {exc}"
            ) from exc
