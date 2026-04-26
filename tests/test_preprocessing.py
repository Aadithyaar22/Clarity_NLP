from app.schemas import PreprocessRequest
from app.services.preprocessing import preprocess_document
from app.services.sentiment import analyze_sentiment
from app.schemas import SentimentRequest


def test_preprocess_removes_noise_and_preserves_negation():
    result = preprocess_document(PreprocessRequest(text="I am not happy!!! Visit https://openai.com 123"))

    assert result.cleaned_text == "am not happy visit"
    assert "not" in result.tokens
    assert result.analytics.tokens == 4


def test_sentiment_handles_negation():
    result = analyze_sentiment(SentimentRequest(text="I am not happy with this bad service"))

    assert result.label == "negative"
    assert "not happy" in result.negative_terms

