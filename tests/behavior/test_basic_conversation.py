"""
Tests comportementaux de la conversation Mnesis.

Rôle :
    Vérifier qu'une instance peut saluer, mémoriser une relation simple et la
    réutiliser dans un échange ultérieur sans LLM.
"""

from pathlib import Path
from mnesis.application.conversation import ConversationService
from mnesis.infrastructure.knowledge_packs import load_knowledge_pack
from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.domain.instances import MnesisInstance
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository


def _service() -> tuple[MnesisInstance, ConversationService]:
    """Construit un moteur conversationnel isolé pour les tests."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    instance = instances.create(MnesisInstance.create("Test"))
    pack = load_knowledge_pack(Path("knowledge/core-fr"))
    return instance, ConversationService(
        knowledge=KnowledgeRepository(database.session_factory),
        memories=MemoryRepository(database.session_factory),
        traces=TraceRepository(database.session_factory),
        lexicon=Lexicon.from_words({item["surface"] for item in pack.lexicon}),
        constructions=ConstructionSet.default_french(),
        responses=pack.responses,
    )


def test_greeting_returns_french_response() -> None:
    """Vérifie qu'une salutation reçoit une réponse française issue du socle."""
    instance, service = _service()
    turn = service.handle(instance.id, "Bonjour")
    assert turn.intent == "SALUER"
    assert turn.response_text == "Bonjour."
    assert turn.trace_id is not None


def test_definition_is_stored_and_recalled_later() -> None:
    """Vérifie qu'une relation enseignée pendant la conversation est réutilisée."""
    instance, service = _service()
    learned = service.handle(instance.id, "chat est un animal")
    recalled = service.handle(instance.id, "Qu'est-ce qu'un chat ?")
    assert learned.response_text == "D'accord. Je retiens qu'un chat est un animal."
    assert recalled.response_text == "Un chat est un animal."
    assert len(service.memories.recent(instance.id, 10)) == 2
