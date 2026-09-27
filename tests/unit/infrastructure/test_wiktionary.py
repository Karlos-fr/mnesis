"""
Tests de l'adaptateur Wiktionnaire.

Rôle :
    Vérifier la conversion d'une page Wiktionnaire française en entrée lexicale
    sans dépendre du réseau pendant les tests.
"""

import httpx

from mnesis.infrastructure.wiktionary import WiktionarySource


def test_wiktionary_adapter_extracts_first_french_definition() -> None:
    """Vérifie l'extraction d'une définition depuis le wikitexte français."""
    payload = {
        "parse": {
            "title": "arboricole",
            "wikitext": (
                "== {{langue|fr}} ==\n"
                "=== {{S|adjectif|fr}} ===\n"
                "# Qui vit dans les [[arbre]]s.\n"
                "# Qui concerne les arbres.\n"
            ),
        }
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/w/api.php"
        assert request.url.params["action"] == "parse"
        assert request.url.params["page"] == "arboricole"
        return httpx.Response(200, json=payload, request=request)

    entry = WiktionarySource(
        client=httpx.Client(transport=httpx.MockTransport(handler))
    ).lookup("arboricole", "fr-FR")

    assert entry is not None
    assert entry.lemma == "arboricole"
    assert entry.part_of_speech == "adjectif"
    assert entry.definition == "Qui vit dans les arbres."


def test_wiktionary_adapter_returns_none_on_missing_page() -> None:
    """Vérifie qu'une page absente n'est pas transformée en connaissance fictive."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"error": {"code": "missingtitle", "info": "Page inexistante"}},
            request=request,
        )

    source = WiktionarySource(
        client=httpx.Client(transport=httpx.MockTransport(handler))
    )

    assert source.lookup("motintrouvable", "fr-FR") is None
