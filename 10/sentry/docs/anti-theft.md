# Do this first: real anti-theft (stronger than any monitor)

Sentry tells you *who* is using your machine. But if a laptop is **stolen**,
software sitting on top of the OS is the weak layer — a thief can reformat
the disk, pull the drive, or reinstall the OS, and any monitor is gone in
minutes. No amount of hiding changes that; the owner cannot out-hide
physical possession.

The strong layer lives **below** the OS, is built into your devices, and
**cannot be removed by someone who just powered the machine on**. Set these
up on all three machines; Sentry then complements them.

## 1. Full-disk encryption (this is the real protection)

Without your password the disk is unreadable, so a thief gets a brick and
your data stays private.

- **macOS:** System Settings → Privacy & Security → **FileVault** → On.
- **Windows:** Settings → Privacy & security → **Device encryption** /
  **BitLocker** → On (save the recovery key to your Microsoft account).
- **Fedora:** best done at install time (**LUKS** — "Encrypt my data" in
  the installer). Converting an existing install is involved; if it isn't
  encrypted, plan a reinstall with encryption on.

## 2. Find My / remote lock + wipe (the "control it and deny them" feature)

These are OS-level, survive login attempts, and let you locate, **lock**,
message, and **erase** the device remotely — the things you wanted a RAT
for, done at a layer a RAT can't reach.

- **macOS:** System Settings → your name → **Find My** → Find My Mac → On.
  Manage from iCloud.com/find or another Apple device.
- **Windows:** Settings → Privacy & security → **Find my device** → On.
  Manage from account.microsoft.com/devices.
- **Android phone:** Settings → Security → **Find My Device** → On
  (google.com/android/find).
- **iPhone:** Settings → your name → Find My → **Find My iPhone** → On.
- **Fedora:** no built-in equivalent. Use encryption + a BIOS/UEFI password,
  and optionally install **Prey** (open source) for locate/photo reports.

## 3. Firmware / BIOS / UEFI password

Stops a thief from booting a USB stick to reinstall around your encryption.

- **Mac (Apple silicon):** covered by FileVault + Activation Lock.
- **Mac (Intel):** recoveryOS → Utilities → **Firmware Password**.
- **Windows/Fedora laptop:** enter BIOS/UEFI at boot (F2/Del), set a
  **supervisor/admin password**, and disable boot from USB.

## 4. Prey (optional, open source) — photo + locate reports

Cross-platform, visible, legal. Adds "take a photo of whoever has it" and
location reports on top of the above. https://preyproject.com

---

With 1–3 in place, a stolen laptop is a locked, encrypted, unbootable,
locatable, remotely-wipeable brick — which beats a concealed monitor on
every count, and keeps you on the right side of the law.
