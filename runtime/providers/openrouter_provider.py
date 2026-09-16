from openai import OpenAI

from .base import DeepResearchProvider


OPENAI_DEEP_RESEARCH_MODELS = {
    "openai/o4-mini-deep-research",
    "openai/o3-deep-research",
}


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
            timeout=3600,
        )

        try:

            print(
                f"Using OpenRouter model: {model}"
            )

            # OpenAI Deep Research models must use
            # the Responses API.
            if model in OPENAI_DEEP_RESEARCH_MODELS:

                response = client.responses.create(
                    model=model,
                    input=prompt,
                )

                report = getattr(
                    response,
                    "output_text",
                    None
                )

            # Keep the existing Chat Completions path
            # for other OpenRouter models such as
            # Perplexity Sonar Deep Research.
            else:

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