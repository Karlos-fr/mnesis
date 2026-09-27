"""
Service conversationnel principal de Mnesis.

Rôle :
    Orchestrer analyse linguistique, connaissances, apprentissage lexical,
    mémoire, croyances, sélection d'action, trace cognitive et réalisation textuelle.
"""

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from mnesis.application.beliefs import BeliefEngine
from mnesis.application.learning import LexicalLearningService
from mnesis.domain.knowledge import Claim, ClaimStatus, Concept, KnowledgeOrigin
from mnesis.domain.memory import Episode
from mnesis.domain.traces import DecisionTrace
from mnesis.infrastructure.repositories.knowledge import KnowledgeRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository
from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.language.parser import parse_utterance
from mnesis.language.realizer import SurfaceRealizer


class ConversationTurn(BaseModel):
    """Résultat externe d'un tour de conversation traité par Mnesis."""

    response_text: str
    intent: str | None
    trace_id: UUID
    learned_items: list[UUID] = Field(default_factory=list)


class ConversationService:
    """Coordonne le premier cycle conversationnel cognitif de Mnesis."""

    def __init__(
        self,
        *,
        knowledge: KnowledgeRepository,
        memories: MemoryRepository,
        traces: TraceRepository,
        lexicon: Lexicon,
        constructions: ConstructionSet,
        responses: dict[str, list[str]],
        learning: LexicalLearningService | None = None,
    ) -> None:
        """
        Initialise le service avec ses dépôts et ressources linguistiques.

        Paramètres :
            knowledge:
                Dépôt des concepts, lexèmes et affirmations.
            memories:
                Dépôt des souvenirs épisodiques.
            traces:
                Dépôt des traces de décision.
            lexicon:
                Lexique de démarrage fourni par le socle linguistique.
            constructions:
                Constructions françaises reconnues par le parseur.
            responses:
                Formulations contrôlées issues du socle linguistique.
            learning:
                Service optionnel d'apprentissage lexical autonome.
        """
        self.knowledge = knowledge
        self.memories = memories
        self.traces = traces
        self._lexicon = lexicon
        self._constructions = constructions
        self._realizer = SurfaceRealizer(responses)
        self._beliefs = BeliefEngine()
        self._learning = learning

    def handle(self, instance_id: UUID, text: str) -> ConversationTurn:
        """
        Traite un message utilisateur et retourne la réponse ainsi que sa trace.

        Paramètres :
            instance_id:
                Instance Mnesis à laquelle appartient l'échange.
            text:
                Message textuel reçu.

        Retour :
            Tour de conversation contenant la réponse, la trace et les éléments appris.
        """
        parsed = parse_utterance(text, self._lexicon, self._constructions)
        action = "DEMANDER_CLARIFICATION"
        response = self._realizer.clarification()
        confidence = 0.4
        learned: list[UUID] = []
        consulted_concepts: list[UUID] = []
        consulted_claims: list[UUID] = []

        if parsed.intent == "SALUER":
            action = "RÉPONDRE"
            response = self._realizer.greeting()
            confidence = 0.95
        elif parsed.intent == "DEFINIR":
            frame = parsed.semantic_frames[0]
            subject = self._ensure_concept(instance_id, frame["subject"], "entity")
            obj = self._ensure_concept(instance_id, frame["object"], "category")
            claim = Claim(
                subject_id=subject.id,
                predicate="EST_UN",
                object_id=obj.id,
                confidence=0.65,
                status=ClaimStatus.ACCEPTED,
                origin=KnowledgeOrigin.USER,
            )
            self.knowledge.add_claim(instance_id, claim)
            action = "RÉPONDRE"
            response = self._realizer.acknowledge_definition(subject.label, obj.label)
            confidence = 0.8
            learned.extend([subject.id, obj.id, claim.id])
            consulted_concepts.extend([subject.id, obj.id])
            consulted_claims.append(claim.id)
        elif parsed.intent == "DEMANDER_DEFINITION":
            response, confidence, consulted_concepts, consulted_claims = self._answer_definition(
                instance_id,
                parsed.semantic_frames[0]["concept"].casefold(),
                response,
                confidence,
            )
            if consulted_claims:
                action = "RÉPONDRE"
        elif parsed.intent is None and parsed.unknown_tokens and self._learning is not None:
            word = parsed.unknown_tokens[0]
            result = self._learning.learn_unknown_word(instance_id, word)
            if result.success:
                action = "RÉPONDRE"
                confidence = 0.65
                response = self._realizer.learned_word(word)
                learned.extend(
                    item
                    for item in (result.lexeme_id, result.concept_id)
                    if item is not None
                )

        episode = self.memories.add_episode(
            instance_id,
            Episode(
                instance_id=instance_id,
                occurred_at=datetime.now(UTC),
                summary=text,
                importance=0.4,
                affect={},
            ),
        )
        trace = self.traces.add(
            DecisionTrace(
                instance_id=instance_id,
                action=action,
                confidence=confidence,
                candidate_actions={
                    "RÉPONDRE": 0.9 if action == "RÉPONDRE" else 0.2,
                    "DEMANDER_CLARIFICATION": (
                        0.9 if action == "DEMANDER_CLARIFICATION" else 0.2
                    ),
                    "RELANCER": 0.1,
                },
                consulted_concepts=consulted_concepts,
                consulted_claims=consulted_claims,
                recalled_memories=[episode.id],
                affect_snapshot={},
            )
        )
        return ConversationTurn(
            response_text=response,
            intent=parsed.intent,
            trace_id=trace.id,
            learned_items=learned,
        )

    def _answer_definition(
        self,
        instance_id: UUID,
        label: str,
        default_response: str,
        default_confidence: float,
    ) -> tuple[str, float, list[UUID], list[UUID]]:
        """
        Recherche et réalise la meilleure définition disponible d'un concept.

        Paramètres :
            instance_id:
                Instance dans laquelle rechercher la connaissance.
            label:
                Libellé du concept demandé.
            default_response:
                Réponse conservée lorsqu'aucune définition n'est disponible.
            default_confidence:
                Confiance conservée lorsqu'aucune définition n'est disponible.

        Retour :
            Réponse, confiance et identifiants consultés pour la trace.
        """
        subject = self.knowledge.find_concept(instance_id, label)
        if subject is None:
            return default_response, default_confidence, [], []

        taxonomy_claims = self.knowledge.list_claims_for_subject(
            instance_id, subject.id, "EST_UN"
        )
        if taxonomy_claims:
            assessment = self._beliefs.evaluate(taxonomy_claims)
            preferred = next(
                claim for claim in taxonomy_claims if claim.id == assessment.preferred_claim_id
            )
            obj = (
                self.knowledge.get_concept(instance_id, preferred.object_id)
                if preferred.object_id
                else None
            )
            if obj is not None:
                response = (
                    self._realizer.uncertain_definition(subject.label, obj.label)
                    if assessment.status is ClaimStatus.CONFLICTED
                    else self._realizer.definition(subject.label, obj.label)
                )
                return (
                    response,
                    assessment.confidence,
                    [subject.id, obj.id],
                    assessment.all_claim_ids,
                )

        lexical_claims = self.knowledge.list_claims_for_subject(
            instance_id, subject.id, "DEFINI_COMME"
        )
        if lexical_claims:
            assessment = self._beliefs.evaluate(lexical_claims)
            preferred = next(
                claim for claim in lexical_claims if claim.id == assessment.preferred_claim_id
            )
            if isinstance(preferred.literal, str):
                return (
                    self._realizer.lexical_definition(subject.label, preferred.literal),
                    assessment.confidence,
                    [subject.id],
                    assessment.all_claim_ids,
                )

        return default_response, default_confidence, [subject.id], []

    def _ensure_concept(self, instance_id: UUID, label: str, kind: str) -> Concept:
        """
        Retourne un concept existant ou crée le concept local demandé.

        Paramètres :
            instance_id:
                Instance propriétaire du concept.
            label:
                Libellé à rechercher ou à créer.
            kind:
                Type sémantique utilisé lors d'une création.

        Retour :
            Concept existant ou nouvellement persisté.
        """
        existing = self.knowledge.find_concept(instance_id, label.casefold())
        if existing is not None:
            return existing
        return self.knowledge.add_concept(
            instance_id,
            Concept(kind=kind, label=label.casefold()),
        )
