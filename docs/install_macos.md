## macOS Installation Steps:
* download the macOS setup .dmg [here](https://github.com/Adam-Color/AppUsageGUI/releases/latest) (under the "assets" section)
* double-click the .dmg to open it
* agree to the [license](../LICENSE.txt)
* drag the "AppUsageGUI" folder to the "Applications" folder

## Running on macOS:
>Due to Apple's restrictions when it comes to open source applications such as ours, a workaround is needed to get AppUsageGUI to run on macOS.

If you encounter the error message saying the app was not opened, click "done", then go into your security settings and allow AppUsageGUI to run on your device

Enter this in your terminal if AppUsageGUI does not run:

```shell
xattr -dr com.apple.quarantine /Applications/DisplayCAL.app
```