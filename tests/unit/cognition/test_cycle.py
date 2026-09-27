"""
Tests du cycle cognitif générique.

Rôle :
    Vérifier que l'orchestration complète fonctionne à partir de données sans
    branchement métier dans le cycle lui-même.
"""

from mnesis.cognition.actions import ActionEngine
from mnesis.cognition.cycle import CognitiveCycle, CognitiveEvent
from mnesis.cognition.procedures import ProcedureExecutor
from mnesis.cognition.rules import DeclarativeRule, RuleCondition, RuleEngine
from mnesis.language.constructions import ConstructionSet, InputConstruction, Lexicon
from mnesis.language.interpreter import LanguageInterpreter
from mnesis.language.realization import LanguageRealizer, OutputConstruction


def _cycle() -> CognitiveCycle:
    """Construit un cycle cognitif avec des composants génériques réels."""
    return CognitiveCycle(
        interpreter=LanguageInterpreter(),
        rule_engine=RuleEngine(),
        action_engine=ActionEngine(),
        procedure_executor=ProcedureExecutor(),
        realizer=LanguageRealizer(),
    )


def test_cycle_handles_greeting_from_data_only() -> None:
    """Vérifie qu'une salutation traverse tout le cycle sans logique dédiée."""
    input_construction = InputConstruction(
        id="hello-input",
        language="fr",
        pattern=[{"literal": "bonjour"}],
        semantics={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        confidence=0.99,
        origin="test",
    )
    rule = DeclarativeRule(
        id="hello-rule",
        conditions=[
            RuleCondition(source="frame", path="type", operator="eq", value="SOCIAL_ACT"),
            RuleCondition(source="frame", path="slots.act", operator="eq", value="GREETING"),
        ],
        action_type="ASSERT",
        payload={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        base_score=0.9,
    )
    output = OutputConstruction(
        id="hello-output",
        language="fr",
        semantic_pattern={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        templates=["Bonjour."],
        confidence=0.99,
        origin="test",
    )

    result = _cycle().process(
        CognitiveEvent(text="Bonjour"),
        state={},
        lexicon=Lexicon.from_words({"bonjour"}),
        input_constructions=ConstructionSet(declarative_items=(input_construction,)),
        rules=[rule],
        output_constructions=[output],
    )

    assert result.response_text == "Bonjour."
    assert result.selected_action.action_type == "ASSERT"
    assert result.input_frames[0].type == "SOCIAL_ACT"


def test_cycle_can_clarify_unrecognized_text_via_empty_frame_rule() -> None:
    """Vérifie qu'un texte inconnu est géré par une règle déclarative EMPTY."""
    clarify_rule = DeclarativeRule(
        id="clarify-empty",
        conditions=[
            RuleCondition(source="frame", path="type", operator="eq", value="EMPTY")
        ],
        action_type="ASSERT",
        payload={"type": "CLARIFICATION", "slots": {}},
        base_score=0.8,
    )
    output = OutputConstruction(
        id="clarify-output",
        language="fr",
        semantic_pattern={"type": "CLARIFICATION"},
        templates=["Je n'ai pas compris."],
        confidence=0.9,
        origin="test",
    )

    result = _cycle().process(
        CognitiveEvent(text="phrase inconnue"),
        state={},
        lexicon=Lexicon.from_words(set()),
        input_constructions=ConstructionSet(),
        rules=[clarify_rule],
        output_constructions=[output],
    )

    assert result.response_text == "Je n'ai pas compris."
    assert result.input_frames == []
