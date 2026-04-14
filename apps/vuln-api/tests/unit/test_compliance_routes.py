"""Unit tests for compliance routes."""


def test_compliance_rules(asgi_client):
    response = asgi_client.get("/api/compliance/rules")
    assert response.status_code == 200
    data = response.json()
    assert len(data["active_rules"]) == 3
    assert "transaction_splitting" in data["bypass_mechanisms"]


def test_reporting_sar_rejects_empty_body(asgi_client):
    response = asgi_client.post("/api/reporting/sar", content=b"")
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "Content-Type must be application/json"


def test_compliance_bypass_rejects_empty_body(asgi_client):
    response = asgi_client.post("/api/compliance/bypass", content=b"")
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "Content-Type must be application/json"


def test_audit_trails_put_rejects_empty_body(asgi_client):
    response = asgi_client.put("/api/audit/trails", content=b"")
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "Content-Type must be application/json"


def test_compliance_status(asgi_client):
    response = asgi_client.get("/api/compliance/status")
    assert response.status_code == 200
    data = response.json()
    assert data["audit_ready"] is True
    assert len(data["compliance_frameworks"]) == 3
