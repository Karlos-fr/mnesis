"""
Scénario vertical de référence de Mnesis V1.

Rôle :
    Prouver dans un seul scénario que le socle français, l'apprentissage lexical,
    le doute, la mémoire, les traces et l'isolation fonctionnent ensemble.
"""

from pathlib import Path

from mnesis.application.conversation import ConversationService
from mnesis.application.learning import DictionaryEntry, LexicalLearningService
from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import KnowledgeOrigin
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.knowledge_packs import deploy_knowledge_pack, load_knowledge_pack
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository
from mnesis.language.constructions import ConstructionSet, Lexicon


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
    """Valide la première tranche fonctionnelle complète sans LLM."""
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
    service = ConversationService(
        knowledge=knowledge,
        memories=memories,
        traces=traces,
        lexicon=Lexicon.from_words({item["surface"] for item in pack.lexicon}),
        constructions=ConstructionSet.default_french(),
        responses=pack.responses,
        learning=learning,
    )

    assert service.handle(personal.id, "Bonjour").response_text == "Bonjour."

    assert knowledge.find_lexeme(personal.id, "arboricole") is None
    learned_turn = service.handle(personal.id, "arboricole")
    assert learned_turn.learned_items
    learned = knowledge.find_lexeme(personal.id, "arboricole")
    assert learned is not None
    assert any(
        claim.origin is KnowledgeOrigin.DICTIONARY
        for claim in knowledge.list_claims(personal.id)
    )

    recalled = service.handle(personal.id, "Qu'est-ce qu'un arboricole ?")
    assert "vit dans les arbres" in recalled.response_text.casefold()

    service.handle(personal.id, "salutation est un animal")
    doubt = service.handle(personal.id, "Qu'est-ce qu'une salutation ?")
    assert "pas certain" in doubt.response_text
    assert "acte_conversationnel" in doubt.response_text

    assert memories.recent(personal.id, 20)
    assert traces.get(personal.id, doubt.trace_id) is not None
    assert knowledge.list_claims(isolated.id) == []
    assert knowledge.find_lexeme(isolated.id, "arboricole") is None
