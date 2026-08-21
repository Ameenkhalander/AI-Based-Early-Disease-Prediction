"""Minimal runnable API for the current frontend demo slice."""

from pathlib import Path
import json
import sqlite3
from typing import Any
from io import BytesIO

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from PIL import Image


class AssessmentRequest(BaseModel):
	raw_text: str | None = Field(default=None)
	text: str | None = Field(default=None)
	session_id: str | None = Field(default=None)
	answers: list[str] = Field(default_factory=list)



class HistoryRecord(BaseModel):
	kind: str = "symptoms"
	text: str
	review_type: str = ""
	details: dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="Carepath API", version="0.1.0")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:8000", "http://localhost:8001", "http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

database_path = Path(__file__).resolve().parents[1] / "data" / "carepath.sqlite3"
database_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
	connection = sqlite3.connect(database_path)
	connection.row_factory = sqlite3.Row
	return connection


def initialize_database() -> None:
	with get_connection() as connection:
		connection.execute(
			"""CREATE TABLE IF NOT EXISTS assessment_history (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				kind TEXT NOT NULL,
				text TEXT NOT NULL,
				review_type TEXT NOT NULL DEFAULT '',
				details_json TEXT NOT NULL DEFAULT '{}',
				created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
			)"""
		)


initialize_database()


def assess(text: str) -> dict[str, Any]:
	value = text.lower()
	emergency_terms = ["chest pain", "trouble breathing", "difficulty breathing", "severe bleeding", "unconscious", "stroke", "suicidal"]
	emergency = next((term for term in emergency_terms if term in value), None)
	if emergency:
		return {"emergency": True, "emergency_message": f"Seek urgent help now. You mentioned {emergency}.", "predictions": [], "follow_up": None}

	if any(term in value for term in ("cough", "sore throat", "fever", "congestion", "runny nose")):
		predictions = [
			{"label": "Viral upper respiratory pattern", "explanation": "Throat irritation, cough, congestion, and fever can occur together."},
			{"label": "Seasonal allergies", "explanation": "Nasal symptoms and throat irritation can also follow an allergic pattern."},
			{"label": "Irritation or reflux", "explanation": "A persistent scratchy throat can have non-infectious causes."},
		]
		follow_up = {"question": "When did these symptoms begin?", "options": ["Today", "1-3 days ago", "More than a week ago"]}
	elif any(term in value for term in ("headache", "migraine", "nausea")):
		predictions = [
			{"label": "Tension-type headache pattern", "explanation": "Head pressure can be linked with tension, sleep, or hydration."},
			{"label": "Migraine pattern", "explanation": "Nausea or light sensitivity may be worth discussing with a clinician."},
			{"label": "Viral illness", "explanation": "Headache can occur alongside an early viral illness."},
		]
		follow_up = {"question": "How strong is the discomfort right now?", "options": ["Mild", "Moderate", "Severe"]}
	else:
		predictions = [{"label": "General symptom pattern", "explanation": "More context is needed before a meaningful pattern can be considered."}]
		follow_up = {"question": "How long have you noticed this change?", "options": ["Less than a day", "A few days", "More than a week"]}
	return {"emergency": False, "emergency_message": None, "predictions": predictions, "follow_up": follow_up}


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok", "service": "carepath-api", "database": "sqlite"}


@app.get("/api/v1/history")
def list_history() -> list[dict[str, Any]]:
	with get_connection() as connection:
		rows = connection.execute(
			"SELECT id, kind, text, review_type, details_json, created_at FROM assessment_history ORDER BY id DESC LIMIT 50"
		).fetchall()
	return [
		{
			"id": row["id"],
			"type": row["kind"],
			"text": row["text"],
			"reviewType": row["review_type"],
			"details": json.loads(row["details_json"]),
			"date": row["created_at"],
		}
		for row in rows
	]


@app.post("/api/v1/history", status_code=201)
def create_history(record: HistoryRecord) -> dict[str, Any]:
	with get_connection() as connection:
		cursor = connection.execute(
			"INSERT INTO assessment_history (kind, text, review_type, details_json) VALUES (?, ?, ?, ?)",
			(record.kind, record.text, record.review_type, json.dumps(record.details)),
		)
		return {"id": cursor.lastrowid, "status": "stored"}


@app.post("/api/v1/assessment")
@app.post("/api/assessment")
def assessment(request: AssessmentRequest) -> dict[str, Any]:
	text = (request.raw_text or request.text or "").strip()
	if not text:
		return {"emergency": False, "predictions": [], "follow_up": {"question": "What symptoms are you noticing?", "options": []}}
	response = assess(text)
	response["session_id"] = request.session_id
	response["answers"] = request.answers
	return response


@app.post("/api/v1/image-analysis")
async def image_analysis(
	file: UploadFile = File(...),
	analysis_type: str = Form("general"),
	context: str = Form(""),
) -> dict[str, Any]:
	"""Validate an image and expose the optional CNN inference boundary."""
	if analysis_type not in {"general", "lesion"}:
		return {"status": "error", "message": "analysis_type must be general or lesion"}
	image_bytes = await file.read()
	try:
		with Image.open(BytesIO(image_bytes)) as image:
			image.verify()
		with Image.open(BytesIO(image_bytes)) as image:
			width, height = image.size
	except Exception:
		return {"status": "error", "message": "The uploaded file is not a readable image."}

	model_directory = Path(__file__).resolve().parents[1] / "artifacts" / f"image_model_{'lesion' if analysis_type == 'lesion' else 'general'}"
	weights = next((path for path in model_directory.glob("*") if path.suffix in {".pt", ".pth", ".onnx"}), None)
	return {
		"status": "model_unavailable" if weights is None else "model_ready",
		"analysis_type": analysis_type,
		"filename": file.filename,
		"content_type": file.content_type,
		"width": width,
		"height": height,
		"context_received": bool(context.strip()),
		"message": "No trained CNN weights are present in this repository. Add model weights and class metadata to enable disease classification." if weights is None else "CNN artifact detected; inference adapter is ready to load it.",
	}


frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
if frontend_dir.exists():
	app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")
