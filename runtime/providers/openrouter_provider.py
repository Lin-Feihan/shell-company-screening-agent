from openai import OpenAI

from .base import DeepResearchProvider


class OpenRouterDeepResearchProvider(
    DeepResearchProvider
):

    provider_name = "openrouter"

    def run(self, prompt):

        model = self.config.get(
            "model",
            self.config.get(
                "default_model",
                "openai/o4-mini-deep-research"
            )
        )

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=1800.0,
        )

        try:

            print(
                f"Using OpenRouter model: {model}"
            )

            response = (
                client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )
            )

            if not response.choices:
                raise RuntimeError(
                    "OpenRouter returned no choices."
                )

            report = (
                response
                .choices[0]
                .message
                .content
            )

            if not report:
                raise RuntimeError(
                    "OpenRouter returned an "
                    "empty research report."
                )

            return report

        except Exception as exc:

            raise RuntimeError(
                "OpenRouter Deep Research "
                f"failed: {exc}"
            ) from exc