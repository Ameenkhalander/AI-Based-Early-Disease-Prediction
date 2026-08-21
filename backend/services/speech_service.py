"""speech_service.py

WHY: wraps faster-whisper so the rest of the app never imports it
     directly -- if we ever swap runtimes (e.g. to whisper.cpp for a
     CPU-only deployment, per docs/DEPLOYMENT.md), only this file changes.
INPUT: audio bytes (wav/mp3/webm).
OUTPUT: TranscriptResult(text: str, language: str, duration_s: float).
LOADS: artifacts/speech/metadata.json (model size/version used).
"""

# Implementation added in Phase 11.
