"""Run a blocking operation off the Tk main thread without freezing the UI."""
from __future__ import annotations

import threading
from typing import Callable, Optional

from .widgets import LogConsole


def run_operation(
    widget,
    worker: Callable[[Callable[[str, str], None]], object],
    log_console: LogConsole,
    on_start: Optional[Callable[[], None]] = None,
    on_done: Optional[Callable[[object], None]] = None,
) -> None:
    """Run `worker(log_fn)` on a background thread.

    `worker` receives a `log_fn(message, level="info")` it can call freely;
    those calls (and the final result) are safely marshaled back onto the Tk
    main thread via `widget.after(0, ...)`.
    """

    def log_fn(message: str, level: str = "info") -> None:
        widget.after(0, lambda: log_console.log(message, level))

    def thread_target() -> None:
        try:
            result = worker(log_fn)
        except Exception as exc:  # noqa: BLE001 - surface unexpected errors instead of crashing the thread
            # `except ... as exc` unbinds exc as soon as this block ends, so
            # capture the message now rather than inside the deferred lambda.
            error_message = f"Unexpected error: {exc}"
            widget.after(0, lambda: log_console.log(error_message, "error"))
            if on_done:
                widget.after(0, lambda: on_done(None))
            return
        if on_done:
            widget.after(0, lambda: on_done(result))

    if on_start:
        on_start()
    threading.Thread(target=thread_target, daemon=True).start()
