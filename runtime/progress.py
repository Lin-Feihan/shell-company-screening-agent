import threading
import time


def format_elapsed(seconds):
    seconds = int(seconds)

    hours, remainder = divmod(
        seconds,
        3600
    )

    minutes, seconds = divmod(
        remainder,
        60
    )

    if hours:
        return (
            f"{hours}h "
            f"{minutes}m "
            f"{seconds}s"
        )

    if minutes:
        return (
            f"{minutes}m "
            f"{seconds}s"
        )

    return f"{seconds}s"


class ResearchProgress:
    """
    Provider-independent heartbeat for
    long-running research tasks.

    This does not estimate percentage completion.
    It only confirms that the local process is
    still waiting for the research provider.
    """

    def __init__(
        self,
        provider_name,
        model_name=None,
        interval_seconds=60,
    ):
        self.provider_name = provider_name
        self.model_name = model_name
        self.interval_seconds = (
            interval_seconds
        )

        self.started_at = None

        self.stop_event = (
            threading.Event()
        )

        self.thread = None


    def __enter__(self):
        self.started_at = (
            time.monotonic()
        )

        label = self.provider_name

        if self.model_name:
            label += (
                f" / {self.model_name}"
            )

        print()
        print(
            f"Research started: {label}",
            flush=True
        )

        print(
            "The research provider is "
            "working in the background.",
            flush=True
        )

        self.thread = threading.Thread(
            target=self._heartbeat,
            daemon=True,
        )

        self.thread.start()

        return self


    def _heartbeat(self):
        while not self.stop_event.wait(
            self.interval_seconds
        ):
            elapsed = (
                time.monotonic()
                - self.started_at
            )

            print(
                "Still researching... "
                f"{format_elapsed(elapsed)} "
                "elapsed.",
                flush=True
            )


    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        self.stop_event.set()

        if self.thread:
            self.thread.join(
                timeout=1
            )

        elapsed = (
            time.monotonic()
            - self.started_at
        )

        print()

        if exc_type is None:
            print(
                "Research response received "
                f"after "
                f"{format_elapsed(elapsed)}.",
                flush=True
            )
        else:
            print(
                "Research request stopped "
                f"after "
                f"{format_elapsed(elapsed)}.",
                flush=True
            )

        return False