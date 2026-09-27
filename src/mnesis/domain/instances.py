"""
Modèle d'instance Mnesis.

Rôle :
    Représenter une entité Mnesis indépendante possédant sa propre identité,
    sa personnalité et son état affectif.
"""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from mnesis.domain.affect import AffectState, Personality


class MnesisInstance(BaseModel):
    """Représente une instance isolée du moteur cognitif Mnesis."""

    id: UUID
    name: str = Field(min_length=1)
    locale: str = Field(default="fr-FR", min_length=2)
    personality: Personality = Field(default_factory=Personality)
    affect: AffectState = Field(default_factory=AffectState)

    @classmethod
    def create(cls, name: str, locale: str = "fr-FR") -> "MnesisInstance":
        """
        Crée une nouvelle instance avec des états internes indépendants.

        Paramètres :
            name:
                Nom humainement lisible de l'instance.
            locale:
                Locale linguistique initiale de l'instance.

        Retour :
            Une nouvelle instance possédant un identifiant UUID unique.
        """
        return cls(id=uuid4(), name=name, locale=locale)
