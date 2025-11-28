import os
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'sivem_model.pkl')

app = FastAPI()
origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class PredictBody(BaseModel):
    features: list | None = None
    registered_cases: int | None = None
    baleamentos: int | None = None
    detencoes: int | None = None
    mortes: int | None = None
    province: str | None = None

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/predict')
def predict(body: PredictBody):
    model = load_model()
    if model is None:
        raise HTTPException(status_code=503, detail='Modelo indisponivel')
    order = ['registered_cases', 'baleamentos', 'detencoes', 'mortes']
    if body.features is not None:
        arr = np.array(body.features, dtype=float).reshape(1, -1)
        try:
            proba = model.predict_proba(arr)[:, 1][0]
        except Exception:
            proba = None
        pred = int(model.predict(arr)[0])
        return {'prediction': pred, 'probability': proba}
    row = {
        'registered_cases': body.registered_cases or 0,
        'baleamentos': body.baleamentos or 0,
        'detencoes': body.detencoes or 0,
        'mortes': body.mortes or 0,
    }
    cols = order.copy()
    df = pd.DataFrame([row])
    if body.province is not None:
        df['province'] = body.province
        cols.append('province')
    X = df[cols]
    try:
        proba = model.predict_proba(X)[:, 1][0]
    except Exception:
        proba = None
    pred = int(model.predict(X)[0])
    return {'prediction': pred, 'probability': proba}
