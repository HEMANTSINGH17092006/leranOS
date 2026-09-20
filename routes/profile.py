import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from database.models import User, StudentProfile, LearningGoal, LearnerClusterResult, QuizAttempt
from routes.auth import login_required, get_current_user

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    profile = user.profile
    cluster_res = user.cluster_result
    goals = LearningGoal.query.filter_by(user_id=user.id).order_by(LearningGoal.created_at.desc()).all()
    
    attempts_count = QuizAttempt.query.filter_by(user_id=user.id).count()
    if attempts_count == 0 and cluster_res:
        attempts_count = cluster_res.total_attempts
        
    if cluster_res:
        mastery_score = round(cluster_res.mastery_score, 1)
        quiz_accuracy = round(cluster_res.quiz_accuracy, 1)
        avg_time = round(cluster_res.avg_time_per_question, 1)
        prev_score = round(cluster_res.previous_score, 1)
        study_time = round(cluster_res.total_study_time, 1)
        cluster_label = cluster_res.cluster_label
        cluster_id = cluster_res.cluster_id
        learning_level = cluster_res.overall_learning_level
        weak_areas = json.loads(cluster_res.weak_areas_json) if cluster_res.weak_areas_json else []
        subject_scores = json.loads(cluster_res.subject_scores_json) if cluster_res.subject_scores_json else {}
    else:
        mastery_score = 68.0
        quiz_accuracy = 74.0
        avg_time = 75.4
        prev_score = 49.8
        study_time = 12.4
        cluster_label = "Developing Learner"
        cluster_id = 1
        learning_level = "Developing Learner"
        weak_areas = ["Functions", "Time Management"]
        subject_scores = {
            "Python": 72.0,
            "Data Structures": 61.0,
            "Algorithms": 54.0,
            "Database": 48.0,
            "Web Development": 66.0
        }

    # Subject colors mapping
    subject_palette = {
        "Python": {"color": "#3b82f6", "bg": "bg-primary"},
        "Data Structures": {"color": "#06b6d4", "bg": "bg-info"},
        "Algorithms": {"color": "#f97316", "bg": "bg-warning"},
        "Database": {"color": "#ef4444", "bg": "bg-danger"},
        "Web Development": {"color": "#10b981", "bg": "bg-success"}
    }
    
    formatted_subjects = []
    for sub, score in subject_scores.items():
        pal = subject_palette.get(sub, {"color": "#6366f1", "bg": "bg-primary"})
        formatted_subjects.append({
            "name": sub,
            "score": round(score, 1),
            "color": pal["color"],
            "bg_class": pal["bg"]
        })
        
    preferred_subs = profile.preferred_subjects if profile and profile.preferred_subjects else "Python, Data Structures"
    areas_to_improve_str = ", ".join([w.split(" (")[0] for w in weak_areas[:2]]) if weak_areas else "Functions, Time Management"

    return render_template(
        "profile.html",
        user=user,
        profile=profile,
        mastery_score=mastery_score,
        quiz_accuracy=quiz_accuracy,
        avg_time=avg_time,
        prev_score=prev_score,
        study_time=study_time,
        attempts_count=attempts_count,
        cluster_label=cluster_label,
        cluster_id=cluster_id,
        learning_level=learning_level,
        goals=goals,
        preferred_subs=preferred_subs,
        areas_to_improve_str=areas_to_improve_str,
        subjects=formatted_subjects,
        current_date=datetime.now().strftime("%B %d, %Y")
    )
