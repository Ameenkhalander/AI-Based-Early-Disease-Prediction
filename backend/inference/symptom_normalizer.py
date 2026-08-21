"""symptom_normalizer.py

WHY THIS FILE EXISTS
    Maps free-text/synonym symptom mentions ("throwing up", "vomiting",
    "puking") onto the single canonical symptom vocabulary used by the
    structured prediction model (the ~40-80 disease Candidate-A feature
    columns). Without this step the extractor's vocabulary and the
    predictor's training vocabulary would never line up.

INPUT
    list[SymptomMention] (affirmed + negated, from negation_detector.py)
    previous canonical vector (if this is a follow-up-question turn)

OUTPUT
    CanonicalSymptomVector:
        positive: set[str]   # canonical symptom ids present
        negative: set[str]   # canonical symptom ids explicitly denied
        unknown:  set[str]   # canonical symptoms never asked about

HOW IT CONNECTS
    negation_detector.py -> THIS FILE -> emergency_detector.py -> predictor.py
    question_engine.py also writes back into this vector as the user
    answers follow-up questions.
"""

# Implementation added in Phase 7.
