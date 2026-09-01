"""Unit tests for middleware, request IDs, timing headers, and sanitized error responses."""

from fastapi.testclient import TestClient


def test_request_id_generated_and_returned_in_headers(client: TestClient):
    """Verify request ID is generated when not provided by client."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_request_id_preserved_when_supplied(client: TestClient):
    """Verify client-supplied request ID is preserved."""
    custom_id = "client-trace-123456"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


def test_timing_header_present(client: TestClient):
    """Verify X-Process-Time-Ms header is returned."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Process-Time-Ms" in response.headers
    latency = float(response.headers["X-Process-Time-Ms"])
    assert latency >= 0.0


def test_error_response_contains_request_id(client: TestClient):
    """Verify error responses include request_id matching header."""
    custom_id = "test-error-trace-999"
    response = client.get(
        "/api/v1/reviews/missing-uuid-123",
        headers={"X-Request-ID": custom_id},
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["request_id"] == custom_id
    assert data["error"]["code"] == "REVIEW_NOT_FOUND"


def test_validation_error_format(client: TestClient):
    """Verify 422 validation errors conform to standardized error envelope."""
    response = client.post("/api/v1/reviews", json={})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in data["error"]
