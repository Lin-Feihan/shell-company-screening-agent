import re
from pathlib import Path


def load_file(path):
    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def inject_settings(prompt, settings):
    """
    Replace {{variable}} placeholders
    with runtime task settings.
    """

    for key, value in settings.items():
        placeholder = "{{" + key + "}}"

        prompt = prompt.replace(
            placeholder,
            str(value)
        )

    return prompt


def build_prompt(prompt_path, settings):
    core_prompt = load_file(
        prompt_path
    )

    final_prompt = inject_settings(
        core_prompt,
        settings
    )

    unresolved = sorted(
        set(
            re.findall(
                r"\{\{([^{}]+)\}\}",
                final_prompt
            )
        )
    )

    if unresolved:
        raise ValueError(
            "Unresolved prompt variables: "
            + ", ".join(unresolved)
        )

    return final_prompt
