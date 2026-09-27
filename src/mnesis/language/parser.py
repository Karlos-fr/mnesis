"""
Parseur linguistique contrôlé de Mnesis.

Rôle :
    Transformer une phrase française simple en intention et cadres sémantiques
    explicites, tout en signalant les formes lexicales encore inconnues.
"""

import re

from pydantic import BaseModel

from mnesis.language.constructions import ConstructionSet, Lexicon

_TOKEN_PATTERN = re.compile(r"[\wÀ-ÿ'-]+|\?", flags=re.UNICODE)
_GRAMMATICAL_FORMS = {"est", "un", "une", "qu'est-ce", "qu’un", "qu'une", "qu'un", "que", "?"}


class ParsedUtterance(BaseModel):
    """Résultat inspectable de l'analyse d'un énoncé utilisateur."""

    text: str
    tokens: list[str]
    intent: str | None
    semantic_frames: list[dict[str, str]]
    unknown_tokens: list[str]


def parse_utterance(text: str, lexicon: Lexicon, constructions: ConstructionSet) -> ParsedUtterance:
    """Analyse une phrase et retourne intention, cadres sémantiques et mots inconnus."""
    normalized = text.strip().casefold().replace("’", "'")
    if not normalized:
        raise ValueError("Le message ne peut pas être vide.")

    tokens = _TOKEN_PATTERN.findall(normalized)
    unknown = [token for token in tokens if token not in _GRAMMATICAL_FORMS and not lexicon.contains(token)]
    intent: str | None = None
    frames: list[dict[str, str]] = []

    for construction in constructions.items:
        match = re.fullmatch(construction.pattern, normalized, flags=re.IGNORECASE)
        if match is None:
            continue
        intent = construction.intent
        if intent == "DEFINIR":
            frames.append({"subject": match.group("subject"), "predicate": "EST_UN", "object": match.group("object")})
        elif intent == "DEMANDER_DEFINITION":
            frames.append({"concept": match.group("concept")})
        break

    return ParsedUtterance(text=text, tokens=tokens, intent=intent, semantic_frames=frames, unknown_tokens=unknown)
