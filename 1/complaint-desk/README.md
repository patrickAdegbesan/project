# ComplaintDesk — Online Complaint Management System

**Caleb University, Lagos**
Bachelor of Science (B.Sc.) Computer Science — Final Year Project

| | |
|---|---|
| **Author** | Danbaba George |
| **Matric No.** | 22/10444 |
| **Supervisor** | Dr. Ayorinde Oduroye Peters |
| **Department** | Computer Science |
| **Session** | 2024/2025 |

---

## Overview

ComplaintDesk is a full-stack web application that gives Caleb University students and staff a streamlined, transparent channel to submit, track, and resolve complaints. All data is stored in a real database — no hardcoded content anywhere in the system.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Pure HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3 — Flask REST API |
| Database | SQLite 3 (via Python `sqlite3` module) |
| Auth | Flask `session` + `werkzeug.security` (bcrypt hashing) |
| CORS | `flask-cors` |

---

## Project Structure

```
complaint-desk/
├── index.html                  # Screen index / design overview
├── 01-login.html               # Login page (all roles)
├── 02-register.html            # Account registration
├── 03-user-dashboard.html      # Student dashboard
├── 04-submit-complaint.html    # Submit a new complaint
├── 05-my-complaints.html       # Student — view own complaints
├── 06-complaint-detail.html    # Complaint detail + message thread
├── 07-admin-dashboard.html     # Admin KPI dashboard
├── 08-admin-all-complaints.html# Admin — all complaints table
├── 11-admin-users.html         # Admin — user management
├── 12-admin-reports.html       # Admin — analytics & reports
├── 13-profile-settings.html    # Profile & password settings
├── admin-announcements.html    # Admin — create/manage announcements
├── admin-settings.html         # System settings
├── admin-help.html             # Admin help center
├── staff-dashboard.html        # Staff dashboard
├── css/
│   └── styles.css              # Global design system stylesheet
├── js/
│   ├── api.js                  # Shared API client (all pages import this)
│   └── app.js                  # Legacy app utilities
├── img/
│   ├── logo.svg                # Full logo (light)
│   ├── logo-dark.svg           # Full logo (dark sidebar)
│   └── logo-icon.svg           # Icon-only logo (favicons, topbar)
└── backend/
    ├── app.py                  # Flask application — all API routes
    ├── schema.sql              # SQLite schema + seed data
    ├── complaintdesk.db        # SQLite database file (auto-created)
    └── run.sh                  # Convenience start script
```

---

## Installation & Setup

### Requirements

- Python 3.8 or higher
- pip

### 1. Install dependencies

```bash
pip install flask flask-cors werkzeug
```

### 2. Start the server

```bash
cd complaint-desk/backend
python app.py
```

Or using the shell script:

```bash
cd complaint-desk/backend
bash run.sh
```

The server will:
1. Create the SQLite database automatically from `schema.sql` (first run only)
2. Seed the default accounts with real password hashes
3. Start listening at `http://127.0.0.1:5000`

### 3. Open the application

Open your browser and go to:

```
http://127.0.0.1:5000
```

> **Important:** Always access the app via `http://127.0.0.1:5000`, not by opening HTML files directly with `file://`. Direct file opening breaks all API calls since there is no server to handle them.

---

## Default Accounts

The database is seeded with three default accounts on first run:

| Role | Email | Password |
|---|---|---|
| Administrator | `administrator@caleb.edu.ng` | `Admin@1234` |
| Staff | `c.okafor@caleb.edu.ng` | `Staff@1234` |
| Student | `a.nwosu@student.caleb.edu.ng` | `Student@1234` |

New accounts can be registered at `http://127.0.0.1:5000/02-register.html`.

---

## Features

### Student Portal
- Register an account and log in securely
- Submit complaints with title, category, priority level, and optional anonymous flag
- Each complaint gets a unique reference number (format: `CD-XXXX-NNNN`)
- View all personal complaints with live status tracking
- Open any complaint to read the full message thread and reply to staff responses
- View announcements targeted to students
- Update profile name, phone number, and password

### Staff Portal
- Log in to a dedicated staff dashboard
- View complaints assigned to them
- Add responses to complaint threads
- View announcements targeted to staff

### Admin Panel
- **Dashboard** — live KPIs: total complaints, open, resolved, urgent count, and total users
- **All Complaints** — searchable, filterable table with status and priority filters
- **Complaint Management** — update status, priority, and assigned staff on any complaint
- **Users** — view all users, filter by role, search by name/email, suspend/activate accounts
- **Reports** — analytics by category, status, priority, department; bar chart of monthly volume; average resolution time
- **Announcements** — create, edit, publish, draft, pin, and delete announcements; target by role (all / students / staff)
- **Settings** — system configuration saved to the database

---

## Database Schema

### Tables

**`users`** — all system accounts (students, staff, admins)

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| name | TEXT | Full name |
| email | TEXT | Unique, used for login |
| password | TEXT | Bcrypt hash via werkzeug |
| role | TEXT | `student` / `staff` / `admin` |
| department | TEXT | Faculty or unit |
| matric_no | TEXT | Students only |
| staff_id | TEXT | Staff only |
| phone | TEXT | Optional contact |
| is_active | INTEGER | 1 = active, 0 = suspended |
| created_at | TEXT | ISO datetime |

**`categories`** — complaint categories (seeded with 10 default categories)

**`complaints`** — the core table

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| ref_no | TEXT | Unique, format `CD-XXXX-NNNN` |
| title | TEXT | Short complaint title |
| description | TEXT | Full detail |
| category_id | INTEGER | FK → categories |
| priority | TEXT | `low` / `medium` / `high` / `urgent` |
| status | TEXT | `open` / `in_progress` / `resolved` / `closed` / `rejected` |
| user_id | INTEGER | FK → users (submitter) |
| assigned_to | INTEGER | FK → users (staff handler) |
| is_anonymous | INTEGER | 1 = submitter identity hidden |
| created_at / updated_at / resolved_at | TEXT | ISO datetimes |

**`responses`** — message thread entries per complaint

**`announcements`** — system-wide notices with targeting, pinning, and draft support

---

## API Reference

All endpoints are served from the Flask app at `http://127.0.0.1:5000`.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create a new account |
| POST | `/api/auth/login` | Login; returns `{user, redirect, message}` |
| POST | `/api/auth/logout` | End session |
| GET | `/api/auth/me` | Get current session user (401 if not logged in) |
| POST | `/api/auth/change-password` | Change own password |
| POST | `/api/auth/update-profile` | Update own name and phone |

### Complaints (Student / Staff)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/complaints` | List own complaints (filterable by status, search) |
| POST | `/api/complaints` | Submit a new complaint |
| GET | `/api/complaints/<id>` | Get complaint detail + response thread |
| POST | `/api/complaints/<id>/respond` | Add a message to the thread |
| GET | `/api/user/stats` | Own stats: total, open, in progress, resolved |

### Admin — Complaints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/complaints` | All complaints (filterable by status, priority, search) |
| PUT | `/api/admin/complaints/<id>` | Update status, priority, assigned staff |

### Admin — Users

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/users` | List all users (filterable by role, search) |
| POST | `/api/admin/users` | Create a user account |
| GET | `/api/admin/users/<id>` | Get a single user |
| PUT | `/api/admin/users/<id>` | Update user (name, role, is_active) |

### Admin — Stats & Reports

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/stats` | KPIs + by-category breakdown + recent complaints |
| GET | `/api/admin/reports?period=30` | Full analytics report (default: 30-day window) |

### Announcements

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/announcements` | Announcements for the current user's role |
| GET | `/api/admin/announcements` | All announcements (admin view) |
| POST | `/api/admin/announcements` | Create announcement |
| PUT | `/api/admin/announcements/<id>` | Update / publish draft / pin |
| DELETE | `/api/admin/announcements/<id>` | Delete announcement |

### Other

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/categories` | List all active complaint categories (public) |
| GET | `/api/admin/settings` | Load system settings |
| POST | `/api/admin/settings` | Save system settings |

---

## Access Control

Every protected API endpoint checks the session using decorators:

- `@login_required` — any authenticated user
- `@role_required('admin')` — admin only
- `@role_required('admin', 'staff')` — admin or staff

On the frontend, every page calls `requireAuth(expectedRole)` on load (defined in `js/api.js`). If the session has expired or the user has the wrong role, they are immediately redirected to the login page.

Role colour coding across the UI:

| Role | Colour |
|---|---|
| Student | Blue `#1a73e8` |
| Staff | Green `#34a853` |
| Admin | Red `#ea4335` |

---

## Running in Production

This project is configured for local development. Before deploying:

1. Replace `app.secret_key` with a long random string stored in an environment variable
2. Set `SESSION_COOKIE_SECURE = True` and serve over HTTPS
3. Replace the development Flask server with a production WSGI server (e.g. Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
4. Consider PostgreSQL or MySQL instead of SQLite for concurrent multi-user access

---

## Complaint Reference Number Format

Each complaint is assigned a unique reference number at submission time:

```
CD-XKQR-7291
│   │    └── 4 random digits
│   └────── 4 random uppercase letters
└────────── "CD" prefix (ComplaintDesk)
```

Generated by `gen_ref()` in `backend/app.py`. Collisions are checked against the database before assignment.

---

## Seeded Complaint Categories

The database comes pre-loaded with 10 categories:

1. Academic Affairs — Registrar
2. Fees & Bursary — Bursary
3. Hostel & Accommodation — Student Affairs
4. Library Services — Library
5. IT & Portal Issues — ICT
6. Lecturers & Courses — Academic Affairs
7. Health Services — Medical Centre
8. Security — Security Unit
9. Cafeteria & Welfare — Student Affairs
10. General Enquiry

---

*ComplaintDesk — Caleb University Online Complaint Management System*
*© 2024 — Computer Science Department, Caleb University, Lagos*
