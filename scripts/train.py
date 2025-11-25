import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "incidentes_clean_wide.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "sivem_model.pkl")

def main():
    if not os.path.exists(DATA_PATH):
        return
    df = pd.read_csv(DATA_PATH)
    X = df.select_dtypes(include=["number"]).drop(columns=[c for c in ["registered_cases"] if c in df.columns])
    y = (df.get("registered_cases") > 0).astype(int) if "registered_cases" in df.columns else None
    if y is None:
        return
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

if __name__ == "__main__":
    main()