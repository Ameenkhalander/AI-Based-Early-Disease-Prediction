"""predictor.py

WHY THIS FILE EXISTS
    Loads the trained structured model (XGBoost, per Phase 4-6 decision)
    from artifacts/text_model/ and turns a CanonicalSymptomVector into
    ranked disease predictions.

INPUT
    CanonicalSymptomVector (positive/negative/unknown canonical symptoms)

OUTPUT
    list[PredictionResult], ranked, each with:
        disease: str
        model_score: float   # NOT called "probability" unless calibrated
        confidence_category: str  # low/moderate/high, from confidence.py

HOW IT CONNECTS
    emergency_detector.py (only reached if NOT an emergency) -> THIS FILE
    -> question_engine.py (to decide if more info is needed)
    -> explainability.py (to generate SHAP explanation for the result)

DESIGN NOTE
    This file only loads and calls the artifact -- it never trains.
    Training lives in ml/text/train_baseline.py and train_deep_learning.py.
    This keeps the backend fast to deploy and free of heavy training
    dependencies.
"""

# Implementation added in Phase 7 (loads artifact selected in Phase 6).
