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
        """Réalise une définition simple sous la forme « Un X est un Y »."""
        return f"Un {subject} est un {obj}."

    def uncertain_definition(self, subject: str, obj: str) -> str:
        """Exprime explicitement le doute tout en donnant l'hypothèse préférée."""
        return (
            "Je ne suis pas certain, mais les éléments les plus fiables indiquent "
            f"qu'un {subject} est un {obj}."
        )

    def lexical_definition(self, word: str, definition: str) -> str:
        """Restitue une définition lexicale acquise depuis une source extérieure."""
        return f"D'après ce que j'ai appris, « {word} » signifie : {definition}"

    def learned_word(self, word: str) -> str:
        """Signale qu'un mot inconnu vient d'être acquis par Mnesis."""
        return f"J'ai appris le mot « {word} »."

    def follow_up(self) -> str:
        """Retourne une formulation de relance issue du socle linguistique."""
        return self._responses["RELANCER"][0]

    def clarification(self) -> str:
        """Retourne la formulation de clarification configurée dans le socle."""
        return self._responses["DEMANDER_CLARIFICATION"][0]
