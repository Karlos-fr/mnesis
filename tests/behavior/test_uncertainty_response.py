"""
Tests du doute exprimé en conversation.

Rôle :
    Vérifier qu'une contradiction en mémoire sémantique devient une proposition
    incertaine réalisée par core-fr, sans condition métier dans le service.
"""

from mnesis.api.app import create_app
from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, KnowledgeOrigin


def test_conflicting_definitions_produce_uncertainty() -> None:
    """Vérifie qu'une relation conflictuelle est verbalisée avec un doute."""
    app = create_app("sqlite+pysqlite:///:memory:")
    services = app.state.services
    instance = services.instances.create(MnesisInstance.create("Test"))
    knowledge = services.knowledge
    subject = knowledge.add_concept(
        instance.id,
        Concept(kind="entity", label="chauve-souris"),
    )
    mammal = knowledge.add_concept(
        instance.id,
        Concept(kind="category", label="mammifère"),
    )
    bird = knowledge.add_concept(
        instance.id,
        Concept(kind="category", label="oiseau"),
    )
    knowledge.add_claim(
        instance.id,
        Claim(
            subject_id=subject.id,
            predicate="IS_A",
            object_id=mammal.id,
            confidence=0.99,
            status=ClaimStatus.TRUSTED,
            origin=KnowledgeOrigin.KNOWLEDGE_PACK,
        ),
    )
    knowledge.add_claim(
        instance.id,
        Claim(
            subject_id=subject.id,
            predicate="IS_A",
            object_id=bird.id,
            confidence=0.7,
            status=ClaimStatus.TENTATIVE,
            origin=KnowledgeOrigin.USER,
        ),
    )
    turn = services.conversation.handle(
        instance.id,
        "Qu'est-ce qu'une chauve-souris ?",
    )
    assert "pas certain" in turn.response_text
    assert "mammifère" in turn.response_text
