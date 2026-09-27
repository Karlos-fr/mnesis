"""
Structures linguistiques de Mnesis.

Rôle :
    Décrire les constructions déclaratives indépendantes de toute logique métier.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from mnesis.semantic.frames import SemanticFrame


@dataclass(frozen=True)
class Lexicon:
    """Représente l'ensemble normalisé des formes lexicales actuellement connues."""

    words: frozenset[str]

    @classmethod
    def from_words(cls, words: set[str]) -> "Lexicon":
        """
        Construit un lexique depuis un ensemble de formes.

        Paramètres :
            words:
                Formes lexicales à considérer comme connues.

        Retour :
            Lexique normalisé en minuscules.
        """
        return cls(frozenset(word.casefold() for word in words))

    def contains(self, word: str) -> bool:
        """Indique si une forme est connue dans le lexique courant."""
        return word.casefold() in self.words


class InputConstruction(BaseModel):
    """
    Décrit une construction linguistique d'entrée entièrement déclarative.

    Le motif est une séquence d'atomes décrits par dictionnaire. Un atome peut
    être un littéral, un lemme, un lexème ou une variable capturée.
    """

    id: str = Field(min_length=1)
    language: str = Field(min_length=2)
    pattern: list[dict[str, str]] = Field(min_length=1)
    semantics: dict[str, Any]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    origin: str = Field(min_length=1)
    usage_count: int = Field(default=0, ge=0)
    reinforced_at: datetime | None = None


class ConstructionMatch(BaseModel):
    """Résultat d'appariement d'une construction avec un texte d'entrée."""

    construction_id: str
    captures: dict[str, str]
    frame: SemanticFrame


@dataclass(frozen=True)
class ConstructionSet:
    """Regroupe uniquement les constructions déclaratives actives."""

    declarative_items: tuple[InputConstruction, ...] = field(default_factory=tuple)

    def match(self, text: str, lexicon: Lexicon) -> list[ConstructionMatch]:
        """
        Applique toutes les constructions déclaratives compatibles à un texte.

        Paramètres :
            text:
                Énoncé brut à analyser.
            lexicon:
                Lexique actif de l'instance.

        Retour :
            Tous les appariements valides, dans l'ordre des constructions.
        """
        tokens = _tokenize(text)
        matches: list[ConstructionMatch] = []
        for construction in self.declarative_items:
            captures = _match_pattern(tokens, construction.pattern, lexicon)
            if captures is None:
                continue
            frame = _build_frame(construction, captures)
            matches.append(
                ConstructionMatch(
                    construction_id=construction.id,
                    captures=captures,
                    frame=frame,
                )
            )
        return matches


def _tokenize(text: str) -> list[str]:
    """Normalise un texte en unités séparées par les espaces pour la V1."""
    return [token.casefold() for token in text.strip().split() if token.strip()]


def _match_pattern(
    tokens: list[str],
    pattern: list[dict[str, str]],
    lexicon: Lexicon,
) -> dict[str, str] | None:
    """Apparie une séquence de tokens à un motif déclaratif simple."""
    if len(tokens) != len(pattern):
        return None
    captures: dict[str, str] = {}
    for token, atom in zip(tokens, pattern, strict=True):
        if "literal" in atom and token != atom["literal"].casefold():
            return None
        if "lemma" in atom and token != atom["lemma"].casefold():
            return None
        if "lexeme" in atom:
            expected = atom["lexeme"].casefold()
            if token != expected or not lexicon.contains(token):
                return None
        if "variable" in atom:
            captures[atom["variable"]] = token
    return captures


def _build_frame(
    construction: InputConstruction,
    captures: dict[str, str],
) -> SemanticFrame:
    """Construit un frame sémantique en substituant les variables capturées."""
    semantics = construction.semantics
    slots = {
        key: _substitute(value, captures)
        for key, value in dict(semantics.get("slots", {})).items()
    }
    return SemanticFrame(
        type=str(semantics["type"]),
        slots=slots,
        confidence=construction.confidence,
        provenance=[f"construction:{construction.id}"],
    )


def _substitute(value: Any, captures: dict[str, str]) -> Any:
    """Remplace les références $variable d'une valeur par leur capture."""
    if isinstance(value, str) and value.startswith("$"):
        return captures.get(value[1:], value)
    if isinstance(value, list):
        return [_substitute(item, captures) for item in value]
    if isinstance(value, dict):
        return {key: _substitute(item, captures) for key, item in value.items()}
    return value
