import os
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "sivem_model.pkl")

def predict(features):
    if not os.path.exists(MODEL_PATH):
        return None
    model = joblib.load(MODEL_PATH)
    X = np.array(features).reshape(1, -1)
    y = model.predict(X)
    return y[0]

if __name__ == "__main__":
    print(predict([0, 0, 0]))