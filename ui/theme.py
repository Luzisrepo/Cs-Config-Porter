"""A small, intentional color palette instead of CustomTkinter's defaults.

Dark slate background with a warm amber accent -- a nod to CS2's own HUD
color language -- plus clear semantic colors for success / danger states.
"""

BG_ROOT = "#15181d"
BG_PANEL = "#1c2027"
BG_CARD = "#232833"
BG_INPUT = "#282e3a"

BORDER = "#333a48"

TEXT_PRIMARY = "#e8eaed"
TEXT_MUTED = "#8b93a3"

ACCENT = "#f2a33d"       # amber -- primary actions
ACCENT_HOVER = "#d98d2b"
ACCENT_TEXT = "#1a1406"

SUCCESS = "#4caf7d"
SUCCESS_HOVER = "#3d9268"

DANGER = "#e35d5d"
DANGER_HOVER = "#c14a4a"

LOG_INFO = "#c7ccd6"
LOG_SUCCESS = "#6fcf9b"
LOG_ERROR = "#f0837f"
LOG_MUTED = "#7d8494"

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"


def apply_log_tags(textbox) -> None:
    """Configure the color tags used by widgets.LogConsole."""
    textbox.tag_config("info", foreground=LOG_INFO)
    textbox.tag_config("success", foreground=LOG_SUCCESS)
    textbox.tag_config("error", foreground=LOG_ERROR)
    textbox.tag_config("muted", foreground=LOG_MUTED)
