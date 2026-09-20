import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, session
from database.models import User, StudentProfile, QuizAttempt, LearnerClusterResult, LearningGoal
from routes.auth import login_required, get_current_user

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    profile = user.profile
    cluster_res = user.cluster_result
    
    # Fetch recent quiz attempts for progress chart
    recent_attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.asc()).all()
    
    # Build chart data
    chart_labels = [f"Attempt {i+1}" for i in range(len(recent_attempts))] if recent_attempts else ["Attempt 1"]
    chart_scores = [round(a.score, 1) for a in recent_attempts] if recent_attempts else [68.0]
    chart_accuracies = [round(a.accuracy, 1) for a in recent_attempts] if recent_attempts else [74.0]
    
    # Calculate real stats from attempts or fallback to cluster_res
    attempts_count = len(recent_attempts)
    total_study_time = round(cluster_res.total_study_time if cluster_res else 12.4, 1)
    
    if cluster_res:
        mastery_score = round(cluster_res.mastery_score, 1)
        quiz_accuracy = round(cluster_res.quiz_accuracy, 1)
        avg_time = round(cluster_res.avg_time_per_question, 1)
        prev_score = round(cluster_res.previous_score, 1)
        cluster_label = cluster_res.cluster_label
        cluster_id = cluster_res.cluster_id
        learning_level = cluster_res.overall_learning_level
        insights = json.loads(cluster_res.insights_json) if cluster_res.insights_json else []
        recommendations = json.loads(cluster_res.recommendations_json) if cluster_res.recommendations_json else []
        weak_areas = json.loads(cluster_res.weak_areas_json) if cluster_res.weak_areas_json else []
        strengths = json.loads(cluster_res.strengths_json) if cluster_res.strengths_json else []
    else:
        mastery_score = 68.0
        quiz_accuracy = 74.0
        avg_time = 75.4
        prev_score = 49.8
        cluster_label = "Developing Learner"
        cluster_id = 1
        learning_level = "Developing Learner"
        insights = []
        recommendations = []
        weak_areas = ["Python Functions", "Data Structures", "Time Management"]
        strengths = ["Python basics", "Consistent attendance"]
        
    # Calculate score improvement delta
    score_delta = round(mastery_score - prev_score, 1)
    
    return render_template(
        "dashboard.html",
        user=user,
        profile=profile,
        cluster_res=cluster_res,
        mastery_score=mastery_score,
        quiz_accuracy=quiz_accuracy,
        total_study_time=total_study_time,
        total_attempts=attempts_count if attempts_count > 0 else (cluster_res.total_attempts if cluster_res else 8),
        avg_time=avg_time,
        prev_score=prev_score,
        score_delta=score_delta,
        cluster_label=cluster_label,
        cluster_id=cluster_id,
        learning_level=learning_level,
        insights=insights,
        recommendations=recommendations[:3],  # top 3 recommendations on dashboard
        weak_areas=weak_areas,
        strengths=strengths,
        chart_labels=json.dumps(chart_labels[-8:]),
        chart_scores=json.dumps(chart_scores[-8:]),
        chart_accuracies=json.dumps(chart_accuracies[-8:]),
        current_date=datetime.now().strftime("%B %d, %Y")
    )
