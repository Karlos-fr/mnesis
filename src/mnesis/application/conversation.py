"""
Service conversationnel principal de Mnesis.

Rôle :
    Orchestrer analyse linguistique, connaissances, mémoire, croyances,
    sélection d'action, trace cognitive et réalisation textuelle.
"""

from datetime import UTC, datetime
from uuid import UUID
from pydantic import BaseModel, Field
from mnesis.application.beliefs import BeliefEngine
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

    def __init__(self, *, knowledge: KnowledgeRepository, memories: MemoryRepository, traces: TraceRepository, lexicon: Lexicon, constructions: ConstructionSet, responses: dict[str, list[str]]) -> None:
        """Initialise le service avec ses dépôts et ressources linguistiques explicites."""
        self.knowledge, self.memories, self.traces = knowledge, memories, traces
        self._lexicon, self._constructions = lexicon, constructions
        self._realizer, self._beliefs = SurfaceRealizer(responses), BeliefEngine()

    def handle(self, instance_id: UUID, text: str) -> ConversationTurn:
        """Traite un message utilisateur et retourne la réponse ainsi que sa trace."""
        parsed = parse_utterance(text, self._lexicon, self._constructions)
        action, response = "DEMANDER_CLARIFICATION", self._realizer.clarification()
        learned: list[UUID] = []
        concepts: list[UUID] = []
        claim_ids: list[UUID] = []
        if parsed.intent == "SALUER":
            action, response = "RÉPONDRE", self._realizer.greeting()
        elif parsed.intent == "DEFINIR":
            frame = parsed.semantic_frames[0]
            subject = self._ensure_concept(instance_id, frame["subject"], "entity")
            obj = self._ensure_concept(instance_id, frame["object"], "category")
            claim = Claim(subject_id=subject.id, predicate="EST_UN", object_id=obj.id, confidence=0.65, status=ClaimStatus.ACCEPTED, origin=KnowledgeOrigin.USER)
            self.knowledge.add_claim(instance_id, claim)
            action, response = "RÉPONDRE", self._realizer.acknowledge_definition(subject.label, obj.label)
            learned.extend([subject.id, obj.id, claim.id]); concepts.extend([subject.id, obj.id]); claim_ids.append(claim.id)
        elif parsed.intent == "DEMANDER_DEFINITION":
            subject = self.knowledge.find_concept(instance_id, parsed.semantic_frames[0]["concept"].casefold())
            if subject is not None:
                claims = self.knowledge.list_claims_for_subject(instance_id, subject.id, "EST_UN")
                if claims:
                    assessment = self._beliefs.evaluate(claims)
                    preferred = next(c for c in claims if c.id == assessment.preferred_claim_id)
                    obj = self.knowledge.get_concept(instance_id, preferred.object_id) if preferred.object_id else None
                    if obj is not None:
                        action = "RÉPONDRE"
                        response = self._realizer.uncertain_definition(subject.label, obj.label) if assessment.status is ClaimStatus.CONFLICTED else self._realizer.definition(subject.label, obj.label)
                        concepts.extend([subject.id, obj.id]); claim_ids.extend(assessment.all_claim_ids)
        episode = self.memories.add_episode(instance_id, Episode(instance_id=instance_id, occurred_at=datetime.now(UTC), summary=text, importance=0.4, affect={}))
        trace = self.traces.add(DecisionTrace(instance_id=instance_id, action=action, candidate_actions={"RÉPONDRE": 0.9 if action == "RÉPONDRE" else 0.2, "DEMANDER_CLARIFICATION": 0.9 if action == "DEMANDER_CLARIFICATION" else 0.2, "RELANCER": 0.1}, consulted_concepts=concepts, consulted_claims=claim_ids, recalled_memories=[episode.id], affect_snapshot={}))
        return ConversationTurn(response_text=response, intent=parsed.intent, trace_id=trace.id, learned_items=learned)

    def _ensure_concept(self, instance_id: UUID, label: str, kind: str) -> Concept:
        """Retourne un concept existant ou crée le concept local demandé."""
        existing = self.knowledge.find_concept(instance_id, label.casefold())
        return existing if existing is not None else self.knowledge.add_concept(instance_id, Concept(kind=kind, label=label.casefold()))
