from app.schemas import SentimentRequest, SentimentResponse
from app.schemas import PreprocessRequest, PreprocessOptions
from app.services.preprocessing import preprocess_document


POSITIVE_TERMS = {
    "amazing", "best", "brilliant", "clean", "delight", "excellent", "fast",
    "good", "great", "happy", "love", "loved", "powerful", "smooth", "win",
}
NEGATIVE_TERMS = {
    "bad", "broken", "bug", "crash", "crashed", "damaged", "hate", "late",
    "poor", "sad", "slow", "terrible", "worse", "worst", "angry", "issue",
    "failed", "failure", "unhappy",
}
NEGATORS = {"no", "not", "never", "cannot", "cant", "can't", "wont", "won't"}


def analyze_sentiment(payload: SentimentRequest) -> SentimentResponse:
    processed = preprocess_document(
        PreprocessRequest(
            text=payload.text,
            options=PreprocessOptions(remove_stopwords=False, min_token_length=2),
        )
    )
    tokens = processed.tokens
    positive_hits: list[str] = []
    negative_hits: list[str] = []
    score = 0

    for index, token in enumerate(tokens):
        inverted = any(previous in NEGATORS for previous in tokens[max(0, index - 3):index])
        if token in POSITIVE_TERMS:
            if inverted:
                negative_hits.append(f"not {token}")
                score -= 1
            else:
                positive_hits.append(token)
                score += 1
        if token in NEGATIVE_TERMS:
            if inverted:
                positive_hits.append(f"not {token}")
                score += 1
            else:
                negative_hits.append(token)
                score -= 1

    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"

    confidence = min(0.98, 0.5 + abs(score) * 0.16)
    explanation = "Lexicon sentiment with nearby negation handling, inspired by the notebook sentiment pipeline."
    return SentimentResponse(
        label=label,
        score=round(score / max(len(tokens), 1), 3),
        confidence=round(confidence, 2),
        positive_terms=positive_hits,
        negative_terms=negative_hits,
        explanation=explanation,
    )
