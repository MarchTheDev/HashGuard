import logging
import os
import threading
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

from hashguard.config import (
    get_current_theme_colors, load_config, save_config, adjust_color, THEMES, SUCCESS, WARNING
)
from hashguard.hashing import (
    compute_hashes, detect_hash_type, parse_hash_text, format_size, HASH_ALGORITHMS
)
from hashguard.ui.components import Toast, apply_theme_to_widget
from hashguard.ui.settings_window import SettingsWindow

logger = logging.getLogger("HashGuard.MainWindow")

class HashGuard(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("HashGuard — File Integrity Checker")
        self._set_initial_window_size()
        
        self._hashes: dict = {}
        self._filepath: str = ""
        self._loaded_hashes: dict = {}
        self._loaded_hash_file: str = ""

        # Load configurations & theme
        self._config = load_config()
        self._theme_colors = get_current_theme_colors(self._config)
        
        # Standard tk.Tk uses 'bg' (or 'background') configuration option
        self.configure(bg=self._theme_colors["BG_ROOT"])
        self.resizable(True, True)

        self._selected_algorithms: dict[str, tk.BooleanVar] = {}
        self._hash_widgets: dict[str, tuple[ctk.CTkLabel, ctk.CTkEntry, ctk.CTkButton]] = {}

        self._build_ui()
        self.apply_theme()
        self._update_hash_rows()

    def _set_initial_window_size(self):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(980, int(screen_w * 0.90))
        height = min(980, int(screen_h * 0.92))
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(780, 760)

    def _get_color_for_role(self, role: str) -> str:
        return self._theme_colors.get(role, "#FFFFFF")

    def _get_selected_algorithms(self) -> list:
        return [algo for algo, var in self._selected_algorithms.items() if var.get()]

    def _on_algorithm_toggled(self):
        selected = self._get_selected_algorithms()
        if not selected:
            messagebox.showwarning("Warning", "At least one hashing algorithm must remain selected.")
            self._selected_algorithms["md5"].set(True)
            selected = ["md5"]

        self._config["algorithms"] = selected
        save_config(self._config)
        self._update_hash_rows()

    def _update_hash_rows(self):
        selected = self._get_selected_algorithms()

        for algo, (lbl, ent, btn) in self._hash_widgets.items():
            if algo in selected:
                lbl.grid()
                ent.grid()
                btn.grid()
            else:
                lbl.grid_remove()
                ent.grid_remove()
                btn.grid_remove()

        if not self._filepath:
            return

        missing = [algo for algo in selected if algo not in self._hashes]
        if missing:
            self._compute()

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.theme_role = "root"
        
        self._build_header()
        self._build_body()

    def _build_header(self):
        self.hdr = ctk.CTkFrame(self, fg_color=self._get_color_for_role("BG_CARD"), corner_radius=0, height=58)
        self.hdr.theme_role = "card"
        self.hdr.grid(row=0, column=0, sticky="ew")
        self.hdr.grid_columnconfigure(1, weight=1)
        self.hdr.grid_propagate(False)

        title_lbl = ctk.CTkLabel(
            self.hdr,
            text="🔒  HashGuard",
            font=("Segoe UI", 19, "bold"),
        )
        title_lbl.theme_role = "accent"
        title_lbl.grid(row=0, column=0, sticky="w", padx=(24, 10), pady=14)

        sub_lbl = ctk.CTkLabel(
            self.hdr,
            text="MD5 · SHA-1 · SHA-256 · SHA-512 integrity checker",
            font=("Segoe UI", 13),
        )
        sub_lbl.theme_role = "dim"
        sub_lbl.grid(row=0, column=1, sticky="w", padx=10)

        settings_btn = ctk.CTkButton(
            self.hdr,
            text="⚙  Settings",
            width=100,
            height=32,
            font=("Segoe UI", 12, "bold"),
            command=self._open_settings,
        )
        settings_btn.theme_role = "neutral"
        settings_btn.grid(row=0, column=2, sticky="e", padx=24, pady=13)

    def _open_settings(self):
        if hasattr(self, "_settings_win") and self._settings_win.winfo_exists():
            self._settings_win.lift()
            self._settings_win.focus()
        else:
            self._settings_win = SettingsWindow(self)

    def _build_body(self):
        body = ctk.CTkScrollableFrame(self, fg_color=self._get_color_for_role("BG_ROOT"), corner_radius=0)
        body.theme_role = "scrollable"
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        padx = 24

        sect1 = self._section_label(body, "HASH METHODS")
        sect1.grid(row=0, column=0, sticky="w", padx=padx, pady=(10, 2))

        methods_card = self._card(body)
        methods_card.grid(row=1, column=0, sticky="ew", padx=padx, pady=(0, 6))

        desc_lbl = ctk.CTkLabel(
            methods_card,
            text="Select which hashing algorithms to compute. Your selection is remembered.",
            font=("Segoe UI", 12),
        )
        desc_lbl.theme_role = "dim"
        desc_lbl.grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(12, 10))

        col = 0
        for algo, info in HASH_ALGORITHMS.items():
            var = tk.BooleanVar(value=algo in self._config["algorithms"])
            self._selected_algorithms[algo] = var

            cb = ctk.CTkCheckBox(
                methods_card,
                text=info["label"],
                variable=var,
                font=("Segoe UI", 13, "bold"),
            )
            cb.theme_role = "checkbox"
            cb.configure(command=self._on_algorithm_toggled)
            cb.grid(row=1, column=col, padx=(14 if col == 0 else 12, 12), pady=(0, 14), sticky="w")
            col += 1

        sect2 = self._section_label(body, "SELECT OR DRAG & DROP FILE")
        sect2.grid(row=2, column=0, sticky="w", padx=padx, pady=(8, 2))

        file_card = self._card(body)
        file_card.grid(row=3, column=0, sticky="ew", padx=padx, pady=(0, 6))
        file_card.grid_columnconfigure(0, weight=1)

        self.file_var = tk.StringVar(value="No file selected…")
        self.file_entry = ctk.CTkEntry(
            file_card,
            textvariable=self.file_var,
            font=("Segoe UI", 13),
            height=40,
            state="readonly",
        )
        self.file_entry.theme_role = "entry"
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(14, 10), pady=(14, 10))

        browse_btn = ctk.CTkButton(
            file_card,
            text="Browse…",
            width=120,
            height=40,
            font=("Segoe UI", 13, "bold"),
            command=self._browse,
        )
        browse_btn.theme_role = "accent"
        browse_btn.grid(row=0, column=1, padx=(0, 14), pady=(14, 10))

        self.drop_zone = ctk.CTkFrame(
            file_card,
            corner_radius=8,
            height=62,
            border_width=2,
        )
        self.drop_zone.theme_role = "drop_zone"
        self.drop_zone.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14))
        self.drop_zone.grid_columnconfigure(0, weight=1)
        self.drop_zone.grid_propagate(False)

        self.drop_label = ctk.CTkLabel(
            self.drop_zone,
            text="⬇   Drop your target file here",
            font=("Segoe UI", 14),
        )
        self.drop_label.theme_role = "dim"
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self._on_drop_main)
        self.drop_zone.dnd_bind("<<DragEnter>>", self._on_drag_enter_main)
        self.drop_zone.dnd_bind("<<DragLeave>>", self._on_drag_leave_main)

        self.progress = ctk.CTkProgressBar(body, height=3)
        self.progress.theme_role = "progress"
        self.progress.set(0)
        self.progress.grid(row=4, column=0, sticky="ew", padx=padx, pady=(4, 0))
        self.progress.grid_remove()

        self.progress_label = ctk.CTkLabel(body, text="", font=("Segoe UI", 12))
        self.progress_label.theme_role = "dim"
        self.progress_label.grid(row=5, column=0, sticky="w", padx=padx)
        self.progress_label.grid_remove()

        sect3 = self._section_label(body, "GENERATED HASHES")
        sect3.grid(row=6, column=0, sticky="w", padx=padx, pady=(8, 2))

        hash_card = self._card(body)
        hash_card.grid(row=7, column=0, sticky="ew", padx=padx, pady=(0, 6))
        hash_card.grid_columnconfigure(0, weight=1)

        self.hash_rows_frame = ctk.CTkFrame(hash_card, fg_color="transparent")
        self.hash_rows_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        self.hash_rows_frame.grid_columnconfigure(1, weight=1)

        self._hash_vars = {}
        row_idx = 0
        for algo, info in HASH_ALGORITHMS.items():
            var = tk.StringVar(value="—")
            self._hash_vars[algo] = var
            self._hash_widgets[algo] = self._create_hash_row(
                self.hash_rows_frame,
                row_idx,
                info["label"],
                var,
                lambda a=algo: self._copy_hash(a),
            )
            row_idx += 1

        actions = ctk.CTkFrame(hash_card, fg_color="transparent")
        actions.grid(row=1, column=0, padx=14, pady=(6, 14), sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)

        compute_btn = ctk.CTkButton(
            actions,
            text="⟳  Compute Hashes",
            height=40,
            font=("Segoe UI", 13, "bold"),
            command=self._compute,
        )
        compute_btn.theme_role = "accent"
        compute_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        export_btn = ctk.CTkButton(
            actions,
            text="⬇  Export Hashes .txt",
            height=40,
            font=("Segoe UI", 13, "bold"),
            command=self._export_hashes,
        )
        export_btn.theme_role = "neutral"
        export_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        sect4 = self._section_label(body, "VERIFY INTEGRITY")
        sect4.grid(row=8, column=0, sticky="w", padx=padx, pady=(8, 2))

        verify_card = self._card(body)
        verify_card.grid(row=9, column=0, sticky="ew", padx=padx, pady=(0, 10))
        verify_card.grid_columnconfigure(0, weight=1)

        desc_lbl2 = ctk.CTkLabel(
            verify_card,
            text=(
                "Paste a checksum, or drag & drop a .txt file containing labeled hashes "
                "such as MD5: and SHA-256:. Multiple hashes will be verified side-by-side."
            ),
            font=("Segoe UI", 12),
            wraplength=850,
            justify="left",
        )
        desc_lbl2.theme_role = "dim"
        desc_lbl2.grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(14, 8))

        self.verify_entry = ctk.CTkEntry(
            verify_card,
            placeholder_text="Paste a single hash here…",
            font=("Consolas", 12),
            height=42,
        )
        self.verify_entry.theme_role = "entry"
        self.verify_entry.grid(row=1, column=0, sticky="ew", padx=(14, 10), pady=(0, 10))
        self.verify_entry.bind("<KeyRelease>", self._on_verify_type)

        paste_btn = ctk.CTkButton(
            verify_card,
            text="Paste",
            width=90,
            height=42,
            font=("Segoe UI", 12, "bold"),
            command=self._paste,
        )
        paste_btn.theme_role = "neutral"
        paste_btn.grid(row=1, column=1, padx=(0, 8), pady=(0, 10))

        load_btn = ctk.CTkButton(
            verify_card,
            text="Load .txt",
            width=100,
            height=42,
            font=("Segoe UI", 12, "bold"),
            command=self._browse_hash_file,
        )
        load_btn.theme_role = "neutral"
        load_btn.grid(row=1, column=2, padx=(0, 8), pady=(0, 10))

        verify_btn = ctk.CTkButton(
            verify_card,
            text="Verify",
            width=100,
            height=42,
            font=("Segoe UI", 12, "bold"),
            command=self._verify,
        )
        verify_btn.theme_role = "accent"
        verify_btn.grid(row=1, column=3, padx=(0, 14), pady=(0, 10))

        self.detected_label = ctk.CTkLabel(verify_card, text="", font=("Segoe UI", 12))
        self.detected_label.theme_role = "dim"
        self.detected_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 8))
        self.detected_label.grid_remove()

        self.hash_file_var = tk.StringVar(value="No hash text file loaded.")
        self.hash_file_entry = ctk.CTkEntry(
            verify_card,
            textvariable=self.hash_file_var,
            font=("Segoe UI", 12),
            height=38,
            state="readonly",
        )
        self.hash_file_entry.theme_role = "entry"
        self.hash_file_entry.grid(row=3, column=0, columnspan=4, sticky="ew", padx=14, pady=(0, 10))

        self.hash_drop_zone = ctk.CTkFrame(
            verify_card,
            height=58,
            border_width=2,
        )
        self.hash_drop_zone.theme_role = "drop_zone"
        self.hash_drop_zone.grid(row=4, column=0, columnspan=4, sticky="ew", padx=14, pady=(0, 10))
        self.hash_drop_zone.grid_columnconfigure(0, weight=1)
        self.hash_drop_zone.grid_propagate(False)

        self.hash_drop_label = ctk.CTkLabel(
            self.hash_drop_zone,
            text="⬇   Drop a hash .txt file here",
            font=("Segoe UI", 13),
        )
        self.hash_drop_label.theme_role = "dim"
        self.hash_drop_label.place(relx=0.5, rely=0.5, anchor="center")

        self.hash_drop_zone.drop_target_register(DND_FILES)
        self.hash_drop_zone.dnd_bind("<<Drop>>", self._on_drop_hash_file)
        self.hash_drop_zone.dnd_bind("<<DragEnter>>", self._on_drag_enter_hash)
        self.hash_drop_zone.dnd_bind("<<DragLeave>>", self._on_drag_leave_hash)

        self.loaded_hashes_label = ctk.CTkLabel(
            verify_card,
            text="",
            font=("Segoe UI", 12),
            justify="left",
            wraplength=850,
        )
        self.loaded_hashes_label.theme_role = "dim"
        self.loaded_hashes_label.grid(row=5, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 8))
        self.loaded_hashes_label.grid_remove()

        self.result_frame = ctk.CTkFrame(verify_card, fg_color="transparent", corner_radius=8)
        self.result_frame.grid(row=6, column=0, columnspan=4, sticky="ew", padx=14, pady=(0, 14))
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_remove()

        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=("Segoe UI", 14, "bold"),
            wraplength=850,
            justify="left",
        )
        self.result_label.theme_role = "main"
        self.result_label.grid(row=0, column=0, padx=14, pady=10, sticky="w")

        footer_lbl = ctk.CTkLabel(
            body,
            text="HashGuard  ·  uses Python hashlib  ·  fully offline utility",
            font=("Segoe UI", 11),
        )
        footer_lbl.theme_role = "dim"
        footer_lbl.grid(row=10, column=0, pady=(12, 16))

    def _section_label(self, parent, text):
        lbl = ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
        )
        lbl.theme_role = "accent"
        return lbl

    def _card(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.theme_role = "card"
        frame.grid_propagate(True)
        return frame

    def _create_hash_row(self, parent, row, label, var, copy_cmd):
        lbl = ctk.CTkLabel(
            parent,
            text=label,
            width=82,
            font=("Segoe UI", 12, "bold"),
            anchor="e",
        )
        lbl.theme_role = "dim"
        lbl.grid(row=row, column=0, padx=(0, 10), pady=(0, 8))

        ent = ctk.CTkEntry(
            parent,
            textvariable=var,
            font=("Consolas", 12),
            height=38,
            state="readonly",
        )
        ent.theme_role = "entry"
        ent.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        btn = ctk.CTkButton(
            parent,
            text="Copy",
            width=76,
            height=38,
            font=("Segoe UI", 12),
            command=copy_cmd,
        )
        btn.theme_role = "neutral"
        btn.grid(row=row, column=2, padx=(10, 0), pady=(0, 8))
        return lbl, ent, btn

    # ── Theme Application Engine ──────────────────────────────────────────────
    def apply_theme(self):
        logger.info("Applying dynamic theme to widgets...")
        self._theme_colors = get_current_theme_colors(self._config)
        
        # Standard tk.Tk uses 'bg' configure (NOT bg_color/fg_color)
        self.configure(bg=self._theme_colors["BG_ROOT"])
        
        def recurse(widget):
            apply_theme_to_widget(widget, self._theme_colors)
            for child in widget.winfo_children():
                recurse(child)
                
        recurse(self)
        self.update_idletasks()

    # ── Drag & Drop Handlers ─────────────────────────────────────────────────
    def _extract_drop_path(self, event) -> str:
        path = event.data.strip()
        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]
        return path

    def _on_drag_enter_main(self, event):
        accent = self._get_color_for_role("ACCENT")
        self.drop_zone.configure(border_color=accent, fg_color=adjust_color(accent, -0.65))
        self.drop_label.configure(text="⬇   Release to load target file", text_color=accent)

    def _on_drag_leave_main(self, event):
        card_bg = self._get_color_for_role("BG_CARD")
        self.drop_zone.configure(border_color=adjust_color(card_bg, 0.15), fg_color=adjust_color(card_bg, -0.15))
        self.drop_label.configure(text="⬇   Drop your target file here", text_color=self._get_color_for_role("FG_DIM"))

    def _on_drop_main(self, event):
        self._on_drag_leave_main(event)
        path = self._extract_drop_path(event)
        if os.path.isfile(path):
            self._load_file(path)
        else:
            messagebox.showwarning("Not a file", "Please drop a single file (not a folder).")

    def _on_drag_enter_hash(self, event):
        accent = self._get_color_for_role("ACCENT")
        self.hash_drop_zone.configure(border_color=accent, fg_color=adjust_color(accent, -0.65))
        self.hash_drop_label.configure(text="⬇   Release to load hash .txt", text_color=accent)

    def _on_drag_leave_hash(self, event):
        card_bg = self._get_color_for_role("BG_CARD")
        self.hash_drop_zone.configure(border_color=adjust_color(card_bg, 0.15), fg_color=adjust_color(card_bg, -0.15))
        self.hash_drop_label.configure(text="⬇   Drop a hash .txt file here", text_color=self._get_color_for_role("FG_DIM"))

    def _on_drop_hash_file(self, event):
        self._on_drag_leave_hash(event)
        path = self._extract_drop_path(event)
        if os.path.isfile(path) and path.lower().endswith(".txt"):
            self._load_hash_file(path)
        elif os.path.isfile(path):
            messagebox.showwarning("Wrong file type", "Please drop a .txt hash file here.")
        else:
            messagebox.showwarning("Not a file", "Please drop a single .txt file.")

    # ── File loading ─────────────────────────────────────────────────────────
    def _browse(self):
        path = filedialog.askopenfilename(title="Select a file to hash")
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        self._filepath = path
        try:
            size_str = format_size(os.path.getsize(path))
            display = f"{os.path.basename(path)}  ({size_str})"
            logger.info(f"Loaded file: {path} ({size_str})")
        except OSError as e:
            logger.error(f"Error loading file {path}: {e}")
            display = os.path.basename(path)

        short = display if len(display) < 72 else "…" + display[-69:]
        self.file_var.set(short)
        self.file_entry.configure(text_color=self._get_color_for_role("FG_MAIN"))
        self.drop_label.configure(text=f"✔  {os.path.basename(path)}", text_color=SUCCESS)

        for algo, var in self._hash_vars.items():
            var.set("—" if self._selected_algorithms[algo].get() else "")

        self._hashes = {}
        self._set_result("", "neutral")
        self._compute()

    def _browse_hash_file(self):
        path = filedialog.askopenfilename(
            title="Select hash text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self._load_hash_file(path)

    def _load_hash_file(self, path: str):
        logger.info(f"Loading external hash text file: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            try:
                with open(path, "r", encoding="latin-1") as f:
                    text = f.read()
            except Exception as exc:
                logger.error(f"Failed decoding hash text file: {exc}")
                messagebox.showerror("Error", f"Could not read hash file:\n{exc}")
                return
        except Exception as exc:
            logger.error(f"Failed reading hash text file: {exc}")
            messagebox.showerror("Error", f"Could not read hash file:\n{exc}")
            return

        parsed = parse_hash_text(text)
        if not parsed:
            logger.warning("No labeled hashes parsed from loaded file.")
            messagebox.showwarning(
                "No hashes found",
                "No valid labeled hashes were found. Expected lines like:\n\nMD5: ...\nSHA-256: ...",
            )
            return

        self._loaded_hashes = parsed
        self._loaded_hash_file = path
        self.hash_file_var.set(os.path.basename(path))
        self.hash_file_entry.configure(text_color=self._get_color_for_role("FG_MAIN"))
        self.hash_drop_label.configure(text=f"✔  {os.path.basename(path)}", text_color=SUCCESS)

        summary = []
        for algo in ("md5", "sha1", "sha256", "sha512"):
            if algo in parsed:
                summary.append(HASH_ALGORITHMS[algo]["label"])
        self.loaded_hashes_label.configure(text="Loaded hashes: " + ", ".join(summary), text_color=self._get_color_for_role("ACCENT"))
        self.loaded_hashes_label.grid()

        self._set_result("", "neutral")

        if self._hashes:
            self._verify()

    # ── Hashing Threading ────────────────────────────────────────────────────
    def _compute(self):
        if not self._filepath:
            messagebox.showwarning("No file", "Please select a file first.")
            return

        selected = self._get_selected_algorithms()
        if not selected:
            messagebox.showwarning("No algorithm", "Please select at least one hash algorithm.")
            return

        for algo in HASH_ALGORITHMS:
            if algo in selected:
                self._hash_vars[algo].set("Computing…")
            else:
                self._hash_vars[algo].set("")

        self._set_result("", "neutral")
        self.progress.set(0)
        self.progress.grid()
        self.progress_label.configure(text="Hashing file…")
        self.progress_label.grid()
        self.update_idletasks()

        logger.info(f"Computing hashes for {self._filepath} with {selected}")

        def worker():
            try:
                result = compute_hashes(self._filepath, selected, progress_cb=self._update_progress)
                self._hashes = result
                self.after(0, self._show_hashes)
            except Exception as exc:
                logger.exception("Error computing hashes in worker thread")
                self.after(0, lambda: self._show_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _update_progress(self, pct):
        self.after(0, lambda: self.progress.set(pct))

    def _show_hashes(self):
        for algo, var in self._hash_vars.items():
            if algo in self._hashes:
                var.set(self._hashes[algo])
            else:
                var.set("—" if self._selected_algorithms[algo].get() else "")

        self.progress.set(1)
        self.progress_label.configure(text="Done ✓")
        self.after(1500, lambda: (self.progress.grid_remove(), self.progress_label.grid_remove()))

        if self._loaded_hashes or self.verify_entry.get().strip():
            self._verify()

    def _show_error(self, msg):
        for algo, var in self._hash_vars.items():
            if self._selected_algorithms[algo].get():
                var.set("Error")
        self.progress.grid_remove()
        self.progress_label.grid_remove()
        messagebox.showerror("Error", f"Could not read file:\n{msg}")

    # ── Export / Copy ────────────────────────────────────────────────────────
    def _export_hashes(self):
        if not self._hashes:
            messagebox.showwarning("No hashes", "Compute hashes first, then export them.")
            return

        default_name = "Hash.txt"
        if self._filepath:
            default_name = Path(self._filepath).stem + " - Hash.txt"

        initial_dir = os.path.dirname(self._filepath) if self._filepath else None

        dialog_kwargs = {
            "title": "Save hash text file",
            "defaultextension": ".txt",
            "initialfile": default_name,
            "filetypes": [("Text files", "*.txt")],
        }
        if initial_dir:
            dialog_kwargs["initialdir"] = initial_dir

        path = filedialog.asksaveasfilename(**dialog_kwargs)
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                export_filename = os.path.basename(self._filepath) if self._filepath else ""
                lines = []
                if export_filename:
                    lines.append(f"Filename: {export_filename}\n")
                for algo in ("md5", "sha1", "sha256", "sha512"):
                    if algo in self._hashes:
                        lines.append(f"{HASH_ALGORITHMS[algo]['display']}: {self._hashes[algo]}")
                f.write("\n".join(lines))
            logger.info(f"Exported calculated hashes to {path}")
            messagebox.showinfo("Exported", f"Hashes saved to:\n{path}")
        except Exception as exc:
            logger.error(f"Failed exporting hashes to {path}: {exc}")
            messagebox.showerror("Export failed", f"Could not save file:\n{exc}")

    def _copy_hash(self, algo: str):
        text = self._hashes.get(algo, "")
        if not text or text in ("—", "Computing…", "Error"):
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        _, _, btn = self._hash_widgets[algo]
        label = HASH_ALGORITHMS[algo]["label"]
        self.update_idletasks()
        x = btn.winfo_rootx() + btn.winfo_width() // 2
        y = btn.winfo_rooty()
        Toast(self, f"✔  {label} copied!", x, y)

    # ── Verification ─────────────────────────────────────────────────────────
    def _paste(self):
        try:
            text = self.clipboard_get().strip()
            self.verify_entry.delete(0, "end")
            self.verify_entry.insert(0, text)
            self._on_verify_type()
        except Exception as e:
            logger.warning(f"Failed to paste from clipboard: {e}")

    def _on_verify_type(self, event=None):
        text = self.verify_entry.get().strip()
        kind = detect_hash_type(text)
        if kind:
            info = HASH_ALGORITHMS[kind]
            self.detected_label.configure(
                text=f"Detected pasted hash: {info['label']}  ({info['length']} hex chars)",
                text_color=self._get_color_for_role("ACCENT"),
            )
            self.detected_label.grid()
        elif text:
            self.detected_label.configure(
                text="⚠  Not a valid MD5, SHA-1, SHA-256, or SHA-512 hash",
                text_color=WARNING,
            )
            self.detected_label.grid()
        else:
            self.detected_label.grid_remove()
        self._set_result("", "neutral")

    def _verify(self):
        if not self._hashes:
            messagebox.showwarning("No hash", "Compute the file's hash first.")
            return

        pasted = self.verify_entry.get().strip().upper()

        if self._loaded_hashes:
            lines = []
            ok_count = 0
            fail_count = 0
            warn_count = 0

            for algo in ("md5", "sha1", "sha256", "sha512"):
                expected = self._loaded_hashes.get(algo)
                if not expected:
                    continue

                computed = self._hashes.get(algo, "")
                label = HASH_ALGORITHMS[algo]["label"]
                if not computed or computed in ("—", "Computing…", "Error"):
                    lines.append(f"⚠  {label}: not computed")
                    warn_count += 1
                elif computed == expected:
                    lines.append(f"✔  {label}: match")
                    ok_count += 1
                else:
                    lines.append(f"✗  {label}: mismatch")
                    fail_count += 1

            if fail_count:
                state = "error"
                header = "Hash file verification failed:"
            elif ok_count and warn_count:
                state = "warning"
                header = "Hash file verification partially complete:"
            elif ok_count:
                state = "success"
                header = "All loaded hashes matched:"
            else:
                state = "warning"
                header = "No loaded hashes could be checked:"

            self._set_result(header + "\n\n" + "\n".join(lines), state)
            return

        if not pasted:
            messagebox.showwarning(
                "Empty",
                "Paste a hash to verify, or load a .txt file containing hashes first.",
            )
            return

        kind = detect_hash_type(pasted)
        if kind is None:
            self._set_result(
                "✗  Not a recognised hash — must be 32 (MD5), 40 (SHA-1), 64 (SHA-256), or 128 (SHA-512) chars",
                "error",
            )
            return

        computed = self._hashes.get(kind, "")
        if not computed or computed in ("—", "Computing…", "Error"):
            algo_label = HASH_ALGORITHMS[kind]["label"]
            self._set_result(
                f"⚠  {algo_label} was not computed. Enable it in HASH METHODS and recompute.",
                "warning",
            )
            return

        if pasted == computed:
            algo = HASH_ALGORITHMS[kind]["label"]
            self._set_result(f"✔  {algo} match — file is intact!", "success")
        else:
            self._set_result("✗  Hash mismatch — file may be corrupted or tampered!", "error")

    def _set_result(self, text, state):
        colors = {
            "success": (SUCCESS, "#0D3020"),
            "error": (ERROR, "#3A0D0D"),
            "warning": (WARNING, "#2E1E00"),
            "neutral": (self._get_color_for_role("FG_DIM"), "transparent"),
        }
        fg, bg = colors.get(state, colors["neutral"])
        self.result_label.configure(text=text, text_color=fg)
        self.result_frame.configure(fg_color=bg)

        if state == "neutral" or not text:
            self.result_frame.grid_remove()
        else:
            self.result_frame.grid()
