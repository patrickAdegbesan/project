"""Geospatial proximity service using Nominatim (OpenStreetMap) geocoding."""
import math
import time
from typing import Optional, Tuple
from functools import lru_cache
from loguru import logger
import requests
from app.config import settings


# Lagos-specific coordinate overrides for fast, accurate lookups
LAGOS_COORDS: dict[str, Tuple[float, float]] = {
    "ikeja": (6.6018, 3.3515),
    "surulere": (6.4969, 3.3572),
    "lekki": (6.4483, 3.5305),
    "lekki phase 1": (6.4338, 3.4695),
    "victoria island": (6.4281, 3.4219),
    "vi": (6.4281, 3.4219),
    "ikoyi": (6.4530, 3.4364),
    "yaba": (6.5076, 3.3742),
    "gbagada": (6.5530, 3.3886),
    "maryland": (6.5613, 3.3586),
    "ojodu": (6.6338, 3.3532),
    "berger": (6.6338, 3.3532),
    "ketu": (6.5867, 3.3918),
    "mile 12": (6.6051, 3.3858),
    "agege": (6.6138, 3.3213),
    "oshodi": (6.5513, 3.3501),
    "mushin": (6.5272, 3.3564),
    "isolo": (6.5159, 3.3416),
    "festac": (6.4621, 3.2748),
    "amuwo odofin": (6.4718, 3.2957),
    "ajah": (6.4694, 3.5697),
    "sangotedo": (6.4434, 3.6013),
    "ikorodu": (6.6194, 3.5050),
    "apapa": (6.4483, 3.3622),
    "tin can": (6.4369, 3.3221),
    "trade fair": (6.4769, 3.2840),
    "badagry": (6.4126, 2.8932),
    "epe": (6.5843, 3.9763),
    "ojota": (6.5875, 3.3939),
    "alausa": (6.6012, 3.3468),
    "oregun": (6.5994, 3.3408),
    "ogba": (6.6003, 3.3229),
    "ifako": (6.6330, 3.3413),
    "gbagada phase 2": (6.5530, 3.3886),
    "palmgrove": (6.5414, 3.3628),
    "onipanu": (6.5469, 3.3633),
    "bariga": (6.5387, 3.3931),
    "shomolu": (6.5413, 3.3878),
    "dopemu": (6.6010, 3.2985),
    "meiran": (6.6443, 3.2720),
    "abule egba": (6.6171, 3.2554),
    "ipaja": (6.6107, 3.2538),
    "ayobo": (6.6082, 3.2221),
    "igando": (6.5523, 3.2728),
    "alimosho": (6.6097, 3.2720),
    "egbe": (6.5564, 3.2757),
    "idimu": (6.5633, 3.2686),
    "iyana ipaja": (6.6004, 3.2576),
    "magodo": (6.6025, 3.3886),
    "ojuelegba": (6.5113, 3.3621),
    "lagos": (6.5244, 3.3792),
    "lagos island": (6.4530, 3.3958),
    "lagos mainland": (6.5019, 3.3774),
    "abuja": (9.0765, 7.3986),
    "port harcourt": (4.8156, 7.0498),
    "ph": (4.8156, 7.0498),
    "ibadan": (7.3775, 3.9470),
    "kano": (12.0022, 8.5920),
    "enugu": (6.4584, 7.5464),
    "onitsha": (6.1414, 6.7866),
    "warri": (5.5167, 5.7500),
    "benin": (6.3350, 5.6037),
    "calabar": (4.9517, 8.3220),
}


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in kilometres between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def distance_score(distance_km: float, max_km: float = 50.0) -> float:
    """Convert distance to 0-1 score (closer = higher)."""
    return max(0.0, 1.0 - distance_km / max_km)


@lru_cache(maxsize=512)
def geocode(location_str: str) -> Optional[Tuple[float, float]]:
    """
    Convert a location string to (lat, lon).
    1. Check local Lagos dictionary first (fast, no API call).
    2. Fall back to Nominatim API.
    """
    key = location_str.lower().strip()

    # Direct lookup
    if key in LAGOS_COORDS:
        return LAGOS_COORDS[key]

    # Partial match — check if any key is a substring
    for known, coords in LAGOS_COORDS.items():
        if known in key or key in known:
            return coords

    # Nominatim fallback
    return _nominatim_geocode(location_str)


def _nominatim_geocode(location_str: str) -> Optional[Tuple[float, float]]:
    """Call OpenStreetMap Nominatim for coordinates."""
    # Bias search toward Nigeria/Lagos
    query = location_str
    if "nigeria" not in query.lower() and "lagos" not in query.lower():
        query = f"{query}, Lagos, Nigeria"

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "ng",
    }
    headers = {"User-Agent": settings.NOMINATIM_USER_AGENT}

    try:
        time.sleep(1)  # Nominatim rate limit: 1 req/sec
        resp = requests.get(url, params=params, headers=headers,
                            timeout=settings.GEOCODE_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logger.warning(f"Nominatim geocoding failed for '{location_str}': {e}")

    return None


def get_proximity_info(
    location_str: str,
    hub_lat: float = settings.HUB_LAT,
    hub_lon: float = settings.HUB_LONG,
) -> dict:
    """
    Return full proximity info for a candidate location string.
    """
    coords = geocode(location_str) if location_str else None

    if coords is None:
        return {
            "lat": None,
            "lon": None,
            "distance_km": None,
            "proximity_score": 0.5,  # neutral score when unknown
            "color": "secondary",
            "geocoded": False,
        }

    lat, lon = coords
    dist = haversine(lat, lon, hub_lat, hub_lon)
    score = distance_score(dist)

    if dist < settings.PROXIMITY_GREEN:
        color = "success"
    elif dist < settings.PROXIMITY_YELLOW:
        color = "warning"
    else:
        color = "danger"

    return {
        "lat": lat,
        "lon": lon,
        "distance_km": round(dist, 2),
        "proximity_score": round(score, 4),
        "color": color,
        "geocoded": True,
    }
