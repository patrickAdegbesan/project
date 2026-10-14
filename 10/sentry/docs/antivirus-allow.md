# Allowing Sentry in your own antivirus

Your antivirus may flag Sentry, because "grab the webcam + screen and email
it" is exactly the behaviour antivirus watches for. That is working as
intended. Because this is **your** software on **your** machine, the correct
move is to **allow** it — openly — not to evade detection.

This is the whole difference between a tool and malware: a thief on a stolen
machine can't add an antivirus exclusion, but you, the owner, can. The
ownership is what makes it both effective and legal.

## Windows (Microsoft Defender)

1. Start → **Windows Security** → **Virus & threat protection**.
2. Under *Virus & threat protection settings*, click **Manage settings**.
3. Scroll to **Exclusions** → **Add or remove exclusions** → **Add an
   exclusion** → **Folder**.
4. Choose the `sentry` folder.
5. Also allow camera access: Settings → Privacy & security → **Camera** → on,
   and allow desktop apps.

Third-party AV (Norton, Kaspersky, etc.) has the same idea under
"Exclusions", "Allowed apps", or "Whitelist".

## macOS

macOS doesn't "quarantine" it like AV, but it gates the sensitive bits
behind permission prompts. Approve them:

1. System Settings → **Privacy & Security** → **Camera** → enable for the
   process (Terminal/python, or Sentry if you package it).
2. System Settings → **Privacy & Security** → **Screen Recording** → enable
   it, then log out/in so it takes effect.
3. If Gatekeeper blocks a script, right-click → Open once to approve it.

## Linux (Fedora)

Fedora ships no always-on AV by default. The gates are permissions:

- Camera: your user must be in the **video** group — `groups | grep video`;
  if missing, `sudo usermod -aG video $USER` then re-login.
- Screenshot: works for the logged-in user's GNOME session. Background
  capture on a locked Wayland screen is restricted by design; if screenshots
  come out blank set `screenshot = false` in `config.ini`.

## If you use ClamAV or similar and it keeps flagging capture.py

Add the sentry folder to its exclude path (e.g. `clamd.conf`
`ExcludePath`), or sign/allow your own file. Do **not** try to obfuscate the
script to slip past the scanner — that turns a legitimate tool into malware
and is the one thing this project refuses to do.
