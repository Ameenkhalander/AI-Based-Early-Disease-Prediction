# AI Healthcare Assistant

**Status: Frontend demo and SQLite-backed API available; trained models remain.**
No trained models are included yet. The repository began as the
approved architecture from Phase 1 laid out as a folder structure, with
every file carrying a docstring that explains its purpose, inputs,
outputs, and which build phase implements it -- see PHASE1_RESEARCH.md
for the full dataset/architecture reasoning that this scaffold follows.

## Run the full app

From the repository root, run `python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8001` and open `http://localhost:8001/frontend/`. Assessment and image check-ins are stored in `data/carepath.sqlite3` through `/api/v1/history`. The History view loads both types from SQLite and falls back to browser storage if the API is unavailable. Image uploads are validated by `/api/v1/image-analysis`; it reports `model_unavailable` until trained CNN weights and class metadata are placed in the appropriate `artifacts/image_model_*` directory.

## What this project will do (once built)
A symptom-assessment web app: describe symptoms by text or voice, get
doctor-style follow-up questions, a top-3 explainable prediction (never
a diagnosis), emergency detection, an optional skin-image analysis
module, and a downloadable PDF report.

## Full documentation index
- `PHASE1_RESEARCH.md` -- dataset research, ML-vs-DL reasoning, architecture
- `docs/ARCHITECTURE.md`
- `docs/DATASETS.md`
- `docs/MODEL_CARD.md` (filled in from Phase 6/15)
- `docs/API.md` (filled in from Phase 16)
- `docs/DEPLOYMENT.md` (filled in from Phase 22)
- `docs/SAFETY.md`

## Repo layout
See `docs/ARCHITECTURE.md`. Every subpackage (`backend/inference/`,
`ml/text/`, `ml/vision/`, etc.) has an `__init__.py` or per-file
docstring explaining what belongs there.

## Medical safety
This system never claims to provide a diagnosis. See `docs/SAFETY.md`
and `backend/inference/emergency_detector.py`.
