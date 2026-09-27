"""
Réalisation textuelle contrôlée de Mnesis.

Rôle :
    Transformer une intention et des données sémantiques en phrases françaises
    déterministes sans utiliser de modèle génératif.
"""


class SurfaceRealizer:
    """Produit les formulations françaises minimales de la V1."""

    def __init__(self, responses: dict[str, list[str]]) -> None:
        """Initialise le réalisateur avec les formulations fournies par core-fr."""
        self._responses = responses

    def greeting(self) -> str:
        """Retourne la première salutation configurée dans le socle."""
        return self._responses["SALUER"][0]

    def acknowledge_definition(self, subject: str, obj: str) -> str:
        """Confirme la mémorisation d'une relation de définition."""
        return f"D'accord. Je retiens qu'un {subject} est un {obj}."

    def definition(self, subject: str, obj: str) -> str:
        """Réalise une définition simple."""
        return f"Un {subject} est un {obj}."

    def uncertain_definition(self, subject: str, obj: str) -> str:
        """Exprime explicitement le doute avec l'hypothèse préférée."""
        return f"Je ne suis pas certain, mais les éléments les plus fiables indiquent qu'un {subject} est un {obj}."

    def clarification(self) -> str:
        """Retourne la formulation de clarification du socle."""
        return self._responses["DEMANDER_CLARIFICATION"][0]
