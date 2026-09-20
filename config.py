import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Detect serverless runtime (Vercel, AWS Lambda, etc.)
IS_SERVERLESS = bool(
    os.environ.get("VERCEL") 
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") 
    or os.environ.get("LAMBDA_TASK_ROOT")
)

# On serverless platforms (Vercel), writable storage is in system temp directory
if IS_SERVERLESS:
    INSTANCE_DIR = (Path(tempfile.gettempdir()) / "learnos_instance").resolve()
else:
    INSTANCE_DIR = (BASE_DIR / "instance").resolve()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "learnos-super-secret-key-2026-prod-secure")
    _db_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'learning.db'}"
    )
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    BASE_DIR = BASE_DIR
    INSTANCE_DIR = INSTANCE_DIR
    
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
