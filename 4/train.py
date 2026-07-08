#!/usr/bin/env python3
"""
SentinelIQ — model training.

Generates a synthetic fraud dataset (datagen.py), trains a logistic
regression classifier and writes:

  model/model.pkl      the fitted pipeline (scaler + classifier)
  model/metrics.json   honest held-out metrics: accuracy, precision,
                       recall, F1, ROC AUC, ROC and PR curve points,
                       confusion matrix and feature importances

Run:  python train.py [--n 40000] [--seed 42]
"""

import argparse
import json
import os
from datetime import datetime, timezone

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_recall_curve, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from datagen import FEATURES, generate

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")


def downsample(xs, ys, k=60):
    idx = np.linspace(0, len(xs) - 1, min(k, len(xs))).astype(int)
    return [[round(float(xs[i]), 4), round(float(ys[i]), 4)] for i in idx]


def train(n=40000, seed=42):
    X, y, _meta = generate(n=n, fraud_rate=0.02, seed=seed)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, random_state=seed, stratify=y)

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    pipe.fit(X_tr, y_tr)

    prob = pipe.predict_proba(X_te)[:, 1]
    pred = (prob >= 0.5).astype(int)

    fpr, tpr, _ = roc_curve(y_te, prob)
    prec_c, rec_c, _ = precision_recall_curve(y_te, prob)
    cm = confusion_matrix(y_te, pred)

    coefs = pipe.named_steps["clf"].coef_[0]
    importances = sorted(
        ({"feature": f, "weight": round(float(abs(w)), 4),
          "direction": "fraud" if w > 0 else "legit"}
         for f, w in zip(FEATURES, coefs)),
        key=lambda d: -d["weight"])

    metrics = {
        "model": "LogisticRegression (balanced)",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "train_size": len(X_tr),
        "test_size": len(X_te),
        "fraud_rate": round(float(y.mean()), 4),
        "accuracy":  round(float(accuracy_score(y_te, pred)) * 100, 2),
        "precision": round(float(precision_score(y_te, pred)) * 100, 2),
        "recall":    round(float(recall_score(y_te, pred)) * 100, 2),
        "f1":        round(float(f1_score(y_te, pred)) * 100, 2),
        "roc_auc":   round(float(roc_auc_score(y_te, prob)), 4),
        "confusion": {"tn": int(cm[0][0]), "fp": int(cm[0][1]),
                      "fn": int(cm[1][0]), "tp": int(cm[1][1])},
        "roc_curve": downsample(fpr, tpr),
        "pr_curve":  downsample(rec_c, prec_c),
        "importances": importances,
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipe, os.path.join(MODEL_DIR, "model.pkl"))
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    m = train(n=args.n, seed=args.seed)
    print(f"[OK] model saved to {MODEL_DIR}")
    print(f"  accuracy {m['accuracy']}%  precision {m['precision']}%  "
          f"recall {m['recall']}%  f1 {m['f1']}%  ROC AUC {m['roc_auc']}")
