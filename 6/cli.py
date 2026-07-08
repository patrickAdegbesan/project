#!/usr/bin/env python3
"""
Lush Hair NG Resume Screener — Terminal client.

Every function of the web app, from the terminal: upload resumes for
screening, watch job progress, view ranked results, shortlist
candidates, inspect candidate breakdowns, manage job roles, export to
Excel and view dashboard stats. Commands drive the same FastAPI
application in-process (TestClient), so screening uses the exact same
NLP/scoring pipeline and database as the website. Works fully offline
(geocoding falls back to the built-in Lagos location dictionary).

  python cli.py roles
  python cli.py upload <role_id> <file.pdf> [more files...]
  python cli.py status <job_id>
  python cli.py results <job_id>
  python cli.py candidate <candidate_id>
  python cli.py shortlist <score_id ...> [--off]
  python cli.py export <job_id> [-o results.xlsx]
  python cli.py stats
  python cli.py interactive
"""

import argparse
import json
import os
import sys
import time

os.environ.setdefault("DEBUG", "false")   # keep SQL echo out of CLI output

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def show(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_roles(_args):
    roles = client.get("/api/job-roles").json()
    for r in roles:
        print(f"\n#{r['id']}  {r['title']}  (min {r['min_experience']} yrs, "
              f"hub {r['hub_lat']},{r['hub_long']})")
        print(f"    skills: {', '.join(r['required_skills'])}")


def cmd_upload(args):
    files = []
    for path in args.files:
        if not os.path.exists(path):
            print(f"file not found: {path}")
            return
        files.append(("files", (os.path.basename(path), open(path, "rb"))))
    res = client.post("/api/upload", data={"job_role_id": str(args.role_id)},
                      files=files)
    data = res.json()
    if res.status_code != 200:
        print("error:", data)
        return
    job_id = data.get("job_id")
    print(f"Upload accepted — job #{job_id} ({len(args.files)} file(s)). Processing…")
    while True:
        st = client.get(f"/api/status/{job_id}").json()
        state = st.get("status")
        print(f"  status: {state}  ({st.get('processed', '?')}/{st.get('total', '?')})")
        if state in ("completed", "failed", "error"):
            break
        time.sleep(1)
    if state == "completed":
        cmd_results(argparse.Namespace(job_id=job_id))


def cmd_status(args):
    show(client.get(f"/api/status/{args.job_id}").json())


def cmd_results(args):
    data = client.get(f"/api/results/{args.job_id}").json()
    cands = data.get("results", [])
    if not cands:
        print("no results:", data)
        return
    print(f"\nJob #{data.get('job_id')} — {data.get('job_role','')} "
          f"({data.get('total_candidates', len(cands))} candidates)")
    print(f"{'rank':>4}  {'cand':>4}  {'total':>6}  {'skill':>6}  {'exp':>6}  "
          f"{'prox':>6}  {'dist km':>7}  {'short':<5}  name")
    for c in cands:
        print(f"{c['rank']:>4}  {c['candidate_id']:>4}  {c['total_score']:>6}  "
              f"{c['skill_score']:>6}  {c['exp_score']:>6}  {c['proximity_score']:>6}  "
              f"{c['distance_km']:>7}  {'yes' if c.get('shortlisted') else 'no':<5}  "
              f"{c.get('name','?')}")
        if c.get("skill_gap_summary"):
            print(f"      {c['skill_gap_summary']}")


def cmd_candidate(args):
    show(client.get(f"/api/candidate/{args.candidate_id}").json())


def cmd_shortlist(args):
    res = client.post("/api/shortlist", json={
        "score_ids": args.score_ids,
        "shortlisted": not args.off,
    })
    show(res.json())


def cmd_export(args):
    res = client.get(f"/api/export/{args.job_id}")
    if res.status_code != 200:
        print("error:", res.text[:300])
        return
    out = args.output or f"job_{args.job_id}_results.xlsx"
    with open(out, "wb") as f:
        f.write(res.content)
    print(f"saved {out} ({len(res.content)} bytes)")


def cmd_stats(_args):
    show(client.get("/api/dashboard/stats").json())


def interactive(_args):
    actions = {
        "1": ("Job roles",            lambda: cmd_roles(None)),
        "2": ("Upload resumes",       lambda: cmd_upload(argparse.Namespace(
            role_id=int(input("Role id: ")),
            files=input("File path(s), space-separated: ").split()))),
        "3": ("Job status",           lambda: cmd_status(argparse.Namespace(
            job_id=int(input("Job id: "))))),
        "4": ("Results",              lambda: cmd_results(argparse.Namespace(
            job_id=int(input("Job id: "))))),
        "5": ("Candidate detail",     lambda: cmd_candidate(argparse.Namespace(
            candidate_id=int(input("Candidate id: "))))),
        "6": ("Toggle shortlist",     lambda: cmd_shortlist(argparse.Namespace(
            score_ids=[int(x) for x in input("Score id(s), space-separated: ").split()],
            off=input("Remove from shortlist? [y/N] ").lower() == "y"))),
        "7": ("Export to Excel",      lambda: cmd_export(argparse.Namespace(
            job_id=int(input("Job id: ")), output=None))),
        "8": ("Dashboard stats",      lambda: cmd_stats(None)),
    }
    while True:
        print("\n===== Lush Hair NG Resume Screener =====")
        for k, (label, _) in actions.items():
            print(f"  {k}. {label}")
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
    p = argparse.ArgumentParser(description="Lush Hair NG terminal client")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("roles").set_defaults(fn=cmd_roles)

    sp = sub.add_parser("upload")
    sp.add_argument("role_id", type=int)
    sp.add_argument("files", nargs="+")
    sp.set_defaults(fn=cmd_upload)

    sp = sub.add_parser("status"); sp.add_argument("job_id", type=int); sp.set_defaults(fn=cmd_status)
    sp = sub.add_parser("results"); sp.add_argument("job_id", type=int); sp.set_defaults(fn=cmd_results)
    sp = sub.add_parser("candidate"); sp.add_argument("candidate_id", type=int); sp.set_defaults(fn=cmd_candidate)

    sp = sub.add_parser("shortlist")
    sp.add_argument("score_ids", type=int, nargs="+",
                    help="score_id values from the results view")
    sp.add_argument("--off", action="store_true", help="remove from shortlist")
    sp.set_defaults(fn=cmd_shortlist)

    sp = sub.add_parser("export")
    sp.add_argument("job_id", type=int)
    sp.add_argument("-o", "--output")
    sp.set_defaults(fn=cmd_export)

    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    sub.add_parser("interactive").set_defaults(fn=interactive)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
