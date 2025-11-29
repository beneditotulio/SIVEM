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

class ForecastBody(BaseModel):
    province: str
    year: int
    external: dict | None = None

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

def load_wide():
    path = os.path.join(BASE_DIR, 'data', 'processed', 'incidentes_clean_wide.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    if 'start_date' in df.columns:
        try:
            df['start_date'] = pd.to_datetime(df['start_date'])
        except Exception:
            pass
    return df

def load_raw():
    path = os.path.join(BASE_DIR, 'data', 'raw', 'dados_de_incidentes_manifestacoes_mocambique(2024).csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    return df

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/provinces')
def provinces():
    df = load_wide()
    if df is None:
        df = load_raw()
    if df is None:
        return {'provinces': []}
    if 'country' in df.columns:
        try:
            df = df[df['country'].astype(str).str.lower().str.contains('mozambique')]
        except Exception:
            pass
    col = 'province' if 'province' in df.columns else None
    if col is None:
        return {'provinces': []}
    vals = sorted([str(v) for v in df[col].dropna().unique()])
    return {'provinces': vals}

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

@app.post('/forecast')
def forecast(body: ForecastBody):
    df = load_wide()
    if df is None:
        raise HTTPException(status_code=400, detail='Dados processados indisponiveis')
    col_prov = 'province' if 'province' in df.columns else None
    if col_prov is None:
        raise HTTPException(status_code=400, detail='Coluna province ausente')
    subset = df[df[col_prov] == body.province]
    if 'start_date' in subset.columns and subset['start_date'].notna().any():
        subset_year = subset[subset['start_date'].dt.year == body.year]
        if len(subset_year) > 0:
            subset = subset_year
    if len(subset) == 0:
        subset = df
    rc_mean = float(subset['registered_cases'].mean()) if 'registered_cases' in subset.columns else 0.0
    p_b = float((subset['baleamentos'] == 1).mean()) if 'baleamentos' in subset.columns else 0.0
    p_d = float((subset['detencoes'] == 1).mean()) if 'detencoes' in subset.columns else 0.0
    p_m = float((subset['mortes'] == 1).mean()) if 'mortes' in subset.columns else 0.0
    exp_b = int(round(rc_mean * p_b))
    exp_d = int(round(rc_mean * p_d))
    exp_m = int(round(rc_mean * p_m))
    model = load_model()
    prob = None
    pred = None
    if model is not None:
        X = {
            'registered_cases': rc_mean,
            'baleamentos': 1 if p_b > 0.1 else 0,
            'detencoes': 1 if p_d > 0.1 else 0,
            'mortes': 1 if p_m > 0.1 else 0,
        }
        X = pd.DataFrame([X])
        X[col_prov] = body.province
        try:
            prob = float(model.predict_proba(X)[0, 1])
        except Exception:
            prob = None
        try:
            pred = int(model.predict(X)[0])
        except Exception:
            pred = None
    result = {
        'province': body.province,
        'year': body.year,
        'prediction': pred,
        'probability': prob,
        'registered_cases_mean': rc_mean,
        'expected_counts': {
            'baleamentos': exp_b,
            'detencoes': exp_d,
            'mortes': exp_m,
        },
        'baselines': {
            'p_baleamentos': p_b,
            'p_detencoes': p_d,
            'p_mortes': p_m,
        }
    }
    return result
