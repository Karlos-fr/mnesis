"""
Tests d'isolation des constructions linguistiques.

Rôle :
    Garantir qu'une construction apprise ou ajoutée localement à une instance
    n'est jamais visible depuis une autre instance.
"""

from mnesis.domain.instances import MnesisInstance
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.repositories.constructions import ConstructionRepository
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.language.constructions import InputConstruction


def test_construction_is_isolated_between_instances() -> None:
    """Vérifie qu'une construction locale à A reste absente de B."""
    database = create_database("sqlite+pysqlite:///:memory:")
    create_schema(database.engine)
    instances = InstanceRepository(database.session_factory)
    first = instances.create(MnesisInstance.create("A"))
    second = instances.create(MnesisInstance.create("B"))
    repository = ConstructionRepository(database.session_factory)
    construction = InputConstruction(
        id="learned-ca-roule",
        language="fr",
        pattern=[{"literal": "ça"}, {"literal": "roule"}],
        semantics={"type": "QUERY", "slots": {"kind": "INTERLOCUTOR_STATE"}},
        confidence=0.72,
        origin="learned",
    )

    repository.add(first.id, construction)

    assert repository.list_for_instance(first.id, "fr") == [construction]
    assert repository.list_for_instance(second.id, "fr") == []
