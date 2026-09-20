from functools import wraps
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import db
from database.models import User, StudentProfile, LearningRecord, LearnerClusterResult
from config import Config
from ml.clustering import predict_single_learner
from ml.learner_analysis import analyze_learner
from ml.recommendation_engine import generate_recommendations

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if "user_id" in session:
        return db.session.get(User, session["user_id"])
    return None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html")
            
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            session.permanent = True
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
        
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        degree = request.form.get("degree", "B.Tech CSE").strip()
        year = request.form.get("year", "1st Year").strip()
        
        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template("register.html")
            
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for("auth.login"))
            
        # Create new user
        user = User(name=name, email=email, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Generate new student_id
        count_students = StudentProfile.query.count() + 1
        stu_code = f"STU{count_students:05d}"
        
        profile = StudentProfile(
            user_id=user.id,
            student_id_code=stu_code,
            degree=degree,
            year=year,
            learning_streak=1,
            target_mastery_score=80.0,
            preferred_subjects="Python, Data Structures"
        )
        db.session.add(profile)
        db.session.flush()
        
        # Create baseline initial learning records
        initial_subjects = ["Python", "Data Structures", "Algorithms", "Database", "Web Development"]
        for sub in initial_subjects:
            rec = LearningRecord(
                student_id_code=stu_code,
                subject=sub,
                quiz_score=50.0,
                quiz_accuracy=50.0,
                total_attempts=1,
                study_time_hours=1.0,
                average_time_per_question=75.0,
                completion_rate=100.0,
                previous_score=40.0,
                current_score=50.0,
                practice_questions=10,
                difficulty_level="Medium",
                time_management_score=60.0,
                consistency_score=65.0,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(rec)
        db.session.flush()
        
        # Run ML cluster prediction
        learner_features = {
            "avg_quiz_score": 50.0,
            "quiz_accuracy": 50.0,
            "total_attempts": 5,
            "total_study_time": 5.0,
            "avg_time_per_question": 75.0,
            "completion_rate": 100.0,
            "practice_questions": 50,
            "consistency_score": 65.0,
            "time_management_score": 60.0,
            "score_python": 50.0,
            "score_data_structures": 50.0,
            "score_algorithms": 50.0,
            "score_database": 50.0,
            "score_web_development": 50.0
        }
        pred = predict_single_learner(learner_features, Config.MODELS_DIR)
        analysis = analyze_learner(learner_features, pred)
        recs = generate_recommendations(analysis)
        
        cluster_entry = LearnerClusterResult(
            user_id=user.id,
            student_id_code=stu_code,
            cluster_id=pred["cluster_id"],
            cluster_label=pred["cluster_label"],
            confidence_score=pred["confidence_score"],
            overall_learning_level=analysis["overall_learning_level"],
            mastery_score=analysis["mastery_score"],
            quiz_accuracy=analysis["quiz_accuracy"],
            avg_time_per_question=analysis["avg_time_per_question"],
            total_study_time=analysis["total_study_time"],
            total_attempts=analysis["total_attempts"],
            previous_score=analysis["previous_score"],
            strengths_json=json.dumps(analysis["strengths"]),
            weak_areas_json=json.dumps(analysis["weak_areas"]),
            behaviour_json=json.dumps(analysis["behaviour"]),
            insights_json=json.dumps(analysis["insights"]),
            recommendations_json=json.dumps(recs["recommendations"]),
            learning_path_json=json.dumps(recs["learning_path"]),
            subject_scores_json=json.dumps(analysis["subject_scores"])
        )
        db.session.add(cluster_entry)
        db.session.commit()
        
        # Auto login
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_email"] = user.email
        session.permanent = True
        
        flash(f"Account created successfully! Welcome to LearnOS, {user.name}.", "success")
        return redirect(url_for("dashboard.index"))
        
    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))
