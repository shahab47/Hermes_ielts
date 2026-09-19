"""Tests for diagnostic onboarding endpoints (Phase 14)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_onboard_learner_flow(client: TestClient) -> None:
    """Test full learner onboarding request."""
    payload = {
        "external_user_id": "tg_987654321",
        "target_exam": "IELTS Academic",
        "target_overall_band": 7.5,
        "available_daily_minutes": 45,
        "explanation_language": "fa",
        "prior_overall_score": 6.0,
    }

    response = client.post("/diagnostic/onboard", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["baseline_status"] == "completed"
    assert data["initial_estimated_band"] == 6.0
    assert "learner_id" in data
    assert "first_week_plan" in data
    assert len(data["first_week_plan"]["activities"]) >= 2
    assert "X-Request-ID" in response.headers
