"""Integration tests for the FastAPI application.

These test the API endpoints using FastAPI's TestClient.
They do NOT require running services (DB, Redis) — they verify
route wiring, request validation, and response shapes.
"""

import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gtm.api.deps import get_db, get_current_tenant


@pytest.fixture()
def client():
    """Create a test client with mocked storage backends."""
    with (
        patch("gtm.storage.database.init_db"),
        patch("gtm.storage.redis_client.init_redis"),
        patch("gtm.storage.s3.init_s3"),
    ):
        from gtm.api.app import create_app

        app = create_app()

        # Override DB and auth dependencies for testing
        mock_session = MagicMock(spec=Session)
        app.dependency_overrides[get_db] = lambda: mock_session
        app.dependency_overrides[get_current_tenant] = lambda: "test-tenant"

        yield TestClient(app)

        app.dependency_overrides.clear()


class TestHealthEndpoints:
    def test_liveness(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestAnalysisValidation:
    def test_missing_required_fields(self, client):
        resp = client.post("/api/v1/analyses", json={"brand": "X"})
        assert resp.status_code == 422  # Validation error

    def test_invalid_url(self, client):
        resp = client.post(
            "/api/v1/analyses",
            json={
                "site_url": "not-a-url",
                "brand": "Test",
                "audience_primary": "devs",
            },
        )
        assert resp.status_code == 422
