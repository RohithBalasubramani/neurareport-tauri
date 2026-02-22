#!/bin/bash
# NeuraReport Desktop — Full Build Script (Linux)
#
# Usage: ./build.sh [appimage|deb|all] [--skip-sidecar]
# Default: appimage (single portable executable)
#
# Prerequisites:
#   - .venv with backend dependencies + pyinstaller
#   - Node.js + npm
#   - Rust toolchain
#   - linuxdeploy + AppRun in ~/.cache/tauri/

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
SRC_TAURI="$FRONTEND_DIR/src-tauri"
BUNDLE_DIR="$SRC_TAURI/target/release/bundle"
INSTALLERS_DIR="$SCRIPT_DIR/installers"

TARGET="${1:-appimage}"
SKIP_SIDECAR=false
for arg in "$@"; do
  [ "$arg" = "--skip-sidecar" ] && SKIP_SIDECAR=true
done

echo "=== NeuraReport Desktop Build ==="
echo "Target: $TARGET"
echo ""

# ——————————————————————————————————————————
# Step 0: Build Python backend sidecar
# ——————————————————————————————————————————
if [ "$SKIP_SIDECAR" = false ]; then
  echo "[0/3] Building backend sidecar (PyInstaller)..."
  "$SCRIPT_DIR/.venv/bin/pyinstaller" backend/neurareport-backend.spec \
    --distpath "$SRC_TAURI/" --noconfirm --clean 2>&1 | tail -3

  # Resolve symlinks (Tauri resource copy doesn't handle them)
  echo "Resolving symlinks..."
  SIDECAR_DIR="$SRC_TAURI/neurareport-backend"
  find "$SIDECAR_DIR" -type l | while read link; do
    target=$(readlink -f "$link")
    if [ -f "$target" ]; then
      rm "$link"
      cp "$target" "$link"
    fi
  done
  echo "Done ($(find "$SIDECAR_DIR" -type l | wc -l) symlinks remaining)"
  echo ""
else
  echo "[0/3] Skipping sidecar build (--skip-sidecar)"
  echo ""
fi

cd "$FRONTEND_DIR"

# ——————————————————————————————————————————
# Step 1: Build via Tauri (deb works cleanly)
# ——————————————————————————————————————————
echo "[1/3] Building Tauri application (deb)..."
npx tauri build --bundles deb 2>&1 | tail -5
echo ""

DEB_FILE="$BUNDLE_DIR/deb/NeuraReport_1.0.0_amd64.deb"
if [ ! -f "$DEB_FILE" ]; then
  echo "ERROR: .deb build failed"
  exit 1
fi

mkdir -p "$INSTALLERS_DIR"

if [ "$TARGET" = "deb" ]; then
  cp "$DEB_FILE" "$INSTALLERS_DIR/"
  echo "=== Done ==="
  echo "Installer: $INSTALLERS_DIR/NeuraReport_1.0.0_amd64.deb"
  exit 0
fi

# ——————————————————————————————————————————
# Step 2: Create AppImage from deb structure
# ——————————————————————————————————————————
if [ "$TARGET" = "appimage" ] || [ "$TARGET" = "all" ]; then
  echo "[2/3] Creating AppImage..."

  APPIMAGE_DIR="$BUNDLE_DIR/appimage"
  APPDIR="$APPIMAGE_DIR/NeuraReport.AppDir"
  DEB_DATA="$BUNDLE_DIR/deb/NeuraReport_1.0.0_amd64"

  rm -rf "$APPDIR" "$APPIMAGE_DIR"/*.AppImage
  mkdir -p "$APPIMAGE_DIR"

  # Build AppDir from deb data
  mkdir -p "$APPDIR"
  cp -r "$DEB_DATA/data/usr" "$APPDIR/usr"

  # AppRun binary
  cp "$HOME/.cache/tauri/AppRun-x86_64" "$APPDIR/AppRun"
  chmod +x "$APPDIR/AppRun"

  # Desktop entry
  cat > "$APPDIR/NeuraReport.desktop" << 'DESKTOP'
[Desktop Entry]
Categories=Utility;
Comment=NeuraReport Desktop Application
Exec=neurareport-desktop
Icon=neurareport-desktop
Name=NeuraReport
Terminal=false
Type=Application
DESKTOP

  # Icon
  ICON_SRC="$(find "$APPDIR/usr/share/icons" -name "*.png" -print -quit 2>/dev/null)"
  if [ -n "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$APPDIR/neurareport-desktop.png"
    ln -sf neurareport-desktop.png "$APPDIR/.DirIcon"
  fi

  # Run linuxdeploy with PyInstaller-compatible env vars
  NO_STRIP=1 \
  ARCH=x86_64 \
  LD_LIBRARY_PATH="$APPDIR/usr/lib/NeuraReport/_internal:$APPDIR/usr/lib/NeuraReport/_internal/pillow.libs" \
  "$HOME/.cache/tauri/linuxdeploy-x86_64.AppImage" \
    --appdir "$APPDIR" \
    --output appimage 2>&1 | grep -E "Success|ERROR" | head -5

  APPIMAGE_FILE="$(ls "$APPIMAGE_DIR"/NeuraReport*.AppImage 2>/dev/null | head -1)"
  if [ -z "$APPIMAGE_FILE" ]; then
    echo "ERROR: AppImage creation failed"
    exit 1
  fi

  cp "$APPIMAGE_FILE" "$INSTALLERS_DIR/NeuraReport_1.0.0_x86_64.AppImage"
  echo "AppImage: $(du -h "$INSTALLERS_DIR/NeuraReport_1.0.0_x86_64.AppImage" | cut -f1)"
fi

# ——————————————————————————————————————————
# Step 3: Copy deb if building all
# ——————————————————————————————————————————
if [ "$TARGET" = "all" ]; then
  cp "$DEB_FILE" "$INSTALLERS_DIR/"
  echo ".deb: $(du -h "$INSTALLERS_DIR/NeuraReport_1.0.0_amd64.deb" | cut -f1)"
fi

echo ""
echo "=== Build Complete ==="
ls -lh "$INSTALLERS_DIR/"*.AppImage "$INSTALLERS_DIR/"*.deb 2>/dev/null
