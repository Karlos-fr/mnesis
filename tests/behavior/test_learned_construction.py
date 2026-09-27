"""
Tests d'apprentissage local de constructions linguistiques.

Rôle :
    Prouver qu'une expression inconnue peut être enseignée, renforcée puis
    utilisée par une seule instance sans modification du moteur ni de core-fr.
"""

from mnesis.api.app import create_app
from mnesis.application.construction_learning import (
    USABLE_CONSTRUCTION_CONFIDENCE,
    ConstructionLearningService,
)
from mnesis.domain.instances import MnesisInstance
from mnesis.semantic.frames import SemanticFrame


def test_taught_construction_becomes_usable_after_reinforcement() -> None:
    """Vérifie le cycle inconnu → enseigné → renforcé → compris."""
    app = create_app("sqlite+pysqlite:///:memory:")
    services = app.state.services
    first = services.instances.create(MnesisInstance.create("A"))
    second = services.instances.create(MnesisInstance.create("B"))
    learning = ConstructionLearningService(services.constructions)

    before = services.conversation.handle(first.id, "Ça roule ?")
    assert "pas certain" in before.response_text

    learned = learning.teach(
        first.id,
        "Ça roule ?",
        SemanticFrame(type="QUERY", slots={"kind": "INTERLOCUTOR_STATE"}),
        source="user://teaching/1",
    )
    assert learned.confidence < USABLE_CONSTRUCTION_CONFIDENCE

    before_threshold = services.conversation.handle(first.id, "Ça roule ?")
    assert "pas certain" in before_threshold.response_text

    reinforced = learning.reinforce(
        first.id,
        learned.id,
        evidence="user://confirmation/2",
    )
    assert reinforced.confidence >= USABLE_CONSTRUCTION_CONFIDENCE

    turn = services.conversation.handle(first.id, "Ça roule ?")
    assert turn.response_text == "Comment vas-tu ?"

    isolated = services.conversation.handle(second.id, "Ça roule ?")
    assert "pas certain" in isolated.response_text
