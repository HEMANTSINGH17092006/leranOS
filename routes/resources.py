from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from database.models import User, StudentProfile, LearningResource
from routes.auth import login_required, get_current_user

resources_bp = Blueprint("resources", __name__)

@resources_bp.route("/resources")
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    subject_filter = request.args.get("subject", "All")
    type_filter = request.args.get("type", "All")
    
    query = LearningResource.query
    if subject_filter and subject_filter != "All":
        query = query.filter_by(subject=subject_filter)
    if type_filter and type_filter != "All":
        query = query.filter_by(resource_type=type_filter)
        
    resources = query.all()
    
    subjects = ["All", "Python", "Data Structures", "Algorithms", "Database", "Web Development"]
    types = ["All", "Notes", "Video", "Quiz", "Project", "Article"]
    
    return render_template(
        "resources.html",
        user=user,
        profile=user.profile,
        resources=resources,
        subjects=subjects,
        types=types,
        selected_subject=subject_filter,
        selected_type=type_filter,
        current_date=datetime.now().strftime("%B %d, %Y")
    )
