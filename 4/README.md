# SentinelIQ — Credit Card Fraud Detection

A self-contained fraud-detection system: a trained machine-learning
model, a Flask + SQLite backend, a rich web dashboard, and a terminal
client with the same functionality. Runs fully offline — no CDNs, no
external APIs, no internet required.

---

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate   # or use your own env
pip install -r requirements.txt

python train.py     # generate dataset + train the model (writes model/)
python app.py       # start the server
```

Open <http://127.0.0.1:5004>.

## What it does

- **Model** — `train.py` generates a synthetic credit-card dataset in the
  classic PCA-anonymised shape (Amount, hour, V1–V17 subset) with
  overlapping fraud/legit distributions, trains a balanced logistic
  regression, and saves honest held-out metrics (accuracy, precision,
  recall, F1, ROC AUC, ROC/PR curves, confusion matrix, feature
  weights) to `model/metrics.json`.
- **Backend** — `app.py` scores transactions with the trained model and
  stores every scored transaction in SQLite (`sentineliq.db`).
- **Dashboard** — `index.html` reads live data from the API: KPIs,
  30-day fraud trend, hourly/category breakdowns, live transaction
  feed, single-transaction predictor with an animated gauge and real
  per-feature factor contributions, batch scoring, and real ROC/PR /
  feature-importance charts. Opened directly as a file (without the
  backend) it falls back to built-in sample data so the page still renders.

## API

| Endpoint                | Description                                |
|-------------------------|--------------------------------------------|
| `POST /api/predict`     | Score one transaction, store it            |
| `POST /api/batch`       | Generate + score a batch (`{"n": 200}`)    |
| `GET /api/transactions` | Recent scored transactions                 |
| `GET /api/stats`        | KPIs, daily trend, hourly/category splits  |
| `GET /api/model`        | Training metrics of the current model      |
| `POST /api/retrain`     | Retrain and hot-reload the model           |

## Terminal client

Every dashboard function is available from the terminal:

```bash
python cli.py predict --amount 4299 --hour 3 --v14 -9.7 --v17 -6.9
python cli.py batch --n 500
python cli.py transactions --verdict block
python cli.py stats
python cli.py model
python cli.py retrain
python cli.py interactive      # menu-driven session
```

The CLI drives the same Flask app in-process against the same database
and model — no server or network needed.

## Files

```
index.html        dashboard (self-contained, vendor/ assets only)
vendor/           Chart.js (local copy — no CDN)
datagen.py        synthetic transaction generator
train.py          model training + metrics
app.py            Flask API + static serving
cli.py            terminal client
model/            model.pkl + metrics.json (generated)
sentineliq.db     scored transactions (generated)
```
