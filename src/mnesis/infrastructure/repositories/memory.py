"""
Dépôt de mémoire épisodique de Mnesis.

Rôle :
    Persister et relire les épisodes d'une instance tout en maintenant une
    isolation stricte entre les historiques des différentes instances.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import sessionmaker

from mnesis.domain.memory import Episode
from mnesis.infrastructure.db import EpisodeRecord


class MemoryRepository:
    """Fournit les opérations de persistance de la mémoire épisodique."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initialise le dépôt avec une fabrique de sessions SQLAlchemy."""
        self._session_factory = session_factory

    def add_episode(self, instance_id: UUID, episode: Episode) -> Episode:
        """Persiste un épisode pour une instance et retourne l'objet inchangé."""
        if episode.instance_id != instance_id:
            raise ValueError("L'épisode doit appartenir à l'instance cible.")
        with self._session_factory.begin() as session:
            session.add(EpisodeRecord(
                id=str(episode.id), instance_id=str(instance_id),
                occurred_at=episode.occurred_at.isoformat(), summary=episode.summary,
                importance=episode.importance, affect=episode.affect,
                recall_count=episode.recall_count, accessibility=episode.accessibility,
            ))
        return episode

    def recent(self, instance_id: UUID, limit: int) -> list[Episode]:
        """Retourne les épisodes les plus récents de l'instance demandée."""
        with self._session_factory() as session:
            records = session.scalars(
                select(EpisodeRecord).where(EpisodeRecord.instance_id == str(instance_id))
                .order_by(desc(EpisodeRecord.occurred_at)).limit(limit)
            ).all()
        return [Episode(
            id=UUID(record.id), instance_id=UUID(record.instance_id),
            occurred_at=datetime.fromisoformat(record.occurred_at), summary=record.summary,
            importance=record.importance, affect=record.affect,
            recall_count=record.recall_count, accessibility=record.accessibility,
        ) for record in records]
