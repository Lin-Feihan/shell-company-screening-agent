import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx2pdf import convert


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


def normalize_text(text):
    """
    Normalize punctuation that can cause
    inconsistent rendering across PDF engines.
    """

    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": " - ",
        "\u2212": "-",
        "\u00a0": " ",
        "\u202f": " ",
        "\u200b": "",
        "\ufeff": "",
    }

    for source, target in replacements.items():
        text = text.replace(
            source,
            target
        )

    return text


def get_output_directory(
    output_directory
):
    output_dir = (
        REPO_ROOT
        / output_directory
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return output_dir


def save_markdown(
    report,
    filename,
    output_directory="output"
):
    output_dir = (
        get_output_directory(
            output_directory
        )
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


def set_cell_shading(
    cell,
    fill="E9EDF2"
):
    tc_pr = (
        cell._tc
        .get_or_add_tcPr()
    )

    shading = OxmlElement(
        "w:shd"
    )

    shading.set(
        qn("w:fill"),
        fill
    )

    tc_pr.append(
        shading
    )


def set_repeat_table_header(row):
    tr_pr = (
        row._tr
        .get_or_add_trPr()
    )

    tbl_header = OxmlElement(
        "w:tblHeader"
    )

    tbl_header.set(
        qn("w:val"),
        "true"
    )

    tr_pr.append(
        tbl_header
    )


def format_run(
    run,
    font_size=10.5,
    bold=False
):
    run.font.name = "Arial"
    run.font.size = Pt(
        font_size
    )
    run.bold = bold


def add_inline_text(
    paragraph,
    text,
    font_size=10.5
):
    """
    Minimal Markdown inline formatter.
    Supports **bold** text.
    """

    parts = re.split(
        r"(\*\*.*?\*\*)",
        text
    )

    for part in parts:
        if not part:
            continue

        if (
            part.startswith("**")
            and part.endswith("**")
            and len(part) >= 4
        ):
            run = paragraph.add_run(
                part[2:-2]
            )

            format_run(
                run,
                font_size=font_size,
                bold=True
            )

        else:
            run = paragraph.add_run(
                part
            )

            format_run(
                run,
                font_size=font_size
            )


def configure_document(document):
    section = (
        document.sections[0]
    )

    section.top_margin = Inches(
        0.7
    )

    section.bottom_margin = Inches(
        0.7
    )

    section.left_margin = Inches(
        0.7
    )

    section.right_margin = Inches(
        0.7
    )

    normal = (
        document.styles[
            "Normal"
        ]
    )

    normal.font.name = "Arial"
    normal.font.size = Pt(
        10.5
    )

    normal.paragraph_format.space_after = Pt(
        6
    )

    normal.paragraph_format.line_spacing = 1.15

    heading_sizes = {
        "Title": 20,
        "Heading 1": 15,
        "Heading 2": 12.5,
        "Heading 3": 11,
        "Heading 4": 10.5,
    }

    for style_name, size in (
        heading_sizes.items()
    ):
        style = (
            document.styles[
                style_name
            ]
        )

        style.font.name = "Arial"
        style.font.size = Pt(
            size
        )

        style.font.bold = True


def is_table_separator(line):
    stripped = (
        line.strip()
    )

    if not (
        stripped.startswith("|")
        and stripped.endswith("|")
    ):
        return False

    cells = [
        cell.strip()
        for cell in (
            stripped
            .strip("|")
            .split("|")
        )
    ]

    if not cells:
        return False

    for cell in cells:
        if not re.fullmatch(
            r":?-{3,}:?",
            cell
        ):
            return False

    return True


def parse_table_row(line):
    return [
        cell.strip()
        for cell in (
            line.strip()
            .strip("|")
            .split("|")
        )
    ]


def add_table(
    document,
    rows
):
    if not rows:
        return

    column_count = max(
        len(row)
        for row in rows
    )

    table = document.add_table(
        rows=len(rows),
        cols=column_count
    )

    table.style = (
        "Table Grid"
    )

    table.autofit = True

    for row_index, row_data in enumerate(
        rows
    ):
        row = (
            table.rows[
                row_index
            ]
        )

        if row_index == 0:
            set_repeat_table_header(
                row
            )

        for column_index in range(
            column_count
        ):
            cell = (
                row.cells[
                    column_index
                ]
            )

            text = (
                row_data[
                    column_index
                ]
                if column_index
                < len(row_data)
                else ""
            )

            paragraph = (
                cell.paragraphs[0]
            )

            paragraph.paragraph_format.space_after = Pt(
                0
            )

            add_inline_text(
                paragraph,
                text,
                font_size=8
            )

            if row_index == 0:
                set_cell_shading(
                    cell
                )

                for run in (
                    paragraph.runs
                ):
                    run.bold = True

    document.add_paragraph()


def add_heading(
    document,
    text,
    level
):
    if level == 1:
        paragraph = document.add_heading(
            level=1
        )
    elif level == 2:
        paragraph = document.add_heading(
            level=2
        )
    elif level == 3:
        paragraph = document.add_heading(
            level=3
        )
    else:
        paragraph = document.add_heading(
            level=4
        )

    add_inline_text(
        paragraph,
        text,
        font_size={
            1: 15,
            2: 12.5,
            3: 11,
            4: 10.5,
        }.get(
            level,
            10.5
        )
    )


def add_paragraph(
    document,
    text
):
    paragraph = (
        document.add_paragraph()
    )

    add_inline_text(
        paragraph,
        text
    )


def add_bullet(
    document,
    text
):
    paragraph = document.add_paragraph(
        style="List Bullet"
    )

    add_inline_text(
        paragraph,
        text
    )


def add_numbered_item(
    document,
    text
):
    paragraph = document.add_paragraph(
        style="List Number"
    )

    add_inline_text(
        paragraph,
        text
    )


def markdown_to_docx(
    report,
    docx_path
):
    report = normalize_text(
        report
    )

    document = Document()

    configure_document(
        document
    )

    lines = report.splitlines()

    index = 0
    first_heading = True

    while index < len(lines):
        line = lines[index].rstrip()

        if not line.strip():
            index += 1
            continue

        heading_match = re.match(
            r"^(#{1,6})\s+(.+)$",
            line
        )

        if heading_match:
            level = len(
                heading_match.group(1)
            )

            text = (
                heading_match
                .group(2)
                .strip()
            )

            if (
                level == 1
                and first_heading
            ):
                title = (
                    document.add_paragraph(
                        style="Title"
                    )
                )

                title.alignment = (
                    WD_ALIGN_PARAGRAPH.CENTER
                )

                add_inline_text(
                    title,
                    text,
                    font_size=20
                )

                first_heading = False

            else:
                add_heading(
                    document,
                    text,
                    min(
                        level,
                        4
                    )
                )

            index += 1
            continue

        if (
            line.strip().startswith("|")
            and index + 1 < len(lines)
            and is_table_separator(
                lines[index + 1]
            )
        ):
            rows = [
                parse_table_row(
                    line
                )
            ]

            index += 2

            while (
                index < len(lines)
                and lines[index]
                .strip()
                .startswith("|")
            ):
                rows.append(
                    parse_table_row(
                        lines[index]
                    )
                )

                index += 1

            add_table(
                document,
                rows
            )

            continue

        bullet_match = re.match(
            r"^\s*[-*+]\s+(.+)$",
            line
        )

        if bullet_match:
            add_bullet(
                document,
                bullet_match.group(1)
            )

            index += 1
            continue

        numbered_match = re.match(
            r"^\s*\d+\.\s+(.+)$",
            line
        )

        if numbered_match:
            add_numbered_item(
                document,
                numbered_match.group(1)
            )

            index += 1
            continue

        paragraph_lines = [
            line.strip()
        ]

        index += 1

        while index < len(lines):
            next_line = (
                lines[index]
                .rstrip()
            )

            if not next_line.strip():
                break

            if re.match(
                r"^(#{1,6})\s+",
                next_line
            ):
                break

            if re.match(
                r"^\s*[-*+]\s+",
                next_line
            ):
                break

            if re.match(
                r"^\s*\d+\.\s+",
                next_line
            ):
                break

            if (
                next_line
                .strip()
                .startswith("|")
            ):
                break

            paragraph_lines.append(
                next_line.strip()
            )

            index += 1

        paragraph_text = " ".join(
            paragraph_lines
        )

        add_paragraph(
            document,
            paragraph_text
        )

    document.save(
        str(docx_path)
    )


def save_docx(
    report,
    filename,
    output_directory="output"
):
    output_dir = (
        get_output_directory(
            output_directory
        )
    )

    docx_path = (
        output_dir
        / filename
    )

    markdown_to_docx(
        report,
        docx_path
    )

    return docx_path


def save_pdf_from_docx(
    docx_path,
    pdf_path
):
    try:
        convert(
            str(docx_path),
            str(pdf_path)
        )

    except Exception as exc:
        raise RuntimeError(
            "DOCX was created successfully, "
            "but PDF conversion failed. "
            "Make sure Microsoft Word is "
            "installed on this Windows computer."
        ) from exc

    return pdf_path


def save_report(
    report,
    client_name,
    provider_name,
    output_directory="output"
):
    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
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

    docx_path = save_docx(
        report,
        base_name + ".docx",
        output_directory
    )

    output_dir = (
        get_output_directory(
            output_directory
        )
    )

    pdf_path = (
        output_dir
        / (
            base_name
            + ".pdf"
        )
    )

    save_pdf_from_docx(
        docx_path,
        pdf_path
    )

    return {
        "markdown": md_path,
        "docx": docx_path,
        "pdf": pdf_path,
    }