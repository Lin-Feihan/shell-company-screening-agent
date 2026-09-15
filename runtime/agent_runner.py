from pathlib import Path

from runtime.prompt_builder import (
    build_prompt
)

from runtime.progress import (
    ResearchProgress
)


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def run_agent(
    settings,
    provider
):
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

    runtime_settings = (
        settings.copy()
    )

    runtime_settings[
        "output_specification"
    ] = output_specification

    prompt = build_prompt(
        prompt_path,
        runtime_settings
    )

    provider_name = getattr(
        provider,
        "provider_name",
        "deep-research"
    )

    model_name = (
        provider.config.get("model")
        or provider.config.get("agent")
        or provider.config.get("preset")
        or "default"
    )

    heartbeat_interval = (
        provider.config.get(
            "heartbeat_interval_seconds",
            60
        )
    )

    with ResearchProgress(
        provider_name=provider_name,
        model_name=model_name,
        interval_seconds=(
            heartbeat_interval
        ),
    ):
        report = provider.run(
            prompt
        )

    return report