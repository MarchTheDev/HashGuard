"""Auto-build helper."""
from __future__ import annotations
import shutil
import subprocess
from hashguard_app.config import BASE_DIR, UI_PATH

def _npm_executable() -> str | None:
    for candidate in ("npm", "npm.cmd"):
        path = shutil.which(candidate)
        if path:
            return path
    return None

def ensure_ui_built() -> bool:
    if UI_PATH.exists():
        return True
    
    # If UI file was deleted or missing, attempt a fallback build if npm exists
    npm = _npm_executable()
    if not npm:
        print("=" * 60)
        print("Error: HashGuard UI file not found at:", UI_PATH)
        print("Please ensure hashguard_app/UI/index.html is included in your repository.")
        print("=" * 60)
        return False

    node_modules = BASE_DIR / "node_modules"
    try:
        if not node_modules.exists():
            print("Installing frontend dependencies (npm install)…")
            subprocess.run([npm, "install"], cwd=str(BASE_DIR), check=True)
        print("Building UI (npm run build)…")
        subprocess.run([npm, "run", "build"], cwd=str(BASE_DIR), check=True)
        dist_file = BASE_DIR / "dist" / "index.html"
        if dist_file.exists():
            UI_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dist_file, UI_PATH)
    except Exception as exc:
        print(f"Could not automatically rebuild UI: {exc}")
        return False

    return UI_PATH.exists()
