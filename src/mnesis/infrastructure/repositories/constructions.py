"""
Dépôt des constructions linguistiques de Mnesis.

Rôle :
    Persister et relire les constructions déclaratives en garantissant leur
    isolation par instance et la conservation de leur provenance.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from mnesis.infrastructure.db import ConstructionRecord
from mnesis.language.constructions import InputConstruction


class ConstructionRepository:
    """Fournit la persistance des constructions linguistiques déclaratives."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initialise le dépôt avec la fabrique de sessions SQLAlchemy fournie."""
        self._session_factory = session_factory

    def add(
        self,
        instance_id: UUID | None,
        construction: InputConstruction,
    ) -> InputConstruction:
        """Persiste une construction pour une instance ou un socle global."""
        with self._session_factory.begin() as session:
            session.add(
                ConstructionRecord(
                    id=construction.id,
                    instance_id=str(instance_id) if instance_id else None,
                    language=construction.language.casefold(),
                    pattern=construction.pattern,
                    semantics=construction.semantics,
                    confidence=construction.confidence,
                    origin=construction.origin,
                    usage_count=construction.usage_count,
                    reinforced_at=(
                        construction.reinforced_at.isoformat()
                        if construction.reinforced_at is not None
                        else None
                    ),
                )
            )
        return construction


    def get(
        self,
        instance_id: UUID,
        construction_id: str,
    ) -> InputConstruction | None:
        """Retourne une construction locale par identifiant ou None."""
        with self._session_factory() as session:
            record = session.get(ConstructionRecord, construction_id)
            if record is None or record.instance_id != str(instance_id):
                return None
            return self._to_domain(record)

    def update(
        self,
        instance_id: UUID,
        construction: InputConstruction,
    ) -> InputConstruction:
        """Met à jour une construction existante appartenant à l'instance."""
        with self._session_factory.begin() as session:
            record = session.get(ConstructionRecord, construction.id)
            if record is None or record.instance_id != str(instance_id):
                raise ValueError("Construction introuvable pour cette instance.")
            record.pattern = construction.pattern
            record.semantics = construction.semantics
            record.confidence = construction.confidence
            record.origin = construction.origin
            record.usage_count = construction.usage_count
            record.reinforced_at = (
                construction.reinforced_at.isoformat()
                if construction.reinforced_at is not None
                else None
            )
        return construction

    def list_for_instance(
        self,
        instance_id: UUID,
        language: str,
    ) -> list[InputConstruction]:
        """Liste les constructions locales d'une instance pour une langue."""
        with self._session_factory() as session:
            records = session.scalars(
                select(ConstructionRecord)
                .where(
                    ConstructionRecord.instance_id == str(instance_id),
                    ConstructionRecord.language == language.casefold(),
                )
                .order_by(ConstructionRecord.id)
            ).all()
        return [self._to_domain(record) for record in records]

    @staticmethod
    def _to_domain(record: ConstructionRecord) -> InputConstruction:
        """Reconstruit une construction de domaine depuis une ligne SQLAlchemy."""
        return InputConstruction(
            id=record.id,
            language=record.language,
            pattern=record.pattern,
            semantics=record.semantics,
            confidence=record.confidence,
            origin=record.origin,
            usage_count=record.usage_count,
            reinforced_at=(
                datetime.fromisoformat(record.reinforced_at)
                if record.reinforced_at
                else None
            ),
        )
