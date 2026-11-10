"""
API Tests for FraudShield Authentication and RBAC.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_new_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new_investigator@fraudshield.io",
            "full_name": "New Investigator",
            "password": "Password123!",
            "role": "INVESTIGATOR",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new_investigator@fraudshield.io"
    assert data["role"] == "INVESTIGATOR"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email_conflict(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@fraudshield.io",  # Already seeded
            "full_name": "Admin Clone",
            "password": "Password123!",
        },
    )
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data["detail"]


@pytest.mark.asyncio
async def test_login_success_returns_jwt(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@fraudshield.io",
            "password": "AdminPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@fraudshield.io"


@pytest.mark.asyncio
async def test_login_invalid_password_fails(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@fraudshield.io",
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@fraudshield.io"
    assert data["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_get_me_unauthorized_without_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

