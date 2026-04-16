"""Unit tests for migrated education Starlette routes."""


def test_education_remote_client_requires_session_for_all_public_endpoints(asgi_remote_client):
    for path in (
        "/api/v1/education/vulns",
        "/api/v1/education/vulns/CHM-BANK-001",
        "/api/v1/education/portals",
        "/api/v1/education/owasp",
    ):
        response = asgi_remote_client.get(path)
        assert response.status_code == 401


def test_education_requires_session_for_vulnerability_catalog(asgi_remote_client):
    response = asgi_remote_client.get("/api/v1/education/vulns")

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "Authentication required to access educational metadata"


def test_education_vulnerability_catalog_filters_by_portal(asgi_client, set_asgi_session):
    set_asgi_session(asgi_client, {"user_id": "edu-user"})

    response = asgi_client.get("/api/v1/education/vulns?portal=banking")

    assert response.status_code == 200
    data = response.json()
    assert "CHM-BANK-001" in data
    assert data["CHM-BANK-001"]["portal"] == "banking"
    assert "config_key" not in data["CHM-BANK-001"]


def test_education_vulnerability_detail_reports_patch_state(asgi_client, set_asgi_session):
    set_asgi_session(asgi_client, {"user_id": "edu-user"})

    response = asgi_client.get("/api/v1/education/vulns/CHM-BANK-001")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Business Logic Manipulation (Transfer)"
    assert data["is_patched"] is False


def test_education_portals_returns_known_portal_list(asgi_client, set_asgi_session):
    set_asgi_session(asgi_client, {"user_id": "edu-user"})

    response = asgi_client.get("/api/v1/education/portals")

    assert response.status_code == 200
    data = response.json()
    assert "banking" in data["portals"]
