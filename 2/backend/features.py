"""
URL Feature Extraction — 32 structural features, no network calls required.
All features derived purely from the URL string using re, urllib.parse, math.
"""
import re
import math
from urllib.parse import urlparse, parse_qs
from typing import Dict

# ── Constants ────────────────────────────────────────────────────────────────

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "pw", "xyz", "info", "click",
    "top", "online", "site", "icu", "club", "live", "stream",
    "download", "review", "country", "kim", "science", "work",
}

BRAND_NAMES = {
    "paypal", "apple", "microsoft", "amazon", "google", "facebook",
    "netflix", "instagram", "twitter", "linkedin", "ebay", "wellsfargo",
    "chase", "bankofamerica", "citibank", "dropbox", "yahoo", "outlook",
    "office365", "icloud", "steam", "roblox", "walmart", "target",
}

SUSPICIOUS_WORDS = {
    "login", "signin", "verify", "update", "confirm", "secure",
    "account", "banking", "password", "credential", "suspend",
    "unlock", "validate", "authenticate", "billing", "renew",
    "alert", "recovery", "limited", "access", "click", "free",
}

IP_PATTERN = re.compile(
    r"((\d{1,3}\.){3}\d{1,3})"
)

# Brands used for typosquat detection (plain names, no TLD)
BRAND_NAMES_TYPO = [
    "paypal", "apple", "microsoft", "amazon", "google", "facebook",
    "netflix", "instagram", "twitter", "linkedin", "ebay", "wellsfargo",
    "chase", "dropbox", "yahoo", "outlook", "icloud", "steam",
    "roblox", "walmart", "whatsapp", "youtube", "tiktok", "snapchat",
]


def _edit_distance(a: str, b: str) -> int:
    """Fast iterative Levenshtein distance."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]


def _typosquat_score(hostname: str) -> float:
    """
    Returns 1.0 if the registered domain name looks like a typosquat of a
    known brand (edit distance 1–3, length ratio close to the brand name).
    Returns 0.0 otherwise.
    """
    # Use only the SLD part (e.g. "instajhgram" from "www.instajhgram.com")
    parts = hostname.rstrip(".").split(".")
    sld = parts[-2] if len(parts) >= 2 else parts[0]

    # Skip if the SLD IS a known brand (legitimate)
    if sld in BRAND_NAMES_TYPO:
        return 0.0

    for brand in BRAND_NAMES_TYPO:
        dist = _edit_distance(sld, brand)
        # Typosquat window: 1–3 edits AND similar length (within 4 chars)
        if 1 <= dist <= 3 and abs(len(sld) - len(brand)) <= 4:
            return 1.0
    return 0.0

# ── Helpers ───────────────────────────────────────────────────────────────────

def _entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    n = len(s)
    return -sum((f / n) * math.log2(f / n) for f in freq.values())


def _extract_tld(hostname: str) -> str:
    parts = hostname.rstrip(".").split(".")
    return parts[-1].lower() if parts else ""


def _extract_domain_parts(hostname: str):
    """Return (subdomains_str, registered_domain, tld)."""
    parts = hostname.split(".")
    if len(parts) >= 3:
        return ".".join(parts[:-2]), ".".join(parts[-2:]), parts[-1]
    elif len(parts) == 2:
        return "", hostname, parts[-1]
    else:
        return "", hostname, ""


# ── Main extractor ────────────────────────────────────────────────────────────

def extract_features(url: str) -> Dict[str, float]:
    """Return ordered dict of 30 numeric features for a URL string."""

    raw = url.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "http://" + raw

    try:
        parsed = urlparse(raw)
    except Exception:
        parsed = urlparse("http://unknown")

    scheme   = parsed.scheme or ""
    hostname = (parsed.hostname or "").lower()
    path     = parsed.path or ""
    query    = parsed.query or ""
    fragment = parsed.fragment or ""
    port     = parsed.port

    subdomains_str, reg_domain, tld = _extract_domain_parts(hostname)
    subdomain_count = len(subdomains_str.split(".")) if subdomains_str else 0

    full_url = raw.lower()
    url_len  = len(full_url)

    # Brand checks
    brand_in_subdomain = int(any(b in subdomains_str.lower() for b in BRAND_NAMES))
    brand_in_path      = int(any(b in path.lower() for b in BRAND_NAMES))

    # Suspicious keyword count in full URL
    suspicious_words_count = sum(1 for w in SUSPICIOUS_WORDS if w in full_url)

    query_params = parse_qs(query)

    features = {
        # ── URL structure ─────────────────────────────────────────
        "url_length":               float(url_len),
        "num_dots":                 float(full_url.count(".")),
        "num_hyphens":              float(full_url.count("-")),
        "num_digits":               float(sum(c.isdigit() for c in full_url)),
        "num_special_chars":        float(sum(c in "!@#$%^&*()_+=[]{}|;:',<>?`~" for c in full_url)),
        "num_slashes":              float(full_url.count("/")),
        "url_depth":                float(len([p for p in path.split("/") if p])),

        # ── Domain ────────────────────────────────────────────────
        "domain_length":            float(len(reg_domain)),
        "subdomain_count":          float(subdomain_count),
        "has_ip_address":           float(bool(IP_PATTERN.search(hostname))),
        "tld_suspicious":           float(tld.lower() in SUSPICIOUS_TLDS),
        "tld_in_path":              float(tld.lower() in path.lower()),

        # ── Lexical ───────────────────────────────────────────────
        "has_at_symbol":            float("@" in full_url),
        "has_double_slash":         float("//" in path),
        "https_token_in_domain":    float("https" in hostname),
        "url_entropy":              _entropy(full_url),
        "digit_ratio":              float(sum(c.isdigit() for c in full_url)) / max(url_len, 1),
        "letter_ratio":             float(sum(c.isalpha() for c in full_url)) / max(url_len, 1),

        # ── Path / Query ──────────────────────────────────────────
        "path_length":              float(len(path)),
        "query_length":             float(len(query)),
        "num_query_params":         float(len(query_params)),
        "fragment_present":         float(bool(fragment)),

        # ── Brand / Keywords ──────────────────────────────────────
        "brand_in_subdomain":       float(brand_in_subdomain),
        "brand_in_path":            float(brand_in_path),
        "suspicious_words_count":   float(suspicious_words_count),
        "has_port":                 float(port is not None),

        # ── Protocol / Misc ───────────────────────────────────────
        "is_https":                 float(scheme == "https"),
        "domain_has_hyphen":        float("-" in reg_domain),
        "num_subdomains_gt2":       float(subdomain_count > 2),
        "url_has_encoded_chars":    float("%" in full_url),

        # ── Typosquatting ─────────────────────────────────────────
        "brand_typosquat":          _typosquat_score(hostname),
        "brand_exact_in_domain":    float(any(b in reg_domain.split(".")[0] for b in BRAND_NAMES)
                                          and not any(b == reg_domain.split(".")[0] for b in BRAND_NAMES)),
    }

    return features


FEATURE_NAMES = list(extract_features("http://example.com").keys())
