"""voice.py -- POST /api/voice

WHY: entry point for voice-based symptom assessment. Converts audio to
text with faster-whisper, then hands off to EXACTLY the same inference
pipeline as assessment.py -- there is no separate voice prediction logic.
INPUT: multipart audio file + session_id.
OUTPUT: same AssessmentResponse shape as assessment.py, plus the raw
        transcript so the frontend can show the user what was heard.
CALLS: services.speech_service.transcribe() -> api.routes.assessment's
       underlying pipeline (shared inference call, not duplicated code).
"""

# Implementation added in Phase 11.
