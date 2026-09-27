"""
Tests d'isolation des instances dans la persistance.

Rôle :
    Garantir qu'une connaissance locale à une instance ne peut pas être lue
    depuis une autre instance Mnesis.
"""

from uuid import uuid4

from mnesis.domain.instances import MnesisInstance
from mnesis.domain.knowledge import Claim, ClaimStatus, KnowledgeOrigin
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository


def test_learning_in_one_instance_does_not_leak_to_another() -> None:
    """Vérifie l'isolation stricte des affirmations entre deux instances."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    knowledge = KnowledgeRepository(database.session_factory)

    first = instances.create(MnesisInstance.create("Personnel"))
    second = instances.create(MnesisInstance.create("Public"))
    claim = Claim(
        subject_id=uuid4(),
        predicate="EST_UN",
        literal="concept privé",
        confidence=0.8,
        status=ClaimStatus.ACCEPTED,
        origin=KnowledgeOrigin.USER,
    )

    knowledge.add_claim(first.id, claim)

    assert knowledge.list_claims(first.id) == [claim]
    assert knowledge.list_claims(second.id) == []
