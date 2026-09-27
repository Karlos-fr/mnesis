"""
Test comportemental d'une contradiction utilisateur.

Rôle :
    Vérifier que Mnesis conserve les affirmations concurrentes et refuse
    l'écrasement silencieux du socle de connaissances.
"""

from uuid import uuid4

from mnesis.application.beliefs import BeliefEngine
from mnesis.domain.knowledge import Claim, ClaimStatus, KnowledgeOrigin


def test_user_claim_does_not_replace_trusted_knowledge() -> None:
    """Vérifie le conflit chauve-souris mammifère contre chauve-souris oiseau."""
    subject = uuid4()
    mammal = Claim(subject_id=subject, predicate="EST_UN", literal="mammifère", confidence=0.99, status=ClaimStatus.TRUSTED, origin=KnowledgeOrigin.KNOWLEDGE_PACK)
    bird = Claim(subject_id=subject, predicate="EST_UN", literal="oiseau", confidence=0.7, status=ClaimStatus.TENTATIVE, origin=KnowledgeOrigin.USER)
    assessment = BeliefEngine().evaluate([mammal, bird])
    assert assessment.status is ClaimStatus.CONFLICTED
    assert assessment.preferred_claim_id == mammal.id
    assert set(assessment.all_claim_ids) == {mammal.id, bird.id}
