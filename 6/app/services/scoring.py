"""Multi-criteria ranking and skill-gap analysis."""
import json
from typing import List, Dict, Any
from fuzzywuzzy import fuzz
from app.config import settings


def normalize_experience(years: float, min_required: float = 1.0) -> float:
    """
    Score experience 0-1.
    - Below minimum: proportional penalty
    - At/above minimum: linear up to MAX_EXPERIENCE_YEARS
    """
    if years <= 0:
        return 0.0
    if years < min_required:
        return (years / min_required) * 0.5
    score = min(years / settings.MAX_EXPERIENCE_YEARS, 1.0)
    return round(score, 4)


def skill_match_score(
    candidate_skills: List[str],
    required_skills: List[str],
) -> tuple[float, List[str], List[str]]:
    """
    Compare candidate skills to required skills using fuzzy matching.
    Returns (score, matched_skills, missing_skills).
    """
    if not required_skills:
        return 1.0, candidate_skills, []

    matched = []
    missing = []
    candidate_lower = [s.lower() for s in candidate_skills]

    for req in required_skills:
        req_lower = req.lower()
        best_ratio = 0
        for cand in candidate_lower:
            ratio = fuzz.partial_ratio(req_lower, cand)
            if ratio > best_ratio:
                best_ratio = ratio
        if best_ratio >= 75:
            matched.append(req)
        else:
            missing.append(req)

    score = len(matched) / len(required_skills) if required_skills else 1.0
    return round(score, 4), matched, missing


def generate_skill_gap_summary(
    candidate_skills: List[str],
    required_skills: List[str],
    matched: List[str],
    missing: List[str],
    exp_years: float,
    min_exp: float,
) -> str:
    """Generate a human-readable skill gap summary."""
    parts = []

    match_pct = int((len(matched) / len(required_skills)) * 100) if required_skills else 100

    if match_pct >= 80:
        parts.append(f"Strong skill alignment ({match_pct}% match).")
    elif match_pct >= 50:
        parts.append(f"Moderate skill alignment ({match_pct}% match).")
    else:
        parts.append(f"Significant skill gaps ({match_pct}% match).")

    if missing:
        top_missing = missing[:3]
        parts.append(f"Missing: {', '.join(top_missing)}.")

    if exp_years < min_exp:
        parts.append(
            f"Experience ({exp_years:.1f} yrs) is below requirement ({min_exp:.1f} yrs)."
        )
    elif exp_years >= min_exp * 2:
        parts.append(f"Exceeds experience requirement ({exp_years:.1f} yrs).")

    # Domain-specific insights
    hair_skills = {"hair", "beauty", "salon", "wig", "lash", "cosmetology"}
    cand_lower = {s.lower() for s in candidate_skills}
    if not hair_skills.intersection(cand_lower):
        parts.append("No hair/beauty industry background detected.")
    else:
        parts.append("Has relevant hair/beauty industry experience.")

    return " ".join(parts)


def calculate_total_score(
    skill_score: float,
    exp_score: float,
    proximity_score: float,
) -> float:
    """Weighted total score."""
    total = (
        settings.WEIGHT_SKILL * skill_score
        + settings.WEIGHT_EXPERIENCE * exp_score
        + settings.WEIGHT_PROXIMITY * proximity_score
    )
    return round(min(total, 1.0), 4)


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort candidates by total_score descending, assign ranks."""
    ranked = sorted(candidates, key=lambda c: c["total_score"], reverse=True)
    for i, c in enumerate(ranked):
        c["rank"] = i + 1
    return ranked
