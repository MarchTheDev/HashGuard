"""
HashGuard — File Integrity Checker

This is the thin entry point wrapper for the modularized HashGuard application.
All code and UI components are organized neatly under the `hashguard/` package.
This avoids needing to touch this file when making future feature enhancements.

To modify components:
- Hashing Logic:          hashguard/hashing.py
- Update Engine:          hashguard/updater.py
- Configuration/Themes:   hashguard/config.py
- Main UI Window:         hashguard/ui/main_window.py
- Settings Tabs UI:       hashguard/ui/settings_window.py
- Style/Custom Widgets:   hashguard/ui/components.py
"""

import sys
import logging
from hashguard.ui.main_window import HashGuard

# Configure Global Root Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == "__main__":
    app = HashGuard()
    app.mainloop()
