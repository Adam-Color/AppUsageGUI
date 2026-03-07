#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

# Read version from _version.py
app_version=$(python -c "import sys; sys.path.insert(0, 'src'); from _version import __version__; print(__version__)")

echo "Building macOS installer for version $app_version..."

# Ensure dist directory exists
mkdir -p dist/AppUsageGUI

# Update Info.plist
plutil -replace CFBundleShortVersionString -string "$app_version" "dist/AppUsageGUI.app/Contents/Info.plist"

# Move .app into folder for DMG
mv "dist/AppUsageGUI.app" "dist/AppUsageGUI/"

# Create DMG with correct paths
create-dmg \
  --volicon "src/core/resources/icon.icns" \
  --volname "AppUsageGUIsetup" \
  --window-pos 200 190 \
  --window-size 800 400 \
  --app-drop-link 600 185 \
  --eula "LICENSE.txt" \
  "dist/AppUsageGUI_v${app_version}_macOS_setup.dmg" \
  "dist/AppUsageGUI/"

echo "macOS installer created: dist/AppUsageGUI_v${app_version}_macOS_setup.dmg"
