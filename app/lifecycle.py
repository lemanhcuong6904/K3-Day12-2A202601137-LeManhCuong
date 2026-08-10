"""CP4 - graceful shutdown signal handling."""

from __future__ import annotations

import signal


class Lifecycle:
    """Track whether the process is draining before shutdown."""

    def __init__(self) -> None:
        self.shutting_down = False
        self._previous: dict = {}

    def request_shutdown(self, signum=None, frame=None) -> None:
        self.shutting_down = True
        previous = self._previous.get(signum)
        if callable(previous):
            previous(signum, frame)

    def install(self) -> None:
        for sig in (signal.SIGTERM, signal.SIGINT):
            self._previous[sig] = signal.getsignal(sig)
            signal.signal(sig, self.request_shutdown)


lifecycle = Lifecycle()
