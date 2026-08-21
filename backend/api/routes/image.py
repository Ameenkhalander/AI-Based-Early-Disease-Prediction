"""image.py -- POST /api/image-analysis

WHY: entry point for the skin-image module. Routes to one of two
distinct models based on the "analysis_type" the user selects in the UI
(general skin condition vs. pigmented lesion screening) -- these are
never merged into one label space (see docs/DATASETS.md for why).
INPUT: multipart image file + analysis_type: "general" | "lesion".
OUTPUT: ImagePredictionResponse -- label, confidence, Grad-CAM overlay
        image, safety disclaimer text, "consult a dermatologist" guidance.
CALLS: services.image_service.classify()
"""

# Implementation added in Phase 16.
