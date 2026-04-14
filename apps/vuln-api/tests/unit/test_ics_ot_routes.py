"""Unit tests for ICS/OT routes."""


def test_ics_scada_systems(asgi_client):
    response = asgi_client.get("/api/ics/scada/systems")
    assert response.status_code == 200
    data = response.json()
    assert data["total_systems"] == 3
    assert data["authentication_required"] is False


def test_plc_commands_send(asgi_client):
    response = asgi_client.post(
        "/api/plc/commands/send",
        json={"plc_id": "PLC-101", "command": "WRITE", "register": "40001", "value": 99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plc_id"] == "PLC-101"
    assert data["command_accepted"] is True


def test_ics_hmi_interfaces(asgi_client):
    response = asgi_client.get("/api/ics/hmi/interfaces")
    assert response.status_code == 200
    data = response.json()
    assert data["unauthenticated_access"] == 1
    assert data["session_hijacking_possible"] is True


def test_ot_network_segment(asgi_client):
    response = asgi_client.post(
        "/api/ot/network/segment",
        json={"source_segment": "Control-LAN", "target_segment": "OT-DMZ", "bypass_firewall": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bypass_firewall"] is True
    assert data["lateral_movement_enabled"] is True
