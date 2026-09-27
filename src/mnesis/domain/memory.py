"""
Modèles de mémoire épisodique de Mnesis.

Rôle :
    Représenter les événements vécus par une instance avec les métadonnées
    nécessaires au rappel, à l'importance et à la future consolidation.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Episode(BaseModel):
    """Représente un événement mémorisé dans l'histoire d'une instance."""

    id: UUID = Field(default_factory=uuid4)
    instance_id: UUID
    occurred_at: datetime
    summary: str = Field(min_length=1)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    affect: dict[str, float] = Field(default_factory=dict)
    recall_count: int = Field(default=0, ge=0)
    accessibility: float = Field(default=1.0, ge=0.0, le=1.0)
