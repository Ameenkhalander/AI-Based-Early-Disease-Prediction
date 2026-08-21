"""assessment.py -- POST /api/assessment

WHY: entry point for text-based symptom assessment.
INPUT: AssessmentRequest (schemas/assessment.py) -- raw_text, session_id,
       and (on follow-up turns) previous CanonicalSymptomVector + answer.
OUTPUT: AssessmentResponse -- either an EmergencyResult, a NextQuestion,
        or a final ranked list of PredictionResult + ExplanationResult.
CALLS: inference.symptom_extractor -> negation_detector -> symptom_normalizer
       -> emergency_detector -> predictor -> question_engine -> explainability
       services.storage_service (persist session state to the database)
"""

# Implementation added in Phase 16.
