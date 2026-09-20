import json
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Relationships
    profile = db.relationship("StudentProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    quiz_attempts = db.relationship("QuizAttempt", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    goals = db.relationship("LearningGoal", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    cluster_result = db.relationship("LearnerClusterResult", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    student_id_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    degree = db.Column(db.String(100), default="B.Tech CSE")
    year = db.Column(db.String(50), default="2nd Year")
    learning_streak = db.Column(db.Integer, default=12)
    target_mastery_score = db.Column(db.Float, default=85.0)
    preferred_subjects = db.Column(db.String(255), default="Python, Data Structures")
    avatar_url = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "student_id_code": self.student_id_code,
            "degree": self.degree,
            "year": self.year,
            "learning_streak": self.learning_streak,
            "target_mastery_score": self.target_mastery_score,
            "preferred_subjects": self.preferred_subjects.split(", ") if self.preferred_subjects else [],
            "created_at": self.created_at.strftime("%d %b %Y") if self.created_at else ""
        }


class LearningRecord(db.Model):
    __tablename__ = "learning_records"

    id = db.Column(db.Integer, primary_key=True)
    student_id_code = db.Column(db.String(20), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False, index=True)
    quiz_score = db.Column(db.Float, nullable=False)
    quiz_accuracy = db.Column(db.Float, nullable=False)
    total_attempts = db.Column(db.Integer, default=1)
    study_time_hours = db.Column(db.Float, default=1.0)
    average_time_per_question = db.Column(db.Float, default=60.0)  # seconds
    completion_rate = db.Column(db.Float, default=100.0)  # percentage
    previous_score = db.Column(db.Float, default=0.0)
    current_score = db.Column(db.Float, default=0.0)
    practice_questions = db.Column(db.Integer, default=10)
    difficulty_level = db.Column(db.String(20), default="Medium")
    time_management_score = db.Column(db.Float, default=70.0)
    consistency_score = db.Column(db.Float, default=75.0)
    timestamp = db.Column(db.DateTime, default=utc_now, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id_code": self.student_id_code,
            "subject": self.subject,
            "quiz_score": self.quiz_score,
            "quiz_accuracy": self.quiz_accuracy,
            "total_attempts": self.total_attempts,
            "study_time_hours": self.study_time_hours,
            "average_time_per_question": self.average_time_per_question,
            "completion_rate": self.completion_rate,
            "previous_score": self.previous_score,
            "current_score": self.current_score,
            "practice_questions": self.practice_questions,
            "difficulty_level": self.difficulty_level,
            "time_management_score": self.time_management_score,
            "consistency_score": self.consistency_score,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False, index=True)
    topic = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    explanation = db.Column(db.Text, default="")
    difficulty = db.Column(db.String(20), default="Medium")

    def to_dict(self, include_answer=False):
        data = {
            "id": self.id,
            "subject": self.subject,
            "topic": self.topic,
            "question_text": self.question_text,
            "options": {
                "A": self.option_a,
                "B": self.option_b,
                "C": self.option_c,
                "D": self.option_d
            },
            "difficulty": self.difficulty
        }
        if include_answer:
            data["correct_option"] = self.correct_option
            data["explanation"] = self.explanation
        return data


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student_id_code = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default="Medium")
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)  # percentage 0-100
    accuracy = db.Column(db.Float, nullable=False)  # percentage 0-100
    time_taken_seconds = db.Column(db.Float, nullable=False)
    avg_time_per_question = db.Column(db.Float, nullable=False)
    answers_json = db.Column(db.Text, default="{}")
    timestamp = db.Column(db.DateTime, default=utc_now, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "student_id_code": self.student_id_code,
            "subject": self.subject,
            "difficulty": self.difficulty,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "score": round(self.score, 1),
            "accuracy": round(self.accuracy, 1),
            "time_taken_seconds": round(self.time_taken_seconds, 1),
            "avg_time_per_question": round(self.avg_time_per_question, 1),
            "answers": json.loads(self.answers_json) if self.answers_json else {},
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "date_display": self.timestamp.strftime("%d %b %Y, %I:%M %p") if self.timestamp else None
        }


class LearningGoal(db.Model):
    __tablename__ = "learning_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255), default="")
    target_date = db.Column(db.String(100), default="Target: Next 1 month")
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "target_date": self.target_date,
            "is_completed": self.is_completed,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else None
        }


class LearningResource(db.Model):
    __tablename__ = "learning_resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(50), nullable=False, index=True)
    resource_type = db.Column(db.String(50), default="Notes")  # Notes, Video, Quiz, Article, Project
    difficulty = db.Column(db.String(20), default="Beginner")
    estimated_time = db.Column(db.String(50), default="15 mins")
    link = db.Column(db.String(255), default="#")
    icon = db.Column(db.String(50), default="bi-book")
    content_summary = db.Column(db.Text, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "subject": self.subject,
            "resource_type": self.resource_type,
            "difficulty": self.difficulty,
            "estimated_time": self.estimated_time,
            "link": self.link,
            "icon": self.icon,
            "content_summary": self.content_summary
        }


class LearnerClusterResult(db.Model):
    __tablename__ = "learner_cluster_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    student_id_code = db.Column(db.String(20), nullable=False, index=True)
    cluster_id = db.Column(db.Integer, nullable=False)
    cluster_label = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, default=85.0)  # percentage
    overall_learning_level = db.Column(db.String(100), default="Developing Learner")
    mastery_score = db.Column(db.Float, default=68.0)
    quiz_accuracy = db.Column(db.Float, default=74.0)
    avg_time_per_question = db.Column(db.Float, default=75.4)
    total_study_time = db.Column(db.Float, default=12.4)
    total_attempts = db.Column(db.Integer, default=8)
    previous_score = db.Column(db.Float, default=49.8)
    strengths_json = db.Column(db.Text, default="[]")
    weak_areas_json = db.Column(db.Text, default="[]")
    behaviour_json = db.Column(db.Text, default="{}")
    insights_json = db.Column(db.Text, default="[]")
    recommendations_json = db.Column(db.Text, default="[]")
    learning_path_json = db.Column(db.Text, default="[]")
    subject_scores_json = db.Column(db.Text, default="{}")
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "student_id_code": self.student_id_code,
            "cluster_id": self.cluster_id,
            "cluster_label": self.cluster_label,
            "confidence_score": round(self.confidence_score, 1),
            "overall_learning_level": self.overall_learning_level,
            "mastery_score": round(self.mastery_score, 1),
            "quiz_accuracy": round(self.quiz_accuracy, 1),
            "avg_time_per_question": round(self.avg_time_per_question, 1),
            "total_study_time": round(self.total_study_time, 1),
            "total_attempts": self.total_attempts,
            "previous_score": round(self.previous_score, 1),
            "strengths": json.loads(self.strengths_json) if self.strengths_json else [],
            "weak_areas": json.loads(self.weak_areas_json) if self.weak_areas_json else [],
            "behaviour": json.loads(self.behaviour_json) if self.behaviour_json else {},
            "insights": json.loads(self.insights_json) if self.insights_json else [],
            "recommendations": json.loads(self.recommendations_json) if self.recommendations_json else [],
            "learning_path": json.loads(self.learning_path_json) if self.learning_path_json else [],
            "subject_scores": json.loads(self.subject_scores_json) if self.subject_scores_json else {},
            "updated_at": self.updated_at.strftime("%b %d, %Y, %I:%M %p") if self.updated_at else ""
        }
