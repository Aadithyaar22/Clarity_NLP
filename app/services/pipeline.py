from app.schemas import (
    AnnotationRequest,
    PipelineDocument,
    PipelineRequest,
    PipelineResponse,
    PreprocessRequest,
    SentimentRequest,
)
from app.services.annotation import annotate_text
from app.services.intelligence import build_corpus_insight, build_document_triage
from app.services.preprocessing import _analytics, _frequencies, preprocess_document
from app.services.sentiment import analyze_sentiment


def run_pipeline(payload: PipelineRequest) -> PipelineResponse:
    documents: list[PipelineDocument] = []
    triage_insights = []
    sentiments = []
    all_tokens: list[str] = []

    for document in payload.documents:
        preprocessing = preprocess_document(PreprocessRequest(text=document, options=payload.options))
        sentiment = analyze_sentiment(SentimentRequest(text=document))
        annotations = annotate_text(AnnotationRequest(text=document))
        triage = build_document_triage(preprocessing, sentiment)

        all_tokens.extend(preprocessing.tokens)
        sentiments.append(sentiment)
        triage_insights.append(triage)
        documents.append(
            PipelineDocument(
                preprocessing=preprocessing,
                sentiment=sentiment,
                annotations=annotations,
                triage=triage,
            )
        )

    return PipelineResponse(
        documents=documents,
        corpus_analytics=_analytics("\n".join(payload.documents), all_tokens),
        top_terms=_frequencies(all_tokens, limit=20),
        corpus_insight=build_corpus_insight(triage_insights, sentiments),
    )
