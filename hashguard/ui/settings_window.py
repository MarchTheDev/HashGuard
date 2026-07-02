import re
import sys
import os
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter.colorchooser import askcolor
import webbrowser

from hashguard.config import (
    VERSION, CREATOR, GITHUB_REPO, THEMES, SUCCESS, ERROR, WARNING,
    get_current_theme_colors, save_config, adjust_color, generate_theme_from_accent, is_dark
)
from hashguard.updater import check_latest_release, download_file
from hashguard.ui.components import apply_theme_to_widget

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("740x580")
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
        w = 740
        h = 580
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self):
        self.theme_role = "root"
        
        # Clean segmented flat tabview inspired by GhostHunterPro
        self.tabview = ctk.CTkTabview(self, corner_radius=16, border_width=1)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)
        
        self.tab_about = self.tabview.add("About")
        self.tab_appearance = self.tabview.add("Appearance")
        self.tab_updates = self.tabview.add("Updates")
        
        self._build_about_tab()
        self._build_appearance_tab()
        self._build_updates_tab()
        
    def _build_about_tab(self):
        self.tab_about.grid_columnconfigure(0, weight=1)
        self.tab_about.theme_role = "card"
        
        # Large minimalist logo & metadata info card
        logo_frame = ctk.CTkFrame(self.tab_about, fg_color="transparent")
        logo_frame.grid(row=0, column=0, pady=(40, 20), sticky="n")
        
        title_lbl = ctk.CTkLabel(logo_frame, text="🔒  HashGuard", font=("JetBrains Mono", 28, "bold"))
        title_lbl.theme_role = "accent"
        title_lbl.pack(pady=2)
        
        meta_lbl = ctk.CTkLabel(logo_frame, text=f"Version v{VERSION}  •  Created by {CREATOR}", font=("Segoe UI", 12, "bold"))
        meta_lbl.theme_role = "dim"
        meta_lbl.pack(pady=4)
        
        # Framed detail box resembling game hub libraries in GHP
        details_box = ctk.CTkFrame(self.tab_about, corner_radius=12, border_width=1, border_color="#333344")
        details_box.theme_role = "card"
        details_box.grid(row=1, column=0, padx=40, pady=(0, 30), sticky="ew")
        
        desc_txt = (
            "An elegant, high-performance offline integrity validator designed to calculate, "
            "tweak, and parse cryptographic file checksums (MD5, SHA-1, SHA-256, SHA-512).\n\n"
            "Fully compatible with automated push actions, parallel hashing threads, "
            "drag-and-drop text listings, custom aesthetic palettes, and secure automated self-updates."
        )
        desc_lbl = ctk.CTkLabel(details_box, text=desc_txt, font=("Segoe UI", 12), wraplength=540, justify="center")
        desc_lbl.theme_role = "main"
        desc_lbl.pack(padx=20, pady=20)
        
        gh_btn = ctk.CTkButton(
            self.tab_about, 
            text="GitHub Repository ↗", 
            font=("Segoe UI", 13, "bold"),
            height=38,
            corner_radius=8,
            command=self._open_github
        )
        gh_btn.theme_role = "accent"
        gh_btn.grid(row=2, column=0, pady=10)

    def _open_github(self):
        webbrowser.open(f"https://github.com/{GITHUB_REPO}")

    def _build_appearance_tab(self):
        self.tab_appearance.theme_role = "card"
        
        # Dual-column responsive layout replicating the Settings panels in GhostHunterPro v3.0
        main_layout = ctk.CTkFrame(self.tab_appearance, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=12, pady=12)
        main_layout.grid_columnconfigure(0, weight=11) # Customizer panel
        main_layout.grid_columnconfigure(1, weight=9)  # Interactive Side Actions card
        main_layout.grid_rowconfigure(0, weight=1)
        
        # COLUMN 0: Custom Theme Configurator
        self.left_panel = ctk.CTkFrame(main_layout, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_panel.grid_columnconfigure(1, weight=1)
        
        theme_lbl = ctk.CTkLabel(self.left_panel, text="Theme Preset:", font=("Segoe UI", 12, "bold"))
        theme_lbl.theme_role = "main"
        theme_lbl.grid(row=0, column=0, sticky="w", pady=(0, 12))
        
        themes_list = list(THEMES.keys()) + ["Custom Theme"]
        current_theme = self.parent._config.get("theme", "Default (Cyberpunk Dark)")
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.left_panel,
            values=themes_list,
            command=self._on_theme_changed,
            font=("Segoe UI", 11),
            corner_radius=8
        )
        self.theme_menu.set(current_theme)
        self.theme_menu.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))
        
        # Sleek dividing border line
        sep = ctk.CTkFrame(self.left_panel, height=1, fg_color="#333344")
        sep.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        
        # Swatches grid list
        self.color_vars = {}
        self.color_pick_btns = {}
        
        color_roles = [
            ("ACCENT", "Accent Color"),
            ("BG_ROOT", "Root Background"),
            ("BG_CARD", "Card Background"),
            ("FG_MAIN", "Main Text"),
            ("FG_DIM", "Dim Text")
        ]
        
        current_colors = get_current_theme_colors(self.parent._config)
        
        row_i = 2
        for key, label in color_roles:
            lbl = ctk.CTkLabel(self.left_panel, text=label, font=("Segoe UI", 12))
            lbl.theme_role = "main"
            lbl.grid(row=row_i, column=0, sticky="w", pady=6)
            
            val = current_colors.get(key, "#FFFFFF")
            var = tk.StringVar(value=val)
            self.color_vars[key] = var
            var.trace_add("write", lambda name, idx, mode, k=key, v=var: self._on_color_typing(k, v))
            
            # The button itself displays the hex value inside its color background - elegant GHP style!
            pick_btn = ctk.CTkButton(
                self.left_panel,
                text=val,
                fg_color=val,
                hover_color=adjust_color(val, 0.1),
                text_color="#FFFFFF" if is_dark(val) else "#000000",
                font=("JetBrains Mono", 11, "bold"),
                height=32,
                corner_radius=8,
                command=lambda k=key: self._open_color_picker(k)
            )
            pick_btn.grid(row=row_i, column=1, sticky="ew", padx=(12, 0), pady=6)
            self.color_pick_btns[key] = pick_btn
            
            row_i += 1
            
        # COLUMN 1: GHP-Style Command Panels
        self.right_panel = ctk.CTkFrame(main_layout, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure((0, 1), weight=1)
        
        # Panel A: Magic Auto-Generator Card
        self.magic_card = ctk.CTkFrame(self.right_panel, corner_radius=14, border_width=1, border_color="#333344")
        self.magic_card.theme_role = "card"
        self.magic_card.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.magic_card.grid_columnconfigure(0, weight=1)
        
        mag_title = ctk.CTkLabel(self.magic_card, text="⚡  Theme Auto-Generator", font=("Segoe UI", 13, "bold"))
        mag_title.theme_role = "accent"
        mag_title.pack(anchor="w", padx=16, pady=(16, 5))
        
        mag_desc = ctk.CTkLabel(
            self.magic_card,
            text=(
                "Choose any accent color and let our color algorithm desaturate and "
                "contrast corresponding cards, backgrounds, and text blocks seamlessly."
            ),
            font=("Segoe UI", 11),
            wraplength=230,
            justify="left"
        )
        mag_desc.theme_role = "dim"
        mag_desc.pack(anchor="w", padx=16, pady=(0, 18))
        
        self.magic_btn = ctk.CTkButton(
            self.magic_card,
            text="Auto-Generate Theme",
            font=("Segoe UI", 12, "bold"),
            height=36,
            corner_radius=8,
            command=self._magic_generate_theme
        )
        self.magic_btn.theme_role = "neutral"
        self.magic_btn.pack(fill="x", padx=16, pady=(0, 16))
        
        # Panel B: Save & Apply Card
        self.save_card = ctk.CTkFrame(self.right_panel, corner_radius=14, border_width=1, border_color="#333344")
        self.save_card.theme_role = "card"
        self.save_card.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.save_card.grid_columnconfigure(0, weight=1)
        
        save_title = ctk.CTkLabel(self.save_card, text="💾  Save Changes", font=("Segoe UI", 13, "bold"))
        save_title.theme_role = "main"
        save_title.pack(anchor="w", padx=16, pady=(16, 5))
        
        save_desc = ctk.CTkLabel(
            self.save_card,
            text=(
                "All edits reflect on your active interface immediately. "
                "Commit these changes to set this custom layout as your permanent default."
            ),
            font=("Segoe UI", 11),
            wraplength=230,
            justify="left"
        )
        save_desc.theme_role = "dim"
        save_desc.pack(anchor="w", padx=16, pady=(0, 18))
        
        self.save_theme_btn = ctk.CTkButton(
            self.save_card, 
            text="Save & Apply Theme", 
            font=("Segoe UI", 13, "bold"),
            height=38,
            corner_radius=8,
            command=self._save_custom_theme
        )
        self.save_theme_btn.theme_role = "accent"
        self.save_theme_btn.pack(fill="x", padx=16, pady=(0, 16))

    def _on_color_typing(self, key, var):
        val = var.get().strip()
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", val):
            self._update_color_button(key, val)

    def _update_color_button(self, key, hex_color):
        btn = self.color_pick_btns.get(key)
        if btn:
            btn.configure(
                fg_color=hex_color,
                hover_color=adjust_color(hex_color, 0.1),
                text=hex_color,
                text_color="#FFFFFF" if is_dark(hex_color) else "#000000"
            )

    def _open_color_picker(self, key):
        current_theme = self.theme_menu.get()
        if current_theme != "Custom Theme":
            self.theme_menu.set("Custom Theme")
            self._on_theme_changed("Custom Theme")
            
        current_color = self.color_vars[key].get().strip()
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", current_color):
            current_color = "#FFFFFF"
            
        _, picked_hex = askcolor(color=current_color, title=f"Choose {key}")
        if picked_hex:
            picked_hex = picked_hex.upper()
            self.color_vars[key].set(picked_hex)
            self._update_color_button(key, picked_hex)
            self._preview_theme_live()

    def _magic_generate_theme(self):
        current_accent = self.color_vars["ACCENT"].get().strip()
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", current_accent):
            current_accent = "#4A9EFF"
            
        _, picked_hex = askcolor(color=current_accent, title="Pick Theme Base Accent Color")
        if not picked_hex:
            return
            
        # Instantly toggle Option Menu
        self.theme_menu.set("Custom Theme")
        self._on_theme_changed("Custom Theme")
        
        generated = generate_theme_from_accent(picked_hex)
        for key, val in generated.items():
            self.color_vars[key].set(val)
            self._update_color_button(key, val)
            
        self._preview_theme_live()

    def _preview_theme_live(self):
        temp_colors = {}
        for key, var in self.color_vars.items():
            val = var.get().strip().upper()
            if re.fullmatch(r"#[0-9A-F]{6}", val):
                temp_colors[key] = val
            else:
                return
                
        self.parent._theme_colors = temp_colors
        self.parent.apply_theme()
        self.apply_theme()

    def _on_theme_changed(self, choice):
        self.parent._config["theme"] = choice
        
        if choice != "Custom Theme":
            preset_colors = THEMES[choice]
            for key, val in preset_colors.items():
                self.color_vars[key].set(val)
                self._update_color_button(key, val)
                
            save_config(self.parent._config)
            self.parent.apply_theme()
            self.apply_theme()
        else:
            saved_custom = self.parent._config.get("custom_theme", {})
            for key, val in saved_custom.items():
                self.color_vars[key].set(val)
                self._update_color_button(key, val)

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
        
        # Centered minimalist updates hub - clean GHP design
        header_frame = ctk.CTkFrame(self.tab_updates, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(35, 10), sticky="n")
        
        title = ctk.CTkLabel(header_frame, text="Software Releases Hub", font=("Segoe UI", 16, "bold"))
        title.theme_role = "accent"
        title.pack()
        
        # Details card
        info_card = ctk.CTkFrame(self.tab_updates, corner_radius=12, border_width=1, border_color="#333344")
        info_card.theme_role = "card"
        info_card.grid(row=1, column=0, columnspan=2, padx=40, pady=10, sticky="ew")
        info_card.grid_columnconfigure((0, 1), weight=1)
        
        curr_title = ctk.CTkLabel(info_card, text="Installed Version:", font=("Segoe UI", 12, "bold"))
        curr_title.theme_role = "main"
        curr_title.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        curr_val = ctk.CTkLabel(info_card, text=f"v{VERSION}", font=("JetBrains Mono", 12, "bold"))
        curr_val.theme_role = "main"
        curr_val.grid(row=0, column=1, sticky="e", padx=20, pady=15)
        
        late_title = ctk.CTkLabel(info_card, text="Latest on GitHub:", font=("Segoe UI", 12, "bold"))
        late_title.theme_role = "main"
        late_title.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        self.latest_ver_lbl = ctk.CTkLabel(info_card, text="Unknown (Check now)", font=("JetBrains Mono", 12))
        self.latest_ver_lbl.theme_role = "dim"
        self.latest_ver_lbl.grid(row=1, column=1, sticky="e", padx=20, pady=(0, 15))
        
        self.update_status_lbl = ctk.CTkLabel(
            self.tab_updates, 
            text="Press Check for Updates to query GitHub.", 
            font=("Segoe UI", 12, "italic"),
            wraplength=480,
            justify="center"
        )
        self.update_status_lbl.theme_role = "dim"
        self.update_status_lbl.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.update_progress = ctk.CTkProgressBar(self.tab_updates, height=6, corner_radius=3)
        self.update_progress.theme_role = "progress"
        self.update_progress.grid(row=3, column=0, columnspan=2, padx=40, pady=(0, 20))
        self.update_progress.grid_remove()
        
        btn_frame = ctk.CTkFrame(self.tab_updates, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 25))
        
        self.check_btn = ctk.CTkButton(
            btn_frame, 
            text="Check for Updates", 
            font=("Segoe UI", 13, "bold"),
            height=36,
            corner_radius=8,
            command=self._check_updates
        )
        self.check_btn.theme_role = "accent"
        self.check_btn.pack(side="left", padx=10)
        
        self.install_btn = ctk.CTkButton(
            btn_frame, 
            text="Download & Install", 
            font=("Segoe UI", 13, "bold"),
            height=36,
            corner_radius=8,
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
        self.configure(fg_color=theme["BG_ROOT"])
        
        self.tab_about.configure(fg_color=theme["BG_CARD"])
        self.tab_appearance.configure(fg_color=theme["BG_CARD"])
        self.tab_updates.configure(fg_color=theme["BG_CARD"])
        
        self.tabview.configure(
            fg_color=theme["BG_CARD"],
            border_color=adjust_color(theme["BG_CARD"], 0.1),
            segmented_button_fg_color=theme["BG_ROOT"],
            segmented_button_selected_color=theme["ACCENT"],
            segmented_button_unselected_color=theme["BG_CARD"],
            segmented_button_selected_hover_color=adjust_color(theme["ACCENT"], -0.1),
            segmented_button_unselected_hover_color=adjust_color(theme["BG_CARD"], 0.05),
            text_color=theme["FG_MAIN"]
        )
        
        def recurse(widget):
            apply_theme_to_widget(widget, theme)
            for child in widget.winfo_children():
                recurse(child)
                
        recurse(self)
        self.update_idletasks()
