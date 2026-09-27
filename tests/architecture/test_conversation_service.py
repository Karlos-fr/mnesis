"""
Tests architecturaux du service conversationnel.

Rôle :
    Empêcher le retour de branches métier fondées sur des intentions codées en
    dur dans le service qui orchestre le cycle cognitif.
"""

from pathlib import Path


def test_conversation_service_contains_no_hardcoded_business_intents() -> None:
    """Vérifie que le service ne dépend plus des anciennes intentions métier."""
    source = Path("src/mnesis/application/conversation.py").read_text(encoding="utf-8")
    for forbidden in [
        "SALUER",
        "DEFINIR",
        "DEMANDER_DEFINITION",
        "RELANCER",
        "parsed.intent",
    ]:
        assert forbidden not in source
