"""
Tests de l'exécuteur de procédures primitives.

Rôle :
    Vérifier que les actions génériques sont transformées en résultats
    sémantiques ou effets explicites sans procédure conversationnelle métier.
"""

from mnesis.cognition.actions import ActionCandidate
from mnesis.cognition.procedures import ProcedureExecutor


def _action(action_type: str, payload: dict) -> ActionCandidate:
    """Construit une action candidate minimale pour les tests."""
    return ActionCandidate(
        rule_id="test",
        action_type=action_type,
        payload=payload,
        base_score=0.5,
        score=0.5,
    )


def test_assert_produces_semantic_frame() -> None:
    """Vérifie qu'ASSERT produit la proposition portée par son payload."""
    result = ProcedureExecutor().execute(
        _action(
            "ASSERT",
            {
                "type": "PROPOSITION",
                "slots": {"predicate": "IS_A", "subject": "chat", "object": "animal"},
            },
        ),
        {},
    )
    assert result.semantic_output is not None
    assert result.semantic_output.type == "PROPOSITION"
    assert result.semantic_output.slots["predicate"] == "IS_A"


def test_ask_produces_query_frame() -> None:
    """Vérifie qu'ASK produit une requête sémantique."""
    result = ProcedureExecutor().execute(
        _action("ASK", {"type": "QUERY", "slots": {"kind": "INTERLOCUTOR_STATE"}}),
        {},
    )
    assert result.semantic_output is not None
    assert result.semantic_output.type == "QUERY"


def test_store_requests_explicit_side_effect() -> None:
    """Vérifie que STORE demande une persistance plutôt que de la cacher."""
    result = ProcedureExecutor().execute(
        _action("STORE", {"type": "PROPOSITION", "slots": {"predicate": "IS_A"}}),
        {},
    )
    assert result.semantic_output is None
    assert result.side_effects[0]["type"] == "STORE_FRAME"


def test_research_produces_research_goal_side_effect() -> None:
    """Vérifie que RESEARCH produit un objectif explicite pour un exécuteur dédié."""
    result = ProcedureExecutor().execute(
        _action("RESEARCH", {"kind": "LEXICAL", "term": "arboricole"}),
        {},
    )
    assert result.semantic_output is None
    assert result.side_effects == [
        {"type": "RESEARCH", "goal": {"kind": "LEXICAL", "term": "arboricole"}}
    ]


def test_store_uses_injected_semantic_memory_callback() -> None:
    """Vérifie que STORE délègue la persistance au contexte générique."""
    stored: list[str] = []
    frame = {
        "type": "PROPOSITION",
        "slots": {"predicate": "IS_A", "subject": "chat", "object": "animal"},
    }

    def store_frame(value):
        stored.append(value.slots["subject"])
        return ["claim-1"]

    result = ProcedureExecutor().execute(
        _action("STORE", {"from_frame": True}),
        {"input_frames": [frame], "store_frame": store_frame},
    )
    assert stored == ["chat"]
    assert result.semantic_output is not None
    assert result.learned_items == ["claim-1"]


def test_retrieve_uses_injected_semantic_memory_callback() -> None:
    """Vérifie que RETRIEVE délègue la requête à la mémoire sémantique injectée."""
    def retrieve(query):
        assert query == {"subject_label": "chat", "predicate": "IS_A"}
        return {
            "type": "PROPOSITION",
            "slots": {"predicate": "IS_A", "subject": "chat", "object": "animal"},
        }

    result = ProcedureExecutor().execute(
        _action("RETRIEVE", {"subject_label": "chat", "predicate": "IS_A"}),
        {"retrieve": retrieve},
    )
    assert result.semantic_output is not None
    assert result.semantic_output.slots["object"] == "animal"
