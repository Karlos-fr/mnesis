"""
Tests du moteur de croyances Mnesis.

Rôle :
    Vérifier l'évaluation déterministe de la confiance et des contradictions.
"""

from uuid import uuid4

from mnesis.application.beliefs import BeliefEngine
from mnesis.domain.knowledge import Claim, ClaimStatus, KnowledgeOrigin


def test_knowledge_pack_outweighs_equally_confident_user_claim() -> None:
    """Vérifie que le socle conserve une autorité supérieure à une assertion utilisateur isolée."""
    subject = uuid4()
    trusted = Claim(subject_id=subject, predicate="EST_UN", literal="mammifère", confidence=0.9, status=ClaimStatus.TRUSTED, origin=KnowledgeOrigin.KNOWLEDGE_PACK)
    user = Claim(subject_id=subject, predicate="EST_UN", literal="oiseau", confidence=0.9, status=ClaimStatus.TENTATIVE, origin=KnowledgeOrigin.USER)
    assessment = BeliefEngine().evaluate([trusted, user])
    assert assessment.status is ClaimStatus.CONFLICTED
    assert assessment.preferred_claim_id == trusted.id
    assert assessment.supporting_claims == [trusted.id]
    assert assessment.contradicting_claims == [user.id]
