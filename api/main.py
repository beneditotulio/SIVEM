from fastapi import FastAPI
from pydantic import BaseModel
import os
import joblib
import numpy as np

app = FastAPI()

class PredictInput(BaseModel):
    features: list[float]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "sivem_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "encoder.pkl")

def _load(path):
    if os.path.exists(path):
        return joblib.load(path)
    return None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(inp: PredictInput):
    model = _load(MODEL_PATH)
    if model is None:
        return {"error": "modelo indisponivel"}
    X = np.array(inp.features).reshape(1, -1)
    y = model.predict(X)
    return {"prediction": y[0]}