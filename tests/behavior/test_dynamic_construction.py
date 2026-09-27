"""
Test d'ajout dynamique d'une construction conversationnelle.

Rôle :
    Prouver qu'une nouvelle formulation peut devenir compréhensible sans
    modification du code Python du moteur cognitif.
"""

from mnesis.api.app import create_app
from mnesis.domain.instances import MnesisInstance
from mnesis.language.constructions import InputConstruction


def test_coucou_is_understood_after_data_only_construction_is_added() -> None:
    """Vérifie qu'une construction ajoutée localement est prise en compte à chaud."""
    app = create_app("sqlite+pysqlite:///:memory:")
    services = app.state.services
    instance = services.instances.create(MnesisInstance.create("Test"))
    services.constructions.add(
        instance.id,
        InputConstruction(
            id="local-coucou",
            language="fr",
            pattern=[{"literal": "coucou"}],
            semantics={"type": "SOCIAL_ACT", "slots": {"act": "GREETING"}},
            confidence=0.9,
            origin="learned",
        ),
    )

    turn = services.conversation.handle(instance.id, "Coucou")

    assert turn.response_text == "Bonjour."
