import json
import logging
import re
from pathlib import Path

VERSION = "1.0.0"
CREATOR = "MarchTheDev"
GITHUB_REPO = "MarchTheDev/HashGuard"

# Global colors for states
SUCCESS = "#3DD68C"
ERROR = "#FF5C5C"
WARNING = "#FFB347"

CONFIG_FILE = Path.home() / ".hashguard_config.json"
logger = logging.getLogger("HashGuard.Config")

THEMES = {
    "Default (Cyberpunk Dark)": {
        "ACCENT": "#4A9EFF",
        "BG_ROOT": "#13131F",
        "BG_CARD": "#1E1E2E",
        "FG_MAIN": "#E0E0F0",
        "FG_DIM": "#8888AA"
    },
    "Emerald Garden": {
        "ACCENT": "#2ECC71",
        "BG_ROOT": "#0F1C15",
        "BG_CARD": "#172A20",
        "FG_MAIN": "#ECF0F1",
        "FG_DIM": "#95A5A6"
    },
    "Rubellite (Crimson)": {
        "ACCENT": "#E74C3C",
        "BG_ROOT": "#1C1111",
        "BG_CARD": "#2A1B1B",
        "FG_MAIN": "#F5EBEB",
        "FG_DIM": "#A89898"
    },
    "Amethyst (Purple)": {
        "ACCENT": "#9B59B6",
        "BG_ROOT": "#16121E",
        "BG_CARD": "#221C2D",
        "FG_MAIN": "#F2EEF6",
        "FG_DIM": "#A299B0"
    },
    "Sunset Gold": {
        "ACCENT": "#F39C12",
        "BG_ROOT": "#1D1710",
        "BG_CARD": "#292118",
        "FG_MAIN": "#FDF6EC",
        "FG_DIM": "#B5A593"
    },
}

def adjust_color(hex_color: str, factor: float) -> str:
    """Lightens or darkens a hex color by a factor. factor > 0 lightens, < 0 darkens."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return f"#{hex_color}"
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        if factor < 0:
            r = int(r * (1 + factor))
            g = int(g * (1 + factor))
            b = int(b * (1 + factor))
        else:
            r = int(r + (255 - r) * factor)
            g = int(g + (255 - g) * factor)
            b = int(b + (255 - b) * factor)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f"#{r:02X}{g:02X}{b:02X}"
    except ValueError:
        return f"#{hex_color}"

def is_dark(hex_color: str) -> bool:
    """Determine if a color is dark using perceived luminance."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return True
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5
    except ValueError:
        return True

def load_config() -> dict:
    default = {
        "algorithms": ["md5", "sha256"],
        "theme": "Default (Cyberpunk Dark)",
        "custom_theme": {
            "ACCENT": "#4A9EFF",
            "BG_ROOT": "#13131F",
            "BG_CARD": "#1E1E2E",
            "FG_MAIN": "#E0E0F0",
            "FG_DIM": "#8888AA"
        }
    }
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                valid_algos = [a for a in data.get("algorithms", []) if a in ["md5", "sha1", "sha256", "sha512"]]
                if valid_algos:
                    default["algorithms"] = valid_algos
                if "theme" in data:
                    default["theme"] = data["theme"]
                if "custom_theme" in data:
                    default["custom_theme"].update(data["custom_theme"])
    except Exception as e:
        logger.warning(f"Failed to load config: {e}")
    return default

def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f)
        logger.info("Saved configuration successfully.")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")

def get_current_theme_colors(config: dict) -> dict:
    theme_name = config.get("theme", "Default (Cyberpunk Dark)")
    if theme_name == "Custom Theme":
        custom = config.get("custom_theme", {})
        default_theme = THEMES["Default (Cyberpunk Dark)"]
        return {k: custom.get(k, default_theme[k]) for k in default_theme}
    return THEMES.get(theme_name, THEMES["Default (Cyberpunk Dark)"])
