import pandas as pd
import numpy as np

CORE_SUBJECTS = [
    "Python",
    "Data Structures",
    "Algorithms",
    "Database",
    "Web Development"
]

FEATURE_COLUMNS = [
    "avg_quiz_score",
    "quiz_accuracy",
    "total_attempts",
    "total_study_time",
    "avg_time_per_question",
    "completion_rate",
    "practice_questions",
    "consistency_score",
    "time_management_score",
    "score_python",
    "score_data_structures",
    "score_algorithms",
    "score_database",
    "score_web_development"
]

def load_raw_data(filepath):
    """Loads and validates CSV learning data."""
    df = pd.read_csv(filepath)
    # Clean any nulls or infs
    df = df.dropna()
    return df

def aggregate_learner_profiles(df):
    """
    Aggregates record-level data by student_id to construct unified learner-level feature profiles.
    """
    grouped = df.groupby("student_id")
    
    records = []
    for student_id, group in grouped:
        # Base aggregation
        avg_quiz_score = group["quiz_score"].mean()
        quiz_accuracy = group["quiz_accuracy"].mean()
        total_attempts = len(group)
        total_study_time = group["study_time_hours"].sum()
        avg_time_per_question = group["average_time_per_question"].mean()
        completion_rate = group["completion_rate"].mean()
        practice_questions = group["practice_questions"].sum()
        consistency_score = group["consistency_score"].mean()
        time_management_score = group["time_management_score"].mean()
        
        # Subject-wise breakdown
        subj_means = group.groupby("subject")["quiz_score"].mean().to_dict()
        score_python = subj_means.get("Python", avg_quiz_score)
        score_dsa = subj_means.get("Data Structures", avg_quiz_score)
        score_algo = subj_means.get("Algorithms", avg_quiz_score)
        score_db = subj_means.get("Database", avg_quiz_score)
        score_web = subj_means.get("Web Development", avg_quiz_score)
        
        records.append({
            "student_id": student_id,
            "avg_quiz_score": round(avg_quiz_score, 2),
            "quiz_accuracy": round(quiz_accuracy, 2),
            "total_attempts": int(total_attempts),
            "total_study_time": round(total_study_time, 2),
            "avg_time_per_question": round(avg_time_per_question, 2),
            "completion_rate": round(completion_rate, 2),
            "practice_questions": int(practice_questions),
            "consistency_score": round(consistency_score, 2),
            "time_management_score": round(time_management_score, 2),
            "score_python": round(score_python, 2),
            "score_data_structures": round(score_dsa, 2),
            "score_algorithms": round(score_algo, 2),
            "score_database": round(score_db, 2),
            "score_web_development": round(score_web, 2)
        })
        
    profile_df = pd.DataFrame(records)
    return profile_df

def extract_feature_matrix(profile_df):
    """Extracts numerical features array for ML scaling and clustering."""
    X = profile_df[FEATURE_COLUMNS].copy()
    return X
