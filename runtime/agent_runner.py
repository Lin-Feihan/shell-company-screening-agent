from pathlib import Path

from prompt_builder import build_prompt


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def run_agent(settings, provider):
    """
    Build the final Shell Company Screening
    prompt and execute it through the selected
    Deep Research provider.
    """

    output_spec_path = (
        REPO_ROOT
        / "output_spec.md"
    )

    prompt_path = (
        REPO_ROOT
        / "prompt.md"
    )

    output_specification = (
        output_spec_path.read_text(
            encoding="utf-8"
        )
    )

    runtime_settings = settings.copy()

    runtime_settings[
        "output_specification"
    ] = output_specification

    prompt = build_prompt(
        prompt_path,
        runtime_settings
    )

    report = provider.run(
        prompt
    )

    return report
