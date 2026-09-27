"""
Cycle cognitif générique de Mnesis.

Rôle :
    Orchestrer interprétation, activation, règles, scoring, procédures et
    réalisation linguistique sans connaître la langue ni les intentions métier.
"""

from typing import Any

from pydantic import BaseModel, Field

from mnesis.cognition.actions import ActionCandidate, ActionEngine
from mnesis.cognition.activation import ActivationEngine, ActivationResult
from mnesis.cognition.procedures import ProcedureExecutor, ProcedureResult
from mnesis.cognition.rules import DeclarativeRule, RuleEngine, RuleResult
from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.language.interpreter import LanguageInterpreter
from mnesis.language.realization import LanguageRealizer, OutputConstruction
from mnesis.semantic.frames import SemanticFrame


class CognitiveEvent(BaseModel):
    """Événement textuel présenté au cycle cognitif."""

    text: str = Field(min_length=1)


class CognitiveResult(BaseModel):
    """Résultat inspectable d'un passage complet dans le cycle cognitif."""

    response_text: str
    input_frames: list[SemanticFrame]
    activation: ActivationResult
    rule_results: list[RuleResult]
    ranked_actions: list[ActionCandidate]
    selected_action: ActionCandidate
    procedure_result: ProcedureResult


class CognitiveCycle:
    """Orchestre les moteurs génériques qui composent un tour cognitif."""

    def __init__(
        self,
        *,
        interpreter: LanguageInterpreter,
        rule_engine: RuleEngine,
        action_engine: ActionEngine,
        procedure_executor: ProcedureExecutor,
        realizer: LanguageRealizer,
        activation_engine: ActivationEngine | None = None,
    ) -> None:
        """Initialise le cycle avec des composants injectés et testables isolément."""
        self._interpreter = interpreter
        self._activation = activation_engine or ActivationEngine()
        self._rules = rule_engine
        self._actions = action_engine
        self._procedures = procedure_executor
        self._realizer = realizer

    def process(
        self,
        event: CognitiveEvent,
        *,
        state: dict[str, Any],
        lexicon: Lexicon,
        input_constructions: ConstructionSet,
        rules: list[DeclarativeRule],
        output_constructions: list[OutputConstruction],
    ) -> CognitiveResult:
        """Exécute un cycle cognitif complet à partir de ressources déclaratives."""
        frames = self._interpreter.interpret(event.text, input_constructions, lexicon)
        activation = self._activation.activate(frames)
        rule_results = self._rules.evaluate(activation.frames, state, rules)
        ranked = self._actions.rank(rule_results, state)
        if not ranked:
            raise ValueError("Aucune règle n'a produit d'action candidate.")
        selected = ranked[0]
        procedure_result = self._procedures.execute(selected, state)
        if procedure_result.semantic_output is None:
            raise ValueError(
                "L'action sélectionnée ne produit pas de sortie sémantique réalisable."
            )
        response = self._realizer.realize(
            procedure_result.semantic_output,
            output_constructions,
            state,
        )
        return CognitiveResult(
            response_text=response,
            input_frames=frames,
            activation=activation,
            rule_results=rule_results,
            ranked_actions=ranked,
            selected_action=selected,
            procedure_result=procedure_result,
        )
