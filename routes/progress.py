import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from database.models import User, StudentProfile, QuizAttempt, LearnerClusterResult
from routes.auth import login_required, get_current_user

progress_bp = Blueprint("progress", __name__)

@progress_bp.route("/progress")
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    profile = user.profile
    cluster_res = user.cluster_result
    
    attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.asc()).all()
    
    # Historical series for Chart.js
    dates = [a.timestamp.strftime("%d %b") for a in attempts] if attempts else ["Day 1"]
    scores = [round(a.score, 1) for a in attempts] if attempts else [68.0]
    accuracies = [round(a.accuracy, 1) for a in attempts] if attempts else [74.0]
    avg_times = [round(a.avg_time_per_question, 1) for a in attempts] if attempts else [75.4]
    
    # Subject-wise attempts breakdown
    subject_counts = {}
    for a in attempts:
        subject_counts[a.subject] = subject_counts.get(a.subject, 0) + 1
        
    subject_scores = json.loads(cluster_res.subject_scores_json) if (cluster_res and cluster_res.subject_scores_json) else {
        "Python": 72.0, "Data Structures": 61.0, "Algorithms": 54.0, "Database": 48.0, "Web Development": 66.0
    }
    
    mastery_score = cluster_res.mastery_score if cluster_res else 68.0
    quiz_acc = cluster_res.quiz_accuracy if cluster_res else 74.0
    total_study_time = cluster_res.total_study_time if cluster_res else 12.4
    
    return render_template(
        "progress.html",
        user=user,
        profile=profile,
        cluster_res=cluster_res,
        mastery_score=mastery_score,
        quiz_acc=quiz_acc,
        total_study_time=total_study_time,
        attempts=list(reversed(attempts)),
        total_attempts=len(attempts),
        dates_json=json.dumps(dates),
        scores_json=json.dumps(scores),
        accuracies_json=json.dumps(accuracies),
        avg_times_json=json.dumps(avg_times),
        subject_scores_json=json.dumps(subject_scores),
        subject_counts_json=json.dumps(subject_counts),
        current_date=datetime.now().strftime("%B %d, %Y")
    )
