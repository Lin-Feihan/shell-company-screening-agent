import datetime


def save_report(report, path="output/report.md"):

    with open(path, "w", encoding="utf-8") as f:
        f.write(report)


def format_output(report):

    return {
        "generated_time": str(
            datetime.datetime.now()
        ),
        "report": report
    }
