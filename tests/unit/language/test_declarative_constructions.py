"""
Tests des constructions linguistiques déclaratives.

Rôle :
    Vérifier que de nouvelles formes linguistiques produisent des frames
    sémantiques sans ajouter de logique métier au moteur Python.
"""

from mnesis.language.constructions import ConstructionSet, InputConstruction, Lexicon
from mnesis.language.interpreter import LanguageInterpreter


def test_literal_construction_can_be_added_as_data() -> None:
    """Vérifie que « coucou » peut devenir une salutation par simple donnée."""
    construction = InputConstruction(
        id="test-coucou",
        language="fr",
        pattern=[{"literal": "coucou"}],
        semantics={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        confidence=0.9,
        origin="test",
    )
    constructions = ConstructionSet(declarative_items=(construction,))

    frames = LanguageInterpreter().interpret(
        "Coucou",
        constructions,
        Lexicon.from_words({"coucou"}),
    )

    assert len(frames) == 1
    assert frames[0].type == "SOCIAL_ACT"
    assert frames[0].slots == {"act": "GREETING"}
    assert frames[0].provenance == ["construction:test-coucou"]


def test_variable_capture_is_substituted_into_semantics() -> None:
    """Vérifie qu'une variable de forme est injectée dans le frame produit."""
    construction = InputConstruction(
        id="test-is-a",
        language="fr",
        pattern=[
            {"variable": "subject"},
            {"literal": "est"},
            {"literal": "un"},
            {"variable": "object"},
        ],
        semantics={
            "type": "PROPOSITION",
            "slots": {"predicate": "IS_A", "subject": "$subject", "object": "$object"},
        },
        confidence=0.95,
        origin="test",
    )

    frames = LanguageInterpreter().interpret(
        "chat est un animal",
        ConstructionSet(declarative_items=(construction,)),
        Lexicon.from_words({"chat", "est", "un", "animal"}),
    )

    assert frames[0].slots == {
        "predicate": "IS_A",
        "subject": "chat",
        "object": "animal",
    }


def test_two_matching_constructions_keep_two_candidates() -> None:
    """Vérifie qu'une ambiguïté conserve toutes les interprétations candidates."""
    first = InputConstruction(
        id="first",
        language="fr",
        pattern=[{"literal": "salut"}],
        semantics={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        confidence=0.8,
        origin="test",
    )
    second = InputConstruction(
        id="second",
        language="fr",
        pattern=[{"literal": "salut"}],
        semantics={"type": "LEXICAL_EVENT", "slots": {"word": "salut"}},
        confidence=0.5,
        origin="test",
    )

    frames = LanguageInterpreter().interpret(
        "salut",
        ConstructionSet(declarative_items=(first, second)),
        Lexicon.from_words({"salut"}),
    )

    assert [frame.type for frame in frames] == ["SOCIAL_ACT", "LEXICAL_EVENT"]
