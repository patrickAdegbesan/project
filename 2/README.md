# PhishGuard AI — Phishing Attack Detection & Prevention System

**BSc Final Year Project**
**Author:** Sanwo Abdulquayyum Subomi
**Institution:** Caleb University
**Topic:** The Development of a Machine Learning-based System for Phishing Attack Detection and Prevention

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Project Structure](#3-project-structure)
4. [How It Works — End to End](#4-how-it-works--end-to-end)
   - [Step 1: URL Submitted by User](#step-1-url-submitted-by-user)
   - [Step 2: Feature Extraction](#step-2-feature-extraction)
   - [Step 3: ML Model Inference](#step-3-ml-model-inference)
   - [Step 4: SHAP Explanation](#step-4-shap-explanation)
   - [Step 5: Result Stored in Database](#step-5-result-stored-in-database)
   - [Step 6: Response Sent to Frontend](#step-6-response-sent-to-frontend)
5. [Machine Learning Model](#5-machine-learning-model)
6. [Feature Engineering (All 32 Features)](#6-feature-engineering-all-32-features)
7. [Typosquatting Detection](#7-typosquatting-detection)
8. [API Reference](#8-api-reference)
9. [Database Schema](#9-database-schema)
10. [Frontend Pages](#10-frontend-pages)
11. [Setup & Running the System](#11-setup--running-the-system)
12. [Training the Model](#12-training-the-model)
13. [Tech Stack](#13-tech-stack)

---

## 1. Project Overview

PhishGuard AI is a full-stack web application that detects phishing URLs in real time using machine learning. A user pastes any URL into the interface and within seconds receives:

- A **classification** (Phishing or Legitimate)
- A **risk score** from 0–100
- A **confidence percentage**
- A **SHAP feature importance chart** explaining which URL properties drove the decision
- **Feature detail cards** breaking down individual indicators

The system runs entirely offline — no network calls are made to the URL being analysed. All detection is based on structural and lexical properties of the URL string itself.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (User)                        │
│              frontend/index.html                         │
│   Dashboard · Results · History · Admin · About          │
└───────────────────────┬─────────────────────────────────┘
                        │  HTTP (fetch API)
                        ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (port 8000)                 │
│                   backend/main.py                        │
│                                                          │
│  POST /api/analyze   ──► features.py ──► predict.py     │
│  GET  /api/history   ──► SQLite DB                      │
│  POST /api/feedback  ──► SQLite DB                      │
│  GET  /api/admin/stats ──► SQLite DB                    │
│  GET  /api/admin/model-metrics ──► model/metrics.json   │
└───────────┬───────────────────────┬─────────────────────┘
            │                       │
            ▼                       ▼
┌───────────────────┐   ┌──────────────────────────────┐
│   SQLite Database  │   │     ML Model (pickle)         │
│  data/phishguard  │   │  model/phishing_model.pkl     │
│       .db         │   │  GradientBoostingClassifier   │
│                   │   │  + StandardScaler pipeline    │
│  url_records      │   │  32 features · 30,000 samples │
│  feedback_records │   └──────────────────────────────┘
└───────────────────┘
```

---

## 3. Project Structure

```
project/
├── backend/
│   ├── main.py              # FastAPI app — routes, CORS, static file serving
│   ├── features.py          # URL feature extraction (32 features, no network)
│   ├── predict.py           # Load model, run inference, compute SHAP proxy
│   ├── train.py             # Download dataset, generate synthetic data, train model
│   ├── database.py          # SQLAlchemy engine + session factory
│   ├── models.py            # ORM models: URLRecord, FeedbackRecord
│   ├── requirements.txt
│   └── routers/
│       ├── analyze.py       # POST /api/analyze
│       ├── history.py       # GET  /api/history
│       ├── feedback.py      # POST /api/feedback, GET, PATCH
│       └── admin.py         # GET  /api/admin/stats, /api/admin/model-metrics
│
├── frontend/
│   └── index.html           # Single-file SPA (HTML + CSS + JS)
│
├── model/
│   ├── phishing_model.pkl   # Trained sklearn pipeline (auto-generated)
│   ├── feature_names.json   # Ordered list of 32 feature names
│   └── metrics.json         # Accuracy, precision, recall, F1 from training run
│
└── data/
    ├── phishguard.db        # SQLite database (auto-created on first run)
    └── phishing_dataset.csv # Cached training dataset (auto-downloaded)
```

---

## 4. How It Works — End to End

### Step 1: URL Submitted by User

The user types or pastes a URL into the input box on the Dashboard and clicks **Analyze**. The frontend sends a POST request to the backend:

```
POST /api/analyze
Content-Type: application/json

{ "url": "https://www.instajhgram.com/officialcampusdash/" }
```

While the API processes the request, an animated scanning sequence plays in the UI (resolving domain → extracting features → computing SHAP → classifying).

---

### Step 2: Feature Extraction

`backend/features.py` receives the raw URL string and extracts **32 numeric features** from it using only Python's built-in libraries (`re`, `urllib.parse`, `math`). No HTTP requests are made to the target URL.

Each feature is a float — either a count, a ratio, a flag (0 or 1), or a computed value like Shannon entropy.

Examples:
- `url_length = 47.0` — total character count of the URL
- `num_hyphens = 0.0` — hyphens in the URL
- `tld_suspicious = 0.0` — is the TLD in the high-risk list (.tk, .xyz, .ml, etc.)
- `brand_typosquat = 1.0` — domain is 1–3 edit-distance from a known brand name
- `url_entropy = 3.82` — Shannon entropy of the URL characters

The full list of 32 features is described in [Section 6](#6-feature-engineering-all-32-features).

---

### Step 3: ML Model Inference

`backend/predict.py` loads the trained model pipeline from `model/phishing_model.pkl` (loaded once at startup, cached in memory).

The 32 features are assembled into a NumPy array in the exact order stored in `model/feature_names.json`, then passed through the pipeline:

```
raw features (32 floats)
    → StandardScaler (normalise each feature to zero mean / unit variance)
    → GradientBoostingClassifier
    → probability vector [P(legitimate), P(phishing)]
```

The model outputs a probability. For example:
- `P(phishing) = 0.97` → **PHISHING**, risk score = 97
- `P(phishing) = 0.03` → **LEGITIMATE**, risk score = 3

**Hard rule override:** If `brand_typosquat = 1.0`, the result is forced to **PHISHING** with a minimum risk score of 85, regardless of what the model outputs. Typosquatting of a known brand is treated as a definitive signal.

---

### Step 4: SHAP Explanation

Because the standard SHAP library requires large binary dependencies (llvmlite, 56 MB) that could not be downloaded, a custom attribution proxy is used instead.

For each of the 32 features, an attribution value is computed as:

```
attribution = feature_importance × direction × normalised_value
```

Where:
- **`feature_importance`** — the model's global `feature_importances_` array (how much each feature contributes to splits across all trees)
- **`direction`** — +1 if the feature pushes toward phishing when high (e.g. `num_hyphens`), -1 if it pushes toward legitimate when high (e.g. `is_https`)
- **`normalised_value`** — for binary/ratio features: `value − 0.5` (so 0 → −0.5, 1 → +0.5); for count features: `log(1 + value) / 10`

Result:
- **Positive attribution** → this feature's current value pushes toward **PHISHING** (shown as red bar)
- **Negative attribution** → this feature's current value pushes toward **LEGITIMATE** (shown as blue bar)

The top 5 features by absolute attribution are returned with the result.

---

### Step 5: Result Stored in Database

The backend saves a row to the `url_records` SQLite table:

```
url, domain, classification, risk_score, confidence,
features_json (all 32 values), shap_json (top 5), created_at
```

This powers the History page, the Admin dashboard statistics, and the detection volume chart.

---

### Step 6: Response Sent to Frontend

The API returns a JSON response:

```json
{
  "url_id": 42,
  "url": "https://www.instajhgram.com/officialcampusdash/",
  "domain": "www.instajhgram.com",
  "classification": "phishing",
  "risk_score": 85,
  "confidence": 85.0,
  "features": { "url_length": 47.0, "num_hyphens": 0.0, ... },
  "shap_features": [
    { "name": "brand_typosquat", "value": 1.0, "shap_value": 0.312 },
    ...
  ],
  "created_at": "2026-06-28T10:42:00"
}
```

The frontend renders:
- The **risk gauge** animates from 0 to the risk score
- The **verdict badge** (PHISHING / LEGITIMATE) appears with the appropriate colour
- The **SHAP bar chart** draws each bar (red = phishing direction, blue = legitimate direction)
- The **feature cards** show the value and plain-English description of each top feature

---

## 5. Machine Learning Model

### Algorithm

**GradientBoostingClassifier** (scikit-learn) — an ensemble of 300 shallow decision trees trained sequentially, each tree correcting the errors of the previous one.

Hyperparameters:
```
n_estimators  = 300
max_depth     = 5
learning_rate = 0.08
subsample     = 0.8
random_state  = 42
```

The model is wrapped in a scikit-learn `Pipeline`:
```
Pipeline([
    ("scaler", StandardScaler()),
    ("clf",    GradientBoostingClassifier(...))
])
```

StandardScaler normalises each feature so no single large-valued feature (like `url_length`) dominates.

### Training Data

A real-world phishing dataset (GregaVrbancic Phishing Dataset, 88,647 rows, 111 features) is downloaded and checked against our 32 feature names. Since the dataset uses different feature names, the system generates **30,000 synthetic samples** instead — 15,000 phishing and 15,000 legitimate — using a seeded random number generator (`numpy.random.default_rng(42)`) to ensure reproducibility.

Each synthetic sample has realistic feature distributions:

| Feature group | Phishing range | Legitimate range |
|---|---|---|
| `url_length` | 60–250 chars | 10–55 chars |
| `num_hyphens` | 2–9 | 0–2 |
| `tld_suspicious` | 70% chance = 1 | always 0 |
| `brand_in_subdomain` | 70% chance = 1 | always 0 |
| `suspicious_words_count` | 2–9 | 0–2 |
| `brand_typosquat` | 60% chance = 1 | always 0 |
| `is_https` | 50% chance | always 1 |

### Performance

On the 6,000-sample held-out test set:

| Metric | Score |
|---|---|
| Accuracy | 100.0% |
| Precision | 100.0% |
| Recall | 100.0% |
| F1-Score | 100.0% |

> Note: 100% accuracy is expected because the model is tested on synthetic data from the same distribution it was trained on. Real-world performance on diverse, live phishing URLs will differ — this is a known limitation of synthetic training data.

---

## 6. Feature Engineering (All 32 Features)

All features are extracted from the raw URL string with zero network calls.

### URL Structure (7 features)

| Feature | Description |
|---|---|
| `url_length` | Total character count of the URL |
| `num_dots` | Number of `.` characters |
| `num_hyphens` | Number of `-` characters |
| `num_digits` | Number of digit characters (0–9) |
| `num_special_chars` | Count of special characters (`!@#$%` etc.) |
| `num_slashes` | Number of `/` characters |
| `url_depth` | Number of path segments (e.g. `/a/b/c` = depth 3) |

### Domain (5 features)

| Feature | Description |
|---|---|
| `domain_length` | Character length of the registered domain |
| `subdomain_count` | Number of subdomain levels |
| `has_ip_address` | 1 if the host is a raw IP address (e.g. `192.168.1.1`) |
| `tld_suspicious` | 1 if TLD is in the high-risk list (`.tk`, `.ml`, `.xyz`, `.info`, etc.) |
| `tld_in_path` | 1 if the TLD string appears inside the URL path |

### Lexical (6 features)

| Feature | Description |
|---|---|
| `has_at_symbol` | 1 if `@` is in the URL (used to obscure real domain) |
| `has_double_slash` | 1 if `//` appears in the path after the protocol |
| `https_token_in_domain` | 1 if the word "https" appears inside the domain name |
| `url_entropy` | Shannon entropy of the URL characters (high = more obfuscated) |
| `digit_ratio` | Fraction of URL characters that are digits |
| `letter_ratio` | Fraction of URL characters that are letters |

### Path & Query (4 features)

| Feature | Description |
|---|---|
| `path_length` | Character length of the URL path |
| `query_length` | Character length of the query string |
| `num_query_params` | Number of key=value query parameters |
| `fragment_present` | 1 if a `#fragment` is in the URL |

### Brand & Keywords (4 features)

| Feature | Description |
|---|---|
| `brand_in_subdomain` | 1 if a known brand name appears in the subdomain |
| `brand_in_path` | 1 if a known brand name appears in the URL path |
| `suspicious_words_count` | Count of words like "login", "verify", "secure", "update", "confirm" in the URL |
| `has_port` | 1 if a non-standard port is specified |

### Protocol & Misc (4 features)

| Feature | Description |
|---|---|
| `is_https` | 1 if the URL uses HTTPS |
| `domain_has_hyphen` | 1 if the registered domain contains a hyphen |
| `num_subdomains_gt2` | 1 if there are more than 2 subdomain levels |
| `url_has_encoded_chars` | 1 if `%xx` percent-encoding appears in the URL |

### Typosquatting (2 features)

| Feature | Description |
|---|---|
| `brand_typosquat` | 1 if the domain's SLD is within 3 Levenshtein edit-distance of a known brand but is not that brand (e.g. `instajhgram` → 2 edits from `instagram`) |
| `brand_exact_in_domain` | 1 if a full brand name string is embedded in the domain but the domain is not that brand (e.g. `paypal-login.com`) |

---

## 7. Typosquatting Detection

Typosquatting is when an attacker registers a domain name that is visually similar to a well-known brand — for example `instajhgram.com` instead of `instagram.com` — hoping victims will not notice the difference.

PhishGuard detects this using **Levenshtein edit distance**, which counts the minimum number of single-character insertions, deletions, or substitutions needed to turn one string into another.

```
instajhgram  →  instagram
              insert 'j' and 'h'
edit distance = 2
```

The algorithm checks the domain's second-level domain (SLD) against a list of 24 major brands:

> paypal, apple, microsoft, amazon, google, facebook, netflix, instagram, twitter, linkedin, ebay, wellsfargo, chase, dropbox, yahoo, outlook, icloud, steam, roblox, walmart, whatsapp, youtube, tiktok, snapchat

A URL is flagged as a typosquat if:
- Edit distance is **1, 2, or 3**
- The SLD length differs from the brand name by **no more than 4 characters**
- The SLD is **not itself** the exact brand name (to avoid false positives on `instagram.com`)

When `brand_typosquat = 1`, a **hard rule** overrides the model output and forces the classification to **PHISHING** with a minimum risk score of **85%**. This is intentional — typosquatting is such a high-confidence signal that it should not be overridden by other clean features.

---

## 8. API Reference

All endpoints are prefixed with `/api`. The server also serves the frontend at `/`.

### `POST /api/analyze`

Analyse a URL and return the classification.

**Request body:**
```json
{ "url": "https://example.com/path" }
```

**Response:**
```json
{
  "url_id": 1,
  "url": "https://example.com/path",
  "domain": "example.com",
  "classification": "legitimate",
  "risk_score": 5,
  "confidence": 95.0,
  "features": { "url_length": 27.0, "num_hyphens": 0.0, ... },
  "shap_features": [
    { "name": "is_https", "value": 1.0, "shap_value": -0.212 },
    ...
  ],
  "created_at": "2026-06-28T10:00:00"
}
```

---

### `GET /api/history`

Retrieve paginated scan history.

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `limit` | int | 20 | Results per page |
| `cls` | string | — | Filter by `phishing` or `legitimate` |
| `risk_min` | int | 0 | Minimum risk score |
| `risk_max` | int | 100 | Maximum risk score |
| `search` | string | — | Search URL text |

---

### `POST /api/feedback`

Submit a correction on a misclassified URL.

**Request body:**
```json
{
  "url_id": 42,
  "fb_type": "fp",
  "comment": "This is a legitimate site, not phishing."
}
```

`fb_type` must be `"fp"` (false positive — was labelled phishing but is legitimate) or `"fn"` (false negative — was labelled legitimate but is phishing).

---

### `GET /api/feedback`

List pending feedback items.

**Query parameters:** `reviewed=false` (default) or `reviewed=true`

---

### `PATCH /api/feedback/{id}/review`

Mark a feedback item as reviewed (admin action).

---

### `GET /api/admin/stats`

Return live system statistics computed from the database.

**Response includes:**
- `total_analyzed`, `phishing_count`, `legitimate_count`
- `avg_risk_score`, `phishing_rate`
- `feedback_pending`
- `today_total`, `today_phishing`
- `avg_response_ms` — rolling average of the last 200 API response times
- `daily_counts` — array of 7 days with `{date, phishing, legitimate}` counts
- `top_phishing_domains` — top 5 most-seen phishing domains

---

### `GET /api/admin/model-metrics`

Return training metrics from the last model training run.

**Response:**
```json
{
  "accuracy": 100.0,
  "precision": 100.0,
  "recall": 100.0,
  "f1": 100.0,
  "train_size": 24000,
  "test_size": 6000,
  "features": 32,
  "trained_at": "2026-06-28T02:50:43",
  "model": "GradientBoostingClassifier"
}
```

---

## 9. Database Schema

SQLite database at `data/phishguard.db`, managed by SQLAlchemy. Tables are created automatically on first run.

### `url_records`

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `url` | TEXT | Full URL that was analysed |
| `domain` | TEXT | Extracted hostname |
| `classification` | TEXT | `"phishing"` or `"legitimate"` |
| `risk_score` | FLOAT | 0–100 |
| `confidence` | FLOAT | 0–100 |
| `features_json` | TEXT | JSON string of all 32 feature values |
| `shap_json` | TEXT | JSON string of top 5 SHAP attributions |
| `created_at` | DATETIME | UTC timestamp of the scan |

### `feedback_records`

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `url_id` | INTEGER FK | References `url_records.id` |
| `url` | TEXT | Denormalised URL copy |
| `fb_type` | TEXT | `"fp"` or `"fn"` |
| `comment` | TEXT | Optional user comment |
| `reviewed` | BOOLEAN | Whether an admin has reviewed this |
| `created_at` | DATETIME | UTC timestamp |

---

## 10. Frontend Pages

The entire frontend is a single HTML file (`frontend/index.html`) with embedded CSS and JavaScript. It is a single-page application that swaps sections in and out without page reloads.

### Dashboard
- URL input box with example URLs
- Three stat cards: Total URLs Analysed, Phishing Detected, Legitimate URLs (all loaded live from the API)
- Recent Detections feed showing the last 5 scans with time-ago labels

### Results
- Animated scan sequence while the API processes
- Risk score gauge (0–100) with animated counter
- Verdict badge (PHISHING / LEGITIMATE) with dynamic colour
- Legitimacy/Phishing confidence bar
- SHAP feature importance horizontal bar chart (red = phishing direction, blue = legitimate direction)
- Feature detail cards with plain-English descriptions
- Export to CSV button
- Report Incorrect Classification button (opens feedback modal)

### History
- Searchable, filterable, paginated table of all scans
- Filter by classification, risk range, and URL text
- Classification badges and risk score chips for each row

### Admin
- Four live metric cards: Scans Today, Phishing Rate, Average Risk Score, Average Response Time
- Model performance cards: Accuracy, Precision, Recall, F1 (loaded from `model/metrics.json`)
- Detection volume bar chart — 7-day daily breakdown of phishing vs legitimate
- Feedback queue — pending user corrections with approve/dismiss buttons
- Top phishing domains list

### About
- Project description, methodology, tech stack summary, and academic context

---

## 11. Setup & Running the System

### Prerequisites

- Python 3.8 or later
- pip

### Installation

```bash
# Clone or navigate to the project directory
cd project/

# Install Python dependencies
pip install -r backend/requirements.txt
```

### Train the Model (first time only)

```bash
cd backend
python3 train.py
```

This will:
1. Attempt to download the GregaVrbancic Phishing Dataset (~5 MB CSV)
2. Detect that the dataset's feature names don't match our 32 features
3. Generate 30,000 synthetic training samples instead
4. Train the GradientBoostingClassifier pipeline (~3–5 seconds)
5. Save `model/phishing_model.pkl`, `model/feature_names.json`, `model/metrics.json`

You only need to run this once. The model files persist between server restarts.

### Start the Server

```bash
cd backend
python3 -m uvicorn main:app --port 8000
```

### Open the Application

Open your browser and go to:

```
http://localhost:8000/
```

The API documentation (Swagger UI) is available at:

```
http://localhost:8000/docs
```

### Stopping the Server

Press `Ctrl + C` in the terminal where uvicorn is running.

---

## 12. Training the Model

The training script (`backend/train.py`) handles everything automatically.

```bash
cd backend
python3 train.py
```

**What it does:**

1. **Downloads dataset** — fetches the GregaVrbancic Phishing Dataset CSV (if not already cached in `data/phishing_dataset.csv`)
2. **Checks feature compatibility** — compares the dataset's columns against the 32 features our extractor produces
3. **Generates synthetic data** — since the real dataset uses different feature names, 30,000 synthetic samples are generated using `numpy.random.default_rng(42)` (fixed seed for reproducibility)
4. **Splits data** — 80% training (24,000 rows), 20% test (6,000 rows)
5. **Trains pipeline** — StandardScaler + GradientBoostingClassifier
6. **Evaluates** — prints accuracy, precision, recall, F1 and a full classification report
7. **Saves artefacts:**
   - `model/phishing_model.pkl` — the trained pipeline
   - `model/feature_names.json` — ordered list of 32 feature names
   - `model/metrics.json` — training metrics (served by the admin API)

To retrain from scratch (e.g. after adding new features), delete the synthetic data cache and retrain:

```bash
rm data/synthetic_urls.csv
cd backend && python3 train.py
```

---

## 13. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5 / CSS3 / Vanilla JS | Single-page application, no framework |
| **Icons** | Lucide Icons (CDN) | UI icons throughout the interface |
| **Charts** | Chart.js (CDN) | Risk gauge, SHAP bars, admin volume chart |
| **Backend** | FastAPI (Python) | REST API, CORS, static file serving |
| **ASGI Server** | Uvicorn | Production-grade ASGI server |
| **ML Model** | scikit-learn | GradientBoostingClassifier + StandardScaler Pipeline |
| **Feature Extraction** | Python stdlib | `re`, `urllib.parse`, `math` — no external deps |
| **Database ORM** | SQLAlchemy | Session management, query building |
| **Database** | SQLite | Lightweight embedded database, zero configuration |
| **Model Persistence** | joblib | Serialise/deserialise the trained pipeline |
| **Data Processing** | pandas + NumPy | Training data manipulation |
| **Design System** | Custom CSS (glass-morphism dark theme) | Dark navy palette, cyan accent, dot-grid background |

---

*PhishGuard AI — BSc Final Year Project, Caleb University*
