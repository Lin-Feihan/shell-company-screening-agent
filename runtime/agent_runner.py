from prompt_builder import build_prompt


def run_deep_research(prompt):
    """
    Placeholder function.

    Replace this function with the actual
    Deep Research API call after runtime
    integration is confirmed.
    """

    raise NotImplementedError(
        "Deep Research API integration required."
    )


def run_agent(settings):
    with open("../output_spec.md", "r", encoding="utf-8") as f:
        output_specification = f.read()

    settings = settings.copy()
    settings["output_specification"] = output_specification

    prompt = build_prompt(
        "../prompt.md",
        settings
    )

    result = run_deep_research(
        prompt
    )

    return result
