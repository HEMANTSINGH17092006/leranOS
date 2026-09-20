import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "learnos-super-secret-key-2026-prod-secure")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'learning.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ML Models and Data paths
    MODELS_DIR = BASE_DIR / "models"
    DATA_DIR = BASE_DIR / "data"
    
    SCALER_PATH = MODELS_DIR / "scaler.pkl"
    KMEANS_PATH = MODELS_DIR / "kmeans.pkl"
    METADATA_PATH = MODELS_DIR / "model_metadata.json"
    LEARNING_DATA_PATH = DATA_DIR / "learning_data.csv"
    QUIZ_QUESTIONS_PATH = DATA_DIR / "quiz_questions.json"
    
    # Session configurations
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
