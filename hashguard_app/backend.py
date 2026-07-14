"""
HashGuard backend - handles file operations, hashing, and state management.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Import MD4 fallback
try:
    from hashguard_app.md4 import MD4
    HAS_MD4 = True
except ImportError:
    HAS_MD4 = False

# Import optional libraries
try:
    import xxhash
    HAS_XXHASH = True
except ImportError:
    HAS_XXHASH = False

try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

# Import config
from hashguard_app.config import DATA_DIR, STATE_FILE, UPDATE_CACHE_DIR

# Setup logging
LOG_FILE = DATA_DIR / "backend.log"

def log(msg: str):
    """Write to log file for debugging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    
    # Ensure directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write to log file
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
    except:
        pass  # If logging fails, continue anyway


class Backend:
    """Handles file operations, hashing, and state management"""
    
    def __init__(self):
        log("Backend initialized")
        log(f"State file: {STATE_FILE}")
        log(f"Data directory: {DATA_DIR}")
    
    # ========== STATE MANAGEMENT ==========
    
    def load_state(self) -> dict:
        """Load application state from disk"""
        log(f"load_state() called")
        log(f"  State file exists: {STATE_FILE.exists()}")
        
        if not STATE_FILE.exists():
            log("  No state file found, returning empty dict")
            return {}
        
        try:
            content = STATE_FILE.read_text(encoding='utf-8')
            log(f"  File size: {len(content)} bytes")
            
            state = json.loads(content)
            log(f"  State loaded successfully")
            log(f"  Keys: {list(state.keys())}")
            
            if 'currentThemeName' in state:
                log(f"  Theme: {state['currentThemeName']}")
            if 'selectedAlgorithms' in state:
                log(f"  Selected: {len(state['selectedAlgorithms'])} algorithms")
            if 'favoriteAlgorithms' in state:
                log(f"  Favorites: {len(state['favoriteAlgorithms'])} algorithms")
            
            return state
            
        except Exception as e:
            log(f"  ERROR loading state: {e}")
            import traceback
            log(f"  Traceback: {traceback.format_exc()}")
            return {}
    
    def save_state(self, state: dict) -> dict:
        """Save application state to disk"""
        log(f"save_state() called")
        log(f"  State keys: {list(state.keys())}")
        
        try:
            # Ensure directory exists
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Write state to file
            content = json.dumps(state, indent=2, ensure_ascii=False)
            STATE_FILE.write_text(content, encoding='utf-8')
            
            log(f"  State saved successfully")
            log(f"  File size: {len(content)} bytes")
            
            # Verify the file was written
            if STATE_FILE.exists():
                log(f"  Verification: File exists")
                actual_size = STATE_FILE.stat().st_size
                log(f"  Verification: File size is {actual_size} bytes")
                
                if actual_size == len(content):
                    log(f"  Verification: Size matches")
                else:
                    log(f"  WARNING: Size mismatch! Expected {len(content)}, got {actual_size}")
            else:
                log(f"  ERROR: File does not exist after save!")
            
            return {"ok": True}
            
        except Exception as e:
            log(f"  ERROR saving state: {e}")
            import traceback
            log(f"  Traceback: {traceback.format_exc()}")
            return {"ok": False, "error": str(e)}
    

    # ========== FILE EXPORT ==========

    def save_hash_txt(self, filename: str) -> str:

        """Ask user where to save the hash txt file, return the chosen path or empty string"""

        log(f"save_hash_txt() called with filename: {filename}")

        # In pywebview, we use create_file_dialog to let user pick save location

        try:

            import webview

            # Get the main window

            windows = webview.windows

            if windows:

                result = windows[0].create_file_dialog(

                    webview.SAVE_DIALOG,

                    save_filename=filename,

                    file_types=('Text Files (*.txt)',)

                )

                if result and len(result) > 0:

                    path = result[0] if isinstance(result, tuple) else result

                    log(f"  User chose path: {path}")

                    return path

            log("  No path selected or no windows")

            return ""

        except Exception as e:

            log(f"  ERROR in save_hash_txt: {e}")

            return ""



    def write_hash_file(self, path: str, content: str) -> dict:

        """Write hash report content to the specified file path"""

        log(f"write_hash_file() called for path: {path}")

        try:

            from pathlib import Path as PathLib

            p = PathLib(path)

            p.parent.mkdir(parents=True, exist_ok=True)

            p.write_text(content, encoding='utf-8')

            log(f"  File written successfully, size: {p.stat().st_size} bytes")

            return {"ok": True}

        except Exception as e:

            log(f"  ERROR writing file: {e}")

            return {"ok": False, "error": str(e)}
    
    # ========== UPDATE MANAGEMENT ==========
    
    def download_update(self, url: str) -> dict:
        """Download update installer from URL"""
        log(f"download_update() called with URL: {url}")
        try:
            import urllib.request
            from pathlib import Path as PathLib
            
            # Create filename from URL
            filename = PathLib(url).name or "HashGuard-Setup.exe"
            target_path = UPDATE_CACHE_DIR / filename
            
            log(f"  Downloading to: {target_path}")
            
            # Download the file
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "HashGuard"}
            )
            
            with urllib.request.urlopen(request, timeout=120) as response:
                target_path.write_bytes(response.read())
            
            log(f"  Download complete, size: {target_path.stat().st_size} bytes")
            return {"ok": True, "path": str(target_path)}
            
        except Exception as e:
            log(f"  ERROR downloading update: {e}")
            import traceback
            log(f"  Traceback: {traceback.format_exc()}")
            return {"ok": False, "error": str(e)}
    
    def launch_installer(self, path: str) -> dict:
        """Launch the downloaded installer"""
        log(f"launch_installer() called with path: {path}")
        try:
            from pathlib import Path as PathLib
            
            target = PathLib(path)
            
            if not target.exists():
                log(f"  ERROR: Installer file not found at {path}")
                return {"ok": False, "error": "Installer file not found"}
            
            log(f"  Launching installer: {target}")
            
            # Launch the installer
            if os.name == "nt":
                # Windows
                os.startfile(str(target))
            else:
                # Linux/Mac (for testing)
                import subprocess
                subprocess.Popen([str(target)])
            
            log(f"  Installer launched successfully")
            return {"ok": True}
            
        except Exception as e:
            log(f"  ERROR launching installer: {e}")
            import traceback
            log(f"  Traceback: {traceback.format_exc()}")
            return {"ok": False, "error": str(e)}




    # ========== HASH COMPUTATION ==========
    
    def compute_hash(self, file_path: str, algorithm: str) -> dict:
        """Compute hash of a file using the specified algorithm"""
        log(f"compute_hash() called: {algorithm} on {Path(file_path).name}")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            log(f"  ERROR: File does not exist")
            return {"ok": False, "error": "File not found"}
        
        try:
            # Read file in chunks to handle large files
            hasher = self._get_hasher(algorithm)
            
            if hasher is None:
                log(f"  ERROR: Unknown algorithm: {algorithm}")
                return {"ok": False, "error": f"Unknown algorithm: {algorithm}"}
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(65536):  # 64KB chunks
                    hasher.update(chunk)
            
            hash_hex = hasher.hexdigest()
            log(f"  Hash computed: {hash_hex[:32]}...")
            
            return {"ok": True, "hash": hash_hex}
            
        except Exception as e:
            log(f"  ERROR computing hash: {e}")
            return {"ok": False, "error": str(e)}
    
    def _get_hasher(self, algorithm: str):
        """Get a hasher instance for the specified algorithm"""
        algorithm = algorithm.upper()
        
        # Standard algorithms
        if algorithm in ['MD5', 'SHA1', 'SHA-1', 'SHA224', 'SHA-224', 
                        'SHA256', 'SHA-256', 'SHA384', 'SHA-384', 
                        'SHA512', 'SHA-512']:
            algo_map = {
                'MD5': 'md5',
                'SHA1': 'sha1', 'SHA-1': 'sha1',
                'SHA224': 'sha224', 'SHA-224': 'sha224',
                'SHA256': 'sha256', 'SHA-256': 'sha256',
                'SHA384': 'sha384', 'SHA-384': 'sha384',
                'SHA512': 'sha512', 'SHA-512': 'sha512',
            }
            return hashlib.new(algo_map[algorithm])
        
        # SHA3 family
        elif algorithm in ['SHA3_224', 'SHA3-224', 'SHA3_256', 'SHA3-256',
                          'SHA3_384', 'SHA3-384', 'SHA3_512', 'SHA3-512']:
            algo_map = {
                'SHA3_224': 'sha3_224', 'SHA3-224': 'sha3_224',
                'SHA3_256': 'sha3_256', 'SHA3-256': 'sha3_256',
                'SHA3_384': 'sha3_384', 'SHA3-384': 'sha3_384',
                'SHA3_512': 'sha3_512', 'SHA3-512': 'sha3_512',
            }
            return hashlib.new(algo_map[algorithm])
        
        # BLAKE2
        elif algorithm in ['BLAKE2B', 'BLAKE2B-256', 'BLAKE2B-512']:
            if algorithm == 'BLAKE2B-256':
                return hashlib.blake2b(digest_size=32)
            elif algorithm == 'BLAKE2B-512':
                return hashlib.blake2b(digest_size=64)
            else:
                return hashlib.blake2b()
        
        elif algorithm in ['BLAKE2S', 'BLAKE2S-256']:
            return hashlib.blake2s()
        
        # MD4 (with fallback)
        elif algorithm == 'MD4':
            if HAS_MD4:
                log(f"  Using pure-Python MD4 fallback")
                return MD4()
            else:
                log(f"  ERROR: MD4 not available")
                return None
        
        # xxHash family
        elif algorithm in ['XXH32', 'XXH64', 'XXH3', 'XXH3-128']:
            if not HAS_XXHASH:
                log(f"  ERROR: xxhash not installed")
                return None
            
            if algorithm == 'XXH32':
                return xxhash.xxh32()
            elif algorithm == 'XXH64':
                return xxhash.xxh64()
            elif algorithm == 'XXH3':
                return xxhash.xxh3_64()
            elif algorithm == 'XXH3-128':
                return xxhash.xxh3_128()
        
        # BLAKE3
        elif algorithm == 'BLAKE3':
            if not HAS_BLAKE3:
                log(f"  ERROR: blake3 not installed")
                return None
            return blake3.blake3()
        
        # RIPEMD-160
        elif algorithm in ['RIPEMD160', 'RIPEMD-160']:
            return hashlib.new('ripemd160')
        
        else:
            log(f"  ERROR: Unknown algorithm: {algorithm}")
            return None
    
    def compute_hashes(self, file_path: str, algorithms: List[str]) -> dict:
        """Compute multiple hashes for a file"""
        log(f"compute_hashes() called with {len(algorithms)} algorithms")
        
        results = {}
        
        for algo in algorithms:
            result = self.compute_hash(file_path, algo)
            if result.get('ok'):
                results[algo] = result['hash']
            else:
                results[algo] = None
                log(f"  Failed to compute {algo}: {result.get('error')}")
        
        return {"ok": True, "hashes": results}
