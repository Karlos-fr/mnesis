# Mnesis

Mnesis est un agent conversationnel cognitif expérimental **sans LLM**. Son objectif est d'apprendre progressivement le langage, des connaissances, des souvenirs et des compétences à partir de textes et d'interactions, tout en conservant une représentation explicite et inspectable de ce qu'il sait, de ce dont il doute et de la manière dont il l'a appris.

La V1 se concentre sur une conversation textuelle simple en français, un socle linguistique versionné, la mémoire épisodique, la provenance des connaissances, les niveaux de confiance, les contradictions et l'apprentissage lexical.

## Principes

- aucune dépendance à un LLM pour comprendre, raisonner ou répondre ;
- mots et concepts représentés séparément ;
- plusieurs instances Mnesis isolées ;
- connaissances partageables uniquement via des paquets explicitement déployés ;
- provenance et confiance conservées pour les connaissances apprises ;
- utilisateur traité comme une source parmi d'autres ;
- décisions et apprentissages inspectables.

## Prérequis

- Python 3.13 ou supérieur ;
- Node.js 22 ou supérieur pour l'interface Web ;
- npm ;
- SQLite, fourni avec Python dans la plupart des installations.

Aucun serveur de base de données n'est nécessaire pour la V1.

## Installation Python

```bash
python -m venv .venv
```

Sous Linux/macOS :

```bash
source .venv/bin/activate
```

Sous Windows PowerShell :

```powershell
.venv\Scripts\Activate.ps1
```

Installer ensuite Mnesis et les outils de développement :

```bash
python -m pip install -e ".[dev]"
```

## Préparer la base

La configuration par défaut utilise `mnesis.db` à la racine du projet.

```bash
alembic upgrade head
```

## Construire l'interface Web

```bash
cd web
npm install
npm run build
cd ..
```

L'interface est volontairement réalisée en TypeScript natif pour la V1 : elle reste légère et ne contient aucune logique cognitive.

## Lancer Mnesis

```bash
uvicorn mnesis.api.app:app --reload
```

Puis ouvrir :

```text
http://127.0.0.1:8000/
```

Lorsque le répertoire `web/dist` existe, FastAPI sert directement l'interface Web à la racine. Les routes API restent sous `/api/v1`.

## Créer une instance par API

```bash
curl -X POST http://127.0.0.1:8000/api/v1/instances \
  -H "Content-Type: application/json" \
  -d '{"name":"Personnel","locale":"fr-FR"}'
```

La réponse fournit l'identifiant de l'instance.

## Déployer explicitement `core-fr`

Le socle français n'est pas une connaissance globale implicite. Il est déployé volontairement dans chaque instance qui doit l'utiliser :

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/instances/<INSTANCE_ID>/knowledge-packs/core-fr
```

L'interface Web effectue ce déploiement explicitement après la création de son instance.

## Envoyer un message

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/instances/<INSTANCE_ID>/messages \
  -H "Content-Type: application/json" \
  -d '{"text":"Bonjour"}'
```

La réponse contient notamment `trace_id`, qui permet d'inspecter la décision cognitive :

```bash
curl \
  http://127.0.0.1:8000/api/v1/instances/<INSTANCE_ID>/traces/<TRACE_ID>
```

## Apprentissage lexical

Lorsqu'un message réduit à un mot inconnu est reçu et qu'aucune construction connue ne s'applique, Mnesis peut demander une définition au Wiktionnaire français. La définition est transformée en :

- un lexème ;
- un concept ;
- une affirmation `DEFINI_COMME` ;
- une preuve conservant l'URL de la source ;
- un niveau de confiance initial.

Une définition trouvée sur Internet n'est donc jamais assimilée à une vérité absolue.

## Tests Python

```bash
pytest -v
```

Qualité statique :

```bash
ruff check .
mypy src
```

## Tests Web

```bash
cd web
npm test
npm run build
```


## Architecture cognitive apprenable

La conversation n'est plus pilotée par une liste d'intentions codées en Python. Le flux principal est désormais :

```text
texte
  ↓
constructions d'entrée déclaratives
  ↓
frames sémantiques
  ↓
règles déclaratives
  ↓
actions candidates + scoring
  ↓
primitives cognitives
  ↓
construction de sortie déclarative
  ↓
texte
```

`ConversationService` ne connaît donc ni `SALUER`, ni `DEFINIR`, ni une autre intention métier. Le français de démarrage réside dans `knowledge/core-fr/`.

### Ajouter une nouvelle formulation sans modifier Python

Une construction d'entrée associe une forme à un sens. Une instance peut par exemple recevoir localement une construction équivalente à :

```yaml
language: fr
pattern:
  - literal: coucou
semantics:
  type: SOCIAL_ACT
  slots:
    act: GREETING
```

Le même moteur peut immédiatement interpréter cette forme si la construction est active. Les constructions apprises localement restent isolées entre instances.

### Apprentissage d'une construction

Une construction enseignée commence avec une confiance faible. Elle n'est utilisée qu'après renforcement au-delà du seuil d'utilisation. Cela permet à Mnesis de distinguer une hypothèse linguistique d'une construction réellement maîtrisée.

### Recherche autonome

Un mot isolé inconnu devient un `KNOWLEDGE_GAP`. Les règles de `core-fr` peuvent alors proposer l'action générique `RESEARCH`. L'exécuteur spécialisé choisit la source lexicale, apprend la définition avec provenance et confiance, puis cette connaissance devient réutilisable dans une conversation ultérieure.

### Diagnostic cognitif

Les traces exposent notamment :

- les interprétations sémantiques candidates ;
- les règles déclenchées ;
- les actions candidates et leurs scores ;
- l'action sélectionnée ;
- la construction de sortie utilisée ;
- l'état affectif observé.

Cela permet de comprendre pourquoi Mnesis a répondu d'une certaine manière sans afficher ces détails dans la conversation principale.

## Documentation de conception

- spécification initiale : `docs/superpowers/specs/2026-09-27-mnesis-cognitive-agent-design.md` ;
- spécification du cycle cognitif : `docs/superpowers/specs/2026-09-27-cognitive-cycle-refactor-design.md` ;
- plan du refactor cognitif : `docs/superpowers/plans/2026-09-27-cognitive-cycle-refactor.md` ;
- plan V1 : `docs/superpowers/plans/2026-09-27-mnesis-v1.md` ;
- règles de développement : `AGENT.md`.

## État de la V1

La première tranche fonctionnelle vise à démontrer qu'une instance peut :

1. recevoir et mémoriser des échanges textuels ;
2. utiliser un socle français versionné ;
3. distinguer les mots des concepts ;
4. apprendre un mot absent depuis une source lexicale ;
5. réutiliser ensuite cette définition ;
6. conserver provenance et niveau de confiance ;
7. détecter des affirmations contradictoires ;
8. exprimer un doute plutôt que masquer l'incertitude ;
9. isoler ses apprentissages de ceux d'une autre instance ;
10. exposer une trace inspectable de ses décisions.

Le comptage réellement appris, la recherche Web multi-source, l'oubli avancé, l'apprentissage généralisé de procédures et les adaptateurs de réseaux sociaux feront l'objet d'étapes ultérieures.
