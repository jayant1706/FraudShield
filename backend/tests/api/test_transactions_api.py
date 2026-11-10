"""
API Tests for FraudShield Transaction Ingestion and Investigation Status Updates.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_transaction(client: AsyncClient, investigator_headers: dict):
    payload = {
        "external_transaction_id": "TXN_FLOW_001",
        "amount": 149.99,
        "merchant_category": "electronics",
        "device_id": "DEV_TEST_01",
        "location": "Chicago, USA",
    }
    create_resp = await client.post(
        "/api/v1/transactions",
        json=payload,
        headers=investigator_headers,
    )
    assert create_resp.status_code == 201
    txn = create_resp.json()
    assert txn["external_transaction_id"] == "TXN_FLOW_001"
    assert txn["amount"] == 149.99
    assert txn["status"] == "PENDING"

    # Get by ID
    get_resp = await client.get(
        f"/api/v1/transactions/{txn['id']}",
        headers=investigator_headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == txn["id"]


@pytest.mark.asyncio
async def test_list_transactions_with_pagination_and_filters(client: AsyncClient, investigator_headers: dict):
    response = await client.get(
        "/api/v1/transactions?page=1&page_size=10&status=PENDING",
        headers=investigator_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "total_pages" in data


@pytest.mark.asyncio
async def test_update_transaction_status_and_rbac(
    client: AsyncClient, investigator_headers: dict, user_headers: dict
):
    # Ingest txn
    create_resp = await client.post(
        "/api/v1/transactions",
        json={
            "external_transaction_id": "TXN_STATUS_REVIEW_01",
            "amount": 890.0,
            "merchant_category": "travel",
        },
        headers=investigator_headers,
    )
    txn_id = create_resp.json()["id"]

    # 1. Regular user forbidden from changing investigation status
    forbidden_resp = await client.patch(
        f"/api/v1/transactions/{txn_id}/status",
        json={"status": "REJECTED", "investigation_notes": "Attempt from normal user"},
        headers=user_headers,
    )
    assert forbidden_resp.status_code == 403

    # 2. Investigator allowed
    update_resp = await client.patch(
        f"/api/v1/transactions/{txn_id}/status",
        json={"status": "REJECTED", "investigation_notes": "Confirmed compromised card account."},
        headers=investigator_headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "REJECTED"
    assert "Confirmed compromised" in data["investigation_notes"]

