"""Test d'indépendance linguistique du cycle cognitif."""

from mnesis.cognition.actions import ActionEngine
from mnesis.cognition.cycle import CognitiveCycle, CognitiveEvent
from mnesis.cognition.procedures import ProcedureExecutor
from mnesis.cognition.rules import DeclarativeRule, RuleCondition, RuleEngine
from mnesis.language.constructions import ConstructionSet, InputConstruction, Lexicon
from mnesis.language.interpreter import LanguageInterpreter
from mnesis.language.realization import LanguageRealizer, OutputConstruction


def test_same_cognitive_cycle_can_use_english_data_only() -> None:
    """Vérifie qu'un mini-pack anglais fonctionne sans code linguistique dédié."""
    cycle = CognitiveCycle(
        interpreter=LanguageInterpreter(),
        rule_engine=RuleEngine(),
        action_engine=ActionEngine(),
        procedure_executor=ProcedureExecutor(),
        realizer=LanguageRealizer(),
    )
    input_construction = InputConstruction(
        id="en-hello-input",
        language="en",
        pattern=[{"literal": "hello"}],
        semantics={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        confidence=0.99,
        origin="test-pack-en",
    )
    rule = DeclarativeRule(
        id="en-greeting-rule",
        conditions=[
            RuleCondition(
                source="frame",
                path="type",
                operator="eq",
                value="SOCIAL_ACT",
            ),
            RuleCondition(
                source="frame",
                path="slots.act",
                operator="eq",
                value="GREETING",
            ),
        ],
        action_type="ASSERT",
        payload={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        base_score=0.9,
    )
    output = OutputConstruction(
        id="en-hello-output",
        language="en",
        semantic_pattern={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
        templates=["Hello."],
        confidence=0.99,
        origin="test-pack-en",
    )

    result = cycle.process(
        CognitiveEvent(text="Hello"),
        state={},
        lexicon=Lexicon.from_words({"hello"}),
        input_constructions=ConstructionSet(
            declarative_items=(input_construction,)
        ),
        rules=[rule],
        output_constructions=[output],
    )

    assert result.response_text == "Hello."
    assert result.output_construction_id == "en-hello-output"
