"""
Fabrique de l'application HTTP Mnesis.

Rôle :
    Assembler infrastructure, services applicatifs et routes FastAPI sans
    déplacer de logique cognitive dans la couche réseau.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from mnesis.api.dependencies import AppServices
from mnesis.api.routes import conversations, diagnostics, instances
from mnesis.application.conversation import ConversationService
from mnesis.application.learning import DictionarySource, LexicalLearningService
from mnesis.infrastructure.db import create_database, create_schema
from mnesis.infrastructure.knowledge_packs import load_knowledge_pack
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository
from mnesis.infrastructure.wiktionary import WiktionarySource
from mnesis.language.constructions import ConstructionSet, Lexicon


def create_app(
    database_url: str = "sqlite+pysqlite:///./mnesis.db",
    core_fr_path: Path = Path("knowledge/core-fr"),
    dictionary_source: DictionarySource | None = None,
    web_dist_path: Path = Path("web/dist"),
) -> FastAPI:
    """
    Construit une application FastAPI prête à servir Mnesis.

    Paramètres :
        database_url:
            URL SQLAlchemy utilisée pour la persistance.
        core_fr_path:
            Chemin du paquet linguistique français de base.
        dictionary_source:
            Source lexicale injectable ; Wiktionnaire est utilisé par défaut.
        web_dist_path:
            Répertoire du build Web, servi à la racine lorsqu’il existe.

    Retour :
        Application FastAPI entièrement assemblée.
    """
    database = create_database(database_url)
    create_schema(database.engine)
    instance_repository = InstanceRepository(database.session_factory)
    knowledge_repository = KnowledgeRepository(database.session_factory)
    memory_repository = MemoryRepository(database.session_factory)
    trace_repository = TraceRepository(database.session_factory)
    pack = load_knowledge_pack(core_fr_path)
    learning = LexicalLearningService(
        knowledge_repository,
        dictionary_source or WiktionarySource(),
    )
    conversation = ConversationService(
        knowledge=knowledge_repository,
        memories=memory_repository,
        traces=trace_repository,
        lexicon=Lexicon.from_words({str(item["surface"]) for item in pack.lexicon}),
        constructions=ConstructionSet.default_french(),
        responses=pack.responses,
        learning=learning,
        instances=instance_repository,
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
        # Le montage intervient après les routes API afin de ne jamais les masquer.
        app.mount("/", StaticFiles(directory=web_dist_path, html=True), name="web")
    return app


app = create_app()
