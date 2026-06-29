# 🚀 Redrob AI – Intelligent Candidate Discovery & Ranking System

An AI-powered candidate ranking system built for the **Redrob AI Hackathon**. The system intelligently evaluates candidates by combining technical qualifications, behavioral signals, profile consistency, and penalty detection to generate an explainable ranking score.

---

# 📌 Problem Statement

Recruiters often receive thousands of applications for a single job opening. Manually evaluating candidates is time-consuming and inconsistent.

Our solution automates candidate discovery by:

- Parsing job descriptions
- Evaluating candidate technical skills
- Analyzing behavioral signals
- Detecting inconsistencies
- Applying penalties for suspicious profiles
- Producing an explainable final ranking score

---

# ✨ Features

- 📄 Automatic Job Description Parsing
- 🧠 Technical Skill Matching
- 📈 Behavioral Signal Scoring
- 🔍 Resume Consistency Detection
- ⚠️ Penalty Engine
- 🏆 Final Candidate Ranking
- 📊 Explainable Score Breakdown
- 💻 Interactive Streamlit Dashboard
- 📁 CSV Export of Ranked Candidates

---

# 🏗️ Project Architecture

```
                Job Description
                       │
                       ▼
                Job Parser Node
                       │
                       ▼
             Candidate Information
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
Technical Scorer  Behavioral Scorer  Consistency Detector
      │                │                │
      └────────────────┼────────────────┘
                       ▼
                 Penalty Engine
                       │
                       ▼
                Score Aggregator
                       │
                       ▼
               Final Candidate Score
                       │
                       ▼
            Streamlit Dashboard + CSV
```

---

# 📂 Project Structure

```
redrob-ai-ranker/

│
├── app/
│   └── streamlit_app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── feature_store/
│   └── skill_vocabulary.json
│
├── langgraph_pipeline/
│   ├── nodes/
│   │      parser.py
│   │      job_parser.py
│   │      technical_scorer.py
│   │      behavioral_scorer.py
│   │      consistency_detector.py
│   │      penalty_engine.py
│   │      score_aggregator.py
│   │
│   ├── graph.py
│   └── state.py
│
├── tests/
│
├── requirements.txt
│
└── README.md
```

---

# ⚙️ Tech Stack

- Python
- LangGraph
- LangChain
- Streamlit
- Pandas
- NumPy
- JSON
- FAISS (optional)
- Sentence Transformers (optional)

---

# 📊 Candidate Scoring Methodology

The final score combines multiple evaluation components.

## 1️⃣ Technical Score

Evaluates:

- Required Skills
- Experience
- Education
- Certifications

Weights:

| Component | Weight |
|-----------|--------|
| Skills | 50% |
| Experience | 25% |
| Education | 15% |
| Certifications | 10% |

---

## 2️⃣ Behavioral Score

Uses Redrob behavioral signals including:

- Profile Completeness
- Recruiter Response Rate
- Average Response Time
- Interview Completion Rate
- Offer Acceptance Rate
- Last Active Date
- Notice Period

---

## 3️⃣ Consistency Detection

Detects:

- Resume vs Title mismatch
- Skill inconsistency
- Frequent job hopping

Produces a consistency score.

---

## 4️⃣ Penalty Engine

Applies deductions for suspicious or inconsistent profiles.

Examples:

- Low consistency
- Missing information
- Poor profile quality

---

## 5️⃣ Final Ranking Score

```
Final Score =
(Technical Score × 70%)
+
(Behavioral Score × 30%)
− Penalties
```

Candidates are then ranked in descending order.

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Dragon17warrior01/redrob-ai-ranker.git
```

Move into the project

```bash
cd redrob-ai-ranker
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

Run the Streamlit dashboard

```bash
streamlit run app/streamlit_app.py
```

The application will open automatically in your browser.

---

# 📈 Dashboard Features

- Upload Job Description
- Parse Requirements
- Rank Candidates
- View Candidate Breakdown
- Score Visualization
- Download Ranked Candidates as CSV

---

# 📷 Sample Workflow

1. Upload Job Description
2. Parse Skills & Experience
3. Evaluate Candidate Dataset
4. Compute Technical Scores
5. Compute Behavioral Scores
6. Detect Inconsistencies
7. Apply Penalties
8. Aggregate Final Score
9. Display Ranked Candidates
10. Export Results

---

# 🎯 Future Improvements

- LLM-based Resume Understanding
- Semantic Skill Matching
- Interview Recommendation Engine
- Recruiter Feedback Loop
- Real-time Candidate Database
- Vector Search with FAISS/Pinecone
- Explainable AI Dashboard
- Cloud Deployment

---

# 👩‍💻 Team

**Prajakta Ningole**

Built for the **Redrob AI Intelligent Candidate Discovery & Ranking Challenge**.

---

# 📄 License

This project was developed for educational and hackathon purposes.
