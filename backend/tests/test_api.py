from datetime import date

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import init_db


client = TestClient(app)


def setup_module(module):  # type: ignore
    init_db()


def test_create_agent_and_voucher_flow(tmp_path):
    # Crear agente
    agent_payload = {
        "name": "Agente Demo",
        "email": "agente@example.com",
        "phone": "+54 11 5555 5555",
        "role": "Ventas",
    }
    response = client.post("/agents", json=agent_payload)
    assert response.status_code == 201, response.text
    agent_id = response.json()["id"]

    voucher_payload = {
        "code": "VCH-001",
        "client_name": "Juan Perez",
        "issue_date": date.today().isoformat(),
        "currency": "USD",
        "total_amount": 1200.50,
        "status": "emitido",
        "notes": "Paquete Cancún",
    }

    response = client.post("/vouchers", json=voucher_payload)
    assert response.status_code == 201, response.text
    voucher = response.json()

    movement_payload = {
        "voucher_id": voucher["id"],
        "agent_id": agent_id,
        "type": "ingreso",
        "amount": 500.0,
        "description": "Adelanto del cliente",
    }

    response = client.post("/movements", json=movement_payload)
    assert response.status_code == 201, response.text
    movement = response.json()
    assert movement["agent_id"] == agent_id

    response = client.get(f"/vouchers/{voucher['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "VCH-001"
    assert len(body["movements"]) == 1

    response = client.get("/dashboard")
    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["total_vouchers"] >= 1
    assert dashboard["total_ingresos"] >= 500.0
