"""
Service conversationnel de Mnesis.

Rôle :
    Adapter un message textuel vers le cycle cognitif générique, puis persister
    l'épisode et la trace. Aucune intention métier n'est connue de ce service.
"""

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from mnesis.cognition.cycle import CognitiveCycle, CognitiveEvent
from mnesis.cognition.rules import DeclarativeRule
from mnesis.cognition.semantic_memory import SemanticMemory
from mnesis.domain.memory import Episode
from mnesis.domain.traces import DecisionTrace
from mnesis.infrastructure.repositories.constructions import ConstructionRepository
from mnesis.infrastructure.repositories.instances import InstanceRepository
from mnesis.infrastructure.repositories.memory import MemoryRepository
from mnesis.infrastructure.repositories.traces import TraceRepository
from mnesis.language.constructions import ConstructionSet, Lexicon
from mnesis.language.realization import OutputConstruction


class ConversationTurn(BaseModel):
    """Résultat externe d'un tour de conversation traité par le cycle cognitif."""

    response_text: str
    trace_id: UUID
    learned_items: list[str] = Field(default_factory=list)


class ConversationService:
    """Orchestre un tour conversationnel sans logique linguistique ou métier."""

    def __init__(
        self,
        *,
        cycle: CognitiveCycle,
        instances: InstanceRepository,
        memories: MemoryRepository,
        traces: TraceRepository,
        semantic_memory: SemanticMemory,
        constructions: ConstructionRepository,
        language: str,
        lexicon: Lexicon,
        input_constructions: ConstructionSet,
        rules: list[DeclarativeRule],
        output_constructions: list[OutputConstruction],
    ) -> None:
        """Initialise le service avec les composants et ressources du cycle."""
        self._cycle = cycle
        self._instances = instances
        self.memories = memories
        self.traces = traces
        self._semantic_memory = semantic_memory
        self._constructions = constructions
        self._language = language
        self._lexicon = lexicon
        self._input_constructions = input_constructions
        self._rules = rules
        self._output_constructions = output_constructions

    def handle(self, instance_id: UUID, text: str) -> ConversationTurn:
        """Traite un message par le cycle générique et persiste épisode et trace."""
        instance = self._instances.get(instance_id)
        if instance is None:
            raise ValueError("Instance Mnesis introuvable.")
        state = {
            "personality": instance.personality.model_dump(),
            "affect": instance.affect.model_dump(),
        }
        local_constructions = self._constructions.list_for_instance(
            instance_id, self._language
        )
        active_constructions = ConstructionSet(
            declarative_items=(
                self._input_constructions.declarative_items
                + tuple(local_constructions)
            )
        )
        result = self._cycle.process(
            CognitiveEvent(text=text),
            state=state,
            lexicon=self._lexicon,
            input_constructions=active_constructions,
            rules=self._rules,
            output_constructions=self._output_constructions,
            procedure_context={
                "store_frame": lambda frame: self._semantic_memory.store(
                    instance_id, frame
                ),
                "retrieve": lambda query: self._semantic_memory.retrieve(
                    instance_id, query
                ),
            },
        )
        episode = self.memories.add_episode(
            instance_id,
            Episode(
                instance_id=instance_id,
                occurred_at=datetime.now(UTC),
                summary=text,
                importance=0.4,
                affect=instance.affect.model_dump(),
            ),
        )
        trace = self.traces.add(
            DecisionTrace(
                instance_id=instance_id,
                action=result.selected_action.action_type,
                confidence=result.selected_action.score,
                candidate_actions={
                    f"{index}:{candidate.action_type}": candidate.score
                    for index, candidate in enumerate(result.ranked_actions)
                },
                recalled_memories=[episode.id],
                affect_snapshot=instance.affect.model_dump(),
            )
        )
        return ConversationTurn(
            response_text=result.response_text,
            trace_id=trace.id,
            learned_items=result.procedure_result.learned_items,
        )
