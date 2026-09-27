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
            "RETRIEVE": self._retrieve,
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
        """Persiste un frame via le callback de mémoire sémantique injecté."""
        raw_frame = (
            context.get("input_frames", [None])[0]
            if action.payload.get("from_frame")
            else action.payload.get("frame")
        )
        if raw_frame is None and "type" in action.payload and "slots" in action.payload:
            raw_frame = action.payload
        if raw_frame is None:
            raise ValueError("STORE nécessite un frame à persister.")
        frame = (
            raw_frame
            if isinstance(raw_frame, SemanticFrame)
            else SemanticFrame.model_validate(raw_frame)
        )
        store_frame = context.get("store_frame")
        if not callable(store_frame):
            return ProcedureResult(
                side_effects=[{"type": "STORE_FRAME", "frame": frame.model_dump()}],
            )
        learned = store_frame(frame) or []
        return ProcedureResult(
            semantic_output=frame,
            learned_items=[str(item) for item in learned],
        )

    def _retrieve(
        self,
        action: ActionCandidate,
        context: dict[str, Any],
    ) -> ProcedureResult:
        """Délègue une requête à la mémoire sémantique injectée."""
        retrieve = context.get("retrieve")
        if not callable(retrieve):
            raise ValueError("RETRIEVE nécessite un callback de récupération.")
        query = {key: value for key, value in action.payload.items() if key != "fallback"}
        raw = retrieve(query)
        if raw is None:
            fallback = action.payload.get("fallback")
            if fallback is None:
                raise ValueError("La mémoire sémantique n'a produit aucun résultat.")
            raw = fallback
        frame = raw if isinstance(raw, SemanticFrame) else SemanticFrame.model_validate(raw)
        return ProcedureResult(semantic_output=frame)

    def _research(
        self,
        action: ActionCandidate,
        context: dict[str, Any],
    ) -> ProcedureResult:
        """Exécute une recherche injectée ou expose son objectif comme effet."""
        research = context.get("research")
        if not callable(research):
            return ProcedureResult(
                side_effects=[{"type": "RESEARCH", "goal": action.payload}]
            )
        outcome = research(action.payload)
        return ProcedureResult(
            semantic_output=outcome.semantic_output,
            learned_items=outcome.learned_items,
        )
