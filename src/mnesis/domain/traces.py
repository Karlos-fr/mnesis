"""
Traces d'explication des décisions cognitives de Mnesis.

Rôle :
    Conserver une représentation inspectable des informations consultées et
    de la sélection d'action réalisée par le moteur conversationnel.
"""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DecisionTrace(BaseModel):
    """Décrit les principaux facteurs ayant conduit à une décision cognitive."""

    id: UUID = Field(default_factory=uuid4)
    instance_id: UUID
    action: str = Field(min_length=1)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    candidate_actions: dict[str, float] = Field(default_factory=dict)
    consulted_concepts: list[UUID] = Field(default_factory=list)
    consulted_claims: list[UUID] = Field(default_factory=list)
    recalled_memories: list[UUID] = Field(default_factory=list)
    affect_snapshot: dict[str, float] = Field(default_factory=dict)
