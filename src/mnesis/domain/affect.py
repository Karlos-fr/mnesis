"""
Modèles affectifs et de personnalité de Mnesis.

Rôle :
    Représenter les traits relativement stables d'une instance ainsi que son
    état émotionnel courant sous forme de dimensions numériques inspectables.

Contraintes :
    Toutes les dimensions sont normalisées dans l'intervalle fermé [0, 1].
"""

from pydantic import BaseModel, Field


class Personality(BaseModel):
    """Représente les traits de personnalité relativement stables d'une instance."""

    curiosity: float = Field(default=0.6, ge=0.0, le=1.0)
    extraversion: float = Field(default=0.5, ge=0.0, le=1.0)
    agreeableness: float = Field(default=0.5, ge=0.0, le=1.0)
    humor: float = Field(default=0.4, ge=0.0, le=1.0)
    optimism: float = Field(default=0.5, ge=0.0, le=1.0)
    impulsiveness: float = Field(default=0.3, ge=0.0, le=1.0)


class AffectState(BaseModel):
    """Représente l'état émotionnel courant et mesurable d'une instance Mnesis."""

    joy: float = Field(default=0.5, ge=0.0, le=1.0)
    sadness: float = Field(default=0.0, ge=0.0, le=1.0)
    anger: float = Field(default=0.0, ge=0.0, le=1.0)
    fear: float = Field(default=0.0, ge=0.0, le=1.0)
    curiosity: float = Field(default=0.6, ge=0.0, le=1.0)
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    boredom: float = Field(default=0.0, ge=0.0, le=1.0)
