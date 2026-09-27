"""
Tests du pont générique vers la mémoire sémantique.

Rôle :
    Vérifier qu'un frame relationnel peut être persisté puis récupéré sans que
    le service conversationnel connaisse une intention linguistique.
"""

from mnesis.cognition.semantic_memory import SemanticMemory
from mnesis.domain.instances import MnesisInstance
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.semantic.frames import SemanticFrame


def _memory() -> tuple[MnesisInstance, SemanticMemory]:
    """Construit une mémoire sémantique isolée pour les tests."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    instance = instances.create(MnesisInstance.create("Test"))
    return instance, SemanticMemory(KnowledgeRepository(database.session_factory))


def test_store_and_retrieve_relation_through_generic_payload() -> None:
    """Vérifie la persistance et le rappel d'une relation sémantique générique."""
    instance, memory = _memory()
    frame = SemanticFrame(
        type="PROPOSITION",
        slots={"predicate": "IS_A", "subject": "chat", "object": "animal"},
        confidence=0.95,
    )
    learned = memory.store(instance.id, frame)
    recalled = memory.retrieve(
        instance.id,
        {"subject_label": "chat", "predicate": "IS_A"},
    )
    assert len(learned) == 3
    assert recalled is not None
    assert recalled.type == "PROPOSITION"
    assert recalled.slots == {
        "predicate": "IS_A",
        "subject": "chat",
        "object": "animal",
    }


def test_retrieve_returns_none_when_relation_is_unknown() -> None:
    """Vérifie qu'une absence de connaissance reste explicite."""
    instance, memory = _memory()
    assert memory.retrieve(
        instance.id,
        {"subject_label": "inconnu", "predicate": "IS_A"},
    ) is None
