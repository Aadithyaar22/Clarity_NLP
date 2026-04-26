from collections import Counter
import re
import string

from app.schemas import (
    BatchPreprocessRequest,
    BatchPreprocessResponse,
    PreprocessRequest,
    PreprocessResponse,
    TextAnalytics,
    TokenMetric,
)


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "that", "the", "this", "to",
    "was", "were", "will", "with", "you", "your", "i", "am", "we", "they",
}
NEGATIONS = {"no", "not", "never", "none", "cannot", "can't", "won't", "n't"}
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
REPEATED_PATTERN = re.compile(r"(.)\1{2,}")


def preprocess_document(payload: PreprocessRequest) -> PreprocessResponse:
    text = payload.text or ""
    options = payload.options
    warnings: list[str] = []
    working = text.strip()

    if not working:
        warnings.append("Input was empty after trimming whitespace.")

    if options.lowercase:
        working = working.lower()
    if options.remove_urls:
        working = URL_PATTERN.sub(" ", working)
    if options.remove_emails:
        working = EMAIL_PATTERN.sub(" ", working)
    if options.remove_numbers:
        working = re.sub(r"\d+", " ", working)
    if options.normalize_repeats:
        working = REPEATED_PATTERN.sub(r"\1\1", working)
    if options.remove_punctuation:
        working = working.translate(str.maketrans({mark: " " for mark in string.punctuation}))

    raw_tokens = [token for token in working.split() if token]
    tokens: list[str] = []
    for token in raw_tokens:
        if len(token) < options.min_token_length and token not in NEGATIONS:
            continue
        if options.remove_stopwords and token in STOPWORDS:
            if options.preserve_negations and token in NEGATIONS:
                tokens.append(token)
            continue
        tokens.append(token)

    if text and not tokens:
        warnings.append("No semantic tokens remained after preprocessing.")

    cleaned_text = " ".join(tokens)
    return PreprocessResponse(
        original_text=text,
        cleaned_text=cleaned_text,
        tokens=tokens,
        analytics=_analytics(text, tokens),
        frequencies=_frequencies(tokens),
        warnings=warnings,
    )


def preprocess_batch(payload: BatchPreprocessRequest) -> BatchPreprocessResponse:
    documents = [
        preprocess_document(PreprocessRequest(text=document, options=payload.options))
        for document in payload.documents
    ]
    all_tokens = [token for document in documents for token in document.tokens]
    original_text = "\n".join(payload.documents)

    return BatchPreprocessResponse(
        documents=documents,
        corpus_analytics=_analytics(original_text, all_tokens),
        top_terms=_frequencies(all_tokens, limit=20),
    )


def _frequencies(tokens: list[str], limit: int = 10) -> list[TokenMetric]:
    return [TokenMetric(token=token, count=count) for token, count in Counter(tokens).most_common(limit)]


def _analytics(original_text: str, tokens: list[str]) -> TextAnalytics:
    token_count = len(tokens)
    unique_count = len(set(tokens))
    average_length = sum(len(token) for token in tokens) / token_count if token_count else 0
    noisy_chars = len(re.findall(r"[^A-Za-z\s]", original_text))
    noise_score = noisy_chars / max(len(original_text), 1)

    return TextAnalytics(
        characters=len(original_text),
        tokens=token_count,
        unique_tokens=unique_count,
        lexical_diversity=round(unique_count / token_count, 3) if token_count else 0,
        average_token_length=round(average_length, 2),
        noise_score=round(noise_score, 3),
    )

