"""question_engine.py

WHY THIS FILE EXISTS
    Implements the "doctor-style" follow-up question logic. Given the
    current differential (predictor.py's ranked output) and the current
    CanonicalSymptomVector, decides the single highest-value question to
    ask next -- or decides no more questions are needed.

INPUT
    CanonicalSymptomVector
    list[PredictionResult]
    list[str] of already-asked question ids (repetition guard)

OUTPUT
    NextQuestion | None:
        question_text: str
        target_symptom: str
        score_breakdown: dict  # for debugging/explainability

HOW IT CONNECTS
    predictor.py + confidence.py -> THIS FILE
    If a question is returned, the API returns it to the frontend chat
    UI; the user's answer flows back into symptom_normalizer.py, which
    re-triggers predictor.py -- this is the loop shown in the
    architecture diagram (F -> G -> I -> J -> K -> F).

DESIGN NOTE -- the scoring function
    question_score = diagnostic_discrimination
                    + emergency_priority
                    + symptom_relevance
                    + unanswered_information_bonus
                    - repetition_penalty

    diagnostic_discrimination is approximated with an information-gain-
    style calculation: for each unknown canonical symptom, how much does
    knowing its value (present/absent) reduce entropy over the current
    top-N differential, using each disease's symptom-association strengths
    from the training data. This is intentionally simple and explainable
    rather than a learned policy -- it must be auditable so we can say
    "the model asked about X because X best separates Dengue from
    Malaria right now," which is the entire point of this component.
"""

# Implementation added in Phase 8.
