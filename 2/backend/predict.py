"""
Inference — load model, extract features, compute feature importance as SHAP proxy.
Uses sklearn GradientBoostingClassifier; no xgboost or shap library needed.
"""
import os, json
import numpy as np
import joblib
from features import extract_features

MODEL_DIR   = os.path.join(os.path.dirname(__file__), "../model")
MODEL_PATH  = os.path.join(MODEL_DIR, "phishing_model.pkl")
FNAMES_PATH = os.path.join(MODEL_DIR, "feature_names.json")

_pipeline      = None
_feature_names = None
_importances   = None   # global feature importances from trained model


def _load():
    global _pipeline, _feature_names, _importances
    if _pipeline is not None:
        return

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model not found. Run: cd backend && python3 train.py"
        )

    _pipeline = joblib.load(MODEL_PATH)
    with open(FNAMES_PATH) as f:
        _feature_names = json.load(f)

    # Pre-extract global feature importances from the GBM
    clf = _pipeline.named_steps["clf"]
    if hasattr(clf, "feature_importances_"):
        _importances = clf.feature_importances_
    else:
        _importances = np.ones(len(_feature_names)) / len(_feature_names)


def _local_shap_proxy(X_row: np.ndarray, prob_phishing: float) -> np.ndarray:
    """
    Lightweight local feature attribution without shap library.
    Combines global feature importance with the feature value's deviation
    from a neutral baseline (0.5 for binary features, 0 for counts).
    Sign is assigned based on whether the feature increases phishing risk.
    """
    if _importances is None:
        return np.zeros(len(_feature_names))

    PHISHING_DIRECTION = {
        "url_length", "num_dots", "num_hyphens", "num_digits", "num_special_chars",
        "num_slashes", "url_depth", "domain_length", "subdomain_count",
        "has_ip_address", "tld_suspicious", "tld_in_path", "has_at_symbol",
        "has_double_slash", "https_token_in_domain", "url_entropy", "digit_ratio",
        "path_length", "query_length", "num_query_params", "brand_in_subdomain",
        "brand_in_path", "suspicious_words_count", "has_port", "domain_has_hyphen",
        "num_subdomains_gt2", "url_has_encoded_chars",
        "brand_typosquat", "brand_exact_in_domain",
    }

    # Attribution sign: does this feature's CURRENT VALUE push toward phishing?
    #   Positive  → feature value pushes toward PHISHING  (red bar)
    #   Negative  → feature value pushes toward LEGITIMATE (blue bar)
    # We do NOT multiply by prob_phishing so absent phishing features
    # correctly show as blue (pushing toward legitimate).
    vals  = X_row.flatten()
    attrs = []
    for i, (name, v) in enumerate(zip(_feature_names, vals)):
        imp = float(_importances[i]) if i < len(_importances) else 0.0
        direction = 1.0 if name in PHISHING_DIRECTION else -1.0
        # Normalise value to a signed deviation
        # Binary/ratio (0-1): centre at 0.5 so 0 → -0.5, 1 → +0.5
        # Counts: log-scale relative to 0 baseline
        if v <= 1.0:
            norm = v - 0.5
        else:
            norm = np.log1p(v) / 10.0
        attrs.append(imp * direction * norm)

    return np.array(attrs)


def predict(url: str) -> dict:
    """
    Returns:
        classification  : "phishing" | "legitimate"
        risk_score      : int 0–100
        confidence      : float 0–100
        features        : {name: value}
        shap_features   : [{name, value, shap_value}, ...]   top 5
    """
    _load()

    raw_features = extract_features(url)
    X_row = np.array([[raw_features.get(f, 0.0) for f in _feature_names]])

    scaler = _pipeline.named_steps["scaler"]
    clf    = _pipeline.named_steps["clf"]

    X_scaled      = scaler.transform(X_row)
    prob_phishing = float(clf.predict_proba(X_scaled)[0][1])
    prediction    = int(clf.predict(X_scaled)[0])

    classification = "phishing" if prediction == 1 else "legitimate"
    risk_score     = round(prob_phishing * 100)
    confidence     = round(max(prob_phishing, 1 - prob_phishing) * 100, 1)

    # Hard rule: typosquatting of a known brand is always phishing,
    # regardless of other URL features being clean.
    if raw_features.get("brand_typosquat", 0) == 1.0:
        classification = "phishing"
        risk_score     = max(risk_score, 85)
        prob_phishing  = max(prob_phishing, 0.85)
        confidence     = round(prob_phishing * 100, 1)

    # Local attribution scores
    attr = _local_shap_proxy(X_row, prob_phishing)

    # Top 5 features by absolute attribution
    indices = np.argsort(np.abs(attr))[::-1][:5]
    shap_features = [
        {
            "name":       _feature_names[i],
            "value":      round(float(X_row[0][i]), 4),
            "shap_value": round(float(attr[i]), 4),
        }
        for i in indices
    ]

    return {
        "classification": classification,
        "risk_score":     risk_score,
        "confidence":     confidence,
        "features":       {k: round(v, 4) for k, v in raw_features.items()},
        "shap_features":  shap_features,
    }
