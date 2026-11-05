AppUsageGUI for Linux is distributed as an [AppImage](https://appimage.org/): a single file that runs on most distributions (Ubuntu, Debian, Fedora, Arch, openSUSE, ...) with no installation.

Builds are available for **x86_64** (most PCs) and **aarch64** (ARM, e.g. Raspberry Pi 4/5 with a 64-bit OS). Not sure which you have? Run `uname -m`.

## Linux Installation Steps:

- download the AppImage for your architecture [here](https://github.com/Adam-Color/AppUsageGUI/releases/latest) (under the "assets" section)
- (optional) verify the download, with the `.sha256` file in the same folder:

```shell
sha256sum -c AppUsageGUI_v*_LINUX_x86_64.AppImage.sha256
```

- make it executable:

```shell
chmod +x AppUsageGUI_v*_LINUX_x86_64.AppImage
```

- run it:

```shell
./AppUsageGUI_v*_LINUX_x86_64.AppImage
```

To update, download the new AppImage and delete the old one.

## Adding AppUsageGUI to your application menu

AppImages don't add themselves to your menu. Tools like [AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher), [Gear Lever](https://flathub.org/apps/it.mijorus.gearlever) or [Dumpling](https://github.com/probonopd/dumpling) can do this for you.

## Troubleshooting

- **"AppImages require FUSE to run" / it does not start:** install FUSE (`libfuse2` on Debian/Ubuntu, `fuse-libs` on Fedora), or run it without FUSE:

```shell
./AppUsageGUI_v*_LINUX_x86_64.AppImage --appimage-extract-and-run
```

- **Wayland:** AppUsageGUI uses X11 features to detect idle time. On a Wayland desktop it runs through XWayland, and mouse-idle detection may be limited. Logging in with an X11 session works fully.

Your sessions and settings are stored in `~/.local/share/AppUsageGUI`.
