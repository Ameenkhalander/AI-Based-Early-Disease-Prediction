"""explainability.py

WHY THIS FILE EXISTS
    Produces a "why did the model consider this condition" explanation
    from the ACTUAL trained model, not hard-coded text.

INPUT
    trained model artifact + CanonicalSymptomVector + PredictionResult

OUTPUT
    ExplanationResult:
        top_contributing_symptoms: list[(symptom, shap_value)]
        summary_text: str

HOW IT CONNECTS
    predictor.py -> THIS FILE -> returned to the API response and used
    in report_service.py for the PDF report.
    For the image models, the equivalent concept (Grad-CAM heatmap) lives
    in services/image_service.py instead, since it operates on pixels,
    not a feature vector -- but the API-facing shape of the explanation
    is kept consistent between text and image results.

DESIGN NOTE
    Uses SHAP's TreeExplainer, which is fast and exact for tree-based
    models like XGBoost. This is why XGBoost was preferred over an MLP
    for the structured predictor when the accuracy difference was
    marginal -- native SHAP support is a real, honest deployment
    advantage, not just an implementation convenience.
"""

# Implementation added in Phase 10.
