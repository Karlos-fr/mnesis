"""Tests HTTP de gestion des instances Mnesis."""

from fastapi.testclient import TestClient
from mnesis.api.app import create_app


def test_create_and_get_instance() -> None:
    """Vérifie qu'une instance créée via HTTP peut être relue."""
    client = TestClient(create_app("sqlite+pysqlite:///:memory:"))
    created = client.post("/api/v1/instances", json={"name": "Personnel", "locale": "fr-FR"})
    assert created.status_code == 201
    instance_id = created.json()["id"]
    fetched = client.get(f"/api/v1/instances/{instance_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Personnel"
