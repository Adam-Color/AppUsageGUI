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
        windows_only_1 = '--collect-submodules pywinauto'
    run_command(
        f'{python_executable} -m PyInstaller -D --clean --name {PROJECT_NAME} '
        f'--noconfirm '
        f'--windowed '
        f'--add-data "src/core:core" '
        f'--add-data "{icon_file}:." '
        f'--add-data "LICENSE.txt:." '
        f'{windows_only_1} '
        f'--collect-submodules core '
        f'--collect-submodules psutil '
        f'--collect-submodules tkinter '
        f'--collect-submodules pynput '
        f'--collect-submodules requests '
        f'--collect-submodules PIL '
        f'--collect-submodules pyperclip '
        f'--exclude-module PIL.tests '
        f'--exclude-module tkinter.test '
        f'--icon={icon_file} '
        f'--add-data "src/_version.py:." '
        f'--add-data "src/_path.py:." '
        f'--add-data "src/_logging.py:." '
        f'--target-architecture {platform.machine()} '
        f'{ENTRY_POINT}'
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
