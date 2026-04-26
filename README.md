# NLP Preprocessing Engine

A production-style full-stack NLP workbench built from the notebook ideas in
[`Aadithyaar22/-NLP-Preprocessing-Engine`](https://github.com/Aadithyaar22/-NLP-Preprocessing-Engine).

It turns the original assignment notebooks into a usable API and frontend for:

- Advanced text preprocessing
- Batch corpus analytics
- Token frequency and quality signals
- Sentiment classification
- Lightweight token annotation
- A polished browser dashboard served by FastAPI

## Run Locally

```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

Open <http://127.0.0.1:8000>.

## Test

```bash
python3 -m pytest
```

## API

FastAPI docs are available at <http://127.0.0.1:8000/docs>.

Important endpoints:

- `GET /health`
- `POST /api/v1/preprocess`
- `POST /api/v1/batch`
- `POST /api/v1/sentiment`
- `POST /api/v1/annotate`
- `POST /api/v1/pipeline`

