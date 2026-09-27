"""
Dépendances partagées de l'API Mnesis.

Rôle :
    Regrouper les services initialisés par l'application afin que les routes
    restent de simples adaptateurs HTTP sans logique cognitive.
"""

from dataclasses import dataclass

from fastapi import Request

from mnesis.application.conversation import ConversationService
from mnesis.infrastructure.knowledge_packs import KnowledgePack
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.traces import TraceRepository


@dataclass(frozen=True)
class AppServices:
    """Regroupe les services et dépôts accessibles aux routes FastAPI."""

    instances: InstanceRepository
    knowledge: KnowledgeRepository
    conversation: ConversationService
    traces: TraceRepository
    core_fr: KnowledgePack


def get_services(request: Request) -> AppServices:
    """
    Retourne les services associés à l'application courante.

    Paramètres :
        request:
            Requête FastAPI portant l'état de l'application.

    Retour :
        Services initialisés au démarrage de l'application.
    """
    return request.app.state.services
