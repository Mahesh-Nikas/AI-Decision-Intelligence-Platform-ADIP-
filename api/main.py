from fastapi import FastAPI
from pydantic import BaseModel
from api.db import get_connection
from decision_engine.rules import make_decision
from model.inference import predict_score


app = FastAPI()

class DecisionRequest(BaseModel):
    decision_type: str
    inputs: dict


@app.get("/")
def health_check():
    return {"status": "AI Decision Intelligence API running"}

@app.post("/decide")
def decide(req: DecisionRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # 1) Store decision
    cursor.execute(
        "INSERT INTO decisions (decision_type) VALUES (%s)",
        (req.decision_type,)
    )
    decision_id = cursor.lastrowid

    # 2) Store inputs
    for k, v in req.inputs.items():
        cursor.execute(
            "INSERT INTO decision_inputs (decision_id, input_key, input_value) VALUES (%s,%s,%s)",
            (decision_id, k, str(v))
        )

    # 3) Predict using real ML model
    score = predict_score(req.inputs)

    cursor.execute(
        "INSERT INTO predictions (decision_id, model_name, model_version, score) VALUES (%s,%s,%s,%s)",
        (decision_id, "resume_model", "v1", score)
    )

    # 4) Decision Engine
    result = make_decision(
        decision_type=req.decision_type,
        model_score=score,
        inputs=req.inputs
    )


    # 5) Store outcome
    cursor.execute(
        "INSERT INTO outcomes (decision_id, final_result, feedback_notes) VALUES (%s,%s,%s)",
        (decision_id, result["decision"], result["reason"])
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "decision_id": decision_id,
        "final_decision": result
    }
