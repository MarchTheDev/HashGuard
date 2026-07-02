import re
import sys
import os
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import webbrowser

from hashguard.config import (
    VERSION, CREATOR, GITHUB_REPO, THEMES, SUCCESS, ERROR, WARNING,
    get_current_theme_colors, save_config, adjust_color
)
from hashguard.updater import check_latest_release, download_file
from hashguard.ui.components import apply_theme_to_widget

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("620x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._center_window()
        self._build_ui()
        self.apply_theme()
        
    def _center_window(self):
        self.update_idletasks()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        w = 620
        h = 520
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self):
        self.theme_role = "root"
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=14, pady=14)
        
        self.tab_about = self.tabview.add("About")
        self.tab_appearance = self.tabview.add("Appearance")
        self.tab_updates = self.tabview.add("Updates")
        
        self._build_about_tab()
        self._build_appearance_tab()
        self._build_updates_tab()
        
    def _build_about_tab(self):
        self.tab_about.grid_columnconfigure(0, weight=1)
        self.tab_about.theme_role = "card"
        
        title_lbl = ctk.CTkLabel(self.tab_about, text="HashGuard", font=("Segoe UI", 24, "bold"))
        title_lbl.theme_role = "accent"
        title_lbl.grid(row=0, column=0, pady=(24, 4))
        
        ver_lbl = ctk.CTkLabel(self.tab_about, text=f"Version v{VERSION}", font=("Segoe UI", 14, "bold"))
        ver_lbl.theme_role = "main"
        ver_lbl.grid(row=1, column=0, pady=2)
        
        creator_lbl = ctk.CTkLabel(self.tab_about, text=f"Created by {CREATOR}", font=("Segoe UI", 12, "italic"))
        creator_lbl.theme_role = "dim"
        creator_lbl.grid(row=2, column=0, pady=(0, 24))
        
        desc_txt = (
            "A clean, robust, and offline checksum utility designed to verify and "
            "generate hash hashes (MD5, SHA-1, SHA-256, SHA-512) for software integrity. "
            "Features include parallel thread calculation, smart bulk text file verification, "
            "drag-and-drop mechanics, fully customizable colors, and secure self-updates."
        )
        desc_lbl = ctk.CTkLabel(self.tab_about, text=desc_txt, font=("Segoe UI", 12), wraplength=480, justify="center")
        desc_lbl.theme_role = "dim"
        desc_lbl.grid(row=3, column=0, padx=20, pady=(0, 30))
        
        gh_btn = ctk.CTkButton(
            self.tab_about, 
            text="GitHub Repository ↗", 
            font=("Segoe UI", 13, "bold"),
            command=self._open_github
        )
        gh_btn.theme_role = "accent"
        gh_btn.grid(row=4, column=0, pady=10)

    def _open_github(self):
        webbrowser.open(f"https://github.com/{GITHUB_REPO}")

    def _build_appearance_tab(self):
        self.tab_appearance.grid_columnconfigure((0, 1), weight=1)
        self.tab_appearance.theme_role = "card"
        
        theme_lbl = ctk.CTkLabel(self.tab_appearance, text="Select Theme Preset:", font=("Segoe UI", 13, "bold"))
        theme_lbl.theme_role = "main"
        theme_lbl.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        themes_list = list(THEMES.keys()) + ["Custom Theme"]
        current_theme = self.parent._config.get("theme", "Default (Cyberpunk Dark)")
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.tab_appearance,
            values=themes_list,
            command=self._on_theme_changed,
            font=("Segoe UI", 12)
        )
        self.theme_menu.set(current_theme)
        self.theme_menu.grid(row=0, column=1, sticky="ew", padx=20, pady=(15, 5))
        
        # Color Editor Container
        self.colors_frame = ctk.CTkFrame(self.tab_appearance, fg_color="transparent")
        self.colors_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=15)
        self.colors_frame.grid_columnconfigure(1, weight=1)
        
        self.color_vars = {}
        self.color_previews = {}
        self.color_entries = {}
        
        color_roles = [
            ("ACCENT", "Accent Accent:"),
            ("BG_ROOT", "Root Background:"),
            ("BG_CARD", "Card Background:"),
            ("FG_MAIN", "Main Text:"),
            ("FG_DIM", "Dim Text:")
        ]
        
        current_colors = get_current_theme_colors(self.parent._config)
        
        row_i = 0
        for key, label in color_roles:
            lbl = ctk.CTkLabel(self.colors_frame, text=label, font=("Segoe UI", 12))
            lbl.theme_role = "main"
            lbl.grid(row=row_i, column=0, sticky="w", pady=5)
            
            var = tk.StringVar(value=current_colors.get(key, ""))
            self.color_vars[key] = var
            var.trace_add("write", lambda name, idx, mode, k=key, v=var: self._on_color_typing(k, v))
            
            entry = ctk.CTkEntry(self.colors_frame, textvariable=var, font=("Consolas", 12), width=120)
            entry.theme_role = "entry"
            entry.grid(row=row_i, column=1, sticky="ew", padx=(10, 10), pady=5)
            self.color_entries[key] = entry
            
            preview = tk.Canvas(self.colors_frame, width=20, height=20, bd=0, highlightthickness=1)
            preview.grid(row=row_i, column=2, padx=(0, 10), pady=5)
            self.color_previews[key] = preview
            self._update_preview_patch(key, var.get())
            
            row_i += 1
            
        self.save_theme_btn = ctk.CTkButton(
            self.tab_appearance, 
            text="Save Custom Theme", 
            font=("Segoe UI", 13, "bold"),
            command=self._save_custom_theme
        )
        self.save_theme_btn.theme_role = "accent"
        self.save_theme_btn.grid(row=2, column=0, columnspan=2, pady=(5, 15))
        
        self._toggle_color_inputs(current_theme)

    def _toggle_color_inputs(self, theme_choice):
        state = "normal" if theme_choice == "Custom Theme" else "disabled"
        for key, entry in self.color_entries.items():
            entry.configure(state=state)
        
        if theme_choice == "Custom Theme":
            self.save_theme_btn.grid()
        else:
            self.save_theme_btn.grid_remove()

    def _on_color_typing(self, key, var):
        val = var.get().strip()
        self._update_preview_patch(key, val)

    def _update_preview_patch(self, key, hex_color):
        preview = self.color_previews.get(key)
        if preview and re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_color):
            preview.configure(bg=hex_color)

    def _on_theme_changed(self, choice):
        self.parent._config["theme"] = choice
        
        if choice != "Custom Theme":
            preset_colors = THEMES[choice]
            for key, val in preset_colors.items():
                self.color_vars[key].set(val)
                self._update_preview_patch(key, val)
                
            save_config(self.parent._config)
            self.parent.apply_theme()
            self.apply_theme()
        else:
            saved_custom = self.parent._config.get("custom_theme", {})
            for key, val in saved_custom.items():
                self.color_vars[key].set(val)
                self._update_preview_patch(key, val)
                
        self._toggle_color_inputs(choice)

    def _save_custom_theme(self):
        custom_theme = {}
        for key, var in self.color_vars.items():
            val = var.get().strip().upper()
            if not re.fullmatch(r"#[0-9A-F]{6}", val):
                messagebox.showerror(
                    "Invalid Color", 
                    f"Invalid hex code for {key}: '{val}'. Must be in format #RRGGBB (e.g. #FF2255)"
                )
                return
            custom_theme[key] = val
            
        self.parent._config["custom_theme"] = custom_theme
        self.parent._config["theme"] = "Custom Theme"
        
        save_config(self.parent._config)
        self.parent.apply_theme()
        self.apply_theme()
        messagebox.showinfo("Theme Saved", "Your custom theme has been successfully saved and applied!")

    def _build_updates_tab(self):
        self.tab_updates.grid_columnconfigure((0, 1), weight=1)
        self.tab_updates.theme_role = "card"
        
        curr_title = ctk.CTkLabel(self.tab_updates, text="Current Version Installed:", font=("Segoe UI", 12, "bold"))
        curr_title.theme_role = "main"
        curr_title.grid(row=0, column=0, sticky="w", padx=30, pady=(25, 5))
        
        curr_val = ctk.CTkLabel(self.tab_updates, text=f"v{VERSION}", font=("Segoe UI", 13))
        curr_val.theme_role = "main"
        curr_val.grid(row=0, column=1, sticky="w", padx=30, pady=(25, 5))
        
        late_title = ctk.CTkLabel(self.tab_updates, text="Latest Version Available:", font=("Segoe UI", 12, "bold"))
        late_title.theme_role = "main"
        late_title.grid(row=1, column=0, sticky="w", padx=30, pady=5)
        
        self.latest_ver_lbl = ctk.CTkLabel(self.tab_updates, text="Unknown (Check now)", font=("Segoe UI", 13))
        self.latest_ver_lbl.theme_role = "dim"
        self.latest_ver_lbl.grid(row=1, column=1, sticky="w", padx=30, pady=5)
        
        self.update_status_lbl = ctk.CTkLabel(
            self.tab_updates, 
            text="Press Check for Updates to query GitHub.", 
            font=("Segoe UI", 12, "italic"),
            wraplength=480,
            justify="center"
        )
        self.update_status_lbl.theme_role = "dim"
        self.update_status_lbl.grid(row=2, column=0, columnspan=2, pady=25)
        
        self.update_progress = ctk.CTkProgressBar(self.tab_updates, height=6)
        self.update_progress.theme_role = "progress"
        self.update_progress.grid(row=3, column=0, columnspan=2, padx=40, pady=(0, 20))
        self.update_progress.grid_remove()
        
        btn_frame = ctk.CTkFrame(self.tab_updates, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.check_btn = ctk.CTkButton(
            btn_frame, 
            text="Check for Updates", 
            font=("Segoe UI", 13, "bold"),
            command=self._check_updates
        )
        self.check_btn.theme_role = "accent"
        self.check_btn.pack(side="left", padx=10)
        
        self.install_btn = ctk.CTkButton(
            btn_frame, 
            text="Download & Install", 
            font=("Segoe UI", 13, "bold"),
            command=self._install_update
        )
        self.install_btn.theme_role = "neutral"
        self.install_btn.pack(side="left", padx=10)
        self.install_btn.configure(state="disabled")

    def _check_updates(self):
        self.check_btn.configure(state="disabled", text="Checking…")
        self.update_status_lbl.configure(text="Connecting to GitHub...", text_color=self.parent._get_color_for_role("FG_DIM"))
        
        def worker():
            res = check_latest_release(GITHUB_REPO)
            self.after(0, lambda: self._on_check_complete(res))
            
        threading.Thread(target=worker, daemon=True).start()
        
    def _on_check_complete(self, res):
        self.check_btn.configure(state="normal", text="Check for Updates")
        if not res:
            self.update_status_lbl.configure(
                text="Could not reach GitHub. Please verify your internet connection.",
                text_color=ERROR
            )
            return
            
        latest_ver = res["version"].lstrip("v")
        current_ver = VERSION.lstrip("v")
        
        self.latest_ver_lbl.configure(text=f"v{latest_ver}")
        self.latest_ver_lbl.theme_role = "main"
        
        try:
            curr_parts = [int(p) for p in current_ver.split(".")]
            late_parts = [int(p) for p in latest_ver.split(".")]
            has_update = late_parts > curr_parts
        except Exception:
            has_update = latest_ver != current_ver
            
        if has_update:
            self.update_status_lbl.configure(
                text=f"Update found: Version v{latest_ver} is available!",
                text_color=SUCCESS
            )
            
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
                        
            if self.setup_asset:
                self.install_btn.configure(state="normal", text="Download & Install Update")
            else:
                self.install_btn.configure(state="normal", text="View Release Page ↗")
        else:
            self.update_status_lbl.configure(
                text="You are using the latest official release version of HashGuard.",
                text_color=SUCCESS
            )
            self.install_btn.configure(state="disabled")

    def _install_update(self):
        if not getattr(self, "setup_asset", None):
            import webbrowser
            webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
            return
            
        self.install_btn.configure(state="disabled", text="Downloading…")
        self.check_btn.configure(state="disabled")
        self.update_progress.grid()
        self.update_progress.set(0)
        
        url = self.setup_asset["browser_download_url"]
        filename = self.setup_asset["name"]
        
        import tempfile
        temp_dir = tempfile.gettempdir()
        dest_path = os.path.join(temp_dir, filename)
        
        def download_worker():
            success = download_file(url, dest_path, progress_cb=self._update_download_progress)
            self.after(0, lambda: self._on_download_complete(success, dest_path))
            
        threading.Thread(target=download_worker, daemon=True).start()
        
    def _update_download_progress(self, pct):
        self.after(0, lambda: self.update_progress.set(pct))
        
    def _on_download_complete(self, success, dest_path):
        self.update_progress.grid_remove()
        if success:
            self.update_status_lbl.configure(
                text="Download completed! Launching installer...",
                text_color=SUCCESS
            )
            try:
                if sys.platform == "win32":
                    os.startfile(dest_path)
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", dest_path])
                
                self.parent.destroy()
                sys.exit(0)
            except Exception as e:
                self.update_status_lbl.configure(
                    text=f"Failed to launch downloaded installer. Saved to: {dest_path}",
                    text_color=ERROR
                )
        else:
            self.update_status_lbl.configure(text="Download aborted or failed. Try again.", text_color=ERROR)
            self.install_btn.configure(state="normal", text="Download & Install Update")
            self.check_btn.configure(state="normal")

    def apply_theme(self):
        theme = get_current_theme_colors(self.parent._config)
        
        # FIX: Changed 'bg_color' to 'fg_color' for CTkToplevel configuration
        self.configure(fg_color=theme["BG_ROOT"])
        
        self.tabview.configure(
            segmented_button_fg_color=theme["BG_CARD"],
            segmented_button_selected_color=theme["ACCENT"],
            segmented_button_selected_hover_color=adjust_color(theme["ACCENT"], -0.1),
            segmented_button_unselected_color=theme["BG_CARD"],
            segmented_button_unselected_hover_color=adjust_color(theme["BG_CARD"], 0.05),
            text_color=theme["FG_MAIN"]
        )
        
        def recurse(widget):
            apply_theme_to_widget(widget, theme)
            for child in widget.winfo_children():
                recurse(child)
                
        recurse(self)
        
        for key, canvas in self.color_previews.items():
            canvas.configure(highlightbackground=adjust_color(theme["BG_CARD"], 0.25))
            
        self.update_idletasks()
