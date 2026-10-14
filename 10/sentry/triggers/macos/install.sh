#!/usr/bin/env bash
# Install the Sentry LaunchAgent on macOS. Run from this folder:
#   bash install.sh
# Uninstall: bash uninstall.sh
set -euo pipefail

SENTRY_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="$(command -v python3)"
PLIST_SRC="$SENTRY_DIR/triggers/macos/com.sentry.monitor.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.sentry.monitor.plist"

echo "Sentry dir : $SENTRY_DIR"
echo "Python     : $PYTHON"

mkdir -p "$HOME/Library/LaunchAgents" "$SENTRY_DIR/evidence"

# Fill the placeholders into a copy in LaunchAgents.
sed -e "s#__PYTHON__#$PYTHON#g" \
    -e "s#__SENTRY_DIR__#$SENTRY_DIR#g" \
    "$PLIST_SRC" > "$PLIST_DST"

# Reload.
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

echo
echo "Installed and loaded: com.sentry.monitor"
echo "It is listed openly here:"
launchctl list | grep sentry || true
echo
echo "IMPORTANT (macOS privacy): the first time it runs, macOS will ask you"
echo "to grant Camera and Screen Recording permission. Approve both in"
echo "System Settings -> Privacy & Security, or captures will be blank."
echo
echo "For wake-from-sleep capture too, install sleepwatcher:"
echo "  brew install sleepwatcher"
echo "  echo '$PYTHON $SENTRY_DIR/capture.py --once' > ~/.wakeup"
echo "  chmod +x ~/.wakeup"
echo "  brew services start sleepwatcher"
