"""
Tests du service d'apprentissage lexical.

Rôle :
    Prouver qu'un mot réellement absent peut être acquis depuis une source
    dictionnaire puis conservé avec sa provenance.
"""

from mnesis.application.learning import DictionaryEntry, LexicalLearningService
from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import KnowledgeOrigin
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository


class FakeDictionarySource:
    """Source déterministe utilisée pour tester l'apprentissage sans réseau."""
    def __init__(self, entry: DictionaryEntry | None) -> None:
        self.entry = entry
    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """Retourne l'entrée configurée, indépendamment du réseau."""
        return self.entry


def _repositories() -> tuple[MnesisInstance, KnowledgeRepository]:
    """Prépare une instance et son dépôt dans une base SQLite isolée."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    instance = instances.create(MnesisInstance.create("Test"))
    return instance, KnowledgeRepository(database.session_factory)


def test_unknown_word_is_learned_with_dictionary_provenance() -> None:
    """Vérifie l'acquisition réelle d'un mot auparavant absent."""
    instance, repository = _repositories()
    source = FakeDictionarySource(DictionaryEntry(word="arboricole", lemma="arboricole", part_of_speech="adjectif", definition="Qui vit dans les arbres.", source_uri="https://fr.wiktionary.org/wiki/arboricole"))
    service = LexicalLearningService(repository, source)
    assert repository.find_lexeme(instance.id, "arboricole") is None
    result = service.learn_unknown_word(instance.id, "arboricole")
    learned = repository.find_lexeme(instance.id, "arboricole")
    assert result.success is True
    assert learned is not None
    assert learned.lemma == "arboricole"
    assert any(claim.origin is KnowledgeOrigin.DICTIONARY for claim in repository.list_claims(instance.id))


def test_failed_dictionary_lookup_creates_no_knowledge() -> None:
    """Vérifie qu'une source vide ne fabrique aucune connaissance."""
    instance, repository = _repositories()
    result = LexicalLearningService(repository, FakeDictionarySource(None)).learn_unknown_word(instance.id, "motintrouvable")
    assert result.success is False
    assert repository.find_lexeme(instance.id, "motintrouvable") is None
    assert repository.list_claims(instance.id) == []
