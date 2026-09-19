"""Tests for health check endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ielts-learning-service"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data


def test_readiness_check(client: TestClient) -> None:
    """Readiness endpoint returns status with checks."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
    assert "timestamp" in data
