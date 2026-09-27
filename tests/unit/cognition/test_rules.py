"""
Tests du moteur de règles déclaratives.

Rôle :
    Vérifier que les actions candidates proviennent de règles décrites en
    données, sans branchement métier dans le moteur cognitif.
"""

import pytest
from pydantic import ValidationError

from mnesis.cognition.rules import DeclarativeRule, RuleCondition, RuleEngine
from mnesis.semantic.frames import SemanticFrame


def test_greeting_rule_proposes_social_response_from_data() -> None:
    """Vérifie qu'une règle de donnée transforme un acte social en action candidate."""
    rule = DeclarativeRule(
        id="respond-to-greeting",
        conditions=[
            RuleCondition(source="frame", path="type", operator="eq", value="SOCIAL_ACT"),
            RuleCondition(source="frame", path="slots.act", operator="eq", value="GREETING"),
        ],
        action_type="SOCIAL_RESPONSE",
        payload={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        base_score=0.8,
    )
    frame = SemanticFrame(type="SOCIAL_ACT", slots={"act": "GREETING"})

    results = RuleEngine().evaluate([frame], {}, [rule])

    assert len(results) == 1
    assert results[0].action_type == "SOCIAL_RESPONSE"
    assert results[0].payload == {"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}}
    assert results[0].base_score == 0.8


def test_rule_can_use_numeric_state_threshold() -> None:
    """Vérifie qu'une condition peut lire génériquement un chemin d'état numérique."""
    rule = DeclarativeRule(
        id="curious-follow-up",
        conditions=[
            RuleCondition(
                source="state",
                path="personality.curiosity",
                operator="gte",
                value=0.8,
            )
        ],
        action_type="ASK",
        payload={"type": "QUERY", "slots": {"kind": "INTERLOCUTOR_STATE"}},
        base_score=0.5,
    )

    results = RuleEngine().evaluate(
        [SemanticFrame(type="EVENT")],
        {"personality": {"curiosity": 0.9}},
        [rule],
    )

    assert [result.action_type for result in results] == ["ASK"]


def test_unknown_rule_operator_is_rejected_at_validation() -> None:
    """Vérifie qu'une règle mal formée est rejetée avant son exécution."""
    with pytest.raises(ValidationError):
        RuleCondition(
            source="frame",
            path="type",
            operator="contains_magic",
            value="EVENT",
        )
