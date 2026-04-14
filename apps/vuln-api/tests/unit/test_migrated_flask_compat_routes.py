"""Compatibility tests for migrated Starlette routes exposed via Flask create_app()."""

import pytest


def assert_matching_error_contract(flask_response, asgi_response):
    flask_data = flask_response.get_json()
    asgi_data = asgi_response.json()

    assert flask_data["error"] == asgi_data["error"]
    assert flask_data["status"] == asgi_data["status"]
    assert flask_data["path"] == asgi_data["path"]
    assert flask_data["method"] == asgi_data["method"]
    assert flask_data["debug"]["query_params"] == asgi_data["debug"]["query_params"]


@pytest.mark.parametrize(
    ("path", "expected_status", "field", "expected_value"),
    [
        ("/api/v1/gov/cases/1", 200, "case_id", "1"),
        ("/api/v1/telecom/subscribers/sub-1/profile", 200, "subscriber", {"subscriber_id": "sub-1"}),
        ("/api/v1/energy-utilities/meters/meter-1/readings", 200, "reading", {"meter_id": "meter-1"}),
        ("/api/security/monitoring/bypass", 200, "monitoring_disabled", True),
        ("/api/loyalty/program/details", 200, "points_expiry_days", 365),
        ("/api/compliance/status", 200, "audit_ready", True),
    ],
)
def test_migrated_routes_remain_reachable_via_flask_compat(client, path, expected_status, field, expected_value):
    response = client.get(path)

    assert response.status_code == expected_status
    data = response.get_json()
    if isinstance(expected_value, dict):
        for key, value in expected_value.items():
            assert data[field][key] == value
    else:
        assert data[field] == expected_value


def test_strict_json_routes_match_between_flask_and_asgi(client, asgi_client):
    flask_response = client.post("/api/reporting/sar", data=b"")
    asgi_response = asgi_client.post("/api/reporting/sar", content=b"")

    assert flask_response.status_code == 415
    assert asgi_response.status_code == 415
    assert_matching_error_contract(flask_response, asgi_response)


def test_vendor_json_media_types_work_for_flask_and_asgi(client, asgi_client):
    payload = '{"incident_type":"credential_theft","severity":"high"}'
    headers = {"content-type": "application/vnd.api+json"}

    flask_response = client.post("/api/incidents/create", data=payload, content_type=headers["content-type"])
    asgi_response = asgi_client.post("/api/incidents/create", content=payload, headers=headers)

    assert flask_response.status_code == 201
    assert asgi_response.status_code == 201
    assert flask_response.get_json()["severity"] == "high"
    assert asgi_response.json()["severity"] == "high"


def test_malformed_json_rejected_by_flask_and_asgi(client, asgi_client):
    payload = "{"

    flask_response = client.post("/api/incidents/create", data=payload, content_type="application/json")
    asgi_response = asgi_client.post("/api/incidents/create", content=payload, headers={"content-type": "application/json"})

    assert flask_response.status_code == 400
    assert asgi_response.status_code == 400
    assert_matching_error_contract(flask_response, asgi_response)


def test_non_object_json_rejected_by_flask_and_asgi(client, asgi_client):
    payload = "[]"

    flask_response = client.post("/api/incidents/create", data=payload, content_type="application/json")
    asgi_response = asgi_client.post("/api/incidents/create", content=payload, headers={"content-type": "application/json"})

    assert flask_response.status_code == 400
    assert asgi_response.status_code == 400
    assert_matching_error_contract(flask_response, asgi_response)
