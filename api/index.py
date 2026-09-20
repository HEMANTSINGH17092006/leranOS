import sys
from pathlib import Path

# Ensure the root project directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the WSGI Flask application
from app import app

# Expose WSGI handler for Vercel Serverless Functions
handler = app
