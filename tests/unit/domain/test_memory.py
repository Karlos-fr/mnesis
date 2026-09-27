"""
Tests des modèles de mémoire et de trace cognitive.

Rôle :
    Vérifier que les épisodes et traces conservent les informations nécessaires
    à l'explication des décisions de Mnesis.
"""

from datetime import UTC, datetime
from uuid import uuid4

from mnesis.domain.memory import Episode
from mnesis.domain.traces import DecisionTrace


def test_episode_keeps_context_and_recall_metadata() -> None:
    """Vérifie qu'un épisode conserve contexte, importance et rappel."""
    episode = Episode(instance_id=uuid4(), occurred_at=datetime.now(UTC), summary="Discussion sur un projet", importance=0.7, affect={"joy": 0.6})
    assert episode.recall_count == 0
    assert episode.accessibility == 1.0
    assert episode.importance == 0.7


def test_decision_trace_records_consulted_state() -> None:
    """Vérifie qu'une trace relie concepts, croyances, souvenirs et décision."""
    trace = DecisionTrace(instance_id=uuid4(), action="RÉPONDRE", candidate_actions={"RÉPONDRE": 0.9, "RELANCER": 0.3}, consulted_concepts=[uuid4()], consulted_claims=[uuid4()], recalled_memories=[uuid4()], affect_snapshot={"curiosity": 0.7})
    assert trace.action == "RÉPONDRE"
    assert trace.candidate_actions["RÉPONDRE"] == 0.9
    assert trace.consulted_concepts
