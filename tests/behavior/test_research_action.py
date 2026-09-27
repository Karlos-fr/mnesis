"""
Tests de l'action cognitive générique RESEARCH.

Rôle :
    Vérifier qu'un mot isolé inconnu crée une lacune de connaissance, déclenche
    une recherche lexicale puis devient une connaissance réutilisable.
"""

from mnesis.api.app import create_app
from mnesis.application.learning import DictionaryEntry
from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import KnowledgeOrigin


class FakeDictionarySource:
    """Source lexicale déterministe utilisée sans accès réseau."""

    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """Retourne une définition uniquement pour arboricole."""
        if word.casefold() != "arboricole":
            return None
        return DictionaryEntry(
            word="arboricole",
            lemma="arboricole",
            part_of_speech="adjectif",
            definition="Qui vit dans les arbres.",
            source_uri="dictionary://test/arboricole",
        )


def test_unknown_word_triggers_research_then_becomes_reusable() -> None:
    """Vérifie le cycle KnowledgeGap → RESEARCH → apprentissage → rappel."""
    app = create_app(
        "sqlite+pysqlite:///:memory:",
        dictionary_source=FakeDictionarySource(),
    )
    services = app.state.services
    instance = services.instances.create(MnesisInstance.create("Test"))

    assert services.knowledge.find_lexeme(instance.id, "arboricole") is None

    learned = services.conversation.handle(instance.id, "arboricole")

    assert "appris" in learned.response_text
    assert services.knowledge.find_lexeme(instance.id, "arboricole") is not None
    assert any(
        claim.origin is KnowledgeOrigin.DICTIONARY
        for claim in services.knowledge.list_claims(instance.id)
    )

    recalled = services.conversation.handle(
        instance.id,
        "Qu'est-ce qu'un arboricole ?",
    )
    assert "vit dans les arbres" in recalled.response_text.casefold()
