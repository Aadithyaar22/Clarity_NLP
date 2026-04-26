from app.schemas import (
    AnnotationRequest,
    PipelineDocument,
    PipelineRequest,
    PipelineResponse,
    PreprocessRequest,
    SentimentRequest,
)
from app.services.annotation import annotate_text
from app.services.preprocessing import _analytics, _frequencies, preprocess_document
from app.services.sentiment import analyze_sentiment


def run_pipeline(payload: PipelineRequest) -> PipelineResponse:
    documents: list[PipelineDocument] = []
    all_tokens: list[str] = []

    for document in payload.documents:
        preprocessing = preprocess_document(PreprocessRequest(text=document, options=payload.options))
        all_tokens.extend(preprocessing.tokens)
        documents.append(
            PipelineDocument(
                preprocessing=preprocessing,
                sentiment=analyze_sentiment(SentimentRequest(text=document)),
                annotations=annotate_text(AnnotationRequest(text=document)),
            )
        )

    return PipelineResponse(
        documents=documents,
        corpus_analytics=_analytics("\n".join(payload.documents), all_tokens),
        top_terms=_frequencies(all_tokens, limit=20),
    )

