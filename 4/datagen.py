"""
SentinelIQ — synthetic transaction generator.

Produces credit-card transactions in the same shape as the classic
PCA-anonymised fraud dataset (Time, Amount, V-features), with fraud rows
drawn from shifted distributions (V14/V17/V3 strongly negative, larger
night-time amounts) so a trained model has a genuine signal to learn.

Used by train.py to build the training set and by app.py to simulate
batches for scoring. No network access required.
"""

import numpy as np

FEATURES = ["v1", "v2", "v3", "v4", "v14", "v17", "amount", "hour"]

CATEGORIES = [
    # (name, share of legit traffic, share of fraud traffic)
    ("Online Retail",  0.28, 0.42),
    ("Electronics",    0.10, 0.22),
    ("Travel",         0.08, 0.14),
    ("Groceries",      0.22, 0.04),
    ("Fuel",           0.12, 0.05),
    ("Restaurants",    0.14, 0.06),
    ("Fashion",        0.06, 0.07),
]


def _pick_categories(rng, is_fraud, n):
    names = [c[0] for c in CATEGORIES]
    legit_p = np.array([c[1] for c in CATEGORIES], dtype=float)
    fraud_p = np.array([c[2] for c in CATEGORIES], dtype=float)
    legit_p /= legit_p.sum()
    fraud_p /= fraud_p.sum()
    out = np.empty(n, dtype=object)
    fraud_idx = is_fraud.astype(bool)
    out[fraud_idx] = rng.choice(names, size=fraud_idx.sum(), p=fraud_p)
    out[~fraud_idx] = rng.choice(names, size=(~fraud_idx).sum(), p=legit_p)
    return out


def generate(n=20000, fraud_rate=0.02, seed=None):
    """Return (X, y, meta) where X is an (n, 8) array in FEATURES order,
    y is 0/1 fraud labels and meta is a dict of per-row extras."""
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < fraud_rate).astype(int)
    n_fraud = int(y.sum())
    n_legit = n - n_fraud

    def col(legit_dist, fraud_dist):
        c = np.empty(n)
        c[y == 0] = legit_dist(n_legit)
        c[y == 1] = fraud_dist(n_fraud)
        return c

    # Fraud distributions overlap the legit ones substantially — otherwise
    # the classes are trivially separable and the metrics are meaningless.
    v1  = col(lambda k: rng.normal(0.0, 1.0, k), lambda k: rng.normal(-0.9, 1.6, k))
    v2  = col(lambda k: rng.normal(0.0, 1.0, k), lambda k: rng.normal(0.6,  1.4, k))
    v3  = col(lambda k: rng.normal(0.0, 1.0, k), lambda k: rng.normal(-1.8, 1.8, k))
    v4  = col(lambda k: rng.normal(0.0, 1.0, k), lambda k: rng.normal(0.9,  1.5, k))
    v14 = col(lambda k: rng.normal(0.0, 1.0, k), lambda k: rng.normal(-3.2, 2.0, k))
    v17 = col(lambda k: rng.normal(0.0, 1.0, k), lambda k: rng.normal(-2.4, 1.9, k))

    # Legit purchases: modest lognormal amounts, daytime-skewed hours.
    # Fraud: larger and more dispersed amounts, night-skewed hours.
    amount = col(lambda k: rng.lognormal(3.4, 1.0, k),
                 lambda k: rng.lognormal(5.1, 1.4, k)).round(2)
    hour_legit = lambda k: np.clip(rng.normal(14, 4.5, k), 0, 23.99)
    hour_fraud = lambda k: (rng.normal(2.5, 3.5, k) % 24)
    hour = col(hour_legit, hour_fraud)

    X = np.column_stack([v1, v2, v3, v4, v14, v17, amount, hour])
    meta = {
        "category": _pick_categories(rng, y, n),
        "hour": hour.astype(int),
    }
    return X, y, meta
