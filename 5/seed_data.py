"""
Seed TaskMind with a full year of realistic hardcoded task data.
Run: python seed_data.py
"""
from app import app, db, bcrypt, User, Task, calculate_priority
from datetime import date, datetime, timedelta
import random

TODAY = date.today()

def d(offset):
    """Return a date offset from today."""
    return TODAY + timedelta(days=offset)

def dt(offset, hour=10, minute=0):
    """Return a datetime offset from today."""
    return datetime.combine(d(offset), datetime.min.time()).replace(hour=hour, minute=minute)


TASKS = [
    # ── OVERDUE (already past) ─────────────────────────────────────────────
    dict(title="File annual tax return",             due=d(-180), time="17:00", imp=3, effort=240,  done=True,  done_at=dt(-179, 14)),
    dict(title="Renew car insurance",                due=d(-160), time=None,    imp=3, effort=30,   done=True,  done_at=dt(-159, 9)),
    dict(title="Submit Q1 expense report",           due=d(-120), time="12:00", imp=3, effort=60,   done=True,  done_at=dt(-118, 11)),
    dict(title="Book dentist appointment",           due=d(-110), time=None,    imp=2, effort=15,   done=True,  done_at=dt(-109, 10)),
    dict(title="Review team performance reports",    due=d(-100), time="16:00", imp=3, effort=120,  done=True,  done_at=dt(-98,  15)),
    dict(title="Update LinkedIn profile",            due=d(-95),  time=None,    imp=1, effort=45,   done=True,  done_at=dt(-93,  19)),
    dict(title="Migrate old photos to cloud",        due=d(-90),  time=None,    imp=1, effort=180,  done=True,  done_at=dt(-87,  20)),
    dict(title="Prepare mid-year budget review",     due=d(-85),  time="10:00", imp=3, effort=90,   done=True,  done_at=dt(-84,  9)),
    dict(title="Complete online safety training",    due=d(-80),  time="17:00", imp=2, effort=60,   done=True,  done_at=dt(-80,  16)),
    dict(title="Submit Q2 project report",           due=d(-75),  time="12:00", imp=3, effort=120,  done=True,  done_at=dt(-74,  11)),
    dict(title="Organise team offsite logistics",    due=d(-70),  time="09:00", imp=3, effort=90,   done=True,  done_at=dt(-70,  8)),
    dict(title="Archive old project files",          due=d(-65),  time=None,    imp=1, effort=60,   done=True,  done_at=dt(-63,  14)),
    dict(title="Write blog post: AI in productivity",due=d(-60),  time=None,    imp=2, effort=120,  done=True,  done_at=dt(-58,  20)),
    dict(title="Upgrade laptop OS",                  due=d(-55),  time=None,    imp=2, effort=45,   done=True,  done_at=dt(-54,  18)),
    dict(title="Review vendor contracts",            due=d(-50),  time="15:00", imp=3, effort=90,   done=True,  done_at=dt(-49,  14)),
    dict(title="Plan Q3 OKRs",                      due=d(-45),  time="10:00", imp=3, effort=120,  done=True,  done_at=dt(-44,  10)),
    dict(title="Order new office supplies",          due=d(-42),  time=None,    imp=1, effort=20,   done=True,  done_at=dt(-42,  12)),
    dict(title="Conduct 1:1 with each team member",  due=d(-38),  time="14:00", imp=3, effort=180,  done=True,  done_at=dt(-37,  15)),
    dict(title="Read 'Deep Work' by Cal Newport",    due=d(-35),  time=None,    imp=1, effort=300,  done=True,  done_at=dt(-28,  21)),
    dict(title="Set up new project repo on GitHub",  due=d(-30),  time=None,    imp=2, effort=30,   done=True,  done_at=dt(-30,  10)),
    dict(title="Prepare investor update deck",       due=d(-28),  time="09:00", imp=3, effort=180,  done=True,  done_at=dt(-28,  8)),
    dict(title="Schedule Q3 sprint planning",        due=d(-25),  time="11:00", imp=3, effort=30,   done=True,  done_at=dt(-25,  11)),
    dict(title="Fix homepage loading bug",           due=d(-22),  time=None,    imp=3, effort=90,   done=True,  done_at=dt(-22,  16)),
    dict(title="Update product roadmap",             due=d(-20),  time="14:00", imp=3, effort=120,  done=True,  done_at=dt(-19,  13)),
    dict(title="Review pull requests from team",     due=d(-18),  time=None,    imp=2, effort=60,   done=True,  done_at=dt(-18,  17)),
    dict(title="Send newsletter to subscribers",     due=d(-16),  time="10:00", imp=2, effort=90,   done=True,  done_at=dt(-16,  9)),
    dict(title="Audit website accessibility",        due=d(-14),  time=None,    imp=2, effort=120,  done=True,  done_at=dt(-13,  15)),
    dict(title="Write unit tests for auth module",   due=d(-12),  time=None,    imp=3, effort=90,   done=True,  done_at=dt(-12,  14)),
    dict(title="Review and approve design mockups",  due=d(-10),  time="13:00", imp=3, effort=60,   done=True,  done_at=dt(-10,  12)),
    dict(title="Refactor database query layer",      due=d(-8),   time=None,    imp=2, effort=180,  done=True,  done_at=dt(-7,   16)),
    dict(title="Send client follow-up emails",       due=d(-7),   time="12:00", imp=3, effort=45,   done=True,  done_at=dt(-7,   11)),
    dict(title="Update API documentation",           due=d(-6),   time=None,    imp=2, effort=90,   done=True,  done_at=dt(-5,   14)),
    dict(title="Fix mobile responsiveness issues",   due=d(-5),   time=None,    imp=3, effort=120,  done=True,  done_at=dt(-5,   17)),
    dict(title="Deploy hotfix to production",        due=d(-4),   time="16:00", imp=3, effort=30,   done=True,  done_at=dt(-4,   15)),
    dict(title="Prepare weekly team standup agenda", due=d(-4),   time="08:30", imp=2, effort=20,   done=True,  done_at=dt(-4,   8)),
    dict(title="Review marketing campaign results",  due=d(-3),   time="14:00", imp=2, effort=60,   done=True,  done_at=dt(-3,   13)),
    dict(title="Update project dependencies",        due=d(-3),   time=None,    imp=2, effort=45,   done=True,  done_at=dt(-3,   16)),
    dict(title="Sync with design team on branding",  due=d(-2),   time="11:00", imp=2, effort=60,   done=True,  done_at=dt(-2,   10)),
    dict(title="Write post-mortem for outage",       due=d(-2),   time=None,    imp=3, effort=90,   done=True,  done_at=dt(-1,   14)),
    dict(title="Submit expense receipts",            due=d(-1),   time="17:00", imp=2, effort=20,   done=True,  done_at=dt(-1,   16)),

    # ── OVERDUE (not done — truly overdue) ────────────────────────────────
    dict(title="Renew domain name (taskmind.io)",    due=d(-5),   time=None,    imp=3, effort=15,   done=False, done_at=None),
    dict(title="Reply to partnership proposal email",due=d(-3),   time=None,    imp=3, effort=30,   done=False, done_at=None),
    dict(title="Update team org chart",              due=d(-2),   time=None,    imp=2, effort=20,   done=False, done_at=None),
    dict(title="Pay freelancer invoice #1042",       due=d(-1),   time="17:00", imp=3, effort=10,   done=False, done_at=None),

    # ── TODAY ──────────────────────────────────────────────────────────────
    dict(title="Morning standup call",               due=d(0),    time="09:00", imp=3, effort=30,   done=True,  done_at=dt(0, 9, 30)),
    dict(title="Review overnight CI failures",       due=d(0),    time="09:30", imp=3, effort=30,   done=True,  done_at=dt(0, 10)),
    dict(title="Write daily progress notes",         due=d(0),    time="18:00", imp=1, effort=15,   done=False, done_at=None),
    dict(title="Code review: payments service PR",   due=d(0),    time="14:00", imp=3, effort=60,   done=False, done_at=None),
    dict(title="Update Jira board for sprint",       due=d(0),    time="10:00", imp=2, effort=20,   done=False, done_at=None),

    # ── UPCOMING (next 2 weeks) ────────────────────────────────────────────
    dict(title="Submit quarterly report",            due=d(1),    time="17:00", imp=3, effort=120,  done=False, done_at=None),
    dict(title="Review project proposal",            due=d(1),    time="14:00", imp=3, effort=60,   done=False, done_at=None),
    dict(title="Team meeting prep",                  due=d(1),    time="09:00", imp=3, effort=30,   done=False, done_at=None),
    dict(title="Demo new features to stakeholders",  due=d(2),    time="15:00", imp=3, effort=60,   done=False, done_at=None),
    dict(title="Fix search ranking algorithm bug",   due=d(2),    time=None,    imp=3, effort=120,  done=False, done_at=None),
    dict(title="Buy groceries",                      due=d(2),    time=None,    imp=2, effort=45,   done=False, done_at=None),
    dict(title="Write integration tests for API",    due=d(3),    time=None,    imp=2, effort=90,   done=False, done_at=None),
    dict(title="Send weekly status update to CEO",   due=d(3),    time="17:00", imp=3, effort=30,   done=False, done_at=None),
    dict(title="Optimise slow database queries",     due=d(4),    time=None,    imp=2, effort=120,  done=False, done_at=None),
    dict(title="Record product demo video",          due=d(4),    time="13:00", imp=2, effort=90,   done=False, done_at=None),
    dict(title="Call dentist",                       due=d(5),    time=None,    imp=2, effort=15,   done=False, done_at=None),
    dict(title="Review competitor product launches",  due=d(5),    time=None,    imp=2, effort=60,   done=False, done_at=None),
    dict(title="Prepare onboarding docs for new hire",due=d(6),   time=None,    imp=3, effort=90,   done=False, done_at=None),
    dict(title="Run security audit on API endpoints",due=d(6),    time=None,    imp=3, effort=120,  done=False, done_at=None),
    dict(title="Design new dashboard layout",        due=d(7),    time=None,    imp=2, effort=180,  done=False, done_at=None),
    dict(title="Read AI paper: Attention Is All You Need", due=d(7), time=None, imp=1, effort=180,  done=False, done_at=None),
    dict(title="Monthly 1:1 with manager",           due=d(8),    time="10:00", imp=3, effort=60,   done=False, done_at=None),
    dict(title="Set up staging environment",         due=d(8),    time=None,    imp=2, effort=90,   done=False, done_at=None),
    dict(title="Finalise hiring job descriptions",   due=d(9),    time="12:00", imp=3, effort=60,   done=False, done_at=None),
    dict(title="Plan team retrospective session",    due=d(9),    time=None,    imp=2, effort=45,   done=False, done_at=None),
    dict(title="Implement dark mode toggle",         due=d(10),   time=None,    imp=1, effort=120,  done=False, done_at=None),
    dict(title="Review SLA agreements with vendors", due=d(10),   time="14:00", imp=2, effort=60,   done=False, done_at=None),
    dict(title="Write technical spec: notifications",due=d(11),   time=None,    imp=3, effort=120,  done=False, done_at=None),
    dict(title="Explore new ML libraries",           due=d(11),   time=None,    imp=1, effort=120,  done=False, done_at=None),
    dict(title="Update privacy policy page",         due=d(12),   time="17:00", imp=3, effort=45,   done=False, done_at=None),
    dict(title="Prepare Q3 budget proposal",         due=d(12),   time=None,    imp=3, effort=180,  done=False, done_at=None),
    dict(title="Set up error monitoring (Sentry)",   due=d(13),   time=None,    imp=2, effort=60,   done=False, done_at=None),
    dict(title="Schedule annual performance reviews",due=d(14),   time="11:00", imp=3, effort=30,   done=False, done_at=None),

    # ── FUTURE (2 weeks – 3 months) ───────────────────────────────────────
    dict(title="Plan company all-hands meeting",     due=d(18),   time="10:00", imp=3, effort=120,  done=False, done_at=None),
    dict(title="Submit conference talk proposal",    due=d(20),   time="23:59", imp=2, effort=120,  done=False, done_at=None),
    dict(title="Build internal analytics dashboard", due=d(21),   time=None,    imp=2, effort=480,  done=False, done_at=None),
    dict(title="Complete AWS certification course",  due=d(25),   time=None,    imp=2, effort=600,  done=False, done_at=None),
    dict(title="Launch beta program for new feature",due=d(28),   time="09:00", imp=3, effort=240,  done=False, done_at=None),
    dict(title="Conduct user research interviews",   due=d(30),   time=None,    imp=3, effort=180,  done=False, done_at=None),
    dict(title="Write end-of-quarter board report",  due=d(35),   time="17:00", imp=3, effort=180,  done=False, done_at=None),
    dict(title="Migrate infrastructure to Kubernetes",due=d(40),  time=None,    imp=2, effort=480,  done=False, done_at=None),
    dict(title="Run A/B test on checkout flow",      due=d(45),   time=None,    imp=2, effort=120,  done=False, done_at=None),
    dict(title="Hire senior backend engineer",       due=d(50),   time=None,    imp=3, effort=300,  done=False, done_at=None),
    dict(title="Read 'The Lean Startup'",            due=d(60),   time=None,    imp=1, effort=360,  done=False, done_at=None),
    dict(title="Publish open-source SDK v2.0",       due=d(60),   time=None,    imp=2, effort=480,  done=False, done_at=None),
    dict(title="Plan annual team retreat",           due=d(75),   time=None,    imp=2, effort=180,  done=False, done_at=None),
    dict(title="Renew professional certifications",  due=d(90),   time=None,    imp=2, effort=120,  done=False, done_at=None),
    dict(title="Complete redesign of mobile app",    due=d(90),   time=None,    imp=3, effort=960,  done=False, done_at=None),
    dict(title="Evaluate new cloud providers",       due=d(100),  time=None,    imp=2, effort=180,  done=False, done_at=None),
    dict(title="Write company engineering blog",     due=d(120),  time=None,    imp=1, effort=120,  done=False, done_at=None),
    dict(title="Plan product launch event",          due=d(150),  time=None,    imp=3, effort=300,  done=False, done_at=None),
    dict(title="Annual salary review process",       due=d(180),  time=None,    imp=3, effort=240,  done=False, done_at=None),
    dict(title="Explore international expansion",    due=d(270),  time=None,    imp=2, effort=480,  done=False, done_at=None),
    dict(title="Complete Series A fundraising",      due=d(365),  time=None,    imp=3, effort=600,  done=False, done_at=None),
]


def seed(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found. Creating...")
            user = User(
                username=username,
                email=f"{username}@demo.com",
                password=bcrypt.generate_password_hash("demo123").decode()
            )
            db.session.add(user)
            db.session.commit()

        # Remove previous demo tasks only
        Task.query.filter_by(user_id=user.id, is_demo=True).delete()
        db.session.commit()

        added = 0
        for t in TASKS:
            score, label = calculate_priority(t['imp'], t['due'], t['effort'])
            task = Task(
                user_id=user.id,
                title=t['title'],
                due_date=t['due'],
                due_time=t['time'],
                importance=t['imp'],
                effort_minutes=t['effort'],
                priority_score=score,
                priority_label=label,
                completed=t['done'],
                completed_at=t['done_at'],
                is_demo=True,
                created_at=datetime.combine(t['due'] - timedelta(days=random.randint(1,7)),
                                            datetime.min.time()).replace(hour=random.randint(8,18)),
            )
            db.session.add(task)
            added += 1

        db.session.commit()
        print(f"Seeded {added} tasks for user '{username}'.")

        # Summary
        tasks = Task.query.filter_by(user_id=user.id).all()
        total     = len(tasks)
        completed = sum(1 for t in tasks if t.completed)
        overdue   = sum(1 for t in tasks if t.due_date and t.due_date < TODAY and not t.completed)
        high      = sum(1 for t in tasks if t.priority_label == 'High' and not t.completed)
        print(f"\nDatabase summary for '{username}':")
        print(f"  Total tasks  : {total}")
        print(f"  Completed    : {completed}")
        print(f"  Pending      : {total - completed}")
        print(f"  Overdue      : {overdue}")
        print(f"  High priority: {high}")


if __name__ == "__main__":
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else "demo"
    seed(username)
    print(f"\nDone! Log in at http://localhost:5000 with username='{username}' password='demo123'")
