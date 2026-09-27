# Mnesis — Plan d’implémentation du cycle cognitif apprenable

> **Pour les agents d’implémentation :** SOUS-SKILL OBLIGATOIRE : utiliser `superpowers:subagent-driven-development` ou `superpowers:executing-plans` pour exécuter ce plan tâche par tâche. Les étapes utilisent la syntaxe de cases à cocher (`- [ ]`) pour le suivi.

**Objectif :** remplacer le moteur conversationnel dirigé par intents par un cycle cognitif générique où constructions linguistiques, règles et comportements sont décrits comme des données chargeables ou apprenables.

**Architecture :** le texte est interprété par des constructions déclaratives vers des représentations sémantiques génériques. Un moteur de règles produit des actions candidates, un moteur d’actions les score selon état interne et contexte, puis un exécuteur générique produit un résultat sémantique réalisé en texte par des constructions de sortie. `ConversationService` ne conserve qu’un rôle d’orchestration.

**Pile technique :** Python 3.13+, Pydantic v2, SQLAlchemy 2.x, Alembic, SQLite, YAML, pytest.

**Spécification :** `docs/superpowers/specs/2026-09-27-cognitive-cycle-refactor-design.md`

## Contraintes globales

- Aucun LLM.
- Aucun branchement métier du type `if parsed.intent == ...` dans le cycle conversationnel.
- Le moteur Python ne doit pas connaître le français.
- Les constructions linguistiques sont des données.
- Les règles cognitives et conversationnelles sont des données.
- Les actions du moteur sont génériques.
- Toute capacité doit être traçable comme native, issue d’un paquet ou apprise.
- Les constructions/règles apprises localement restent isolées par instance.
- `core-fr` contient le bootstrap linguistique français, pas le moteur.
- Les tests existants de mémoire, confiance, isolation et provenance doivent rester verts.
- Toute documentation et tout commentaire sont en français.
- Aucun branchement Git ni worktree.

## Points de vigilance pour la revue

1. **Une construction invalide ou ambiguë** ne doit pas faire tomber le cycle : elle doit être ignorée ou produire une hypothèse de faible confiance.
2. **Deux constructions concurrentes** peuvent matcher le même texte : le moteur doit conserver plusieurs interprétations candidates avant sélection.
3. **Une construction locale d’instance** ne doit jamais fuiter vers une autre instance.
4. **Une règle déclarative mal formée** doit être rejetée lors du chargement plutôt que provoquer une erreur tardive pendant une conversation.
5. **Un texte français non reconnu** doit pouvoir aboutir à clarification ou apprentissage, sans ajout de nouveau `if` métier dans le code.

---

## Structure cible

```text
src/mnesis/
├── cognition/
│   ├── cycle.py
│   ├── activation.py
│   ├── rules.py
│   ├── actions.py
│   └── procedures.py
├── semantic/
│   ├── frames.py
│   └── matching.py
├── language/
│   ├── interpreter.py
│   ├── constructions.py
│   ├── realization.py
│   └── learning.py
├── application/
│   ├── conversation.py
│   └── construction_learning.py
└── infrastructure/
    ├── knowledge_packs.py
    └── repositories/
        └── constructions.py

knowledge/core-fr/
├── input-constructions.yaml
├── output-constructions.yaml
├── rules.yaml
└── actions.yaml
```

---

### Tâche 1 : Introduire les représentations sémantiques génériques

**Fichiers :**
- Créer : `src/mnesis/semantic/frames.py`
- Créer : `tests/unit/semantic/test_frames.py`

**Interfaces :**
- Consomme : aucune.
- Produit :
  - `SemanticValue`
  - `SemanticFrame(type: str, slots: dict[str, SemanticValue], confidence: float, provenance: list[str])`
  - structures capables de représenter proposition, requête, acte social et objectif sans dépendance linguistique.

- [x] **Étape 1 : écrire les tests en échec**

Couvrir :
- représentation d’une proposition `IS_A(chat, animal)` ;
- représentation d’un acte social `GREETING` ;
- confiance bornée ;
- sérialisation stable.

- [x] **Étape 2 : lancer les tests**

Exécuter : `pytest tests/unit/semantic/test_frames.py -v`  
Attendu : échec car les modèles n’existent pas.

- [x] **Étape 3 : implémenter les modèles minimaux**

Pas de classe spécifique `GreetingFrame` ou `DefinitionFrame` : uniquement des structures génériques.

- [x] **Étape 4 : vérifier**

Exécuter : `pytest tests/unit/semantic/test_frames.py -v`

- [x] **Étape 5 : commit**

```bash
git add src/mnesis/semantic tests/unit/semantic
git commit -m "feat: ajouter les représentations sémantiques génériques"
```

---

### Tâche 2 : Remplacer les constructions codées par des constructions déclaratives

**Fichiers :**
- Reprendre : `src/mnesis/language/constructions.py`
- Créer : `src/mnesis/language/interpreter.py`
- Créer : `tests/unit/language/test_declarative_constructions.py`

**Interfaces :**
- Consomme : `SemanticFrame`.
- Produit :
  - `InputConstruction`
  - `ConstructionMatch`
  - `ConstructionSet.match(text, lexicon) -> list[ConstructionMatch]`
  - `LanguageInterpreter.interpret(text, constructions, lexicon) -> list[SemanticFrame]`.

- [x] **Étape 1 : écrire un test de construction chargée depuis des données**

Créer en test une construction :
`"coucou" -> SemanticFrame(type="SOCIAL_ACT", slots={"act": "GREETING"})`.

Aucun mot `coucou` ne doit apparaître dans le code de production.

- [x] **Étape 2 : vérifier l’échec**

Exécuter : `pytest tests/unit/language/test_declarative_constructions.py -v`.

- [x] **Étape 3 : implémenter le matching générique**

Le moteur doit supporter au minimum :
- littéraux ;
- variables ;
- lexèmes/lemmes ;
- captures ;
- production d’un frame via substitution des variables.

- [x] **Étape 4 : ajouter le test d’ambiguïté**

Deux constructions matching le même texte doivent produire deux candidats.

- [x] **Étape 5 : vérifier et commit**

```bash
pytest tests/unit/language/test_declarative_constructions.py -v
git add src/mnesis/language tests/unit/language
git commit -m "feat: rendre les constructions linguistiques déclaratives"
```

---

### Tâche 3 : Persister constructions et provenance par instance

**Fichiers :**
- Créer : `src/mnesis/infrastructure/repositories/constructions.py`
- Modifier : `src/mnesis/infrastructure/db.py`
- Créer : `alembic/versions/0006_constructions.py`
- Créer : `tests/integration/test_construction_isolation.py`

**Interfaces :**
- Consomme : `InputConstruction`.
- Produit :
  - `ConstructionRepository.add(instance_id, construction)`
  - `ConstructionRepository.list_for_instance(instance_id, language)`
  - distinction `knowledge_pack` / `learned`.

- [x] **Étape 1 : écrire le test d’isolation**

Une construction ajoutée à A est visible dans A mais pas B.

- [x] **Étape 2 : constater l’échec**

Exécuter : `pytest tests/integration/test_construction_isolation.py -v`.

- [x] **Étape 3 : implémenter schéma et dépôt**

Champs minimum :
- id ;
- instance_id nullable pour constructions pack/globales déployées ;
- language ;
- pattern ;
- semantics ;
- confidence ;
- origin ;
- usage_count ;
- reinforced_at.

- [x] **Étape 4 : vérifier la migration**

Exécuter :
- `alembic upgrade head`
- test d’isolation.

- [x] **Étape 5 : commit**

```bash
git add src/mnesis/infrastructure alembic tests/integration
git commit -m "feat: persister les constructions apprises"
```

---

### Tâche 4 : Introduire le moteur de règles déclaratives

**Fichiers :**
- Créer : `src/mnesis/cognition/rules.py`
- Créer : `tests/unit/cognition/test_rules.py`

**Interfaces :**
- Consomme : `SemanticFrame`, état cognitif simplifié.
- Produit :
  - `RuleCondition`
  - `DeclarativeRule`
  - `RuleResult`
  - `RuleEngine.evaluate(frames, state, rules) -> list[RuleResult]`.

- [x] **Étape 1 : écrire le test d’une règle de salutation comme donnée**

Entrée :
`SOCIAL_ACT(act=GREETING)`

Règle :
proposer action `SOCIAL_RESPONSE`.

Le test doit définir la règle dans ses données, pas via une classe spécialisée.

- [x] **Étape 2 : constater l’échec**

Exécuter : `pytest tests/unit/cognition/test_rules.py -v`.

- [x] **Étape 3 : implémenter l’évaluation générique**

Support minimal :
- égalité ;
- présence d’un slot ;
- seuil numérique sur état/personnalité ;
- production d’une action candidate.

- [x] **Étape 4 : tester règle invalide**

Un opérateur inconnu ou une structure invalide est rejeté lors de la validation.

- [x] **Étape 5 : commit**

```bash
git add src/mnesis/cognition tests/unit/cognition
git commit -m "feat: ajouter le moteur de règles déclaratives"
```

---

### Tâche 5 : Ajouter le moteur d’actions et le scoring générique

**Fichiers :**
- Créer : `src/mnesis/cognition/actions.py`
- Créer : `tests/unit/cognition/test_actions.py`

**Interfaces :**
- Consomme : `RuleResult`, personnalité, affect, drives simplifiés.
- Produit :
  - `ActionCandidate(type, payload, base_score, modifiers, score)`
  - `ActionEngine.rank(candidates, state) -> list[ActionCandidate]`
  - `ActionEngine.select(...) -> ActionCandidate`.

- [ ] **Étape 1 : écrire le test de scoring**

Une action `ASK` reçoit un bonus de curiosité/extraversion selon des modificateurs décrits dans la donnée de règle.

- [ ] **Étape 2 : constater l’échec**

Exécuter : `pytest tests/unit/cognition/test_actions.py -v`.

- [ ] **Étape 3 : implémenter le score générique**

Aucun test de type :
`if action == "RELANCER"`.

Les modificateurs utilisent un chemin d’état générique, par exemple :
`personality.curiosity`, `affect.curiosity`.

- [ ] **Étape 4 : tester égalité de scores**

Départage stable et déterministe.

- [ ] **Étape 5 : commit**

```bash
git add src/mnesis/cognition tests/unit/cognition
git commit -m "feat: ajouter le moteur générique de sélection d’actions"
```

---

### Tâche 6 : Introduire l’exécuteur de procédures primitives

**Fichiers :**
- Créer : `src/mnesis/cognition/procedures.py`
- Créer : `tests/unit/cognition/test_procedures.py`

**Interfaces :**
- Consomme : `ActionCandidate`.
- Produit :
  - `ProcedureResult(semantic_output, learned_items, side_effects)`
  - `ProcedureExecutor.execute(action, context) -> ProcedureResult`.

- [ ] **Étape 1 : écrire les tests pour primitives génériques**

Couvrir :
- `ASSERT` : produire une proposition sémantique ;
- `ASK` : produire une requête sémantique ;
- `STORE` : demander persistance d’un frame ;
- `RESEARCH` : produire un objectif de recherche.

- [ ] **Étape 2 : constater l’échec**

- [ ] **Étape 3 : implémenter uniquement les primitives**

Aucune procédure `SALUER` ou `DEFINIR`.

- [ ] **Étape 4 : vérifier**

- [ ] **Étape 5 : commit**

---

### Tâche 7 : Rendre la réalisation linguistique déclarative

**Fichiers :**
- Créer : `src/mnesis/language/realization.py`
- Déprécier progressivement : `src/mnesis/language/realizer.py`
- Créer : `tests/unit/language/test_declarative_realization.py`

**Interfaces :**
- Consomme : `SemanticFrame`, `OutputConstruction`.
- Produit :
  - `OutputConstruction`
  - `LanguageRealizer.realize(frame, constructions, context) -> str`.

- [ ] **Étape 1 : écrire le test “nouvelle sortie sans code”**

Définir dans le test une construction de sortie :
`SOCIAL_ACT(GREETING) -> "Bonjour."`.

- [ ] **Étape 2 : constater l’échec**

- [ ] **Étape 3 : implémenter sélection + substitution générique**

- [ ] **Étape 4 : tester plusieurs variantes**

Sélection déterministe pour la V1 ; variation pourra venir ensuite.

- [ ] **Étape 5 : commit**

---

### Tâche 8 : Construire le `CognitiveCycle`

**Fichiers :**
- Créer : `src/mnesis/cognition/cycle.py`
- Créer : `src/mnesis/cognition/activation.py`
- Créer : `tests/unit/cognition/test_cycle.py`

**Interfaces :**
- Consomme :
  - `LanguageInterpreter`
  - `RuleEngine`
  - `ActionEngine`
  - `ProcedureExecutor`
  - `LanguageRealizer`.
- Produit :
  - `CognitiveCycle.process(instance_id, event) -> CognitiveResult`.

- [ ] **Étape 1 : écrire le test d’un cycle de salutation sans logique métier**

Le test assemble :
- construction d’entrée ;
- règle ;
- action ;
- construction de sortie.

Le cycle doit produire `Bonjour.`.

- [ ] **Étape 2 : constater l’échec**

- [ ] **Étape 3 : implémenter l’orchestration minimale**

Pipeline strict :
interpret → activate → rules → actions → execute → realize → trace.

- [ ] **Étape 4 : ajouter test de non-reconnaissance**

Aucune construction → une règle générique peut proposer `CLARIFY`.

- [ ] **Étape 5 : commit**

---

### Tâche 9 : Migrer `core-fr` vers constructions/règles déclaratives

**Fichiers :**
- Créer : `knowledge/core-fr/input-constructions.yaml`
- Créer : `knowledge/core-fr/output-constructions.yaml`
- Créer : `knowledge/core-fr/rules.yaml`
- Modifier : `src/mnesis/infrastructure/knowledge_packs.py`
- Test : `tests/unit/infrastructure/test_core_fr_cognitive_pack.py`

**Interfaces :**
- Consomme : modèles des tâches 2, 4 et 7.
- Produit : `core-fr` capable de porter :
  - salutations ;
  - assertion `X est un Y` ;
  - question de définition ;
  - clarification ;
  - doute ;
  - relance.

- [ ] **Étape 1 : écrire les tests de contenu**

Vérifier que le paquet charge constructions d’entrée, sorties et règles.

- [ ] **Étape 2 : constater l’échec**

- [ ] **Étape 3 : migrer les comportements existants dans YAML**

Le code Python ne doit contenir aucun des mots/intentions spécifiques nécessaires au test.

- [ ] **Étape 4 : vérifier**

- [ ] **Étape 5 : commit**

---

### Tâche 10 : Réduire `ConversationService` à un orchestrateur mince

**Fichiers :**
- Remplacer : `src/mnesis/application/conversation.py`
- Test : `tests/architecture/test_conversation_service.py`

**Interfaces :**
- Consomme : `CognitiveCycle`.
- Produit :
  - `ConversationService.handle(instance_id, text) -> ConversationTurn`.

- [ ] **Étape 1 : écrire le test architectural**

Lire le source de `conversation.py` et vérifier l’absence de :
- `SALUER`
- `DEFINIR`
- `DEMANDER_DEFINITION`
- `RELANCER`
- `parsed.intent`.

- [ ] **Étape 2 : constater l’échec sur le code actuel**

- [ ] **Étape 3 : remplacer le service**

Le service :
1. construit l’événement ;
2. appelle `CognitiveCycle.process()` ;
3. adapte le résultat vers `ConversationTurn`.

- [ ] **Étape 4 : exécuter les tests comportementaux existants adaptés**

- [ ] **Étape 5 : commit**

---

### Tâche 11 : Prouver l’ajout d’une nouvelle formulation sans modifier Python

**Fichiers :**
- Test : `tests/behavior/test_dynamic_construction.py`

**Interfaces :**
- Consomme : dépôt de constructions + cycle.
- Produit : preuve architecturale B.

- [ ] **Étape 1 : écrire le test**

Après démarrage :
- ajouter une construction `"Coucou" → SOCIAL_ACT(GREETING)` uniquement par donnée ;
- envoyer « Coucou » ;
- vérifier réponse sociale correcte.

- [ ] **Étape 2 : constater l’échec**

- [ ] **Étape 3 : corriger uniquement le chargement dynamique si nécessaire**

Aucun ajout de condition `coucou`.

- [ ] **Étape 4 : vérifier**

- [ ] **Étape 5 : commit**

---

### Tâche 12 : Apprentissage local d’une construction

**Fichiers :**
- Créer : `src/mnesis/application/construction_learning.py`
- Test : `tests/behavior/test_learned_construction.py`

**Interfaces :**
- Consomme : `ConstructionRepository`.
- Produit :
  - `ConstructionLearningService.teach(instance_id, form, semantic_frame, source) -> LearnedConstruction`
  - `reinforce(instance_id, construction_id, evidence) -> LearnedConstruction`.

- [ ] **Étape 1 : écrire le test du scénario “Ça roule ?”**

1. inconnu au départ ;
2. enseignement `Ça roule ? → QUERY(INTERLOCUTOR_STATE)` ;
3. confiance initiale faible ;
4. renforcement ;
5. seuil d’utilisation atteint ;
6. expression comprise sur nouvelle conversation.

- [ ] **Étape 2 : vérifier l’échec**

- [ ] **Étape 3 : implémenter apprentissage + renforcement**

Seuil V1 explicite et documenté, par exemple `usable_confidence >= 0.70`.

- [ ] **Étape 4 : ajouter test d’isolation**

Instance B ne comprend toujours pas cette construction.

- [ ] **Étape 5 : commit**

---

### Tâche 13 : Transformer la recherche lexicale en action générique `RESEARCH`

**Fichiers :**
- Modifier : `src/mnesis/cognition/procedures.py`
- Créer : `src/mnesis/cognition/research.py`
- Modifier : `src/mnesis/application/learning.py`
- Test : `tests/behavior/test_research_action.py`

**Interfaces :**
- Consomme : KnowledgeGap / action `RESEARCH`.
- Produit : `ResearchExecutor.execute(goal) -> LearningResult`.

- [ ] **Étape 1 : écrire le test**

Mot inconnu → règle déclarative → action `RESEARCH(kind=LEXICAL)` → source dictionnaire → apprentissage.

- [ ] **Étape 2 : constater l’échec**

- [ ] **Étape 3 : déplacer la dépendance dictionnaire hors du service conversationnel**

- [ ] **Étape 4 : vérifier provenance et confiance**

- [ ] **Étape 5 : commit**

---

### Tâche 14 : Adapter mémoire, traces et API au nouveau cycle

**Fichiers :**
- Modifier : `src/mnesis/domain/traces.py`
- Modifier : `src/mnesis/infrastructure/repositories/traces.py`
- Modifier : `src/mnesis/api/app.py`
- Modifier : `src/mnesis/api/routes/diagnostics.py`
- Tests : `tests/integration/api/test_cognitive_trace_api.py`

**Interfaces :**
- Consomme : `CognitiveResult`.
- Produit : trace comprenant :
  - interprétations candidates ;
  - règles déclenchées ;
  - actions candidates ;
  - score final ;
  - construction de sortie utilisée.

- [ ] **Étape 1 : écrire le test API**

- [ ] **Étape 2 : constater l’échec**

- [ ] **Étape 3 : enrichir la trace sans exposer les détails dans la conversation principale**

- [ ] **Étape 4 : vérifier**

- [ ] **Étape 5 : commit**

---

### Tâche 15 : Test d’interchangeabilité linguistique

**Fichiers :**
- Test : `tests/architecture/test_language_independence.py`

**Interfaces :**
- Consomme : cycle générique.
- Produit : preuve architecturale E.

- [ ] **Étape 1 : écrire un mini paquet anglais uniquement dans le test**

Par exemple :
- `"hello" → SOCIAL_ACT(GREETING)`
- sortie `SOCIAL_ACT(GREETING) → "Hello."`.

- [ ] **Étape 2 : exécuter avec le même `CognitiveCycle`**

- [ ] **Étape 3 : vérifier qu’aucune modification Python n’est requise**

Le test doit réussir sans import de module spécifique français.

- [ ] **Étape 4 : commit**

---

### Tâche 16 : Valider la nouvelle tranche verticale

**Fichiers :**
- Remplacer/adapter : `tests/behavior/test_v1_vertical_slice.py`
- Modifier : `README.md`

**Interfaces :**
- Consomme : toute la nouvelle architecture.
- Produit : scénario de référence du moteur apprenable.

- [ ] **Étape 1 : couvrir le scénario complet**

Le test doit démontrer :

1. instance créée ;
2. `core-fr` déployé ;
3. « Bonjour » compris via une construction de donnée ;
4. `X est un Y` compris via une construction ;
5. question de définition traitée via règle/action générique ;
6. ajout de « Coucou » sans modification Python ;
7. construction locale apprise puis renforcée ;
8. isolation de cette construction ;
9. mot inconnu déclenchant une action `RESEARCH` ;
10. doute face à contradiction ;
11. personnalité influençant le scoring ;
12. trace cognitive complète.

- [ ] **Étape 2 : lancer et constater les éventuels écarts**

- [ ] **Étape 3 : corriger uniquement ce qui appartient à ce refactor**

- [ ] **Étape 4 : lancer la vérification complète**

Exécuter :
- `pytest -v`
- `ruff check .`
- `mypy src`
- `cd web && npm test`
- `cd web && npm run build`
- migration Alembic sur base SQLite vierge.

- [ ] **Étape 5 : documenter la nouvelle architecture**

README :
- moteur générique ;
- rôle de `core-fr` ;
- ajout dynamique de constructions ;
- apprentissage local ;
- exemple de diagnostic.

- [ ] **Étape 6 : commit**

```bash
git add .
git commit -m "refactor: remplacer les intents par un cycle cognitif apprenable"
```

---

## Hors de ce plan

- induction grammaticale générale depuis corpus libre ;
- génération morphologique complète du français ;
- apprentissage mathématique procédural ;
- oubli/consolidation avancés ;
- recherche Web multi-source générale ;
- extraction sémantique de pages Wikipédia libres ;
- voix et vision.

## Critère de sortie

Le refactor est considéré terminé lorsque Mnesis peut comprendre et produire de nouveaux comportements conversationnels ajoutés ou appris sous forme de données, sans ajout de branches métier dans le code Python, tout en conservant provenance, confiance, isolation et inspectabilité.
