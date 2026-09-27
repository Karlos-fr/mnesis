"""Garde-fou contre le retour du moteur conversationnel à intents codés en dur."""

from pathlib import Path


def test_python_core_contains_no_legacy_business_intents() -> None:
    """Vérifie que les anciens intents métier ont entièrement quitté le moteur Python."""
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("src").rglob("*.py")
    )
    for forbidden in ["SALUER", "DEFINIR", "DEMANDER_DEFINITION", "parsed.intent"]:
        assert forbidden not in source
