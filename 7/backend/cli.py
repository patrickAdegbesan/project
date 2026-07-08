#!/usr/bin/env python3
"""
Study Planner — Terminal client.

The full functionality of the website, from the terminal: register,
login, tasks, study schedule, progress logs, goals, analytics dashboard,
AI recommendations, search, and the admin panel. It drives the same
Flask application in-process (test client), so everything goes through
the same routes, validation and database as the website. Fully offline.

Usage:  python cli.py          (from the backend/ directory)
"""

import getpass
import json
import sys

from app import create_app

app = create_app()


class Session:
    def __init__(self):
        self.http = app.test_client()
        self.token = None
        self.user = None

    def call(self, method, path, body=None):
        headers = {"X-Auth-Token": self.token} if self.token else {}
        fn = getattr(self.http, method)
        res = fn(path, json=body, headers=headers) if body is not None \
            else fn(path, headers=headers)
        return res.status_code, (res.get_json() or {})


def show(data):
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def unwrap(data):
    return data.get("data", data)


# ── Auth ─────────────────────────────────────────────────────────────────────

def login_flow(s):
    while True:
        print("\n===== Study Planner =====\n  1. Login\n  2. Register\n  0. Exit")
        choice = input("> ").strip()
        if choice == "0":
            return False
        if choice == "2":
            body = {
                "username": input("Username: ").strip(),
                "email":    input("Email: ").strip(),
                "name":     input("Full name: ").strip(),
                "password": getpass.getpass("Password: "),
            }
            code, data = s.call("post", "/api/auth/register", body)
        else:
            body = {
                "email":    input("Email: ").strip(),
                "password": getpass.getpass("Password: "),
            }
            code, data = s.call("post", "/api/auth/login", body)
        payload = unwrap(data)
        if code < 300 and payload.get("token"):
            s.token = payload["token"]
            s.user = payload.get("user", {})
            print(f"Welcome, {s.user.get('username', 'user')}!")
            return True
        print("Failed:", data.get("error", data))


# ── Tasks ────────────────────────────────────────────────────────────────────

def list_tasks(s):
    _, data = s.call("get", "/api/tasks")
    tasks = unwrap(data).get("tasks", [])
    print(f"\nTasks ({len(tasks)}):")
    for t in tasks:
        mark = "x" if t.get("status") == "completed" else " "
        print(f"  [{mark}] #{t['id']:<4} ({t.get('priority','?'):<6}) "
              f"{t['title']}  — due {t.get('due_date') or 'n/a'}, "
              f"{t.get('subject','')}")


def add_task(s):
    body = {
        "title":             input("Title: ").strip(),
        "subject":           input("Subject: ").strip(),
        "due_date":          input("Due date (YYYY-MM-DD): ").strip(),
        "priority":          input("Priority (low/medium/high) [medium]: ").strip() or "medium",
        "estimated_minutes": int(input("Estimated minutes [60]: ") or 60),
        "description":       input("Description: ").strip(),
    }
    code, data = s.call("post", "/api/tasks", body)
    show(unwrap(data))


def update_task_status(s):
    tid = input("Task id: ").strip()
    status = input("New status (pending/in_progress/completed): ").strip()
    _, data = s.call("put", f"/api/tasks/{tid}", {"status": status})
    show(unwrap(data))


def delete_task(s):
    tid = input("Task id: ").strip()
    _, data = s.call("delete", f"/api/tasks/{tid}")
    show(data)


def search_tasks(s):
    q = input("Search query: ").strip()
    _, data = s.call("get", f"/api/tasks?search={q}")
    tasks = unwrap(data).get("tasks", [])
    print(f"\nMatches ({len(tasks)}):")
    for t in tasks:
        print(f"  #{t['id']:<4} {t['title']}  ({t.get('subject','')})")


# ── Schedule / progress / goals ──────────────────────────────────────────────

def show_schedule(s, today=False):
    path = "/api/schedule/today" if today else "/api/schedule"
    _, data = s.call("get", path)
    blocks = unwrap(data).get("blocks", unwrap(data).get("schedule", []))
    print(f"\nSchedule ({len(blocks)} block(s)):")
    for b in blocks:
        print(f"  #{b.get('id'):<4} {b.get('day_of_week', b.get('date',''))} "
              f"{b.get('start_time','')}-{b.get('end_time','')}  "
              f"{b.get('subject','')} — {b.get('activity', b.get('title',''))}")


def add_schedule_block(s):
    body = {
        "day_of_week": input("Day of week (0=Mon .. 6=Sun): ").strip(),
        "start_time":  input("Start (HH:MM): ").strip(),
        "end_time":    input("End (HH:MM): ").strip(),
        "subject":     input("Subject: ").strip(),
        "activity":    input("Activity: ").strip(),
    }
    _, data = s.call("post", "/api/schedule", body)
    show(unwrap(data))


def log_progress(s):
    body = {
        "task_id":       int(input("Task id (0 = none): ") or 0) or None,
        "subject":       input("Subject: ").strip(),
        "minutes":       int(input("Minutes studied: ") or 0),
        "focus_rating":  int(input("Focus rating 1-5 [3]: ") or 3),
        "notes":         input("Notes: ").strip(),
    }
    _, data = s.call("post", "/api/progress/log", body)
    show(unwrap(data))


def progress_logs(s):
    _, data = s.call("get", "/api/progress/logs")
    logs = unwrap(data).get("logs", [])
    print(f"\nProgress logs ({len(logs)}):")
    for l in logs[:15]:
        print(f"  {l.get('logged_at', l.get('date',''))}: "
              f"{l.get('minutes','?')} min {l.get('subject','')} "
              f"(focus {l.get('focus_rating','?')}/5)")


def goals(s):
    _, data = s.call("get", "/api/goals")
    gs = unwrap(data).get("goals", [])
    print(f"\nGoals ({len(gs)}):")
    for g in gs:
        print(f"  #{g.get('id'):<4} {g.get('title','')} — target "
              f"{g.get('target_minutes', g.get('target',''))} "
              f"({g.get('period','')}) {'done' if g.get('achieved') else ''}")


def add_goal(s):
    body = {
        "title":          input("Title: ").strip(),
        "subject":        input("Subject: ").strip(),
        "target_minutes": int(input("Target minutes: ") or 0),
        "period":         input("Period (daily/weekly) [weekly]: ").strip() or "weekly",
    }
    _, data = s.call("post", "/api/goals", body)
    show(unwrap(data))


# ── Analytics / AI ───────────────────────────────────────────────────────────

def dashboard(s):
    _, data = s.call("get", "/api/analytics/dashboard")
    show(unwrap(data))


def recommendations(s):
    _, data = s.call("get", "/api/analytics/recommendations")
    payload = unwrap(data)
    recs = payload.get("recommendations", payload)
    if isinstance(recs, list):
        print("\nAI recommendations:")
        for r in recs:
            if isinstance(r, dict):
                print(f"  - {r.get('message', r.get('text', r))}")
            else:
                print(f"  - {r}")
    else:
        show(recs)


# ── Admin ────────────────────────────────────────────────────────────────────

def admin_stats(s):
    _, data = s.call("get", "/api/admin/stats")
    show(unwrap(data))


def admin_users(s):
    _, data = s.call("get", "/api/admin/users")
    users = unwrap(data).get("users", [])
    for u in users:
        print(f"  #{u.get('id'):<4} {u.get('username','')} <{u.get('email','')}> "
              f"{'[admin]' if u.get('is_admin') else ''}")


def admin_activity(s):
    _, data = s.call("get", "/api/admin/activity")
    show(unwrap(data))


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    s = Session()
    if not login_flow(s):
        return
    actions = [
        ("Tasks",                 lambda: list_tasks(s)),
        ("Add task",              lambda: add_task(s)),
        ("Update task status",    lambda: update_task_status(s)),
        ("Delete task",           lambda: delete_task(s)),
        ("Search tasks",          lambda: search_tasks(s)),
        ("Full schedule",         lambda: show_schedule(s)),
        ("Today's schedule",      lambda: show_schedule(s, today=True)),
        ("Add schedule block",    lambda: add_schedule_block(s)),
        ("Log study progress",    lambda: log_progress(s)),
        ("Progress history",      lambda: progress_logs(s)),
        ("Goals",                 lambda: goals(s)),
        ("Add goal",              lambda: add_goal(s)),
        ("Analytics dashboard",   lambda: dashboard(s)),
        ("AI recommendations",    lambda: recommendations(s)),
        ("[admin] Stats",         lambda: admin_stats(s)),
        ("[admin] Users",         lambda: admin_users(s)),
        ("[admin] Activity log",  lambda: admin_activity(s)),
    ]
    while True:
        print(f"\n===== Study Planner — {s.user.get('username','')} =====")
        for i, (label, _) in enumerate(actions, 1):
            print(f"  {i:>2}. {label}")
        print("   0. Exit")
        choice = input("> ").strip()
        if choice == "0":
            break
        try:
            actions[int(choice) - 1][1]()
        except (ValueError, IndexError):
            print("Invalid choice.")
        except (KeyboardInterrupt, EOFError):
            print("\n(cancelled)")
        except Exception as exc:
            print(f"Error: {exc}")
    print("Bye.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye.")
        sys.exit(0)
