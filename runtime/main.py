import getpass
from datetime import date
from pathlib import Path

import yaml

from runtime.agent_runner import run_agent
from runtime.output_handler import save_report
from runtime.providers import get_provider


RUNTIME_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

CONFIG_PATH = (
    RUNTIME_DIR
    / "config.yaml"
)


PROVIDER_DISPLAY_NAMES = {
    "openai": "OpenAI",
    "openrouter": "OpenRouter",
    "gemini": "Gemini",
    "perplexity": "Perplexity",
}


def load_config():
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:
        config = yaml.safe_load(file)

    if not config:
        raise ValueError(
            "config.yaml is empty or invalid."
        )

    if "providers" not in config:
        raise ValueError(
            "config.yaml does not contain "
            "a 'providers' section."
        )

    return config


def ask_required(label):
    while True:
        value = input(
            f"{label}: "
        ).strip()

        if value:
            return value

        print(
            "This field is required."
        )


def ask_optional(
    label,
    default=""
):
    display_default = (
        f" [{default}]"
        if default
        else ""
    )

    value = input(
        f"{label}{display_default}: "
    ).strip()

    if value:
        return value

    return default


def collect_task_settings():
    print()
    print(
        "Enter the shell company "
        "screening task."
    )
    print()

    settings = {}

    settings["client_name"] = (
        ask_required(
            "Client Name"
        )
    )

    settings["target_market"] = (
        ask_required(
            "Target Listed Market"
        )
    )

    settings["research_cutoff_date"] = (
        ask_optional(
            "Research Cut-off Date",
            date.today().isoformat()
        )
    )

    settings["control_requirement"] = (
        ask_optional(
            "Control Requirement",
            "Not specified"
        )
    )

    settings[
        "capital_structure_preference"
    ] = ask_optional(
        "Capital Structure Preference",
        "Not specified"
    )

    settings[
        "warrant_dilution_preference"
    ] = ask_optional(
        "Warrant and Dilution Preference",
        "Not specified"
    )

    settings[
        "reporting_compliance_requirement"
    ] = ask_optional(
        "Reporting, Legal and "
        "Regulatory Requirement",
        "Not specified"
    )

    settings[
        "historical_financing_preference"
    ] = ask_optional(
        "Historical Financing Preference",
        "Not specified"
    )

    settings[
        "market_cap_requirement"
    ] = ask_optional(
        "Market Capitalization Requirement",
        "No fixed threshold"
    )

    settings[
        "transaction_objective"
    ] = ask_optional(
        "Transaction Objective",
        "Not specified"
    )

    settings[
        "additional_requirements"
    ] = ask_optional(
        "Additional Client Requirements",
        "Not specified"
    )

    settings[
        "additional_context"
    ] = ask_optional(
        "Additional Context",
        "Not specified"
    )

    return settings


def choose_provider(config):
    providers = {}

    for name, provider_config in (
        config["providers"].items()
    ):
        if provider_config is None:
            continue

        if not isinstance(
            provider_config,
            dict
        ):
            continue

        if provider_config.get(
            "enabled",
            True
        ):
            providers[name] = (
                provider_config
            )

    if not providers:
        raise ValueError(
            "No enabled Deep Research "
            "providers were found."
        )

    names = list(
        providers.keys()
    )

    print()
    print(
        "Select Deep Research Provider:"
    )
    print()

    for index, name in enumerate(
        names,
        start=1
    ):
        display_name = (
            PROVIDER_DISPLAY_NAMES
            .get(
                name,
                name.capitalize()
            )
        )

        print(
            f"{index}. {display_name}"
        )

    while True:
        selection = input(
            "\nProvider: "
        ).strip().lower()

        if selection.isdigit():
            index = (
                int(selection) - 1
            )

            if (
                0
                <= index
                < len(names)
            ):
                name = names[
                    index
                ]

                return (
                    name,
                    providers[
                        name
                    ].copy()
                )

        if selection in providers:
            return (
                selection,
                providers[
                    selection
                ].copy()
            )

        print(
            "Invalid provider selection."
        )


def choose_provider_model(
    provider_name,
    provider_config
):
    models = (
        provider_config
        .get(
            "models",
            []
        )
    )

    if not models:
        return provider_config

    display_name = (
        PROVIDER_DISPLAY_NAMES
        .get(
            provider_name,
            provider_name.capitalize()
        )
    )

    print()
    print(
        f"Select {display_name} "
        f"Deep Research Model:"
    )
    print()

    for index, model in enumerate(
        models,
        start=1
    ):
        print(
            f"{index}. {model}"
        )

    default_model = (
        provider_config
        .get(
            "default_model"
        )
    )

    if (
        not default_model
        and models
    ):
        default_model = (
            models[0]
        )

    while True:
        selection = input(
            "\nModel"
            f" [{default_model}]: "
        ).strip()

        if not selection:
            selected_model = (
                default_model
            )
            break

        if selection.isdigit():
            index = (
                int(selection) - 1
            )

            if (
                0
                <= index
                < len(models)
            ):
                selected_model = (
                    models[index]
                )
                break

        if selection in models:
            selected_model = (
                selection
            )
            break

        print(
            "Invalid model selection."
        )

    provider_config[
        "model"
    ] = selected_model

    return provider_config


def print_saved_artifact(
    label,
    path
):
    if path is not None:
        print(
            f"{label}: {path}"
        )


def main():
    config = load_config()

    print()
    print("=" * 50)

    print(
        config
        .get(
            "agent",
            {}
        )
        .get(
            "name",
            "Shell Company Screening Agent"
        )
    )

    print("=" * 50)

    settings = (
        collect_task_settings()
    )

    provider_name, provider_config = (
        choose_provider(
            config
        )
    )

    if provider_config.get(
        "models"
    ):
        provider_config = (
            choose_provider_model(
                provider_name,
                provider_config
            )
        )

    print()

    display_name = (
        PROVIDER_DISPLAY_NAMES
        .get(
            provider_name,
            provider_name.capitalize()
        )
    )

    api_key = getpass.getpass(
        f"Enter your "
        f"{display_name} "
        f"API Key: "
    )

    provider = get_provider(
        provider_name=provider_name,
        api_key=api_key,
        config=provider_config,
    )

    print()
    print(
        "Starting Deep Research..."
    )
    print(
        "This may take several minutes."
    )
    print()

    try:

        result = run_agent(
            settings=settings,
            provider=provider,
        )

        output_directory = (
            config
            .get(
                "output",
                {}
            )
            .get(
                "directory",
                "output"
            )
        )

        report_paths = save_report(
            result=result,
            client_name=settings[
                "client_name"
            ],
            provider_name=(
                provider_name
            ),
            output_directory=(
                output_directory
            ),
        )

        print()
        print(
            "Research completed."
        )
        print()

        print(
            "Artifacts saved:"
        )

        print_saved_artifact(
            "Markdown",
            report_paths.get(
                "markdown"
            )
        )

        print_saved_artifact(
            "Evidence JSON",
            report_paths.get(
                "evidence"
            )
        )

        print_saved_artifact(
            "DOCX",
            report_paths.get(
                "docx"
            )
        )

        print_saved_artifact(
            "PDF",
            report_paths.get(
                "pdf"
            )
        )

        warnings = (
            report_paths.get(
                "warnings",
                []
            )
            or []
        )

        if warnings:
            print()
            print(
                "Completed with warnings:"
            )

            for warning in warnings:
                print(
                    f"- {warning}"
                )

        print()
        print(
            "Evidence captured:"
        )

        print(
            f"- Citations: "
            f"{len(result.citations)}"
        )

        print(
            f"- Sources: "
            f"{len(result.sources)}"
        )

    except Exception as exc:

        print()
        print(
            "Agent run failed."
        )

        print(
            str(exc)
        )


if __name__ == "__main__":
    main()