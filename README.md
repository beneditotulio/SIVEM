# 🇲🇿 SIVEM – Sistema Inteligente de Vigilância de Eventos e Manifestações

Plataforma de previsão de incidentes sociopolíticos em Moçambique com IA, composta por pipeline de dados, modelo de Machine Learning, API REST e dashboard web.

---

## 📁 Estrutura do Repositório

```
SIVEM/
│
├── data/
│   ├── raw/                 # Dados originais (não modificados)
│   ├── processed/           # Dados limpos e artefactos gerados
│   └── external/            # Fontes externas (ONU, ACLED, INE, etc.)
│
├── notebooks/
│   ├── 01_exploracao.ipynb          # EDA (Exploração dos Dados)
│   ├── 02_preprocessamento.ipynb    # Limpeza, tratamento e engenharia de features
│   ├── 03_treinamento_modelo.ipynb  # Treino e métricas do modelo
│   ├── 04_avaliacao_modelo.ipynb    # Avaliação e matrizes de confusão
│   └── 05_previsoes_futuras.ipynb   # Previsão de incidentes (output final)
│
├── model/
│   ├── sivem_model.pkl           # Modelo treinado (Joblib)
│   └── encoder.pkl               # Codificador das variáveis categóricas
│
├── api/
│   ├── main.py                   # API FastAPI para servir o modelo
│   ├── requirements.txt          # Bibliotecas da API
│   └── utils/                    # Funções auxiliares
│
├── dashboard/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/api.js       # Ligação à API do modelo
│   │   └── App.jsx
│   └── package.json              # React + Vite
│
├── docs/
│   ├── arquitectura_do_sistema.pdf
│   ├── metodologia_datawave.pdf
│   └── apresentacao_evento.pptx
│
├── scripts/
│   ├── preprocess.py             # Limpeza e normalização de dados
│   ├── train.py                  # Treino do modelo (Random Forest)
│   └── predict.py                # Utilitário simples de previsão
│
├── tests/
│   ├── test_api.py
│   ├── test_preprocess.py
│   └── test_model.py
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 📌 Descrição

O SIVEM utiliza dados históricos e contextuais para prever a probabilidade de ocorrência de incidentes durante períodos pós‑eleitorais em Moçambique. O sistema fornece:

- Previsões binárias: `0` (sem incidentes) / `1` (com incidentes)
- Visualizações temporais e por província
- API REST para integração com aplicações externas
- Dashboard web para exploração interativa

Projeto desenvolvido para o DataWave 2025.

---

## 🎯 Objetivo Principal

Responder à pergunta: “Haverá incidentes amanhã?” através de um classificador treinado em dados de eventos, contexto e histórico temporal.

---

## 🧠 Tecnologias

- Backend & IA: `Python`, `Pandas`, `NumPy`, `scikit-learn`, `RandomForest`, `Joblib`, `FastAPI`
- Frontend: `React` + `Vite` (ESM), integração via `fetch`
- Infraestrutura: `GitHub`, opcional `Docker` e `CI/CD`

---

## 🏗️ Arquitetura

```
Coleta → Pré-processamento → Feature Engineering → Treino (Random Forest)
      → API REST (FastAPI) → Dashboard React (gráficos e mapa)
```

---

## 📊 Dataset (exemplos de variáveis)

- `data`/`start_date`
- `province`
- `incident_type`/`types`
- `registered_cases`
- Derivadas: indicadores por tipo, agregações semanais/mensais, lags
- Alvo: `incident_tomorrow` (proposta para evolução)

---

## 🚀 Como Executar

### 1) Clonar

```
git clone https://github.com/SEU_USUARIO/SIVEM.git
cd SIVEM
```

### 2) Pré-processar dados

```
python scripts/preprocess.py
```

Gera CSVs e figuras em `data/processed/`.

### 3) Treinar modelo

```
python scripts/train.py
```

Salva o modelo em `model/sivem_model.pkl`.

### 4) API (FastAPI)

```
pip install -r api/requirements.txt
uvicorn api.main:app --reload
```

Endpoints:

- `GET /health`
- `POST /predict` body: `{ "features": [f1, f2, ...] }`

### 5) Dashboard (React + Vite)

```
cd dashboard
npm install
npm run dev
```

O serviço comunica com a API em `http://localhost:8000` (configurado em `dashboard/src/services/api.js`).

---

## 🧪 Testes

- Testes básicos em `tests/` (API e módulos). Podem ser executados com `pytest` após instalação das dependências necessárias.

---

## 🧷 Roadmap

- LSTM/Temporal para previsão sequencial
- Integração de dados meteorológicos e socioeconómicos
- Autenticação JWT na API pública
- Deploy em Render/Heroku/Azure
- Automatizar ingestão com scraping e gateways (SMS/USSD)

---

## 👤 Autores

- Túlio Benedito Nhantumbo — AI Engineer / Full Stack Developer
- Contribuidores DataWave 2025

---

## 📄 Licença

MIT License — livre para uso, estudo e modificação.