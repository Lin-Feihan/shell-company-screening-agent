import re
from datetime import datetime
from pathlib import Path


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def safe_filename(value):
    value = str(value).strip()

    value = re.sub(
        r'[<>:"/\\|?*\n\r\t]+',
        "_",
        value
    )

    value = re.sub(
        r"\s+",
        "_",
        value
    )

    return value or "client"


def save_report(
    report,
    client_name,
    provider_name,
    output_directory="output"
):
    output_dir = (
        REPO_ROOT
        / output_directory
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    client = safe_filename(
        client_name
    )

    provider = safe_filename(
        provider_name
    )

    filename = (
        f"shell_screening_"
        f"{client}_"
        f"{provider}_"
        f"{timestamp}.md"
    )

    output_path = (
        output_dir
        / filename
    )

    output_path.write_text(
        report,
        encoding="utf-8"
    )

    return output_path
