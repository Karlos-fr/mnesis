"""Fabrique de l'application HTTP Mnesis."""

from pathlib import Path
from fastapi import FastAPI
from mnesis.api.dependencies import AppServices
from mnesis.api.routes import conversations, diagnostics, instances
from mnesis.application.conversation import ConversationService
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.knowledge_packs import load_knowledge_pack
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository
from mnesis.language.constructions import ConstructionSet, Lexicon


def create_app(database_url: str = "sqlite+pysqlite:///./mnesis.db", core_fr_path: Path = Path("knowledge/core-fr")) -> FastAPI:
    """Construit une application FastAPI prête à servir Mnesis."""
    database = create_database(database_url)
    create_schema(database.engine)
    instance_repository = InstanceRepository(database.session_factory)
    knowledge_repository = KnowledgeRepository(database.session_factory)
    memory_repository = MemoryRepository(database.session_factory)
    trace_repository = TraceRepository(database.session_factory)
    pack = load_knowledge_pack(core_fr_path)
    conversation = ConversationService(knowledge=knowledge_repository, memories=memory_repository, traces=trace_repository, lexicon=Lexicon.from_words({str(item["surface"]) for item in pack.lexicon}), constructions=ConstructionSet.default_french(), responses=pack.responses)
    app = FastAPI(title="Mnesis", version="0.1.0")
    app.state.services = AppServices(instances=instance_repository, conversation=conversation, traces=trace_repository)
    app.include_router(instances.router)
    app.include_router(conversations.router)
    app.include_router(diagnostics.router)
    return app


app = create_app()
