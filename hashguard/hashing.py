import hashlib
import os
import re

HASH_ALGORITHMS = {
    "md5": {"label": "MD5", "length": 32, "display": "MD5"},
    "sha1": {"label": "SHA-1", "length": 40, "display": "SHA-1"},
    "sha256": {"label": "SHA-256", "length": 64, "display": "SHA-256"},
    "sha512": {"label": "SHA-512", "length": 128, "display": "SHA-512"},
}

TEXT_KEY_TO_ALGO = {
    "MD5": "md5", "MD-5": "md5",
    "SHA1": "sha1", "SHA-1": "sha1", "SHA 1": "sha1",
    "SHA256": "sha256", "SHA-256": "sha256", "SHA 256": "sha256",
    "SHA512": "sha512", "SHA-512": "sha512", "SHA 512": "sha512",
}

def compute_hashes(filepath: str, algorithms: list, progress_cb=None) -> dict:
    hashers = {}
    for algo in algorithms:
        if algo == "md5":
            hashers["md5"] = hashlib.md5()
        elif algo == "sha1":
            hashers["sha1"] = hashlib.sha1()
        elif algo == "sha256":
            hashers["sha256"] = hashlib.sha256()
        elif algo == "sha512":
            hashers["sha512"] = hashlib.sha512()

    try:
        total = os.path.getsize(filepath)
    except OSError:
        total = 0

    size = 0
    with open(filepath, "rb") as f:
        while True:
            data = f.read(1024 * 1024)
            if not data:
                break
            for hasher in hashers.values():
                hasher.update(data)
            size += len(data)
            if progress_cb and total:
                progress_cb(size / total)

    return {name: h.hexdigest().upper() for name, h in hashers.items()}

def detect_hash_type(text: str):
    h = text.strip().upper()
    if re.fullmatch(r"[0-9A-F]{128}", h):
        return "sha512"
    if re.fullmatch(r"[0-9A-F]{64}", h):
        return "sha256"
    if re.fullmatch(r"[0-9A-F]{40}", h):
        return "sha1"
    if re.fullmatch(r"[0-9A-F]{32}", h):
        return "md5"
    return None

def parse_hash_text(text: str) -> dict:
    found = {}
    lines = text.splitlines()

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue

        for raw_label, algo in TEXT_KEY_TO_ALGO.items():
            label_pattern = re.escape(raw_label)
            match = re.match(
                rf"^\s*{label_pattern}\s*(?:[:=\-]\s*)?(.*)$",
                line,
                flags=re.IGNORECASE,
            )
            if not match:
                continue

            value = match.group(1).strip().upper()
            if not value and i + 1 < len(lines):
                value = lines[i + 1].strip().upper()

            value = value.replace(" ", "")
            expected_len = HASH_ALGORITHMS[algo]["length"]
            if re.fullmatch(rf"[0-9A-F]{{{expected_len}}}", value):
                found[algo] = value
            break

    return found

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
