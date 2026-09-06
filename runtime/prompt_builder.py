import os


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def inject_settings(prompt, settings):
    """
    Replace template variables in the prompt
    with runtime-provided task settings.
    """

    for key, value in settings.items():
        placeholder = "{{" + key + "}}"
        prompt = prompt.replace(
            placeholder,
            str(value)
        )

    return prompt


def build_prompt(prompt_path, settings):
    core_prompt = load_file(prompt_path)

    final_prompt = inject_settings(
        core_prompt,
        settings
    )

    if "{{" in final_prompt or "}}" in final_prompt:
        raise ValueError(
            "Unresolved template variables remain in the prompt."
        )

    return final_prompt
