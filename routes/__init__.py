from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.profile import profile_bp
from routes.analysis import analysis_bp
from routes.recommendations import recommendations_bp
from routes.quiz import quiz_bp
from routes.progress import progress_bp
from routes.resources import resources_bp
from routes.settings import settings_bp
from routes.api import api_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
