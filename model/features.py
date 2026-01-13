# model/features.py
def build_features(inputs: dict) -> list:
    """
    Convert raw inputs into numeric feature vector.
    Keep this deterministic and versioned.
    """
    experience = float(inputs.get("experience_years", 0))
    confidence = float(inputs.get("confidence_score", 0))
    skills = inputs.get("skills", "")
    skill_count = len(skills.split(",")) if skills else 0

    # Feature order matters (document it)
    return [experience, confidence, skill_count]
