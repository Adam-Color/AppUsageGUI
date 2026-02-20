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
    
    version_str = '.'.join(version_parts[:4])
    # Convert to tuple format (e.g., "1.8.5.0" -> (1, 8, 5, 0))
    version_tuple = tuple(int(x) for x in version_parts[:4])
    
    version_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx?id=7
VSVersionInfo(
  ffi=FixedFileInfo(
    # Contains as much info as Windows will allow. All of these
    # items are strings. Include them all.
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[StringFileInfo(
    [StringTable(u'040904B0',
    [StringTable(u'CompanyName', u''),
     StringTable(u'FileDescription', u'{PROJECT_NAME}'),
     StringTable(u'FileVersion', u'{version_str}'),
     StringTable(u'InternalName', u'{PROJECT_NAME}'),
     StringTable(u'LegalCopyright', u''),
     StringTable(u'OriginalFilename', u'{PROJECT_NAME}.exe'),
     StringTable(u'ProductName', u'{PROJECT_NAME}'),
     StringTable(u'ProductVersion', u'{version_str}')])]),
   VarFileInfo([VarFileInfo(u'Translation', [1033, 1200])])],
  strFileInfo=None
  description="AppUsageGUI"

)
'''
    with open('version_info.txt', 'w') as f:
        f.write(version_content)
    return '--version-file=version_info.txt'

def create_macos_app_bundle_info():
    """Create Info.plist for macOS .app bundle."""
    version = get_version()
    bundle_id = "com.appusagegui.app"
    
    info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>AppUsageGUI</string>
    <key>CFBundleExecutable</key>
    <string>{PROJECT_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_id}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>AppUsageGUI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{version}</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2026. All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
'''
    
    app_bundle = os.path.join(DIST_DIR, f"{PROJECT_NAME}.app")
    contents_dir = os.path.join(app_bundle, "Contents")
    os.makedirs(contents_dir, exist_ok=True)
    
    info_plist_path = os.path.join(contents_dir, "Info.plist")
    with open(info_plist_path, 'w') as f:
        f.write(info_plist)
    print(f"Created Info.plist at {info_plist_path}")

if __name__ == "__main__":
    build_executable()
    if platform.system() == "Darwin":  # macOS
        create_macos_app_bundle_info()
    print(f"Build completed successfully!")
