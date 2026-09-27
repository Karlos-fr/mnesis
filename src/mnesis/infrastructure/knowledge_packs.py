"""
Chargement et déploiement des paquets de connaissances Mnesis.

Rôle :
    Lire un socle versionné depuis des fichiers YAML et déployer concepts,
    lexèmes et affirmations dans une instance en conservant leur origine.
"""

from pathlib import Path
from uuid import UUID

import yaml
from pydantic import BaseModel, Field

from mnesis.cognition.rules import DeclarativeRule
from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, KnowledgeOrigin
from mnesis.domain.language import Lexeme, LexicalSense, MasteryLevel
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.language.constructions import InputConstruction
from mnesis.language.realization import OutputConstruction


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
    input_constructions: list[InputConstruction] = Field(default_factory=list)
    output_constructions: list[OutputConstruction] = Field(default_factory=list)
    rules: list[DeclarativeRule] = Field(default_factory=list)


class DeploymentResult(BaseModel):
    """Résume les éléments effectivement déployés dans une instance."""

    concepts_deployed: int
    lexemes_deployed: int
    claims_deployed: int


def _read_yaml(path: Path) -> object:
    """Lit un fichier YAML du paquet et retourne sa structure Python."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_knowledge_pack(path: Path) -> KnowledgePack:
    """Charge un paquet de connaissances depuis un répertoire."""
    return KnowledgePack(
        manifest=KnowledgePackManifest.model_validate(_read_yaml(path / "manifest.yaml")),
        lexicon=list(_read_yaml(path / "lexicon.yaml")),
        concepts=list(_read_yaml(path / "concepts.yaml")),
        relations=list(_read_yaml(path / "relations.yaml")),
        constructions=list(_read_yaml(path / "constructions.yaml")),
        responses=dict(_read_yaml(path / "responses.yaml")),
        input_constructions=[
            InputConstruction.model_validate(item)
            for item in list(_read_yaml(path / "input-constructions.yaml"))
        ],
        output_constructions=[
            OutputConstruction.model_validate(item)
            for item in list(_read_yaml(path / "output-constructions.yaml"))
        ],
        rules=[
            DeclarativeRule.model_validate(item)
            for item in list(_read_yaml(path / "rules.yaml"))
        ],
    )


def deploy_knowledge_pack(
    instance_id: UUID,
    pack: KnowledgePack,
    repository: KnowledgeRepository,
) -> DeploymentResult:
    """Déploie concepts, lexèmes et affirmations du paquet dans une instance."""
    concepts_deployed = 0
    lexemes_deployed = 0
    claims_deployed = 0

    for item in pack.concepts:
        label = str(item["label"]).casefold()
        if repository.find_concept(instance_id, label) is not None:
            continue
        repository.add_concept(
            instance_id,
            Concept(
                id=UUID(str(item["id"])),
                kind=str(item["kind"]),
                label=label,
            ),
        )
        concepts_deployed += 1

    language = pack.manifest.locale.split("-", maxsplit=1)[0].casefold()
    for item in pack.lexicon:
        surface = str(item["surface"]).casefold()
        if repository.find_lexeme(instance_id, surface) is not None:
            continue
        repository.add_lexeme(
            instance_id,
            Lexeme(
                surface=surface,
                lemma=str(item["lemma"]).casefold(),
                language=language,
                part_of_speech=str(item["part_of_speech"]),
                senses=[
                    LexicalSense(
                        concept_id=UUID(str(item["concept_id"])),
                        confidence=0.99,
                    )
                ],
                mastery=MasteryLevel.MASTERED,
            ),
        )
        lexemes_deployed += 1

    for relation in pack.relations:
        claim = Claim(
            subject_id=UUID(str(relation["subject_id"])),
            predicate=str(relation["predicate"]),
            object_id=UUID(str(relation["object_id"])),
            confidence=float(relation["confidence"]),
            status=ClaimStatus(str(relation["status"])),
            origin=KnowledgeOrigin.KNOWLEDGE_PACK,
        )
        repository.add_claim(instance_id, claim)
        claims_deployed += 1

    return DeploymentResult(
        concepts_deployed=concepts_deployed,
        lexemes_deployed=lexemes_deployed,
        claims_deployed=claims_deployed,
    )
