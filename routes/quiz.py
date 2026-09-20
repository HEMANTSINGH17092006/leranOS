import json
import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db
from database.models import User, StudentProfile, QuizQuestion, QuizAttempt, LearningRecord, LearnerClusterResult
from routes.auth import login_required, get_current_user
from config import Config
from ml.clustering import predict_single_learner
from ml.learner_analysis import analyze_learner
from ml.recommendation_engine import generate_recommendations

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/practice-quiz")
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    subject_filter = request.args.get("subject", "")
    difficulty_filter = request.args.get("difficulty", "")
    
    # Available subjects and question counts
    subjects = [
        {"name": "Python", "icon": "bi-code-slash", "color": "text-primary", "bg": "bg-primary-subtle", "desc": "Functions, OOP, Scopes, Decorators"},
        {"name": "Data Structures", "icon": "bi-diagram-3", "color": "text-info", "bg": "bg-info-subtle", "desc": "Arrays, Linked Lists, Trees, Heaps"},
        {"name": "Algorithms", "icon": "bi-cpu", "color": "text-warning", "bg": "bg-warning-subtle", "desc": "Sorting, Searching, Dynamic Programming, Graphs"},
        {"name": "Database", "icon": "bi-database", "color": "text-danger", "bg": "bg-danger-subtle", "desc": "SQL, Normalization, ACID, Indexing"},
        {"name": "Web Development", "icon": "bi-globe", "color": "text-success", "bg": "bg-success-subtle", "desc": "HTTP, DOM, Security, REST APIs"}
    ]
    
    for s in subjects:
        s["question_count"] = QuizQuestion.query.filter_by(subject=s["name"]).count()
        
    # User's recent attempts
    recent_attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.desc()).limit(5).all()
    
    return render_template(
        "practice_quiz.html",
        user=user,
        profile=user.profile,
        subjects=subjects,
        selected_subject=subject_filter,
        selected_difficulty=difficulty_filter,
        recent_attempts=recent_attempts,
        current_date=datetime.now().strftime("%B %d, %Y")
    )

@quiz_bp.route("/practice-quiz/start", methods=["GET", "POST"])
@login_required
def start():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
        
    subject = request.args.get("subject") or request.form.get("subject", "All")
    difficulty = request.args.get("difficulty") or request.form.get("difficulty", "All")
    
    query = QuizQuestion.query
    if subject and subject != "All":
        query = query.filter_by(subject=subject)
    if difficulty and difficulty != "All":
        query = query.filter_by(difficulty=difficulty)
        
    all_questions = query.all()
    
    if not all_questions:
        flash(f"No questions found for {subject} ({difficulty}). Showing available questions.", "info")
        all_questions = QuizQuestion.query.all()
        
    # Sample up to 5 questions
    sample_size = min(5, len(all_questions))
    selected_questions = random.sample(all_questions, sample_size) if len(all_questions) >= sample_size else all_questions
    
    questions_json = [q.to_dict(include_answer=True) for q in selected_questions]
    
    return render_template(
        "quiz_active.html",
        user=user,
        profile=user.profile,
        subject=subject,
        difficulty=difficulty,
        questions=selected_questions,
        questions_json=json.dumps(questions_json),
        total_questions=len(selected_questions),
        duration_minutes=len(selected_questions) * 1.5,
        current_date=datetime.now().strftime("%B %d, %Y")
    )
