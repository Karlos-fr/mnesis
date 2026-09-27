"""
Tests du paquet racine Mnesis.

Rôle :
    Vérifier les métadonnées minimales exposées par le paquet Python.
"""

import mnesis


def test_package_exposes_version() -> None:
    """Vérifie que le paquet expose la version initiale attendue."""
    assert mnesis.__version__ == "0.1.0"
