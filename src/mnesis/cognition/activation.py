"""
Moteur d'activation cognitive minimal de Mnesis.

Rôle :
    Fournir une frontière explicite pour l'activation future de concepts et de
    souvenirs, sans introduire de comportement métier dans le cycle.
"""

from pydantic import BaseModel, Field

from mnesis.semantic.frames import SemanticFrame


class ActivationResult(BaseModel):
    """Résume les éléments activés à partir des perceptions courantes."""

    frames: list[SemanticFrame] = Field(default_factory=list)
    concept_ids: list[str] = Field(default_factory=list)
    memory_ids: list[str] = Field(default_factory=list)


class ActivationEngine:
    """Active les éléments pertinents ; la V1 relaie au minimum les frames perçus."""

    def activate(self, frames: list[SemanticFrame]) -> ActivationResult:
        """Active les représentations directement perçues."""
        return ActivationResult(frames=frames)
