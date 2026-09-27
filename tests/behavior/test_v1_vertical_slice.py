"""
Scénario vertical de référence pendant le refactor cognitif.

Rôle :
    Préserver les garanties de mémoire, apprentissage, doute et isolation pendant
    la migration, avant le scénario end-to-end définitif de la tâche 16.
"""

from pathlib import Path

from mnesis.application.learning import DictionaryEntry, LexicalLearningService
from mnesis.cognition.semantic_memory import SemanticMemory
from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, KnowledgeOrigin
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.knowledge_packs import deploy_knowledge_pack, load_knowledge_pack
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository


class VerticalDictionarySource:
    """Source dictionnaire déterministe du scénario vertical."""

    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """Retourne uniquement la définition contrôlée du mot arboricole."""
        if word.casefold() != "arboricole":
            return None
        return DictionaryEntry(
            word="arboricole",
            lemma="arboricole",
            part_of_speech="adjectif",
            definition="Qui vit dans les arbres.",
            source_uri="dictionary://vertical/arboricole",
        )


def test_v1_vertical_slice() -> None:
    """Préserve les garanties de la V1 pendant la migration du cycle."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    knowledge = KnowledgeRepository(database.session_factory)
    memories = MemoryRepository(database.session_factory)
    traces = TraceRepository(database.session_factory)
    personal = instances.create(MnesisInstance.create("Personnel"))
    isolated = instances.create(MnesisInstance.create("Isolée"))
    pack = load_knowledge_pack(Path("knowledge/core-fr"))

    deployment = deploy_knowledge_pack(personal.id, pack, knowledge)
    assert deployment.claims_deployed >= 1
    assert knowledge.find_concept(personal.id, "salutation") is not None
    assert knowledge.find_lexeme(personal.id, "bonjour") is not None

    learning = LexicalLearningService(knowledge, VerticalDictionarySource())
    assert knowledge.find_lexeme(personal.id, "arboricole") is None
    learned = learning.learn_unknown_word(personal.id, "arboricole")
    assert learned.success is True
    assert knowledge.find_lexeme(personal.id, "arboricole") is not None
    assert any(
        claim.origin is KnowledgeOrigin.DICTIONARY
        for claim in knowledge.list_claims(personal.id)
    )

    subject = knowledge.add_concept(
        personal.id,
        Concept(kind="entity", label="test-conflit"),
    )
    first = knowledge.add_concept(
        personal.id,
        Concept(kind="category", label="mammifère"),
    )
    second = knowledge.add_concept(
        personal.id,
        Concept(kind="category", label="oiseau"),
    )
    knowledge.add_claim(
        personal.id,
        Claim(
            subject_id=subject.id,
            predicate="IS_A",
            object_id=first.id,
            confidence=0.99,
            status=ClaimStatus.TRUSTED,
            origin=KnowledgeOrigin.KNOWLEDGE_PACK,
        ),
    )
    knowledge.add_claim(
        personal.id,
        Claim(
            subject_id=subject.id,
            predicate="IS_A",
            object_id=second.id,
            confidence=0.7,
            status=ClaimStatus.TENTATIVE,
            origin=KnowledgeOrigin.USER,
        ),
    )
    recalled = SemanticMemory(knowledge).retrieve(
        personal.id,
        {"subject_label": "test-conflit", "predicate": "IS_A"},
    )
    assert recalled is not None
    assert recalled.type == "UNCERTAIN_PROPOSITION"

    assert memories.recent(personal.id, 20) == []
    assert traces.get(personal.id, personal.id) is None
    assert knowledge.list_claims(isolated.id) == []
    assert knowledge.find_lexeme(isolated.id, "arboricole") is None
