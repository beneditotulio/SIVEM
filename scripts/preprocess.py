import os
import re
import unicodedata
import pandas as pd
import numpy as np
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOT = True
except Exception:
    plt = None
    sns = None
    HAS_PLOT = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'dados_de_incidentes_manifestacoes_mocambique_2024.xlsx')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

def _norm_colnames(cols):
    return [unicodedata.normalize('NFKD', str(c)).encode('ascii', 'ignore').decode('ascii').strip().lower() for c in cols]

def _find_col(df, candidates):
    norm_cols = _norm_colnames(df.columns)
    for cand in candidates:
        cn = unicodedata.normalize('NFKD', cand).encode('ascii', 'ignore').decode('ascii').strip().lower()
        for i, nc in enumerate(norm_cols):
            if cn == nc:
                return df.columns[i]
    for cand in candidates:
        cn = unicodedata.normalize('NFKD', cand).encode('ascii', 'ignore').decode('ascii').strip().lower()
        for i, nc in enumerate(norm_cols):
            if cn in nc or nc in cn:
                return df.columns[i]
    return None

def _parse_period(val):
    if pd.isna(val):
        return pd.NaT
    s = str(val).strip()
    s = s.replace('\u2013', '-').replace('–', '-').replace('—', '-').replace('\u2014', '-')
    m_single = re.search(r'(\d{1,2})\/(\d{1,2})\/(\d{4})', s)
    if m_single:
        d, m, y = m_single.groups()
        y = int(y)
        if y == 2004:
            y = 2024
        try:
            return pd.Timestamp(year=y, month=int(m), day=int(d))
        except Exception:
            return pd.NaT
    m_range = re.search(r'(\d{1,2})\s*[-]\s*(\d{1,2})\/(\d{1,2})\/(\d{4})', s)
    if m_range:
        d1, d2, m, y = m_range.groups()
        y = int(y)
        if y == 2004:
            y = 2024
        try:
            return pd.Timestamp(year=y, month=int(m), day=int(d1))
        except Exception:
            return pd.NaT
    m_alt = re.search(r'(\d{1,2}).*?(\d{1,2})\/(\d{4})', s)
    if m_alt:
        d1, m, y = m_alt.groups()
        y = int(y)
        if y == 2004:
            y = 2024
        try:
            return pd.Timestamp(year=y, month=int(m), day=int(d1))
        except Exception:
            return pd.NaT
    return pd.NaT

def _strip_accents(s):
    if s is None:
        return None
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')

def _normalize_type(s):
    if s is None:
        return None
    t = _strip_accents(str(s)).lower().strip()
    t = re.sub(r'\s+', ' ', t)
    if t == 'baleamentos':
        return 'baleamentos'
    if t == 'mortes':
        return 'mortes'
    if t == 'detencoes':
        return 'detencoes'
    return t

def _split_types(s):
    if pd.isna(s):
        return []
    x = str(s)
    x = x.replace(' / ', ',').replace('/', ',').replace(';', ',').replace('|', ',')
    x = re.sub(r'\s+e\s+', ',', x)
    parts = [p.strip() for p in x.split(',') if p.strip()]
    parts = [_normalize_type(p) for p in parts]
    parts = [p for p in parts if p]
    return list(dict.fromkeys(parts))

def main():
    engine = None
    try:
        import openpyxl  # noqa: F401
        engine = 'openpyxl'
    except Exception:
        msg = 'Dependencia ausente: openpyxl. Instale com "pip install openpyxl".'
        print({'error': msg, 'file': INPUT_PATH})
        return
    df = pd.read_excel(INPUT_PATH, engine=engine)
    col_period = _find_col(df, ['period', 'periodo', 'período'])
    col_cases = _find_col(df, ['registered_cases', 'casos_registados', 'casos', 'registados'])
    col_type = _find_col(df, ['incident_type', 'tipo_incidente', 'tipo', 'incidente', 'incidentes'])
    col_province = _find_col(df, ['province', 'provincia', 'província'])
    if col_period is None:
        raise RuntimeError('Coluna period nao encontrada')
    if col_cases is None:
        raise RuntimeError('Coluna registered_cases nao encontrada')
    if col_type is None:
        raise RuntimeError('Coluna incident_type nao encontrada')
    if col_province is None:
        col_province = 'province'
        if 'province' not in df.columns:
            df[col_province] = np.nan
    df['start_date'] = df[col_period].apply(_parse_period)
    df['start_date'] = df['start_date'].apply(lambda t: t.replace(year=2024) if (not pd.isna(t) and t.year == 2004) else t)
    df['registered_cases'] = pd.to_numeric(df[col_cases], errors='coerce')
    df['registered_cases'] = df['registered_cases'].fillna(0).astype(int)
    df['types'] = df[col_type].apply(_split_types)
    df_long = df.copy()
    df_long = df_long.explode('types').reset_index(drop=True)
    df_long = df_long[df_long['types'].notna()]
    df_wide = df.copy()
    for t in ['baleamentos', 'detencoes', 'mortes']:
        df_wide[t] = df_wide['types'].apply(lambda lst: 1 if t in (lst or []) else 0)
    long_out = os.path.join(PROCESSED_DIR, 'incidentes_clean_long.csv')
    wide_out = os.path.join(PROCESSED_DIR, 'incidentes_clean_wide.csv')
    df_long.to_csv(long_out, index=False)
    df_wide.to_csv(wide_out, index=False)
    figs = []
    if HAS_PLOT:
        sns.set(style='whitegrid')
    if HAS_PLOT and df_wide['start_date'].notna().any():
        weekly = df_wide[df_wide['start_date'].notna()].groupby(pd.Grouper(key='start_date', freq='W'))['registered_cases'].sum().reset_index()
        monthly = df_wide[df_wide['start_date'].notna()].groupby(pd.Grouper(key='start_date', freq='M'))['registered_cases'].sum().reset_index()
        f1 = plt.figure(figsize=(10,4))
        plt.plot(weekly['start_date'], weekly['registered_cases'])
        plt.title('Tendencia semanal')
        plt.xlabel('Semana')
        plt.ylabel('Casos registados')
        p1 = os.path.join(PROCESSED_DIR, 'fig_tendencia_semanal.png')
        f1.tight_layout()
        f1.savefig(p1)
        plt.close(f1)
        figs.append(p1)
        f2 = plt.figure(figsize=(10,4))
        plt.plot(monthly['start_date'], monthly['registered_cases'])
        plt.title('Tendencia mensal')
        plt.xlabel('Mes')
        plt.ylabel('Casos registados')
        p2 = os.path.join(PROCESSED_DIR, 'fig_tendencia_mensal.png')
        f2.tight_layout()
        f2.savefig(p2)
        plt.close(f2)
        figs.append(p2)
    if HAS_PLOT and df_wide[col_province].notna().any():
        prov_counts = df_wide[df_wide[col_province].notna()].groupby(col_province).size().reset_index(name='total_incidentes')
        f3 = plt.figure(figsize=(10,5))
        sns.barplot(x=col_province, y='total_incidentes', data=prov_counts)
        plt.title('Incidentes por provincia')
        plt.xticks(rotation=45, ha='right')
        p3 = os.path.join(PROCESSED_DIR, 'fig_incidentes_por_provincia.png')
        f3.tight_layout()
        f3.savefig(p3)
        plt.close(f3)
        figs.append(p3)
    dist_types = df_long.groupby('types').size().reset_index(name='contagem')
    if HAS_PLOT and len(dist_types):
        f4 = plt.figure(figsize=(8,4))
        sns.barplot(x='types', y='contagem', data=dist_types)
        plt.title('Distribuicao dos tipos de incidente')
        plt.xticks(rotation=45, ha='right')
        p4 = os.path.join(PROCESSED_DIR, 'fig_distribuicao_tipos.png')
        f4.tight_layout()
        f4.savefig(p4)
        plt.close(f4)
        figs.append(p4)
    if HAS_PLOT and df_long[col_province].notna().any():
        pivot = df_long[df_long[col_province].notna()].pivot_table(index=col_province, columns='types', values='registered_cases', aggfunc='sum', fill_value=0)
        f5 = plt.figure(figsize=(12,6))
        sns.heatmap(pivot, cmap='Reds', linewidths=0.5)
        plt.title('Heatmap por provincia')
        p5 = os.path.join(PROCESSED_DIR, 'fig_heatmap_provincia.png')
        f5.tight_layout()
        f5.savefig(p5)
        plt.close(f5)
        figs.append(p5)
    desc = df_wide['registered_cases'].describe().to_frame(name='registered_cases').reset_index()
    val_errors = []
    if df_wide['registered_cases'].isna().any():
        val_errors.append('registered_cases com NA')
    if (df_wide['registered_cases'] < 0).any():
        val_errors.append('registered_cases com valores negativos')
    if df_wide['start_date'].isna().any():
        pass
    if df_long['types'].isna().any() or (df_long['types'] == '').any():
        val_errors.append('linhas com incident_type vazio')
    report_path = os.path.join(PROCESSED_DIR, 'incidentes_report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('<html><head><meta charset="utf-8"><title>Relatorio de Incidentes</title></head><body>')
        f.write('<h1>Relatorio de Incidentes</h1>')
        if df_wide[col_province].notna().any():
            prov_counts_html = df_wide[df_wide[col_province].notna()].groupby(col_province).size().reset_index(name='total_incidentes').to_html(index=False)
            f.write('<h2>Numero total de incidentes por provincia</h2>')
            f.write(prov_counts_html)
        if df_wide['start_date'].notna().any():
            weekly_html = df_wide[df_wide['start_date'].notna()].groupby(pd.Grouper(key='start_date', freq='W')).size().reset_index(name='total_eventos').to_html(index=False)
            monthly_html = df_wide[df_wide['start_date'].notna()].groupby(pd.Grouper(key='start_date', freq='M')).size().reset_index(name='total_eventos').to_html(index=False)
            f.write('<h2>Tendencia semanal</h2>')
            f.write(weekly_html)
            f.write('<h2>Tendencia mensal</h2>')
            f.write(monthly_html)
        dist_types_html = dist_types.to_html(index=False)
        f.write('<h2>Distribuicao dos tipos de incidente</h2>')
        f.write(dist_types_html)
        f.write('<h2>Analise descritiva dos casos registados</h2>')
        f.write(desc.to_html(index=False))
        if HAS_PLOT:
            for p in figs:
                rel = os.path.relpath(p, PROCESSED_DIR)
                f.write(f'<h3>Figura: {os.path.basename(p)}</h3><img src="{rel}" style="max-width:100%;height:auto;"/>')
        if val_errors:
            f.write('<h2>Validacao</h2><ul>')
            for e in val_errors:
                f.write(f'<li>{e}</li>')
            f.write('</ul>')
        else:
            f.write('<h2>Validacao</h2><p>Sem inconsistencias encontradas.</p>')
        f.write('</body></html>')
    print({'long_out': long_out, 'wide_out': wide_out, 'report': report_path, 'validation_errors': val_errors})

if __name__ == '__main__':
    main()

