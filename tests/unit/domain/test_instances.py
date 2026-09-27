"""
Tests du modèle d'instance Mnesis.

Rôle :
    Vérifier l'identité d'une instance et l'indépendance de ses états internes.
"""

from uuid import uuid4

from mnesis.domain.affect import AffectState, Personality
from mnesis.domain.instances import MnesisInstance


def test_instance_preserves_identity_and_locale() -> None:
    """Vérifie qu'une instance conserve son identité et sa langue."""
    instance_id = uuid4()
    personality = Personality()
    affect = AffectState()

    instance = MnesisInstance(
        id=instance_id,
        name="Personnel",
        locale="fr-FR",
        personality=personality,
        affect=affect,
    )

    assert instance.id == instance_id
    assert instance.name == "Personnel"
    assert instance.locale == "fr-FR"


def test_two_instances_keep_distinct_affect_objects() -> None:
    """Vérifie que deux instances ne partagent pas leur état affectif."""
    first = MnesisInstance.create(name="A", locale="fr-FR")
    second = MnesisInstance.create(name="B", locale="fr-FR")

    assert first.affect is not second.affect
    assert first.personality is not second.personality
