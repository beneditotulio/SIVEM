import os
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'sivem_model.pkl')

app = FastAPI(title="SIVEM API (dev)")

# CORS (ajuste conforme necessidade)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve ficheiros estáticos do relatório (acesso: /reports/incidentes_report.html)
# directory path is relative to api/main.py -> ../data/processed
app.mount("/reports", StaticFiles(directory="../data/processed", html=True), name="reports")

# Modelos de request (ajuste conforme o seu esquema real)
class ForecastReq(BaseModel):
    province: str
    year: int

class PredictReq(BaseModel):
    province: str
    registered_cases: int
    baleamentos: int = 0
    detencoes: int = 0
    mortes: int = 0

# Health
@app.get("/health")
async def health():
    return {"status": "ok"}

# Provinces (retorna lista de províncias)
@app.get("/provinces")
async def provinces():
    # adapte para ler de ficheiro ou DB; aqui um fallback
    return {"provinces": ["Cabo Delgado","Gaza","Inhambane","Manica","Maputo","Maputo Provincia","Nampula","Niassa","Sofala","Tete","Zambezia"]}

# Forecast (exemplo mínimo)
@app.post("/forecast")
async def forecast(req: ForecastReq):
    if not req.province:
        raise HTTPException(status_code=400, detail="province required")
    # substitua com lógica real (modelo) — aqui resposta mock
    return {
        "province": req.province,
        "year": req.year,
        "probability": 0.23,
        "prediction": 0,
        "registered_cases_mean": 4.5,
        "expected_counts": {"baleamentos": 1, "detencoes": 0, "mortes": 0}
    }

# Predict (exemplo mínimo)
@app.post("/predict")
async def predict(req: PredictReq):
    if not req.province:
        raise HTTPException(status_code=400, detail="province required")
    # lógica real aqui — mock response
    probability = min(1.0, 0.05 * req.registered_cases + 0.2 * req.baleamentos + 0.3 * req.mortes)
    prediction = 1 if probability > 0.5 else 0
    return {"province": req.province, "probability": probability, "prediction": prediction}
