import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_WIDE = os.path.join(BASE_DIR, 'data', 'processed', 'incidentes_clean_wide.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data():
    df = pd.read_csv(DATA_WIDE)
    return df

def build_dataset(df):
    y_col = 'incident_tomorrow'
    if y_col not in df.columns:
        df[y_col] = (df['registered_cases'] > 0).astype(int)
    features = ['registered_cases', 'baleamentos', 'detencoes', 'mortes']
    if 'province' in df.columns:
        features.append('province')
    X = df[features].copy()
    y = df[y_col].astype(int)
    cat_cols = [c for c in ['province'] if c in X.columns]
    num_cols = [c for c in X.columns if c not in cat_cols]
    preprocessor = ColumnTransformer([
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ], remainder='passthrough')
    model = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42, n_jobs=-1)
    pipe = Pipeline(steps=[('prep', preprocessor), ('clf', model)])
    return X, y, pipe, preprocessor

def train_and_eval(X, y, pipe):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, zero_division=0)),
        'f1': float(f1_score(y_test, y_pred, zero_division=0)),
    }
    return pipe, metrics

def save_artifacts(pipe, preprocessor):
    model_path = os.path.join(MODEL_DIR, 'sivem_model.pkl')
    enc_path = os.path.join(MODEL_DIR, 'encoder.pkl')
    joblib.dump(pipe, model_path)
    try:
        enc = pipe.named_steps['prep'].transformers_[0][1]
        joblib.dump(enc, enc_path)
    except Exception:
        joblib.dump(preprocessor, enc_path)
    return {'model': model_path, 'encoder': enc_path}

def main():
    df = load_data()
    X, y, pipe, preprocessor = build_dataset(df)
    pipe, metrics = train_and_eval(X, y, pipe)
    paths = save_artifacts(pipe, preprocessor)
    print({'artifacts': paths, 'metrics': metrics})

if __name__ == '__main__':
    main()

