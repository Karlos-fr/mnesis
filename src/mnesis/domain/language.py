"""
Modèles lexicaux de Mnesis.

Rôle :
    Représenter les formes linguistiques indépendamment des concepts qu'elles
    désignent et suivre leur niveau de maîtrise par une instance.
"""

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MasteryLevel(StrEnum):
    """Décrit le niveau de maîtrise d'un lexème par une instance Mnesis."""

    UNKNOWN = "unknown"
    SEEN = "seen"
    PARTIALLY_UNDERSTOOD = "partially_understood"
    UNDERSTOOD = "understood"
    USABLE = "usable"
    MASTERED = "mastered"


class LexicalSense(BaseModel):
    """Associe un lexème à un concept avec un niveau de confiance explicite."""

    concept_id: UUID
    confidence: float = Field(ge=0.0, le=1.0)


class Lexeme(BaseModel):
    """Représente une forme lexicale connue indépendamment du concept associé."""

    id: UUID = Field(default_factory=uuid4)
    surface: str = Field(min_length=1)
    lemma: str = Field(min_length=1)
    language: str = Field(min_length=2)
    part_of_speech: str = Field(min_length=1)
    senses: list[LexicalSense] = Field(default_factory=list)
    mastery: MasteryLevel = MasteryLevel.SEEN
