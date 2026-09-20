import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session
from database import db
from database.models import (
    User, StudentProfile, LearningRecord, QuizQuestion, 
    QuizAttempt, LearningGoal, LearningResource, LearnerClusterResult
)
from config import Config
from routes.auth import get_current_user
from ml.clustering import predict_single_learner
from ml.learner_analysis import analyze_learner
from ml.recommendation_engine import generate_recommendations

api_bp = Blueprint("api", __name__, url_prefix="/api")

def recalculate_user_ml_profile(user):
    """
    Core ML Feedback Pipeline:
    Aggregates all learner records & quiz attempts for the user,
    runs the ML model, updates the AI analysis, and saves the new cluster result.
    """
    profile = user.profile
    stu_code = profile.student_id_code if profile else f"STU{user.id:05d}"
    
    # Fetch all learning records for this student
    records = LearningRecord.query.filter_by(student_id_code=stu_code).all()
    attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
    
    if not records and not attempts:
        # Fallback baseline
        avg_score = 65.0
        quiz_acc = 70.0
        total_attempts = 1
        total_study_time = 5.0
        avg_time = 75.0
        completion = 100.0
        practice_qs = 10
        consistency = 70.0
        time_mgmt = 65.0
        subj_scores = {"Python": 65.0, "Data Structures": 60.0, "Algorithms": 55.0, "Database": 60.0, "Web Development": 60.0}
        prev_score = 50.0
    else:
        # Aggregate real records
        all_scores = [r.quiz_score for r in records] + [a.score for a in attempts]
        all_accuracies = [r.quiz_accuracy for r in records] + [a.accuracy for a in attempts]
        all_times = [r.average_time_per_question for r in records] + [a.avg_time_per_question for a in attempts]
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 65.0
        quiz_acc = sum(all_accuracies) / len(all_accuracies) if all_accuracies else 70.0
        total_attempts = len(records) + len(attempts)
        total_study_time = sum([r.study_time_hours for r in records]) + sum([a.time_taken_seconds / 3600 for a in attempts])
        avg_time = sum(all_times) / len(all_times) if all_times else 75.0
        completion = 100.0
        practice_qs = sum([r.practice_questions for r in records]) + sum([a.total_questions for a in attempts])
        
        consistency_scores = [r.consistency_score for r in records if r.consistency_score]
        consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else min(95.0, 60.0 + len(attempts) * 2.5)
        
        time_mgmt_scores = [r.time_management_score for r in records if r.time_management_score]
        time_mgmt = sum(time_mgmt_scores) / len(time_mgmt_scores) if time_mgmt_scores else max(40.0, 100.0 - (avg_time * 0.5))
        
        # Subject-wise scores calculation
        subj_scores = {}
        for sub in ["Python", "Data Structures", "Algorithms", "Database", "Web Development"]:
            sub_rec_scores = [r.quiz_score for r in records if r.subject == sub]
            sub_att_scores = [a.score for a in attempts if a.subject == sub]
            combined = sub_rec_scores + sub_att_scores
            subj_scores[sub] = round(sum(combined) / len(combined), 1) if combined else round(avg_score, 1)
            
        prev_scores = [r.previous_score for r in records if r.previous_score > 0]
        prev_score = prev_scores[0] if prev_scores else round(max(30.0, avg_score - 15.0), 1)
        
    learner_features = {
        "avg_quiz_score": round(avg_score, 2),
        "quiz_accuracy": round(quiz_acc, 2),
        "total_attempts": int(total_attempts),
        "total_study_time": round(total_study_time, 2),
        "avg_time_per_question": round(avg_time, 2),
        "completion_rate": round(completion, 2),
        "practice_questions": int(practice_qs),
        "consistency_score": round(consistency, 2),
        "time_management_score": round(time_mgmt, 2),
        "score_python": subj_scores.get("Python", avg_score),
        "score_data_structures": subj_scores.get("Data Structures", avg_score),
        "score_algorithms": subj_scores.get("Algorithms", avg_score),
        "score_database": subj_scores.get("Database", avg_score),
        "score_web_development": subj_scores.get("Web Development", avg_score),
        "previous_score": prev_score
    }
    
    # Run ML cluster prediction
    pred = predict_single_learner(learner_features, Config.MODELS_DIR)
    
    # Run AI Analysis & Recommendations
    analysis = analyze_learner(learner_features, pred)
    recs = generate_recommendations(analysis)
    
    # Persist or update cluster result in DB
    cluster_res = LearnerClusterResult.query.filter_by(user_id=user.id).first()
    if not cluster_res:
        cluster_res = LearnerClusterResult(user_id=user.id, student_id_code=stu_code)
        db.session.add(cluster_res)
        
    cluster_res.cluster_id = pred["cluster_id"]
    cluster_res.cluster_label = pred["cluster_label"]
    cluster_res.confidence_score = pred["confidence_score"]
    cluster_res.overall_learning_level = analysis["overall_learning_level"]
    cluster_res.mastery_score = analysis["mastery_score"]
    cluster_res.quiz_accuracy = analysis["quiz_accuracy"]
    cluster_res.avg_time_per_question = analysis["avg_time_per_question"]
    cluster_res.total_study_time = analysis["total_study_time"]
    cluster_res.total_attempts = analysis["total_attempts"]
    cluster_res.previous_score = analysis["previous_score"]
    cluster_res.strengths_json = json.dumps(analysis["strengths"])
    cluster_res.weak_areas_json = json.dumps(analysis["weak_areas"])
    cluster_res.behaviour_json = json.dumps(analysis["behaviour"])
    cluster_res.insights_json = json.dumps(analysis["insights"])
    cluster_res.recommendations_json = json.dumps(recs["recommendations"])
    cluster_res.learning_path_json = json.dumps(recs["learning_path"])
    cluster_res.subject_scores_json = json.dumps(analysis["subject_scores"])
    cluster_res.updated_at = datetime.now(timezone.utc)
    
    db.session.commit()
    return cluster_res, analysis, recs

@api_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    cluster_res = user.cluster_result
    return jsonify({
        "status": "success",
        "user": user.to_dict(),
        "profile": user.profile.to_dict() if user.profile else {},
        "cluster_result": cluster_res.to_dict() if cluster_res else {}
    })

@api_bp.route("/profile", methods=["GET"])
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    goals = [g.to_dict() for g in user.goals.all()]
    return jsonify({
        "status": "success",
        "user": user.to_dict(),
        "profile": user.profile.to_dict() if user.profile else {},
        "goals": goals,
        "cluster_result": user.cluster_result.to_dict() if user.cluster_result else {}
    })

@api_bp.route("/analysis", methods=["GET"])
def get_analysis():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    return jsonify({
        "status": "success",
        "analysis": user.cluster_result.to_dict() if user.cluster_result else {}
    })

@api_bp.route("/analysis/refresh", methods=["POST"])
def refresh_analysis():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    cluster_res, analysis, recs = recalculate_user_ml_profile(user)
    
    return jsonify({
        "status": "success",
        "message": "AI Analysis refreshed successfully using latest learner performance data.",
        "cluster_result": cluster_res.to_dict(),
        "analysis": analysis,
        "recommendations": recs
    })

@api_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if not user.cluster_result:
        return jsonify({"status": "success", "recommendations": [], "learning_path": []})
        
    return jsonify({
        "status": "success",
        "recommendations": json.loads(user.cluster_result.recommendations_json) if user.cluster_result.recommendations_json else [],
        "learning_path": json.loads(user.cluster_result.learning_path_json) if user.cluster_result.learning_path_json else []
    })

@api_bp.route("/progress", methods=["GET"])
def get_progress():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.asc()).all()
    return jsonify({
        "status": "success",
        "attempts": [a.to_dict() for a in attempts]
    })

@api_bp.route("/quiz/submit", methods=["POST"])
def submit_quiz():
    """
    Processes quiz submission, grades questions, commits attempt & record,
    triggers ML cluster re-calculation, and returns review.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    subject = data.get("subject", "General")
    difficulty = data.get("difficulty", "Medium")
    user_answers = data.get("answers", {})  # e.g. { "question_id": "A" }
    time_taken = float(data.get("time_taken_seconds", 120.0))
    
    if not user_answers:
        return jsonify({"error": "No answers provided in quiz submission"}), 400
        
    question_ids = list(user_answers.keys())
    questions = QuizQuestion.query.filter(QuizQuestion.id.in_(question_ids)).all()
    
    if not questions:
        return jsonify({"error": "Questions not found in database"}), 404
        
    total_questions = len(questions)
    correct_count = 0
    review_list = []
    
    for q in questions:
        selected_opt = str(user_answers.get(str(q.id), "")).strip().upper()
        is_correct = (selected_opt == q.correct_option.strip().upper())
        if is_correct:
            correct_count += 1
            
        review_list.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "selected_option": selected_opt,
            "correct_option": q.correct_option,
            "is_correct": is_correct,
            "explanation": q.explanation,
            "options": {
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d
            }
        })
        
    score_pct = round((correct_count / total_questions) * 100.0, 1)
    accuracy_pct = score_pct
    avg_time_per_q = round(time_taken / total_questions, 1)
    
    profile = user.profile
    stu_code = profile.student_id_code if profile else f"STU{user.id:05d}"
    
    # 1. Save QuizAttempt
    attempt = QuizAttempt(
        user_id=user.id,
        student_id_code=stu_code,
        subject=subject if subject != "All" else "General",
        difficulty=difficulty,
        total_questions=total_questions,
        correct_answers=correct_count,
        score=score_pct,
        accuracy=accuracy_pct,
        time_taken_seconds=time_taken,
        avg_time_per_question=avg_time_per_q,
        answers_json=json.dumps(user_answers),
        timestamp=datetime.utcnow()
    )
    db.session.add(attempt)
    
    # 2. Save LearningRecord to feed ongoing ML dataset
    rec = LearningRecord(
        student_id_code=stu_code,
        subject=subject if subject != "All" else "General",
        quiz_score=score_pct,
        quiz_accuracy=accuracy_pct,
        total_attempts=1,
        study_time_hours=round(time_taken / 3600.0, 2),
        average_time_per_question=avg_time_per_q,
        completion_rate=100.0,
        previous_score=user.cluster_result.mastery_score if user.cluster_result else 50.0,
        current_score=score_pct,
        practice_questions=total_questions,
        difficulty_level=difficulty,
        time_management_score=min(100.0, max(30.0, 100.0 - (avg_time_per_q * 0.5))),
        consistency_score=75.0,
        timestamp=datetime.utcnow()
    )
    db.session.add(rec)
    db.session.commit()
    
    # 3. Trigger Core ML Re-calculation Feedback Loop
    cluster_res, analysis, recs = recalculate_user_ml_profile(user)
    
    return jsonify({
        "status": "success",
        "message": "Quiz submitted successfully! Learner profile and AI analysis updated.",
        "attempt_id": attempt.id,
        "score": score_pct,
        "accuracy": accuracy_pct,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "time_taken_seconds": time_taken,
        "avg_time_per_question": avg_time_per_q,
        "updated_mastery_score": cluster_res.mastery_score,
        "updated_cluster": cluster_res.cluster_label,
        "learning_level": cluster_res.overall_learning_level,
        "review": review_list
    })

@api_bp.route("/goals", methods=["POST"])
def add_goal():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    target_date = data.get("target_date", "Target: Next 1 month").strip()
    
    if not title:
        return jsonify({"error": "Goal title is required"}), 400
        
    goal = LearningGoal(
        user_id=user.id,
        title=title,
        description=description,
        target_date=target_date,
        is_completed=False
    )
    db.session.add(goal)
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "message": "Goal added successfully",
        "goal": goal.to_dict()
    }), 201

@api_bp.route("/goals/<int:goal_id>", methods=["PUT"])
def update_goal(goal_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    goal = LearningGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404
        
    data = request.get_json() or {}
    if "is_completed" in data:
        goal.is_completed = bool(data["is_completed"])
    if "title" in data and data["title"].strip():
        goal.title = data["title"].strip()
    if "target_date" in data and data["target_date"].strip():
        goal.target_date = data["target_date"].strip()
        
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Goal updated successfully",
        "goal": goal.to_dict()
    })

@api_bp.route("/goals/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    goal = LearningGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404
        
    db.session.delete(goal)
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Goal deleted successfully"
    })

@api_bp.route("/resources", methods=["GET"])
def get_resources():
    subject = request.args.get("subject")
    res_type = request.args.get("type")
    
    query = LearningResource.query
    if subject and subject != "All":
        query = query.filter_by(subject=subject)
    if res_type and res_type != "All":
        query = query.filter_by(resource_type=res_type)
        
    resources = query.all()
    return jsonify({
        "status": "success",
        "resources": [r.to_dict() for r in resources]
    })
