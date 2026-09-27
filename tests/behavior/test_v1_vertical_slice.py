"""Scénario vertical final du cycle cognitif apprenable de Mnesis.

Rôle :
    Démontrer que les capacités conversationnelles viennent des données, des
    règles et de l'apprentissage, et non de branches métier codées en Python.
"""

from pathlib import Path

from mnesis.api.app import create_app
from mnesis.application.construction_learning import ConstructionLearningService
from mnesis.application.learning import DictionaryEntry
from mnesis.domain.affect import AffectState, Personality
from mnesis.domain.instances import MnesisInstance
from mnesis.infrastructure.knowledge_packs import deploy_knowledge_pack, load_knowledge_pack
from mnesis.language.constructions import InputConstruction
from mnesis.semantic.frames import SemanticFrame


class VerticalDictionarySource:
    """Source lexicale déterministe utilisée par le scénario vertical."""

    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """Retourne une définition uniquement pour le mot arboricole."""
        if word.casefold() != "arboricole":
            return None
        return DictionaryEntry(
            word="arboricole",
            lemma="arboricole",
            part_of_speech="adjectif",
            definition="Qui vit dans les arbres.",
            source_uri="dictionary://vertical/arboricole",
        )


def test_v1_vertical_slice_uses_learnable_cognitive_cycle() -> None:
    """Valide le cycle déclaratif, l'apprentissage, l'isolation et la trace."""
    app = create_app(
        "sqlite+pysqlite:///:memory:",
        dictionary_source=VerticalDictionarySource(),
    )
    services = app.state.services
    personal = services.instances.create(MnesisInstance.create("Personnel"))
    isolated = services.instances.create(MnesisInstance.create("Isolée"))
    pack = load_knowledge_pack(Path("knowledge/core-fr"))

    deployment = deploy_knowledge_pack(personal.id, pack, services.knowledge)
    assert deployment.concepts_deployed >= 1
    assert deployment.lexemes_deployed >= 1
    assert deployment.claims_deployed >= 1

    greeting = services.conversation.handle(personal.id, "Bonjour")
    assert greeting.response_text == "Bonjour."

    stored = services.conversation.handle(personal.id, "chat est un animal")
    assert stored.response_text == "Un chat est un animal."
    recalled = services.conversation.handle(personal.id, "Qu'est-ce qu'un chat ?")
    assert recalled.response_text == "Un chat est un animal."

    services.constructions.add(
        personal.id,
        InputConstruction(
            id="local-coucou",
            language="fr",
            pattern=[{"literal": "coucou"}],
            semantics={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
            confidence=0.9,
            origin="learned:test",
        ),
    )
    assert services.conversation.handle(personal.id, "Coucou").response_text == "Bonjour."

    construction_learning = ConstructionLearningService(services.constructions)
    taught = construction_learning.teach(
        personal.id,
        "Ça roule ?",
        SemanticFrame(type="QUERY", slots={"kind": "INTERLOCUTOR_STATE"}),
        source="user://teaching",
    )
    assert "pas certain" in services.conversation.handle(personal.id, "Ça roule ?").response_text
    construction_learning.reinforce(personal.id, taught.id, "user://confirmation")
    assert services.conversation.handle(personal.id, "Ça roule ?").response_text == "Comment vas-tu ?"
    assert "pas certain" in services.conversation.handle(isolated.id, "Ça roule ?").response_text

    learned_word = services.conversation.handle(personal.id, "arboricole")
    assert "appris" in learned_word.response_text
    lexical_recall = services.conversation.handle(personal.id, "Qu'est-ce qu'un arboricole ?")
    assert "vit dans les arbres" in lexical_recall.response_text.casefold()

    services.conversation.handle(personal.id, "salutation est un animal")
    doubt = services.conversation.handle(personal.id, "Qu'est-ce qu'une salutation ?")
    assert "pas certain" in doubt.response_text
    assert "acte_conversationnel" in doubt.response_text

    curious = services.instances.create(
        MnesisInstance(
            id=MnesisInstance.create("tmp").id,
            name="Curieuse",
            locale="fr-FR",
            personality=Personality(curiosity=0.95, extraversion=0.8),
            affect=AffectState(curiosity=0.95),
        )
    )
    curious_turn = services.conversation.handle(curious.id, "Bonjour")
    assert curious_turn.response_text == "Comment vas-tu ?"

    trace = services.traces.get(personal.id, doubt.trace_id)
    assert trace is not None
    assert trace.interpretations
    assert trace.triggered_rules
    assert trace.candidate_actions
    assert trace.output_construction_id is not None

    assert services.knowledge.find_lexeme(isolated.id, "arboricole") is None
