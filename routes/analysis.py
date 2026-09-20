import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from database.models import User, StudentProfile, LearnerClusterResult, QuizAttempt
from routes.auth import login_required, get_current_user
from ml.learner_analysis import CLASS_BENCHMARKS

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/ai-analysis")
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    profile = user.profile
    cluster_res = user.cluster_result
    
    attempts_count = QuizAttempt.query.filter_by(user_id=user.id).count()
    if attempts_count == 0 and cluster_res:
        attempts_count = cluster_res.total_attempts

    if cluster_res:
        mastery_score = round(cluster_res.mastery_score, 1)
        quiz_accuracy = round(cluster_res.quiz_accuracy, 1)
        avg_time = round(cluster_res.avg_time_per_question, 1)
        prev_score = round(cluster_res.previous_score, 1)
        study_time = round(cluster_res.total_study_time, 1)
        confidence = round(cluster_res.confidence_score, 1)
        cluster_label = cluster_res.cluster_label
        cluster_id = cluster_res.cluster_id
        learning_level = cluster_res.overall_learning_level
        strengths = json.loads(cluster_res.strengths_json) if cluster_res.strengths_json else []
        weak_areas = json.loads(cluster_res.weak_areas_json) if cluster_res.weak_areas_json else []
        behaviour = json.loads(cluster_res.behaviour_json) if cluster_res.behaviour_json else {}
        insights = json.loads(cluster_res.insights_json) if cluster_res.insights_json else []
        subject_scores = json.loads(cluster_res.subject_scores_json) if cluster_res.subject_scores_json else {}
        last_updated = cluster_res.updated_at.strftime("%b %d, %Y, %I:%M %p") if cluster_res.updated_at else datetime.now().strftime("%b %d, %Y, %I:%M %p")
    else:
        mastery_score = 68.0
        quiz_accuracy = 74.0
        avg_time = 75.4
        prev_score = 49.8
        study_time = 12.4
        confidence = 87.0
        cluster_label = "Needs Support"
        cluster_id = 1
        learning_level = "Developing Learner"
        strengths = ["Good improvement in quiz accuracy", "Consistent study time", "Better performance in Python basics"]
        weak_areas = ["Data Structures (low accuracy)", "Algorithm problem solving (more attempts)", "Time management (higher solving time)", "Increase mastery score"]
        behaviour = {"consistency": 78.0, "concept_understanding": 62.0, "problem_solving": 56.0, "time_management": 59.0}
        insights = []
        subject_scores = {"Python": 72.0, "Data Structures": 61.0, "Algorithms": 54.0, "Database": 48.0, "Web Development": 66.0}
        last_updated = datetime.now().strftime("%b %d, %Y, %I:%M %p")

    # Format subject comparison for dual bar display
    subject_comparison = []
    for sub, score in subject_scores.items():
        class_avg = CLASS_BENCHMARKS.get(sub, 60.0)
        subject_comparison.append({
            "subject": sub,
            "user_score": round(score, 1),
            "class_avg": round(class_avg, 1)
        })
        
    ai_suggestion = (
        f"Focus on {weak_areas[0] if weak_areas else 'Data Structures and Algorithms'} with structured practice. "
        "Try answering 10 medium-level questions daily to optimize problem-solving speed."
    )

    return render_template(
        "ai_analysis.html",
        user=user,
        profile=profile,
        mastery_score=mastery_score,
        quiz_accuracy=quiz_accuracy,
        avg_time=avg_time,
        prev_score=prev_score,
        study_time=study_time,
        attempts_count=attempts_count,
        confidence=confidence,
        cluster_label=cluster_label,
        cluster_id=cluster_id,
        learning_level=learning_level,
        strengths=strengths,
        weak_areas=weak_areas,
        behaviour=behaviour,
        insights=insights,
        subject_comparison=subject_comparison,
        ai_suggestion=ai_suggestion,
        last_updated=last_updated,
        current_date=datetime.now().strftime("%B %d, %Y")
    )
