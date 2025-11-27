import os
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_predict_unavailable_model():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base, 'model', 'sivem_model.pkl')
    if not os.path.exists(model_path):
        r = client.post('/predict', json={'features': [0,0,0,0]})
        assert r.status_code == 503

