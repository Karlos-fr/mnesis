"""
Dépôt des traces de décision cognitive.

Rôle :
    Persister les explications techniques d'une décision afin qu'elles soient
    consultables sans encombrer la conversation principale.
"""

from uuid import UUID

from sqlalchemy.orm import sessionmaker

from mnesis.domain.traces import DecisionTrace
from mnesis.infrastructure.db import TraceRecord


class TraceRepository:
    """Persiste et relit les traces de décision d'une instance."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initialise le dépôt avec une fabrique de sessions SQLAlchemy."""
        self._session_factory = session_factory

    def add(self, trace: DecisionTrace) -> DecisionTrace:
        """Persiste une trace et retourne l'objet de domaine inchangé."""
        with self._session_factory.begin() as session:
            session.add(
                TraceRecord(
                    id=str(trace.id),
                    instance_id=str(trace.instance_id),
                    action=trace.action,
                    confidence=trace.confidence,
                    candidate_actions=trace.candidate_actions,
                    consulted_concepts=[str(value) for value in trace.consulted_concepts],
                    consulted_claims=[str(value) for value in trace.consulted_claims],
                    recalled_memories=[str(value) for value in trace.recalled_memories],
                    affect_snapshot=trace.affect_snapshot,
                )
            )
        return trace

    def get(self, instance_id: UUID, trace_id: UUID) -> DecisionTrace | None:
        """Retourne une trace uniquement si elle appartient à l'instance demandée."""
        with self._session_factory() as session:
            record = session.get(TraceRecord, str(trace_id))
            if record is None or record.instance_id != str(instance_id):
                return None
            return DecisionTrace(
                id=UUID(record.id),
                instance_id=UUID(record.instance_id),
                action=record.action,
                confidence=record.confidence,
                candidate_actions=record.candidate_actions,
                consulted_concepts=[UUID(value) for value in record.consulted_concepts],
                consulted_claims=[UUID(value) for value in record.consulted_claims],
                recalled_memories=[UUID(value) for value in record.recalled_memories],
                affect_snapshot=record.affect_snapshot,
            )
