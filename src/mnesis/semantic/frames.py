"""
Représentations sémantiques génériques de Mnesis.

Rôle :
    Décrire le sens sous forme de frames indépendants du français, utilisables
    par l'interpréteur, le raisonnement, les actions et la réalisation.
"""

from typing import TypeAlias

from pydantic import BaseModel, Field


SemanticScalar: TypeAlias = str | int | float | bool | None
SemanticValue: TypeAlias = SemanticScalar | list[SemanticScalar] | dict[str, SemanticScalar]


class SemanticFrame(BaseModel):
    """
    Représente une unité de sens générique manipulée par le cycle cognitif.

    Le type et les slots sont volontairement ouverts afin que le moteur ne
    dépende d'aucune langue ni d'aucune intention conversationnelle précise.
    """

    type: str = Field(min_length=1)
    slots: dict[str, SemanticValue] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    provenance: list[str] = Field(default_factory=list)
