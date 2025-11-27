import os
import argparse
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'sivem_model.pkl')

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError('Modelo nao encontrado')
    return joblib.load(MODEL_PATH)

def predict_from_file(model, data_path, out_path=None):
    df = pd.read_csv(data_path)
    cols = ['registered_cases', 'baleamentos', 'detencoes', 'mortes']
    if 'province' in df.columns:
        cols.append('province')
    X = df[cols]
    preds = model.predict(X)
    proba = None
    try:
        proba = model.predict_proba(X)[:, 1]
    except Exception:
        pass
    out = df.copy()
    out['incident_pred'] = preds
    if proba is not None:
        out['incident_proba'] = proba
    if out_path:
        out.to_csv(out_path, index=False)
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()
    model = load_model()
    out = predict_from_file(model, args.data, args.out)
    print({'rows': len(out), 'out': args.out})

if __name__ == '__main__':
    main()

