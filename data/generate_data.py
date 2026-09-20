import os
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = DATA_DIR / "learning_data.csv"

SUBJECTS = [
    "Python",
    "Data Structures",
    "Algorithms",
    "Database",
    "Web Development"
]

DIFFICULTIES = ["Easy", "Medium", "Hard"]

# We will generate 260 students with ~20 records each -> ~5,200 records
NUM_STUDENTS = 260
RECORDS_PER_STUDENT = 20

def generate_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)
    random.seed(42)
    
    records = []
    base_time = datetime(2025, 9, 1)

    for s_idx in range(1, NUM_STUDENTS + 1):
        student_id = f"STU{s_idx:05d}"
        
        # Determine student persona/archetype to create natural clustering patterns
        if s_idx == 1:
            # Hemant Singh (Demo user): Developing Learner with solid Python, needs support on Data Structures
            persona = "developing"
            base_acc = 74.0
            base_time_per_q = 75.4
            base_consistency = 78.0
            base_time_mgmt = 59.0
            subject_affinity = {
                "Python": 72.0,
                "Data Structures": 61.0,
                "Algorithms": 54.0,
                "Database": 48.0,
                "Web Development": 66.0
            }
        else:
            archetype_choice = random.random()
            if archetype_choice < 0.30:
                # Strong Performer / High Performer
                persona = "high_performer"
                base_acc = random.uniform(82, 96)
                base_time_per_q = random.uniform(35, 55)
                base_consistency = random.uniform(80, 95)
                base_time_mgmt = random.uniform(80, 95)
                subject_affinity = {sub: base_acc + random.uniform(-6, 6) for sub in SUBJECTS}
            elif archetype_choice < 0.65:
                # Developing Learner
                persona = "developing"
                base_acc = random.uniform(62, 79)
                base_time_per_q = random.uniform(60, 85)
                base_consistency = random.uniform(65, 82)
                base_time_mgmt = random.uniform(55, 75)
                subject_affinity = {sub: base_acc + random.uniform(-10, 10) for sub in SUBJECTS}
            else:
                # Needs Support
                persona = "needs_support"
                base_acc = random.uniform(40, 60)
                base_time_per_q = random.uniform(80, 115)
                base_consistency = random.uniform(40, 62)
                base_time_mgmt = random.uniform(40, 60)
                subject_affinity = {sub: base_acc + random.uniform(-8, 8) for sub in SUBJECTS}

        student_time = base_time + timedelta(days=random.randint(0, 15))
        prev_score = max(30.0, round(base_acc - random.uniform(10, 20), 1))

        for r_idx in range(1, RECORDS_PER_STUDENT + 1):
            subject = SUBJECTS[(r_idx - 1) % len(SUBJECTS)]
            diff = random.choices(DIFFICULTIES, weights=[0.4, 0.45, 0.15])[0]
            
            diff_modifier = 5 if diff == "Easy" else (0 if diff == "Medium" else -8)
            
            # Progress over attempts: slight improvement
            growth = (r_idx / RECORDS_PER_STUDENT) * random.uniform(4, 12)
            
            raw_acc = subject_affinity[subject] + diff_modifier + growth + random.gauss(0, 4)
            quiz_accuracy = round(min(100.0, max(25.0, raw_acc)), 1)
            quiz_score = round(min(100.0, max(20.0, quiz_accuracy + random.gauss(0, 3))), 1)
            
            study_hours = round(max(0.5, random.uniform(1.0, 3.5) + (1.0 if persona == "high_performer" else 0.5)), 1)
            avg_time_q = round(max(25.0, base_time_per_q + random.gauss(0, 6) - (growth * 0.5)), 1)
            completion = round(min(100.0, max(60.0, 95.0 + random.gauss(0, 4))), 1)
            practice_qs = random.randint(8, 25)
            
            time_mgmt = round(min(100.0, max(30.0, base_time_mgmt + random.gauss(0, 4))), 1)
            consistency = round(min(100.0, max(30.0, base_consistency + random.gauss(0, 4))), 1)
            
            current_score = quiz_score
            timestamp = student_time + timedelta(days=r_idx * 4, hours=random.randint(1, 8))
            
            record = {
                "student_id": student_id,
                "subject": subject,
                "quiz_score": quiz_score,
                "quiz_accuracy": quiz_accuracy,
                "total_attempts": r_idx,
                "study_time_hours": study_hours,
                "average_time_per_question": avg_time_q,
                "completion_rate": completion,
                "previous_score": prev_score,
                "current_score": current_score,
                "practice_questions": practice_qs,
                "difficulty_level": diff,
                "time_management_score": time_mgmt,
                "consistency_score": consistency,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            records.append(record)
            prev_score = current_score

    # Write to CSV
    fieldnames = list(records[0].keys())
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Successfully generated {len(records)} realistic learning records in {OUTPUT_CSV}")
    return len(records)

if __name__ == "__main__":
    generate_dataset()
