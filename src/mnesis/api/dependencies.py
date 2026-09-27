"""Dépendances partagées de l'API Mnesis."""

from dataclasses import dataclass
from fastapi import Request
from mnesis.application.conversation import ConversationService
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.traces import TraceRepository


@dataclass(frozen=True)
class AppServices:
    """Regroupe les services et dépôts accessibles aux routes FastAPI."""
    instances: InstanceRepository
    conversation: ConversationService
    traces: TraceRepository


def get_services(request: Request) -> AppServices:
    """Retourne les services associés à l'application courante."""
    return request.app.state.services
