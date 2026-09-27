"""
Tests de l'adaptateur Wiktionnaire.

Rôle :
    Vérifier la conversion d'une réponse HTTP structurée en entrée lexicale
    sans dépendre du réseau pendant les tests.
"""

import httpx
from mnesis.infrastructure.wiktionary import WiktionarySource


def test_wiktionary_adapter_extracts_first_french_definition() -> None:
    """Vérifie l'extraction d'une définition exploitable depuis la réponse REST."""
    payload = {"fr": [{"partOfSpeech": "adjectif", "language": "Français", "definitions": [{"definition": "Qui vit dans les arbres."}]}]}
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload, request=request)
    entry = WiktionarySource(client=httpx.Client(transport=httpx.MockTransport(handler))).lookup("arboricole", "fr-FR")
    assert entry is not None
    assert entry.lemma == "arboricole"
    assert entry.part_of_speech == "adjectif"
    assert entry.definition == "Qui vit dans les arbres."


def test_wiktionary_adapter_returns_none_on_not_found() -> None:
    """Vérifie qu'une entrée absente n'est pas transformée en définition fictive."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, request=request)
    source = WiktionarySource(client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert source.lookup("motintrouvable", "fr-FR") is None
