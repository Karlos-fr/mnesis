"""
Tests du moteur générique de sélection d'actions.

Rôle :
    Vérifier que le score des actions dépend uniquement des données de règle et
    de chemins génériques dans l'état cognitif.
"""

from mnesis.cognition.actions import ActionEngine
from mnesis.cognition.rules import RuleResult


def test_action_score_uses_declared_state_modifiers() -> None:
    """Vérifie qu'un bonus de curiosité/extraversion est appliqué par données."""
    result = RuleResult(
        rule_id="follow-up",
        action_type="ASK",
        payload={"type": "QUERY", "slots": {"kind": "INTERLOCUTOR_STATE"}},
        base_score=0.4,
        modifiers={
            "personality.curiosity": 0.3,
            "personality.extraversion": 0.2,
        },
    )

    ranked = ActionEngine().rank(
        [result],
        {"personality": {"curiosity": 0.8, "extraversion": 0.5}},
    )

    assert ranked[0].score == 0.74
    assert ranked[0].action_type == "ASK"


def test_action_selection_is_stable_when_scores_are_equal() -> None:
    """Vérifie qu'une égalité de score conserve l'ordre des propositions."""
    first = RuleResult(rule_id="first", action_type="A", payload={}, base_score=0.5)
    second = RuleResult(rule_id="second", action_type="B", payload={}, base_score=0.5)

    selected = ActionEngine().select([first, second], {})

    assert selected.rule_id == "first"
