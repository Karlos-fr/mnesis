"""
Tests comportementaux de la conversation Mnesis.

Rôle :
    Vérifier que le cycle générique sait saluer, mémoriser une relation et la
    rappeler ensuite à partir des seules données de core-fr.
"""

from mnesis.api.app import create_app
from mnesis.domain.affect import AffectState, Personality
from mnesis.domain.instances import MnesisInstance


def _service():
    """Construit une application en mémoire et retourne instance, service et traces."""
    app = create_app("sqlite+pysqlite:///:memory:")
    services = app.state.services
    instance = services.instances.create(MnesisInstance.create("Test"))
    return instance, services.conversation, services.traces


def test_greeting_returns_french_response() -> None:
    """Vérifie qu'une salutation est interprétée et réalisée depuis core-fr."""
    instance, service, _ = _service()
    turn = service.handle(instance.id, "Bonjour")
    assert turn.response_text == "Bonjour."
    assert turn.trace_id is not None


def test_definition_is_stored_and_recalled_later() -> None:
    """Vérifie qu'une relation enseignée est persistée puis récupérée."""
    instance, service, _ = _service()
    learned = service.handle(instance.id, "chat est un animal")
    recalled = service.handle(instance.id, "Qu'est-ce qu'un chat ?")
    assert learned.response_text == "Un chat est un animal."
    assert recalled.response_text == "Un chat est un animal."
    assert len(service.memories.recent(instance.id, 10)) == 2


def test_high_curiosity_and_extraversion_change_action_scoring() -> None:
    """Vérifie que l'état interne modifie le score sans branche métier."""
    app = create_app("sqlite+pysqlite:///:memory:")
    services = app.state.services
    instance = services.instances.create(
        MnesisInstance(
            id=MnesisInstance.create("temp").id,
            name="Curieuse",
            locale="fr-FR",
            personality=Personality(curiosity=0.95, extraversion=0.8),
            affect=AffectState(curiosity=0.95),
        )
    )
    turn = services.conversation.handle(instance.id, "Bonjour")
    trace = services.traces.get(instance.id, turn.trace_id)
    assert turn.response_text == "Comment vas-tu ?"
    assert trace is not None
    assert trace.action == "ASK"
    assert trace.affect_snapshot["curiosity"] == 0.95
