"""settings.py

WHY: centralizes all environment-driven configuration (DB URL, model
     artifact paths, whisper model size, CORS origins, etc.) using
     pydantic-settings, reading from .env. Nothing else in the codebase
     should call os.environ directly -- import settings from here instead.
"""

# Implementation added in Phase 16.
