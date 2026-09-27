"""
Tests de persistance de la mémoire épisodique.

Rôle :
    Vérifier qu'un épisode reste rattaché à son instance et peut être relu.
"""

from datetime import UTC, datetime

from mnesis.domain.instances import MnesisInstance
from mnesis.domain.memory import Episode
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository


def test_episode_is_persisted_for_its_instance() -> None:
    """Vérifie qu'un épisode persistant est récupéré uniquement pour son instance."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    memories = MemoryRepository(database.session_factory)
    instance = instances.create(MnesisInstance.create("Personnel"))
    other = instances.create(MnesisInstance.create("Autre"))
    episode = Episode(instance_id=instance.id, occurred_at=datetime.now(UTC), summary="Bonjour", importance=0.4, affect={"joy": 0.5})
    memories.add_episode(instance.id, episode)
    assert memories.recent(instance.id, 10) == [episode]
    assert memories.recent(other.id, 10) == []
