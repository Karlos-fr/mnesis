"""
Apprentissage local de constructions linguistiques.

Rôle :
    Créer puis renforcer des associations forme → sens propres à une instance,
    afin qu'elles deviennent utilisables après accumulation de confiance.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from mnesis.infrastructure.repositories.constructions import ConstructionRepository
from mnesis.language.constructions import InputConstruction
from mnesis.semantic.frames import SemanticFrame

USABLE_CONSTRUCTION_CONFIDENCE = 0.70
_INITIAL_CONSTRUCTION_CONFIDENCE = 0.50
_REINFORCEMENT_STEP = 0.25


class ConstructionLearningService:
    """Enseigne et renforce des constructions locales à une instance Mnesis."""

    def __init__(self, repository: ConstructionRepository) -> None:
        """Initialise le service avec le dépôt persistant des constructions."""
        self._repository = repository

    def teach(
        self,
        instance_id: UUID,
        form: str,
        semantic_frame: SemanticFrame,
        source: str,
    ) -> InputConstruction:
        """Crée une hypothèse locale de construction sous le seuil d'utilisation."""
        tokens = [token.casefold() for token in form.strip().split() if token.strip()]
        if not tokens:
            raise ValueError("La forme enseignée ne peut pas être vide.")
        construction = InputConstruction(
            id=f"learned-{uuid4()}",
            language="fr",
            pattern=[{"literal": token} for token in tokens],
            semantics=semantic_frame.model_dump(include={"type", "slots"}),
            confidence=_INITIAL_CONSTRUCTION_CONFIDENCE,
            origin=f"learned:{source}",
        )
        return self._repository.add(instance_id, construction)

    def reinforce(
        self,
        instance_id: UUID,
        construction_id: str,
        evidence: str,
    ) -> InputConstruction:
        """Renforce une construction existante après une confirmation."""
        construction = self._repository.get(instance_id, construction_id)
        if construction is None:
            raise ValueError("Construction à renforcer introuvable.")
        updated = construction.model_copy(
            update={
                "confidence": min(1.0, construction.confidence + _REINFORCEMENT_STEP),
                "reinforced_at": datetime.now(UTC),
                "origin": f"{construction.origin}|reinforced:{evidence}",
            }
        )
        return self._repository.update(instance_id, updated)
