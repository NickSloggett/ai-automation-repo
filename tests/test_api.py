"""Tests for API endpoints."""

import pytest
from fastapi import status


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_ready(client):
    """Test readiness probe."""
    response = client.get("/health/ready")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"


def test_health_live(client):
    """Test liveness probe."""
    response = client.get("/health/live")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "alive"


def test_app_info(client):
    """Test application info endpoint."""
    response = client.get("/info")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_create_agent(client, sample_task_config):
    """Test agent creation endpoint."""
    payload = {
        "name": "test_agent",
        "description": "Test agent",
        "agent_type": "task",
        "config": sample_task_config,
    }

    response = client.post("/agents/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == "test_agent"
    assert data["agent_type"] == "task"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_agents(client):
    """Test listing agents."""
    response = client.get("/agents/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_agent_not_found(client):
    """Test getting non-existent agent."""
    response = client.get("/agents/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND







