#!/bin/bash
# This script is used to create the installer for the macOS version of the application

create-dmg --volicon src/core/resources/icon.icns --volname AppUsageGUIsetup --window-pos 200 190 --window-size 800 400 --app-drop-link 600 185 --eula LICENSE.txt dist/AppUsageGUI_v1.2.0_MACOS_setup.dmg dist/AppUsageGUI.app