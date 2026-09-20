from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from database.models import User, StudentProfile
from routes.auth import login_required, get_current_user

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    profile = user.profile
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "update_profile":
            name = request.form.get("name", "").strip()
            degree = request.form.get("degree", "").strip()
            year = request.form.get("year", "").strip()
            target_score = request.form.get("target_score", "80")
            preferred = request.form.get("preferred_subjects", "").strip()
            
            if name:
                user.name = name
            if profile:
                if degree:
                    profile.degree = degree
                if year:
                    profile.year = year
                if preferred:
                    profile.preferred_subjects = preferred
                try:
                    profile.target_mastery_score = float(target_score)
                except ValueError:
                    pass
            db.session.commit()
            flash("Profile settings updated successfully.", "success")
            return redirect(url_for("settings.index"))
            
        elif action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")
            
            if not user.check_password(current_pw):
                flash("Current password is incorrect.", "danger")
            elif len(new_pw) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "danger")
            else:
                user.set_password(new_pw)
                db.session.commit()
                flash("Password updated successfully.", "success")
            return redirect(url_for("settings.index"))
            
    return render_template(
        "settings.html",
        user=user,
        profile=profile,
        current_date=datetime.now().strftime("%B %d, %Y")
    )
