import json
import logging
import ssl
import urllib.request
from hashguard.config import GITHUB_REPO

logger = logging.getLogger("HashGuard.Updater")

try:
    _ssl_context = ssl._create_unverified_context()
except AttributeError:
    _ssl_context = None

def check_latest_release(repo=GITHUB_REPO):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HashGuard-Updater"})
        with urllib.request.urlopen(req, context=_ssl_context, timeout=6) as response:
            data = json.loads(response.read().decode())
            return {
                "version": data.get("tag_name", "").strip(),
                "assets": data.get("assets", []),
                "html_url": data.get("html_url", ""),
                "body": data.get("body", "")
            }
    except Exception as e:
        logger.error(f"Failed checking GitHub updates: {e}")
        return None

def download_file(url, dest_path, progress_cb=None):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HashGuard-Updater"})
        with urllib.request.urlopen(req, context=_ssl_context) as response:
            total_size = int(response.info().get('Content-Length', 0))
            bytes_so_far = 0
            block_size = 1024 * 64
            
            with open(dest_path, 'wb') as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_so_far += len(chunk)
                    if progress_cb and total_size > 0:
                        progress_cb(bytes_so_far / total_size)
            return True
    except Exception as e:
        logger.error(f"Download of update failed: {e}")
        return False
