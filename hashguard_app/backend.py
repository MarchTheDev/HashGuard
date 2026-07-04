"""
HashGuard Python backend.

All public methods are exposed to the webview JS layer as
window.pywebview.api.<method_name>().

The JS front-end calls these for anything that needs native OS access:
  - file open / save dialogs
  - hash computation (via hashlib, so it also works on large files
    without loading them entirely into the browser sandbox)
  - persisting settings / theme to disk
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import webview  # type: ignore

from hashguard_app.config import STATE_FILE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_hash(file_path: str, algorithm: str) -> str:
    """Return the hex digest of *file_path* using *algorithm*."""
    algo_key = algorithm.lower().replace("-", "")
    hasher = hashlib.new(algo_key)
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Backend class
# ---------------------------------------------------------------------------

class Backend:
    """Exposed to JavaScript as ``window.pywebview.api``."""

    # ------------------------------------------------------------------
    # File dialogs
    # ------------------------------------------------------------------

    def pick_file(self) -> str | None:
        """Open a native file-open dialog and return the chosen path."""
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("All Files (*.*)",),
        )
        if result:
            return result[0]
        return None

    def pick_files(self) -> list[str] | None:
        """Open a native file-open dialog allowing multiple files and return paths."""
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=("All Files (*.*)",),
        )
        if result:
            return list(result)
        return None

    def pick_hash_txt(self) -> str | None:
        """Open a native file-open dialog filtered to .txt files."""
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("Text Files (*.txt)", "All Files (*.*)"),
        )
        if result:
            return result[0]
        return None

    def save_hash_txt(self, filename: str) -> str | None:
        """Open a native save-file dialog and return the chosen path."""
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=filename,
            file_types=("Text Files (*.txt)",),
        )
        # pywebview returns a string (not a list) from SAVE_DIALOG
        if result:
            return result if isinstance(result, str) else result[0]
        return None

    # ------------------------------------------------------------------
    # Hash computation
    # ------------------------------------------------------------------

    def compute_hashes(self, file_path: str, algorithms: list[str]) -> dict[str, Any]:
        """
        Compute one or more hashes for *file_path*.

        Returns ``{"ok": True, "hashes": {"MD5": "...", ...}}``
        or      ``{"ok": False, "error": "..."}``
        """
        try:
            hashes: dict[str, str] = {}
            # Single pass — open the file once and feed all hashers
            hashers = {algo: hashlib.new(algo.lower().replace("-", ""))
                       for algo in algorithms}
            with open(file_path, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    for h in hashers.values():
                        h.update(chunk)
            for algo, h in hashers.items():
                hashes[algo] = h.hexdigest()
            return {"ok": True, "hashes": hashes}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def compute_batch_hashes(self, file_paths: list[str], algorithms: list[str]) -> dict[str, Any]:
        """
        Compute one or more hashes for multiple files.

        Returns ``{"ok": True, "results": [{"path": "...", "name": "...", "size": 123, "hashes": {"MD5": "...", ...}}, ...]}``
        """
        try:
            results = []
            for fp in file_paths:
                p = Path(fp)
                if not p.exists() or not p.is_file():
                    continue
                info = {"path": fp, "name": p.name, "size": p.stat().st_size}
                res = self.compute_hashes(fp, algorithms)
                if res["ok"]:
                    info["hashes"] = res["hashes"]
                else:
                    info["error"] = res.get("error")
                results.append(info)
            return {"ok": True, "results": results}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def verify_hashes(
        self,
        file_path: str,
        expected: list[dict[str, str]],   # [{"algorithm": "SHA-256", "hash": "abc…"}]
    ) -> dict[str, Any]:
        """
        Verify one or more expected hashes against *file_path*.

        Returns ``{"ok": True, "results": {"SHA-256": true, ...}}``
        or      ``{"ok": False, "error": "..."}``
        """
        try:
            algorithms = [e["algorithm"] for e in expected]
            computed_result = self.compute_hashes(file_path, algorithms)
            if not computed_result["ok"]:
                return computed_result

            computed = computed_result["hashes"]
            results: dict[str, bool] = {
                e["algorithm"]: computed.get(e["algorithm"], "").lower()
                                 == e["hash"].lower()
                for e in expected
            }
            return {"ok": True, "results": results}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Export / import helpers
    # ------------------------------------------------------------------

    def write_hash_file(self, save_path: str, content: str) -> dict[str, Any]:
        """Write *content* to *save_path* on disk."""
        try:
            Path(save_path).write_text(content, encoding="utf-8")
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def read_hash_file(self, file_path: str) -> dict[str, Any]:
        """Read a .txt hash file from disk and return its content."""
        try:
            content = Path(file_path).read_text(encoding="utf-8")
            return {"ok": True, "content": content}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def get_file_info(self, file_path: str) -> dict[str, Any]:
        """Return name and size of a file."""
        try:
            p = Path(file_path)
            return {"ok": True, "name": p.name, "size": p.stat().st_size}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Persistent state (theme, algorithm prefs, custom themes)
    # ------------------------------------------------------------------

    def load_state(self) -> dict:
        """Return the persisted state dict (empty dict if none saved yet)."""
        return _load_state()

    def save_state(self, state: dict) -> dict[str, Any]:
        """Persist *state* to disk."""
        try:
            _save_state(state)
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
