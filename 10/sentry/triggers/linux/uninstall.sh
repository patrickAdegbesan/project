#!/usr/bin/env bash
# Remove Sentry triggers on Linux.
set -euo pipefail
systemctl --user disable sentry.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/sentry.service"
systemctl --user daemon-reload 2>/dev/null || true
sudo rm -f /usr/lib/systemd/system-sleep/sentry-resume
echo "Removed Sentry resume hook and user service."
