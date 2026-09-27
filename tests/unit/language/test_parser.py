"""
Tests du parseur français contrôlé.

Rôle :
    Vérifier l'interprétation des premières constructions linguistiques de Mnesis.
"""

import pytest

from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.language.parser import parse_utterance


def _lexicon() -> Lexicon:
    """Construit le lexique minimal utilisé par les tests du parseur."""
    return Lexicon.from_words({"bonjour", "chat", "animal", "un", "est", "qu'est-ce", "que", "?"})


def _constructions() -> ConstructionSet:
    """Construit les constructions minimales utilisées par les tests."""
    return ConstructionSet.default_french()


def test_parser_recognizes_greeting() -> None:
    """Vérifie la reconnaissance d'une salutation."""
    parsed = parse_utterance("Bonjour", _lexicon(), _constructions())
    assert parsed.intent == "SALUER"


def test_parser_extracts_is_a_relation() -> None:
    """Vérifie l'extraction d'une relation X EST_UN Y."""
    parsed = parse_utterance("chat est un animal", _lexicon(), _constructions())
    assert parsed.intent == "DEFINIR"
    assert parsed.semantic_frames == [{"subject": "chat", "predicate": "EST_UN", "object": "animal"}]


def test_parser_recognizes_definition_question() -> None:
    """Vérifie la reconnaissance d'une question de définition."""
    parsed = parse_utterance("Qu'est-ce qu'un chat ?", _lexicon(), _constructions())
    assert parsed.intent == "DEMANDER_DEFINITION"
    assert parsed.semantic_frames[0]["concept"] == "chat"


def test_parser_reports_unknown_word() -> None:
    """Vérifie qu'un mot inconnu reste visible pour l'apprentissage ultérieur."""
    parsed = parse_utterance("bonjour axolotl", _lexicon(), _constructions())
    assert "axolotl" in parsed.unknown_tokens


def test_parser_rejects_blank_input() -> None:
    """Vérifie qu'une entrée vide n'est jamais transformée en événement cognitif."""
    with pytest.raises(ValueError, match="vide"):
        parse_utterance("   ", _lexicon(), _constructions())
