"""
Tests du paquet cognitif core-fr.

Rôle :
    Vérifier que le socle français porte désormais ses constructions d'entrée,
    ses constructions de sortie et ses règles conversationnelles comme données.
"""

from pathlib import Path

from mnesis.infrastructure.knowledge_packs import load_knowledge_pack

CORE_FR = Path("knowledge/core-fr")


def test_core_fr_loads_declarative_input_constructions() -> None:
    """Vérifie que les formes françaises de bootstrap sont chargées comme données."""
    pack = load_knowledge_pack(CORE_FR)
    ids = {item.id for item in pack.input_constructions}

    assert "fr-greeting-bonjour" in ids
    assert "fr-is-a-masculine" in ids
    assert "fr-definition-query-masculine" in ids


def test_core_fr_loads_output_constructions() -> None:
    """Vérifie que les formulations de sortie ne résident plus dans Python."""
    pack = load_knowledge_pack(CORE_FR)
    ids = {item.id for item in pack.output_constructions}

    assert "fr-output-greeting" in ids
    assert "fr-output-is-a" in ids
    assert "fr-output-clarification" in ids


def test_core_fr_loads_declarative_rules() -> None:
    """Vérifie que les comportements de bootstrap sont fournis comme règles."""
    pack = load_knowledge_pack(CORE_FR)
    ids = {rule.id for rule in pack.rules}

    assert "fr-rule-greeting" in ids
    assert "fr-rule-clarify-empty" in ids
    assert all(rule.action_type for rule in pack.rules)
