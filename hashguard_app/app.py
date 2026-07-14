"""
HashGuard application entry point.
Creates the pywebview window pointing at the built HTML UI.
"""

from __future__ import annotations

from hashguard_app.config import APP_TITLE, UI_PATH, ICON_PATH
from hashguard_app.backend import Backend
from hashguard_app.build_ui import ensure_ui_built


def main() -> None:
    try:
        import webview  # type: ignore
    except ImportError:
        print("pywebview is required. Install it with:")
        print("    pip install pywebview")
        input("\nPress Enter to close…")
        return

    if not ensure_ui_built():
        input("\nPress Enter to close…")
        return

    backend = Backend()

    webview.create_window(
        APP_TITLE,
        url=UI_PATH.resolve().as_uri(),
        js_api=backend,
        width=1280,
        height=860,
        min_size=(900, 640),
        text_select=False,
        background_color="#090d16",
    )

    icon_arg = str(ICON_PATH) if ICON_PATH and ICON_PATH.exists() else None
    webview.start(icon=icon_arg, debug=False, private_mode=False)
