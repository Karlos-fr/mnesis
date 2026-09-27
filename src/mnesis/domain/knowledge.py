"""
Modèles de connaissances, croyances et preuves de Mnesis.

Rôle :
    Représenter les concepts, affirmations et preuves de manière explicite,
    versionnable et inspectable, sans écrasement silencieux de l'historique.
"""

from datetime import datetime
from enum import StrEnum
from typing import TypeAlias
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


LiteralValue: TypeAlias = str | int | float | bool


class ClaimStatus(StrEnum):
    """Décrit le statut épistémique courant d'une affirmation."""

    TENTATIVE = "tentative"
    ACCEPTED = "accepted"
    TRUSTED = "trusted"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"


class KnowledgeOrigin(StrEnum):
    """Identifie l'origine d'une connaissance ou d'un élément de preuve."""

    NATIVE = "native"
    KNOWLEDGE_PACK = "knowledge_pack"
    USER = "user"
    DICTIONARY = "dictionary"
    WEB = "web"
    INFERENCE = "inference"
    LEARNED_PROCEDURE = "learned_procedure"


class Concept(BaseModel):
    """Représente une unité sémantique indépendante de ses formes lexicales."""

    id: UUID = Field(default_factory=uuid4)
    kind: str = Field(min_length=1)
    label: str = Field(min_length=1)


class Evidence(BaseModel):
    """Représente une preuve soutenant ou contredisant une affirmation."""

    id: UUID = Field(default_factory=uuid4)
    source_type: KnowledgeOrigin
    source_uri: str = Field(min_length=1)
    observed_at: datetime
    reliability: float = Field(ge=0.0, le=1.0)
    statement: str = Field(min_length=1)


class Claim(BaseModel):
    """Représente une affirmation sémantique et l'état de confiance associé."""

    id: UUID = Field(default_factory=uuid4)
    subject_id: UUID
    predicate: str = Field(min_length=1)
    object_id: UUID | None = None
    literal: LiteralValue | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    status: ClaimStatus
    origin: KnowledgeOrigin
    evidence: list[Evidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_object_or_literal(self) -> "Claim":
        """
        Vérifie qu'une affirmation possède exactement une cible.

        Retour :
            L'affirmation validée.

        Erreurs :
            ValueError:
                Levée si l'objet et la valeur littérale sont simultanément
                présents ou simultanément absents.
        """
        if (self.object_id is None) == (self.literal is None):
            raise ValueError("Une affirmation doit avoir un object_id ou un literal, mais pas les deux.")
        return self
