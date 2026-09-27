"""
Dépôt des connaissances persistantes de Mnesis.

Rôle :
    Persister les affirmations en imposant leur rattachement explicite à une
    instance afin d'empêcher toute fuite de connaissances entre instances.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from mnesis.domain.knowledge import Claim, ClaimStatus, Evidence, KnowledgeOrigin
from mnesis.infrastructure.db import ClaimRecord


class KnowledgeRepository:
    """Fournit les opérations de persistance des affirmations sémantiques."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initialise le dépôt avec la fabrique de sessions fournie."""
        self._session_factory = session_factory

    def add_claim(self, instance_id: UUID, claim: Claim) -> Claim:
        """Persiste une affirmation pour l'instance donnée et la retourne inchangée."""
        record = ClaimRecord(
            id=str(claim.id),
            instance_id=str(instance_id),
            subject_id=str(claim.subject_id),
            predicate=claim.predicate,
            object_id=str(claim.object_id) if claim.object_id else None,
            literal=claim.literal,
            confidence=claim.confidence,
            status=claim.status.value,
            origin=claim.origin.value,
            evidence=[item.model_dump(mode="json") for item in claim.evidence],
        )
        with self._session_factory.begin() as session:
            session.add(record)
        return claim

    def list_claims(self, instance_id: UUID) -> list[Claim]:
        """Retourne uniquement les affirmations appartenant à l'instance donnée."""
        with self._session_factory() as session:
            records = session.scalars(
                select(ClaimRecord).where(ClaimRecord.instance_id == str(instance_id))
            ).all()
        return [self._to_domain(record) for record in records]

    @staticmethod
    def _to_domain(record: ClaimRecord) -> Claim:
        """Reconstruit une affirmation de domaine depuis son enregistrement SQL."""
        return Claim(
            id=UUID(record.id),
            subject_id=UUID(record.subject_id),
            predicate=record.predicate,
            object_id=UUID(record.object_id) if record.object_id else None,
            literal=record.literal,
            confidence=record.confidence,
            status=ClaimStatus(record.status),
            origin=KnowledgeOrigin(record.origin),
            evidence=[Evidence.model_validate(item) for item in record.evidence],
        )
