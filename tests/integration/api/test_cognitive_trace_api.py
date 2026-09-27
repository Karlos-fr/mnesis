"""Tests API des traces cognitives enrichies."""

from fastapi.testclient import TestClient

from mnesis.api.app import create_app


def test_trace_exposes_cycle_details() -> None:
    """Vérifie que le diagnostic expose interprétation, règles, scores et sortie."""
    client = TestClient(create_app("sqlite+pysqlite:///:memory:"))
    instance_id = client.post(
        "/api/v1/instances",
        json={"name": "Test", "locale": "fr-FR"},
    ).json()["id"]
    turn = client.post(
        f"/api/v1/instances/{instance_id}/messages",
        json={"text": "Bonjour"},
    ).json()
    trace = client.get(
        f"/api/v1/instances/{instance_id}/traces/{turn['trace_id']}"
    )
    assert trace.status_code == 200
    body = trace.json()
    assert body["interpretations"][0]["type"] == "SOCIAL_ACT"
    assert "fr-rule-greeting" in body["triggered_rules"]
    assert body["candidate_actions"]
    assert body["output_construction_id"] in {
        "fr-output-greeting",
        "fr-output-interlocutor-state",
    }
