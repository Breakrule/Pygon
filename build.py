import os
import subprocess
import shutil

import sys

print("Building Pygon using PyInstaller...")

# Clean previous builds
for folder in ["build", "dist"]:
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)

# Resolve the pyinstaller executable in the virtual environment
pyinstaller_path = os.path.join(os.path.dirname(sys.executable), "pyinstaller.exe")
if not os.path.exists(pyinstaller_path):
    pyinstaller_path = "pyinstaller" # Fallback to standard PATH

# Clean environment variables to prevent global python interference
env = os.environ.copy()
env.pop("PYTHONHOME", None)
env.pop("PYTHONPATH", None)

# We package the main pygon.py as windowed to hide the black console
subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--clean",
    "--noconfirm",
    "--name", "Pygon",
    "--onefile", # Single standalone executable
    "--windowed", # hide console loop
    "--icon", "NONE", # we don't have an icon yet
    "--add-data", f"services{os.pathsep}services", # Copy the whole directory
    "--collect-all", "services", # Force include dynamic modules
    "pygon.py"
], env=env)

print("Build complete. Copying necessary directories...")

# PyInstaller creates dist/Pygon.exe
dist_dir = "dist"

# Ensure required folders exist in the distribution next to the EXE
for folder in ["bin", "www"]:
    os.makedirs(os.path.join(dist_dir, folder), exist_ok=True)

# Copy default index
if os.path.exists("www/index.html"):
    shutil.copy("www/index.html", os.path.join(dist_dir, "www", "index.html"))

print("Packaging Finished! Accessible at dist/Pygon.exe")
