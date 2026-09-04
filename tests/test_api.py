"""
Basic tests for PrescriptionLens AI FastAPI backend.
Run with: pytest tests/test_api.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """/health should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_analyze_empty_text_returns_400():
    """/analyze should reject empty prescription text."""
    response = client.post("/analyze", json={"prescription_text": "   "})
    assert response.status_code == 400


def test_chat_missing_fields_returns_422():
    """/chat should fail validation when required fields are missing."""
    response = client.post("/chat", json={"question": "What medicines are listed?"})
    assert response.status_code == 422


def test_chat_empty_question_returns_400():
    """/chat should reject an empty question even with valid prescription text."""
    response = client.post(
        "/chat",
        json={"question": "   ", "prescription_text": "Paracetamol 500mg twice daily"},
    )
    assert response.status_code == 400


def test_ocr_missing_param_returns_422():
    """/ocr requires image_base64 query param; missing it should fail validation."""
    response = client.post("/ocr")
    assert response.status_code == 422


def test_invalid_route_returns_404():
    """A nonexistent route should return 404."""
    response = client.get("/nonexistent-route")
    assert response.status_code == 404
