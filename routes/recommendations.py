import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from database.models import User, StudentProfile, LearnerClusterResult
from routes.auth import login_required, get_current_user

recommendations_bp = Blueprint("recommendations", __name__)

@recommendations_bp.route("/recommendations")
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    profile = user.profile
    cluster_res = user.cluster_result
    
    if cluster_res:
        learning_level = cluster_res.overall_learning_level
        cluster_label = cluster_res.cluster_label
        cluster_id = cluster_res.cluster_id
        mastery_score = round(cluster_res.mastery_score, 1)
        target_score = round(profile.target_mastery_score if profile else 80.0, 1)
        recommendations = json.loads(cluster_res.recommendations_json) if cluster_res.recommendations_json else []
        learning_path = json.loads(cluster_res.learning_path_json) if cluster_res.learning_path_json else []
    else:
        learning_level = "Developing Learner"
        cluster_label = "Needs Support"
        cluster_id = 1
        mastery_score = 68.0
        target_score = 80.0
        recommendations = []
        learning_path = []
        
    gap_to_target = max(0, round(target_score - mastery_score, 1))

    # Recommended Resources list
    recommended_resources = [
        {
            "title": "Python Functions - Concept Notes",
            "type_label": "PDF • 12 pages",
            "type": "Notes",
            "icon": "bi-file-earmark-pdf text-danger",
            "action_url": "/resources?subject=Python"
        },
        {
            "title": "Data Structures - Video Lecture",
            "type_label": "Video • 25 mins",
            "type": "Video",
            "icon": "bi-play-circle text-primary",
            "action_url": "/resources?subject=Data Structures"
        },
        {
            "title": "Practice Questions - Set 1",
            "type_label": "Quiz • 10 questions",
            "type": "Quiz",
            "icon": "bi-question-square text-success",
            "action_url": "/practice-quiz?subject=Data Structures"
        },
        {
            "title": "Time Management Tips",
            "type_label": "Article • 8 mins",
            "type": "Article",
            "icon": "bi-clock text-warning",
            "action_url": "/resources"
        },
        {
            "title": "Python Mini Project Ideas",
            "type_label": "Guide • 5 projects",
            "type": "Project",
            "icon": "bi-code-slash text-info",
            "action_url": "/resources?subject=Python"
        }
    ]

    expected_outcomes = [
        "Improve quiz accuracy to 85%",
        "Reduce average time to 60 sec",
        "Strengthen Python and Data Structures",
        "Increase overall mastery score to 80%",
        "Build confidence for advanced topics"
    ]

    return render_template(
        "recommendations.html",
        user=user,
        profile=profile,
        learning_level=learning_level,
        cluster_label=cluster_label,
        cluster_id=cluster_id,
        mastery_score=mastery_score,
        target_score=target_score,
        gap_to_target=gap_to_target,
        recommendations=recommendations,
        learning_path=learning_path,
        recommended_resources=recommended_resources,
        expected_outcomes=expected_outcomes,
        current_date=datetime.now().strftime("%B %d, %Y")
    )
