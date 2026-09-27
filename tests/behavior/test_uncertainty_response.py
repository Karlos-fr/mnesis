"""
Tests du doute exprimé en conversation.

Rôle :
    Vérifier qu'une contradiction entre deux connaissances est traduite en
    incertitude explicite dans la réponse textuelle.
"""

from pathlib import Path
from mnesis.application.conversation import ConversationService
from mnesis.infrastructure.knowledge_packs import load_knowledge_pack
from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, KnowledgeOrigin
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository


def test_conflicting_definitions_produce_uncertainty() -> None:
    """Vérifie qu'une question sur une croyance conflictuelle exprime le doute."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    instance = instances.create(MnesisInstance.create("Test"))
    knowledge = KnowledgeRepository(database.session_factory)
    subject = knowledge.add_concept(instance.id, Concept(kind="entity", label="chauve-souris"))
    mammal = knowledge.add_concept(instance.id, Concept(kind="category", label="mammifère"))
    bird = knowledge.add_concept(instance.id, Concept(kind="category", label="oiseau"))
    knowledge.add_claim(instance.id, Claim(subject_id=subject.id, predicate="EST_UN", object_id=mammal.id, confidence=0.99, status=ClaimStatus.TRUSTED, origin=KnowledgeOrigin.KNOWLEDGE_PACK))
    knowledge.add_claim(instance.id, Claim(subject_id=subject.id, predicate="EST_UN", object_id=bird.id, confidence=0.7, status=ClaimStatus.TENTATIVE, origin=KnowledgeOrigin.USER))
    pack = load_knowledge_pack(Path("knowledge/core-fr"))
    service = ConversationService(knowledge=knowledge, memories=MemoryRepository(database.session_factory), traces=TraceRepository(database.session_factory), lexicon=Lexicon.from_words({item["surface"] for item in pack.lexicon}), constructions=ConstructionSet.default_french(), responses=pack.responses)
    turn = service.handle(instance.id, "Qu'est-ce qu'une chauve-souris ?")
    assert "pas certain" in turn.response_text
    assert "mammifère" in turn.response_text
