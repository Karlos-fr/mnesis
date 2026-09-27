"""
Tests du modèle lexical de Mnesis.

Rôle :
    Garantir la séparation entre les formes linguistiques et les concepts.
"""

from uuid import uuid4

from mnesis.domain.language import Lexeme, LexicalSense, MasteryLevel


def test_multiple_lexemes_can_reference_same_concept() -> None:
    """Vérifie que plusieurs mots peuvent désigner un même concept."""
    concept_id = uuid4()
    voiture = Lexeme(
        surface="voiture",
        lemma="voiture",
        language="fr",
        part_of_speech="nom",
        senses=[LexicalSense(concept_id=concept_id, confidence=0.95)],
        mastery=MasteryLevel.UNDERSTOOD,
    )
    automobile = Lexeme(
        surface="automobile",
        lemma="automobile",
        language="fr",
        part_of_speech="nom",
        senses=[LexicalSense(concept_id=concept_id, confidence=0.9)],
        mastery=MasteryLevel.SEEN,
    )

    assert voiture.senses[0].concept_id == automobile.senses[0].concept_id
    assert voiture.id != automobile.id
