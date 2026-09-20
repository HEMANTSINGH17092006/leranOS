import os
from pathlib import Path
from flask import Flask, render_template, session
from config import Config
from database import db, init_db
from database.models import User
from routes import register_blueprints

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure instance directory exists
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    
    # Initialize Database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
    # Register Blueprints
    register_blueprints(app)
    
    # Global context processors for templates
    @app.context_processor
    def inject_globals():
        current_user = None
        if "user_id" in session:
            current_user = db.session.get(User, session["user_id"])
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

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n========================================================")
    print(f"  LearnOS - AI Personalised Learning Platform")
    print(f"  Serving at: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host="127.0.0.1", port=port, debug=True)
