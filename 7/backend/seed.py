"""
seed.py — Populate the database with 7 months of realistic demo data.

Usage:
    cd backend
    python seed.py

Creates a demo account:
    Email    : demo@calebuniversity.edu.ng
    Password : Demo1234
"""

import sys
import os
import sqlite3
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from config import active_config as cfg
from models.user import create_user, get_user_by_email, init_users_table, get_db
from models.task import init_tasks_table
from models.schedule import init_schedule_table
from models.progress import init_progress_tables
from services.reminder_service import init_reminders_table

# ---------------------------------------------------------------------------
# Seed constants
# ---------------------------------------------------------------------------

DEMO_USER = {
    "username":  "chibuzor99",
    "email":     "demo@calebuniversity.edu.ng",
    "password":  "Demo1234",
    "full_name": "Nwachukwu Chibuzor Benjamin",
}

SUBJECTS = [
    "CSC 301 — Data Structures",
    "CSC 302 — Algorithms",
    "CSC 305 — Operating Systems",
    "CSC 401 — Artificial Intelligence",
    "CSC 403 — Software Engineering",
    "MTH 201 — Numerical Methods",
    "GST 301 — Entrepreneurship",
]

SUBJECT_SHORT = {
    "CSC 301 — Data Structures":   "CSC 301",
    "CSC 302 — Algorithms":        "CSC 302",
    "CSC 305 — Operating Systems": "CSC 305",
    "CSC 401 — Artificial Intelligence": "CSC 401",
    "CSC 403 — Software Engineering":    "CSC 403",
    "MTH 201 — Numerical Methods": "MTH 201",
    "GST 301 — Entrepreneurship":  "GST 301",
}

TASK_TEMPLATES = [
    # (title_template, estimated_minutes, base_priority)
    ("Complete assignment on {topic}",          90,  "high"),
    ("Read Chapter {n} of {subject} textbook", 60,  "medium"),
    ("Revise lecture notes for {subject}",      45,  "medium"),
    ("Prepare for {subject} quiz",              75,  "high"),
    ("Group project meeting — {subject}",       60,  "medium"),
    ("Submit {subject} lab report",             120, "urgent"),
    ("Practice past exam questions — {subject}", 90, "high"),
    ("Watch recorded lecture: {topic}",          40, "low"),
    ("Write term paper outline — {subject}",    100, "high"),
    ("Code {topic} implementation",             150, "high"),
    ("Attend {subject} tutorial",                60, "medium"),
    ("Complete online quiz for {subject}",       30, "medium"),
    ("Review feedback on {subject} assignment",  30, "low"),
    ("Create flashcards for {subject}",          45, "low"),
    ("Summarise week's {subject} lectures",      60, "medium"),
]

TOPICS = [
    "binary search trees", "graph traversal", "dynamic programming",
    "memory management", "process scheduling", "neural networks",
    "regression analysis", "software testing", "UML diagrams",
    "sorting algorithms", "hash tables", "linked lists",
    "recursion", "database normalisation", "TCP/IP protocols",
]

BLOCK_TITLES = [
    "Morning Study Session", "Afternoon Revision", "Evening Review",
    "Deep Focus Block", "Library Session", "Group Study",
    "Lecture Catch-Up", "Problem Sets", "Research Time",
    "Project Work", "Note-Taking", "Past Papers Practice",
]

GOAL_TEMPLATES = [
    ("Complete all semester assignments",     "tasks",  30,  18),
    ("Study 200 hours this semester",         "hours",  200, 120),
    ("Achieve 80% average in CSC courses",    "score",  80,  65),
    ("Submit all lab reports on time",        "tasks",  12,  10),
    ("Read all textbook chapters",            "tasks",  40,  22),
    ("Attend all tutorial sessions",          "tasks",  24,  20),
]

BLOCK_COLORS = {
    "study":  "#4A90D9",
    "break":  "#27ae60",
    "review": "#f39c12",
    "exam":   "#e74c3c",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_past_date(days_ago_min=1, days_ago_max=210):
    delta = random.randint(days_ago_min, days_ago_max)
    return (date.today() - timedelta(days=delta)).isoformat()


def rand_future_date(days_ahead_min=1, days_ahead_max=60):
    delta = random.randint(days_ahead_min, days_ahead_max)
    return (date.today() + timedelta(days=delta)).isoformat()


def rand_datetime_future(days=60):
    delta = random.randint(1, days)
    hour  = random.choice([9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20])
    dt = datetime.now() + timedelta(days=delta)
    return dt.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat()


def rand_datetime_past(days_ago_min=1, days_ago_max=210):
    delta = random.randint(days_ago_min, days_ago_max)
    hour  = random.choice([9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20])
    dt = datetime.now() - timedelta(days=delta)
    return dt.replace(hour=hour, minute=random.choice([0, 15, 30, 45]),
                      second=0, microsecond=0).isoformat()


def pick_subject():
    return random.choice(SUBJECTS)


def make_task_title(subject):
    template, est, priority = random.choice(TASK_TEMPLATES)
    short = SUBJECT_SHORT[subject]
    title = template.format(
        topic=random.choice(TOPICS),
        subject=short,
        n=random.randint(1, 12),
    )
    return title, est, priority


# ---------------------------------------------------------------------------
# Database direct inserts (bypassing models to set timestamps freely)
# ---------------------------------------------------------------------------

def insert_task(conn, user_id, title, subject, priority, status,
                due_date, estimated_minutes, actual_minutes,
                created_at, completed_at, tags=""):
    conn.execute(
        """INSERT INTO tasks
           (user_id, title, subject, priority, status, due_date,
            estimated_minutes, actual_minutes, tags,
            created_at, updated_at, completed_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, title, subject, priority, status, due_date,
         estimated_minutes, actual_minutes, tags,
         created_at, created_at, completed_at)
    )


def insert_study_log(conn, user_id, log_date, subject, minutes, note=""):
    conn.execute(
        """INSERT INTO study_logs (user_id, log_date, subject, minutes, note, created_at)
           VALUES (?,?,?,?,?,?)""",
        (user_id, log_date, subject, minutes, note,
         f"{log_date}T{random.randint(8,20):02d}:{random.choice([0,15,30,45]):02d}:00")
    )


def insert_block(conn, user_id, title, subject, block_date, start_time, end_time,
                 block_type, color):
    now = datetime.utcnow().isoformat()
    conn.execute(
        """INSERT INTO schedule_blocks
           (user_id, title, subject, block_date, start_time, end_time,
            block_type, color, completed, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, title, subject, block_date, start_time, end_time,
         block_type, color, 1, now, now)
    )


def insert_goal(conn, user_id, title, description, target_date, metric,
                target_value, current_value, status):
    now = datetime.utcnow().isoformat()
    conn.execute(
        """INSERT INTO goals
           (user_id, title, description, target_date, metric,
            target_value, current_value, status, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (user_id, title, description, target_date, metric,
         target_value, current_value, status, now, now)
    )


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

def seed():
    os.makedirs(os.path.dirname(cfg.DB_PATH), exist_ok=True)

    # Initialise all tables
    with get_db() as conn:
        init_users_table(conn)
        init_tasks_table(conn)
        init_schedule_table(conn)
        init_progress_tables(conn)
        init_reminders_table(conn)

    # Create or reuse demo user
    user = get_user_by_email(DEMO_USER["email"])
    if not user:
        user = create_user(
            DEMO_USER["username"], DEMO_USER["email"],
            DEMO_USER["password"], DEMO_USER["full_name"]
        )
        print(f"  Created user: {user['email']}")
    else:
        print(f"  User already exists: {user['email']}")

    user_id = user["id"]

    # Grant admin rights to demo user
    with get_db() as conn:
        conn.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
        conn.commit()
    print("  Granted admin access to demo user.")

    today = date.today()

    with get_db() as conn:

        # ----------------------------------------------------------------
        # TASKS — 7 months of history
        # ----------------------------------------------------------------
        print("  Seeding tasks...")
        tasks_inserted = 0

        # Completed tasks — past 7 months (130 tasks)
        for _ in range(130):
            subject = pick_subject()
            title, est, priority = make_task_title(subject)
            created  = rand_datetime_past(210)
            due_iso  = rand_past_date(1, 200)
            due_dt   = f"{due_iso}T{random.randint(9,20):02d}:00:00"
            actual   = int(est * random.uniform(0.7, 1.4))
            completed_at = rand_datetime_past(1, 200)
            insert_task(conn, user_id, title, subject, priority,
                        "completed", due_dt, est, actual,
                        created, completed_at,
                        tags=random.choice(["exam", "assignment", "project", "revision", ""]))
            tasks_inserted += 1

        # In-progress tasks (15)
        for _ in range(15):
            subject = pick_subject()
            title, est, priority = make_task_title(subject)
            created = rand_datetime_past(30)
            due_dt  = rand_datetime_future(20)
            insert_task(conn, user_id, title, subject, priority,
                        "in_progress", due_dt, est, int(est * 0.4),
                        created, None,
                        tags=random.choice(["project", "assignment", ""]))
            tasks_inserted += 1

        # Pending tasks — future deadlines (40)
        for _ in range(40):
            subject = pick_subject()
            title, est, priority = make_task_title(subject)
            created = rand_datetime_past(14)
            due_dt  = rand_datetime_future(60)
            insert_task(conn, user_id, title, subject, priority,
                        "pending", due_dt, est, 0,
                        created, None,
                        tags=random.choice(["exam", "coursework", "reading", ""]))
            tasks_inserted += 1

        # Overdue tasks (8)
        for _ in range(8):
            subject = pick_subject()
            title, est, priority = make_task_title(subject)
            created  = rand_datetime_past(40)
            due_dt   = rand_datetime_past(1, 14)
            insert_task(conn, user_id, title, subject,
                        random.choice(["high", "urgent"]),
                        "pending", due_dt, est, 0,
                        created, None, tags="overdue")
            tasks_inserted += 1

        # Urgent tasks due very soon (5)
        for _ in range(5):
            subject = pick_subject()
            title, est, _ = make_task_title(subject)
            created = rand_datetime_past(5)
            hours_ahead = random.randint(6, 47)
            due_dt = (datetime.now() + timedelta(hours=hours_ahead)).isoformat()
            insert_task(conn, user_id, title, subject, "urgent",
                        "pending", due_dt, est, 0, created, None, tags="urgent,exam")
            tasks_inserted += 1

        conn.commit()
        print(f"    {tasks_inserted} tasks created.")

        # ----------------------------------------------------------------
        # STUDY LOGS — 7 months of daily sessions
        # ----------------------------------------------------------------
        print("  Seeding study logs...")
        logs_inserted = 0
        current = today - timedelta(days=210)

        while current <= today:
            weekday = current.weekday()  # 0=Mon, 6=Sun
            # Study on weekdays more than weekends
            num_sessions = random.choices(
                [0, 1, 2, 3],
                weights=[10, 30, 40, 20] if weekday < 5 else [40, 40, 15, 5]
            )[0]

            for _ in range(num_sessions):
                subject = pick_subject()
                minutes = random.choice([25, 30, 45, 50, 60, 75, 90, 120])
                insert_study_log(conn, user_id, current.isoformat(), subject, minutes)
                logs_inserted += 1

            current += timedelta(days=1)

        conn.commit()
        print(f"    {logs_inserted} study log entries created.")

        # ----------------------------------------------------------------
        # SCHEDULE BLOCKS — past 4 weeks + next 2 weeks
        # ----------------------------------------------------------------
        print("  Seeding schedule blocks...")
        blocks_inserted = 0
        sched_start = today - timedelta(days=28)
        sched_end   = today + timedelta(days=14)
        current = sched_start

        while current <= sched_end:
            weekday = current.weekday()
            # Skip Sunday mostly
            if weekday == 6 and random.random() > 0.3:
                current += timedelta(days=1)
                continue

            # 1–4 blocks per day
            num_blocks = random.choices([1, 2, 3, 4], weights=[20, 40, 30, 10])[0]
            used_hours = set()

            for _ in range(num_blocks):
                hour = random.choice([8,9,10,11,13,14,15,16,17,18,19,20])
                if hour in used_hours:
                    continue
                used_hours.add(hour)

                block_type = random.choices(
                    ["study", "review", "break", "exam"],
                    weights=[60, 25, 12, 3]
                )[0]
                subject = pick_subject()
                duration = random.choice([1, 1, 2])  # hours
                end_hour = min(hour + duration, 22)

                insert_block(
                    conn, user_id,
                    title=random.choice(BLOCK_TITLES),
                    subject=SUBJECT_SHORT[subject],
                    block_date=current.isoformat(),
                    start_time=f"{hour:02d}:00",
                    end_time=f"{end_hour:02d}:00",
                    block_type=block_type,
                    color=BLOCK_COLORS[block_type],
                )
                blocks_inserted += 1

            current += timedelta(days=1)

        conn.commit()
        print(f"    {blocks_inserted} schedule blocks created.")

        # ----------------------------------------------------------------
        # GOALS
        # ----------------------------------------------------------------
        print("  Seeding goals...")
        for title, metric, target, current_val in GOAL_TEMPLATES:
            status = "achieved" if current_val >= target else "active"
            target_date = (today + timedelta(days=random.randint(30, 90))).isoformat()
            insert_goal(conn, user_id, title, "", target_date, metric,
                        target, current_val, status)

        conn.commit()
        print(f"    {len(GOAL_TEMPLATES)} goals created.")

    print("\nSeed complete!")
    print("─" * 40)
    print(f"  Login email : {DEMO_USER['email']}")
    print(f"  Password    : {DEMO_USER['password']}")
    print("─" * 40)


if __name__ == "__main__":
    print("\nSeeding Study Planner database...\n")
    seed()
