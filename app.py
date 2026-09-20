import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, session
from config import Config, INSTANCE_DIR, BASE_DIR
from database import db, init_db
from database.models import User, QuizQuestion
from routes import register_blueprints

def _check_and_seed_db(app):
    with app.app_context():
        try:
            # Check if quiz questions table has data; if empty, seed default dataset
            if not QuizQuestion.query.first():
                from database.seed import seed_database
                print("[LearnOS] First boot / Empty database detected. Seeding initial data...")
                seed_database()
                print("[LearnOS] Seeding complete.")
        except Exception as e:
            print(f"[LearnOS] Seeding check notice: {e}")

def create_app(config_class=Config):
    app = Flask(
        __name__,
        instance_path=str(INSTANCE_DIR),
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
    )
    app.config.from_object(config_class)
    
    # Ensure instance directory exists
    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[LearnOS] Instance directory notice: {e}")
    
    # Initialize Database
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[LearnOS] db.create_all notice: {e}")
        
    _check_and_seed_db(app)
        
    # Register Blueprints
    register_blueprints(app)
    
    # Global context processors for templates
    @app.context_processor
    def inject_globals():
        current_user = None
        if "user_id" in session:
            try:
                current_user = db.session.get(User, session["user_id"])
            except Exception:
                current_user = None
        return {
            "current_user": current_user,
            "app_name": "LearnOS"
        }
        
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500
        
    return app

# Main WSGI app object
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n========================================================")
    print(f"  LearnOS - AI Personalised Learning Platform")
    print(f"  Serving at: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
