"""Tests for Binomind MVP."""
import pytest
from fastapi.testclient import TestClient
from main import app, AnalysisRequest, service

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze_happy_path():
    payload = {
        "binary_path": "firmware.bin",
        "context_size": 1024
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["chunks_processed"] > 0
    assert "// Generated Pseudocode" in data["pseudocode"]
    assert len(data["functions_found"]) > 0

def test_analyze_failure_invalid_format():
    payload = {
        "binary_path": "image.jpg",
        "context_size": 1024
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 500

def test_analyze_failure_missing_path():
    payload = {
        "context_size": 1024
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422