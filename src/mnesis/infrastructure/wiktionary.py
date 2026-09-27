"""
Adaptateur HTTP vers Wiktionnaire.

Rôle :
    Interroger l'API Action MediaWiki du Wiktionnaire français et convertir la
    première définition française exploitable en entrée lexicale normalisée.
"""

import re

import httpx

from mnesis.application.learning import DictionaryEntry

_FRENCH_SECTION = re.compile(
    r"==\s*\{\{langue\|fr\}\}\s*==(.*?)(?=\n==\s*\{\{langue\||\Z)",
    flags=re.DOTALL | re.IGNORECASE,
)
_PART_OF_SPEECH = re.compile(r"\{\{S\|([^|}]+)\|fr(?:\|[^}]*)?\}\}", flags=re.IGNORECASE)
_DEFINITION = re.compile(r"^#(?![:*])\s*(.+)$", flags=re.MULTILINE)
_WIKI_LINK = re.compile(r"\[\[(?:[^]|]+\|)?([^]]+)\]\]")
_TEMPLATE = re.compile(r"\{\{[^{}]+\}\}")
_HTML_TAG = re.compile(r"<[^>]+>")


class WiktionarySource:
    """Source dictionnaire basée sur l'API Action du Wiktionnaire français."""

    def __init__(self, client: httpx.Client | None = None) -> None:
        """
        Initialise l'adaptateur avec un client HTTP injectable.

        Paramètres :
            client:
                Client HTTP réutilisable. Un client avec délai de dix secondes
                est créé lorsqu'aucun client n'est fourni.
        """
        self._client = client or httpx.Client(timeout=10.0)

    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """
        Retourne la première définition française exploitable d'un mot.

        Paramètres :
            word:
                Mot recherché dans le Wiktionnaire français.
            locale:
                Locale demandée. La V1 ne traite que les locales françaises.

        Retour :
            Entrée lexicale normalisée ou None lorsqu'aucune définition française
            exploitable n'est disponible.
        """
        if not locale.casefold().startswith("fr"):
            return None

        response = self._client.get(
            "https://fr.wiktionary.org/w/api.php",
            params={
                "action": "parse",
                "page": word,
                "prop": "wikitext",
                "format": "json",
                "formatversion": "2",
                "origin": "*",
            },
        )
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            return None

        wikitext = payload.get("parse", {}).get("wikitext")
        if not isinstance(wikitext, str):
            return None

        section_match = _FRENCH_SECTION.search(wikitext)
        if section_match is None:
            return None
        section = section_match.group(1)

        definition_match = _DEFINITION.search(section)
        if definition_match is None:
            return None

        part_match = _PART_OF_SPEECH.search(section[: definition_match.start()])
        part_of_speech = part_match.group(1).strip() if part_match else "inconnu"
        definition = self._clean_wikitext(definition_match.group(1))
        if not definition:
            return None

        return DictionaryEntry(
            word=word,
            lemma=word.casefold(),
            part_of_speech=part_of_speech,
            definition=definition,
            source_uri=f"https://fr.wiktionary.org/wiki/{word}",
        )

    @staticmethod
    def _clean_wikitext(value: str) -> str:
        """
        Simplifie le balisage Wiki d'une définition courte.

        Paramètres :
            value:
                Ligne de définition brute en wikitexte.

        Retour :
            Texte lisible conservant le contenu lexical utile.
        """
        value = _WIKI_LINK.sub(r"\1", value)
        value = _TEMPLATE.sub("", value)
        value = _HTML_TAG.sub("", value)
        return " ".join(value.split()).strip()
