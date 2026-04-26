# Clarity: Feedback Triage

> **Turn messy customer feedback into clear, actionable signals.**
>
> Clarity is a FastAPI-powered NLP workbench that cleans raw text, analyzes sentiment, annotates language patterns, detects the most relevant topic, and produces a triage-style recommendation for each document.

---

## What this project does

Clarity is built for teams that receive large amounts of unstructured text such as:

- customer reviews
- support tickets
- social media comments
- product feedback
- internal issue reports

Instead of reading every message manually, the app helps you quickly understand:

- what the message says after cleaning noisy text
- whether the message is positive, negative, or neutral
- which topic it belongs to, such as delivery, support, payment, or reliability
- how urgent the message may be
- which team should handle it next
- what the important repeated terms are across a batch of documents

The project includes both a **browser interface** and a **REST API**, so it can be used by humans directly or integrated into other systems.

---

## Highlights

- Clean FastAPI backend with versioned API routes
- Rule-based NLP preprocessing with configurable options
- Lexicon-based sentiment analysis with negation handling
- Token annotation for simple POS and chunk labeling
- Topic detection and urgency scoring for triage workflows
- Corpus-level analytics for multi-document analysis
- Exportable JSON report from the frontend
- Modern, polished single-page UI served by the backend
- Test coverage for preprocessing and API behavior

---

## Project flow

The project is designed as a clear pipeline.

### 1) User enters text
The user pastes one or more feedback messages into the frontend. Each line is treated as a separate document.

### 2) Frontend sends the payload
The browser collects the text, applies the selected preprocessing options, and sends the documents to the backend pipeline endpoint.

### 3) Backend preprocesses the documents
The preprocessing service:

- trims whitespace
- optionally converts text to lowercase
- removes URLs, emails, and numbers
- normalizes repeated characters
- removes punctuation
- filters stopwords if enabled
- preserves negations such as `not` and `never`
- returns cleaned tokens and text analytics

### 4) Sentiment is computed
The sentiment service uses a lexicon-based approach:

- positive and negative keyword lists are checked against the tokens
- nearby negation is handled so phrases like `not happy` are treated correctly
- the service returns a sentiment label, score, confidence, and an explanation

### 5) Tokens are annotated
The annotation service produces a lightweight linguistic map of the text:

- determiners
- prepositions
- verbs
- adverbs
- adjectives
- nouns

These annotations are helpful for inspection and demo purposes.

### 6) Triage intelligence is created
The intelligence layer combines preprocessing and sentiment to:

- detect the dominant topic
- estimate urgency
- assign a priority from `P0` to `P3`
- recommend an action and owner
- generate additional model-like signals for comparison

### 7) Corpus insights are built
When multiple documents are submitted, the backend also generates corpus-level insights:

- dominant topic across the batch
- risk level
- negative share
- next recommended step
- topic distribution
- top repeated terms

### 8) Frontend renders the results
The browser shows:

- document-by-document triage cards
- overall corpus metrics
- risk summary
- model lab comparison
- token annotation view
- export option for the final report

---

## Architecture

```text
Browser UI
   │
   ├── captures feedback text + preprocessing settings
   │
   ▼
FastAPI app
   │
   ├── /health
   ├── /api/v1/preprocess
   ├── /api/v1/batch
   ├── /api/v1/sentiment
   ├── /api/v1/annotate
   └── /api/v1/pipeline
   │
   ▼
Service layer
   ├── preprocessing.py   → cleaning, tokenization, analytics
   ├── sentiment.py       → sentiment label and confidence
   ├── annotation.py      → POS/chunk-style tagging
   ├── intelligence.py    → topic, urgency, triage, corpus insights
   └── pipeline.py        → orchestrates the full flow
   │
   ▼
Response models
   └── Pydantic schemas in schemas.py
```

This separation keeps the code easy to maintain:

- **schemas** define the contract
- **services** contain the logic
- **routes** expose the API
- **main** wires the app together
- **static** hosts the frontend assets

---

## Folder structure

```text
Clarity_NLP/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── preprocessing.py
│   │   ├── sentiment.py
│   │   ├── annotation.py
│   │   ├── intelligence.py
│   │   └── pipeline.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── tests/
│   ├── test_api.py
│   └── test_preprocessing.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### What each part does

**`app/main.py`**
- creates the FastAPI application
- configures CORS
- mounts static assets
- serves the main frontend at `/`
- exposes a `/health` endpoint

**`app/core/config.py`**
- stores application settings such as app name, version, and API prefix
- uses cached settings for efficiency

**`app/schemas.py`**
- defines all request and response models
- keeps the API consistent and self-documenting

**`app/api/routes.py`**
- connects HTTP endpoints to service functions
- keeps route definitions clean and minimal

**`app/services/preprocessing.py`**
- handles text cleaning, tokenization, stopword logic, negation preservation, and text analytics

**`app/services/sentiment.py`**
- performs lexicon-based sentiment scoring
- detects positivity and negativity with contextual negation support

**`app/services/annotation.py`**
- assigns lightweight POS and chunk labels to tokens
- useful for explanation and debugging

**`app/services/intelligence.py`**
- detects topics using keyword overlap
- computes urgency and priority
- recommends owners and next actions
- generates batch-level insights

**`app/services/pipeline.py`**
- runs the full document pipeline in one request
- combines preprocessing, sentiment, annotation, and triage into a unified response

**`app/static/index.html`**
- provides the single-page UI for feedback analysis

**`app/static/styles.css`**
- styles the interface with a clean, polished layout

**`app/static/app.js`**
- handles API calls, result rendering, export, and user interactions

**`tests/`**
- verifies API endpoints and preprocessing behavior

---

## How the pipeline works internally

### Preprocessing
The preprocessing layer is designed to clean noisy real-world text without destroying meaning.

It supports toggles for:

- lowercase conversion
- URL removal
- email removal
- number removal
- repeated-character normalization
- punctuation removal
- stopword removal
- negation preservation
- minimum token length filtering

It also returns useful analytics such as:

- character count
- token count
- unique token count
- lexical diversity
- average token length
- noise score

### Sentiment analysis
Sentiment is intentionally transparent and explainable.

The service uses a curated vocabulary of positive and negative terms. It also looks at nearby tokens to catch negation patterns such as:

- `not happy`
- `never good`
- `won't work`

This makes the results easier to interpret than a black-box score.

### Annotation
The annotation module simulates a simple linguistic tagging layer. It is not a full NLP parser, but it provides readable token labels so users can inspect the text structure.

### Intelligence layer
This is where the feedback becomes operational.

The service combines signals from preprocessing and sentiment to decide:

- what the main topic is
- how urgent the message feels
- whether the case should be escalated
- which team should handle it

It also creates a triage priority:

- `P0` — very urgent
- `P1` — high priority
- `P2` — medium priority
- `P3` — low priority

### Corpus insight
When multiple documents are submitted, the engine aggregates the batch and identifies the dominant pattern across the full dataset.

---

## API endpoints

### `GET /health`
Returns basic service status.

**Example response**
```json
{
  "status": "ok",
  "service": "NLP Preprocessing Engine",
  "version": "1.0.0"
}
```

### `POST /api/v1/preprocess`
Cleans and tokenizes a single document.

### `POST /api/v1/batch`
Processes multiple documents and returns corpus-wide preprocessing results.

### `POST /api/v1/sentiment`
Runs sentiment analysis on a single text input.

### `POST /api/v1/annotate`
Returns token-level annotation data.

### `POST /api/v1/pipeline`
Runs the full end-to-end workflow.

---

## Example pipeline request

```json
{
  "documents": [
    "Delivery was late and support never replied.",
    "I loved the clean checkout flow.",
    "The app crashed twice after payment."
  ],
  "options": {
    "lowercase": true,
    "remove_urls": true,
    "remove_emails": true,
    "remove_numbers": true,
    "normalize_repeats": true,
    "remove_punctuation": true,
    "remove_stopwords": false,
    "preserve_negations": true,
    "min_token_length": 2
  }
}
```

The response includes per-document preprocessing, sentiment, annotations, triage, and a corpus insight summary.

---

## Frontend experience

The UI is designed as a guided analysis workspace.

### Intake panel
Paste one note per line and adjust preprocessing settings as needed.

### Signal queue
Shows each cleaned document, sentiment label, priority, topic, owner, and recommended action.

### Insights panel
Displays:

- token counts
- unique terms
- lexical diversity
- noise score
- risk level
- top repeated terms

### Model lab
Compares multiple interpretable signals, including a lexicon baseline, a TF-IDF-style proxy, and a transformer-readiness placeholder.

### Language map
Shows token-level annotation for the first document in the batch.

### Export
The analysis output can be exported as a JSON report for later review.

---

## Getting started

### Requirements
- Python 3.11 or later

### Install dependencies
```bash
pip install -e .
```

### Run the app
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

### Open in browser
- App: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

### Run tests
```bash
python3 -m pytest
```

---

## Why this structure is effective

This project is arranged so that each layer has one responsibility.

- The frontend handles interaction and display.
- The API layer handles HTTP routing.
- The service layer performs NLP logic.
- The schema layer defines the contract.
- The tests verify critical behavior.

That makes the project easier to:

- understand
- extend
- debug
- test
- present in a portfolio or interview

---

## Extending the project

This codebase is a strong base for future improvements such as:

- adding a trained ML classifier
- replacing the rule-based sentiment logic with a transformer model
- using spaCy or NLTK for deeper linguistic analysis
- storing analysis history in a database
- adding user authentication
- building charts for sentiment trends over time
- supporting CSV or file uploads
- adding multi-language support

---

## Notes for contributors

- Keep request and response models inside `schemas.py`
- Put NLP logic inside `services/`
- Add new routes only through `app/api/routes.py`
- Update tests whenever behavior changes
- Keep the frontend readable and lightweight

---

## License

Add the license that matches your intended distribution before publishing the repository publicly.

---

## Closing note

Clarity is intentionally built to feel practical, explainable, and demo-ready. It does not just classify text; it turns feedback into a structured workflow that helps teams decide what to do next.
