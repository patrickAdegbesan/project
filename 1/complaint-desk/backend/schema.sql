-- ComplaintDesk — Caleb University
-- SQLite schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  email       TEXT    NOT NULL UNIQUE,
  password    TEXT    NOT NULL,
  role        TEXT    NOT NULL DEFAULT 'student' CHECK(role IN ('student','staff','admin')),
  department  TEXT,
  matric_no   TEXT,
  staff_id    TEXT,
  phone       TEXT,
  is_active   INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL UNIQUE,
  department  TEXT,
  is_active   INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS complaints (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ref_no       TEXT    NOT NULL UNIQUE,
  title        TEXT    NOT NULL,
  description  TEXT    NOT NULL,
  category_id  INTEGER REFERENCES categories(id),
  priority     TEXT    NOT NULL DEFAULT 'medium' CHECK(priority IN ('low','medium','high','urgent')),
  status       TEXT    NOT NULL DEFAULT 'open' CHECK(status IN ('open','in_progress','resolved','closed','rejected')),
  user_id      INTEGER NOT NULL REFERENCES users(id),
  assigned_to  INTEGER REFERENCES users(id),
  is_anonymous INTEGER NOT NULL DEFAULT 0,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at   TEXT    NOT NULL DEFAULT (datetime('now')),
  resolved_at  TEXT
);

CREATE TABLE IF NOT EXISTS responses (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  complaint_id INTEGER NOT NULL REFERENCES complaints(id),
  user_id      INTEGER NOT NULL REFERENCES users(id),
  message      TEXT    NOT NULL,
  is_internal  INTEGER NOT NULL DEFAULT 0,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS announcements (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT    NOT NULL,
  message      TEXT    NOT NULL,
  target       TEXT    NOT NULL DEFAULT 'all' CHECK(target IN ('all','students','staff')),
  priority     TEXT    NOT NULL DEFAULT 'normal' CHECK(priority IN ('normal','urgent')),
  is_pinned    INTEGER NOT NULL DEFAULT 0,
  is_draft     INTEGER NOT NULL DEFAULT 0,
  author_id    INTEGER NOT NULL REFERENCES users(id),
  view_count   INTEGER NOT NULL DEFAULT 0,
  expires_at   TEXT,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Seed: categories
INSERT OR IGNORE INTO categories (name, department) VALUES
  ('Academic Affairs',       'Registrar'),
  ('Fees & Bursary',         'Bursary'),
  ('Hostel & Accommodation', 'Student Affairs'),
  ('Library Services',       'Library'),
  ('IT & Portal Issues',     'ICT'),
  ('Lecturers & Courses',    'Academic Affairs'),
  ('Health Services',        'Medical Centre'),
  ('Security',               'Security Unit'),
  ('Cafeteria & Welfare',    'Student Affairs'),
  ('General Enquiry',        NULL);

-- Seed: admin user  (password: Admin@1234)
INSERT OR IGNORE INTO users (name, email, password, role, department)
VALUES ('Super Admin', 'administrator@caleb.edu.ng',
        'pbkdf2:sha256:600000$bYcKx8F3$5b73cf0b5a31e7a25e5b1e9b8c2d4f6e8a0c2e4f6b8d0e2f4a6c8e0b2d4f6a8',
        'admin', 'ICT');

-- Seed: staff user  (password: Staff@1234)
INSERT OR IGNORE INTO users (name, email, password, role, department, staff_id)
VALUES ('Chioma Okafor', 'c.okafor@caleb.edu.ng',
        'pbkdf2:sha256:600000$bYcKx8F3$5b73cf0b5a31e7a25e5b1e9b8c2d4f6e8a0c2e4f6b8d0e2f4a6c8e0b2d4f6a8',
        'staff', 'Student Affairs', 'STF-2021-004');

-- Seed: student user  (password: Student@1234)
INSERT OR IGNORE INTO users (name, email, password, role, department, matric_no)
VALUES ('Amara Nwosu', 'a.nwosu@student.caleb.edu.ng',
        'pbkdf2:sha256:600000$bYcKx8F3$5b73cf0b5a31e7a25e5b1e9b8c2d4f6e8a0c2e4f6b8d0e2f4a6c8e0b2d4f6a8',
        'student', 'Computer Science', '22/10444');
