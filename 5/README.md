# TaskMind — AI-Powered Intelligent Task Manager

TaskMind is a full-stack web application that combines natural language processing and machine learning to help you manage tasks intelligently. It parses plain-English task descriptions, calculates AI-driven priority scores, and recommends what to work on next.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [How to Use](#how-to-use)
- [AI & NLP Explained](#ai--nlp-explained)
- [API Reference](#api-reference)
- [Demo Account](#demo-account)
- [Seeding a Full Year of Data](#seeding-a-full-year-of-data)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Natural Language Task Input** — Type tasks like *"Submit report by Friday 5pm, high priority, 2 hours"* and the app extracts the title, due date, time, priority, and effort automatically.
- **AI Priority Scoring** — Every task gets a score (0–100%) computed from importance, deadline proximity, and effort using the Enhanced Eisenhower Matrix formula.
- **"Do Next" Recommendation** — A prominent card on the dashboard always shows which task you should work on right now, explained in plain English.
- **Smart Rescheduling** — When you complete a task, the app detects overdue tasks and offers to reschedule them with one click.
- **Live Dashboard** — Stats (Total, Completed, Pending, Overdue) and a 7-day productivity chart update instantly without page reloads.
- **User Authentication** — Secure registration and login with bcrypt-hashed passwords.
- **Statistics Page** — Completion rate, weekly comparison, average effort, and most productive day.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite (via Flask-SQLAlchemy) |
| NLP | spaCy (`en_core_web_sm`) |
| ML / Math | scikit-learn, NumPy |
| Auth | Flask-Bcrypt |
| Frontend | Bootstrap 5, Chart.js, Font Awesome |
| Language | Vanilla JavaScript (no framework) |

---

## Project Structure

```
taskmind/
├── app.py                  # Main Flask application (routes, models, NLP, AI logic)
├── seed_data.py            # Flood an account with a full year of realistic task data
├── requirements.txt        # Python dependencies
├── setup.sh                # One-command setup script
├── README.md               # This file
├── instance/
│   └── taskmind.db         # SQLite database (auto-created on first run)
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles, animations, color scheme
│   └── js/
│       └── app.js          # Frontend logic (rendering, modals, API calls)
└── templates/
    ├── base.html           # Shared layout (navbar, toasts, JS imports)
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── dashboard.html      # Main dashboard
    └── profile.html        # Statistics & change password
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip

### Steps

**1. Clone or download the project folder, then navigate into it:**

```bash
cd taskmind
```

**2. (Recommended) Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

Or use the setup script which does everything in one go:

```bash
bash setup.sh
```

**4. Download the spaCy language model:**

```bash
python -m spacy download en_core_web_sm
```

> Skip this step if you used `setup.sh` — it handles it automatically.

---

## Running the App

```bash
python app.py
```

The server starts at **http://localhost:5000**. Open it in your browser.

The SQLite database (`instance/taskmind.db`) is created automatically on first run. No database setup is required.

All styles and scripts (Bootstrap, Font Awesome, Chart.js) are bundled
in `static/vendor/`, so the app runs without any internet connection.
The spaCy language model is optional — without it, parsing falls back
to the built-in regex engine automatically.

### Terminal client

Every feature of the website also works from the terminal:

```bash
python cli.py
```

Menu-driven: login/register, add tasks in plain English (same AI
parsing and priority scoring), list/complete/reschedule/delete tasks,
"what should I do next?" recommendations, stats and password change.
It runs the same application code against the same database as the
website — no server or network needed.

---

## How to Use

### 1. Register an Account

Go to `/register`, enter a username, email, and password. Six demo tasks are seeded automatically when you register so you can explore the app immediately.

### 2. Dashboard

After logging in you'll see:

- **Do Next card** (top left, blue gradient) — the single most important task to work on right now.
- **Stats cards** — live counts of Total, Completed, Pending, and Overdue tasks.
- **Productivity chart** — bar chart of tasks completed each day over the last 7 days.
- **Natural language input box** — type a task description and press Enter or click Parse.
- **Task list** — all your tasks with filters (All / Pending / Completed / Overdue).

### 3. Adding a Task with Natural Language

Type in the input box using plain English. Examples:

```
Submit quarterly report by Friday 5pm, high priority, 2 hours
Call dentist tomorrow, 15 minutes
Read AI paper next week, low priority, 3 hours
Buy groceries Saturday, 45 min
Fix production bug ASAP, urgent
```

Click **Parse** (or press Enter). A confirmation modal appears showing what the AI extracted — you can edit any field before saving.

### 4. Adding a Task Manually

Click **Add Manually** (top right of the task list) to open a form where you fill in all fields directly.

### 5. Completing a Task

Click the circular checkbox on the left of any task. It fills green and the task is marked complete. If there are overdue tasks, a toast notification appears offering to reschedule one to tomorrow.

### 6. Editing or Deleting a Task

Click the **⋮** menu on the right of any task card and choose Edit or Delete.

### 7. Statistics Page

Click **Statistics** in the navbar to see:

- Overall completion rate
- Tasks completed this week vs. last week
- Average effort per completed task
- Your most productive day of the week
- Password change form

---

## AI & NLP Explained

### Natural Language Parsing (spaCy + Regex)

When you type a task, the app uses a combination of spaCy NLP and regular expressions to extract:

| What | Example input | Extracted |
|---|---|---|
| Due date | "by Friday", "tomorrow", "next week" | ISO date |
| Due time | "5pm", "2:30pm" | HH:MM |
| Importance | "high priority", "urgent", "ASAP" | 3 (High) |
| Effort | "2 hours", "45 minutes" | minutes |
| Title | everything else after stripping the above | clean string |

### Priority Score Formula (Enhanced Eisenhower Matrix)

Every task is scored 0–100% using:

```
P_score = (I × 0.35) + (U × 0.30) + (D_f × 0.25) + (E_f × 0.10)
```

Where:

| Variable | Meaning | Formula |
|---|---|---|
| `I` | Importance | 3 = High, 2 = Medium, 1 = Low |
| `U` | Urgency (deadline) | `1 / (1 + days_to_deadline)` |
| `D_f` | Deadline decay factor | `e^(−days / 3)` |
| `E_f` | Effort factor (quick tasks score higher) | `1 / (1 + effort_minutes / 60)` |

The raw score is normalised against the theoretical maximum (~1.70), then mapped:

- **High** → score > 70%
- **Medium** → score 40–70%
- **Low** → score < 40%

### "Do Next" Recommendation Formula

The recommendation score adds urgency and personal productivity pattern on top of priority:

```
R_score = (P_score × 0.4) + (U_norm × 0.3) + (M_personal × 0.3)
```

Where `M_personal` favours tasks due in the morning (a simple proxy for when most people are most focused). The task with the highest R_score is shown in the Do Next card.

---

## API Reference

All endpoints require a logged-in session (cookie-based).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/parse` | Parse natural language text. Body: `{"text": "..."}` |
| `POST` | `/api/tasks` | Create a task. Body: see fields below |
| `PUT` | `/api/tasks/<id>` | Update a task (any subset of fields) |
| `DELETE` | `/api/tasks/<id>` | Delete a task |
| `POST` | `/api/tasks/<id>/reschedule` | Set a new due date. Body: `{"new_date": "YYYY-MM-DD"}` |

**Task fields (create / update):**

```json
{
  "title": "string",
  "description": "string",
  "due_date": "YYYY-MM-DD",
  "due_time": "HH:MM",
  "importance": 1,
  "effort_minutes": 30
}
```

**Parse response example:**

```json
{
  "title": "Submit report",
  "due_date": "2026-06-26",
  "due_time": "17:00",
  "importance": 3,
  "effort_minutes": 120,
  "priority_label": "High",
  "priority_score": 0.83,
  "priority_pct": 83
}
```

---

## Demo Account

When you register any new account, six demo tasks are automatically created:

| Task | Due | Priority | Effort |
|---|---|---|---|
| Submit quarterly report | Friday 5pm | High | 2 hours |
| Review project proposal | Tomorrow 2pm | High | 1 hour |
| Buy groceries | Saturday | Medium | 45 min |
| Call dentist | Next Monday | Medium | 15 min |
| Read AI paper | Next week | Low | 3 hours |
| Team meeting prep | Yesterday *(overdue)* | High | 30 min |

---

## Seeding a Full Year of Data

The `seed_data.py` script floods your account with **99 realistic hardcoded tasks** spanning a full year — completed history, today's work, upcoming deadlines, and long-horizon goals. It's useful for exploring the dashboard with real-looking data instead of starting from scratch.

### What gets seeded

| Category | Count | Details |
|---|---|---|
| Completed (with timestamps) | 42 | Tasks going back 180 days — reports, deploys, bug fixes, meetings |
| Overdue (not done) | 4 | Unpaid invoice, expired domain, unanswered emails |
| Due today | 5 | Standup call, CI failures, code review, Jira update |
| Upcoming (next 14 days) | 28 | Sprint work, features, calls, hiring |
| Future (2 weeks – 1 year) | 20 | Fundraising, product launches, certifications, retreats |

Completed tasks have realistic `completed_at` timestamps so the **7-day productivity chart** shows actual bars, the **completion rate** on the Statistics page reflects real history, and the **Most Productive Day** calculation has data to work with.

### How to run it

Make sure the app has been run at least once (so the database exists), then:

```bash
python seed_data.py demo
```

Replace `demo` with any registered username:

```bash
python seed_data.py your_username
```

If the username doesn't exist yet, the script creates it automatically with password `demo123`.

You can run it multiple times safely — it clears the previous seeded tasks before re-inserting, so you won't get duplicates.

### Example output

```
Seeded 98 tasks for user 'demo'.

Database summary for 'demo':
  Total tasks  : 99
  Completed    : 42
  Pending      : 57
  Overdue      : 4
  High priority: 12

Done! Log in at http://localhost:5000 with username='demo' password='demo123'
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'spacy'`**
Run `pip install spacy` then `python -m spacy download en_core_web_sm`.

**`OSError: [E050] Can't find model 'en_core_web_sm'`**
Run `python -m spacy download en_core_web_sm`. The app works without it (falls back to regex-only parsing) but spaCy improves date entity recognition.

**Port 5000 already in use**
Either stop the other process or start on a different port:
```bash
flask run --port 5001
```

**Database errors / fresh start**
Delete `instance/taskmind.db` and restart the app. The database will be recreated automatically.

**Tasks not appearing after login**
Hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R) to clear any cached JavaScript.
