# model/inference.py
import joblib
from model.features import build_features

MODEL_PATH = "model/resume_model_v1.joblib"
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_score(inputs: dict) -> float:
    model = load_model()
    features = build_features(inputs)
    proba = model.predict_proba([features])[0][1]  # probability of class=1
    return float(round(proba, 4))
