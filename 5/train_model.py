"""
TaskMind — Reschedule Success Prediction Model
===============================================
Trains a logistic regression classifier to predict whether a rescheduled
task will be completed by its suggested new date.

Features (Section 3.9.3):
  1. days_overdue              — how many days past the original due date
  2. original_priority         — one-hot encoded (High / Medium / Low)
  3. historical_completion_rate — fraction of past tasks completed on time
  4. typical_completion_hour   — user's modal completion hour (0-23)
  5. current_pending_count     — number of incomplete tasks at reschedule time
  6. rescheduled_day           — one-hot encoded weekday of the new date (0-6)

Target:
  completed_by_suggested (bool) — was the task done by the new due date?

Run:
  python train_model.py [username]
"""

import sys
import numpy as np
from datetime import date, timedelta
from app import app, db
from app import User, Task

# ── Synthetic training data generator ────────────────────────────────────────
# In production this would come from real TaskHistory rows.
# We generate plausible synthetic rows here so the model trains on first run.

def build_dataset(user_id):
    """
    Extract feature matrix X and target vector y from TaskHistory.
    Falls back to synthetic data if insufficient real rows exist.
    """
    # No real TaskHistory table in the monolith — use synthetic data only
    rows = []

    real_data = []
    for r in rows:
        if r.days_overdue is None or r.new_due_date is None:
            continue
        real_data.append({
            'days_overdue':     r.days_overdue,
            'priority':         r.priority_label or 'Medium',
            'new_due_date':     r.new_due_date,
            'completed':        int(r.completed_by_suggested),
        })

    if len(real_data) < 30:
        print(f"  [info] Only {len(real_data)} real reschedule rows — "
              "augmenting with synthetic training data.")
        real_data += _synthetic_rows(300 - len(real_data))

    return _featurise(real_data, user_id)


def _synthetic_rows(n):
    """
    Generate plausible synthetic reschedule rows for bootstrapping.
    Logic mirrors real-world patterns:
      - Tasks rescheduled 1-2 days out are completed at ~75%
      - High-priority tasks have ~80% completion
      - Low-priority tasks with many pending have ~40% completion
    """
    rng  = np.random.default_rng(42)
    rows = []
    priorities = ['High', 'Medium', 'Low']
    today = date.today()

    for _ in range(n):
        days_over  = int(rng.integers(1, 15))
        priority   = rng.choice(priorities, p=[0.35, 0.45, 0.20])
        gap        = int(rng.integers(1, 8))  # days until new due date
        new_date   = today - timedelta(days=int(rng.integers(1, 90)))

        base  = {'High': 0.78, 'Medium': 0.60, 'Low': 0.42}[priority]
        decay = max(0, 1 - days_over * 0.03)
        boost = max(0, 1 - gap * 0.04)
        prob  = min(0.95, base * decay + boost * 0.10)

        rows.append({
            'days_overdue': days_over,
            'priority':     priority,
            'new_due_date': new_date,
            'completed':    int(rng.random() < prob),
        })
    return rows


def _featurise(rows, user_id):
    """
    Build numpy arrays X, y from raw row dicts.
    Applies one-hot encoding for priority and rescheduled_day.
    """
    # Completion rate from Task table
    tasks     = Task.query.filter_by(user_id=user_id).all()
    total     = len(tasks)
    done      = sum(1 for t in tasks if t.completed)
    comp_rate = done / total if total else 0.5

    # Typical completion hour from history
    completed_tasks = [t for t in tasks if t.completed and t.completed_at]
    if completed_tasks:
        hours = [t.completed_at.hour for t in completed_tasks]
        typical_hour = max(set(hours), key=hours.count)
    else:
        typical_hour = 10

    pending_count = sum(1 for t in tasks if not t.completed)

    priority_map = {'High': 0, 'Medium': 1, 'Low': 2}
    X_rows, y = [], []

    for r in rows:
        p_idx = priority_map.get(r['priority'], 1)
        p_ohe = [1 if i == p_idx else 0 for i in range(3)]  # one-hot priority

        nd    = r['new_due_date']
        dow   = nd.weekday() if isinstance(nd, date) else 0
        d_ohe = [1 if i == dow else 0 for i in range(7)]    # one-hot weekday

        row = [
            r['days_overdue'],    # feature 1
            *p_ohe,               # features 2a-c (one-hot: High/Medium/Low)
            comp_rate,            # feature 3
            typical_hour,         # feature 4
            pending_count,        # feature 5
            *d_ohe,               # features 6a-g (one-hot: Mon-Sun)
        ]
        X_rows.append(row)
        y.append(r['completed'])

    return np.array(X_rows, dtype=float), np.array(y, dtype=int)


# ── Training pipeline ─────────────────────────────────────────────────────────

def train(username='demo'):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (accuracy_score, precision_score,
                                 recall_score, f1_score, classification_report)

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found.")
            sys.exit(1)

        print('\n' + '═'*60)
        print('  TaskMind · Reschedule Success Prediction Model')
        print('  scikit-learn · Logistic Regression')
        print('═'*60)

        # ── Data preparation ──────────────────────────────────────────────
        print('\n[1/4] Data preparation...')
        X, y = build_dataset(user.id)
        print(f"  Samples        : {len(y)}")
        print(f"  Features       : {X.shape[1]}")
        print(f"  Positive class : {y.sum()} ({y.mean()*100:.1f}% completed by suggested date)")
        print(f"  Negative class : {(1-y).sum()} ({(1-y).mean()*100:.1f}% not completed)")

        feature_names = [
            'days_overdue',
            'priority_High', 'priority_Medium', 'priority_Low',
            'historical_completion_rate',
            'typical_completion_hour',
            'current_pending_count',
            'rescheduled_Mon', 'rescheduled_Tue', 'rescheduled_Wed',
            'rescheduled_Thu', 'rescheduled_Fri', 'rescheduled_Sat', 'rescheduled_Sun',
        ]
        print(f"\n  Features ({len(feature_names)}):")
        for i, name in enumerate(feature_names, 1):
            print(f"    {i:2}. {name}")

        # ── Feature scaling ───────────────────────────────────────────────
        print('\n[2/4] Feature engineering & scaling (StandardScaler)...')
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)
        scaler  = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test  = scaler.transform(X_test)
        print(f"  Train set : {len(y_train)} samples")
        print(f"  Test set  : {len(y_test)} samples")
        print(f"  Scaling   : mean={scaler.mean_[:3].round(2)} ... (first 3 features)")

        # ── Model training ────────────────────────────────────────────────
        print('\n[3/4] Training Logistic Regression...')
        model = LogisticRegression(
            C=1.0, max_iter=1000, solver='lbfgs', random_state=42)
        model.fit(X_train, y_train)
        print(f"  Solver        : lbfgs")
        print(f"  Regularisation: C=1.0  (L2 penalty)")
        print(f"  Iterations    : {model.n_iter_[0]}")

        # ── Evaluation ────────────────────────────────────────────────────
        print('\n[4/4] Evaluation on held-out test set...')
        y_pred = model.predict(X_test)
        acc  = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec  = recall_score(y_test, y_pred, zero_division=0)
        f1   = f1_score(y_test, y_pred, zero_division=0)

        print(f"\n  {'Metric':<22} {'Score':>8}")
        print(f"  {'─'*30}")
        print(f"  {'Accuracy':<22} {acc:>8.4f}  ({acc*100:.1f}%)")
        print(f"  {'Precision':<22} {prec:>8.4f}  ({prec*100:.1f}%)")
        print(f"  {'Recall':<22} {rec:>8.4f}  ({rec*100:.1f}%)")
        print(f"  {'F1-Score':<22} {f1:>8.4f}  ({f1*100:.1f}%)")

        print(f"\n  Detailed classification report:")
        print('  ' + '-'*42)
        report = classification_report(
            y_test, y_pred,
            target_names=['Not completed', 'Completed by date'],
        )
        for line in report.strip().split('\n'):
            print('  ' + line)

        # ── Feature importance ────────────────────────────────────────────
        print(f"\n  Top feature coefficients (logistic regression weights):")
        coefs = list(zip(feature_names, model.coef_[0]))
        coefs.sort(key=lambda x: abs(x[1]), reverse=True)
        for name, coef in coefs[:7]:
            bar = '█' * int(abs(coef) * 10)
            sign = '+' if coef > 0 else '-'
            print(f"  {name:<34} {sign}{abs(coef):.3f}  {bar}")

        print('\n' + '═'*60)
        print('  Model training complete.')
        print('═'*60 + '\n')

        return model, scaler


if __name__ == '__main__':
    username = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    train(username)
