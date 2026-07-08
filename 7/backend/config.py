"""
config.py — Application configuration settings
Student Study Planner and Time Management System
Nwachukwu Chibuzor Benjamin | 22/9799 | Computer Science, Caleb University
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "caleb-study-planner-secret-2024")
    JWT_EXPIRY_HOURS = 24

    # Database
    DB_PATH = os.path.join(BASE_DIR, "..", "data", "study_planner.db")

    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://0.0.0.0:5500",
        "null",
    ]

    # Vector store directory (for Chroma)
    VECTOR_STORE_DIR = os.path.join(BASE_DIR, "..", "data", "vector_store")

    # Embedding model — lightweight, offline-capable
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    # Adaptive engine thresholds
    HIGH_FOCUS_THRESHOLD = 0.75     # completion rate above which user is "focused"
    LOW_FOCUS_THRESHOLD = 0.40      # completion rate below which user needs support

    # Session / token
    TOKEN_HEADER = "X-Auth-Token"

    # Pagination
    DEFAULT_PAGE_SIZE = 20


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


# Active config
active_config = DevelopmentConfig
