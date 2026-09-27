"""
Moteur d'évaluation des croyances de Mnesis.

Rôle :
    Comparer des affirmations concurrentes de manière déterministe en tenant
    compte de leur confiance et de l'autorité relative de leur provenance.

Contraintes :
    Les coefficients de provenance sont explicites afin que toute décision
    puisse être expliquée et testée.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from mnesis.domain.knowledge import Claim, ClaimStatus, KnowledgeOrigin


_SOURCE_WEIGHTS: dict[KnowledgeOrigin, float] = {
    KnowledgeOrigin.NATIVE: 1.0,
    KnowledgeOrigin.KNOWLEDGE_PACK: 1.0,
    KnowledgeOrigin.INFERENCE: 0.9,
    KnowledgeOrigin.DICTIONARY: 0.85,
    KnowledgeOrigin.WEB: 0.7,
    KnowledgeOrigin.USER: 0.65,
    KnowledgeOrigin.LEARNED_PROCEDURE: 0.9,
}


class BeliefAssessment(BaseModel):
    """Résume l'évaluation d'un ensemble d'affirmations concurrentes."""

    status: ClaimStatus
    confidence: float = Field(ge=0.0, le=1.0)
    preferred_claim_id: UUID | None
    supporting_claims: list[UUID]
    contradicting_claims: list[UUID]
    all_claim_ids: list[UUID]


class BeliefEngine:
    """Évalue des croyances concurrentes sans supprimer les alternatives."""

    def evaluate(self, claims: list[Claim]) -> BeliefAssessment:
        """
        Évalue un ensemble de croyances portant sur une même relation.

        Paramètres :
            claims:
                Affirmations concurrentes à comparer.

        Retour :
            Évaluation indiquant l'affirmation préférée, les preuves
            concurrentes et le statut de conflit.

        Erreurs :
            ValueError:
                Levée si la liste est vide ou mélange plusieurs relations.
        """
        if not claims:
            raise ValueError("Au moins une affirmation est nécessaire.")
        relation_keys = {(claim.subject_id, claim.predicate) for claim in claims}
        if len(relation_keys) != 1:
            raise ValueError("Les affirmations évaluées doivent concerner la même relation.")

        def target(claim: Claim) -> tuple[str, str]:
            """Retourne une clé comparable représentant la cible d’une affirmation."""
            if claim.object_id is not None:
                return ("object", str(claim.object_id))
            return ("literal", repr(claim.literal))

        def score(claim: Claim) -> float:
            """Calcule le score pondéré par la confiance accordée à la source."""
            return claim.confidence * _SOURCE_WEIGHTS[claim.origin]

        preferred = max(claims, key=score)
        preferred_target = target(preferred)
        supporting = [claim.id for claim in claims if target(claim) == preferred_target]
        contradicting = [claim.id for claim in claims if target(claim) != preferred_target]
        has_conflict = bool(contradicting)

        return BeliefAssessment(
            status=ClaimStatus.CONFLICTED if has_conflict else preferred.status,
            confidence=min(1.0, score(preferred)),
            preferred_claim_id=preferred.id,
            supporting_claims=supporting,
            contradicting_claims=contradicting,
            all_claim_ids=[claim.id for claim in claims],
        )
