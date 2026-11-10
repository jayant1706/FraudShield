"""
API Tests for FraudShield Analytics, Health Probes, and Model Lifecycle.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_probe(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_ready_probe(client: AsyncClient):
    response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["model_loaded"] is True


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(client: AsyncClient):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "fraudshield_http_requests_total" in response.text


@pytest.mark.asyncio
async def test_analytics_overview(client: AsyncClient, investigator_headers: dict):
    response = await client.get("/api/v1/analytics/overview", headers=investigator_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data
    assert "fraud_rate_percentage" in data
    assert "high_risk_count" in data


@pytest.mark.asyncio
async def test_analytics_fraud_trends(client: AsyncClient, investigator_headers: dict):
    response = await client.get("/api/v1/analytics/fraud-trends", headers=investigator_headers)
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert len(data["trends"]) > 0


@pytest.mark.asyncio
async def test_analytics_risk_distribution(client: AsyncClient, investigator_headers: dict):
    response = await client.get("/api/v1/analytics/risk-distribution", headers=investigator_headers)
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    risk_names = [item["risk_level"] for item in data["distribution"]]
    assert "LOW" in risk_names
    assert "HIGH" in risk_names


@pytest.mark.asyncio
async def test_model_info_endpoint(client: AsyncClient, investigator_headers: dict):
    response = await client.get("/api/v1/model/info", headers=investigator_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "v1.0.0"
    assert "XGBoost" in data["model_name"]
    assert data["num_features"] == 30


@pytest.mark.asyncio
async def test_model_metrics_endpoint(client: AsyncClient, investigator_headers: dict):
    response = await client.get("/api/v1/model/metrics", headers=investigator_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "v1.0.0"
    assert "metrics" in data


@pytest.mark.asyncio
async def test_list_model_versions(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/model/versions", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["version"] == "v1.0.0"


@pytest.mark.asyncio
async def test_model_retrain_trigger(client: AsyncClient, admin_headers: dict, user_headers: dict):
    # 1. Non-admin forbidden
    forbidden_resp = await client.post(
        "/api/v1/model/retrain",
        json={"dataset_version": "v1.1.0"},
        headers=user_headers,
    )
    assert forbidden_resp.status_code == 403

    # 2. Admin allowed
    retrain_resp = await client.post(
        "/api/v1/model/retrain",
        json={"dataset_version": "v1.1.0"},
        headers=admin_headers,
    )
    assert retrain_resp.status_code == 202
    assert retrain_resp.json()["success"] is True

