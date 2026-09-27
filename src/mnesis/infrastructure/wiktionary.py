"""
Adaptateur HTTP vers Wiktionnaire.

Rôle :
    Interroger une source lexicale Wiktionnaire et convertir sa réponse en une
    entrée normalisée exploitable par le service d'apprentissage.
"""

from urllib.parse import quote
import httpx
from mnesis.application.learning import DictionaryEntry


class WiktionarySource:
    """Source dictionnaire basée sur l'API REST de Wiktionnaire français."""

    def __init__(self, client: httpx.Client | None = None) -> None:
        """Initialise l'adaptateur avec un client HTTP injectable."""
        self._client = client or httpx.Client(timeout=10.0)

    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """Retourne la première définition française exploitable ou None."""
        url = f"https://fr.wiktionary.org/api/rest_v1/page/definition/{quote(word)}"
        response = self._client.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        entries = response.json().get("fr") or []
        for item in entries:
            definitions = item.get("definitions") or []
            if definitions and isinstance(definitions[0].get("definition"), str) and definitions[0]["definition"].strip():
                return DictionaryEntry(word=word, lemma=word.casefold(), part_of_speech=str(item.get("partOfSpeech") or "inconnu"), definition=definitions[0]["definition"].strip(), source_uri=f"https://fr.wiktionary.org/wiki/{quote(word)}")
        return None
