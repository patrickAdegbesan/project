#!/usr/bin/env python3
"""
ComplaintDesk — Terminal client.

Menu-driven interface with the same functionality as the website.
It drives the exact same Flask application in-process (no server, no
network), so every action goes through the same validation, permissions
and database as the browser UI.

Usage:  python cli.py
"""

import getpass
import json
import sys

from app import app


class Client:
    """Thin wrapper around the Flask test client keeping the session."""

    def __init__(self):
        self.http = app.test_client()
        self.user = None

    def call(self, method, path, body=None):
        fn = getattr(self.http, method)
        res = fn(path, json=body) if body is not None else fn(path)
        try:
            data = res.get_json()
        except Exception:
            data = None
        return res.status_code, (data if data is not None else {})


def show(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def ask(prompt, default=None, required=True):
    while True:
        raw = input(f"{prompt}{f' [{default}]' if default is not None else ''}: ").strip()
        if not raw and default is not None:
            return default
        if raw or not required:
            return raw
        print("  (required)")


def pause():
    input("\n  -- press Enter to continue --")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def do_register(c):
    print("\n== Register ==")
    body = {
        "name":     ask("Full name"),
        "email":    ask("Email"),
        "password": getpass.getpass("Password: "),
        "role":     ask("Role (student/staff)", default="student"),
    }
    if body["role"] == "student":
        body["matric_no"] = ask("Matric number", required=False)
        body["department"] = ask("Department", required=False)
    else:
        body["staff_id"] = ask("Staff ID", required=False)
        body["department"] = ask("Department", required=False)
    code, data = c.call("post", "/api/auth/register", body)
    show(data)
    return code < 300


def do_login(c):
    print("\n== Login ==")
    body = {"email": ask("Email"), "password": getpass.getpass("Password: ")}
    code, data = c.call("post", "/api/auth/login", body)
    if code < 300 and "user" in data:
        c.user = data["user"]
        print(f"\nWelcome, {c.user['name']} ({c.user['role']})")
        return True
    show(data)
    return False


def do_logout(c):
    c.call("post", "/api/auth/logout")
    c.user = None
    print("Logged out.")


def do_change_password(c):
    body = {
        "current_password": getpass.getpass("Current password: "),
        "new_password":     getpass.getpass("New password: "),
    }
    _, data = c.call("post", "/api/auth/change-password", body)
    show(data)


def do_update_profile(c):
    body = {}
    name = ask("New name (blank = keep)", required=False)
    dept = ask("New department (blank = keep)", required=False)
    if name:
        body["name"] = name
    if dept:
        body["department"] = dept
    if not body:
        print("Nothing to update.")
        return
    _, data = c.call("post", "/api/auth/update-profile", body)
    show(data)


# ---------------------------------------------------------------------------
# Complaints (user)
# ---------------------------------------------------------------------------

def list_categories(c):
    _, data = c.call("get", "/api/categories")
    cats = data.get("categories", data)
    print("\nCategories:")
    for cat in cats:
        if isinstance(cat, dict):
            print(f"  {cat.get('id')}: {cat.get('name')}")
        else:
            print(f"  - {cat}")
    return cats


def submit_complaint(c):
    print("\n== Submit complaint ==")
    list_categories(c)
    body = {
        "title":       ask("Title"),
        "category_id": int(ask("Category id")),
        "description": ask("Description"),
        "priority":    ask("Priority (low/medium/high)", default="medium"),
    }
    _, data = c.call("post", "/api/complaints", body)
    show(data)


def my_complaints(c):
    _, data = c.call("get", "/api/complaints")
    items = data.get("complaints", [])
    print(f"\nYour complaints ({data.get('total', len(items))}):")
    for it in items:
        print(f"  #{it['id']:<4} [{it.get('status','?'):<12}] {it.get('title','')}")
    return items


def view_complaint(c):
    cid = ask("Complaint id")
    _, data = c.call("get", f"/api/complaints/{cid}")
    show(data)


def respond_complaint(c):
    cid = ask("Complaint id")
    body = {"message": ask("Message")}
    _, data = c.call("post", f"/api/complaints/{cid}/respond", body)
    show(data)


def user_stats(c):
    _, data = c.call("get", "/api/user/stats")
    show(data)


def announcements(c):
    _, data = c.call("get", "/api/announcements")
    for a in data.get("announcements", []):
        print(f"\n[{a.get('created_at','')}] {a.get('title','')}\n  {a.get('body','')}")


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

def admin_complaints(c):
    status = ask("Filter status (blank = all)", required=False)
    path = "/api/admin/complaints" + (f"?status={status}" if status else "")
    _, data = c.call("get", path)
    for it in data.get("complaints", []):
        print(f"  #{it['id']:<4} [{it.get('status','?'):<12}] "
              f"({it.get('priority','?'):<6}) {it.get('title','')}"
              f"  — {it.get('user_name', it.get('user_email',''))}")


def admin_update_complaint(c):
    cid = ask("Complaint id")
    body = {}
    status = ask("New status (blank = keep)", required=False)
    assignee = ask("Assign to user id (blank = keep)", required=False)
    note = ask("Resolution note (blank = none)", required=False)
    if status:
        body["status"] = status
    if assignee:
        body["assigned_to"] = int(assignee)
    if note:
        body["resolution_note"] = note
    _, data = c.call("put", f"/api/admin/complaints/{cid}", body)
    show(data)


def admin_stats(c):
    _, data = c.call("get", "/api/admin/stats")
    show(data)


def admin_users(c):
    _, data = c.call("get", "/api/admin/users")
    for u in data.get("users", []):
        print(f"  #{u['id']:<4} {u.get('role','?'):<8} {u.get('name','')} <{u.get('email','')}>")


def admin_create_user(c):
    body = {
        "name":  ask("Name"),
        "email": ask("Email"),
        "role":  ask("Role (student/staff/admin)", default="staff"),
        "password": getpass.getpass("Password: "),
        "department": ask("Department", required=False),
    }
    _, data = c.call("post", "/api/admin/users", body)
    show(data)


def admin_update_user(c):
    uid = ask("User id")
    body = {}
    for field in ("name", "role", "department", "status"):
        val = ask(f"New {field} (blank = keep)", required=False)
        if val:
            body[field] = val
    _, data = c.call("put", f"/api/admin/users/{uid}", body)
    show(data)


def admin_announcements(c):
    _, data = c.call("get", "/api/admin/announcements")
    for a in data.get("announcements", []):
        print(f"  #{a['id']:<4} {a.get('title','')}")


def admin_post_announcement(c):
    body = {"title": ask("Title"), "body": ask("Body")}
    _, data = c.call("post", "/api/admin/announcements", body)
    show(data)


def admin_reports(c):
    _, data = c.call("get", "/api/admin/reports")
    show(data)


def admin_settings(c):
    _, data = c.call("get", "/api/admin/settings")
    show(data)


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------

def menu(title, options):
    """options: list of (label, fn). Returns False when user exits."""
    print(f"\n===== {title} =====")
    for i, (label, _) in enumerate(options, 1):
        print(f"  {i}. {label}")
    print("  0. Back / exit")
    choice = input("> ").strip()
    if choice == "0":
        return False
    try:
        _, fn = options[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return True
    try:
        fn()
    except KeyboardInterrupt:
        print("\n(cancelled)")
    except Exception as exc:                      # keep the menu alive
        print(f"Error: {exc}")
    return True


def main():
    c = Client()
    print("=" * 46)
    print("  ComplaintDesk — terminal client")
    print("=" * 46)

    while True:
        if c.user is None:
            alive = menu("ComplaintDesk", [
                ("Login",    lambda: do_login(c)),
                ("Register", lambda: do_register(c)),
            ])
            if not alive:
                break
            continue

        common = [
            ("My complaints",        lambda: my_complaints(c)),
            ("Submit complaint",     lambda: submit_complaint(c)),
            ("View complaint",       lambda: view_complaint(c)),
            ("Respond to complaint", lambda: respond_complaint(c)),
            ("My stats",             lambda: user_stats(c)),
            ("Announcements",        lambda: announcements(c)),
            ("Update profile",       lambda: do_update_profile(c)),
            ("Change password",      lambda: do_change_password(c)),
            ("Logout",               lambda: do_logout(c)),
        ]
        admin = [
            ("[admin] All complaints",     lambda: admin_complaints(c)),
            ("[admin] Update complaint",   lambda: admin_update_complaint(c)),
            ("[admin] Stats",              lambda: admin_stats(c)),
            ("[admin] Users",              lambda: admin_users(c)),
            ("[admin] Create user",        lambda: admin_create_user(c)),
            ("[admin] Update user",        lambda: admin_update_user(c)),
            ("[admin] Announcements",      lambda: admin_announcements(c)),
            ("[admin] Post announcement",  lambda: admin_post_announcement(c)),
            ("[admin] Reports",            lambda: admin_reports(c)),
            ("[admin] Settings",           lambda: admin_settings(c)),
        ]
        options = common + (admin if c.user.get("role") == "admin" else [])
        if not menu(f"Menu — {c.user['name']} ({c.user['role']})", options):
            break

    print("Bye.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye.")
        sys.exit(0)
