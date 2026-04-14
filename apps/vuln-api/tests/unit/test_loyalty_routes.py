"""Unit tests for loyalty routes."""


def test_loyalty_program_details(asgi_client):
    response = asgi_client.get("/api/loyalty/program/details")
    assert response.status_code == 200
    data = response.json()
    assert data["points_expiry_days"] == 365
    assert len(data["tiers"]) == 4


def test_loyalty_points_exchange_rates(asgi_client):
    response = asgi_client.get("/api/loyalty/points/exchange-rates")
    assert response.status_code == 200
    data = response.json()
    assert data["exchange_rates"]["points_to_usd"] == 0.01
    assert data["base_currency"] == "USD"


def test_loyalty_rewards_gift_cards(asgi_client):
    response = asgi_client.get("/api/loyalty/rewards/gift-cards")
    assert response.status_code == 200
    data = response.json()
    assert data["digital_delivery"] is True
    assert data["gift_cards"][0]["merchant"] == "Amazon"


def test_loyalty_points_transfer_rejects_empty_body(asgi_client):
    response = asgi_client.post("/api/loyalty/points/transfer", content=b"")
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "Content-Type must be application/json"
