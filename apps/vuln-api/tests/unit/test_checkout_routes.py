"""Unit tests for migrated checkout Starlette routes."""

from app.models import cart_sessions, payment_methods_db


def test_checkout_methods_lists_available_payment_methods(asgi_client):
    payment_methods_db["wire"] = {"enabled": True, "processing_fee": 0.03}

    response = asgi_client.get("/api/checkout/methods")

    assert response.status_code == 200
    data = response.json()
    assert "wire" in data["available_methods"]
    assert any(method["method"] == "wire" for method in data["methods_detail"])


def test_checkout_shipping_address_creates_session_and_processes_cart(asgi_client):
    shipping_response = asgi_client.put(
        "/api/shipping/address",
        json={"line1": "100 Demo Way", "city": "New York", "state": "NY"},
    )

    assert shipping_response.status_code == 200
    shipping_data = shipping_response.json()
    session_id = shipping_data["session_id"]
    assert session_id in cart_sessions
    assert cart_sessions[session_id]["shipping_address"]["city"] == "New York"

    checkout_response = asgi_client.post("/api/checkout/process", json={})

    assert checkout_response.status_code == 200
    checkout_data = checkout_response.json()
    assert checkout_data["session_id"] == session_id
    assert checkout_data["item_count"] == 1
    assert checkout_data["shipping_address"]["line1"] == "100 Demo Way"


def test_checkout_shipping_calculate_returns_quote(asgi_client):
    response = asgi_client.put(
        "/api/shipping/calculate",
        json={"zone": "domestic", "weight_lbs": 4, "expedite": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["shipping_total"] == 24.24
    assert data["estimated_delivery_days"] == 1


def test_checkout_audit_suppress_returns_suppressed_contract(asgi_client):
    response = asgi_client.post(
        "/api/checkout/audit/suppress",
        json={"transaction_ids": ["txn-1"], "reason": "cleanup"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "suppressed"
    assert data["audit_gap"] is True
    assert data["transaction_ids"] == ["txn-1"]


def test_checkout_process_rejects_invalid_cart_item_types(asgi_client):
    shipping_response = asgi_client.put(
        "/api/shipping/address",
        json={"line1": "100 Demo Way", "city": "New York", "state": "NY"},
    )
    session_id = shipping_response.json()["session_id"]
    cart_sessions[session_id]["items"] = [{"sku": "SKU-BAD", "price": "oops", "quantity": 1}]

    response = asgi_client.post("/api/checkout/process", json={})

    assert response.status_code == 400
    assert response.json()["error"] == "Invalid cart item pricing state"
