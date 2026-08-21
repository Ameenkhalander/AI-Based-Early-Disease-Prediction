"""confidence.py

WHY THIS FILE EXISTS
    Converts a raw model_score into a human-readable confidence category
    (e.g. low / moderate / high) and decides whether the pipeline should
    keep asking follow-up questions or is ready to present a final result.

INPUT
    list[PredictionResult] (unranked or ranked scores from predictor.py)
    number of questions already asked
    score gap between top-1 and top-2 predictions

OUTPUT
    ConfidenceAssessment:
        category: str
        should_stop_asking: bool
        reason: str

HOW IT CONNECTS
    predictor.py -> THIS FILE -> question_engine.py (stopping condition)
"""

# Implementation added in Phase 7.
