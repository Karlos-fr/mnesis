"""Tests HTTP du flux conversationnel Mnesis."""

from fastapi.testclient import TestClient
from mnesis.api.app import create_app


def _instance(client: TestClient) -> str:
    """Crée une instance de test et retourne son identifiant."""
    return client.post("/api/v1/instances", json={"name": "Test", "locale": "fr-FR"}).json()["id"]


def test_message_returns_response_and_trace() -> None:
    """Vérifie qu'un message produit une réponse et une trace consultable."""
    client = TestClient(create_app("sqlite+pysqlite:///:memory:"))
    instance_id = _instance(client)
    turn = client.post(f"/api/v1/instances/{instance_id}/messages", json={"text": "Bonjour"})
    assert turn.status_code == 200
    body = turn.json()
    assert body["response_text"] == "Bonjour."
    trace = client.get(f"/api/v1/instances/{instance_id}/traces/{body['trace_id']}")
    assert trace.status_code == 200
    assert trace.json()["action"] == "ASSERT"


def test_blank_message_is_rejected_without_cognitive_event() -> None:
    """Vérifie que l'API rejette une entrée vide avant le moteur cognitif."""
    client = TestClient(create_app("sqlite+pysqlite:///:memory:"))
    instance_id = _instance(client)
    response = client.post(f"/api/v1/instances/{instance_id}/messages", json={"text": "   "})
    assert response.status_code == 422
