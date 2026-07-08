# Student Study Planner and Time Management System

> **Author:** Nwachukwu Chibuzor Benjamin
> **Matric Number:** 22/9799
> **Department:** Computer Science, Caleb University, Lagos
> **Project Type:** Final Year Project

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Installation Guide](#installation-guide)
6. [Running the Application](#running-the-application)
7. [Demo Account and Seed Data](#demo-account-and-seed-data)
8. [API Reference](#api-reference)
9. [Feature Walkthrough](#feature-walkthrough)
10. [Neurodiversity Support](#neurodiversity-support)
11. [Adaptive Learning Engine](#adaptive-learning-engine)
12. [Semantic Search](#semantic-search)
13. [Troubleshooting](#troubleshooting)
14. [Dependencies](#dependencies)

---

## Project Overview

The **Student Study Planner and Time Management System** is a full-stack web application designed to help university students organise their academic workload. It combines classical task management with an adaptive learning engine that personalises study recommendations based on each student's behaviour patterns.

The system includes special support for **neurodiverse learners** — students with ADHD or ASD — through customisable interface modes, adjusted Pomodoro intervals, and structured workflow layouts.

The interface uses **Font Awesome 6** icons throughout (no emojis), a full **dark mode**, and a fully **responsive layout** for desktop, tablet, and mobile.

---

## Features

| # | Feature | Description |
|---|---|---|
| 1 | **User Authentication** | Register, login, logout with secure password hashing (PBKDF2) |
| 2 | **Task Management** | Create, edit, delete, and filter academic tasks with priority levels |
| 3 | **Study Schedule** | Interactive weekly calendar with colour-coded time blocks |
| 4 | **Deadline Management** | Due date tracking with overdue detection and in-app reminders |
| 5 | **Progress Tracking** | Log study sessions and monitor daily/weekly study hours |
| 6 | **Analytics Dashboard** | Charts for task completion, study hours, subject distribution, and trends |
| 7 | **Adaptive Engine** | Personalised study tips and Pomodoro settings based on completion patterns |
| 8 | **Semantic Search** | Search tasks by meaning using vector embeddings (keyword fallback included) |
| 9 | **Neurodiversity Support** | ASD/ADHD-friendly interface modes with customisable accessibility options |
| 10 | **Goal Setting** | Create and track academic goals with visual progress bars |
| 11 | **Dark Mode** | Full dark theme toggle (respects system preference on first load) |
| 12 | **Responsive Design** | Works on desktop, tablet, and mobile with off-canvas sidebar |

---

## Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| HTML5 | Semantic page structure with ARIA accessibility attributes |
| CSS3 (Grid + Flexbox) | Layout, responsive design, dark mode, neuro-profile overrides |
| JavaScript ES6+ | Application logic, API communication, SPA router |
| Chart.js 4.4 | Analytics charts — doughnut, bar, pie, line |
| Font Awesome 6.5 | Icon library (replaces all emojis in the interface) |

### Backend

| Technology | Purpose |
|---|---|
| Python 3.9+ | Server-side language |
| Flask 3 | Web framework and REST API |
| Flask-CORS | Cross-origin request handling |
| Werkzeug | Password hashing (PBKDF2-SHA256) |
| SQLite3 | Relational database (built into Python, no separate server needed) |

### Optional — Semantic Search

| Technology | Purpose |
|---|---|
| sentence-transformers | Generate text embeddings for semantic similarity |
| chromadb | Persistent vector database for storing and querying embeddings |

---

## Project Structure

```
project-root/
│
├── backend/
│   ├── app.py                   # Flask entry point — registers all blueprints
│   ├── config.py                # Configuration (secret key, DB path, CORS)
│   ├── seed.py                  # Demo data loader — 7 months of realistic data
│   │
│   ├── models/
│   │   ├── user.py              # User model, session/token management
│   │   ├── task.py              # Task CRUD and queries
│   │   ├── schedule.py          # Study block model
│   │   └── progress.py          # Study logs and academic goals
│   │
│   ├── services/
│   │   ├── adaptive_engine.py   # Personalised recommendations engine
│   │   ├── semantic_search.py   # Vector search (Chroma) with keyword fallback
│   │   ├── reminder_service.py  # In-app reminder generation and storage
│   │   └── analytics_service.py # Aggregated dashboard statistics
│   │
│   ├── routes/
│   │   ├── auth_routes.py       # /api/auth/* — register, login, logout, profile
│   │   ├── task_routes.py       # /api/tasks/* — CRUD + search + reminders
│   │   ├── schedule_routes.py   # /api/schedule/* + /api/progress/* + /api/goals/*
│   │   └── analytics_routes.py  # /api/analytics/* — dashboard + recommendations
│   │
│   ├── utils/
│   │   ├── helpers.py           # Auth decorator, response helpers, pagination
│   │   └── validators.py        # Input validation functions
│   │
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── index.html               # Single-page application shell
│   │
│   ├── css/
│   │   ├── style.css            # Main styles and CSS design tokens
│   │   ├── dark-mode.css        # Dark theme variable overrides
│   │   └── responsive.css       # Mobile breakpoints and print styles
│   │
│   └── js/
│       ├── app.js               # Bootstrap, global state, API helper, SPA router
│       ├── auth.js              # Login, register, logout
│       ├── tasks.js             # Task CRUD, filters, Font Awesome icon rendering
│       ├── schedule.js          # Weekly calendar planner
│       ├── progress.js          # Session logging and goals
│       ├── analytics.js         # Chart.js dashboard and summary cards
│       ├── adaptive.js          # Recommendations UI
│       ├── search.js            # Global semantic search bar (Ctrl+K)
│       └── ui.js                # Modals, toasts, settings, reminders
│
└── data/
    └── study_planner.db         # SQLite database (auto-created on first run)
```

---

## Installation Guide

### Prerequisites

- Python 3.9 or higher
- A modern web browser (Chrome, Firefox, Edge)
- pip (Python package manager)

### Step 1 — Navigate to the project folder

```bash
cd /path/to/project-root
```

### Step 2 — Install Python dependencies

**Minimal install** (no semantic search — recommended for first run):
```bash
cd backend
pip install flask flask-cors werkzeug
```

**Full install** (includes semantic vector search):
```bash
cd backend
pip install -r requirements.txt
```

> `sentence-transformers` and `chromadb` are large packages (~1 GB). If skipped, the search feature automatically falls back to fast keyword matching with no configuration needed.

### Step 3 — (Optional) Use a virtual environment

```bash
python -m venv venv

# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install flask flask-cors werkzeug
```

---

## Running the Application

### 1. Start the backend server

```bash
cd backend

```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

The SQLite database (`data/study_planner.db`) is created automatically on first run.

### 2. Serve the frontend

Open a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Open your browser at:
```
http://localhost:5500
```

> **Why a server instead of opening the file directly?** Browsers block `fetch()` calls when HTML is opened via `file://`. Serving via `python -m http.server` avoids this restriction.

---

## Demo Account and Seed Data

The project includes a seed script that populates the database with **7 months of realistic academic data** so every page and chart loads with meaningful content immediately.

### Load the demo data

```bash
cd backend
python seed.py
```

### What gets created

| Data type | Count | Description |
|---|---|---|
| Tasks — completed | 130 | Spread across 7 months with realistic completion dates |
| Tasks — in progress | 15 | Currently active tasks |
| Tasks — pending | 40 | Future deadlines up to 60 days ahead |
| Tasks — overdue | 8 | Missed deadlines for testingpython app.py overdue detection |
| Tasks — urgent | 5 | Due within 48 hours |
| Study log sessions | ~320 | Daily study sessions over 7 months across all subjects |
| Schedule blocks | ~80 | Colour-coded blocks across 6 weeks (past 4 + next 2) |
| Academic goals | 6 | Mix of active and achieved goals with progress values |

### Demo login credentials

```
Email    : demo@calebuniversity.edu.ng
Password : Demo1234
```

### Reset and reload data

```bash
# From the project root
rm data/study_planner.db
cd backend && python seed.py
```

---

## API Reference

All endpoints are prefixed with `/api`. Authentication uses the `X-Auth-Token` request header returned on login/register.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Log in, receive session token |
| POST | `/auth/logout` | Invalidate session token |
| GET | `/auth/me` | Get current user profile |
| PUT | `/auth/profile` | Update profile and accessibility settings |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tasks` | List tasks (supports `?status=`, `?priority=`, `?subject=`, `?due_before=`, `?due_after=`) |
| POST | `/tasks` | Create a new task |
| GET | `/tasks/<id>` | Get a single task |
| PUT | `/tasks/<id>` | Update a task |
| DELETE | `/tasks/<id>` | Delete a task |
| GET | `/tasks/search?q=<query>` | Semantic search across tasks |

### Schedule

| Method | Endpoint | Description |
|---|---|---|
| GET | `/schedule?week=YYYY-MM-DD` | Get blocks for a week (Monday date) |
| GET | `/schedule/today` | Get today's blocks only |
| POST | `/schedule` | Create a study block |
| PUT | `/schedule/<id>` | Update a block |
| DELETE | `/schedule/<id>` | Delete a block |

### Progress and Goals

| Method | Endpoint | Description |
|---|---|---|
| POST | `/progress/log` | Log a study session |
| GET | `/progress/logs` | Get session history (supports `?start=`, `?end=`) |
| GET | `/goals` | List goals (supports `?status=active\|achieved`) |
| POST | `/goals` | Create a goal |
| PUT | `/goals/<id>` | Update goal (use `current_value` to log progress) |
| DELETE | `/goals/<id>` | Delete a goal |

### Analytics and Recommendations

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/dashboard` | Full stats for all dashboard charts |
| GET | `/analytics/recommendations` | Adaptive engine output |
| POST | `/analytics/reindex` | Rebuild the semantic search vector index |

### Reminders

| Method | Endpoint | Description |
|---|---|---|
| GET | `/reminders` | List all reminders |
| GET | `/reminders?unread=true` | Unread reminders only |
| POST | `/reminders/read` | Mark reminders as read (body: `{"ids": [1, 2, 3]}`) |
| GET | `/reminders/count` | Get unread reminder count |

---

## Feature Walkthrough

### Tasks

- Click **New Task** (top right of the Tasks page) to open the task form
- Set a title, subject/course code, priority (Low / Medium / High / Urgent), due date, and estimated time in minutes
- Add comma-separated tags such as `exam, revision, project` for organisation
- Filter tasks using the chips: All, Pending, In Progress, Completed, Overdue, Urgent
- Tick the checkbox on any task to mark it complete instantly — the system records the completion timestamp
- Use the pen icon to edit a task or the bin icon to delete it
- Task actions appear on hover (always visible on mobile/touch)

### Schedule

- The weekly calendar shows 08:00–22:00 for each day of the week
- Click any empty time cell to create a block starting at that hour
- Block types are colour-coded: Study (blue), Break (green), Review (amber), Exam (red)
- Use **Prev / Next** to navigate between weeks; **Today** returns to the current week
- Today's blocks are also listed as a quick-reference panel below the calendar

### Progress Tracker

- Log study sessions with subject, duration in minutes, and an optional note
- Create academic goals with a target metric: tasks completed, study hours, or score/grade
- Click **Log Progress** on any goal to add an increment — goals auto-mark as achieved when the target is reached
- Recent session history shows the last 20 entries

### Analytics

All charts update live on page load:

| Chart | Type | Description |
|---|---|---|
| Study Hours — Last 7 Days | Bar | Daily study hours for the current week |
| Tasks by Priority | Bar | Count of tasks at each priority level |
| Subject Distribution | Pie | Task count spread across courses |
| Completion Trend | Line | Daily completed tasks over the last 14 days |
| Task Status Overview | Doughnut | Completed / In Progress / Pending / Overdue |

---

## Neurodiversity Support

Configure your profile in **Settings → Neuro Profile**.

### Standard
- Pomodoro: **25 min work / 5 min break / 15 min long break**
- Normal reminder frequency

### ADHD-friendly
- Pomodoro: **15 min work / 5 min break / 10 min long break**
- Frequent reminders
- Tips focused on short focus sprints, visible task lists, and movement breaks
- Task breakdown suggestions for any task over 60 minutes estimated

### ASD-friendly
- Pomodoro: **30 min work / 10 min break / 20 min long break**
- Structured, predictable reminders
- Tips focused on consistent daily routines and scheduling buffer slots
- Emphasis on predictable workflows and reduced ambiguity

### Additional accessibility settings

| Setting | Effect |
|---|---|
| **Font Size** | Small / Medium / Large — adjusts base font size across the whole app |
| **High Contrast** | Black background, white text, high-contrast borders |
| **Simplified View** | Hides badges, tag lists, and decorative elements to reduce visual noise |
| **Dark Mode** | Full dark theme via the sun/moon toggle in the top bar |

All interactive elements include ARIA labels, keyboard navigation, and focus trapping inside modals. The search bar is accessible via **Ctrl+K** keyboard shortcut.

---

## Adaptive Learning Engine

Located in `backend/services/adaptive_engine.py`. Runs on each visit to the **Recommendations** page.

### What it analyses

| Signal | How it is used |
|---|---|
| Task completion rate | Determines overall productivity level and tone of tips |
| Study log timestamps | Identifies peak study hours across last 30 days |
| Subject breakdown | Finds subjects with lowest completion rates |
| Estimated vs actual time | Detects tasks being under/over-estimated |
| Tasks due within 48 hours | Generates the urgent task alert panel |
| Estimated minutes per task | Flags tasks over 60 minutes for breakdown suggestions |

### What it outputs

- Personalised text tips (adjusted vocabulary and focus for neuro profile)
- Recommended Pomodoro work/break intervals
- Urgent task list with due times
- Step-by-step subtask suggestions for complex tasks
- Per-subject completion rate progress bars

---

## Semantic Search

The search bar (top of every page, shortcut **Ctrl+K**) supports natural language queries.

### How it works

1. **Primary path** — `sentence-transformers` encodes both the query and all task text into vector embeddings. `chromadb` finds the most similar tasks by cosine similarity and returns a ranked list with match percentages.

2. **Automatic fallback** — if the ML libraries are not installed, a TF-IDF-style keyword search runs automatically. No configuration is needed; the switch is transparent to the user.

### Triggering a search

Type in the search bar and results appear after a 400 ms debounce. Clicking a result navigates to the Tasks page and scrolls to and highlights the matching task. Press **Escape** to close results.

### Rebuilding the index

After importing or bulk-editing tasks outside the app, rebuild the index:

```
POST /api/analytics/reindex
```

---

## Troubleshooting

**Backend does not start**

Make sure you are running from inside the `backend/` directory and that Flask is installed:
```bash
cd backend
pip install flask flask-cors werkzeug
python app.py
```

**"Failed to fetch" or CORS error in the browser**

Open `backend/config.py` and add your frontend URL to the `CORS_ORIGINS` list:
```python
CORS_ORIGINS = ["http://localhost:5500", "http://127.0.0.1:5500", "null"]
```
Restart the backend after saving.

**Database error on first run**

The `data/` directory must exist. Create it manually if needed:
```bash
mkdir -p data
```

**Charts do not render**

Chart.js is loaded from a CDN. Check your internet connection, or open the browser DevTools console (F12) for specific error messages.

**Semantic search returns no results**

This is expected if sentence-transformers is not installed — the system falls back to keyword matching automatically. To enable full vector search:
```bash
pip install sentence-transformers chromadb
```
Then trigger a reindex via `POST /api/analytics/reindex`.

**Seed script fails with an existing database**

Delete the old database and re-run:
```bash
rm data/study_planner.db
cd backend && python seed.py
```

---

## Dependencies

### Python — `backend/requirements.txt`

```
flask==3.0.3
flask-cors==4.0.1
werkzeug==3.0.3

# Optional — semantic search (comment out if not needed)
sentence-transformers==2.7.0
chromadb==0.5.0
numpy==1.26.4
```

### Frontend — CDN (no installation required)

| Library | Version | Purpose |
|---|---|---|
| Chart.js | 4.4.2 | Analytics charts |
| Font Awesome | 6.5.1 | Icon library (used in place of emojis throughout the UI) |

---

## Academic Declaration

This project was developed as a final year project submission for the Bachelor of Science degree in Computer Science at Caleb University, Lagos.

| Field | Detail |
|---|---|
| Student | Nwachukwu Chibuzor Benjamin |
| Matric Number | 22/9799 |
| Department | Computer Science |
| Institution | Caleb University, Lagos |
| Academic Session | 2023/2024 |

Email    : demo@calebuniversity.edu.ng
Password : Demo1234
