# SRMS — Student Record Management System (project + report)

This folder holds two related things:

```
9/
├── srms/     the application itself (PHP 8 + MySQL)
└── report/   scripts that generate the accompanying project report
```

## srms/ — the application

A complete Student Record Management System for a tertiary
institution: students, courses, grade entry with GPA/CGPA computation,
attendance, fee structures and payments, academic-session management,
role-based access (admin / registrar / teacher / student), analytics
dashboard and a full audit log.

- Vanilla PHP (no framework) with PDO, Bootstrap 5 UI (bundled
  locally in `srms/assets/vendor/` — runs fully offline).
- Terminal client with the same functionality: `php srms/cli.php`.
- Setup, database schema loading, default accounts and the API are
  documented in detail in [`srms/README.md`](srms/README.md).

Quick start:

```bash
mysql -u root -e "CREATE DATABASE srms CHARACTER SET utf8mb4"
mysql -u root srms < srms/database/srms_schema.sql
php -S localhost:80 -t ..     # serve so the app is reachable at /srms
# then open http://localhost/srms  (admin / Admin@1234)
```

## report/ — project report generator

A python-docx pipeline that builds the written project report
(`SRMS_Project_Report.docx`) chapter by chapter:

| Script | Purpose |
|--------|---------|
| `build_report_ch1.py` … `build_report_ch5.py` | Generate each chapter's content |
| `render_diagrams.py` | Render the figures into `figures/` (architecture, ERD, use-case, screenshots of charts, etc.) |
| `insert_figures.py` | Place the rendered figures into the chapters |
| `assemble_report.py` | Stitch everything into the final `.docx` |

Run order:

```bash
cd report
pip install python-docx matplotlib
python render_diagrams.py
python assemble_report.py
```

> Note: the scripts contain absolute paths from the original author's
> machine (`sys.path.insert(0, '/home/path/...')`); adjust those to
> your checkout location before running.
