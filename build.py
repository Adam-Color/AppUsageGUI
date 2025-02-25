import os
import sys
import shutil
import subprocess

from src._version import __version__

# Project details
PROJECT_NAME = f"AppUsageGUI-v{__version__}"
ENTRY_POINT = "src/main.py"
BUILD_DIR = "build"
DIST_DIR = "dist"
VENV_DIR = ".venv"

def run_command(command):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error: Command '{command}' failed.")
        sys.exit(1)


def build_executable():
    """Build the application using PyInstaller."""
    python_executable = os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin", "python")

    print("Building the application...")
    run_command(
        f'{python_executable} -m PyInstaller --onefile --name {PROJECT_NAME} '
        f'--windowed --clean '
        f'--add-data "src/core{":" if os.name != "nt" else ";"}core" '
        f'--collect-submodules core '
        f'--collect-all psutil '
        f'--collect-all pyautogui '
        f'--collect-all tkinter '
        f'--debug=imports {ENTRY_POINT}'
)



def clean_up():
    """Remove build artifacts."""
    print("Cleaning up...")
    for folder in [BUILD_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

def main():
    print(f"Starting build process for {PROJECT_NAME}...")

    build_executable()
    clean_up()

    print(f"Build completed! Executable is in the '{DIST_DIR}' directory.")

if __name__ == "__main__":
    main()
