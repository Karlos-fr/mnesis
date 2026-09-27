"""
Tests des paquets de connaissances Mnesis.

Rôle :
    Vérifier le chargement versionné de core-fr et la traçabilité de son origine.
"""

from pathlib import Path

from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import KnowledgeOrigin
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.knowledge_packs import deploy_knowledge_pack, load_knowledge_pack
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository

CORE_FR = Path("knowledge/core-fr")


def test_core_fr_loads_versioned_minimal_french_knowledge() -> None:
    """Vérifie que core-fr expose les éléments linguistiques minimum attendus."""
    pack = load_knowledge_pack(CORE_FR)
    assert pack.manifest.name == "core-fr"
    assert pack.manifest.version == "0.1.0"
    assert pack.manifest.locale == "fr-FR"
    assert any(item["lemma"] == "bonjour" for item in pack.lexicon)
    assert any(item["intent"] == "SALUER" for item in pack.constructions)
    assert "SALUER" in pack.responses


def test_deployed_claims_keep_knowledge_pack_origin() -> None:
    """Vérifie qu'une connaissance déployée reste identifiable comme issue d'un pack."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    knowledge = KnowledgeRepository(database.session_factory)
    instance = instances.create(MnesisInstance.create("Test"))
    pack = load_knowledge_pack(CORE_FR)
    result = deploy_knowledge_pack(instance.id, pack, knowledge)
    claims = knowledge.list_claims(instance.id)
    assert result.claims_deployed >= 1
    assert claims
    assert all(claim.origin is KnowledgeOrigin.KNOWLEDGE_PACK for claim in claims)
