import getpass
from datetime import date
from pathlib import Path

import yaml

from agent_runner import run_agent
from output_handler import save_report
from providers import get_provider


RUNTIME_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

CONFIG_PATH = (
    RUNTIME_DIR
    / "config.yaml"
)


def load_config():
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:
        return yaml.safe_load(file)


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
        "Additional Client Requirements"
    )

    settings[
        "additional_context"
    ] = ask_optional(
        "Additional Context"
    )

    return settings


def choose_provider(config):
    providers = {
        name: provider_config
        for name, provider_config
        in config["providers"].items()
        if provider_config.get(
            "enabled",
            True
        )
    }

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
        print(
            f"{index}. "
            f"{name.capitalize()}"
        )

    while True:
        selection = input(
            "\nProvider: "
        ).strip().lower()

        if selection.isdigit():
            index = int(selection) - 1

            if 0 <= index < len(names):
                name = names[index]

                return (
                    name,
                    providers[name]
                )

        if selection in providers:
            return (
                selection,
                providers[selection]
            )

        print(
            "Invalid provider selection."
        )


def main():
    config = load_config()

    print()
    print("=" * 50)
    print(
        config["agent"]["name"]
    )
    print("=" * 50)

    settings = (
        collect_task_settings()
    )

    provider_name, provider_config = (
        choose_provider(config)
    )

    print()

    api_key = getpass.getpass(
        f"Enter your "
        f"{provider_name.capitalize()} "
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
        report = run_agent(
            settings=settings,
            provider=provider,
        )

        output_directory = (
            config
            .get("output", {})
            .get(
                "directory",
                "output"
            )
        )

        report_path = save_report(
            report=report,
            client_name=settings[
                "client_name"
            ],
            provider_name=provider_name,
            output_directory=(
                output_directory
            ),
        )

        print()
        print(
            "Research completed."
        )
        print(
            f"Report saved to:"
        )
        print(
            report_path
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
