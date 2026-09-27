"""
Exécuteur de procédures primitives de Mnesis.

Rôle :
    Exécuter un petit ensemble d'actions cognitives natives et génériques sans
    contenir de comportement conversationnel ou linguistique spécifique.
"""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from mnesis.cognition.actions import ActionCandidate
from mnesis.semantic.frames import SemanticFrame


class ProcedureResult(BaseModel):
    """Résultat explicite d'une procédure primitive exécutée par Mnesis."""

    semantic_output: SemanticFrame | None = None
    learned_items: list[str] = Field(default_factory=list)
    side_effects: list[dict[str, Any]] = Field(default_factory=list)


class ProcedureExecutor:
    """Exécute les primitives cognitives via une table de dispatch explicite."""

    def __init__(self) -> None:
        """Initialise la table des primitives natives disponibles."""
        self._handlers: dict[
            str,
            Callable[[ActionCandidate, dict[str, Any]], ProcedureResult],
        ] = {
            "ASSERT": self._semantic_output,
            "ASK": self._semantic_output,
            "STORE": self._store,
            "RESEARCH": self._research,
        }

    def execute(
        self,
        action: ActionCandidate,
        context: dict[str, Any],
    ) -> ProcedureResult:
        """Exécute une action primitive avec son contexte."""
        handler = self._handlers.get(action.action_type)
        if handler is None:
            raise ValueError(f"Primitive inconnue : {action.action_type}")
        return handler(action, context)

    def _semantic_output(
        self,
        action: ActionCandidate,
        context: dict[str, Any],
    ) -> ProcedureResult:
        """Transforme le payload d'une action en sortie sémantique."""
        del context
        return ProcedureResult(
            semantic_output=SemanticFrame.model_validate(action.payload)
        )

    def _store(
        self,
        action: ActionCandidate,
        context: dict[str, Any],
    ) -> ProcedureResult:
        """Décrit explicitement une demande de persistance d'un frame."""
        del context
        return ProcedureResult(
            side_effects=[{"type": "STORE_FRAME", "frame": action.payload}]
        )

    def _research(
        self,
        action: ActionCandidate,
        context: dict[str, Any],
    ) -> ProcedureResult:
        """Décrit explicitement un objectif de recherche à exécuter ensuite."""
        del context
        return ProcedureResult(
            side_effects=[{"type": "RESEARCH", "goal": action.payload}]
        )
