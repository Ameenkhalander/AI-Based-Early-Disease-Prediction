Backend-facing tests live in backend/tests/ (unit tests for inference/
modules + API tests). This top-level tests/ directory is for
cross-cutting / integration tests added in Phase 21, e.g. a full
text -> prediction -> report round trip.
