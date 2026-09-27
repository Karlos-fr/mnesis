"""
Tests de la réalisation linguistique déclarative.

Rôle :
    Vérifier qu'un frame sémantique peut être réalisé en texte uniquement à
    partir de constructions de sortie décrites en données.
"""

from mnesis.language.realization import LanguageRealizer, OutputConstruction
from mnesis.semantic.frames import SemanticFrame


def test_output_construction_realizes_greeting_without_code_change() -> None:
    """Vérifie qu'une salutation de sortie est entièrement définie par donnée."""
    construction = OutputConstruction(
        id="fr-greeting-output",
        language="fr",
        semantic_pattern={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        templates=["Bonjour."],
        confidence=0.99,
        origin="test",
    )

    text = LanguageRealizer().realize(
        SemanticFrame(type="SOCIAL_ACT", slots={"act": "GREETING"}),
        [construction],
        {},
    )

    assert text == "Bonjour."


def test_output_construction_substitutes_frame_slots() -> None:
    """Vérifie que les slots du frame alimentent un patron textuel générique."""
    construction = OutputConstruction(
        id="fr-is-a-output",
        language="fr",
        semantic_pattern={"type": "PROPOSITION", "slots": {"predicate": "IS_A"}},
        templates=["Un {subject} est un {object}."],
        confidence=0.95,
        origin="test",
    )
    frame = SemanticFrame(
        type="PROPOSITION",
        slots={"predicate": "IS_A", "subject": "chat", "object": "animal"},
    )

    assert LanguageRealizer().realize(frame, [construction], {}) == "Un chat est un animal."


def test_first_equally_ranked_template_is_selected_deterministically() -> None:
    """Vérifie que la V1 produit toujours la première variante à score égal."""
    construction = OutputConstruction(
        id="variants",
        language="fr",
        semantic_pattern={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        templates=["Bonjour.", "Salut."],
        confidence=0.8,
        origin="test",
    )

    frame = SemanticFrame(type="SOCIAL_ACT", slots={"act": "GREETING"})
    assert LanguageRealizer().realize(frame, [construction], {}) == "Bonjour."
