from pydantic import BaseModel, Field


class PreprocessOptions(BaseModel):
    lowercase: bool = True
    remove_urls: bool = True
    remove_emails: bool = True
    remove_numbers: bool = True
    normalize_repeats: bool = True
    remove_punctuation: bool = True
    remove_stopwords: bool = False
    preserve_negations: bool = True
    min_token_length: int = Field(default=2, ge=1, le=12)


class PreprocessRequest(BaseModel):
    text: str = Field(..., max_length=50_000)
    options: PreprocessOptions = Field(default_factory=PreprocessOptions)


class TokenMetric(BaseModel):
    token: str
    count: int


class TextAnalytics(BaseModel):
    characters: int
    tokens: int
    unique_tokens: int
    lexical_diversity: float
    average_token_length: float
    noise_score: float


class PreprocessResponse(BaseModel):
    original_text: str
    cleaned_text: str
    tokens: list[str]
    analytics: TextAnalytics
    frequencies: list[TokenMetric]
    warnings: list[str]


class BatchPreprocessRequest(BaseModel):
    documents: list[str] = Field(..., min_length=1, max_length=100)
    options: PreprocessOptions = Field(default_factory=PreprocessOptions)


class BatchPreprocessResponse(BaseModel):
    documents: list[PreprocessResponse]
    corpus_analytics: TextAnalytics
    top_terms: list[TokenMetric]


class SentimentRequest(BaseModel):
    text: str = Field(..., max_length=20_000)


class SentimentResponse(BaseModel):
    label: str
    score: float
    confidence: float
    positive_terms: list[str]
    negative_terms: list[str]
    explanation: str


class AnnotationRequest(BaseModel):
    text: str = Field(..., max_length=10_000)


class TokenAnnotation(BaseModel):
    token: str
    pos: str
    chunk: str


class AnnotationResponse(BaseModel):
    annotations: list[TokenAnnotation]
    summary: dict[str, int]


class PipelineRequest(BaseModel):
    documents: list[str] = Field(..., min_length=1, max_length=25)
    options: PreprocessOptions = Field(default_factory=PreprocessOptions)


class PipelineDocument(BaseModel):
    preprocessing: PreprocessResponse
    sentiment: SentimentResponse
    annotations: AnnotationResponse


class PipelineResponse(BaseModel):
    documents: list[PipelineDocument]
    corpus_analytics: TextAnalytics
    top_terms: list[TokenMetric]

