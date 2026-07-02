import json
import logging
import os
import sys
import threading
from pathlib import Path
import webview

from hashguard.config import (
    load_config, save_config, VERSION, CREATOR, GITHUB_REPO, generate_theme_from_accent
)
from hashguard.hashing import compute_hashes, parse_hash_text, format_size
from hashguard.updater import check_latest_release, download_file
from hashguard.ui.html_template import HTML_CONTENT

logger = logging.getLogger("HashGuard.API")

class HashGuardAPI:
    def __init__(self, window):
        self.window = window
        self.config = load_config()
        self.filepath = ""
        self.hashes = {}
        self.loaded_hashes = {}
        self.setup_asset = None

    def get_init_details(self):
        """Loads and pushes current application details to JS frontend."""
        details = {
            "version": VERSION,
            "creator": CREATOR,
            "repo": GITHUB_REPO,
            "theme": self.config.get("theme", "Default (Midnight Glow)"),
            "algorithms": self.config.get("algorithms", ["md5", "sha256"]),
            "customTheme": self.config.get("custom_theme", {})
        }
        return json.dumps(details)

    def select_file(self):
        """Opens native file dialog wrapper and starts async hashing."""
        file_types = ('All files (*.*)',)
        result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        if result and len(result) > 0:
            path = result[0]
            self._load_file_path(path)

    def _load_file_path(self, path):
        self.filepath = path
        filename = os.path.basename(path)
        try:
            size_bytes = os.path.getsize(path)
            display_size = format_size(size_bytes)
        except OSError:
            display_size = "Unknown size"
            
        # Notify Javascript frontend
        self.window.evaluate_js(f"onFileLoaded({json.dumps(filename)}, {json.dumps(display_size)})")
        self._async_compute()

    def _async_compute(self):
        selected_algos = self.config.get("algorithms", ["md5", "sha256"])
        
        def run():
            try:
                def progress_callback(pct):
                    self.window.evaluate_js(f"updateProgress({pct})")
                    
                hashes = compute_hashes(self.filepath, selected_algos, progress_cb=progress_callback)
                self.hashes = hashes
                self.window.evaluate_js(f"onHashingDone({json.dumps(json.dumps(hashes))})")
                logger.info(f"Computed hashes successfully for: {self.filepath}")
            except Exception as e:
                logger.exception("Error during async compute thread:")
                self.window.evaluate_js(f"alert('Error computing hashes: {str(e)}')")
                
        threading.Thread(target=run, daemon=True).start()

    def recompute_hashes(self):
        """Forces re-calculation of hashes."""
        if self.filepath:
            self._async_compute()
        else:
            self.window.evaluate_js("alert('No target file selected!')")

    def select_theme(self, theme_name):
        """Saves selected theme configuration preset."""
        self.config["theme"] = theme_name
        save_config(self.config)
        logger.info(f"Selected Theme preset: {theme_name}")

    def save_custom_colors(self, colors_json):
        """Saves theme creator color presets permanently."""
        try:
            colors = json.loads(colors_json)
            self.config["custom_theme"] = colors
            self.config["theme"] = "Custom Theme"
            save_config(self.config)
            logger.info("Custom theme settings successfully saved.")
        except Exception as e:
            logger.error(f"Failed to save custom theme colors: {e}")

    def generate_from_accent(self, accent_hex):
        """Automatically generates matching colorsys dark palettes from an accent color."""
        generated = generate_theme_from_accent(accent_hex)
        return json.dumps(generated)

    def select_hash_file(self):
        """Opens native folder dialog to parse and load .txt reports."""
        file_types = ('Text files (*.txt)', 'All files (*.*)')
        result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        if result and len(result) > 0:
            path = result[0]
            self._load_hash_file_path(path)

    def _load_hash_file_path(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            try:
                with open(path, "r", encoding="latin-1") as f:
                    text = f.read()
            except Exception as e:
                self.window.evaluate_js(f"alert('Failed to read hash report file: {str(e)}')")
                return
                
        parsed = parse_hash_text(text)
        if not parsed:
            self.window.evaluate_js("alert('No valid hashes found. Report must contain lines like MD5: or SHA-256:...')")
            return
            
        self.loaded_hashes = parsed
        filename = os.path.basename(path)
        summary = ", ".join([algo.upper() for algo in parsed])
        
        self.window.evaluate_js(f"onHashFileLoaded({json.dumps(filename)}, {json.dumps(summary)}, {json.dumps(json.dumps(parsed))})")
        logger.info(f"Loaded external report successfully: {path}")

    def export_hashes_report(self):
        """Opens native save-file dialog to export reports."""
        if not self.hashes:
            self.window.evaluate_js("alert('Please compute hashes first!')")
            return
            
        file_types = ('Text files (*.txt)',)
        default_name = "Hash.txt"
        if self.filepath:
            default_name = Path(self.filepath).stem + " - Hash.txt"
            
        result = self.window.create_file_dialog(
            webview.SAVE_DIALOG, 
            directory=os.path.dirname(self.filepath) if self.filepath else "",
            save_filename=default_name,
            file_types=file_types
        )
        if result:
            path = result
            try:
                with open(path, "w", encoding="utf-8") as f:
                    lines = []
                    if self.filepath:
                        lines.append(f"Filename: {os.path.basename(self.filepath)}\n")
                    for algo in ("md5", "sha1", "sha256", "sha512"):
                        if algo in self.hashes:
                            lines.append(f"{algo.upper()}: {self.hashes[algo]}")
                    f.write("\n".join(lines))
                self.window.evaluate_js(f"showToast('💾 Exported report successfully!')")
            except Exception as e:
                self.window.evaluate_js(f"alert('Failed to save file: {str(e)}')")

    def copy_clipboard(self, text):
        """Cross-platform clipboard append helper utilizing lightweight standard library tkinter."""
        try:
            import tkinter as tk
            r = tk.Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(text)
            r.update()
            r.destroy()
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")

    def get_clipboard(self):
        """Cross-platform clipboard read helper."""
        try:
            import tkinter as tk
            r = tk.Tk()
            r.withdraw()
            text = r.clipboard_get()
            r.destroy()
            return text
        except Exception as e:
            logger.error(f"Failed to fetch clipboard: {e}")
            return ""

    def open_github_link(self):
        import webbrowser
        webbrowser.open(f"https://github.com/{GITHUB_REPO}")

    def check_updates_hub(self):
        """Queries GitHub API for latest releases and checks against current client version."""
        res = check_latest_release(GITHUB_REPO)
        if not res:
            return json.dumps({
                "update_available": False, 
                "latest_version": VERSION, 
                "release_notes": "Could not contact GitHub releases server."
            })
            
        latest_ver = res["version"].lstrip("v")
        current_ver = VERSION.lstrip("v")
        
        try:
            curr_parts = [int(p) for p in current_ver.split(".")]
            late_parts = [int(p) for p in latest_ver.split(".")]
            has_update = late_parts > curr_parts
        except Exception:
            has_update = latest_ver != current_ver
            
        self.setup_asset = None
        for asset in res.get("assets", []):
            name = asset.get("name", "")
            if name.endswith(".exe") and "setup" in name.lower():
                self.setup_asset = asset
                break
                
        if not self.setup_asset:
            for asset in res.get("assets", []):
                if asset.get("name", "").endswith(".exe"):
                    self.setup_asset = asset
                    break
                    
        return json.dumps({
            "update_available": has_update,
            "latest_version": latest_ver,
            "release_notes": res.get("body", "No release notes found.")
        })

    def download_and_launch_setup(self):
        """Asynchronously downloads the updater setup file and launches it, shutting down the app."""
        if not getattr(self, "setup_asset", None):
            import webbrowser
            webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
            return True
            
        url = self.setup_asset["browser_download_url"]
        filename = self.setup_asset["name"]
        
        import tempfile
        temp_dir = tempfile.gettempdir()
        dest_path = os.path.join(temp_dir, filename)
        
        def run():
            success = download_file(url, dest_path)
            if success:
                try:
                    if sys.platform == "win32":
                        os.startfile(dest_path)
                    else:
                        import subprocess
                        subprocess.Popen(["xdg-open", dest_path])
                    self.window.destroy()
                    sys.exit(0)
                except Exception as e:
                    logger.error(f"Failed to launch downloaded installer: {e}")
            else:
                self.window.evaluate_js("alert('Update download aborted or failed!')")
                
        threading.Thread(target=run, daemon=True).start()
        return True


def launch_gui():
    """Boots the pywebview window with GHP HTML/CSS rendering."""
    # Ensure window is centered on screen
    window = webview.create_window(
        title="HashGuard — Cryptographic Hub",
        html=HTML_CONTENT,
        width=1120, # Increased size to make everything comfortable, clear, and perfectly proportioned on startup
        height=760,
        resizable=True,
        min_size=(980, 680),
        background_color="#070B14"
    )
    
    # Expose the API
    api = HashGuardAPI(window)
    window.js_api = api
    
    # Disable automatic opening of DevTools in pywebview
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    
    # Start webview loop with debug=False so that DevTools/Inspector does not open on startup
    webview.start(debug=False)
