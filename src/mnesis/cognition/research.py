"""
Exécution des objectifs de recherche de Mnesis.

Rôle :
    Router un objectif cognitif de recherche vers la source spécialisée adaptée,
    sans faire dépendre le cycle conversationnel des fournisseurs externes.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from mnesis.application.learning import LexicalLearningService
from mnesis.semantic.frames import SemanticFrame


class ResearchOutcome(BaseModel):
    """Résultat sémantique et apprentissages produits par une recherche."""

    semantic_output: SemanticFrame
    learned_items: list[str] = Field(default_factory=list)


class ResearchExecutor:
    """Exécute les catégories de recherche cognitives supportées par la V1."""

    def __init__(self, lexical_learning: LexicalLearningService) -> None:
        """Initialise l'exécuteur avec le service d'apprentissage lexical."""
        self._lexical_learning = lexical_learning

    def execute(self, instance_id: UUID, goal: dict[str, object]) -> ResearchOutcome:
        """Exécute un objectif de recherche explicite et retourne son résultat."""
        kind = goal.get("kind")
        term = goal.get("term")
        if kind != "LEXICAL" or not isinstance(term, str) or not term:
            return ResearchOutcome(
                semantic_output=SemanticFrame(type="CLARIFICATION", slots={})
            )
        learned = self._lexical_learning.learn_unknown_word(instance_id, term)
        if not learned.success:
            return ResearchOutcome(
                semantic_output=SemanticFrame(type="CLARIFICATION", slots={})
            )
        items = [
            str(item)
            for item in (learned.lexeme_id, learned.concept_id)
            if item is not None
        ]
        return ResearchOutcome(
            semantic_output=SemanticFrame(
                type="LEARNING_EVENT",
                slots={"kind": "LEXICAL", "term": term.casefold()},
                confidence=0.65,
                provenance=["research:lexical"],
            ),
            learned_items=items,
        )
