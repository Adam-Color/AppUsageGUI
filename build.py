import os
import sys
import shutil
import subprocess
import platform

# Project details
PROJECT_NAME = "AppUsageGUI"
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

    icon_file = "src/core/resources/icon.ico" if os.name == 'nt' else "src/core/resources/icon.icns"
    print("Building the application...")
    if sys.platform == 'darwin':
        run_command('export PYTHONOPTIMIZE=1')
        windows_only_1 = ""
    else:
        run_command('set PYTHONOPTIMIZE=1')
        windows_only_1 = '--collect-all pywinauto'
    run_command(
        f'{python_executable} -m PyInstaller -D --clean --name {PROJECT_NAME} '
        f'--noconfirm '
        f'--windowed --clean '
        f'--add-data "src/core:core" '
        f'--add-data "{icon_file}:." '
        f'--add-data "LICENSE.txt:." '
        f'--collect-submodules core '
        f'--collect-all psutil '
        f'--collect-all tkinter '
        f'--collect-all pynput '
        f'--collect-all requests '
        f'--collect-all PIL '
        f'{windows_only_1} '
        f'--icon={icon_file} '
        f'--add-data "src/_version.py:." '
        f'--add-data "src/_path.py:." '
        f'--target-architecture {platform.machine()} '
        f'--debug=imports {ENTRY_POINT}'
    )

def clean_up():
    """Remove build artifacts."""
    print("Cleaning up...")
    for folder in [BUILD_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

def main():
    print(f"Starting build process for {PROJECT_NAME} under {platform.machine()}...")

    build_executable()
    clean_up()

    print(f"Build completed! Executable is in the '{DIST_DIR}' directory.")

if __name__ == "__main__":
    main()
