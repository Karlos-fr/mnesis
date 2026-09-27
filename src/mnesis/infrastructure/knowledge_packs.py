"""
Chargement et déploiement des paquets de connaissances Mnesis.

Rôle :
    Lire un socle versionné depuis des fichiers YAML et déployer ses
    affirmations dans une instance en conservant explicitement leur origine.
"""

from pathlib import Path
from uuid import UUID

import yaml
from pydantic import BaseModel

from mnesis.domain.knowledge import Claim, ClaimStatus, KnowledgeOrigin
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository


class KnowledgePackManifest(BaseModel):
    """Décrit l'identité et la compatibilité linguistique d'un paquet."""

    name: str
    version: str
    locale: str
    description: str = ""


class KnowledgePack(BaseModel):
    """Regroupe le contenu inspectable d'un paquet de connaissances."""

    manifest: KnowledgePackManifest
    lexicon: list[dict]
    concepts: list[dict]
    relations: list[dict]
    constructions: list[dict]
    responses: dict[str, list[str]]


class DeploymentResult(BaseModel):
    """Résume le nombre d'éléments effectivement déployés dans une instance."""

    claims_deployed: int


def _read_yaml(path: Path) -> object:
    """Lit un fichier YAML du paquet et retourne sa structure Python."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_knowledge_pack(path: Path) -> KnowledgePack:
    """Charge et valide un paquet de connaissances depuis un répertoire."""
    return KnowledgePack(
        manifest=KnowledgePackManifest.model_validate(_read_yaml(path / "manifest.yaml")),
        lexicon=list(_read_yaml(path / "lexicon.yaml")),
        concepts=list(_read_yaml(path / "concepts.yaml")),
        relations=list(_read_yaml(path / "relations.yaml")),
        constructions=list(_read_yaml(path / "constructions.yaml")),
        responses=dict(_read_yaml(path / "responses.yaml")),
    )


def deploy_knowledge_pack(instance_id: UUID, pack: KnowledgePack, repository: KnowledgeRepository) -> DeploymentResult:
    """Déploie les affirmations d'un paquet dans une instance et retourne le bilan."""
    count = 0
    for relation in pack.relations:
        repository.add_claim(
            instance_id,
            Claim(
                subject_id=UUID(str(relation["subject_id"])),
                predicate=str(relation["predicate"]),
                object_id=UUID(str(relation["object_id"])),
                confidence=float(relation["confidence"]),
                status=ClaimStatus(str(relation["status"])),
                origin=KnowledgeOrigin.KNOWLEDGE_PACK,
            ),
        )
        count += 1
    return DeploymentResult(claims_deployed=count)
