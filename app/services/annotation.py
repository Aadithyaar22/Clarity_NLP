from collections import Counter

from app.schemas import AnnotationRequest, AnnotationResponse, TokenAnnotation
from app.schemas import PreprocessOptions, PreprocessRequest
from app.services.preprocessing import preprocess_document


DETERMINERS = {"a", "an", "the", "this", "that", "these", "those"}
PREPOSITIONS = {"in", "on", "at", "by", "for", "from", "with", "over", "under", "into", "of"}
VERBS = {"am", "are", "be", "is", "was", "were", "run", "runs", "build", "builds", "jumps", "feel", "feels"}


def annotate_text(payload: AnnotationRequest) -> AnnotationResponse:
    processed = preprocess_document(
        PreprocessRequest(
            text=payload.text,
            options=PreprocessOptions(remove_stopwords=False, remove_punctuation=True, min_token_length=1),
        )
    )
    annotations = [_annotate_token(token, index) for index, token in enumerate(processed.tokens)]
    summary = Counter(annotation.pos for annotation in annotations)
    return AnnotationResponse(annotations=annotations, summary=dict(summary))


def _annotate_token(token: str, index: int) -> TokenAnnotation:
    if token in DETERMINERS:
        pos = "DT"
        chunk = "B-NP"
    elif token in PREPOSITIONS:
        pos = "IN"
        chunk = "B-PP"
    elif token in VERBS or token.endswith("ing") or token.endswith("ed"):
        pos = "VB"
        chunk = "B-VP"
    elif token.endswith("ly"):
        pos = "RB"
        chunk = "B-ADVP"
    elif token.endswith(("ous", "ful", "able", "ive", "al")):
        pos = "JJ"
        chunk = "I-NP" if index else "B-NP"
    else:
        pos = "NN"
        chunk = "I-NP" if index else "B-NP"

    return TokenAnnotation(token=token, pos=pos, chunk=chunk)

