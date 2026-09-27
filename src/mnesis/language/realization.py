"""
Réalisation linguistique déclarative de Mnesis.

Rôle :
    Transformer des frames sémantiques en texte à partir de constructions de
    sortie décrites en données, sans connaissance métier intégrée au moteur.
"""

from typing import Any

from pydantic import BaseModel, Field

from mnesis.semantic.frames import SemanticFrame


class OutputConstruction(BaseModel):
    """Décrit une règle de réalisation textuelle d'un frame sémantique."""

    id: str = Field(min_length=1)
    language: str = Field(min_length=2)
    semantic_pattern: dict[str, Any]
    templates: list[str] = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    origin: str = Field(min_length=1)


class LanguageRealizer:
    """Réalise un frame en texte uniquement à partir des constructions fournies."""

    def select(
        self,
        frame: SemanticFrame,
        constructions: list[OutputConstruction],
    ) -> OutputConstruction:
        """Retourne la meilleure construction de sortie compatible."""
        compatible = [
            construction
            for construction in constructions
            if _semantic_matches(frame, construction.semantic_pattern)
        ]
        if not compatible:
            raise ValueError("Aucune construction de sortie compatible.")
        compatible.sort(key=lambda item: item.confidence, reverse=True)
        return compatible[0]

    def realize(
        self,
        frame: SemanticFrame,
        constructions: list[OutputConstruction],
        context: dict[str, Any],
    ) -> str:
        """Réalise un frame avec la meilleure construction compatible."""
        selected = self.select(frame, constructions)
        values = {**context, **frame.slots, "type": frame.type}
        return selected.templates[0].format_map(values)


def _semantic_matches(frame: SemanticFrame, pattern: dict[str, Any]) -> bool:
    """Vérifie qu'un frame satisfait le sous-ensemble de contraintes du motif."""
    if "type" in pattern and frame.type != pattern["type"]:
        return False
    slot_pattern = pattern.get("slots", {})
    if not isinstance(slot_pattern, dict):
        return False
    for key, expected in slot_pattern.items():
        if key not in frame.slots or frame.slots[key] != expected:
            return False
    return True
