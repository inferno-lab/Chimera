"""Unit tests for security ops routes."""


def test_security_monitoring_bypass(asgi_client):
    response = asgi_client.get("/api/security/monitoring/bypass")
    assert response.status_code == 200
    data = response.json()
    assert data["monitoring_disabled"] is True
    assert "log_suppression" in data["strategies"]


def test_threats_indicators(asgi_client):
    response = asgi_client.get("/api/threats/indicators")
    assert response.status_code == 200
    data = response.json()
    assert data["total_indicators"] == 4
    assert data["indicators"][0]["type"] == "ip_address"


def test_incidents_create_rejects_empty_body(asgi_client):
    response = asgi_client.post("/api/incidents/create", content=b"")
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "Content-Type must be application/json"


def test_defense_metrics(asgi_client):
    response = asgi_client.get("/api/defense/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["metrics_period"] == "24_hours"
    assert "detection_metrics" in data
