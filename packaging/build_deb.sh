#!/usr/bin/env bash
# Builds a .deb package for Focus Timer.
# Run from anywhere; produces dist/focus-timer_<version>_amd64.deb.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VERSION="$(cat VERSION)"
PKG_NAME="focus-timer"
ARCH="amd64"
STAGING_DIR="packaging/staging"
DIST_DIR="dist"

if [ ! -f packaging/icon.png ]; then
  echo "error: packaging/icon.png is missing" >&2
  exit 1
fi

if [ ! -d .venv ]; then
  echo "error: .venv not found; run 'python -m venv .venv && pip install -r requirements.txt' first" >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if ! python -c "import PyInstaller" 2>/dev/null; then
  echo "Installing PyInstaller (build-only tool, not a runtime dependency)..."
  pip install pyinstaller
fi

echo "Building standalone executable with PyInstaller..."
rm -rf build "$DIST_DIR/$PKG_NAME"
pyinstaller packaging/focus-timer.spec --distpath "$DIST_DIR" --workpath build --noconfirm

echo "Assembling .deb staging tree..."
rm -rf "$STAGING_DIR"
mkdir -p \
  "$STAGING_DIR/DEBIAN" \
  "$STAGING_DIR/opt/$PKG_NAME" \
  "$STAGING_DIR/usr/bin" \
  "$STAGING_DIR/usr/share/applications" \
  "$STAGING_DIR/usr/share/pixmaps"

cp -r "$DIST_DIR/$PKG_NAME/." "$STAGING_DIR/opt/$PKG_NAME/"
ln -s "/opt/$PKG_NAME/$PKG_NAME" "$STAGING_DIR/usr/bin/$PKG_NAME"
cp packaging/focus-timer.desktop "$STAGING_DIR/usr/share/applications/"
cp packaging/icon.png "$STAGING_DIR/usr/share/pixmaps/focus-timer.png"

INSTALLED_SIZE="$(du -sk "$STAGING_DIR/opt/$PKG_NAME" | cut -f1)"

cat > "$STAGING_DIR/DEBIAN/control" <<EOF
Package: $PKG_NAME
Version: $VERSION
Architecture: $ARCH
Installed-Size: $INSTALLED_SIZE
Maintainer: Focus Timer <focus-timer@localhost>
Recommends: ffmpeg | vlc, libnotify-bin, pulseaudio-utils
Section: utils
Priority: optional
Description: Compact Pomodoro desktop widget with a local music player
 Focus Timer is a small cross-platform Pomodoro widget with classic and
 custom timer cycles, an alarm and desktop notifications, and an optional
 collapsible local music player for concentration playlists.
EOF

echo "Building .deb..."
mkdir -p "$DIST_DIR"
DEB_PATH="$DIST_DIR/${PKG_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "$STAGING_DIR" "$DEB_PATH"

echo "Built: $DEB_PATH"
