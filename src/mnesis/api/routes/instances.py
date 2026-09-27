"""
Routes HTTP de gestion des instances Mnesis.

Rôle :
    Adapter les requêtes de création, lecture et déploiement du socle aux
    services applicatifs sans introduire de logique cognitive dans HTTP.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from mnesis.api.dependencies import AppServices, get_services
from mnesis.domain.instances import MnesisInstance
from mnesis.infrastructure.knowledge_packs import DeploymentResult, deploy_knowledge_pack

router = APIRouter(prefix="/api/v1/instances", tags=["instances"])


class CreateInstanceRequest(BaseModel):
    """Corps HTTP permettant de créer une instance Mnesis."""

    name: str = Field(min_length=1)
    locale: str = Field(default="fr-FR", min_length=2)


@router.post("", response_model=MnesisInstance, status_code=status.HTTP_201_CREATED)
def create_instance(
    payload: CreateInstanceRequest,
    services: AppServices = Depends(get_services),
) -> MnesisInstance:
    """Crée et persiste une nouvelle instance Mnesis."""
    return services.instances.create(
        MnesisInstance.create(name=payload.name, locale=payload.locale)
    )


@router.get("/{instance_id}", response_model=MnesisInstance)
def get_instance(
    instance_id: UUID,
    services: AppServices = Depends(get_services),
) -> MnesisInstance:
    """Retourne une instance existante ou une erreur HTTP 404."""
    instance = services.instances.get(instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance Mnesis introuvable.")
    return instance


@router.post(
    "/{instance_id}/knowledge-packs/core-fr",
    response_model=DeploymentResult,
)
def deploy_core_fr(
    instance_id: UUID,
    services: AppServices = Depends(get_services),
) -> DeploymentResult:
    """
    Déploie explicitement le socle français versionné dans une instance.

    Paramètres :
        instance_id:
            Instance cible du déploiement.
        services:
            Services configurés par l'application.

    Retour :
        Nombre de concepts, lexèmes et affirmations intégrés.

    Erreurs :
        HTTPException:
            404 si l'instance cible n'existe pas.
    """
    if services.instances.get(instance_id) is None:
        raise HTTPException(status_code=404, detail="Instance Mnesis introuvable.")
    return deploy_knowledge_pack(instance_id, services.core_fr, services.knowledge)
