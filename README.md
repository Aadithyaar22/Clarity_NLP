# Clarity: Feedback Triage

A production-style ML/NLP project built from the notebook ideas in
[`Aadithyaar22/-NLP-Preprocessing-Engine`](https://github.com/Aadithyaar22/-NLP-Preprocessing-Engine).

## Goal

**Clarity**

Clarity helps teams understand messy customer feedback. Paste reviews, support
tickets, or social comments, and the app cleans the text, detects sentiment,
assigns priority, identifies themes, recommends owners, and exports a triage
report.

## Features

- Advanced NLP preprocessing
- Batch corpus analytics
- Sentiment analysis with negation handling
- Priority and urgency scoring
- Topic/theme detection for real customer issues
- Recommended owner and next action
- Classical ML and DL model-lab comparison surface
- POS/chunk-style token annotation
- Exportable JSON triage report
- FastAPI backend with interactive API docs
- Polished browser frontend

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
