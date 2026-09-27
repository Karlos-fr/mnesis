"""
Tests des modèles de personnalité et d'affect.

Rôle :
    Vérifier que toutes les dimensions cognitives restent dans l'intervalle [0, 1].
"""

import pytest
from pydantic import ValidationError

from mnesis.domain.affect import AffectState, Personality


def test_personality_accepts_values_inside_unit_interval() -> None:
    """Vérifie qu'une personnalité valide peut être créée."""
    personality = Personality(curiosity=0.8, humor=0.4)

    assert personality.curiosity == 0.8
    assert personality.humor == 0.4


def test_personality_rejects_value_above_one() -> None:
    """Vérifie qu'un trait supérieur à 1 est rejeté."""
    with pytest.raises(ValidationError):
        Personality(curiosity=1.1)


def test_affect_rejects_negative_value() -> None:
    """Vérifie qu'une émotion négative au sens numérique est rejetée."""
    with pytest.raises(ValidationError):
        AffectState(joy=-0.1)
