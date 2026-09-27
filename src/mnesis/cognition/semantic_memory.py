"""
Pont générique entre frames sémantiques et mémoire de connaissances.

Rôle :
    Persister et récupérer des relations conceptuelles sans dépendre d'une
    langue, d'une formulation ou d'une intention conversationnelle.
"""

from uuid import UUID

from mnesis.application.beliefs import BeliefEngine
from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, KnowledgeOrigin
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.semantic.frames import SemanticFrame


class SemanticMemory:
    """Expose STORE/RETRIEVE sur le graphe conceptuel persistant d'une instance."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        """Initialise le pont avec le dépôt de connaissances fourni."""
        self._repository = repository
        self._beliefs = BeliefEngine()

    def store(self, instance_id: UUID, frame: SemanticFrame) -> list[UUID]:
        """Persiste une relation décrite par un frame sémantique."""
        subject_label = frame.slots.get("subject")
        predicate = frame.slots.get("predicate")
        object_label = frame.slots.get("object")
        if not all(
            isinstance(value, str) and value
            for value in (subject_label, predicate, object_label)
        ):
            raise ValueError(
                "Le frame à stocker doit fournir subject, predicate et object."
            )
        subject = self._ensure_concept(instance_id, subject_label, "entity")
        obj = self._ensure_concept(instance_id, object_label, "concept")
        claim = self._repository.add_claim(
            instance_id,
            Claim(
                subject_id=subject.id,
                predicate=predicate,
                object_id=obj.id,
                confidence=min(frame.confidence, 0.65),
                status=ClaimStatus.ACCEPTED,
                origin=KnowledgeOrigin.USER,
            ),
        )
        return [subject.id, obj.id, claim.id]

    def retrieve(
        self,
        instance_id: UUID,
        query: dict[str, object],
    ) -> SemanticFrame | None:
        """Récupère la meilleure relation correspondant à une requête générique."""
        subject_label = query.get("subject_label")
        predicate = query.get("predicate")
        if not isinstance(subject_label, str) or not isinstance(predicate, str):
            return None
        subject = self._repository.find_concept(instance_id, subject_label.casefold())
        if subject is None:
            return None
        claims = self._repository.list_claims_for_subject(instance_id, subject.id, predicate)
        if not claims:
            return None
        assessment = self._beliefs.evaluate(claims)
        preferred = next(
            claim for claim in claims if claim.id == assessment.preferred_claim_id
        )
        if preferred.object_id is None:
            return None
        obj = self._repository.get_concept(instance_id, preferred.object_id)
        if obj is None:
            return None
        frame_type = (
            "UNCERTAIN_PROPOSITION"
            if assessment.status is ClaimStatus.CONFLICTED
            else "PROPOSITION"
        )
        return SemanticFrame(
            type=frame_type,
            slots={
                "predicate": predicate,
                "subject": subject.label,
                "object": obj.label,
            },
            confidence=assessment.confidence,
            provenance=[f"claim:{claim_id}" for claim_id in assessment.all_claim_ids],
        )

    def _ensure_concept(
        self,
        instance_id: UUID,
        label: str,
        kind: str,
    ) -> Concept:
        """Retourne un concept existant ou en crée un localement."""
        existing = self._repository.find_concept(instance_id, label.casefold())
        if existing is not None:
            return existing
        return self._repository.add_concept(
            instance_id,
            Concept(kind=kind, label=label.casefold()),
        )
