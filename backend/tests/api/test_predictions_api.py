"""
API Tests for FraudShield Prediction Service and Explainability.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_predict_legitimate_transaction(client: AsyncClient, investigator_headers: dict):
    payload = {
        "transaction_id": "TXN_LEGIT_101",
        "amount": 25.40,
        "merchant_category": "groceries",
        "device_id": "DEV_SAFE_01",
        "location": "San Francisco, USA",
        "features": {f"V{i}": 0.05 for i in range(1, 29)},
    }
    response = await client.post(
        "/api/v1/predictions/predict",
        json=payload,
        headers=investigator_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["transaction_id"] == "TXN_LEGIT_101"
    assert "fraud_probability" in data
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "explanations" in data
    assert len(data["explanations"]) > 0
    assert data["model_version"] == "v1.0.0"


@pytest.mark.asyncio
async def test_predict_fraudulent_transaction_signature(client: AsyncClient, investigator_headers: dict):
    # Pass strong fraud signature (negative V14, V12, V10, positive V4)
    fraud_features = {f"V{i}": 0.0 for i in range(1, 29)}
    fraud_features["V14"] = -8.5
    fraud_features["V12"] = -6.2
    fraud_features["V10"] = -5.8
    fraud_features["V4"] = 5.2

    payload = {
        "transaction_id": "TXN_FRAUD_888",
        "amount": 3400.0,  # Also triggers high amount rule
        "merchant_category": "crypto",  # Triggers high risk category rule
        "device_id": "DEV_SUSPECT_99",
        "location": "Unknown Proxy",
        "features": fraud_features,
    }
    response = await client.post(
        "/api/v1/predictions/predict",
        json=payload,
        headers=investigator_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["transaction_id"] == "TXN_FRAUD_888"
    assert data["fraud_probability"] > 0.5
    assert data["risk_level"] == "HIGH"
    assert data["recommended_action"] == "FLAG_FOR_REVIEW"
    assert len(data["rule_triggers"]) > 0
    # Check that V14 or amount is highlighted in SHAP explanations
    top_features = [e["feature"] for e in data["explanations"]]
    assert any("V14" in f or "amount" in f.lower() for f in top_features)


@pytest.mark.asyncio
async def test_predict_invalid_input_negative_amount_fails(client: AsyncClient, investigator_headers: dict):
    payload = {
        "transaction_id": "TXN_INVALID_01",
        "amount": -50.0,  # Invalid negative amount
        "merchant_category": "retail",
    }
    response = await client.post(
        "/api/v1/predictions/predict",
        json=payload,
        headers=investigator_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_prediction_endpoint(client: AsyncClient, investigator_headers: dict):
    payload = {
        "transactions": [
            {
                "transaction_id": "TXN_BATCH_1",
                "amount": 10.0,
                "merchant_category": "coffee",
            },
            {
                "transaction_id": "TXN_BATCH_2",
                "amount": 4500.0,
                "merchant_category": "luxury_jewelry",
            },
        ]
    }
    response = await client.post(
        "/api/v1/predictions/batch",
        json=payload,
        headers=investigator_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 2
    assert len(data["predictions"]) == 2
    assert "summary" in data


@pytest.mark.asyncio
async def test_get_prediction_by_id(client: AsyncClient, investigator_headers: dict):
    # 1. Create a prediction
    create_resp = await client.post(
        "/api/v1/predictions/predict",
        json={
            "transaction_id": "TXN_QUERY_TEST_1",
            "amount": 80.0,
            "merchant_category": "retail",
        },
        headers=investigator_headers,
    )
    pred_id = create_resp.json()["prediction_id"]

    # 2. Fetch by ID
    get_resp = await client.get(
        f"/api/v1/predictions/{pred_id}",
        headers=investigator_headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["prediction_id"] == pred_id

