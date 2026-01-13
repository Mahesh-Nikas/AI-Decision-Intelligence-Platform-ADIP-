# model/trainer.py
import joblib
from sklearn.linear_model import LogisticRegression

def train_and_save():
    # Toy training data (replace later with real outcomes)
    X = [
        [2, 7, 2],  # shortlisted
        [1, 4, 1],  # rejected
        [3, 8, 3],  # shortlisted
        [0, 3, 0],  # rejected
    ]
    y = [1, 0, 1, 0]  # 1=good, 0=bad

    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, "model/resume_model_v1.joblib")
    print("Model saved: resume_model_v1.joblib")

if __name__ == "__main__":
    train_and_save()
