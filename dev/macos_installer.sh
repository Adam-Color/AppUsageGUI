#!/bin/bash
# This script is used to create the installer for the macOS version of the application
app_version='1.8.2'

plutil -replace CFBundleShortVersionString -string ${app_version} ../dist/AppUsageGUI.app/Contents/Info.plist

mv ../dist/AppUsageGUI.app ../dist/AppUsageGUI/

create-dmg --volicon ../src/core/resources/icon.icns --volname AppUsageGUIsetup --window-pos 200 190 --window-size 800 400 --app-drop-link 600 185 --eula ../LICENSE.txt ../dist/AppUsageGUI_v${app_version}_macOS_arm64_setup.dmg ../dist/
