"""Routes HTTP de diagnostic cognitif Mnesis."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from mnesis.api.dependencies import AppServices, get_services
from mnesis.domain.traces import DecisionTrace

router = APIRouter(prefix="/api/v1/instances", tags=["diagnostics"])


@router.get("/{instance_id}/traces/{trace_id}", response_model=DecisionTrace)
def get_trace(instance_id: UUID, trace_id: UUID, services: AppServices = Depends(get_services)) -> DecisionTrace:
    """Retourne une trace cognitive appartenant à l'instance demandée."""
    trace = services.traces.get(instance_id, trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace cognitive introuvable.")
    return trace
