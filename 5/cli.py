#!/usr/bin/env python3
"""
TaskMind — Terminal client.

The full functionality of the website, from the terminal: register,
login, natural-language task entry, AI priority scoring, task list,
complete/edit/delete/reschedule, and the "do next" recommendation.
It drives the same Flask application in-process (test client + app
context), so everything goes through the same code and database as the
website. Works fully offline.

Usage:  python cli.py
"""

import getpass
import sys

from app import app, Task, current_user, get_do_next, task_to_dict


class Session:
    def __init__(self):
        self.http = app.test_client()
        self.username = None


def show_task(t):
    mark = "x" if t.get("completed") else " "
    due = t.get("due_date") or "no due date"
    print(f"  [{mark}] #{t['id']:<4} ({t.get('priority_label','?'):<6} "
          f"{t.get('priority_pct', 0):>3}%) {t['title']}  — due {due}, "
          f"~{t.get('effort_minutes', '?')} min")


def login_flow(s):
    while True:
        print("\n===== TaskMind =====\n  1. Login\n  2. Register\n  0. Exit")
        choice = input("> ").strip()
        if choice == "0":
            return False
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        if choice == "2":
            email = input("Email: ").strip()
            res = s.http.post("/register", data={
                "username": username, "email": email, "password": password})
            if res.status_code not in (200, 302):
                print("Registration failed.")
                continue
        res = s.http.post("/login", data={"username": username, "password": password},
                          follow_redirects=False)
        if res.status_code == 302 and "/login" not in (res.headers.get("Location") or ""):
            s.username = username
            print(f"Welcome, {username}!")
            return True
        print("Login failed — check username/password.")


def with_user(s, fn):
    """Run fn(user) inside an app context bound to the CLI session's user."""
    with app.app_context():
        from app import User
        user = User.query.filter_by(username=s.username).first()
        return fn(user)


def list_tasks(s, include_done=True):
    def go(user):
        q = Task.query.filter_by(user_id=user.id).order_by(
            Task.priority_score.desc())
        tasks = [task_to_dict(t) for t in q.all()]
        return tasks
    tasks = with_user(s, go)
    if not include_done:
        tasks = [t for t in tasks if not t.get("completed")]
    print(f"\nTasks ({len(tasks)}):")
    for t in tasks:
        show_task(t)
    return tasks


def add_task_nlp(s):
    text = input("\nDescribe the task in plain English:\n> ").strip()
    if not text:
        return
    res = s.http.post("/api/parse", json={"text": text})
    parsed = res.get_json()
    print("\nAI parsed:")
    for k in ("title", "due_date", "due_time", "importance",
              "effort_minutes", "priority_label", "priority_pct"):
        print(f"  {k:<15}: {parsed.get(k)}")
    if input("Create this task? [Y/n] ").strip().lower() in ("", "y", "yes"):
        res = s.http.post("/api/tasks", json=parsed)
        data = res.get_json()
        if data and data.get("success"):
            print("Created:")
            show_task(data["task"])
        else:
            print("Failed:", data)


def add_task_manual(s):
    body = {
        "title": input("Title: ").strip(),
        "description": input("Description: ").strip(),
        "due_date": input("Due date (YYYY-MM-DD, blank = none): ").strip(),
        "due_time": input("Due time (HH:MM, blank = none): ").strip(),
        "importance": int(input("Importance 1-3 [2]: ") or 2),
        "effort_minutes": int(input("Effort minutes [30]: ") or 30),
    }
    res = s.http.post("/api/tasks", json=body)
    data = res.get_json()
    if data and data.get("success"):
        print("Created:")
        show_task(data["task"])
    else:
        print("Failed:", data)


def complete_task(s):
    tid = input("Task id: ").strip()
    mark_done = input("Mark as (d)one or (r)eopen? [d] ").strip().lower() != "r"
    res = s.http.put(f"/api/tasks/{tid}", json={"completed": mark_done})
    data = res.get_json() or {}
    if data.get("success"):
        show_task(data["task"])
    else:
        print(f"Failed: {data}")


def delete_task(s):
    tid = input("Task id to delete: ").strip()
    res = s.http.delete(f"/api/tasks/{tid}")
    data = res.get_json() or {}
    print("Deleted." if data.get("success") else f"Failed: {data}")


def reschedule_task(s):
    tid = input("Task id to reschedule: ").strip()
    new_date = input("New due date (YYYY-MM-DD): ").strip()
    res = s.http.post(f"/api/tasks/{tid}/reschedule", json={"due_date": new_date})
    data = res.get_json() or {}
    print(data if data else "No response.")


def do_next(s):
    def go(user):
        return get_do_next(user.id)
    result = with_user(s, go)
    if not result:
        print("\nNo pending tasks — nothing to recommend.")
        return
    task, pct = result
    print("\nAI recommends you work on this next "
          f"(confidence {int(pct * 100)}%):")
    show_task(task_to_dict(task))


def stats(s):
    def go(user):
        from datetime import date
        tasks = Task.query.filter_by(user_id=user.id).all()
        today = date.today()
        return {
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.completed),
            "pending": sum(1 for t in tasks if not t.completed),
            "overdue": sum(1 for t in tasks
                           if t.due_date and t.due_date < today and not t.completed),
        }
    st = with_user(s, go)
    print("\n== Your stats ==")
    for k, v in st.items():
        print(f"  {k:<10}: {v}")


def change_password(s):
    res = s.http.post("/change-password", data={
        "current_password": getpass.getpass("Current password: "),
        "new_password": getpass.getpass("New password: "),
    }, follow_redirects=True)
    print("Password change submitted." if res.status_code == 200 else "Failed.")


def main():
    s = Session()
    if not login_flow(s):
        return
    actions = [
        ("Dashboard / task list",        lambda: list_tasks(s)),
        ("Pending tasks only",           lambda: list_tasks(s, include_done=False)),
        ("Add task (plain English, AI)", lambda: add_task_nlp(s)),
        ("Add task (manual fields)",     lambda: add_task_manual(s)),
        ("What should I do next? (AI)",  lambda: do_next(s)),
        ("Toggle task complete",         lambda: complete_task(s)),
        ("Reschedule task",              lambda: reschedule_task(s)),
        ("Delete task",                  lambda: delete_task(s)),
        ("My stats",                     lambda: stats(s)),
        ("Change password",              lambda: change_password(s)),
    ]
    while True:
        print(f"\n===== TaskMind — {s.username} =====")
        for i, (label, _) in enumerate(actions, 1):
            print(f"  {i}. {label}")
        print("  0. Exit")
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
