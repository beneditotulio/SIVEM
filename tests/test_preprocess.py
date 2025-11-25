import importlib

def test_import_preprocess():
    m = importlib.import_module("scripts.preprocess")
    assert hasattr(m, "main")