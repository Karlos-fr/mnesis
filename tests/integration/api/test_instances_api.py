"""
Tests HTTP de gestion des instances Mnesis.

Rôle :
    Vérifier la création, la consultation et le déploiement du socle via l'API.
"""

from uuid import UUID

from fastapi.testclient import TestClient

from mnesis.api.app import create_app


def test_create_and_get_instance() -> None:
    """Vérifie qu'une instance créée via HTTP peut être relue."""
    client = TestClient(create_app("sqlite+pysqlite:///:memory:"))

    created = client.post(
        "/api/v1/instances",
        json={"name": "Personnel", "locale": "fr-FR"},
    )

    assert created.status_code == 201
    instance_id = created.json()["id"]
    fetched = client.get(f"/api/v1/instances/{instance_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Personnel"


def test_core_fr_can_be_explicitly_deployed_to_instance() -> None:
    """Vérifie que l'API déploie volontairement le socle français dans une instance."""
    app = create_app("sqlite+pysqlite:///:memory:")
    client = TestClient(app)
    instance_id = client.post(
        "/api/v1/instances",
        json={"name": "Personnel", "locale": "fr-FR"},
    ).json()["id"]

    deployed = client.post(
        f"/api/v1/instances/{instance_id}/knowledge-packs/core-fr"
    )

    assert deployed.status_code == 200
    assert deployed.json()["concepts_deployed"] >= 1
    assert deployed.json()["lexemes_deployed"] >= 1
    assert deployed.json()["claims_deployed"] >= 1
    knowledge = app.state.services.knowledge
    assert knowledge.find_concept(UUID(instance_id), "salutation") is not None
    assert knowledge.find_lexeme(UUID(instance_id), "bonjour") is not None
