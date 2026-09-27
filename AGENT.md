# AGENT.md — Règles de développement Mnesis

Ce fichier définit les règles obligatoires à respecter par tout agent ou assistant intervenant sur le dépôt **Mnesis**.

## 1. Langue

- Toute la documentation du projet doit être rédigée en français.
- Les commentaires de code et docstrings doivent être rédigés en français.
- Les noms de classes, fonctions, variables, modules et API peuvent rester en anglais lorsqu’il s’agit d’une convention technique naturelle ou que cela améliore la lisibilité du code.

## 2. Gestion Git

- **Ne jamais créer de branche Git.**
- **Ne jamais créer de worktree Git.**
- Le projet est développé par un seul intervenant à la fois.
- Travailler directement sur la branche principale du dépôt.
- Faire des commits fréquents, cohérents et limités à une unité fonctionnelle claire.
- Ne jamais réécrire ou supprimer un historique Git existant sans instruction explicite.

## 3. Commentaires et documentation du code

Le code doit être documenté de manière systématique.

### 3.1 En-tête de fichier

Chaque fichier source doit commencer par un en-tête indiquant au minimum :

- le rôle du fichier ;
- sa responsabilité principale ;
- les dépendances importantes ou contraintes particulières si elles sont utiles à la compréhension.

Exemple :

```python
"""
Module de gestion des croyances de Mnesis.

Rôle :
    Évaluer les affirmations, leurs preuves et leurs contradictions afin
    de produire un niveau de confiance et un statut de croyance inspectable.

Responsabilités :
    - agréger les preuves ;
    - détecter les contradictions ;
    - calculer la confiance ;
    - conserver la traçabilité des décisions.
"""
```

### 3.2 Classes et autres entités

Chaque classe, dataclass, modèle, enum, protocole ou entité métier doit disposer d’une docstring indiquant :

- son rôle ;
- ce qu’elle représente ;
- les invariants ou contraintes importantes lorsqu’ils existent.

Exemple :

```python
class Claim:
    """
    Représente une affirmation connue ou supposée par une instance Mnesis.

    Une affirmation relie un sujet, un prédicat et un objet ou une valeur,
    tout en conservant son niveau de confiance, son origine et ses preuves.
    """
```

### 3.3 Fonctions et méthodes

Chaque fonction ou méthode non triviale doit disposer d’une docstring précisant :

- son rôle ;
- ses paramètres d’entrée ;
- sa valeur de sortie ;
- les erreurs ou cas particuliers significatifs lorsque cela est utile.

Format recommandé :

```python
def evaluate_claim(claim: Claim, evidence: list[Evidence]) -> BeliefAssessment:
    """
    Évalue une affirmation à partir des preuves disponibles.

    Paramètres :
        claim:
            Affirmation à évaluer.
        evidence:
            Ensemble des preuves compatibles ou contradictoires.

    Retour :
        Une évaluation contenant le statut de la croyance, son niveau de
        confiance et la répartition des preuves.

    Erreurs :
        ValueError:
            Levée si une preuve possède un niveau de fiabilité hors limites.
    """
```

Pour les fonctions très simples dont le comportement est évident, une docstring plus courte est acceptable, mais le rôle et les entrées/sorties doivent rester compréhensibles.

### 3.4 Commentaires internes

- Ajouter des commentaires lorsque le **pourquoi** d’un choix n’est pas évident.
- Ne pas paraphraser inutilement le code ligne par ligne.
- Documenter les algorithmes, heuristiques, seuils et règles cognitives dont le comportement pourrait autrement sembler arbitraire.
- Tout nombre ou seuil influençant le comportement cognitif doit être nommé ou expliqué.

## 4. Principes d’architecture

- Mnesis est un agent conversationnel cognitif **sans LLM**.
- Ne jamais ajouter de dépendance à un LLM pour la compréhension, le raisonnement ou la génération de texte.
- Le moteur cognitif doit rester indépendant de FastAPI, de l’interface Web et des canaux externes.
- Les mots et les concepts doivent rester deux entités distinctes.
- Les connaissances doivent conserver leur provenance, leurs preuves et leur niveau de confiance.
- Les instances Mnesis doivent rester isolées par défaut.
- Les connaissances partagées doivent passer par des paquets de connaissances explicitement déployés.
- Toute capacité doit pouvoir être identifiée comme :
  - native au moteur ;
  - issue d’un paquet de connaissances ;
  - apprise par l’instance.
- Les décisions cognitives doivent être inspectables autant que possible.

## 5. Persistance

- La V1 utilise SQLite.
- L’accès à la base doit passer par SQLAlchemy.
- Les migrations doivent utiliser Alembic.
- Éviter les dépendances inutiles à des particularités SQLite afin de préserver une migration future vers PostgreSQL.
- Ne pas introduire de base graphe tant qu’un besoin réel ne le justifie pas.

## 6. Développement piloté par les tests

Pour chaque fonctionnalité ou correction :

1. écrire ou adapter le test ;
2. constater l’échec attendu ;
3. implémenter le changement minimal ;
4. vérifier que le test passe ;
5. exécuter les tests de régression pertinents ;
6. seulement ensuite effectuer le commit.

Les tests doivent notamment protéger :

- l’isolation des instances ;
- la provenance des connaissances ;
- les niveaux de confiance ;
- les contradictions ;
- les apprentissages réels ;
- la distinction entre connaissances fournies et apprises.

## 7. Apprentissage réel plutôt que simulé

Éviter toute implémentation qui donne l’apparence d’un apprentissage alors que la capacité est codée en dur.

Lorsqu’une capacité est présentée comme apprise, un test doit pouvoir démontrer :

1. qu’elle était absente avant l’apprentissage ;
2. qu’un événement d’apprentissage a modifié l’état interne ;
3. qu’elle peut ensuite être réutilisée dans un cas nouveau.

## 8. Sobriété

- Privilégier des composants petits, cohérents et testables.
- Éviter les abstractions prématurées.
- Éviter les dépendances lourdes lorsqu’une solution simple suffit.
- Ne pas ajouter une fonctionnalité qui n’est pas requise par la spécification ou le plan courant.
- L’interface Web doit rester sobre et ne pas reprendre les codes visuels habituels des assistants d’IA générative.

## 9. Références de conception

Avant toute modification significative, consulter :

- `docs/superpowers/specs/2026-09-27-mnesis-cognitive-agent-design.md`
- le plan d’implémentation actif dans `docs/superpowers/plans/`

En cas de contradiction entre le code existant, le plan et la spécification, ne pas prendre de décision silencieuse : documenter le choix effectué.
