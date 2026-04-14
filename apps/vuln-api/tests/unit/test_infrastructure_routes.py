"""Unit tests for infrastructure routes."""


def test_process_image_command_injection(asgi_client):
    response = asgi_client.post(
        "/api/v1/infrastructure/compute/process-image",
        json={"image_url": "https://example.com/image.png; id"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert "Command injection output" in data["debug_info"]


def test_storage_presign_path_traversal(asgi_client):
    response = asgi_client.post(
        "/api/v1/infrastructure/storage/presign",
        json={"file_id": "../prod-secrets.txt", "action": "GET"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "sensitive-internal-bucket" in data["url"]
    assert "warning" in data


def test_gateway_routes(asgi_client):
    response = asgi_client.get("/api/gateway/routes")
    assert response.status_code == 200
    data = response.json()
    assert data["total_routes"] == 47
    assert data["routes"][0]["service"] == "authentication"


def test_gateway_backdoor(asgi_client):
    response = asgi_client.post("/api/gateway/backdoor", json={"key": "ops-shell"})
    assert response.status_code == 201
    data = response.json()
    assert data["backdoor_key"] == "ops-shell"
    assert data["backdoor_installed"] is True
