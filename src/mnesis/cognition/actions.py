"""
Moteur générique de sélection d'actions de Mnesis.

Rôle :
    Convertir les propositions issues des règles en actions scorées à partir
    de modificateurs déclaratifs lisant l'état cognitif par chemins génériques.
"""

from typing import Any

from pydantic import BaseModel, Field

from mnesis.cognition.rules import RuleResult


class ActionCandidate(BaseModel):
    """Représente une action candidate après calcul de son score contextuel."""

    rule_id: str
    action_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    base_score: float
    modifiers: dict[str, float] = Field(default_factory=dict)
    score: float


class ActionEngine:
    """Classe et sélectionne des actions sans connaître leur signification métier."""

    def rank(
        self,
        results: list[RuleResult],
        state: dict[str, Any],
    ) -> list[ActionCandidate]:
        """Calcule et classe les scores des actions proposées."""
        candidates = [self._candidate(result, state) for result in results]
        return sorted(candidates, key=lambda item: item.score, reverse=True)

    def select(
        self,
        results: list[RuleResult],
        state: dict[str, Any],
    ) -> ActionCandidate:
        """Sélectionne l'action la mieux scorée."""
        ranked = self.rank(results, state)
        if not ranked:
            raise ValueError("Aucune action candidate n'est disponible.")
        return ranked[0]

    def _candidate(
        self,
        result: RuleResult,
        state: dict[str, Any],
    ) -> ActionCandidate:
        """Construit une action candidate en appliquant ses modificateurs d'état."""
        score = result.base_score
        for path, weight in result.modifiers.items():
            value = _read_numeric_path(state, path)
            if value is not None:
                score += value * weight
        return ActionCandidate(
            rule_id=result.rule_id,
            action_type=result.action_type,
            payload=result.payload,
            base_score=result.base_score,
            modifiers=result.modifiers,
            score=round(score, 12),
        )


def _read_numeric_path(root: dict[str, Any], path: str) -> float | None:
    """Lit une valeur numérique depuis un chemin pointé dans l'état cognitif."""
    current: Any = root
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    if isinstance(current, (int, float)) and not isinstance(current, bool):
        return float(current)
    return None
