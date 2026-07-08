#!/usr/bin/env python3
"""
SentinelIQ — Terminal client.

Every function of the web dashboard, from the terminal. Commands drive
the same Flask application in-process (test client), so scoring, batch
runs, stats and retraining use the exact same model, code and database
as the website. Works fully offline.

  python cli.py predict --amount 4299 --hour 3 --v14 -9.7 --v17 -6.9
  python cli.py batch --n 500
  python cli.py transactions [--limit 20] [--verdict block]
  python cli.py stats
  python cli.py model
  python cli.py retrain [--n 40000]
  python cli.py interactive
"""

import argparse
import json
import sys

from app import app
from datagen import FEATURES

client = app.test_client()


def show(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def gauge(p, width=40):
    filled = int(round(p * width))
    return "[" + "#" * filled + "-" * (width - filled) + f"] {p*100:5.1f}%"


def cmd_predict(args):
    body = {f: getattr(args, f) for f in FEATURES}
    res = client.post("/api/predict", json=body)
    data = res.get_json()
    if res.status_code != 200:
        print("error:", data)
        return
    print(f"\nFraud probability {gauge(data['probability'])}")
    print(f"Verdict: {data['verdict'].upper()}  (threshold {data['threshold']})")
    print("Top factors:")
    for f in data["top_factors"]:
        sign = "+" if f["impact"] > 0 else ""
        print(f"  {f['feature']:<8} value {f['value']:>10}   impact {sign}{f['impact']}")


def cmd_batch(args):
    res = client.post("/api/batch", json={"n": args.n})
    data = res.get_json()
    print(f"Scored {data['scored']} transactions — {data['flagged']} flagged")
    print(f"\n{'id':>5}  {'amount':>10}  {'hour':>4}  {'p(fraud)':>8}  verdict  category")
    for r in data["rows"][-args.show:]:
        print(f"{r['id']:>5}  {r['amount']:>10.2f}  {r['hour']:>4}  "
              f"{r['probability']:>8.3f}  {r['verdict']:<7}  {r['category']}")


def cmd_transactions(args):
    q = f"/api/transactions?limit={args.limit}"
    if args.verdict:
        q += f"&verdict={args.verdict}"
    rows = client.get(q).get_json()["transactions"]
    print(f"{'id':>5}  {'amount':>10}  {'hour':>4}  {'p(fraud)':>8}  verdict  category")
    for r in rows:
        print(f"{r['id']:>5}  {r['amount']:>10.2f}  {r['hour']:>4}  "
              f"{r['probability']:>8.3f}  {r['verdict']:<7}  {r['category']}")


def cmd_stats(_args):
    data = client.get("/api/stats").get_json()
    print(f"Total transactions : {data['total_transactions']}")
    print(f"Flagged            : {data['flagged']}  ({data['flag_rate']}%)")
    print(f"Blocked amount     : ${data['blocked_amount']:,.2f}")
    if data["categories"]:
        print("Fraud by category  :")
        for c in data["categories"]:
            print(f"  {c['category']:<15} {c['c']}")
    hours = data["hourly_fraud"]
    if any(hours):
        peak = max(hours)
        print("Fraud by hour      :")
        for h, v in enumerate(hours):
            bar = "#" * int(v / peak * 30) if peak else ""
            print(f"  {h:02d}:00 {bar} {v}")


def cmd_model(_args):
    show(client.get("/api/model").get_json())


def cmd_retrain(args):
    print("Retraining model (this regenerates model/model.pkl)…")
    m = client.post("/api/retrain", json={"n": args.n}).get_json()
    print(f"accuracy {m['accuracy']}%  precision {m['precision']}%  "
          f"recall {m['recall']}%  f1 {m['f1']}%  ROC AUC {m['roc_auc']}")


def interactive(_args):
    while True:
        print("\n===== SentinelIQ =====")
        print("  1. Score a transaction")
        print("  2. Batch simulation")
        print("  3. Recent transactions")
        print("  4. Dashboard stats")
        print("  5. Model metrics")
        print("  6. Retrain model")
        print("  0. Exit")
        choice = input("> ").strip()
        if choice == "0":
            return
        try:
            if choice == "1":
                vals = {}
                for f in FEATURES:
                    raw = input(f"  {f} [0]: ").strip()
                    vals[f] = float(raw) if raw else 0.0
                cmd_predict(argparse.Namespace(**vals))
            elif choice == "2":
                n = int(input("  how many transactions [200]: ") or 200)
                cmd_batch(argparse.Namespace(n=n, show=15))
            elif choice == "3":
                cmd_transactions(argparse.Namespace(limit=20, verdict=None))
            elif choice == "4":
                cmd_stats(None)
            elif choice == "5":
                cmd_model(None)
            elif choice == "6":
                cmd_retrain(argparse.Namespace(n=40000))
            else:
                print("Invalid choice.")
        except (KeyboardInterrupt, EOFError):
            print("\n(cancelled)")
        except Exception as exc:
            print(f"Error: {exc}")


def main():
    p = argparse.ArgumentParser(description="SentinelIQ terminal client")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("predict")
    for f in FEATURES:
        sp.add_argument(f"--{f}", type=float, default=0.0)
    sp.set_defaults(fn=cmd_predict)

    sp = sub.add_parser("batch")
    sp.add_argument("--n", type=int, default=200)
    sp.add_argument("--show", type=int, default=15)
    sp.set_defaults(fn=cmd_batch)

    sp = sub.add_parser("transactions")
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--verdict", choices=["approve", "review", "block"])
    sp.set_defaults(fn=cmd_transactions)

    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    sub.add_parser("model").set_defaults(fn=cmd_model)

    sp = sub.add_parser("retrain")
    sp.add_argument("--n", type=int, default=40000)
    sp.set_defaults(fn=cmd_retrain)

    sub.add_parser("interactive").set_defaults(fn=interactive)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
