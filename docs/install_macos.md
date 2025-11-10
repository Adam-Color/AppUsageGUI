Note: only arm-based systems are currently supported.

## macOS Installation Steps:
* download the macOS setup .dmg [here](https://github.com/Adam-Color/AppUsageGUI/releases/latest) (under the "assets" section)
* ensure that the old version of AppUsageGUI is closed if you are updating
* double-click the .dmg to open it
* agree to the license
* drag the "AppUsageGUI" folder to the "Applications" folder
* if asked to replace another folder, agree to do so

## Running on macOS:

If you encounter the error message saying the app was not opened or was damaged, click "done" or "cancel", then enter this in your terminal:
```shell
xattr -dr com.apple.quarantine /Applications/AppUsageGUI/AppUsageGUI.app
```
If you mistakingly hit 'move to trash' or 'delete', repeat installation steps.

 If you continue to get error messsages, go into your security settings and allow AppUsageGUI to run on your device
