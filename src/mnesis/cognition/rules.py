"""
Moteur de règles déclaratives de Mnesis.

Rôle :
    Évaluer des conditions décrites en données sur des frames sémantiques et
    l'état cognitif, puis produire des propositions d'actions génériques.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from mnesis.semantic.frames import SemanticFrame


class RuleCondition(BaseModel):
    """Décrit une condition générique appliquée à un frame ou à l'état cognitif."""

    source: Literal["frame", "state"]
    path: str = Field(min_length=1)
    operator: Literal["eq", "exists", "gte", "lte"]
    value: Any = None


class DeclarativeRule(BaseModel):
    """Décrit une règle produisant une action candidate lorsque ses conditions passent."""

    id: str = Field(min_length=1)
    conditions: list[RuleCondition] = Field(default_factory=list)
    action_type: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    base_score: float = 0.5
    modifiers: dict[str, float] = Field(default_factory=dict)


class RuleResult(BaseModel):
    """Représente une action proposée par une règle satisfaite."""

    rule_id: str
    action_type: str
    payload: dict[str, Any]
    base_score: float
    modifiers: dict[str, float] = Field(default_factory=dict)


class RuleEngine:
    """Évalue des règles déclaratives sans connaître le sens métier de leurs données."""

    def evaluate(
        self,
        frames: list[SemanticFrame],
        state: dict[str, Any],
        rules: list[DeclarativeRule],
    ) -> list[RuleResult]:
        """Évalue toutes les règles sur les frames candidats et l'état courant."""
        results: list[RuleResult] = []
        candidate_frames = frames or [SemanticFrame(type="EMPTY")]
        for rule in rules:
            for frame in candidate_frames:
                if all(self._matches(condition, frame, state) for condition in rule.conditions):
                    results.append(
                        RuleResult(
                            rule_id=rule.id,
                            action_type=rule.action_type,
                            payload=rule.payload,
                            base_score=rule.base_score,
                            modifiers=rule.modifiers,
                        )
                    )
                    break
        return results

    def _matches(
        self,
        condition: RuleCondition,
        frame: SemanticFrame,
        state: dict[str, Any],
    ) -> bool:
        """Évalue une condition individuelle sur sa source et son opérateur."""
        root: Any = frame.model_dump() if condition.source == "frame" else state
        actual = _read_path(root, condition.path)
        if condition.operator == "exists":
            return actual is not None
        if condition.operator == "eq":
            return actual == condition.value
        if condition.operator == "gte":
            return isinstance(actual, (int, float)) and actual >= condition.value
        if condition.operator == "lte":
            return isinstance(actual, (int, float)) and actual <= condition.value
        return False


def _read_path(root: Any, path: str) -> Any:
    """Lit un chemin pointé dans un dictionnaire ou objet sérialisable."""
    current = root
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        else:
            return None
    return current
