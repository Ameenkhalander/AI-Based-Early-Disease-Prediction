"""image_service.py

WHY: wraps both trained image models (artifacts/image_model_general and
     artifacts/image_model_lesion) plus Grad-CAM explanation generation
     behind one interface.
INPUT: image bytes + analysis_type.
OUTPUT: ImageClassificationResult(label, confidence, gradcam_overlay_png,
        low_confidence_flag: bool).
DESIGN NOTE: if confidence is below a documented threshold, returns
        low_confidence_flag=True instead of forcing a guess -- per the
        image-safety requirement ("insufficient for reliable assessment").
"""

# Implementation added in Phase 16.
