def make_decision(decision_type: str, model_score: float, inputs: dict) -> dict:
    """
    Central decision engine.
    AI suggests, rules decide.
    """

    if decision_type == "resume_screening":
        experience = int(inputs.get("experience_years", 0))

        # Safety rule
        if model_score < 0.50:
            return {
                "decision": "REJECT",
                "reason": "Low AI confidence score"
            }

        # Business rule
        if model_score >= 0.70 and experience >= 2:
            return {
                "decision": "SHORTLIST",
                "reason": "High score with sufficient experience"
            }

        # Human-in-the-loop fallback
        return {
            "decision": "REVIEW",
            "reason": "Borderline case, needs human review"
        }

    return {
        "decision": "UNKNOWN",
        "reason": "Unsupported decision type"
    }
