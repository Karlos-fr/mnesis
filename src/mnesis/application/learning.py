"""
Service d'apprentissage lexical de Mnesis.

Rôle :
    Transformer une définition externe en lexème, concept et affirmation
    persistants, tout en conservant la provenance de l'apprentissage.
"""

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field

from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, Evidence, KnowledgeOrigin
from mnesis.domain.language import Lexeme, LexicalSense, MasteryLevel
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository


class DictionaryEntry(BaseModel):
    """Représente une définition normalisée provenant d'une source lexicale."""

    word: str = Field(min_length=1)
    lemma: str = Field(min_length=1)
    part_of_speech: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    source_uri: str = Field(min_length=1)


class DictionarySource(Protocol):
    """Port minimal requis par le service d'apprentissage lexical."""

    def lookup(self, word: str, locale: str) -> DictionaryEntry | None:
        """Recherche un mot et retourne une entrée normalisée ou None."""
        ...


class LearningResult(BaseModel):
    """Résume le résultat observable d'une tentative d'apprentissage."""

    success: bool
    word: str
    lexeme_id: UUID | None = None
    concept_id: UUID | None = None
    message: str


class LexicalLearningService:
    """Apprend un mot inconnu depuis une source dictionnaire injectée."""

    def __init__(self, repository: KnowledgeRepository, source: DictionarySource) -> None:
        """Initialise le service avec son dépôt et sa source lexicale."""
        self._repository = repository
        self._source = source

    def learn_unknown_word(
        self,
        instance_id: UUID,
        word: str,
        locale: str = "fr-FR",
    ) -> LearningResult:
        """
        Apprend un mot absent du lexique de l'instance.

        Paramètres :
            instance_id:
                Instance qui réalise l'apprentissage.
            word:
                Forme lexicale à rechercher.
            locale:
                Locale utilisée par la source dictionnaire.

        Retour :
            Résultat indiquant si un nouvel apprentissage a été intégré.
        """
        existing = self._repository.find_lexeme(instance_id, word)
        if existing is not None:
            concept_id = existing.senses[0].concept_id if existing.senses else None
            return LearningResult(
                success=True,
                word=word,
                lexeme_id=existing.id,
                concept_id=concept_id,
                message="Le mot était déjà connu.",
            )

        entry = self._source.lookup(word, locale)
        if entry is None:
            return LearningResult(
                success=False,
                word=word,
                message="Aucune définition fiable trouvée.",
            )

        concept = Concept(kind="lexical", label=entry.lemma)
        lexeme = Lexeme(
            surface=entry.word,
            lemma=entry.lemma,
            language=locale.split("-", maxsplit=1)[0],
            part_of_speech=entry.part_of_speech,
            senses=[LexicalSense(concept_id=concept.id, confidence=0.65)],
            mastery=MasteryLevel.PARTIALLY_UNDERSTOOD,
        )
        evidence = Evidence(
            source_type=KnowledgeOrigin.DICTIONARY,
            source_uri=entry.source_uri,
            observed_at=datetime.now(UTC),
            reliability=0.8,
            statement=entry.definition,
        )
        claim = Claim(
            subject_id=concept.id,
            predicate="DEFINI_COMME",
            literal=entry.definition,
            confidence=0.65,
            status=ClaimStatus.TENTATIVE,
            origin=KnowledgeOrigin.DICTIONARY,
            evidence=[evidence],
        )
        self._repository.add_concept(instance_id, concept)
        self._repository.add_lexeme(instance_id, lexeme)
        self._repository.add_claim(instance_id, claim)
        return LearningResult(
            success=True,
            word=word,
            lexeme_id=lexeme.id,
            concept_id=concept.id,
            message="Mot appris depuis le dictionnaire.",
        )
