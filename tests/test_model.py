import os
import joblib

def test_model_load_if_exists():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base, 'model', 'sivem_model.pkl')
    if os.path.exists(model_path):
        m = joblib.load(model_path)
        assert m is not None

