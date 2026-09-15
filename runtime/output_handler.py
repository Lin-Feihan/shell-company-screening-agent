import re
from datetime import datetime
from pathlib import Path

import markdown
from xhtml2pdf import pisa


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



def save_markdown(
    report,
    filename,
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

    path = (
        output_dir
        / filename
    )

    path.write_text(
        report,
        encoding="utf-8"
    )

    return path



def save_pdf(
    report,
    filename,
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


    pdf_path = (
        output_dir
        / filename
    )


    html = markdown.markdown(
        report,
        extensions=[
            "tables",
            "fenced_code"
        ]
    )


    styled_html = f"""
<html>

<head>

<style>

body {{
    font-family: Helvetica;
    font-size: 10pt;
    line-height: 1.5;
}}

h1 {{
    font-size: 18pt;
}}

h2 {{
    font-size: 14pt;
}}

h3 {{
    font-size: 12pt;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    border: 1px solid #444;
    padding: 5px;
}}

</style>

</head>


<body>

{html}

</body>

</html>
"""


    with open(
        pdf_path,
        "wb"
    ) as file:

        pisa.CreatePDF(
            styled_html,
            dest=file
        )


    return pdf_path



def save_report(
    report,
    client_name,
    provider_name,
    output_directory="output"
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


    client = safe_filename(
        client_name
    )

    provider = safe_filename(
        provider_name
    )


    base_name = (
        f"shell_screening_"
        f"{client}_"
        f"{provider}_"
        f"{timestamp}"
    )


    md_path = save_markdown(
        report,
        base_name + ".md",
        output_directory
    )


    pdf_path = save_pdf(
        report,
        base_name + ".pdf",
        output_directory
    )


    return {
        "markdown": md_path,
        "pdf": pdf_path,
    }