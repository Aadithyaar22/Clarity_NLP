from fastapi import APIRouter

from app.services.annotation import annotate_text
from app.services.pipeline import run_pipeline
from app.services.preprocessing import preprocess_batch, preprocess_document
from app.services.sentiment import analyze_sentiment
from app.schemas import (
    AnnotationRequest,
    AnnotationResponse,
    BatchPreprocessRequest,
    BatchPreprocessResponse,
    PipelineRequest,
    PipelineResponse,
    PreprocessRequest,
    PreprocessResponse,
    SentimentRequest,
    SentimentResponse,
)


router = APIRouter(tags=["nlp"])


@router.post("/preprocess", response_model=PreprocessResponse)
def preprocess(payload: PreprocessRequest) -> PreprocessResponse:
    return preprocess_document(payload)


@router.post("/batch", response_model=BatchPreprocessResponse)
def batch(payload: BatchPreprocessRequest) -> BatchPreprocessResponse:
    return preprocess_batch(payload)


@router.post("/sentiment", response_model=SentimentResponse)
def sentiment(payload: SentimentRequest) -> SentimentResponse:
    return analyze_sentiment(payload)


@router.post("/annotate", response_model=AnnotationResponse)
def annotate(payload: AnnotationRequest) -> AnnotationResponse:
    return annotate_text(payload)


@router.post("/pipeline", response_model=PipelineResponse)
def pipeline(payload: PipelineRequest) -> PipelineResponse:
    return run_pipeline(payload)

