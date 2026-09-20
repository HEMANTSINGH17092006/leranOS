def generate_recommendations(analysis_result):
    """
    Generates dynamic personalised recommendations, a 4-step learning path, and resource links
    based on the learner's cluster analysis and subject performance.
    """
    mastery_score = analysis_result.get("mastery_score", 65.0)
    quiz_acc = analysis_result.get("quiz_accuracy", 70.0)
    avg_time = analysis_result.get("avg_time_per_question", 75.0)
    subject_scores = analysis_result.get("subject_scores", {})
    
    # Sort subjects to identify weak and strong areas
    sorted_subs = sorted(subject_scores.items(), key=lambda x: x[1])
    weakest_subj, weak_score = sorted_subs[0] if sorted_subs else ("Data Structures", 50.0)
    strongest_subj, strong_score = sorted_subs[-1] if sorted_subs else ("Python", 80.0)
    
    target_score = 80.0 if mastery_score < 80.0 else min(95.0, mastery_score + 10.0)
    
    # 1. Four Tiered Recommendations
    cards = []
    
    # Card 1: High Priority (Weakest Topic)
    cards.append({
        "id": "rec-1",
        "badge_class": "badge-danger",
        "priority": "High Priority",
        "title": f"Revise: {weakest_subj} Fundamentals",
        "description": f"Your accuracy in this topic ({weak_score:.0f}%) is below your overall performance ({quiz_acc:.0f}%). Strengthening basics will improve your mastery.",
        "estimated_time": "1.5 hrs",
        "expected_improvement": "+10%",
        "action_text": "Start Learning",
        "action_url": f"/resources?subject={weakest_subj}",
        "action_type": "resource",
        "subject": weakest_subj
    })
    
    # Card 2: Recommended (Practice)
    cards.append({
        "id": "rec-2",
        "badge_class": "badge-primary",
        "priority": "Recommended",
        "title": f"Practice: {weakest_subj} Quiz",
        "description": "You take more time on conceptual questions. Practice targeted questions to improve speed and confidence.",
        "estimated_time": "2 hrs",
        "expected_improvement": "+8%",
        "action_text": "Start Practice",
        "action_url": f"/practice-quiz?subject={weakest_subj}",
        "action_type": "quiz",
        "subject": weakest_subj
    })
    
    # Card 3: Suggested (Time Management or Next Subject)
    if avg_time > 65.0:
        cards.append({
            "id": "rec-3",
            "badge_class": "badge-warning",
            "priority": "Suggested",
            "title": "Improve Time Management",
            "description": f"Your average time per question is {avg_time:.1f}s. Try timed quizzes to improve your problem-solving speed.",
            "estimated_time": "1 hr",
            "expected_improvement": "+5%",
            "action_text": "View Strategies",
            "action_url": "/practice-quiz?difficulty=Easy",
            "action_type": "quiz",
            "subject": "General"
        })
    else:
        second_weakest = sorted_subs[1][0] if len(sorted_subs) > 1 else "Algorithms"
        cards.append({
            "id": "rec-3",
            "badge_class": "badge-warning",
            "priority": "Suggested",
            "title": f"Reinforce: {second_weakest}",
            "description": f"Solidify your understanding in {second_weakest} through intermediate level challenge questions.",
            "estimated_time": "1.5 hrs",
            "expected_improvement": "+6%",
            "action_text": "Practice Now",
            "action_url": f"/practice-quiz?subject={second_weakest}",
            "action_type": "quiz",
            "subject": second_weakest
        })
        
    # Card 4: For Later (Advanced Project / Topic)
    cards.append({
        "id": "rec-4",
        "badge_class": "badge-purple",
        "priority": "For Later",
        "title": f"Advanced: {strongest_subj} Projects",
        "description": f"Once you reach 80% accuracy, you can move to advanced {strongest_subj} projects to build real-world experience.",
        "estimated_time": "3 hrs",
        "expected_improvement": "+15%",
        "action_text": "Preview Content",
        "action_url": f"/resources?subject={strongest_subj}",
        "action_type": "resource",
        "subject": strongest_subj
    })
    
    # 2. Recommended Learning Path (4 steps)
    learning_path = [
        {
            "step": 1,
            "title": f"Revise {weakest_subj} Concepts",
            "subtitle": "Complete notes and examples",
            "duration": "1.5 hrs",
            "status": "in_progress",
            "action_url": f"/resources?subject={weakest_subj}"
        },
        {
            "step": 2,
            "title": f"Practice {weakest_subj} Questions",
            "subtitle": "Attempt 10-15 targeted questions",
            "duration": "2 hrs",
            "status": "pending",
            "action_url": f"/practice-quiz?subject={weakest_subj}"
        },
        {
            "step": 3,
            "title": "Give a Timed Quiz",
            "subtitle": "Focus on speed and accuracy",
            "duration": "1 hr",
            "status": "pending",
            "action_url": "/practice-quiz"
        },
        {
            "step": 4,
            "title": f"Work on {strongest_subj} Mini Project",
            "subtitle": "Apply what you learned in practical builds",
            "duration": "3 hrs",
            "status": "pending",
            "action_url": f"/resources?subject={strongest_subj}"
        }
    ]
    
    # 3. Recommended Resources matched to weaknesses
    recommended_resources = [
        {
            "title": f"{weakest_subj} - Concept Notes",
            "type_label": "PDF • 12 pages",
            "type": "Notes",
            "icon": "bi-file-earmark-pdf text-danger",
            "action_url": f"/resources?subject={weakest_subj}"
        },
        {
            "title": f"{weakest_subj} - Video Lecture",
            "type_label": "Video • 25 mins",
            "type": "Video",
            "icon": "bi-play-circle text-primary",
            "action_url": f"/resources?subject={weakest_subj}"
        },
        {
            "title": "Practice Questions - Set 1",
            "type_label": "Quiz • 10 questions",
            "type": "Quiz",
            "icon": "bi-question-square text-success",
            "action_url": f"/practice-quiz?subject={weakest_subj}"
        },
        {
            "title": "Time Management Tips",
            "type_label": "Article • 8 mins",
            "type": "Article",
            "icon": "bi-clock text-warning",
            "action_url": "/resources"
        },
        {
            "title": f"{strongest_subj} Mini Project Ideas",
            "type_label": "Guide • 5 projects",
            "type": "Project",
            "icon": "bi-code-slash text-info",
            "action_url": f"/resources?subject={strongest_subj}"
        }
    ]
    
    # 4. Expected Outcomes
    expected_outcomes = [
        f"Improve quiz accuracy to {min(90.0, quiz_acc + 10.0):.0f}%",
        f"Reduce average time to {max(45.0, avg_time - 15.0):.0f} sec",
        f"Strengthen {strongest_subj} and {weakest_subj} proficiency",
        f"Increase overall mastery score to {target_score:.0f}%",
        "Build confidence for advanced engineering topics"
    ]
    
    return {
        "target_mastery_score": target_score,
        "recommendations": cards,
        "learning_path": learning_path,
        "recommended_resources": recommended_resources,
        "expected_outcomes": expected_outcomes
    }
