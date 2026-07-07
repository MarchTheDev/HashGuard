"""
HashGuard Python backend.

All public methods are exposed to the webview JS layer as
window.pywebview.api.<method_name>().

The JS front-end calls these for anything that needs native OS access:
  - file open / save dialogs
  - hash computation (via hashlib, so it also works on large files
    without loading them entirely into the browser sandbox)
  - persisting settings / theme to disk
  - downloading and installing updates from GitHub Releases
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path
from typing import Any, Callable, Optional

import webview  # type: ignore

from hashguard_app.config import (
    STATE_FILE, UPDATE_CACHE_DIR, INSTALL_DIR, GITHUB_API_RELEASES, APP_VERSION,
)


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

    # ------------------------------------------------------------------
    # Auto-Update: check, download, install
    # ------------------------------------------------------------------

    def get_app_version(self) -> str:
        """Return the current application version string."""
        return APP_VERSION

    def get_install_dir(self) -> str:
        """Return the directory where the app is installed."""
        return str(INSTALL_DIR)

    def check_for_updates(self) -> dict[str, Any]:
        """
        Query the GitHub Releases API and return info about the latest release.

        Returns ``{"ok": True, "update_available": bool, "latest_version": str,
        "release_name": str, "download_url": str | None, "release_url": str,
        "body": str, "published_at": str}``
        """
        try:
            req = urllib.request.Request(
                GITHUB_API_RELEASES,
                headers={"Accept": "application/vnd.github+json", "User-Agent": "HashGuard-App"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            if not isinstance(data, list) or len(data) == 0:
                return {"ok": True, "update_available": False, "reason": "no_releases"}

            latest = data[0]
            tag = latest.get("tag_name", "")
            latest_version = tag.lstrip("v")
            current_clean = APP_VERSION.lstrip("v")

            # Simple version comparison (works for semver-like strings)
            def _ver_tuple(v: str):
                parts = []
                for p in v.split("."):
                    try:
                        parts.append(int(p))
                    except ValueError:
                        parts.append(0)
                return tuple(parts)

            update_available = _ver_tuple(latest_version) > _ver_tuple(current_clean)

            # Find the Windows installer asset (.exe setup file)
            download_url = None
            for asset in latest.get("assets", []):
                name = asset.get("name", "")
                if name.endswith(".exe") and "setup" in name.lower():
                    download_url = asset.get("browser_download_url")
                    break
            # Fallback: first .exe asset
            if download_url is None:
                for asset in latest.get("assets", []):
                    name = asset.get("name", "")
                    if name.endswith(".exe"):
                        download_url = asset.get("browser_download_url")
                        break

            return {
                "ok": True,
                "update_available": update_available,
                "latest_version": latest_version,
                "tag_name": tag,
                "release_name": latest.get("name", tag),
                "download_url": download_url,
                "release_url": latest.get("html_url", ""),
                "body": latest.get("body", ""),
                "published_at": latest.get("published_at", ""),
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc), "update_available": False}

    def download_update(self, url: str) -> dict[str, Any]:
        """
        Download the update installer from *url* to the local cache.

        Returns ``{"ok": True, "path": "..."}`` on success.
        The download runs synchronously (called from a background thread in JS).
        """
        try:
            # Determine filename from URL
            filename = url.rsplit("/", 1)[-1] or "HashGuard-Setup.exe"
            dest = UPDATE_CACHE_DIR / filename

            # Download with progress reporting via a simple approach
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "HashGuard-App"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536
                with open(dest, "wb") as fh:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        fh.write(chunk)
                        downloaded += len(chunk)

            return {"ok": True, "path": str(dest), "size": downloaded}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def launch_installer(self, installer_path: str) -> dict[str, Any]:
        """
        Launch the NSIS installer to perform an in-place upgrade.

        Uses ``ShellExecuteW`` with the ``runas`` verb to properly request
        admin elevation (UAC prompt). The installer is called with ``/S``
        (silent) and ``/UPDATE`` flags.

        Returns ``{"ok": True}`` if the installer was launched.
        """
        try:
            installer = Path(installer_path)
            if not installer.exists():
                return {"ok": False, "error": f"Installer not found: {installer_path}"}

            if platform.system() != "Windows":
                return {"ok": False, "error": "In-app update is only supported on Windows."}

            # Use ShellExecuteW with "runas" to trigger UAC elevation
            # This is the proper way to launch an elevated process on Windows
            try:
                import ctypes.wintypes  # type: ignore

                # ShellExecuteW signature
                shell32 = ctypes.windll.shell32  # type: ignore
                sw = shell32.ShellExecuteW
                sw.argtypes = [
                    ctypes.wintypes.HWND,  # hwnd
                    ctypes.c_wchar_p,      # lpOperation
                    ctypes.c_wchar_p,      # lpFile
                    ctypes.c_wchar_p,      # lpParameters
                    ctypes.c_wchar_p,      # lpDirectory
                    ctypes.c_int,          # nShowCmd
                ]
                sw.restype = ctypes.wintypes.HINSTANCE

                # "runas" verb triggers UAC elevation
                result = sw(
                    None,                    # parent window
                    "runas",                 # request elevation
                    str(installer),          # file to execute
                    "/S /UPDATE",            # silent + upgrade flags
                    str(installer.parent),   # working directory
                    1,                       # SW_SHOWNORMAL
                )

                # ShellExecute returns a value > 32 on success
                if result <= 32:
                    return {"ok": False, "error": f"Failed to launch installer (error code {result}). You may need to run the app as Administrator."}

                return {"ok": True}

            except Exception as shell_err:
                # Fallback: try subprocess with runas via PowerShell
                try:
                    import subprocess
                    ps_cmd = f'Start-Process -FilePath "{installer}" -ArgumentList "/S","/UPDATE" -Verb RunAs'
                    subprocess.Popen(
                        ["powershell", "-Command", ps_cmd],
                        close_fds=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                    return {"ok": True}
                except Exception as fallback_err:
                    return {"ok": False, "error": f"Elevation failed: {str(shell_err)}"}

        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def download_and_install_update(self, url: str) -> dict[str, Any]:
        """
        Convenience: download the installer then immediately launch it.
        The installer will terminate this app and replace it.
        """
        dl = self.download_update(url)
        if not dl.get("ok"):
            return dl
        return self.launch_installer(dl["path"])
