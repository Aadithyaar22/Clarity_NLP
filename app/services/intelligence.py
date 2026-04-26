from collections import Counter

from app.schemas import (
    ActionRecommendation,
    CorpusInsight,
    ModelSignal,
    PreprocessResponse,
    SentimentResponse,
    TopicSignal,
    TriageInsight,
)


TOPICS = {
    "Delivery": {"delivery", "late", "arrived", "shipping", "tracking", "package", "packaging", "order"},
    "Support": {"support", "agent", "reply", "replied", "helpful", "wait", "nobody", "explained"},
    "Payment": {"payment", "checkout", "refund", "promo", "code", "price", "paid", "card"},
    "Reliability": {"app", "crashed", "crash", "broken", "bug", "slow", "fast", "response"},
    "Product Quality": {"quality", "damaged", "excellent", "amazing", "clean", "product"},
    "Returns": {"return", "returns", "refund", "exchange", "replace"},
}

ACTION_BY_TOPIC = {
    "Delivery": ("Audit fulfillment SLA", "Operations", "Shipping and tracking language is appearing in this note."),
    "Support": ("Review support backlog", "Customer Support", "The note mentions response quality or waiting time."),
    "Payment": ("Inspect checkout/refund flow", "Payments", "Payment, refund, or promo-code language is present."),
    "Reliability": ("Create engineering incident", "Engineering", "The note points to crashes, slowness, or broken behavior."),
    "Product Quality": ("Open quality review", "Product", "The note contains product-quality language."),
    "Returns": ("Review returns policy friction", "CX Operations", "Returns or refund terms are prominent."),
    "General": ("Route to customer experience review", "CX Lead", "No dominant operational topic was detected."),
}

URGENT_TERMS = {"crashed", "crash", "broken", "failed", "damaged", "late", "never", "worst", "terrible", "refund"}


def build_document_triage(
    preprocessing: PreprocessResponse,
    sentiment: SentimentResponse,
) -> TriageInsight:
    tokens = preprocessing.tokens
    topic = detect_topic(tokens)
    urgency_score = calculate_urgency(tokens, sentiment, preprocessing.analytics.noise_score)
    priority = priority_from_score(urgency_score)
    action, owner, reason = ACTION_BY_TOPIC.get(topic.name, ACTION_BY_TOPIC["General"])

    return TriageInsight(
        priority=priority,
        urgency_score=urgency_score,
        topic=topic,
        recommendation=ActionRecommendation(action=action, owner=owner, reason=reason),
        model_signals=model_signals(tokens, sentiment, urgency_score),
    )


def build_corpus_insight(document_insights: list[TriageInsight], sentiments: list[SentimentResponse]) -> CorpusInsight:
    topic_counts = Counter(insight.topic.name for insight in document_insights)
    dominant_topic = topic_counts.most_common(1)[0][0] if topic_counts else "General"
    negative_share = (
        sum(1 for sentiment in sentiments if sentiment.label == "negative") / len(sentiments)
        if sentiments
        else 0
    )
    highest_urgency = max((insight.urgency_score for insight in document_insights), default=0)

    if highest_urgency >= 0.75 or negative_share >= 0.5:
        risk_level = "High"
        next_step = "Start with high-priority notes, then assign owners by dominant topic."
    elif highest_urgency >= 0.45:
        risk_level = "Medium"
        next_step = "Review recurring topics and confirm whether they map to known incidents."
    else:
        risk_level = "Low"
        next_step = "Monitor trend volume and collect more feedback before escalation."

    total = max(sum(topic_counts.values()), 1)
    distribution = [
        TopicSignal(name=name, score=round(count / total, 3), evidence=[])
        for name, count in topic_counts.most_common()
    ]

    return CorpusInsight(
        dominant_topic=dominant_topic,
        risk_level=risk_level,
        negative_share=round(negative_share, 3),
        recommended_next_step=next_step,
        topic_distribution=distribution,
    )


def detect_topic(tokens: list[str]) -> TopicSignal:
    token_set = set(tokens)
    best_name = "General"
    best_evidence: list[str] = []

    for name, vocabulary in TOPICS.items():
        evidence = sorted(token_set & vocabulary)
        if len(evidence) > len(best_evidence):
            best_name = name
            best_evidence = evidence

    score = min(1.0, len(best_evidence) / 3) if best_evidence else 0
    return TopicSignal(name=best_name, score=round(score, 3), evidence=best_evidence[:5])


def calculate_urgency(tokens: list[str], sentiment: SentimentResponse, noise_score: float) -> float:
    urgent_hits = len(set(tokens) & URGENT_TERMS)
    sentiment_weight = {"negative": 0.42, "neutral": 0.16, "positive": 0.04}[sentiment.label]
    urgency = sentiment_weight + min(0.38, urgent_hits * 0.13) + min(0.2, noise_score * 0.8)
    return round(min(1.0, urgency), 3)


def priority_from_score(score: float) -> str:
    if score >= 0.75:
        return "P0"
    if score >= 0.55:
        return "P1"
    if score >= 0.32:
        return "P2"
    return "P3"


def model_signals(tokens: list[str], sentiment: SentimentResponse, urgency_score: float) -> list[ModelSignal]:
    tfidf_prediction = "escalate" if urgency_score >= 0.55 else "monitor"
    transformer_prediction = sentiment.label if tokens else "empty"
    return [
        ModelSignal(
            model="Lexicon Sentiment",
            prediction=sentiment.label,
            confidence=sentiment.confidence,
            role="Fast interpretable baseline",
        ),
        ModelSignal(
            model="TF-IDF Linear Proxy",
            prediction=tfidf_prediction,
            confidence=round(0.58 + min(0.34, urgency_score * 0.34), 2),
            role="Classical ML triage baseline",
        ),
        ModelSignal(
            model="Transformer Readiness",
            prediction=transformer_prediction,
            confidence=round(0.62 + min(0.28, len(tokens) / 80), 2),
            role="DL deployment placeholder for BERT/DistilBERT",
        ),
    ]

