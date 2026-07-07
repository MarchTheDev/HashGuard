"""HashGuard configuration and paths."""
from __future__ import annotations
import sys
import os
from pathlib import Path

APP_NAME    = "HashGuard"
APP_VERSION = "1.1"
APP_TITLE   = f"{APP_NAME} — Offline Cryptographic Hub"

# GitHub repository for update checks
GITHUB_REPO = "MarchTheDev/HashGuard"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
GITHUB_RELEASES_PAGE = f"https://github.com/{GITHUB_REPO}/releases"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
    # When running as a frozen exe, the actual install directory is the parent
    INSTALL_DIR = Path(os.path.dirname(sys.executable))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTALL_DIR = BASE_DIR

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

# Temporary download location for updates
UPDATE_CACHE_DIR = DATA_DIR / "updates"
UPDATE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

__all__ = [
    "APP_NAME", "APP_VERSION", "APP_TITLE", "BASE_DIR", "INSTALL_DIR",
    "UI_PATH", "ICON_PATH", "DATA_DIR", "STATE_FILE",
    "GITHUB_REPO", "GITHUB_API_RELEASES", "GITHUB_RELEASES_PAGE",
    "UPDATE_CACHE_DIR",
]
