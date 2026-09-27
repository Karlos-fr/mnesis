"""
Ports applicatifs de Mnesis.

Rôle :
    Définir les contrats entre le cœur d'application et les sources externes.
"""

from typing import Protocol
from mnesis.application.learning import DictionaryEntry


class DictionarySource(Protocol):
    """Contrat d'une source capable de fournir une définition lexicale."""
    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """Retourne une entrée lexicale pour le mot demandé ou None."""
        ...
