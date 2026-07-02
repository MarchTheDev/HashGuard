# 🔒 HashGuard

**HashGuard** is a fast, robust, and completely offline desktop tool for generating and verifying cryptographic file checksums (**MD5, SHA-1, SHA-256, and SHA-512**). Written in Python using **CustomTkinter** and **TkinterDnD2**, it features a modern glassmorphic interface, interactive drag-and-drop actions, bulk text verification, a custom theme engine, and a secure automated self-updater from GitHub.

---

## ✨ Features

- **No Data Leaves Your Machine:** Checksums are processed entirely locally using Python's native `hashlib` library.
- **Selectable Hash Methods:** Instantly show or hide hash formats depending on your needs. Your selection is remembered!
- **Fluid Drag & Drop:** Just drag and drop your target file onto the drop-zone to compute its hashes instantly.
- **Advanced Verification:** 
  - Paste a single checksum to automatically identify its algorithm and check against the file.
  - Drag and drop or load a `.txt` hash file (e.g. standard file format `MD5: ...` and `SHA-256: ...`) to verify multiple checksums simultaneously.
- **Dynamic Theme Engine:**
  - Includes beautiful built-in presets: *Cyberpunk Dark, Emerald Garden, Rubellite Crimson, Amethyst Purple, and Sunset Gold*.
  - Includes a fully customized theme creator—choose your favorite colors, save them, and they are applied instantly and persisted.
- **Automated Self-Updates:** Query the latest GitHub Releases directly from the app, download the update package, and launch the installer in one click.
- **Troubleshooting Logs:** Integrated logging writes all actions and errors to a persistent log file (`~/.hashguard.log`) for easy debugging.

---

## 🛠️ Installation & Running from Source

### Prerequisites

You need **Python 3.10+** installed on your computer.

### Step 1: Clone the Repository
```bash
git clone https://github.com/MarchTheDev/HashGuard.git
cd HashGuard
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python hashguard.py
```

---

## 🚀 Building & Packaging

### Local Compilation with PyInstaller

To bundle the application into a standalone Windows executable (`.exe`):

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Compile:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name "HashGuard" --collect-all tkinterdnd2 --collect-all customtkinter hashguard.py
   ```
The standalone executable will be generated inside the `dist/` directory.

---

## ⚙️ Automated GitHub CI/CD

This repository comes with preconfigured **GitHub Actions** and **NSIS Installer scripts** for compiling and releasing Windows builds automatically!

### How the automated workflow works:
1. **GitHub Action (`.github/workflows/build.yml`)**:
   Every time you push a version change to the `VERSION` file, GitHub Actions will:
   - Check out the codebase.
   - Set up Python and install all dependencies.
   - Build a standalone `.exe` using PyInstaller.
   - Compile a professional installer (`HashGuard-Setup-*.exe`) using NSIS.
   - Package a portable `.zip` file.
   - Publish a new **Draft Release** with these installer assets ready for download.

2. **NSIS Installer (`installer.nsi`)**:
   Compiles a complete Windows installer that sets up registry keys, desktop & start menu shortcuts, an uninstaller, and terminates active processes of the application before replacing files during updates.

3. **Software Self-Update**:
   The "Updates" section in the app settings automatically queries this repository, compares versions, downloads the installer `HashGuard-Setup-*.exe` silently, and runs it to seamlessly perform the update!

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
