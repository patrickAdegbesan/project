#!/usr/bin/env bash
# Install Sentry triggers on Linux (tested on Fedora). Run from this folder:
#   bash install.sh
#
# Installs two things:
#   1. a system-sleep hook  -> fires on resume-from-suspend  (needs sudo)
#   2. a systemd user service -> fires at graphical login    (no sudo)
#
# Both are listed openly; uninstall with uninstall.sh.
set -euo pipefail

SENTRY_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="$(command -v python3)"
RUN_AS="$(id -un)"
HOOK_SRC="$SENTRY_DIR/triggers/linux/sentry-resume"
UNIT_SRC="$SENTRY_DIR/triggers/linux/sentry.service"
HOOK_DST="/usr/lib/systemd/system-sleep/sentry-resume"
UNIT_DST="$HOME/.config/systemd/user/sentry.service"

echo "Sentry dir : $SENTRY_DIR"
echo "Python     : $PYTHON"
echo "Run as     : $RUN_AS"

mkdir -p "$SENTRY_DIR/evidence"

# 1. Resume hook (root-owned, executable).
echo "Installing resume hook (sudo)..."
sudo bash -c "sed -e 's#__SENTRY_DIR__#$SENTRY_DIR#g' \
                  -e 's#__PYTHON__#$PYTHON#g' \
                  -e 's#__RUN_AS__#$RUN_AS#g' \
                  '$HOOK_SRC' > '$HOOK_DST'"
sudo chmod 755 "$HOOK_DST"

# 2. User login service.
echo "Installing user service..."
mkdir -p "$HOME/.config/systemd/user"
sed -e "s#__SENTRY_DIR__#$SENTRY_DIR#g" \
    -e "s#__PYTHON__#$PYTHON#g" \
    "$UNIT_SRC" > "$UNIT_DST"
systemctl --user daemon-reload
systemctl --user enable sentry.service

echo
echo "Done. Verify openly with:"
echo "  ls -l $HOOK_DST"
echo "  systemctl --user status sentry.service"
echo
echo "Fedora notes:"
echo "  * Camera access needs the v4l2 device readable by your user"
echo "    (group 'video'): groups | grep video"
echo "  * Pure-Wayland sessions block screenshots for background apps;"
echo "    GNOME on Fedora works for the logged-in user. If screenshots come"
echo "    out blank, set screenshot=false in config.ini and rely on webcam."
