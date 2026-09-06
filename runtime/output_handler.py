import datetime
import os


def save_report(report, path="output/report.md"):
    directory = os.path.dirname(path)

    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(report)


def format_output(report):

    return {
        "generated_time": str(
            datetime.datetime.now()
        ),
        "report": report
    }
