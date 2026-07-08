# SRMS — Student Record Management System

A PHP/MySQL web application for managing students, courses, grades, attendance,
fees, and academic reporting for a tertiary institution. Built with vanilla PHP
(no framework), PDO for data access, and Bootstrap 5 on the front end.

---

## 1. Tech Stack

| Layer       | Technology                                                   |
|-------------|---------------------------------------------------------------|
| Language    | PHP 8.x (uses typed properties/return types, `password_hash`) |
| Database    | MySQL / MariaDB (InnoDB, `utf8mb4`)                            |
| Web server  | Apache (`mod_rewrite`, `mod_headers`) — XAMPP/WAMP/LAMP or `php -S` |
| Data access | PDO (custom `Database` wrapper, see `config/database.php`)    |
| Front end   | HTML5, Bootstrap 5.3 (CDN), Bootstrap Icons (CDN), jQuery 3.7 (CDN), Chart.js 4.4 (CDN) |
| Custom assets | `assets/css/style.css`, `assets/js/main.js`                 |

No Composer/npm build step is required — all third-party front-end libraries
are pulled from CDN at page render time, so an internet connection is needed
in the browser (not on the server) for styling/charts to load.

---

## 2. Prerequisites

Install these on your machine before setting up the project:

1. **PHP 8.0+** with the `pdo_mysql`, `mbstring`, and `openssl` extensions enabled.
2. **MySQL 5.7+ / MariaDB 10.4+**.
3. **Apache** with `mod_rewrite` and `mod_headers` enabled (required for `.htaccess`).
   - A bundled stack such as **XAMPP**, **WAMP**, **MAMP**, or Laragon works well on
     Windows/macOS. On Linux you can use the native `httpd`/`apache2` + `mysql-server` packages.
4. A code editor / IDE — **VS Code** is recommended, with these extensions:
   - PHP Intelephense (or PHP IntelliSense)
   - MySQL / Database Client (e.g. "SQLTools" or "MySQL" extension)
   - Apache Conf syntax highlighting (optional)

You do **not** need Node.js or Composer for this project.

---

## 3. Installation

### Step 1 — Get the code onto your server's web root

Copy (or clone) the `srms/` directory into your web server's document root.

```bash
# Example for XAMPP on Linux
cp -r srms/ /opt/lampp/htdocs/srms

# Example for native Apache on Linux
cp -r srms/ /var/www/html/srms

# Example for XAMPP on Windows
# Copy the folder into C:\xampp\htdocs\srms
```

### Step 2 — Create the database

Log into MySQL and import the bundled schema (it creates the `srms` database,
all tables, and seed data — sample departments, courses, students, and four
demo user accounts):

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS srms CHARACTER SET utf8mb4"
mysql -u root -p srms < database/srms_schema.sql
```

### Step 3 — Configure database credentials

Edit `config/config.php` and update the DB constants to match your local
MySQL setup:

```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'srms');
define('DB_USER', 'root');
define('DB_PASS', '');          // set your MySQL password here
```

Also update `BASE_URL` if you deploy under a different path/host than
`http://localhost/srms`.

### Step 4 — Enable required Apache modules

The app relies on `.htaccess` for security headers and rewrite rules. Make sure
your Apache config allows overrides for the directory, e.g. in `httpd.conf` /
the relevant vhost:

```apache
<Directory "/var/www/html/srms">
    AllowOverride All
    Require all granted
</Directory>
```

Then enable the modules and restart Apache:

```bash
sudo a2enmod rewrite headers   # Debian/Ubuntu
sudo systemctl restart apache2

# or, for httpd on Fedora/RHEL
sudo apachectl restart
```

### Step 5 — File permissions

The app writes uploaded files (e.g. student photos) to `assets/uploads/`.
Create the directory and make it writable by the web server user:

```bash
mkdir -p assets/uploads
chmod -R 775 assets/uploads
chown -R apache:apache assets/uploads   # or www-data:www-data on Debian/Ubuntu
```

---

## 4. Running the Server

### Option A — Bundled stack (XAMPP/WAMP/MAMP)

Start Apache and MySQL from the control panel, then visit:

```
http://localhost/srms
```

### Option B — Native Apache/MySQL

```bash
sudo systemctl start mysqld
sudo systemctl start httpd      # or apache2
```

Then visit `http://localhost/srms` (or your configured `BASE_URL`).

### Option C — PHP built-in dev server (quick local testing, no Apache)

This skips `.htaccess` rewrite rules, so use it only for quick checks:

```bash
cd srms
php -S localhost:8000
```

Visit `http://localhost:8000`. Note: the security-header/rewrite rules in
`.htaccess` won't apply under the built-in server.

### Logging in

The schema seeds four demo accounts (`admin`, `registrar1`, `dr_eze`,
`mr_adeyemi` — see `database/srms_schema.sql`). Their password hashes are
pre-generated bcrypt values; **do not assume a default password**. Set your
own before using the app:

```php
<?php
// run once via `php -r` or a throwaway script, then UPDATE the row
echo password_hash('YourNewPassword123!', PASSWORD_BCRYPT, ['cost' => 12]);
```

```sql
UPDATE users SET password_hash = '<paste hash here>' WHERE username = 'admin';
```

---

## 5. Project Structure

```
srms/
├── index.php                  # Entry point — redirects to login or dashboard
├── .htaccess                  # Security headers, rewrite rules, blocks config/includes/database dirs
├── config/
│   ├── config.php             # App constants: DB creds, BASE_URL, grading scale, session/CSRF setup
│   └── database.php           # PDO singleton wrapper (Database class, db() helper)
├── includes/
│   ├── auth.php                # loginUser(), logoutUser(), login-attempt throttling
│   ├── functions.php           # Shared helpers: grade calculation, GPA, formatting, audit logging
│   ├── header.php              # Shared <head>/nav markup (Bootstrap/Chart.js CDN includes)
│   ├── sidebar.php             # Role-aware navigation sidebar
│   └── footer.php              # Shared closing markup + JS includes
├── modules/                    # Feature areas, each typically index/add/edit/delete.php
│   ├── auth/                   # login.php, logout.php
│   ├── dashboard/               # Role-specific dashboard widgets/stats
│   ├── students/                 # CRUD for student records
│   ├── courses/                  # CRUD for course catalog
│   ├── grades/                   # Grade entry + GPA calculator
│   ├── attendance/                # Mark attendance, attendance reports
│   ├── fees/                      # Fee payments, statements
│   ├── reports/                   # Transcripts, class lists, attendance summaries
│   ├── users/                      # User account management (admin)
│   └── audit/                      # Audit log viewer
├── api/
│   ├── get_analytics.php       # JSON endpoint feeding dashboard Chart.js graphs
│   └── search_students.php     # AJAX student search/autocomplete
├── assets/
│   ├── css/style.css           # Custom styling on top of Bootstrap
│   ├── js/main.js              # Custom client-side behavior
│   └── uploads/                # Student photo uploads (created at setup, not in repo)
└── database/
    └── srms_schema.sql         # Full schema + seed data (departments, sessions, courses, demo users)
```

### Request flow

1. `index.php` checks the session (via `includes/auth.php`) and routes to
   `modules/auth/login.php` or `modules/dashboard/index.php`.
2. Every module page includes `config/config.php` → `config/database.php` →
   `includes/functions.php`/`auth.php`, then `includes/header.php` +
   `includes/sidebar.php` for shared chrome, and `includes/footer.php` to close out.
3. Data access goes through the `db()` singleton (PDO, prepared statements
   only — see `config/database.php`).

### Roles

`users.role` is one of `admin`, `registrar`, `teacher`, `student`. Sidebar
navigation and module access are gated by role — see `includes/sidebar.php`
and the top of each `modules/*/index.php` for the specific checks.

### Grading

- CA score max: 30, Exam score max: 70 (`MAX_CA_SCORE` / `MAX_EXAM_SCORE` in `config/config.php`).
- Letter grade / grade points: A(70–100)=4.0, B(60–69)=3.0, C(50–59)=2.0, D(45–49)=1.0, F(0–44)=0.0 — see `getLetterGrade()` in `includes/functions.php`.
- GPA = Σ(grade_points × credit_units) / Σ(credit_units) per session — see `calculateGPA()`.

---

## 6. Security Notes

- `.htaccess` blocks direct browser access to `config/`, `includes/`, and
  `database/`, and to any `.sql` file — don't remove these rules in production.
- CSRF tokens are generated per-session in `config/config.php`; module forms
  should include and validate `$_SESSION['csrf_token']`.
- `error_reporting`/`display_errors` are on in `config/config.php` for
  development — turn them off (or rely on the `.htaccess` override) before
  deploying publicly.
- Login attempts are throttled (5 attempts / 15-minute window) in `includes/auth.php`.
