#!/usr/bin/env python3
"""
PhishGuard AI — Terminal client.

Every function of the web dashboard, from the terminal. The commands run
the same FastAPI application in-process (via TestClient), so analysis,
history, feedback and admin stats go through the exact same code and
database as the website. Works fully offline.

Usage (run from the backend/ directory):

  python cli.py analyze <url> [url ...]     Analyze one or more URLs
  python cli.py history [--limit N] [--classification phishing|legitimate]
  python cli.py feedback <url_id> <correct|incorrect> [--comment TEXT]
  python cli.py review-queue                Unreviewed feedback (admin)
  python cli.py review <feedback_id>        Mark feedback reviewed (admin)
  python cli.py stats                       Dashboard statistics (admin)
  python cli.py model                       Model metrics (admin)
  python cli.py interactive                 Menu-driven session
"""

import argparse
import json
import sys

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def show(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def print_verdict(r):
    flag = "PHISHING " if r["classification"] == "phishing" else "LEGITIMATE"
    print(f"\n[{flag}]  {r['url']}")
    print(f"  risk score : {r['risk_score']}/100   confidence: {r['confidence']}%")
    tops = r.get("top_factors") or []
    if tops:
        print("  top factors:")
        for t in tops[:5]:
            if isinstance(t, dict):
                print(f"    - {t.get('feature', t)}: {t.get('impact', '')}")
            else:
                print(f"    - {t}")


def cmd_analyze(args):
    for url in args.urls:
        res = client.post("/api/analyze", json={"url": url})
        if res.status_code != 200:
            print(f"error for {url}: {res.json()}")
            continue
        print_verdict(res.json())


def cmd_history(args):
    params = {"limit": args.limit}
    if args.classification:
        params["classification"] = args.classification
    res = client.get("/api/history", params=params)
    data = res.json()
    rows = data if isinstance(data, list) else data.get("items", data.get("history", []))
    print(f"\n{'id':>4}  {'class':<11} {'risk':>4}  url")
    for row in rows:
        print(f"{row.get('id',''):>4}  {row.get('classification',''):<11} "
              f"{row.get('risk_score',''):>4}  {row.get('url','')[:70]}")


def cmd_feedback(args):
    body = {"url_id": args.url_id,
            "verdict_was": args.verdict,
            "comment": args.comment or ""}
    res = client.post("/api/feedback", json=body)
    show(res.json())


def cmd_review_queue(_args):
    res = client.get("/api/feedback", params={"reviewed": "false"})
    show(res.json())


def cmd_review(args):
    res = client.put(f"/api/feedback/{args.feedback_id}/review")
    show(res.json())


def cmd_stats(_args):
    show(client.get("/api/admin/stats").json())


def cmd_model(_args):
    show(client.get("/api/admin/model-metrics").json())


def interactive(_args):
    actions = {
        "1": ("Analyze a URL", lambda: cmd_analyze(
            argparse.Namespace(urls=[input("URL: ").strip()]))),
        "2": ("History", lambda: cmd_history(
            argparse.Namespace(limit=20, classification=None))),
        "3": ("Submit feedback", lambda: cmd_feedback(argparse.Namespace(
            url_id=int(input("URL id: ")),
            verdict=input("Was the verdict correct or incorrect? "),
            comment=input("Comment (optional): ")))),
        "4": ("Review queue (admin)", lambda: cmd_review_queue(None)),
        "5": ("Mark feedback reviewed (admin)", lambda: cmd_review(
            argparse.Namespace(feedback_id=int(input("Feedback id: "))))),
        "6": ("Dashboard stats (admin)", lambda: cmd_stats(None)),
        "7": ("Model metrics (admin)", lambda: cmd_model(None)),
    }
    while True:
        print("\n===== PhishGuard AI =====")
        for key, (label, _) in actions.items():
            print(f"  {key}. {label}")
        print("  0. Exit")
        choice = input("> ").strip()
        if choice == "0":
            return
        entry = actions.get(choice)
        if not entry:
            print("Invalid choice.")
            continue
        try:
            entry[1]()
        except (KeyboardInterrupt, EOFError):
            print("\n(cancelled)")
        except Exception as exc:
            print(f"Error: {exc}")


def main():
    p = argparse.ArgumentParser(description="PhishGuard AI terminal client")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("analyze");        sp.add_argument("urls", nargs="+"); sp.set_defaults(fn=cmd_analyze)
    sp = sub.add_parser("history");        sp.add_argument("--limit", type=int, default=20); sp.add_argument("--classification"); sp.set_defaults(fn=cmd_history)
    sp = sub.add_parser("feedback");       sp.add_argument("url_id", type=int); sp.add_argument("verdict", choices=["correct", "incorrect"]); sp.add_argument("--comment"); sp.set_defaults(fn=cmd_feedback)
    sp = sub.add_parser("review-queue");   sp.set_defaults(fn=cmd_review_queue)
    sp = sub.add_parser("review");         sp.add_argument("feedback_id", type=int); sp.set_defaults(fn=cmd_review)
    sp = sub.add_parser("stats");          sp.set_defaults(fn=cmd_stats)
    sp = sub.add_parser("model");          sp.set_defaults(fn=cmd_model)
    sp = sub.add_parser("interactive");    sp.set_defaults(fn=interactive)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
