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

def get_version():
    """Read version from src/_version.py"""
    sys.path.insert(0, 'src')
    from _version import __version__
    return __version__

def build_executable():
    """Build the application using PyInstaller."""
    python_executable = os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin", "python")

    icon_file = "src/core/resources/icon.ico" if os.name == 'nt' else "src/core/resources/icon.icns"
    version = get_version()
    
    # Set environment variable in the current process
    os.environ['PYTHONOPTIMIZE'] = '1'
    
    print(f"Building {PROJECT_NAME} v{version}...")
    
    windows_only_1 = '--collect-submodules pywinauto' if os.name == 'nt' else ""
    version_file = ""
    
    # On Windows, create a version file for the .exe
    if os.name == 'nt':
        version_file = create_version_file(version)
    
    run_command(
        f'{python_executable} -m PyInstaller -D --clean --name {PROJECT_NAME} '
        f'--noconfirm '
        f'--windowed '
        f'--add-data "src/core:core" '
        f'--add-data "{icon_file}:." '
        f'--add-data "LICENSE.txt:." '
        f'{windows_only_1} '
        f'--collect-submodules psutil '
        f'--collect-submodules tkinter '
        f'--collect-submodules pynput '
        f'--collect-submodules requests '
        f'--collect-submodules urllib3 '
        f'--hidden-import=PIL.Image '
        f'--hidden-import=PIL.ImageTk '
        f'--collect-submodules pyperclip '
        f'--exclude-module tkinter.test '
        f'--exclude-module tkinter.demos '
        f'--exclude-module PIL.ImageCms '
        f'--exclude-module PIL.ImageQt '
        f'--exclude-module PIL.ImageWin '
        f'--exclude-module PIL._imagingft '
        f'--icon={icon_file} '
        f'--add-data "src/_version.py:." '
        f'--add-data "src/_path.py:." '
        f'--add-data "src/_logging.py:." '
        f'{version_file} '
        f'{ENTRY_POINT}'
    )
    
    # Clean up version file if created
    if version_file and os.path.exists('version_info.txt'):
        os.remove('version_info.txt')

def create_version_file(version):
    """Create a version file for PyInstaller on Windows."""
    version_parts = version.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
