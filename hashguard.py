"""
HashGuard — File Integrity Checker

This is the entry point wrapper for the modern, modularized HashGuard application.
The UI has been migrated to `pywebview` to achieve the exact look, responsiveness,
and flawless custom theme creator capabilities found in GhostHunterPro!

To modify components:
- Hashing Logic:          hashguard/hashing.py
- Update Engine:          hashguard/updater.py
- Configuration/Themes:   hashguard/config.py
- Main GUI Webview:       hashguard/ui/window.py
- HTML/CSS/JS Layout:     hashguard/ui/html_template.py
"""

import sys
import logging
from hashguard.ui.window import launch_gui

# Configure Global Root Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == "__main__":
    launch_gui()
