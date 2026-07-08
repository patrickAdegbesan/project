# Lush Hair NG — AI-Powered Resume Screening System

A production-ready web application that automates resume screening for Lush Hair NG hiring workflows using NLP, geospatial proximity analysis, and multi-criteria scoring.

---

## Features

| Module | Technology |
|---|---|
| Resume Parsing | pdfplumber, PyPDF2, python-docx, pytesseract (OCR) |
| NLP Extraction | spaCy + regex + keyword matching (HuggingFace optional) |
| Geospatial | OpenStreetMap Nominatim + Haversine formula |
| Scoring | Weighted formula: 45% Skill + 35% Experience + 20% Proximity |
| Backend | FastAPI + SQLite (async via aiosqlite) |
| Frontend | Bootstrap 5, DataTables, vanilla JS |

---

## Quick Setup

### 1. Prerequisites

```bash
python 3.10+
pip
# Optional for OCR: tesseract-ocr system package
# Ubuntu: sudo apt install tesseract-ocr poppler-utils
# macOS:  brew install tesseract poppler
```

### 2. Install dependencies

```bash
cd /path/to/project
pip install -r requirements.txt
```

### 3. Download spaCy language model

```bash
python -m spacy download en_core_web_sm
```

### 4. Run the application

```bash
python main.py
```

Open **http://localhost:8000** in your browser.

The database is created automatically on first run and seeded with:
- 3 job roles (ASM, RSM, Dispatch Rider)
- 3 sample candidates with pre-computed scores

The app works fully offline: all styles and scripts (Bootstrap,
Bootstrap Icons, jQuery, DataTables) are bundled in
`app/static/vendor/`, the spaCy model is optional (regex fallback),
and geocoding uses the built-in Lagos location dictionary first —
the OpenStreetMap fallback is only attempted when internet is
available.

### 5. Terminal client (optional)

Every function of the web app also works from the terminal:

```bash
python cli.py roles
python cli.py upload 1 path/to/resume.pdf
python cli.py results 3
python cli.py candidate 6
python cli.py shortlist 4 6          # score ids; add --off to remove
python cli.py export 3 -o out.xlsx
python cli.py stats
python cli.py interactive            # menu-driven session
```

The CLI runs the same FastAPI application in-process against the same
database and scoring pipeline — no server or network needed.

---

## Project Structure

```
/
├── main.py                   # Application entry point
├── requirements.txt
├── README.md
└── app/
    ├── config.py             # Settings (weights, hub location, paths)
    ├── seed.py               # Database seed script
    ├── api/
    │   └── routes.py         # All FastAPI endpoints
    ├── models/
    │   └── database.py       # SQLAlchemy models + DB init
    ├── services/
    │   ├── parser.py         # PDF/DOCX/OCR parsing
    │   ├── nlp.py            # Entity extraction
    │   ├── geospatial.py     # Geocoding + Haversine scoring
    │   ├── scoring.py        # Multi-criteria ranking
    │   └── processor.py      # Background processing pipeline
    ├── static/
    │   ├── css/main.css
    │   └── js/main.js
    ├── templates/
    │   ├── base.html
    │   ├── dashboard.html
    │   ├── upload.html
    │   ├── results.html
    │   └── jobs.html
    └── uploads/              # Uploaded resume files
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload` | Upload resumes + job role ID |
| GET | `/api/status/{job_id}` | Poll processing status |
| GET | `/api/results/{job_id}` | Get ranked candidates |
| POST | `/api/shortlist` | Save shortlisted candidates |
| GET | `/api/export/{job_id}` | Download results as CSV |
| GET | `/api/candidate/{id}` | Full candidate profile |
| GET | `/api/job-roles` | List all job roles |
| POST | `/api/job-roles` | Create job role |
| PUT | `/api/job-roles/{id}` | Update job role |
| DELETE | `/api/job-roles/{id}` | Delete job role |
| GET | `/api/dashboard/stats` | Dashboard statistics |

---

## Scoring Algorithm

```
Total Score = (0.45 × Skill Match) + (0.35 × Experience) + (0.20 × Proximity)
```

- **Skill Match**: Fuzzy string matching between extracted skills and job requirements (≥75% similarity threshold)
- **Experience**: Normalized 0–1 over 15-year scale, with penalty below minimum required years
- **Proximity**: Haversine distance from candidate location to Ikeja hub, normalized 0–1 over 50 km scale

### Proximity colour codes

| Colour | Distance |
|---|---|
| 🟢 Green | < 5 km |
| 🟡 Yellow | 5–15 km |
| 🔴 Red | > 15 km |

---

## Configuration

Edit `app/config.py` or set environment variables:

```env
HUB_LAT=6.6018
HUB_LONG=3.3515
WEIGHT_SKILL=0.45
WEIGHT_EXPERIENCE=0.35
WEIGHT_PROXIMITY=0.20
MAX_EXPERIENCE_YEARS=15
```

---

## Seed Data

Pre-populated on first run:

**Job Roles:**
1. Area Sales Manager (ASM) — 9 required skills, 3+ yrs exp
2. Regional Sales Manager (RSM) — 10 required skills, 5+ yrs exp  
3. Dispatch Rider — 6 required skills, 1+ yr exp

**Sample Candidates:**
- Adaeze Nwosu — Ikeja (0 km from hub) — Sales background
- Chukwuemeka Obi — Surulere (~15 km) — Management background
- Fatima Yusuf — Yaba (~10 km) — Logistics background

---

## OCR for Scanned PDFs

Install system dependencies for OCR support:

```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
```

Without these, the system still processes digital PDFs and DOCX files normally.
