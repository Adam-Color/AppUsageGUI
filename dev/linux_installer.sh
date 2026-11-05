#!/bin/bash
#
# Packages the PyInstaller output (dist/AppUsageGUI/) into a Linux AppImage.
#
# An AppImage is a single file that runs on almost any distro (Ubuntu, Fedora,
# Arch, openSUSE, ...) without installing anything: download, chmod +x, run.
#
# Run `python build.py` first, then: bash dev/linux_installer.sh
#
# Output (both in dist/):
#   AppUsageGUI_v<version>_LINUX_<arch>.AppImage
#   AppUsageGUI_v<version>_LINUX_<arch>.AppImage.sha256
#
# Optional environment variables:
#   APPIMAGETOOL   path to an existing appimagetool binary (skips the download)
#   RELEASE_DATE   release date (YYYY-MM-DD) written to the metadata, default: today (UTC)
set -euo pipefail

if [ "$(uname -s)" != "Linux" ]; then
    echo "Error: this script must be run on Linux." >&2
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

APP_NAME="AppUsageGUI"
# Reverse-DNS ID. For projects hosted on GitHub the convention is
# io.github.<user>.<App>, with "-" in the username replaced by "_".
APP_ID="io.github.adam_color.AppUsageGUI"

# Pinned so builds are reproducible. To upgrade, change the version and update
# the checksums from https://github.com/AppImage/appimagetool/releases
APPIMAGETOOL_VERSION="1.9.1"
APPIMAGETOOL_SHA256_X86_64="ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0"
APPIMAGETOOL_SHA256_AARCH64="f0837e7448a0c1e4e650a93bb3e85802546e60654ef287576f46c71c126a9158"

# Read version from _version.py (no Python needed)
app_version="$(sed -n 's/^__version__ *= *"\(.*\)".*/\1/p' src/_version.py)"
if [ -z "$app_version" ]; then
    echo "Error: could not read the version from src/_version.py" >&2
    exit 1
fi

case "$(uname -m)" in
    x86_64|amd64)  ARCH="x86_64";  APPIMAGETOOL_SHA256="$APPIMAGETOOL_SHA256_X86_64" ;;
    aarch64|arm64) ARCH="aarch64"; APPIMAGETOOL_SHA256="$APPIMAGETOOL_SHA256_AARCH64" ;;
    *)
        echo "Error: unsupported architecture '$(uname -m)' (supported: x86_64, aarch64)" >&2
        exit 1
        ;;
esac

RELEASE_DATE="${RELEASE_DATE:-$(date -u +%Y-%m-%d)}"

PYINSTALLER_DIR="dist/${APP_NAME}"
WORK_DIR="build/linux"
APPDIR="${WORK_DIR}/${APP_NAME}.AppDir"
OUTPUT_NAME="${APP_NAME}_v${app_version}_LINUX_${ARCH}.AppImage"
OUTPUT="dist/${OUTPUT_NAME}"

echo "Building Linux AppImage for version $app_version ($ARCH)..."

if [ ! -x "${PYINSTALLER_DIR}/${APP_NAME}" ]; then
    echo "Error: ${PYINSTALLER_DIR}/${APP_NAME} not found. Run 'python build.py' first." >&2
    exit 1
fi

# --- Assemble the AppDir ---------------------------------------------------
# The AppDir mirrors a normal Linux filesystem layout (usr/bin, usr/share, ...)
rm -rf "$APPDIR"
mkdir -p \
    "$APPDIR/usr/bin" \
    "$APPDIR/usr/lib" \
    "$APPDIR/usr/share/applications" \
    "$APPDIR/usr/share/metainfo" \
    "$APPDIR/usr/share/icons/hicolor/512x512/apps" \
    "$APPDIR/usr/share/licenses/${APP_NAME}"

# The PyInstaller folder must stay together (the executable needs _internal/ next to it)
cp -a "$PYINSTALLER_DIR" "$APPDIR/usr/lib/${APP_NAME}"
ln -s "../lib/${APP_NAME}/${APP_NAME}" "$APPDIR/usr/bin/${APP_NAME}"

# Desktop entry: makes the app show up in the application menu
cp "$SCRIPT_DIR/linux/${APP_ID}.desktop" "$APPDIR/usr/share/applications/${APP_ID}.desktop"
cp "$SCRIPT_DIR/linux/${APP_ID}.desktop" "$APPDIR/${APP_ID}.desktop"

# Icon (must also sit in the AppDir root, plus a .DirIcon link, for AppImage tooling)
cp src/core/resources/icon.png "$APPDIR/usr/share/icons/hicolor/512x512/apps/${APP_ID}.png"
cp src/core/resources/icon.png "$APPDIR/${APP_ID}.png"
ln -s "${APP_ID}.png" "$APPDIR/.DirIcon"

# AppStream metadata with the current version/date filled in
sed -e "s/@VERSION@/${app_version}/g" -e "s/@DATE@/${RELEASE_DATE}/g" \
    "$SCRIPT_DIR/linux/${APP_ID}.metainfo.xml" \
    > "$APPDIR/usr/share/metainfo/${APP_ID}.metainfo.xml"

cp LICENSE.txt "$APPDIR/usr/share/licenses/${APP_NAME}/LICENSE.txt"

# AppRun is the entry point that runs when the AppImage is launched
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE="${APPDIR:-$(dirname "$(readlink -f "$0")")}"
exec "$HERE/usr/lib/AppUsageGUI/AppUsageGUI" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# --- Validate metadata -----------------------------------------------------
if command -v desktop-file-validate >/dev/null 2>&1; then
    desktop-file-validate "$APPDIR/usr/share/applications/${APP_ID}.desktop"
    echo "Desktop entry is valid."
else
    echo "Warning: desktop-file-validate not found (apt install desktop-file-utils); skipping check." >&2
fi

if command -v appstreamcli >/dev/null 2>&1; then
    # Not fatal: newer/older appstream versions disagree on minor style rules
    appstreamcli validate --no-net "$APPDIR/usr/share/metainfo/${APP_ID}.metainfo.xml" \
        || echo "Warning: AppStream metadata has validation issues (see above)." >&2
else
    echo "Warning: appstreamcli not found (apt install appstream); skipping check." >&2
fi

# --- Get appimagetool ------------------------------------------------------
if [ -n "${APPIMAGETOOL:-}" ]; then
    APPIMAGETOOL_BIN="$APPIMAGETOOL"
else
    APPIMAGETOOL_BIN="${WORK_DIR}/appimagetool-${APPIMAGETOOL_VERSION}-${ARCH}.AppImage"
    if [ ! -f "$APPIMAGETOOL_BIN" ]; then
        echo "Downloading appimagetool ${APPIMAGETOOL_VERSION}..."
        curl -fsSL -o "$APPIMAGETOOL_BIN" \
            "https://github.com/AppImage/appimagetool/releases/download/${APPIMAGETOOL_VERSION}/appimagetool-${ARCH}.AppImage"
    fi
    echo "${APPIMAGETOOL_SHA256}  ${APPIMAGETOOL_BIN}" | sha256sum -c -
    chmod +x "$APPIMAGETOOL_BIN"
fi

# --- Build the AppImage ----------------------------------------------------
mkdir -p dist
rm -f "$OUTPUT" "$OUTPUT.sha256"

# APPIMAGE_EXTRACT_AND_RUN lets appimagetool run without FUSE (e.g. in CI/containers).
# --no-appstream: we already validated the metadata above.
ARCH="$ARCH" APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL_BIN" --no-appstream "$APPDIR" "$OUTPUT"
chmod +x "$OUTPUT"

# Checksum so users can verify their download:  sha256sum -c <file>.sha256
(cd dist && sha256sum "$OUTPUT_NAME" > "${OUTPUT_NAME}.sha256")

echo "Linux AppImage created: $OUTPUT"
echo "Checksum created:       $OUTPUT.sha256"
