# Project Archive

A collection of nine independent, self-contained software projects.
Each lives in its own numbered folder, has its own README with full
setup instructions, runs **fully offline** (all styles/scripts are
bundled locally, no CDNs or external APIs), and ships a **terminal
client** with the same functionality as its web interface.

The projects are not linked to each other in any way — any folder can
be copied out and used on its own.

---

## The Projects

| # | Project | What it is | Tech | Web UI | Terminal |
|---|---------|-----------|------|--------|----------|
| [1](1/complaint-desk/) | **ComplaintDesk** | University complaint management system (students/staff submit and track complaints; admins triage, respond, report) | Flask + SQLite, HTML/CSS/JS | `python backend/app.py` → :5000 | `python backend/cli.py` |
| [2](2/) | **PhishGuard AI** | Machine-learning phishing URL detection and prevention (32 lexical features, gradient boosting) | FastAPI + SQLite, scikit-learn | `uvicorn main:app` (from `backend/`) → :8000 | `python backend/cli.py` |
| [3 (2)](3%20(2)/) | **Personal Health Monitor** | Mobile app for logging and visualising daily health vitals, with on-device persistence | React Native (Expo), AsyncStorage | `npx expo start` | `node cli.js` |
| [4](4/) | **SentinelIQ** | Credit-card fraud detection: trained model, scoring API, live analytics dashboard | Flask + SQLite, scikit-learn, Chart.js | `python app.py` → :5004 | `python cli.py` |
| [5](5/) | **TaskMind** | AI task manager: plain-English task entry (NLP), priority scoring, "do next" recommendations | Flask + SQLite, spaCy (optional) | `python app.py` → :5000 | `python cli.py` |
| [6](6/) | **Lush Hair NG Resume Screener** | Automated resume screening: parsing (PDF/DOCX), skill matching, geospatial proximity, multi-criteria ranking, Excel export | FastAPI + SQLite, spaCy (optional) | `python main.py` → :8000 | `python cli.py` |
| [7](7/) | **Student Study Planner** | Study planning and time management: tasks, schedule, progress logs, goals, analytics, adaptive recommendations | Flask + SQLite, vanilla JS frontend | backend :5000 + `python -m http.server 5500` in `frontend/` | `python backend/cli.py` |
| [8](8/) | **Network Congestion Simulation** | Discrete-event simulator for urban telecom networks (Poisson traffic, FIFO queues, M/M/1 validation) with a web control panel | Python (simpy/numpy/matplotlib), Flask | `python app.py` → :5000 | `python main.py` |
| [9](9/) | **SRMS** | Student Record Management System: students, courses, grades/GPA, attendance, fees, reports, audit log — plus a script pipeline that generates the project report | PHP 8 + MySQL, Bootstrap | Apache/`php -S` + MySQL | `php srms/cli.php` |

Each project folder's own README covers installation, configuration,
usage, API reference and the terminal client in detail.

## Conventions shared by all projects

- **Offline-first** — vendored copies of Bootstrap, Chart.js,
  Font Awesome, jQuery, DataTables etc. live inside each project
  (`vendor/` / `static/vendor/` / `assets/vendor/`). No internet is
  required to run any of them; optional online extras (spaCy model
  downloads, OpenStreetMap geocoding) degrade gracefully when offline.
- **Terminal parity** — every project's CLI drives the same
  application code and database as its website, so work done in the
  terminal shows up in the browser and vice versa.
- **Python projects** — create a virtualenv inside the project folder
  and `pip install -r requirements.txt` there; nothing is shared
  between projects.

## Repository layout notes

- `project/` contains **earlier prototype versions** of projects 1–3,
  kept for reference only (see `project/README.md`). The top-level
  numbered folders hold the finished versions.
- Pre-seeded SQLite databases are committed where a project's README
  documents demo data; they are regenerated automatically if deleted.
