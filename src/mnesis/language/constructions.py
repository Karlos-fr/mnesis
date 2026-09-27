"""
Structures linguistiques contrôlées de Mnesis.

Rôle :
    Décrire explicitement le lexique disponible et les premières constructions
    françaises reconnues par le parseur, sans modèle probabiliste.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Lexicon:
    """Représente l'ensemble normalisé des formes lexicales actuellement connues."""

    words: frozenset[str]

    @classmethod
    def from_words(cls, words: set[str]) -> "Lexicon":
        """Construit un lexique normalisé en minuscules depuis un ensemble de formes."""
        return cls(frozenset(word.casefold() for word in words))

    def contains(self, word: str) -> bool:
        """Indique si une forme est connue dans le lexique courant."""
        return word.casefold() in self.words


@dataclass(frozen=True)
class Construction:
    """Décrit une construction linguistique explicite reconnue par le parseur."""

    intent: str
    pattern: str


@dataclass(frozen=True)
class ConstructionSet:
    """Regroupe les constructions actives pour une langue donnée."""

    items: tuple[Construction, ...]

    @classmethod
    def default_french(cls) -> "ConstructionSet":
        """Retourne le jeu minimal de constructions françaises de la V1."""
        return cls(
            (
                Construction("SALUER", r"^(bonjour|salut)[.!]?$"),
                Construction("DEFINIR", r"^(?P<subject>[^ ]+) est (un|une) (?P<object>[^ ?!.]+)[.!]?$"),
                Construction(
                    "DEMANDER_DEFINITION",
                    r"^qu['’]est-ce qu['’](un|une) (?P<concept>[^ ?!.]+) ?\?$",
                ),
            )
        )
