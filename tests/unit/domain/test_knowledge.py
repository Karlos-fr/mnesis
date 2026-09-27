"""
Tests du modèle de connaissances de Mnesis.

Rôle :
    Vérifier les invariants des concepts, affirmations, preuves et niveaux de confiance.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from mnesis.domain.knowledge import Claim, ClaimStatus, Evidence, KnowledgeOrigin


def test_claim_rejects_confidence_above_one() -> None:
    """Vérifie qu'une confiance supérieure à 1 est invalide."""
    with pytest.raises(ValidationError):
        Claim(
            subject_id=uuid4(),
            predicate="EST_UN",
            literal="animal",
            confidence=1.2,
            status=ClaimStatus.ACCEPTED,
            origin=KnowledgeOrigin.USER,
        )


def test_claim_preserves_multiple_sources_of_evidence() -> None:
    """Vérifie qu'une croyance conserve plusieurs preuves sans écrasement."""
    first = Evidence(
        source_type=KnowledgeOrigin.KNOWLEDGE_PACK,
        source_uri="knowledge://core-fr",
        observed_at=datetime.now(UTC),
        reliability=0.95,
        statement="La chauve-souris est un mammifère.",
    )
    second = Evidence(
        source_type=KnowledgeOrigin.USER,
        source_uri="user://conversation/42",
        observed_at=datetime.now(UTC),
        reliability=0.5,
        statement="La chauve-souris est un oiseau.",
    )
    claim = Claim(
        subject_id=uuid4(),
        predicate="EST_UN",
        literal="mammifère",
        confidence=0.95,
        status=ClaimStatus.CONFLICTED,
        origin=KnowledgeOrigin.KNOWLEDGE_PACK,
        evidence=[first, second],
    )

    assert claim.status is ClaimStatus.CONFLICTED
    assert claim.evidence == [first, second]
