"""
Dépôt des connaissances persistantes de Mnesis.

Rôle :
    Persister les affirmations en imposant leur rattachement explicite à une
    instance afin d'empêcher toute fuite de connaissances entre instances.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, Evidence, KnowledgeOrigin
from mnesis.domain.language import Lexeme, LexicalSense, MasteryLevel
from mnesis.infrastructure.db import ClaimRecord, ConceptRecord, LexemeRecord


class KnowledgeRepository:
    """Fournit les opérations de persistance des affirmations sémantiques."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initialise le dépôt avec la fabrique de sessions fournie."""
        self._session_factory = session_factory

    def find_concept(self, instance_id: UUID, label: str) -> Concept | None:
        """Recherche un concept par libellé dans une instance."""
        with self._session_factory() as session:
            record = session.scalars(select(ConceptRecord).where(ConceptRecord.instance_id == str(instance_id), ConceptRecord.label == label.casefold()).limit(1)).first()
        return None if record is None else Concept(id=UUID(record.id), kind=record.kind, label=record.label)

    def get_concept(self, instance_id: UUID, concept_id: UUID) -> Concept | None:
        """Retourne un concept par identifiant s'il appartient à l'instance."""
        with self._session_factory() as session:
            record = session.scalars(select(ConceptRecord).where(ConceptRecord.instance_id == str(instance_id), ConceptRecord.id == str(concept_id)).limit(1)).first()
        return None if record is None else Concept(id=UUID(record.id), kind=record.kind, label=record.label)

    def list_claims_for_subject(self, instance_id: UUID, subject_id: UUID, predicate: str | None = None) -> list[Claim]:
        """Liste les affirmations d'un sujet, éventuellement filtrées par prédicat."""
        with self._session_factory() as session:
            query = select(ClaimRecord).where(ClaimRecord.instance_id == str(instance_id), ClaimRecord.subject_id == str(subject_id))
            if predicate is not None:
                query = query.where(ClaimRecord.predicate == predicate)
            records = session.scalars(query).all()
        return [self._to_domain(record) for record in records]

    def add_concept(self, instance_id: UUID, concept: Concept) -> Concept:
        """Persiste un concept local à une instance et le retourne inchangé."""
        with self._session_factory.begin() as session:
            session.add(ConceptRecord(id=str(concept.id), instance_id=str(instance_id), kind=concept.kind, label=concept.label.casefold()))
        return concept

    def add_lexeme(self, instance_id: UUID, lexeme: Lexeme) -> Lexeme:
        """Persiste un lexème et ses liens vers des concepts pour une instance."""
        with self._session_factory.begin() as session:
            session.add(LexemeRecord(id=str(lexeme.id), instance_id=str(instance_id), surface=lexeme.surface, lemma=lexeme.lemma, language=lexeme.language, part_of_speech=lexeme.part_of_speech, senses=[sense.model_dump(mode="json") for sense in lexeme.senses], mastery=lexeme.mastery.value))
        return lexeme

    def find_lexeme(self, instance_id: UUID, word: str) -> Lexeme | None:
        """Recherche un lexème par forme ou lemme dans une instance donnée."""
        normalized = word.casefold()
        with self._session_factory() as session:
            record = session.scalars(select(LexemeRecord).where(LexemeRecord.instance_id == str(instance_id), (LexemeRecord.lemma == normalized) | (LexemeRecord.surface == normalized)).limit(1)).first()
        if record is None:
            return None
        return Lexeme(id=UUID(record.id), surface=record.surface, lemma=record.lemma, language=record.language, part_of_speech=record.part_of_speech, senses=[LexicalSense.model_validate(item) for item in record.senses], mastery=MasteryLevel(record.mastery))

    def add_claim(self, instance_id: UUID, claim: Claim) -> Claim:
        """Persiste une affirmation pour l'instance donnée et la retourne inchangée."""
        record = ClaimRecord(
            id=str(claim.id),
            instance_id=str(instance_id),
            subject_id=str(claim.subject_id),
            predicate=claim.predicate,
            object_id=str(claim.object_id) if claim.object_id else None,
            literal=claim.literal,
            confidence=claim.confidence,
            status=claim.status.value,
            origin=claim.origin.value,
            evidence=[item.model_dump(mode="json") for item in claim.evidence],
        )
        with self._session_factory.begin() as session:
            session.add(record)
        return claim

    def list_claims(self, instance_id: UUID) -> list[Claim]:
        """Retourne uniquement les affirmations appartenant à l'instance donnée."""
        with self._session_factory() as session:
            records = session.scalars(
                select(ClaimRecord).where(ClaimRecord.instance_id == str(instance_id))
            ).all()
        return [self._to_domain(record) for record in records]

    @staticmethod
    def _to_domain(record: ClaimRecord) -> Claim:
        """Reconstruit une affirmation de domaine depuis son enregistrement SQL."""
        return Claim(
            id=UUID(record.id),
            subject_id=UUID(record.subject_id),
            predicate=record.predicate,
            object_id=UUID(record.object_id) if record.object_id else None,
            literal=record.literal,
            confidence=record.confidence,
            status=ClaimStatus(record.status),
            origin=KnowledgeOrigin(record.origin),
            evidence=[Evidence.model_validate(item) for item in record.evidence],
        )
