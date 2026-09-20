# LearnOS - AI-Based Personalised Learning System

A full-stack, machine-learning-powered personalized education platform built with Python, Flask, SQLite/SQLAlchemy, Scikit-Learn (K-Means Clustering), and modern Vanilla JavaScript + CSS. LearnOS dynamically analyzes student performance, clusters learning archetypes, generates AI-driven diagnostic insights, and adapts real-time recommendations through an interactive practice quiz feedback loop.

---

## 🌟 Key Features

- **Learner Profile Feature Aggregation**: Ingests multi-attempt learning records to build multidimensional student vectors (Accuracy, Mastery Score, Consistency, Time Management, and Subject Proficiency).
- **Unsupervised K-Means Clustering**: Dynamically evaluates candidate cluster counts ($K \in [2, 3, 4, 5]$) via inertia and **Silhouette Scores**, automatically selecting the best $K$ and mapping cluster centroids to meaningful learner segments (`Strong Performer`, `Consistent Learner`, `Developing Learner`, `Needs Support`, `Fast Learner`).
- **Dynamic AI Diagnostic Engine**: Generates real-time analysis highlighting strengths, conceptual bottlenecks, pacing analytics, and behavioural breakdown (Consistency, Understanding, Problem Solving, Time Management).
- **Personalised Recommendation Engine**: Generates 4 tiered priority cards, a 4-step sequential learning path, and targeted study materials linked directly to each student's weakest subjects.
- **Interactive Practice Quiz Engine**: Real-time timed assessment module across 5 core technical subjects (`Python`, `Data Structures`, `Algorithms`, `Database`, `Web Development`).
- **Complete End-to-End Feedback Loop**: Submitting a quiz instantly records the attempt, calculates accuracy, updates the ML feature vector, re-clusters the learner, regenerates AI insights & recommendations, and updates the dashboard live!
- **SaaS-Grade Modern UI**: Matches the reference progress report with dark navy sidebar navigation, clean white rounded cards, circular progress rings, and responsive Chart.js analytics.

---

## 📐 End-to-End Architecture & Feedback Loop

```
CSV / Ingested Learning Data (5,000+ Records)
                      ↓
           Data Preprocessing & Cleaning
                      ↓
       Learner Profile Feature Aggregation
                      ↓
       StandardScaler Feature Normalization
                      ↓
  K-Means Clustering (K=2..5 Silhouette Score Search)
                      ↓
          Learner Cluster & Label Derivation
                      ↓
       AI Diagnostic Analysis & Behaviour Scoring
                      ↓
        Personalised Recommendations & Path
                      ↓
        Web Dashboard, Profile & Analytics
                      ↓
       Practice Quiz Assessment & Submission
                      ↓
   Database Update (QuizAttempt & LearningRecord)
                      ↓
   [Auto-Recomputation & Dynamic UI Refresh Loop]
```

---

## 🛠 Tech Stack

- **Backend**: Python 3.14, Flask 3.1, Jinja2 Templates, Werkzeug
- **Database / ORM**: SQLite 3, SQLAlchemy (Flask-SQLAlchemy 3.1)
- **Machine Learning**: Scikit-Learn 1.8 (KMeans, StandardScaler, Silhouette Score), Pandas 3.0, NumPy 2.4, Joblib
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
- **Security**: Werkzeug password hashing, session-based authentication, sanitized database queries

---

## 📁 Project Structure

```
ai-personalised-learning/
│
├── app.py                     # Flask application factory and runner
├── config.py                  # Environment configurations & database URIs
├── requirements.txt           # Python dependency requirements
├── train_model.py             # Standalone ML training & K-evaluation script
├── README.md                  # System manual and documentation
├── .env.example               # Environment variables template
├── .gitignore
│
├── data/
│   ├── generate_data.py       # Realistic 5,000+ records dataset generator
│   ├── learning_data.csv      # Generated learning records with stable student IDs
│   └── quiz_questions.json    # Extensive question bank across 5 subjects
│
├── models/
│   ├── scaler.pkl             # Fitted StandardScaler
│   ├── kmeans.pkl             # Trained KMeans cluster model
│   └── model_metadata.json    # Optimal K, silhouette score, cluster centroids
│
├── ml/
│   ├── __init__.py
│   ├── preprocessing.py       # Data cleaning & learner-level feature aggregation
│   ├── clustering.py          # K-Means multi-K testing & prediction
│   ├── learner_analysis.py    # AI insights & learning behavior scoring
│   └── recommendation_engine.py # Personalized recommendations & learning path
│
├── database/
│   ├── __init__.py            # SQLAlchemy database initialization
│   ├── models.py              # Models: User, StudentProfile, LearningRecord, etc.
│   └── seed.py                # Database population & initial ML run script
│
├── routes/
│   ├── __init__.py            # Blueprint registration hub
│   ├── auth.py                # Login, registration, session auth
│   ├── dashboard.py           # Student dashboard view
│   ├── profile.py             # My Profile view & streak
│   ├── analysis.py            # AI Analysis view
│   ├── recommendations.py     # Personalised Recommendations view
│   ├── quiz.py                # Practice Quiz hub & active test interface
│   ├── progress.py            # Progress & Analytics view
│   ├── resources.py           # Learning resources directory
│   ├── settings.py            # Profile & password settings
│   └── api.py                 # RESTful APIs (submit quiz, refresh analysis, goals CRUD)
│
├── templates/
│   ├── base.html              # Core layout (dark navy sidebar, topbar, quote pill)
│   ├── login.html             # Login view
│   ├── register.html          # Registration view
│   ├── dashboard.html         # Dashboard (PDF Page 2)
│   ├── profile.html           # My Profile (PDF Page 3)
│   ├── ai_analysis.html       # AI Analysis (PDF Page 4)
│   ├── recommendations.html   # Recommendations (PDF Page 5)
│   ├── practice_quiz.html     # Quiz selector & recent attempts
│   ├── quiz_active.html       # Interactive timed quiz & ML result modal
│   ├── progress.html          # Progress & Chart.js visualizations
│   ├── resources.html         # Resources directory & preview modal
│   ├── settings.html          # User preferences & account settings
│   ├── 404.html               # 404 error page
│   └── 500.html               # 500 error page
│
├── static/
│   ├── css/
│   │   └── style.css          # Design system matching reference PDF
│   └── js/
│       ├── main.js            # Common UI controls & mobile sidebar
│       ├── dashboard.js       # Dashboard Chart.js line graph
│       ├── profile.js         # Goals AJAX CRUD
│       ├── analysis.js        # Live "Refresh Analysis" ML trigger
│       ├── recommendations.js # Interactive recommendations
│       ├── quiz.js            # Timed assessment engine & ML submission
│       └── progress.js        # Historical analytics & radar charts
│
└── instance/
    └── learning.db            # SQLite database file
```

---

## 🤖 Machine Learning Pipeline & Clustering

### 1. Feature Engineering
The raw dataset contains 5,200 records across 260 distinct students (`STU00001` to `STU00260`). The preprocessing engine aggregates these records into 14 distinct numerical features per learner:
- `avg_quiz_score`: Mean quiz score across attempts
- `quiz_accuracy`: Mean accuracy percentage
- `total_attempts`: Count of completed assessments
- `total_study_time`: Cumulative study hours
- `avg_time_per_question`: Latency per problem in seconds
- `completion_rate`: Test completion percentage
- `practice_questions`: Total practice problems attempted
- `consistency_score`: Uniformity of weekly engagement
- `time_management_score`: Speed vs accuracy ratio
- Subject scores: `Python`, `Data Structures`, `Algorithms`, `Database`, `Web Development`

### 2. StandardScaler & K-Means Multi-$K$ Evaluation
Features are normalized using `StandardScaler`. The model tests $K \in [2, 3, 4, 5]$ and evaluates clustering quality at runtime:

| Candidate $K$ | Silhouette Score | Inertia | Cluster Distribution | Evaluation Outcome |
|:---:|:---:|:---:|:---:|:---:|
| **$K = 2$** | **0.4330** | **1503.60** | **[133, 127]** | **Selected (Highest Silhouette Score)** |
| $K = 3$ | 0.3965 | 975.05 | [81, 97, 82] | Candidate |
| $K = 4$ | 0.2913 | 907.94 | [50, 82, 81, 47] | Suboptimal separation |
| $K = 5$ | 0.2492 | 840.87 | [58, 80, 53, 39, 30] | Fragmented clusters |

> **Important Note on Dynamic ML Execution:**  
> The selected $K=2$ and Silhouette Score of $0.4330$ are dynamically computed from the current 5,200-record dataset during training. The system does **not** hard-code these values. If new learning records or customized datasets are supplied, running `python train_model.py` will autonomously recalculate silhouette scores across candidate $K$ values, determine the optimal cluster configuration, and update `models/model_metadata.json` automatically.

### 3. Cluster Interpretation
- **Cluster 0 (`Strong Performer`)**: High average accuracy (87.9%), high consistency (82.3%), balanced question resolution time (54.7s).
- **Cluster 1 (`Needs Support` / `Developing Learner`)**: Moderate average accuracy (58.7%), higher time latency (87.9s), requires foundational revision in complex subjects like Data Structures.

---

## 🚀 Quickstart & Running Locally

### Step 1: Clone or Navigate to Directory
```bash
cd "c:\Users\Hemant\OneDrive\Desktop\adbms"
```

### Step 2: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 3: Generate Dataset (5,200 records)
```bash
python data/generate_data.py
```

### Step 4: Train ML Model & Evaluate $K$
```bash
python train_model.py
```

### Step 5: Seed Database & Initialize Demo User
```bash
python database/seed.py
```

### Step 6: Start Flask Web Server
```bash
python app.py
```

Open your browser at:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Demo Account Credentials

| Attribute | Value |
|---|---|
| **Email** | `demo@example.com` |
| **Password** | `Demo@123` |
| **Student ID** | `STU00001` |
| **Name** | Hemant Singh |

*(You can also register any new student account via the `/register` page).*

---

## 🌐 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard` | Returns current user's profile, metrics, and active recommendations |
| `GET` | `/api/profile` | Returns full learner profile, goals, and streak info |
| `GET` | `/api/analysis` | Returns AI analysis, confidence score, and subject comparisons |
| `POST` | `/api/analysis/refresh` | Re-executes ML analysis pipeline on latest student data |
| `GET` | `/api/recommendations` | Returns 4 priority cards and sequential learning path |
| `GET` | `/api/progress` | Returns chronological quiz attempt series for Chart.js |
| `POST` | `/api/quiz/submit` | Evaluates quiz, commits attempt, re-runs ML profile, and returns feedback |
| `POST` | `/api/goals` | Creates a new learning goal |
| `PUT` | `/api/goals/<id>` | Toggles goal completion or edits target date |
| `DELETE` | `/api/goals/<id>` | Deletes a learning goal |
| `GET` | `/api/resources` | Returns filterable learning resources |

---

## 🧪 Testing the Complete Feedback Loop

1. **Log in** with `demo@example.com` / `Demo@123`.
2. Inspect the **Dashboard** metrics (Mastery Score ~63-68%, Accuracy ~65-74%).
3. Navigate to **Practice Quiz** (`/practice-quiz`) and start a quiz (e.g. Python or Data Structures).
4. Answer the questions and click **Submit Assessment**.
5. The result modal will appear showing immediate grading and confirming that the **ML pipeline has synced**.
6. Return to **Dashboard** or **AI Analysis** — observe that the Mastery Score, Quiz Accuracy, Total Attempts, AI Insights, and Recommendations have dynamically updated!
7. Navigate to **My Profile** and check off a learning goal or create a new one.
8. Navigate to **AI Analysis** and click **Refresh Analysis** to observe live updates.

---

## 📄 License
Academic and Production Ready • Built with ❤️ for Advanced AI-Driven Education Systems.
