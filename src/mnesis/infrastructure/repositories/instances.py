"""
Dépôt de persistance des instances Mnesis.

Rôle :
    Enregistrer et relire les informations propres à une instance sans exposer
    SQLAlchemy au domaine cognitif.
"""

from uuid import UUID

from sqlalchemy.orm import sessionmaker

from mnesis.domain.affect import AffectState, Personality
from mnesis.domain.instances import MnesisInstance
from mnesis.infrastructure.db import InstanceRecord


class InstanceRepository:
    """Fournit les opérations de persistance des instances Mnesis."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initialise le dépôt avec la fabrique de sessions fournie."""
        self._session_factory = session_factory

    def create(self, instance: MnesisInstance) -> MnesisInstance:
        """Persiste une nouvelle instance et retourne l'objet de domaine inchangé."""
        record = InstanceRecord(
            id=str(instance.id),
            name=instance.name,
            locale=instance.locale,
            personality=instance.personality.model_dump(mode="json"),
            affect=instance.affect.model_dump(mode="json"),
        )
        with self._session_factory.begin() as session:
            session.add(record)
        return instance

    def get(self, instance_id: UUID) -> MnesisInstance | None:
        """Retourne l'instance demandée ou None lorsqu'elle n'existe pas."""
        with self._session_factory() as session:
            record = session.get(InstanceRecord, str(instance_id))
            if record is None:
                return None
            return MnesisInstance(
                id=UUID(record.id),
                name=record.name,
                locale=record.locale,
                personality=Personality.model_validate(record.personality),
                affect=AffectState.model_validate(record.affect),
            )
