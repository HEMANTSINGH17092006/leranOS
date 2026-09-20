import numpy as np

CLASS_BENCHMARKS = {
    "Python": 65.0,
    "Data Structures": 60.0,
    "Algorithms": 58.0,
    "Database": 62.0,
    "Web Development": 58.0
}

def analyze_learner(profile_dict, cluster_info):
    """
    Synthesizes comprehensive AI analysis from learner performance profile and ML cluster data.
    """
    quiz_acc = profile_dict.get("quiz_accuracy", 70.0)
    mastery_score = profile_dict.get("avg_quiz_score", 65.0)
    prev_score = profile_dict.get("previous_score", 50.0)
    avg_time = profile_dict.get("avg_time_per_question", 70.0)
    study_time = profile_dict.get("total_study_time", 10.0)
    attempts = profile_dict.get("total_attempts", 5)
    consistency = profile_dict.get("consistency_score", 70.0)
    time_mgmt = profile_dict.get("time_management_score", 60.0)
    
    subject_scores = {
        "Python": profile_dict.get("score_python", 70.0),
        "Data Structures": profile_dict.get("score_data_structures", 60.0),
        "Algorithms": profile_dict.get("score_algorithms", 55.0),
        "Database": profile_dict.get("score_database", 50.0),
        "Web Development": profile_dict.get("score_web_development", 65.0)
    }
    
    # Sort subjects by score
    sorted_subjects = sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
    best_subject, best_sub_score = sorted_subjects[0]
    weakest_subject, weakest_sub_score = sorted_subjects[-1]
    
    # Overall Learning Level & Description
    cluster_label = cluster_info.get("cluster_label", "Developing Learner")
    cluster_id = cluster_info.get("cluster_id", 0)
    confidence = cluster_info.get("confidence_score", 87.0)
    
    if mastery_score >= 80.0:
        overall_level = "Strong Performer"
        level_summary = "You are excelling across core subjects! Maintain momentum with advanced challenges."
    elif mastery_score >= 60.0:
        overall_level = "Developing Learner"
        level_summary = "You are on a good path! With consistent practice, you can reach the next level."
    else:
        overall_level = "Needs Support"
        level_summary = "Focusing on fundamentals and time management will help build solid momentum."

    # Strengths
    strengths = []
    if quiz_acc >= 70.0:
        strengths.append("Good consistency and accuracy in completed quizzes")
    else:
        strengths.append("Regular engagement with learning modules")
        
    if study_time >= 8.0:
        strengths.append(f"Dedicated study commitment with {study_time:.1f} hours logged")
    else:
        strengths.append("Quick adaptability to short practice sessions")
        
    strengths.append(f"Strongest performance in {best_subject} ({best_sub_score:.1f}%)")
    
    if mastery_score > prev_score:
        score_diff = round(mastery_score - prev_score, 1)
        strengths.append(f"Demonstrated upward score progression (+{score_diff} pts)")
        
    # Areas to Improve
    weak_areas = []
    weak_areas.append(f"{weakest_subject} (current score: {weakest_sub_score:.1f}%, below target)")
    
    if len(sorted_subjects) > 1 and sorted_subjects[-2][1] < 65.0:
        second_weakest = sorted_subjects[-2][0]
        weak_areas.append(f"{second_weakest} problem solving (requires more attempts)")
        
    if avg_time > 70.0:
        weak_areas.append(f"Time management ({avg_time:.1f}s average solving time per question)")
    else:
        weak_areas.append("Edge case handling and complex algorithmic questions")
        
    if mastery_score < 80.0:
        weak_areas.append(f"Increase overall mastery score towards target (current: {mastery_score:.1f}%)")
        
    # Behaviour Scores
    concept_understanding = round(np.clip((mastery_score * 0.7 + quiz_acc * 0.3), 40.0, 95.0), 1)
    problem_solving = round(np.clip((quiz_acc * 0.6 + (100.0 - min(avg_time, 100)) * 0.4), 35.0, 95.0), 1)
    behaviour = {
        "consistency": round(consistency, 1),
        "concept_understanding": round(concept_understanding, 1),
        "problem_solving": round(problem_solving, 1),
        "time_management": round(time_mgmt, 1)
    }
    
    # Dynamic AI Insights
    insights = []
    
    # Insight 1: Accuracy trend
    if quiz_acc >= prev_score:
        diff = round(quiz_acc - prev_score, 1)
        insights.append({
            "icon": "bi-graph-up-arrow",
            "type": "positive",
            "text": f"Your quiz accuracy has improved by {diff}% compared to earlier baselines, showing steady progress."
        })
    else:
        insights.append({
            "icon": "bi-info-circle",
            "type": "info",
            "text": "Quiz accuracy has slight variability; pacing yourself through questions will stabilize scores."
        })
        
    # Insight 2: Time vs conceptual depth
    if avg_time > 65.0:
        insights.append({
            "icon": "bi-clock-history",
            "type": "warning",
            "text": f"You spend an average of {avg_time:.1f}s on conceptual questions, indicating a need for timed practice in {weakest_subject}."
        })
    else:
        insights.append({
            "icon": "bi-lightning-charge",
            "type": "positive",
            "text": f"Fast question resolution speed ({avg_time:.1f}s avg). Ensure you double-check multi-step questions."
        })
        
    # Insight 3: Subject hierarchy
    insights.append({
        "icon": "bi-check2-circle",
        "type": "info",
        "text": f"{best_subject} is currently your strongest subject ({best_sub_score:.1f}%), while {weakest_subject} needs structured revision."
    })
    
    # AI Suggestion Box
    ai_suggestion = (
        f"Focus on {weakest_subject} with structured practice. Try answering 10 medium-level "
        f"questions daily to bring your mastery score above 75%."
    )
    
    return {
        "overall_learning_level": overall_level,
        "level_summary": level_summary,
        "assigned_cluster": f"Cluster {cluster_id} ({cluster_label})",
        "cluster_id": cluster_id,
        "cluster_label": cluster_label,
        "confidence_score": confidence,
        "mastery_score": mastery_score,
        "quiz_accuracy": quiz_acc,
        "avg_time_per_question": avg_time,
        "total_study_time": study_time,
        "total_attempts": attempts,
        "previous_score": prev_score,
        "subject_scores": subject_scores,
        "class_benchmarks": CLASS_BENCHMARKS,
        "strengths": strengths,
        "weak_areas": weak_areas,
        "behaviour": behaviour,
        "insights": insights,
        "ai_suggestion": ai_suggestion
    }
