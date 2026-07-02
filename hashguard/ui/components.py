import tkinter as tk
import customtkinter as ctk
from hashguard.config import SUCCESS, ERROR, WARNING, adjust_color, is_dark

class Toast(tk.Toplevel):
    def __init__(self, master, message: str, x: int, y: int):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(bg="#12192A") # Matches GHP panel bg

        lbl = tk.Label(
            self,
            text=message,
            font=("Segoe UI", 10, "bold"),
            fg=SUCCESS,
            bg="#12192A",
            padx=14,
            pady=7,
        )
        lbl.pack()

        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        self.geometry(f"+{x - w // 2}+{y - h - 8}")
        self._fade_in()

    def _fade_in(self, alpha=0.0):
        alpha = min(alpha + 0.08, 1.0)
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(16, lambda: self._fade_in(alpha))
        else:
            self.after(900, self._fade_out)

    def _fade_out(self, alpha=1.0):
        alpha = max(alpha - 0.08, 0.0)
        self.attributes("-alpha", alpha)
        if alpha > 0:
            self.after(16, lambda: self._fade_out(alpha))
        else:
            self.destroy()

def apply_theme_to_widget(widget, theme):
    accent = theme["ACCENT"]
    bg_root = theme["BG_ROOT"]
    bg_card = theme["BG_CARD"]
    fg_main = theme["FG_MAIN"]
    fg_dim = theme["FG_DIM"]
    
    role = getattr(widget, "theme_role", None)
    
    if isinstance(widget, ctk.CTkFrame):
        if role == "root":
            widget.configure(fg_color=bg_root)
        elif role == "card":
            # GHP styled elegant thin outlines on cards
            widget.configure(
                fg_color=bg_card, 
                border_width=1, 
                border_color=adjust_color(bg_card, 0.12)
            )
        elif role == "drop_zone":
            # Sleek GHP drop zone
            widget.configure(
                fg_color=adjust_color(bg_card, -0.2), 
                border_color=adjust_color(bg_card, 0.15)
            )
        else:
            widget.configure(fg_color=bg_card)
            
    elif isinstance(widget, ctk.CTkLabel):
        if role == "accent":
            widget.configure(text_color=accent)
        elif role == "dim":
            widget.configure(text_color=fg_dim)
        elif role == "main":
            widget.configure(text_color=fg_main)
        elif role == "success":
            widget.configure(text_color=SUCCESS)
        elif role == "error":
            widget.configure(text_color=ERROR)
        elif role == "warning":
            widget.configure(text_color=WARNING)
        else:
            widget.configure(text_color=fg_main)
            
    elif isinstance(widget, ctk.CTkButton):
        if role == "accent":
            txt_col = "#FFFFFF" if is_dark(accent) else "#000000"
            widget.configure(fg_color=accent, hover_color=adjust_color(accent, -0.12), text_color=txt_col)
        elif role == "neutral":
            # GHP styled dark buttons
            neutral_bg = adjust_color(bg_card, 0.15)
            widget.configure(fg_color=neutral_bg, hover_color=adjust_color(neutral_bg, 0.12), text_color=fg_main)
        else:
            txt_col = "#FFFFFF" if is_dark(accent) else "#000000"
            widget.configure(fg_color=accent, hover_color=adjust_color(accent, -0.12), text_color=txt_col)
            
    elif isinstance(widget, ctk.CTkEntry):
        widget.configure(
            fg_color=adjust_color(bg_card, -0.15), 
            border_color=adjust_color(bg_card, 0.15), 
            text_color=fg_main,
            placeholder_text_color=fg_dim
        )
        
    elif isinstance(widget, ctk.CTkCheckBox):
        widget.configure(
            fg_color=accent, 
            hover_color=adjust_color(accent, -0.12), 
            text_color=fg_main, 
            border_color=adjust_color(bg_card, 0.2)
        )
        
    elif isinstance(widget, ctk.CTkProgressBar):
        widget.configure(progress_color=accent, fg_color=adjust_color(bg_card, -0.15))
        
    elif isinstance(widget, ctk.CTkScrollableFrame):
        widget.configure(fg_color=bg_root)
