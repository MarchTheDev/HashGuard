"""HashGuard configuration and paths."""
from __future__ import annotations
import sys
from pathlib import Path

APP_NAME    = "HashGuard"
APP_VERSION = "1.1"
APP_TITLE   = f"{APP_NAME} — Offline Cryptographic Hub"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# UI is inside the app package
UI_PATH = BASE_DIR / "hashguard_app" / "UI" / "index.html"

# Optional icon path (looks for hashguard.ico or icon.ico in the project root)
ICON_PATH: Path | None = None
for _candidate in ("hashguard.ico", "icon.ico", "icon.png", "hashguard_app/hashguard.ico", "hashguard_app/icon.ico"):
    _p = BASE_DIR / _candidate
    if _p.exists():
        ICON_PATH = _p
        break

DATA_DIR = BASE_DIR / ".hashguard_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "state.json"

__all__ = ["APP_NAME", "APP_VERSION", "APP_TITLE", "BASE_DIR", "UI_PATH", "ICON_PATH", "DATA_DIR", "STATE_FILE"]
