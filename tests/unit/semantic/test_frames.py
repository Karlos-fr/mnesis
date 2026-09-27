"""
Tests des représentations sémantiques génériques.

Rôle :
    Vérifier que Mnesis peut représenter propositions et actes sociaux sans
    introduire de classes liées à une langue ou à une intention métier.
"""

import pytest
from pydantic import ValidationError

from mnesis.semantic.frames import SemanticFrame


def test_semantic_frame_represents_is_a_proposition() -> None:
    """Vérifie qu'une proposition IS_A peut être représentée génériquement."""
    frame = SemanticFrame(
        type="PROPOSITION",
        slots={"predicate": "IS_A", "subject": "chat", "object": "animal"},
        confidence=0.92,
        provenance=["construction:test-is-a"],
    )

    assert frame.type == "PROPOSITION"
    assert frame.slots["predicate"] == "IS_A"
    assert frame.slots["subject"] == "chat"
    assert frame.slots["object"] == "animal"


def test_semantic_frame_represents_social_act() -> None:
    """Vérifie qu'un acte social reste un frame générique."""
    frame = SemanticFrame(type="SOCIAL_ACT", slots={"act": "GREETING"})

    assert frame.slots == {"act": "GREETING"}


def test_semantic_frame_rejects_confidence_outside_unit_interval() -> None:
    """Vérifie que la confiance d'un frame reste bornée dans [0, 1]."""
    with pytest.raises(ValidationError):
        SemanticFrame(type="EVENT", slots={}, confidence=1.1)


def test_semantic_frame_serialization_is_stable() -> None:
    """Vérifie que le frame est sérialisable pour stockage et traçage."""
    frame = SemanticFrame(
        type="QUERY",
        slots={"kind": "DEFINITION", "target": "chat"},
        confidence=0.7,
        provenance=["construction:query-definition"],
    )

    assert SemanticFrame.model_validate(frame.model_dump()) == frame
