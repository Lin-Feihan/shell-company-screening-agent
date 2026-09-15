import time

from openai import OpenAI

from .base import DeepResearchProvider


class OpenAIDeepResearchProvider(
    DeepResearchProvider
):

    provider_name = "openai"


    def run(self, prompt):

        model = self.config.get(
            "model",
            self.config.get(
                "default_model",
                "o4-mini-deep-research"
            )
        )


        poll_interval = self.config.get(
            "poll_interval_seconds",
            10
        )


        client = OpenAI(
            api_key=self.api_key
        )


        try:

            print(
                f"Using OpenAI model: {model}"
            )


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

                time.sleep(
                    poll_interval
                )


                response = (
                    client.responses.retrieve(
                        response.id
                    )
                )


            if response.status != "completed":

                raise RuntimeError(
                    "OpenAI Deep Research "
                    f"ended with status: "
                    f"{response.status}"
                )


            report = getattr(
                response,
                "output_text",
                None
            )


            if not report:

                raise RuntimeError(
                    "OpenAI returned an "
                    "empty research report."
                )


            return report


        except Exception as exc:

            raise RuntimeError(
                f"OpenAI Deep Research failed: {exc}"
            ) from exc