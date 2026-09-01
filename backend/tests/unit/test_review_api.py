"""Integration tests for Review API endpoints (/api/v1/reviews)."""

from fastapi.testclient import TestClient


def test_submit_review_success(client: TestClient):
    """Verify POST /api/v1/reviews creates a 201 Created review record."""
    payload = {
        "code": "def greet(name):\n    return f'Hello, {name}!'\n",
        "language": "python",
        "filename": "greeter.py",
        "context_notes": "Greeting helper function",
    }
    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "review_id" in data
    assert "analysis_id" in data
    assert data["status"] == "pending"
    assert data["language"] == "python"
    assert data["filename"] == "greeter.py"
    assert data["line_count"] == 3
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-Ms" in response.headers


def test_submit_review_alias_source_code(client: TestClient):
    """Verify POST /api/v1/reviews accepts 'source_code' as field alias."""
    payload = {
        "source_code": "print('testing alias')",
        "language": "python",
    }
    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"


def test_submit_review_empty_code_rejected(client: TestClient):
    """Verify POST /api/v1/reviews rejects empty code payload."""
    payload = {
        "code": "   ",
        "language": "python",
    }
    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_SOURCE_CODE"
    assert "request_id" in data["error"]


def test_submit_review_unsupported_language_rejected(client: TestClient):
    """Verify POST /api/v1/reviews rejects unsupported languages."""
    payload = {
        "code": "public class Main { public static void main(String[] args) {} }",
        "language": "java",
    }
    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_LANGUAGE"


def test_get_review_by_id_endpoint(client: TestClient):
    """Verify GET /api/v1/reviews/{review_id} fetches created record."""
    create_res = client.post(
        "/api/v1/reviews",
        json={"code": "x = 10\ny = 20\n", "language": "python"},
    )
    assert create_res.status_code == 201
    review_id = create_res.json()["review_id"]

    get_res = client.get(f"/api/v1/reviews/{review_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["review_id"] == review_id
    assert data["status"] == "pending"


def test_get_review_not_found(client: TestClient):
    """Verify GET /api/v1/reviews/{invalid_id} returns 404 with structured error."""
    response = client.get("/api/v1/reviews/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "REVIEW_NOT_FOUND"
    assert "request_id" in data["error"]


def test_list_reviews_endpoint(client: TestClient):
    """Verify GET /api/v1/reviews with pagination."""
    # Ensure at least 1 record exists
    client.post("/api/v1/reviews", json={"code": "a = 1", "language": "python"})

    response = client.get("/api/v1/reviews?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_delete_review_endpoint(client: TestClient):
    """Verify DELETE /api/v1/reviews/{review_id} removes record."""
    create_res = client.post("/api/v1/reviews", json={"code": "del_me = True", "language": "python"})
    review_id = create_res.json()["review_id"]

    del_res = client.delete(f"/api/v1/reviews/{review_id}")
    assert del_res.status_code == 204

    # Second fetch should return 404
    fetch_res = client.get(f"/api/v1/reviews/{review_id}")
    assert fetch_res.status_code == 404
