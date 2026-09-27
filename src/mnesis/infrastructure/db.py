"""
Infrastructure de persistance SQL de Mnesis.

Rôle :
    Configurer SQLAlchemy et définir le schéma relationnel minimal de la V1.
    La configuration reste portable afin de faciliter une migration future
    de SQLite vers PostgreSQL.
"""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """Base déclarative commune aux enregistrements SQLAlchemy de Mnesis."""


class InstanceRecord(Base):
    """Enregistrement persistant d'une instance Mnesis."""

    __tablename__ = "instances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    locale: Mapped[str] = mapped_column(String(32), nullable=False)
    personality: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    affect: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class ConceptRecord(Base):
    """Concept sémantique local à une instance."""

    __tablename__ = "concepts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    instance_id: Mapped[str] = mapped_column(String(36), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)


class LexemeRecord(Base):
    """Forme lexicale locale à une instance et liens vers ses concepts."""

    __tablename__ = "lexemes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    instance_id: Mapped[str] = mapped_column(String(36), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, index=True)
    surface: Mapped[str] = mapped_column(String(255), nullable=False)
    lemma: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    part_of_speech: Mapped[str] = mapped_column(String(64), nullable=False)
    senses: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    mastery: Mapped[str] = mapped_column(String(32), nullable=False)


class EpisodeRecord(Base):
    """Enregistrement persistant d'un souvenir épisodique local à une instance."""

    __tablename__ = "episodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    instance_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, index=True
    )
    occurred_at: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    importance: Mapped[float] = mapped_column(Float, nullable=False)
    affect: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    recall_count: Mapped[int] = mapped_column(default=0, nullable=False)
    accessibility: Mapped[float] = mapped_column(Float, nullable=False)


class TraceRecord(Base):
    """Trace persistante d'une décision cognitive locale à une instance."""

    __tablename__ = "decision_traces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    instance_id: Mapped[str] = mapped_column(String(36), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_actions: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    consulted_concepts: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    consulted_claims: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    recalled_memories: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    affect_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class ClaimRecord(Base):
    """Enregistrement persistant d'une affirmation locale à une instance."""

    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    instance_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[str] = mapped_column(String(36), nullable=False)
    predicate: Mapped[str] = mapped_column(String(255), nullable=False)
    object_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    literal: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    origin: Mapped[str] = mapped_column(String(32), nullable=False)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)


@dataclass(frozen=True)
class Database:
    """Regroupe le moteur SQLAlchemy et la fabrique de sessions associée."""

    engine: Engine
    session_factory: sessionmaker


def create_database(url: str) -> Database:
    """
    Crée l'infrastructure SQLAlchemy pour une URL de base donnée.

    Paramètres :
        url:
            URL SQLAlchemy, généralement SQLite dans la V1.

    Retour :
        Le moteur et la fabrique de sessions configurés.
    """
    kwargs: dict[str, Any] = {"future": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            # StaticPool garantit que toutes les sessions de test partagent
            # la même base SQLite en mémoire.
            kwargs["poolclass"] = StaticPool
    engine = create_engine(url, **kwargs)
    return Database(engine=engine, session_factory=sessionmaker(engine, expire_on_commit=False))


def create_schema(engine: Engine) -> None:
    """
    Crée le schéma courant dans une base destinée aux tests ou au prototypage.

    Paramètres :
        engine:
            Moteur SQLAlchemy sur lequel créer les tables.

    Retour :
        Aucun.
    """
    Base.metadata.create_all(engine)
