# Sentry — openly-running intruder monitor

Sentry watches **your own** computer and, whenever the machine wakes up or a
session logs in, it quietly records *who is there*:

- a **webcam photo** of whoever is at the keyboard,
- a **screenshot** of what is on screen,
- a **timestamped log line**,

then **delivers the evidence to you** by email (or saves it to a synced
folder such as Google Drive / iCloud / Dropbox).

It runs on **macOS**, **Windows**, and **Linux (tested on Fedora)** from one
shared Python core, with a small per-OS trigger that fires it on wake/login.

## What Sentry deliberately is NOT

Sentry is **not** a RAT and **not** malware. It makes a point of the
opposite:

- **It does not hide.** It shows up in Activity Monitor / Task Manager /
  `systemctl`, it lives in a plainly-named folder, and you can stop and
  remove it at any time. "Quiet" here means *no pop-ups and no stolen
  window focus* — not *invisible to the operator*.
- **It does not evade antivirus.** Because it is your own software on your
  own machine, you **allow** it in your antivirus (instructions below)
  instead of trying to sneak past it. A stolen machine can't do that — only
  the owner can — which is exactly why this approach is legal and a
  concealed one is not.
- **It does not persist against its owner.** You installed it, you can
  uninstall it. There are no anti-removal tricks.

If what you actually fear is **theft**, software on top of the OS is the
weak layer — a thief reformats the disk and it's gone. The strong layer is
built into your devices; set it up first (see `docs/anti-theft.md`):
full-disk encryption + Find My / Find My Device + a firmware password.
Sentry complements that; it does not replace it.

## Layout

```
sentry/
  capture.py              # cross-platform core: capture + deliver
  config.example.ini      # copy to config.ini and fill in
  requirements.txt
  triggers/
    macos/                # LaunchAgent that fires capture.py on wake/login
    windows/              # Scheduled Task that fires it on wake/logon
    linux/                # systemd sleep-hook + user login service
  docs/
    anti-theft.md         # encryption + Find My setup (do this first)
    antivirus-allow.md    # how to whitelist Sentry in your own AV
```

## Quick start (all platforms)

1. Install Python 3.9+ and the dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy the config and fill it in:
   ```
   cp config.example.ini config.ini
   ```
   Set where evidence goes (an email via Gmail app password, and/or a local
   folder your cloud drive syncs).
3. Test it by hand — this captures one snapshot right now:
   ```
   python capture.py --once
   ```
   Check that a photo + screenshot arrived where you configured.
4. Install the trigger for your OS (see the matching folder under
   `triggers/`). After that, Sentry fires automatically on every wake/login.

See `docs/antivirus-allow.md` if your antivirus quarantines it — you
**allow** it there; you do not hide from it.

## Legal note

Only run Sentry on devices **you own and control**. Recording people is
regulated differently from place to place; a monitor on your own laptop that
reports to you is normal, but putting capture software on a device that
isn't yours — or that others use without knowing — can be illegal. Keep it
to your own machines.
