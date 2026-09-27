"""
Interpréteur linguistique déclaratif de Mnesis.

Rôle :
    Appliquer les constructions disponibles à un énoncé et retourner toutes les
    représentations sémantiques candidates sans connaître leur signification métier.
"""

from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.semantic.frames import SemanticFrame


class LanguageInterpreter:
    """Transforme du texte en frames via les seules constructions déclaratives."""

    def interpret(
        self,
        text: str,
        constructions: ConstructionSet,
        lexicon: Lexicon,
    ) -> list[SemanticFrame]:
        """
        Interprète un texte selon les constructions actives.

        Paramètres :
            text:
                Énoncé utilisateur brut.
            constructions:
                Ensemble de constructions disponibles.
            lexicon:
                Lexique courant de l'instance.

        Retour :
            Toutes les interprétations candidates, dans un ordre déterministe.
        """
        frames = [match.frame for match in constructions.match(text, lexicon)]
        if frames:
            return frames

        tokens = [
            token.strip("?!.,;:").casefold()
            for token in text.strip().split()
            if token.strip("?!.,;:")
        ]
        if len(tokens) == 1 and not lexicon.contains(tokens[0]):
            return [
                SemanticFrame(
                    type="KNOWLEDGE_GAP",
                    slots={"kind": "LEXICAL", "term": tokens[0]},
                    confidence=1.0,
                    provenance=["interpreter:unknown-token"],
                )
            ]
        return []
