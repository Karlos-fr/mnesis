# Mnesis — Refactor du moteur conversationnel vers un cycle cognitif apprenable

**Statut :** Brouillon pour revue  
**Date :** 2026-09-27  
**Projet :** Mnesis  
**Dépôt :** Karlos-fr/mnesis

## 1. Objectif

Remplacer l’architecture conversationnelle actuelle, encore trop dirigée par des intentions codées en dur, par un moteur cognitif générique dans lequel :

- les constructions linguistiques sont des données ;
- les règles de raisonnement sont des données ;
- les actions conversationnelles sont des données ;
- les associations entre forme linguistique, sens et comportement peuvent être chargées depuis un socle ou apprises ensuite ;
- le cœur Python ne contient pas de branchements métier du type `if intent == "SALUER"`, `DEFINIR`, `DEMANDER_DEFINITION`, etc. ;
- une nouvelle façon de parler ou une nouvelle règle conversationnelle peut être ajoutée sans modifier le code du moteur ;
- à terme, Mnesis peut apprendre lui-même de nouvelles constructions et procédures.

Le moteur Python conserve uniquement des mécanismes cognitifs génériques.

## 2. Principe directeur

Le comportement de Mnesis doit être produit par :

```text
MOTEUR GÉNÉRIQUE
      +
CONNAISSANCES
      +
CONSTRUCTIONS LINGUISTIQUES
      +
RÈGLES
      +
PROCÉDURES
      +
MÉMOIRE
      +
ÉTAT INTERNE
      =
COMPORTEMENT
```

Le moteur ne doit pas « connaître » le français.

Il doit uniquement savoir :

- reconnaître/appliquer une construction décrite sous forme de données ;
- créer et manipuler des représentations sémantiques ;
- activer des connaissances et souvenirs ;
- exécuter des règles génériques ;
- proposer et évaluer des actions ;
- exécuter une action générique ;
- réaliser une représentation sémantique avec les connaissances linguistiques disponibles ;
- apprendre et persister de nouvelles structures.

## 3. Problème de l’architecture actuelle

Le fichier `ConversationService` actuel encode encore explicitement des comportements métier :

```python
if parsed.intent == "SALUER":
    ...
elif parsed.intent == "DEFINIR":
    ...
elif parsed.intent == "DEMANDER_DEFINITION":
    ...
```

Cette approche est acceptable uniquement comme bootstrap de validation technique.

Elle ne doit pas devenir la base du produit, car elle impose :

- d’ajouter du code Python pour chaque nouvelle capacité linguistique ;
- de figer les intentions dans le moteur ;
- de limiter l’apprentissage à des valeurs que le moteur connaît déjà ;
- de confondre langage et logique de contrôle ;
- de transformer progressivement Mnesis en chatbot à règles codées à la main.

Le refactor doit supprimer cette dépendance.

## 4. Architecture cible

```text
Message utilisateur
       │
       ▼
┌─────────────────────────────┐
│ 1. LanguageInterpreter      │
│ constructions apprises      │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 2. SemanticRepresentation  │
│ frames / concepts / rôles   │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 3. ActivationEngine         │
│ mémoire / concepts / faits  │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 4. RuleEngine               │
│ règles déclaratives         │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 5. ActionEngine             │
│ propositions + scoring      │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 6. ProcedureExecutor        │
│ actions génériques          │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 7. LanguageRealizer         │
│ constructions de sortie     │
└──────────────┬──────────────┘
               ▼
          Réponse texte
```

Le `ConversationService` devient un orchestrateur mince du cycle.

## 5. Représentation sémantique intermédiaire

Le langage ne doit pas conduire directement à une réponse.

Une phrase est transformée en représentation sémantique.

Exemples :

```text
"Bonjour"

→ Event(
    type = SOCIAL_ACT,
    act = GREETING
  )
```

```text
"Le chat est un animal"

→ Proposition(
    predicate = IS_A,
    subject = Concept("chat"),
    object = Concept("animal")
  )
```

```text
"Qu'est-ce qu'un chat ?"

→ Query(
    kind = DEFINITION,
    target = Concept("chat")
  )
```

Ces structures sont génériques et ne doivent pas dépendre du français.

## 6. Constructions linguistiques comme données

Une construction associe :

- une forme ;
- des contraintes lexicales ou grammaticales ;
- des variables ;
- une représentation sémantique produite ;
- un niveau de confiance ;
- une provenance ;
- un niveau de maîtrise.

Exemple conceptuel :

```yaml
id: fr-is-a-001
language: fr
pattern:
  - variable: X
  - lemma: être
  - article: indefini
  - variable: Y
semantics:
  type: proposition
  predicate: IS_A
  subject: X
  object: Y
origin: knowledge_pack
confidence: 0.99
```

Le moteur applique cette construction sans connaître `IS_A` comme cas conversationnel particulier.

## 7. Constructions de sortie

La génération suit la même logique.

Exemple :

```yaml
semantic_pattern:
  type: proposition
  predicate: IS_A
surface:
  - "Un {subject} est un {object}."
  - "{subject} est un {object}."
```

Une action produit une intention sémantique, puis le réalisateur recherche une construction de sortie compatible.

Le moteur ne doit pas appeler directement des méthodes comme :

- `greeting()` ;
- `definition()` ;
- `uncertain_definition()`.

Ces formulations doivent venir des connaissances linguistiques.

## 8. Règles comme données

Les règles comportementales et cognitives doivent être représentées hors du code.

Exemple :

```yaml
when:
  semantic_type: SOCIAL_ACT
  act: GREETING
then:
  propose_action:
    type: RESPOND_SOCIAL
    semantic_goal:
      type: SOCIAL_ACT
      act: GREETING
base_score: 0.8
```

Une règle peut également prendre en compte :

- confiance ;
- mémoire ;
- personnalité ;
- émotions ;
- besoins ;
- contexte conversationnel.

Exemple :

```text
SI
  acte entrant = GREETING
  ET curiosité > 0.8
  ET extraversion > 0.6
ALORS
  proposer RESPOND_SOCIAL + ASK_INTERLOCUTOR_STATE
```

Ces règles doivent être données au moteur, pas codées dans un `if`.

## 9. Moteur d’actions générique

L’ActionEngine reçoit des propositions d’actions.

Exemples d’actions génériques :

- ASSERT ;
- ASK ;
- STORE ;
- RETRIEVE ;
- CLARIFY ;
- SOCIAL_RESPONSE ;
- RESEARCH ;
- EXECUTE_PROCEDURE ;
- REMAIN_SILENT.

Ces catégories peuvent être natives si elles correspondent à des primitives cognitives.

Leur contenu sémantique, lui, est appris/configuré.

Exemple :

```text
Action:
  type = ASSERT
  payload =
    Proposition(IS_A, chat, animal)
```

## 10. Cycle cognitif

Le nouveau cœur doit suivre un cycle proche de :

```python
perception = interpreter.interpret(event)
activation = activation_engine.activate(perception)
learning_engine.observe(perception, activation)
derived = rule_engine.evaluate(perception, activation)
candidates = action_engine.propose(perception, activation, derived, state)
selected = action_engine.select(candidates, state)
result = procedure_executor.execute(selected)
response = language_realizer.realize(result)
memory.record(event, perception, selected, result)
```

Aucun branchement ne doit tester une intention conversationnelle métier.

## 11. Noyau natif minimal

Certaines primitives doivent rester codées.

Exemples :

- STORE ;
- RETRIEVE ;
- MATCH ;
- COMPARE ;
- TEST ;
- ITERATE ;
- INCREMENT ;
- ASSOCIATE ;
- ACTIVATE ;
- EVALUATE_CONFIDENCE ;
- EXECUTE_RULE ;
- SELECT_ACTION.

Ces primitives constituent les capacités « innées » de Mnesis.

Elles doivent être peu nombreuses, génériques, documentées et testables.

## 12. `core-fr` devient une éducation initiale

Le paquet `core-fr` doit être restructuré pour fournir :

- lexique initial ;
- catégories grammaticales ;
- constructions d’entrée ;
- constructions de sortie ;
- concepts conversationnels ;
- règles sociales de base ;
- morphologie minimale ;
- expressions permettant :
  - saluer ;
  - poser une question ;
  - affirmer ;
  - nier ;
  - demander une définition ;
  - exprimer un doute ;
  - demander une clarification ;
  - relancer.

Ces éléments ne doivent plus nécessiter de code Python spécifique au français.

## 13. Apprentissage de nouvelles constructions

Mnesis doit pouvoir enregistrer de nouvelles constructions.

Première étape :

- une construction peut être ajoutée dynamiquement dans la base ou dans un paquet ;
- elle devient immédiatement utilisable sans redémarrage ni modification de code.

Étape suivante :

- Mnesis peut apprendre une construction à partir de plusieurs exemples/corrections.

Exemple :

```text
Utilisateur : "Ça roule ?"
Mnesis : ne comprend pas.

Utilisateur : "Ça roule ? veut dire comment vas-tu ?"

→ association créée avec confiance faible.
```

Après confirmations supplémentaires :

```text
forme : "ça roule ?"
sens : ASK_INTERLOCUTOR_STATE
confiance : 0.82
origine : learned
```

Mnesis doit alors comprendre cette expression sans changement de code.

## 14. Apprentissage du sens

L’apprentissage ne doit pas se limiter au texte exact.

Le système doit pouvoir associer :

- plusieurs formes à une même représentation sémantique ;
- une même forme à plusieurs sens selon le contexte ;
- des niveaux de confiance distincts.

Exemple :

```text
"Salut"
"Bonjour"
"Coucou"

→ SOCIAL_ACT(GREETING)
```

Le concept interne est distinct des mots utilisés pour l’exprimer.

## 15. Mémoire et apprentissage

Chaque interprétation doit pouvoir :

- renforcer une construction ;
- affaiblir une hypothèse erronée ;
- créer une nouvelle association ;
- produire une demande de clarification ;
- déclencher une recherche ;
- mémoriser une correction.

La mémoire épisodique conserve l’événement ayant conduit à l’apprentissage.

## 16. Incertitude linguistique

Le moteur peut produire plusieurs interprétations candidates.

Exemple :

```text
"Il est lourd."
```

peut générer plusieurs analyses.

Chaque candidate possède :

- score ;
- constructions utilisées ;
- concepts impliqués ;
- contexte compatible ;
- provenance.

Le moteur peut :

- sélectionner l’interprétation la plus probable ;
- demander une clarification ;
- conserver plusieurs hypothèses.

## 17. Émotions, personnalité et motivations

Ces dimensions interviennent dans le scoring des actions et non dans des branches spécifiques.

Exemple :

```text
score(RESEARCH)
 += curiosity * weight_curiosity

score(ASK_FOLLOWUP)
 += extraversion * weight_extraversion
 += social_need * weight_social
```

Les coefficients doivent être explicites, configurables et inspectables.

## 18. Recherche autonome

Une action générique `RESEARCH` peut être proposée lorsque :

- concept inconnu ;
- confiance faible ;
- contradiction ;
- besoin de clarification factuelle.

Le moteur ne doit pas appeler Wiktionnaire directement depuis `ConversationService`.

Un exécuteur d’action recherche la source adaptée à l’objectif.

Exemple :

```text
KnowledgeGap(word="arboricole")
→ Rule proposes RESEARCH(kind=LEXICAL)
→ ResearchExecutor selects dictionary source
→ learning event
→ semantic memory updated
```

## 19. Séparation des responsabilités

### CognitiveCycle

Orchestre les étapes du cycle.

Ne connaît aucune intention métier.

### LanguageInterpreter

Applique les constructions disponibles.

### SemanticEngine

Manipule frames, propositions, questions, événements.

### ActivationEngine

Active concepts, faits et souvenirs reliés.

### RuleEngine

Évalue les règles déclaratives.

### ActionEngine

Produit et classe des actions candidates.

### ProcedureExecutor

Exécute les primitives/procédures.

### LanguageRealizer

Transforme une représentation sémantique en texte.

### LearningEngine

Observe, renforce, crée ou corrige des connaissances et constructions.

### Memory

Persiste épisodes et connaissances.

## 20. Refactor de `ConversationService`

Le service actuel doit perdre toute connaissance métier.

Cible :

```python
class ConversationService:
    def handle(self, instance_id, text):
        event = ConversationEvent(...)
        result = self.cognitive_cycle.process(instance_id, event)
        return ConversationTurn(...)
```

Il peut conserver uniquement :

- validation ;
- création de l’événement ;
- appel du cycle ;
- adaptation du résultat vers l’API.

## 21. Persistance

Ajouter les domaines nécessaires :

- constructions linguistiques ;
- règles ;
- actions/procédures ;
- associations forme ↔ sens ;
- poids/confiances ;
- événements d’apprentissage.

Chaque élément doit conserver :

- instance ou paquet propriétaire ;
- origine ;
- niveau de confiance ;
- date de création ;
- date de renforcement ;
- compteur d’utilisation.

## 22. Compatibilité avec les instances

Les constructions et règles suivent le même modèle que les connaissances :

- fournies par un Knowledge Pack ;
- apprises localement ;
- isolées entre instances ;
- exportables volontairement.

Une instance peut donc développer progressivement son propre langage.

## 23. Preuves architecturales obligatoires

Le refactor n’est pas accepté tant que ces tests ne passent pas.

### Test A — aucune logique métier dans `ConversationService`

Le service ne doit pas tester :

- SALUER ;
- DEFINIR ;
- DEMANDER_DEFINITION ;
- RELANCER ;
- ou une autre intention métier.

### Test B — nouvelle formulation sans code Python

Avec le moteur déjà installé :

1. ajouter une construction dans les données :
   `"Coucou" → SOCIAL_ACT(GREETING)` ;
2. ne modifier aucun fichier Python ;
3. vérifier que Mnesis comprend et répond correctement à « Coucou ».

### Test C — nouvelle construction locale

1. instance A reçoit une construction nouvelle ;
2. instance A la comprend ;
3. instance B ne la comprend pas ;
4. aucune modification de code.

### Test D — construction apprise

1. une expression est inconnue ;
2. un événement d’enseignement crée une hypothèse ;
3. des confirmations renforcent sa confiance ;
4. la construction passe à un niveau utilisable ;
5. un nouvel échange réutilise la construction.

### Test E — langue interchangeable

Le moteur ne contient aucune dépendance fonctionnelle directe aux mots français.

Un futur `core-en` doit pouvoir utiliser le même cycle cognitif.

## 24. Stratégie de migration

Le refactor se fait progressivement.

### Phase 1

Créer les nouvelles structures génériques sans supprimer l’ancien flux.

### Phase 2

Migrer `core-fr` vers constructions/règles déclaratives.

### Phase 3

Faire passer les cas existants :

- salutation ;
- définition ;
- question de définition ;
- doute ;
- relance ;
- apprentissage lexical.

par le nouveau cycle.

### Phase 4

Supprimer les branches métier de `ConversationService`.

### Phase 5

Ajouter l’apprentissage de constructions.

Cette stratégie évite une réécriture totale non testée.

## 25. Hors périmètre immédiat

Ce refactor ne cherche pas encore à résoudre :

- toute la grammaire française ;
- la compréhension libre de textes arbitraires ;
- l’induction grammaticale générale ;
- l’apprentissage complet du langage comme un enfant ;
- les procédures mathématiques complexes ;
- la vision ou la voix.

Il doit fournir l’architecture qui permettra ces évolutions sans réécrire le moteur.

## 26. Critères de réussite

Le refactor est réussi lorsque :

- `ConversationService` ne contient plus de logique métier fondée sur les intents ;
- ajouter une nouvelle construction conversationnelle ne demande pas de modifier Python ;
- `core-fr` contient les connaissances linguistiques de bootstrap ;
- les mêmes composants génériques interprètent toutes les constructions ;
- règles et comportements sont pilotés par des données ;
- personnalité et émotions modifient les scores plutôt que les branches métier ;
- recherche lexicale et clarification sont déclenchées comme actions ;
- les constructions peuvent être apprises, renforcées et utilisées localement ;
- l’origine de chaque capacité reste traçable ;
- les tests V1 existants restent verts ou sont adaptés au nouveau modèle sans perdre leurs garanties.

Le but est que Mnesis ne soit plus un chatbot à intents, mais un moteur cognitif textuel dont le langage et le comportement peuvent réellement évoluer avec l’apprentissage.
