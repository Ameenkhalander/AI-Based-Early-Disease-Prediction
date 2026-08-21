"""emergency_detector.py

WHY THIS FILE EXISTS
    Runs BEFORE any disease prediction. Checks the canonical symptom
    vector (and, ideally, raw text as a second pass) against a curated
    list of red-flag emergency patterns (e.g. chest pain radiating to
    arm/jaw, sudden one-sided weakness, severe breathing difficulty,
    coughing/vomiting blood, loss of consciousness).

INPUT
    CanonicalSymptomVector
    raw_text: str

OUTPUT
    EmergencyResult:
        is_emergency: bool
        matched_patterns: list[str]
        message: str  # e.g. "Potential emergency warning detected..."

HOW IT CONNECTS
    symptom_normalizer.py -> THIS FILE
    If is_emergency is True, the pipeline STOPS here. predictor.py and
    question_engine.py are never called. The API route returns the
    emergency message directly, and the frontend must render it as a
    hard, unmissable warning banner -- never quietly alongside a disease
    prediction.

DESIGN NOTE
    This is intentionally rule-based, not model-based. A missed
    emergency is much worse than a false positive here, so we want a
    reviewable, explicit list of trigger patterns rather than a model
    whose failure modes are harder to audit.
"""

# Implementation added in Phase 9.
