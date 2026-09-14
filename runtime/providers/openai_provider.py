import time

from openai import OpenAI

from .base import DeepResearchProvider


class OpenAIDeepResearchProvider(DeepResearchProvider):

    provider_name = "openai"

    def run(self, prompt):
        model = self.config.get(
            "model",
            "o3-deep-research"
        )

        poll_interval = self.config.get(
            "poll_interval_seconds",
            10
        )

        client = OpenAI(
            api_key=self.api_key
        )

        try:
            response = client.responses.create(
                model=model,
                input=prompt,
                background=True,
                tools=[
                    {
                        "type": "web_search_preview"
                    }
                ],
            )

            while response.status in {
                "queued",
                "in_progress"
            }:
                time.sleep(poll_interval)

                response = client.responses.retrieve(
                    response.id
                )

            if response.status != "completed":
                raise RuntimeError(
                    f"OpenAI Deep Research ended "
                    f"with status: {response.status}"
                )

            if not response.output_text:
                raise RuntimeError(
                    "OpenAI returned an empty report."
                )

            return response.output_text

        except Exception as exc:
            raise RuntimeError(
                f"OpenAI Deep Research failed: {exc}"
            ) from exc
