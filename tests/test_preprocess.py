import os
import pandas as pd
from scripts import preprocess as pp

def test_preprocess_outputs():
    pp.main()
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    long_out = os.path.join(base, 'data', 'processed', 'incidentes_clean_long.csv')
    wide_out = os.path.join(base, 'data', 'processed', 'incidentes_clean_wide.csv')
    assert os.path.exists(long_out)
    assert os.path.exists(wide_out)
    df_wide = pd.read_csv(wide_out)
    for col in ['registered_cases', 'baleamentos', 'detencoes', 'mortes']:
        assert col in df_wide.columns

