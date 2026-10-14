#!/usr/bin/env bash
# Remove the Sentry LaunchAgent on macOS.
set -euo pipefail
PLIST_DST="$HOME/Library/LaunchAgents/com.sentry.monitor.plist"
launchctl unload "$PLIST_DST" 2>/dev/null || true
rm -f "$PLIST_DST"
echo "Removed com.sentry.monitor."
echo "If you set up sleepwatcher: brew services stop sleepwatcher; rm -f ~/.wakeup"
