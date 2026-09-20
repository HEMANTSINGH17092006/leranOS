import sys
import json
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask
from config import Config
from database import db, init_db
from database.models import (
    User, StudentProfile, LearningRecord, QuizQuestion, 
    QuizAttempt, LearningGoal, LearningResource, LearnerClusterResult
)
from ml.preprocessing import aggregate_learner_profiles, extract_feature_matrix
from ml.clustering import train_and_save_pipeline, predict_single_learner
from ml.learner_analysis import analyze_learner
from ml.recommendation_engine import generate_recommendations

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_database():
    app = create_app()
    with app.app_context():
        # Ensure instance directory exists
        instance_dir = PROJECT_ROOT / "instance"
        instance_dir.mkdir(exist_ok=True)
        
        print("=" * 60)
        print("SEEDING AI-BASED PERSONALISED LEARNING DATABASE")
        print("=" * 60)
        
        print("\n[1/7] Dropping and re-creating database schema...")
        db.drop_all()
        db.create_all()
        print("      Database tables created successfully.")
        
        # 1. Create Demo User
        print("\n[2/7] Creating demo user account...")
        demo_user = User(
            name="Hemant Singh",
            email="demo@example.com",
            role="student",
            created_at=datetime(2025, 8, 15)
        )
        demo_user.set_password("Demo@123")
        db.session.add(demo_user)
        db.session.flush()
        
        demo_profile = StudentProfile(
            user_id=demo_user.id,
            student_id_code="STU00001",
            degree="B.Tech CSE",
            year="2nd Year",
            learning_streak=12,
            target_mastery_score=85.0,
            preferred_subjects="Python, Data Structures",
            created_at=datetime(2025, 8, 15)
        )
        db.session.add(demo_profile)
        
        # 2. Insert Learning Goals
        print("\n[3/7] Inserting demo learning goals...")
        now = datetime.now(timezone.utc)
        goals = [
            LearningGoal(
                user_id=demo_user.id,
                title="Improve mastery score to 80%",
                description="Consistently practice 10 questions daily",
                target_date="Target: Next 1 month",
                is_completed=False,
                created_at=now - timedelta(days=10)
            ),
            LearningGoal(
                user_id=demo_user.id,
                title="Complete Python Functions",
                description="Master decorators and generators",
                target_date="Target: This week",
                is_completed=True,
                created_at=now - timedelta(days=7)
            ),
            LearningGoal(
                user_id=demo_user.id,
                title="Increase quiz accuracy to 85%",
                description="Focus on reducing careless mistakes in Data Structures",
                target_date="Target: Next 1 month",
                is_completed=False,
                created_at=now - timedelta(days=5)
            ),
            LearningGoal(
                user_id=demo_user.id,
                title="Reduce average time to 60 sec",
                description="Practice timed mock tests",
                target_date="Target: Next 2 weeks",
                is_completed=False,
                created_at=now - timedelta(days=2)
            )
        ]
        db.session.add_all(goals)
        
        # 3. Load & Insert Learning Records from CSV
        print("\n[4/7] Loading and inserting 5,000+ learning records...")
        csv_path = Config.LEARNING_DATA_PATH
        if not csv_path.exists():
            print(f"      Generating dataset first at {csv_path}...")
            from data.generate_data import generate_dataset
            generate_dataset()
            
        record_count = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rec = LearningRecord(
                    student_id_code=row["student_id"],
                    subject=row["subject"],
                    quiz_score=float(row["quiz_score"]),
                    quiz_accuracy=float(row["quiz_accuracy"]),
                    total_attempts=int(row["total_attempts"]),
                    study_time_hours=float(row["study_time_hours"]),
                    average_time_per_question=float(row["average_time_per_question"]),
                    completion_rate=float(row["completion_rate"]),
                    previous_score=float(row["previous_score"]),
                    current_score=float(row["current_score"]),
                    practice_questions=int(row["practice_questions"]),
                    difficulty_level=row["difficulty_level"],
                    time_management_score=float(row["time_management_score"]),
                    consistency_score=float(row["consistency_score"]),
                    timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                )
                db.session.add(rec)
                record_count += 1
                if record_count % 1000 == 0:
                    db.session.flush()
        print(f"      Inserted {record_count} learning records.")
        
        # 4. Insert Quiz Questions
        print("\n[5/7] Inserting quiz questions bank...")
        q_path = Config.QUIZ_QUESTIONS_PATH
        with open(q_path, "r", encoding="utf-8") as f:
            q_data = json.load(f)
            
        for item in q_data:
            q = QuizQuestion(
                subject=item["subject"],
                topic=item["topic"],
                question_text=item["question_text"],
                option_a=item["option_a"],
                option_b=item["option_b"],
                option_c=item["option_c"],
                option_d=item["option_d"],
                correct_option=item["correct_option"],
                explanation=item.get("explanation", ""),
                difficulty=item.get("difficulty", "Medium")
            )
            db.session.add(q)
        print(f"      Inserted {len(q_data)} quiz questions.")
        
        # 5. Insert Quiz Attempts History for Demo User
        print("\n[6/7] Inserting historical quiz attempts for demo user...")
        demo_attempts = [
            {"subject": "Python", "difficulty": "Easy", "total": 5, "correct": 3, "score": 52.0, "acc": 52.0, "time": 420.0, "days_ago": 24},
            {"subject": "Data Structures", "difficulty": "Medium", "total": 5, "correct": 3, "score": 58.0, "acc": 58.0, "time": 410.0, "days_ago": 20},
            {"subject": "Algorithms", "difficulty": "Medium", "total": 5, "correct": 3, "score": 64.0, "acc": 64.0, "time": 390.0, "days_ago": 16},
            {"subject": "Database", "difficulty": "Easy", "total": 5, "correct": 4, "score": 71.0, "acc": 71.0, "time": 370.0, "days_ago": 12},
            {"subject": "Web Development", "difficulty": "Medium", "total": 5, "correct": 4, "score": 74.0, "acc": 74.0, "time": 360.0, "days_ago": 8},
            {"subject": "Python", "difficulty": "Medium", "total": 5, "correct": 4, "score": 68.0, "acc": 68.0, "time": 380.0, "days_ago": 5},
            {"subject": "Data Structures", "difficulty": "Hard", "total": 5, "correct": 4, "score": 76.0, "acc": 76.0, "time": 350.0, "days_ago": 3},
            {"subject": "Python", "difficulty": "Medium", "total": 5, "correct": 4, "score": 74.0, "acc": 74.0, "time": 377.0, "days_ago": 1}
        ]
        
        for att in demo_attempts:
            q_attempt = QuizAttempt(
                user_id=demo_user.id,
                student_id_code="STU00001",
                subject=att["subject"],
                difficulty=att["difficulty"],
                total_questions=att["total"],
                correct_answers=att["correct"],
                score=att["score"],
                accuracy=att["acc"],
                time_taken_seconds=att["time"],
                avg_time_per_question=round(att["time"] / att["total"], 1),
                answers_json=json.dumps({"1": "B", "2": "C", "3": "A", "4": "B", "5": "D"}),
                timestamp=now - timedelta(days=att["days_ago"])
            )
            db.session.add(q_attempt)
            
        # 6. Insert Learning Resources
        resources = [
            LearningResource(
                title="Python Functions - Concept Notes",
                description="Comprehensive reference on closures, lambda expressions, default arguments, and first-class functions.",
                subject="Python",
                resource_type="Notes",
                difficulty="Intermediate",
                estimated_time="15 mins",
                link="/static/resources/python_functions.pdf",
                icon="bi-file-earmark-pdf",
                content_summary="Covers pure functions, variable scopes (LEGB rule), closures, args/kwargs, and decorator architecture with code snippets."
            ),
            LearningResource(
                title="Python Decorators & Generators",
                description="Deep-dive into Python yield expressions, iterators protocol, and real-world decorator implementations.",
                subject="Python",
                resource_type="Video",
                difficulty="Intermediate",
                estimated_time="25 mins",
                link="https://www.youtube.com",
                icon="bi-play-circle",
                content_summary="Video tutorial explaining memory optimization through lazy evaluation and practical logging decorators."
            ),
            LearningResource(
                title="Data Structures - Array & Linked List Visualizer",
                description="Interactive breakdown of memory representation, pointer traversals, and amortized time complexities.",
                subject="Data Structures",
                resource_type="Notes",
                difficulty="Beginner",
                estimated_time="20 mins",
                link="/static/resources/dsa_arrays.pdf",
                icon="bi-journal-code",
                content_summary="Diagrams and C++/Python implementations of dynamic arrays, singly, doubly, and circular linked lists."
            ),
            LearningResource(
                title="Data Structures - Video Lecture",
                description="Master AVL tree balance factors, heapify algorithms, and hash collision resolution strategies.",
                subject="Data Structures",
                resource_type="Video",
                difficulty="Hard",
                estimated_time="35 mins",
                link="https://www.youtube.com",
                icon="bi-play-btn",
                content_summary="Visual lectures on self-balancing binary search trees, B-Trees, and Priority Queues."
            ),
            LearningResource(
                title="Algorithms - Dynamic Programming Guide",
                description="Step-by-step framework to identify optimal substructure, build recurrence relations, and memoize solutions.",
                subject="Algorithms",
                resource_type="Notes",
                difficulty="Hard",
                estimated_time="30 mins",
                link="/static/resources/dp_guide.pdf",
                icon="bi-cpu",
                content_summary="Detailed patterns covering 0/1 Knapsack, Longest Common Subsequence, and Matrix Chain Multiplication."
            ),
            LearningResource(
                title="Database - Normalization & ACID Masterclass",
                description="Clear explanation of 1NF, 2NF, 3NF, BCNF, and transactional isolation levels (Dirty Read, Non-repeatable Read).",
                subject="Database",
                resource_type="Notes",
                difficulty="Intermediate",
                estimated_time="20 mins",
                link="/static/resources/db_normalization.pdf",
                icon="bi-database-check",
                content_summary="Theoretical and practical SQL schemas illustrating normal forms and isolation anomaly mitigation."
            ),
            LearningResource(
                title="Web Development - REST API Design & Security",
                description="Best practices for RESTful endpoints, status codes, CORS configuration, JWT auth, and CSP protection.",
                subject="Web Development",
                resource_type="Notes",
                difficulty="Intermediate",
                estimated_time="18 mins",
                link="/static/resources/rest_api_security.pdf",
                icon="bi-globe",
                content_summary="Architectural guide for production web apps, HTTP headers, authentication pipelines, and rate limiting."
            ),
            LearningResource(
                title="Python Mini Project Ideas",
                description="5 hands-on portfolio projects: Custom CLI Tool, Personal Finance Tracker, URL Shortener, ML Predictor, Web Scraper.",
                subject="Python",
                resource_type="Project",
                difficulty="Intermediate",
                estimated_time="3 hrs",
                link="#",
                icon="bi-code-slash",
                content_summary="Project specifications with starter code and unit tests."
            ),
            LearningResource(
                title="Time Management for Competitive Coding",
                description="Proven techniques to read problems efficiently, identify time complexity bounds, and avoid over-engineering.",
                subject="Algorithms",
                resource_type="Article",
                difficulty="Beginner",
                estimated_time="8 mins",
                link="#",
                icon="bi-clock",
                content_summary="Mental models for pacing 45-minute coding assessments and debugging edge cases under pressure."
            )
        ]
        db.session.add_all(resources)
        db.session.commit()
        
        # 7. Train/Verify ML Pipeline & Generate Demo User Cluster
        print("\n[7/7] Executing ML clustering pipeline and generating initial AI analysis...")
        raw_df = aggregate_learner_profiles(
            import_learning_records_df()
        )
        
        # Train ML model and save
        train_result = train_and_save_pipeline(raw_df, Config.MODELS_DIR, k_range=[2, 3, 4, 5])
        
        # Predict for demo user
        demo_row = raw_df[raw_df["student_id"] == "STU00001"].iloc[0].to_dict()
        pred = predict_single_learner(demo_row, Config.MODELS_DIR)
        
        # Generate dynamic AI analysis & recommendations
        analysis = analyze_learner(demo_row, pred)
        recs = generate_recommendations(analysis)
        
        # Save initial cluster result
        cluster_entry = LearnerClusterResult(
            user_id=demo_user.id,
            student_id_code="STU00001",
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
        
        print(f"      Initial Learner Cluster: {pred['cluster_label']} (Cluster {pred['cluster_id']})")
        print(f"      AI Confidence Score:     {pred['confidence_score']}%")
        print(f"      Overall Learning Level:  {analysis['overall_learning_level']}")
        print(f"      Mastery Score:           {analysis['mastery_score']}%")
        print(f"      Quiz Accuracy:           {analysis['quiz_accuracy']}%")
        print("=" * 60)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("Demo Account:")
        print("  Email:    demo@example.com")
        print("  Password: Demo@123")
        print("=" * 60)

def import_learning_records_df():
    import pandas as pd
    records = LearningRecord.query.all()
    data = []
    for r in records:
        data.append({
            "student_id": r.student_id_code,
            "subject": r.subject,
            "quiz_score": r.quiz_score,
            "quiz_accuracy": r.quiz_accuracy,
            "total_attempts": r.total_attempts,
            "study_time_hours": r.study_time_hours,
            "average_time_per_question": r.average_time_per_question,
            "completion_rate": r.completion_rate,
            "previous_score": r.previous_score,
            "current_score": r.current_score,
            "practice_questions": r.practice_questions,
            "difficulty_level": r.difficulty_level,
            "time_management_score": r.time_management_score,
            "consistency_score": r.consistency_score,
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else ""
        })
    return pd.DataFrame(data)

if __name__ == "__main__":
    seed_database()
