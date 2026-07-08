from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Lush Hair NG - Resume Screening System"
    DEBUG: bool = True
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/lush_hair.db"

    # Lush Hair Hub - Ikeja, Lagos
    HUB_LAT: float = 6.6018
    HUB_LONG: float = 3.3515
    HUB_NAME: str = "Lush Hair NG HQ, Ikeja, Lagos"

    # Distance thresholds (km)
    PROXIMITY_GREEN: float = 5.0
    PROXIMITY_YELLOW: float = 15.0

    # Scoring weights
    WEIGHT_SKILL: float = 0.45
    WEIGHT_EXPERIENCE: float = 0.35
    WEIGHT_PROXIMITY: float = 0.20

    # Max experience years for normalization
    MAX_EXPERIENCE_YEARS: int = 15

    # Upload settings
    UPLOAD_DIR: Path = BASE_DIR / "app" / "uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".doc"]

    # Geocoding
    NOMINATIM_USER_AGENT: str = "lush_hair_resume_screener_v1"
    GEOCODE_TIMEOUT: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
