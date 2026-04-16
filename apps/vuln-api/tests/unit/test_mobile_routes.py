"""Unit tests for migrated mobile Starlette routes."""


def test_mobile_app_settings_exposes_configuration(asgi_client):
    response = asgi_client.get("/api/mobile/v2/config/app-settings")

    assert response.status_code == 200
    data = response.json()
    assert data["app_version"] == "4.2.1"
    assert data["security_features"]["biometric_auth"] is True


def test_mobile_limits_override_requires_session(asgi_client):
    response = asgi_client.put(
        "/api/mobile/v2/accounts/limits/override",
        json={"daily_limit": 50000},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Authentication required"


def test_mobile_limits_override_uses_session_user(asgi_client, set_asgi_session):
    set_asgi_session(asgi_client, {"user_id": "mobile-user"})

    response = asgi_client.put(
        "/api/mobile/v2/accounts/limits/override",
        json={"daily_limit": 50000, "instant_transfer_limit": 20000},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "mobile-user"
    assert data["daily_limit"] == 50000
    assert data["instant_transfer_limit"] == 20000


def test_mobile_session_transfer_returns_transfer_contract(asgi_client):
    response = asgi_client.post(
        "/api/mobile/v2/auth/session/transfer",
        json={"source_device_id": "iphone-1", "target_device_id": "ipad-2"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_transferred"] is True
    assert data["target_device_id"] == "ipad-2"
