# SIVEM

Estrutura do projecto para processamento, modelagem, API e dashboard.

## Pastas

- `data/raw`: dados originais
- `data/processed`: dados limpos e artefactos
- `data/external`: fontes externas
- `notebooks`: EDA, pré-processamento, treino, avaliação e previsões
- `model`: artefactos do modelo
- `api`: serviço FastAPI
- `dashboard`: aplicação React
- `scripts`: utilitários de linha de comando
- `tests`: testes

## API

- Iniciar: `uvicorn api.main:app --reload`