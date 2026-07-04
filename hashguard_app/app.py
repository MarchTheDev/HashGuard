"""
HashGuard application entry point.
Creates the pywebview window pointing at the built HTML UI.

If the UI hasn't been built yet (dist/index.html missing — for example
right after cloning the repository, since build output usually isn't
committed to source control) this automatically runs `npm install` and
`npm run build` so the app "just works" the first time it's launched.
"""

from __future__ import annotations

from hashguard_app.config import APP_TITLE, UI_PATH
from hashguard_app.backend import Backend
from hashguard_app.build_ui import ensure_ui_built


def main() -> None:
    try:
        import webview  # type: ignore
    except ImportError:
        print("pywebview is required.  Install it with:")
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
        background_color="#0a0f1a",   # matches --color-bg-dark so no white flash
    )

    webview.start(debug=False)
