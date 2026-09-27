"""Routes HTTP de conversation avec Mnesis."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from mnesis.api.dependencies import AppServices, get_services
from mnesis.application.conversation import ConversationTurn

router = APIRouter(prefix="/api/v1/instances", tags=["conversation"])


class MessageRequest(BaseModel):
    """Corps HTTP d'un message envoyé à une instance."""
    text: str

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        """Refuse les messages vides avant tout événement cognitif."""
        if not value.strip():
            raise ValueError("Le message ne peut pas être vide.")
        return value


@router.post("/{instance_id}/messages", response_model=ConversationTurn)
def send_message(instance_id: UUID, payload: MessageRequest, services: AppServices = Depends(get_services)) -> ConversationTurn:
    """Envoie un message à une instance existante."""
    if services.instances.get(instance_id) is None:
        raise HTTPException(status_code=404, detail="Instance Mnesis introuvable.")
    return services.conversation.handle(instance_id, payload.text)
