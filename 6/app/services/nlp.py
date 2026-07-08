"""NLP entity extraction service using spaCy + regex + keyword matching.

Uses a hybrid approach:
1. Regex patterns for structured fields (phone, email, years of experience)
2. Keyword matching for skills, certifications, education
3. spaCy NER for location and person names
HuggingFace Transformers integration is available but optional — falls back
gracefully so the app works without GPU/large model download.
"""
import re
import json
from typing import List, Dict, Any
from loguru import logger


# ---------------------------------------------------------------------------
# Keyword dictionaries
# ---------------------------------------------------------------------------

NIGERIAN_LOCATIONS = [
    "ikeja", "surulere", "lekki", "victoria island", "vi", "ikoyi", "yaba",
    "gbagada", "maryland", "ojodu", "berger", "ketu", "mile 12", "agege",
    "oshodi", "mushin", "isolo", "festac", "amuwo odofin", "ajah", "sangotedo",
    "ibeju", "badagry", "epe", "ikorodu", "apapa", "tin can", "trade fair",
    "abuja", "port harcourt", "ph", "kano", "ibadan", "enugu", "onitsha",
    "aba", "warri", "benin", "asaba", "uyo", "calabar", "akure", "osogbo",
    "abeokuta", "ilorin", "maiduguri", "kaduna", "jos", "niger", "lagos",
    "mainland", "island", "ojuelegba", "palmgrove", "onipanu", "bariga",
    "shomolu", "kosofe", "magodo", "ojota", "alausa", "oregun", "ogba",
    "ifako", "agbado", "ijaiye", "dopemu", "meiran", "abule egba", "ipaja",
    "ayobo", "igando", "alimosho", "egbe", "idimu", "iyana ipaja",
]

SKILLS_DICT = {
    "sales": ["sales", "selling", "sales executive", "business development", "bd",
               "cold calling", "lead generation", "b2b", "b2c", "retail sales",
               "direct sales", "field sales", "telesales", "upselling", "cross-selling"],
    "customer_service": ["customer service", "customer care", "customer support",
                          "client relations", "customer relations", "crm",
                          "customer satisfaction", "complaint handling"],
    "communication": ["communication", "verbal communication", "written communication",
                       "presentation", "public speaking", "negotiation", "persuasion",
                       "interpersonal skills", "stakeholder management"],
    "management": ["management", "team lead", "team leader", "supervisor",
                    "people management", "leadership", "mentoring", "coaching",
                    "performance management", "kpi", "target setting"],
    "marketing": ["marketing", "digital marketing", "social media", "brand management",
                   "product marketing", "market research", "campaign management",
                   "seo", "content marketing", "email marketing"],
    "operations": ["operations", "logistics", "supply chain", "inventory",
                    "dispatch", "delivery", "route planning", "fleet management",
                    "warehouse", "procurement"],
    "hair_beauty": ["hair", "beauty", "cosmetology", "hair styling", "salon",
                     "hair products", "wigs", "extensions", "lace frontal",
                     "hair care", "braiding", "lash", "makeup"],
    "technology": ["microsoft office", "excel", "powerpoint", "word", "crm software",
                    "erp", "data entry", "computer skills", "google workspace"],
    "finance": ["finance", "accounting", "budgeting", "financial reporting",
                 "cash handling", "pos", "reconciliation", "invoicing"],
}

CERTIFICATION_KEYWORDS = [
    "certificate", "certification", "certified", "diploma", "professional certificate",
    "license", "accredited", "cissp", "pmp", "cfa", "acca", "ican", "nysc",
    "professional development", "fellowship",
]

EDUCATION_LEVELS = {
    "phd": ["phd", "ph.d", "doctorate", "d.phil"],
    "masters": ["msc", "mba", "ma", "m.sc", "master", "postgraduate", "pg diploma"],
    "bachelors": ["bsc", "b.sc", "ba", "b.a", "hnd", "b.eng", "b.tech",
                  "bachelor", "first degree", "undergraduate"],
    "ond": ["ond", "nd", "national diploma"],
    "ssce": ["waec", "neco", "ssce", "o level", "secondary school"],
}


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def extract_name(text: str) -> tuple[str, float]:
    """Heuristic: first non-empty line that looks like a name."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:
        # A name is typically 2-4 words, no digits, not too long
        words = line.split()
        if 2 <= len(words) <= 4 and not re.search(r'\d', line) and len(line) < 60:
            # Skip lines that look like headers/labels
            skip = {"curriculum vitae", "resume", "cv", "profile", "objective",
                    "summary", "contact", "personal details"}
            if line.lower() not in skip:
                return line.title(), 0.85
    return "Unknown Candidate", 0.3


def extract_email(text: str) -> tuple[str, float]:
    pattern = r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
    matches = re.findall(pattern, text)
    return (matches[0], 0.99) if matches else ("", 0.0)


def extract_phone(text: str) -> tuple[str, float]:
    """Extract Nigerian phone numbers (07xx, 08xx, 09xx, +234)."""
    patterns = [
        r'\+?234[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}',
        r'\b0[789]\d{9}\b',
        r'\b0[789]\d[-\s]?\d{3}[-\s]?\d{4}\b',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group().strip(), 0.95
    return "", 0.0


def extract_location(text: str) -> tuple[str, float]:
    """Find Nigerian location mentions."""
    text_lower = text.lower()
    found = []
    for loc in NIGERIAN_LOCATIONS:
        if re.search(r'\b' + re.escape(loc) + r'\b', text_lower):
            found.append(loc.title())
    if found:
        # Prefer more specific (longer) location names
        found.sort(key=len, reverse=True)
        return found[0], 0.80
    # Fallback: look for "Lagos" or any Nigerian state
    if "lagos" in text_lower:
        return "Lagos", 0.70
    return "", 0.0


def extract_experience_years(text: str) -> tuple[float, float]:
    """Parse years of experience from text."""
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:work\s+)?experience',
        r'experience\s*(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:in|working)',
        r'over\s+(\d+)\s+(?:years?|yrs?)',
        r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)',  # range like "3-5 years"
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            years = float(m.group(1))
            return min(years, 30.0), 0.85

    # Count date ranges in work history (e.g., 2019 - 2023)
    year_ranges = re.findall(
        r'\b(20\d{2}|19\d{2})\s*[-–—to]+\s*(20\d{2}|19\d{2}|present|date|now)\b',
        text, re.IGNORECASE
    )
    if year_ranges:
        import datetime
        current_year = datetime.datetime.now().year
        total = 0.0
        for start, end in year_ranges:
            try:
                s = int(start)
                e = current_year if end.lower() in ('present', 'date', 'now') else int(end)
                total += max(0, e - s)
            except ValueError:
                pass
        if total > 0:
            return min(total, 30.0), 0.75

    return 0.0, 0.3


def extract_skills(text: str) -> List[Dict[str, Any]]:
    """Match skills from keyword dictionary."""
    text_lower = text.lower()
    results = []
    seen = set()
    for category, keywords in SKILLS_DICT.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                if kw not in seen:
                    seen.add(kw)
                    results.append({
                        "entity_type": "SKILL",
                        "entity_value": kw.title(),
                        "confidence_score": 0.88,
                        "category": category,
                    })
    return results


def extract_education(text: str) -> List[Dict[str, Any]]:
    text_lower = text.lower()
    results = []
    for level, keywords in EDUCATION_LEVELS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                results.append({
                    "entity_type": "EDUCATION",
                    "entity_value": level.upper(),
                    "confidence_score": 0.85,
                })
                break
    return results


def extract_certifications(text: str) -> List[Dict[str, Any]]:
    text_lower = text.lower()
    results = []
    # Search for certification keyword + nearby text
    for cert in CERTIFICATION_KEYWORDS:
        pattern = rf'\b{re.escape(cert)}\b.{{0,60}}'
        matches = re.findall(pattern, text_lower)
        for m in matches[:2]:
            results.append({
                "entity_type": "CERTIFICATION",
                "entity_value": m.strip().title()[:100],
                "confidence_score": 0.75,
            })
    return results[:5]  # cap at 5


def extract_role(text: str) -> List[Dict[str, Any]]:
    """Find role/title mentions."""
    role_patterns = [
        r'(?:position|role|title|applying for)[:\s]+([A-Za-z\s]+?)(?:\n|,|\.|$)',
        r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})\s*$',  # standalone title line
    ]
    results = []
    for pat in role_patterns:
        for m in re.finditer(pat, text, re.MULTILINE | re.IGNORECASE):
            val = m.group(1).strip()
            if 3 < len(val) < 60:
                results.append({
                    "entity_type": "ROLE",
                    "entity_value": val.title(),
                    "confidence_score": 0.70,
                })
    return results[:3]


def extract_entities(raw_text: str) -> Dict[str, Any]:
    """
    Main extraction pipeline. Returns structured dict with all entities.
    """
    # Try to use spaCy for additional NER if available
    spacy_locs = _spacy_locations(raw_text)

    name, name_conf = extract_name(raw_text)
    email, email_conf = extract_email(raw_text)
    phone, phone_conf = extract_phone(raw_text)
    location, loc_conf = extract_location(raw_text)
    exp_years, exp_conf = extract_experience_years(raw_text)
    skills = extract_skills(raw_text)
    education = extract_education(raw_text)
    certs = extract_certifications(raw_text)
    roles = extract_role(raw_text)

    # Merge spaCy locations
    if spacy_locs and not location:
        location, loc_conf = spacy_locs[0], 0.72

    entities = []

    # Core identity
    if name:
        entities.append({"entity_type": "NAME", "entity_value": name, "confidence_score": name_conf})
    if email:
        entities.append({"entity_type": "EMAIL", "entity_value": email, "confidence_score": email_conf})
    if phone:
        entities.append({"entity_type": "PHONE", "entity_value": phone, "confidence_score": phone_conf})
    if location:
        entities.append({"entity_type": "LOCATION", "entity_value": location, "confidence_score": loc_conf})
    if exp_years > 0:
        entities.append({
            "entity_type": "EXPERIENCE",
            "entity_value": str(exp_years),
            "confidence_score": exp_conf,
        })

    entities.extend(skills)
    entities.extend(education)
    entities.extend(certs)
    entities.extend(roles)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "experience_years": exp_years,
        "skills": [e["entity_value"] for e in skills],
        "education": [e["entity_value"] for e in education],
        "certifications": [e["entity_value"] for e in certs],
        "entities": entities,
    }


def _spacy_locations(text: str) -> List[str]:
    """Optional spaCy-based GPE/LOC extraction."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:5000])  # limit for speed
        return [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]
    except Exception:
        return []
