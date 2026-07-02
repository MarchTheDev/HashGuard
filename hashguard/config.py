import json
import logging
import re
import colorsys
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
    "Default (Midnight Glow)": {
        "ACCENT": "#1AC7FF",
        "BG_ROOT": "#070B14",
        "BG_CARD": "#12192A",
        "FG_MAIN": "#ECF2FB",
        "FG_DIM": "#8A96AD"
    },
    "Midnight Blue": {
        "ACCENT": "#4FB9FF",
        "BG_ROOT": "#081019",
        "BG_CARD": "#121C2C",
        "FG_MAIN": "#EFF9FF",
        "FG_DIM": "#7EA8FF"
    },
    "Rubellite Crimson": {
        "ACCENT": "#FF4B75",
        "BG_ROOT": "#110817",
        "BG_CARD": "#1E0E24",
        "FG_MAIN": "#FFF0F3",
        "FG_DIM": "#B3133B"
    },
    "Ember Orange": {
        "ACCENT": "#FF8A3D",
        "BG_ROOT": "#120B0C",
        "BG_CARD": "#231215",
        "FG_MAIN": "#FFEBE8",
        "FG_DIM": "#FF4D6D"
    },
    "Emerald Mint": {
        "ACCENT": "#1FD0A6",
        "BG_ROOT": "#07130F",
        "BG_CARD": "#0F221C",
        "FG_MAIN": "#EEFDF8",
        "FG_DIM": "#3FBF7C"
    }
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

def generate_theme_from_accent(accent_hex: str) -> dict:
    """Generates a cohesive midnight-glow dark theme automatically from a single accent color."""
    accent_hex = accent_hex.lstrip("#")
    if len(accent_hex) != 6:
        accent_hex = "1AC7FF" # fallback
        
    try:
        r, g, b = int(accent_hex[0:2], 16), int(accent_hex[2:4], 16), int(accent_hex[4:6], 16)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # GhostHunterPro themed background values:
        # Base backgrounds are tinted with the accent hue very subtly (low saturation, low value)
        root_r, root_g, root_b = colorsys.hsv_to_rgb(h, min(s * 0.15, 0.08), 0.06)
        bg_root = f"#{int(root_r*255):02X}{int(root_g*255):02X}{int(root_b*255):02X}"
        
        # Card backgrounds are slightly lighter and tinted
        card_r, card_g, card_b = colorsys.hsv_to_rgb(h, min(s * 0.20, 0.12), 0.11)
        bg_card = f"#{int(card_r*255):02X}{int(card_g*255):02X}{int(card_b*255):02X}"
        
        # Crisp Ice-white text and muted slate-gray text (GHP standards)
        fg_main = "#ECF2FB"
        fg_dim = "#8A96AD"
        
        return {
            "ACCENT": f"#{accent_hex.upper()}",
            "BG_ROOT": bg_root,
            "BG_CARD": bg_card,
            "FG_MAIN": fg_main,
            "FG_DIM": fg_dim
        }
    except Exception as e:
        logger.error(f"Error generating theme from accent: {e}")
        return THEMES["Default (Midnight Glow)"]

def load_config() -> dict:
    default = {
        "algorithms": ["md5", "sha256"],
        "theme": "Default (Midnight Glow)",
        "custom_theme": {
            "ACCENT": "#1AC7FF",
            "BG_ROOT": "#070B14",
            "BG_CARD": "#12192A",
            "FG_MAIN": "#ECF2FB",
            "FG_DIM": "#8A96AD"
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
    theme_name = config.get("theme", "Default (Midnight Glow)")
    if theme_name == "Custom Theme":
        custom = config.get("custom_theme", {})
        default_theme = THEMES["Default (Midnight Glow)"]
        return {k: custom.get(k, default_theme[k]) for k in default_theme}
    return THEMES.get(theme_name, THEMES["Default (Midnight Glow)"])
