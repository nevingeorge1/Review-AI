"""Unit and integration tests for health, liveness, and readiness endpoints."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Verify GET / returns API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ReviewAI"
    assert "version" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_root_health_endpoint(client: TestClient):
    """Verify GET /health returns structured health status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "reviewai"
    assert "features" in data
    assert data["features"]["static_analysis_enabled"] is True
    assert data["features"]["llm_enabled"] is True
    assert "limits" in data
    assert data["limits"]["max_source_lines"] > 0


def test_api_v1_health_endpoint(client: TestClient):
    """Verify GET /api/v1/health returns consistent versioned health data."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "reviewai"


def test_liveness_endpoint(client: TestClient):
    """Verify GET /health/live and /api/v1/health/live."""
    for path in ["/health/live", "/api/v1/health/live"]:
        response = client.get(path)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "live"
        assert "timestamp" in data


def test_readiness_endpoint(client: TestClient):
    """Verify GET /health/ready and /api/v1/health/ready."""
    for path in ["/health/ready", "/api/v1/health/ready"]:
        response = client.get(path)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert data["checks"]["storage"] == "ready"
