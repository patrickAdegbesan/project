#!/usr/bin/env python3
"""Sentry — capture who is at the keyboard and deliver the evidence.

This is the cross-platform core. It is meant to be fired by a per-OS trigger
(see triggers/) on wake/login, or run by hand with --once to test.

It runs openly: no hiding from the operator, no antivirus evasion. On your
own machine you *allow* it in your antivirus (see docs/antivirus-allow.md).
"""

from __future__ import annotations

import argparse
import configparser
import datetime as dt
import os
import smtplib
import socket
import sys
from email.message import EmailMessage
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_config(path: Path) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    if not path.exists():
        sys.exit(
            f"No config found at {path}. Copy config.example.ini to "
            f"config.ini and edit it."
        )
    cfg.read(path)
    return cfg


def resolve_dir(base: Path, value: str) -> Path:
    """Resolve a config path relative to the sentry folder, then mkdir -p."""
    p = Path(os.path.expanduser(value))
    if not p.is_absolute():
        p = (base / p).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def take_screenshot(dest: Path) -> Path | None:
    """Save a screenshot of all monitors. Returns the path, or None."""
    try:
        import mss
        import mss.tools
    except ImportError:
        print("mss not installed; skipping screenshot", file=sys.stderr)
        return None
    try:
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])  # [0] = all monitors combined
            mss.tools.to_png(shot.rgb, shot.size, output=str(dest))
        return dest
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"screenshot failed: {exc}", file=sys.stderr)
        return None


def take_webcam(dest: Path, index: int, warmup: int) -> Path | None:
    """Grab one frame from the default camera. Returns the path, or None."""
    try:
        import cv2
    except ImportError:
        print("opencv not installed; skipping webcam", file=sys.stderr)
        return None
    cam = cv2.VideoCapture(index)
    if not cam.isOpened():
        print(f"camera {index} would not open", file=sys.stderr)
        return None
    try:
        frame = None
        # Some cameras hand back a dark first frame; discard a few.
        for _ in range(max(1, warmup)):
            ok, frame = cam.read()
        if not ok or frame is None:
            print("camera returned no frame", file=sys.stderr)
            return None
        cv2.imwrite(str(dest), frame)
        return dest
    finally:
        cam.release()


def append_log(log_path: Path, stamp: str, shots: list[Path]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    user = os.environ.get("USER") or os.environ.get("USERNAME") or "?"
    names = ", ".join(p.name for p in shots) or "(no media captured)"
    line = f"{stamp}\thost={socket.gethostname()}\tuser={user}\t{names}\n"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def send_email(cfg: configparser.ConfigParser, stamp: str,
               attachments: list[Path]) -> None:
    sec = cfg["email"]
    msg = EmailMessage()
    msg["Subject"] = f"[Sentry] activity on {socket.gethostname()} @ {stamp}"
    msg["From"] = sec.get("from_addr")
    msg["To"] = sec.get("to_addr")
    msg.set_content(
        f"Sentry recorded activity on {socket.gethostname()} at {stamp}.\n"
        f"User session: {os.environ.get('USER') or os.environ.get('USERNAME')}\n"
        f"{len(attachments)} file(s) attached."
    )
    for path in attachments:
        data = path.read_bytes()
        subtype = "png" if path.suffix.lower() == ".png" else "jpeg"
        msg.add_attachment(data, maintype="image", subtype=subtype,
                           filename=path.name)
    with smtplib.SMTP(sec.get("smtp_host"), sec.getint("smtp_port")) as s:
        s.starttls()
        s.login(sec.get("username"), sec.get("app_password"))
        s.send_message(msg)


def capture(cfg: configparser.ConfigParser) -> int:
    cap = cfg["capture"]
    out = resolve_dir(HERE, cap.get("output_dir", "./evidence"))
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    shots: list[Path] = []
    if cap.getboolean("screenshot", fallback=True):
        s = take_screenshot(out / f"{stamp}_screen.png")
        if s:
            shots.append(s)
    if cap.getboolean("webcam", fallback=True):
        w = take_webcam(
            out / f"{stamp}_cam.jpg",
            cap.getint("camera_index", fallback=0),
            cap.getint("warmup_frames", fallback=5),
        )
        if w:
            shots.append(w)

    log_file = resolve_dir(HERE, str(Path(cfg["log"].get(
        "file", "./evidence/sentry.log")).parent)) / Path(
        cfg["log"].get("file", "./evidence/sentry.log")).name
    append_log(log_file, stamp, shots)

    if cfg.has_section("email") and cfg["email"].getboolean(
            "enabled", fallback=False) and shots:
        try:
            send_email(cfg, stamp, shots)
            print("evidence emailed")
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"email failed (evidence still saved locally): {exc}",
                  file=sys.stderr)

    print(f"captured {len(shots)} file(s) into {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sentry capture core")
    ap.add_argument("--config", default=str(HERE / "config.ini"),
                    help="path to config.ini")
    ap.add_argument("--once", action="store_true",
                    help="capture a single snapshot now and exit")
    args = ap.parse_args(argv)

    cfg = load_config(Path(args.config))
    # --once and the trigger path both do exactly one capture; the flag just
    # makes the intent explicit when testing by hand.
    return capture(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
