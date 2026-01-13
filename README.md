
# AI Decision Intelligence Platform (ADIP)
## Complete Beginner-to-Advanced Guide (Start → End, No Gaps)

This README explains **EVERY SINGLE PART** of the project:
- what you do
- why you do it
- what code you write
- what that code actually does internally

You can read this file alone and understand the **entire project without errors or confusion**.

------------------------------------------------------------

## 1. WHAT IS THIS PROJECT?

This project is a **Decision System powered by AI**, not just a machine learning model.

Real companies NEVER use AI alone.
They use:

- API (to receive requests)
- Database (to remember everything)
- AI model (to predict score)
- Rules (to control AI)
- Feedback (to improve later)

This project teaches **how AI really works in production**.

------------------------------------------------------------

## 2. COMPLETE PROJECT STRUCTURE

```
AI-Decision-Intelligence-Platform-ADIP/
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── db.py
│
├── decision_engine/
│   ├── __init__.py
│   └── rules.py
│
├── model/
│   ├── __init__.py
│   ├── features.py
│   ├── trainer.py
│   └── inference.py
│
├── data/
│   └── schema.sql
│
├── .venv/
└── README.md
```

Each folder has **ONE clear responsibility**.
No folder does multiple jobs.

------------------------------------------------------------

## 3. DATABASE (SYSTEM MEMORY)

### Why database is required

AI cannot remember past decisions.
Database stores:

- what input came
- what AI predicted
- what decision was taken
- what final outcome happened

Without database:
❌ no learning
❌ no audit
❌ no improvement

------------------------------------------------------------

### data/schema.sql (WRITE EXACTLY THIS)

```sql
CREATE TABLE decisions (
    decision_id INT AUTO_INCREMENT PRIMARY KEY,
    decision_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE decision_inputs (
    input_id INT AUTO_INCREMENT PRIMARY KEY,
    decision_id INT,
    input_key VARCHAR(100),
    input_value VARCHAR(255),
    FOREIGN KEY (decision_id) REFERENCES decisions(decision_id)
);

CREATE TABLE predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    decision_id INT,
    model_name VARCHAR(50),
    model_version VARCHAR(20),
    score DECIMAL(5,4),
    FOREIGN KEY (decision_id) REFERENCES decisions(decision_id)
);

CREATE TABLE outcomes (
    outcome_id INT AUTO_INCREMENT PRIMARY KEY,
    decision_id INT,
    final_result VARCHAR(50),
    feedback_notes TEXT,
    FOREIGN KEY (decision_id) REFERENCES decisions(decision_id)
);
```

### What each table means (simple)

- decisions → one request
- decision_inputs → what data AI saw
- predictions → what AI predicted
- outcomes → final truth

------------------------------------------------------------

## 4. DECISION ENGINE (RULES FIRST, AI SECOND)

### Why rules are mandatory

AI gives probability.
Rules give control.

Companies NEVER allow AI to decide alone.

------------------------------------------------------------

### decision_engine/rules.py

```python
def make_decision(decision_type, model_score, inputs):
    if decision_type == "resume_screening":
        experience = int(inputs.get("experience_years", 0))

        if model_score < 0.50:
            return {"decision": "REJECT", "reason": "Low confidence score"}

        if model_score >= 0.70 and experience >= 2:
            return {"decision": "SHORTLIST", "reason": "Good profile"}

        return {"decision": "REVIEW", "reason": "Borderline case"}

    return {"decision": "UNKNOWN", "reason": "Unsupported decision type"}
```

### What this code does

- takes AI score
- applies safety rules
- returns final decision with reason

------------------------------------------------------------

## 5. MACHINE LEARNING PART

### Important truth

ML does NOT decide.
ML only predicts a number.

------------------------------------------------------------

### model/features.py

```python
def build_features(inputs):
    experience = float(inputs.get("experience_years", 0))
    confidence = float(inputs.get("confidence_score", 0))
    skills = inputs.get("skills", "")
    skill_count = len(skills.split(",")) if skills else 0

    return [experience, confidence, skill_count]
```

### Why this exists

ML understands ONLY numbers.
This converts raw input into numbers.

------------------------------------------------------------

### model/trainer.py

```python
from sklearn.linear_model import LogisticRegression
import joblib

X = [
    [2, 7, 2],
    [1, 4, 1],
    [3, 8, 3],
    [0, 3, 0]
]
y = [1, 0, 1, 0]

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "model/resume_model_v1.joblib")
```

### What happens here

- training happens ONCE
- model is saved to file
- later we only load it

------------------------------------------------------------

### model/inference.py

```python
import joblib
#from model.features import build_features

_model = joblib.load("model/resume_model_v1.joblib")

def predict_score(inputs):
    features = build_features(inputs)
    return float(_model.predict_proba([features])[0][1])
```

### Why separate inference

- training is slow
- prediction must be fast

------------------------------------------------------------

## 6. API LAYER (SYSTEM CONTROLLER)

### Why API exists

Users cannot talk to ML directly.
API controls the flow safely.

------------------------------------------------------------

### api/db.py

```python
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="AI"
    )
```

This file ONLY gives DB connection.

------------------------------------------------------------

### api/main.py (MOST IMPORTANT FILE)

```python
from fastapi import FastAPI
from pydantic import BaseModel
#from api.db import get_connection
#from decision_engine.rules import make_decision
#from model.inference import predict_score

app = FastAPI()

class DecisionRequest(BaseModel):
    decision_type: str
    inputs: dict

@app.get("/")
def health():
    return {"status": "AI Decision Intelligence API running"}

@app.post("/decide")
def decide(req: DecisionRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO decisions (decision_type) VALUES (%s)",
        (req.decision_type,)
    )
    decision_id = cur.lastrowid

    for k, v in req.inputs.items():
        cur.execute(
            "INSERT INTO decision_inputs VALUES (NULL, %s, %s, %s)",
            (decision_id, k, str(v))
        )

    score = predict_score(req.inputs)

    cur.execute(
        "INSERT INTO predictions VALUES (NULL, %s, %s, %s, %s)",
        (decision_id, "resume_model", "v1", score)
    )

    result = make_decision(req.decision_type, score, req.inputs)

    cur.execute(
        "INSERT INTO outcomes VALUES (NULL, %s, %s, %s)",
        (decision_id, result["decision"], result["reason"])
    )

    conn.commit()
    conn.close()

    return {
        "decision_id": decision_id,
        "final_decision": result
    }
```

### What happens step-by-step

1. API receives JSON
2. Decision row created
3. Inputs stored
4. ML predicts score
5. Prediction stored
6. Rules decide
7. Outcome stored
8. Response returned

------------------------------------------------------------

## 7. HOW TO RUN THE PROJECT

```bash
python -m uvicorn api.main:app --reload
```

Open browser:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

------------------------------------------------------------

## 8. COMPLETE FLOW (MEMORIZE)

Client → API → Database → Features → ML → Rules → Database → Response

------------------------------------------------------------

## 9. WHAT YOU CAN EXTEND

- add new decision types
- improve features
- retrain model
- add feedback learning
- add monitoring

------------------------------------------------------------

## 10. RESUME LINE

Built an end-to-end AI Decision Intelligence Platform using FastAPI, MySQL, rule-based decisioning, machine learning inference, and feedback-driven system design.

------------------------------------------------------------

## FINAL NOTE

If you understand THIS README,
you understand how **real AI systems work**.

No shortcuts.
No magic.
Only clean system design.
