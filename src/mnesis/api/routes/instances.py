"""Routes HTTP de gestion des instances Mnesis."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from mnesis.api.dependencies import AppServices, get_services
from mnesis.domain.instances import MnesisInstance

router = APIRouter(prefix="/api/v1/instances", tags=["instances"])


class CreateInstanceRequest(BaseModel):
    """Corps HTTP permettant de créer une instance Mnesis."""
    name: str = Field(min_length=1)
    locale: str = Field(default="fr-FR", min_length=2)


@router.post("", response_model=MnesisInstance, status_code=status.HTTP_201_CREATED)
def create_instance(payload: CreateInstanceRequest, services: AppServices = Depends(get_services)) -> MnesisInstance:
    """Crée et persiste une nouvelle instance Mnesis."""
    return services.instances.create(MnesisInstance.create(name=payload.name, locale=payload.locale))


@router.get("/{instance_id}", response_model=MnesisInstance)
def get_instance(instance_id: UUID, services: AppServices = Depends(get_services)) -> MnesisInstance:
    """Retourne une instance existante ou une erreur HTTP 404."""
    instance = services.instances.get(instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance Mnesis introuvable.")
    return instance
