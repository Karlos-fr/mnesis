"""
Fabrique de l'application HTTP Mnesis.

Rôle :
    Assembler l'infrastructure, le cycle cognitif générique et les routes API.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from mnesis.api.dependencies import AppServices
from mnesis.api.routes import conversations, diagnostics, instances
from mnesis.application.conversation import ConversationService
from mnesis.application.learning import DictionarySource
from mnesis.cognition.actions import ActionEngine
from mnesis.cognition.cycle import CognitiveCycle
from mnesis.cognition.procedures import ProcedureExecutor
from mnesis.cognition.rules import RuleEngine
from mnesis.cognition.semantic_memory import SemanticMemory
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.knowledge_packs import load_knowledge_pack
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository
from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.language.interpreter import LanguageInterpreter
from mnesis.language.realization import LanguageRealizer


def create_app(
    database_url: str = "sqlite+pysqlite:///./mnesis.db",
    core_fr_path: Path = Path("knowledge/core-fr"),
    dictionary_source: DictionarySource | None = None,
    web_dist_path: Path = Path("web/dist"),
) -> FastAPI:
    """
    Construit une application FastAPI prête à servir Mnesis.

    Le paramètre dictionary_source est conservé pour compatibilité et sera
    raccordé à l'action générique RESEARCH dans une tâche ultérieure.
    """
    del dictionary_source
    database = create_database(database_url)
    create_schema(database.engine)
    instance_repository = InstanceRepository(database.session_factory)
    knowledge_repository = KnowledgeRepository(database.session_factory)
    memory_repository = MemoryRepository(database.session_factory)
    trace_repository = TraceRepository(database.session_factory)
    pack = load_knowledge_pack(core_fr_path)
    cycle = CognitiveCycle(
        interpreter=LanguageInterpreter(),
        rule_engine=RuleEngine(),
        action_engine=ActionEngine(),
        procedure_executor=ProcedureExecutor(),
        realizer=LanguageRealizer(),
    )
    conversation = ConversationService(
        cycle=cycle,
        instances=instance_repository,
        memories=memory_repository,
        traces=trace_repository,
        semantic_memory=SemanticMemory(knowledge_repository),
        lexicon=Lexicon.from_words({str(item["surface"]) for item in pack.lexicon}),
        input_constructions=ConstructionSet(
            declarative_items=tuple(pack.input_constructions)
        ),
        rules=pack.rules,
        output_constructions=pack.output_constructions,
    )

    app = FastAPI(title="Mnesis", version="0.1.0")
    app.state.services = AppServices(
        instances=instance_repository,
        knowledge=knowledge_repository,
        conversation=conversation,
        traces=trace_repository,
        core_fr=pack,
    )
    app.include_router(instances.router)
    app.include_router(conversations.router)
    app.include_router(diagnostics.router)
    if web_dist_path.is_dir():
        app.mount("/", StaticFiles(directory=web_dist_path, html=True), name="web")
    return app


app = create_app()
