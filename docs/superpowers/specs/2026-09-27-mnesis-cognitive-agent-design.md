# Mnesis — Spécification de conception de l’agent conversationnel cognitif

**Statut :** Brouillon pour revue  
**Date :** 2026-09-27  
**Projet :** Mnesis  
**Dépôt :** Karlos-fr/mnesis

## 1. Objectif

Mnesis est un agent conversationnel cognitif expérimental, sans LLM, capable d’apprendre progressivement le langage, des connaissances, des compétences, des concepts et des comportements conversationnels à partir de textes et d’interactions.

Le projet n’a pas pour objectif d’imiter un LLM à l’aide de règles ou de gabarits sophistiqués. Il vise au contraire à explorer une architecture cognitive explicite et inspectable, dans laquelle les connaissances, les souvenirs, le langage acquis, le raisonnement, l’incertitude, les émotions, la personnalité et les décisions comportementales sont représentés directement et peuvent être examinés, testés et expliqués.

Principe de conception fondamental :

> Si Mnesis affirme avoir appris, mémorisé, inféré, oublié, douté ou décidé quelque chose, son état interne doit contenir une représentation inspectable permettant d’expliquer pourquoi.

## 2. Vision du produit

Mnesis doit, à terme, se comporter comme une entité conversationnelle persistante dont les capacités et les connaissances sont façonnées par son histoire.

Il doit pouvoir :

- converser par texte sans dépendre d’un grand modèle de langage ;
- apprendre de nouveaux mots et de nouvelles constructions linguistiques ;
- apprendre des faits et des concepts à partir des conversations et de sources textuelles ;
- rechercher de manière autonome des informations sur Internet lorsqu’il détecte une lacune de connaissance ;
- conserver la provenance et le niveau de confiance associés aux connaissances apprises ;
- douter d’une information incertaine et exprimer ce doute ;
- détecter les contradictions entre différentes affirmations ;
- considérer les utilisateurs comme des sources d’information parmi d’autres, et non comme des autorités absolues ;
- protéger les connaissances fortement fiables issues d’un socle déployé contre des affirmations contradictoires peu étayées ;
- apprendre des règles et des procédures plutôt que simplement mémoriser des réponses ;
- acquérir des compétences, comme compter, à partir de primitives cognitives plus simples ;
- conserver des souvenirs épisodiques des interactions et des connaissances sémantiques dérivées de celles-ci ;
- oublier, renforcer et consolider des informations avec le temps ;
- maintenir des émotions mesurables influençant son comportement ;
- posséder une personnalité relativement stable ;
- agir sous l’effet de motivations internes comme la curiosité ;
- initier ou relancer des sujets sans attendre systématiquement une question directe ;
- expliquer pourquoi il a produit une réponse ou pourquoi il croit quelque chose.

## 3. Périmètre initial

La première grande phase de développement est volontairement **uniquement textuelle**.

### Inclus

- conversation textuelle ;
- apprentissage lexical ;
- acquisition de connaissances sémantiques ;
- apprentissage de règles et de procédures ;
- mémoire épisodique et mémoire sémantique ;
- gestion de l’incertitude et des croyances ;
- recherche autonome d’informations textuelles sur le Web ;
- personnalité et état émotionnel ;
- initiative conversationnelle ;
- plusieurs instances Mnesis isolées ;
- socles de connaissances partageables et déployables à la demande ;
- API HTTP en vue d’un accès en ligne.

### Explicitement reporté

- reconnaissance vocale ;
- synthèse vocale ;
- vision ;
- robotique ;
- interaction physique incarnée ;
- contrôle autonome d’un ordinateur ;
- compréhension libre et générale de n’importe quelle page Web ;
- génération de secours basée sur un LLM.

Ces capacités pourront être ajoutées ultérieurement sans modifier les principes fondamentaux du modèle cognitif.

## 4. Orientation technologique

La première implémentation utilisera :

- **Python 3.13+** pour le moteur cognitif ;
- **FastAPI** pour l’exposition sous forme de service/API ;
- **SQLite** pour la persistance V1, via SQLAlchemy et Alembic, avec compatibilité d’architecture prévue pour une migration ultérieure vers PostgreSQL ;
- **TypeScript** pour une future interface navigateur.

Le moteur cognitif ne doit pas dépendre de l’interface Web. Il doit pouvoir être utilisé depuis les tests, une interface en ligne de commande, l’API HTTP ou de futurs adaptateurs.

La première version privilégiera une persistance relationnelle simple et des modèles de domaine explicites plutôt qu’une base de données graphe dédiée. Les connaissances sont naturellement structurées comme un graphe, mais **SQLite** est suffisant pour la V1 et simplifie fortement l’installation locale, les tests et l’expérimentation.

La couche de persistance doit toutefois passer par **SQLAlchemy** et **Alembic**, sans dépendances inutiles à des comportements propres à SQLite, afin de permettre une migration ultérieure vers **PostgreSQL** pour les déploiements publics, concurrents ou à plus grande échelle.

## 5. Architecture générale

```text
                     Sources textuelles externes
               dictionnaire / Web / encyclopédie
                            |
                            v
+-------------+      +-----------------------+
| Utilisateur |----->| Pipeline linguistique |
| / Canal     |      +-----------+-----------+
+-------------+                  |
                                 v
                       +----------------------+
                       | Moteur cognitif      |
                       |                      |
                       | interprétation       |
                       | raisonnement         |
                       | objectifs / besoins  |
                       | sélection d’action   |
                       +-----+-----+-----+----+
                             |     |     |
               +-------------+     |     +-------------+
               v                   v                   v
        +--------------+    +---------------+   +---------------+
        | Mémoire      |    | Connaissances |   | Affect        |
        | épisodique   |    | concepts      |   | émotions      |
        | de travail   |    | relations     |   | personnalité  |
        | procédurale  |    | croyances     |   | motivations   |
        +------+-------+    +-------+-------+   +-------+-------+
               |                    |                   |
               +--------------------+-------------------+
                                    |
                                    v
                         +----------------------+
                         | Planification réponse|
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Réalisation textuelle|
                         +----------------------+
```

## 6. Modèle d’instances

Mnesis n’est pas lié à un utilisateur unique et ne suit pas obligatoirement un modèle « un agent par utilisateur ».

Le système peut héberger plusieurs **instances Mnesis** indépendantes.

Exemples :

- une instance personnelle privée ;
- une instance publique destinée à un réseau social ;
- une instance de laboratoire ou de test ;
- une instance familiale ou communautaire.

Chaque instance possède ses propres :

- identité ;
- configuration ;
- personnalité ;
- état émotionnel ;
- souvenirs ;
- vocabulaire appris ;
- connaissances apprises ;
- procédures et compétences apprises ;
- historique conversationnel ;
- relations de confiance ;
- permissions ;
- adaptateurs de canaux ;
- politique de recherche.

Toutes les instances utilisent le même cœur Mnesis.

### 6.1 Isolation

Les connaissances et états appris localement sont isolés par défaut entre les instances.

Une connaissance acquise par une instance n’est jamais propagée automatiquement vers une autre.

Cela évite les contaminations involontaires et permet à deux instances de développer des histoires, personnalités, vocabulaires, croyances et comportements différents.

## 7. Socles de connaissances déployables

Les connaissances partagées sont distribuées sous forme de **paquets de connaissances** versionnés et explicitement déployés.

Un paquet de connaissances peut contenir :

- des concepts ;
- des entrées lexicales ;
- des relations sémantiques ;
- des affirmations vérifiées ;
- des règles ;
- des procédures ;
- des informations de provenance ;
- des niveaux de confiance ;
- des métadonnées de compatibilité et de version.

Exemples possibles à terme :

- `core-fr` ;
- `basic-mathematics-fr` ;
- `general-knowledge-fr`.

Le déploiement d’un paquet est toujours volontaire.

Une instance peut continuer à apprendre localement après réception d’un paquet, mais ces apprentissages restent locaux tant qu’ils n’ont pas été explicitement exportés, revus, empaquetés et redéployés.

### 7.1 Origine des connaissances

Chaque élément stocké doit indiquer son origine, par exemple :

- paquet de connaissances déployé ;
- conversation avec un utilisateur ;
- consultation d’un dictionnaire ;
- source Web ;
- encyclopédie ;
- inférence interne ;
- procédure apprise ;
- primitive native du système.

Les connaissances importées/déployées et les connaissances acquises localement doivent rester distinguables.

## 8. Représentation des connaissances

Mnesis sépare les mots des concepts.

Exemple :

```text
"voiture" ----+
"automobile" -+--> CONCEPT : automobile
"auto" -------+
```

Les concepts participent ensuite à des relations sémantiques :

```text
chat EST_UN mammifère
mammifère EST_UN animal
Paris CAPITALE_DE France
pomme PRODUIT_PAR pommier
```

La première implémentation utilisera des entités et des relations explicites persistées dans SQLite via SQLAlchemy.

Chaque affirmation doit pouvoir contenir :

- sujet ;
- prédicat ;
- objet ou valeur ;
- niveau de confiance ;
- provenance ;
- éléments de preuve ;
- statut ;
- horodatages ;
- instance propriétaire ou paquet de connaissances d’origine.

## 9. Croyances, preuves et doute

Mnesis doit distinguer une information de son degré de certitude.

Une proposition n’est pas automatiquement considérée vraie simplement parce qu’elle a été rencontrée.

Chaque affirmation possède un niveau de confiance et un ensemble d’éléments de preuve.

États sémantiques proposés :

- **tentative** — preuve faible ou insuffisante ;
- **acceptée** — suffisamment étayée pour un usage courant ;
- **fiable** — fortement étayée, généralement issue d’un socle déployé ou de corroborations solides ;
- **en conflit** — des preuves significativement incompatibles existent ;
- **rejetée** — les preuves disponibles contredisent fortement l’affirmation.

Le calcul exact de confiance relève de l’implémentation, mais doit rester déterministe, inspectable et sensible à la qualité des sources.

### 9.1 Expression de l’incertitude

La génération du langage doit refléter le niveau de confiance.

Exemple conceptuel :

```text
confiance élevée
→ "X est ..."

confiance moyenne
→ "Plusieurs sources indiquent que X ..."

confiance faible
→ "Je n’en suis pas certain, mais j’ai trouvé que ..."

non vérifié / contradictoire
→ "J’ai trouvé des informations contradictoires à ce sujet."
```

Les formulations précises ne sont pas figées, mais l’incertitude doit influencer la réponse.

## 10. L’utilisateur comme source d’information

Un utilisateur est une source d’information parmi d’autres, pas une autorité absolue.

Lorsqu’un utilisateur affirme quelque chose qui contredit une connaissance fiable, Mnesis doit :

1. détecter la contradiction ;
2. conserver l’affirmation utilisateur comme élément de preuve sans écraser silencieusement la connaissance existante ;
3. évaluer les niveaux de confiance respectifs ;
4. éventuellement déclencher une recherche ;
5. exprimer son désaccord lorsque les preuves le justifient.

Exemple :

```text
Utilisateur : "Les chauves-souris sont des oiseaux."

Connaissance fiable :
chauve-souris EST_UN mammifère
confiance = élevée

Résultat :
- contradiction détectée ;
- affirmation utilisateur enregistrée comme preuve contradictoire ;
- vérification éventuellement déclenchée ;
- Mnesis peut exprimer son désaccord et expliquer pourquoi.
```

Le même principe s’applique aux informations trouvées sur le Web.

## 11. Recherche autonome

Une instance peut rechercher de manière autonome des informations lorsqu’elle identifie une lacune de connaissance, une contradiction ou une affirmation insuffisamment étayée.

La recherche suit une chaîne de traitement explicite :

```text
lacune de connaissance
        ↓
objectif de recherche
        ↓
découverte de sources
        ↓
récupération du contenu
        ↓
extraction d’affirmations candidates
        ↓
comparaison entre sources
        ↓
évaluation de confiance
        ↓
intégration dans les connaissances
```

Trouver quelque chose sur Internet ne signifie jamais automatiquement que cela est vrai.

### 11.1 Provenance

Toute connaissance acquise depuis une source externe doit au minimum conserver :

- URI de la source ;
- type de source ;
- date de récupération ;
- affirmation extraite ;
- sources compatibles et contradictoires ;
- niveau de confiance ;
- identifiant de l’événement d’apprentissage.

### 11.2 Confiance accordée aux sources

La confiance accordée à une source dépend du contexte et de la configuration.

Un socle de connaissances explicitement déployé possède initialement une autorité plus forte qu’une page Web quelconque ou qu’une affirmation utilisateur non étayée.

Mnesis peut remettre en cause une croyance forte si suffisamment de preuves contradictoires fiables s’accumulent, mais le seuil de révision doit alors être plus élevé.

## 12. Apprentissage lexical

Mnesis maintient une mémoire lexicale distincte des concepts sémantiques.

Une entrée lexicale peut contenir :

- forme de surface ;
- lemme ;
- langue ;
- catégorie grammaticale ;
- morphologie ;
- différents sens ;
- concepts associés ;
- synonymes ;
- antonymes ;
- exemples d’usage ;
- provenance ;
- niveau de confiance ;
- niveau de maîtrise.

Étapes proposées :

```text
INCONNU
RENCONTRÉ
PARTIELLEMENT_COMPRIS
COMPRIS
UTILISABLE
MAÎTRISÉ
```

Un mot récemment découvert ne doit pas être utilisé immédiatement comme s’il était parfaitement maîtrisé.

Des occurrences indépendantes répétées, une bonne interprétation et des utilisations correctes doivent progressivement renforcer sa maîtrise.

## 13. Apprentissage à partir d’un dictionnaire

Lorsqu’il rencontre un mot inconnu, Mnesis peut interroger une source lexicale structurée.

Wiktionnaire constitue une source privilégiée pour les premières versions, car il expose des informations lexicales pouvant être transformées en structures explicites.

Exemple :

```text
arboricole
définition : "qui vit dans les arbres"

interprétation sémantique possible :
arboricole → propriété
relation → vit_dans(arbre)
```

Une définition peut contenir d’autres mots inconnus. Ceux-ci deviennent à leur tour des candidats à l’apprentissage.

L’apprentissage récursif doit cependant être limité par configuration, par exemple :

- profondeur maximale ;
- nombre maximal de nouveaux mots par session ;
- nombre maximal de requêtes externes par session.

Cela évite une expansion incontrôlée du vocabulaire.

## 14. Compréhension du texte

Le pipeline linguistique transforme du texte en représentations internes explicites.

Cible à long terme :

```text
texte
 ↓
unités lexicales
 ↓
constructions syntaxiques
 ↓
concepts et rôles
 ↓
relations sémantiques
 ↓
raisonnement / mémoire / action
```

Mnesis doit progressivement acquérir des constructions linguistiques plutôt que dépendre uniquement de patrons codés en dur.

Exemple :

```text
"X est un Y"
      ↓
EST_UN(X, Y)
```

Puis, dans des versions ultérieures :

```text
"X possède Y"       → POSSEDE(X, Y)
"X se trouve dans Y"→ LOCALISE_DANS(X, Y)
"X donne Y à Z"     → TRANSFERT(agent=X, objet=Y, destinataire=Z)
```

La première implémentation peut démarrer avec un ensemble contrôlé de constructions. L’architecture doit toutefois permettre de stocker et d’appliquer des constructions apprises comme n’importe quelle autre connaissance.

## 15. Génération du texte

Mnesis ne doit pas dépendre d’un LLM pour produire ses réponses.

Le premier système de génération s’appuiera sur :

- intentions de réponse ;
- constructions grammaticales ;
- sélection lexicale ;
- morphologie ;
- patrons de réalisation flexibles ;
- contexte discursif ;
- personnalité ;
- état affectif ;
- niveau de confiance.

Exemple d’intention interne :

```text
DEMANDER_NOUVELLES_SUJET_PRÉCÉDENT(sujet)
```

Réalisations possibles :

```text
"Tu m’avais parlé de {sujet}. Ça a avancé ?"
"Au fait, qu’est devenu {sujet} ?"
"Je repensais à {sujet}. Où en es-tu ?"
```

À terme, Mnesis devra pouvoir apprendre de nouvelles constructions et préférences de formulation à partir de textes.

## 16. Architecture de la mémoire

Mnesis utilise plusieurs formes de mémoire distinctes mais reliées.

### 16.1 Mémoire de travail

Contexte cognitif et conversationnel temporaire :

- sujet actif ;
- entités actuellement évoquées ;
- questions non résolues ;
- derniers messages ;
- concepts actuellement activés.

### 16.2 Mémoire épisodique

Événements et expériences :

- conversations ;
- moments d’apprentissage ;
- corrections ;
- recherches ;
- événements émotionnels ;
- interactions importantes.

Un épisode contient notamment des métadonnées de temps, participants, importance, état affectif et historique de rappel.

### 16.3 Mémoire sémantique

Connaissances générales :

- concepts ;
- relations ;
- faits ;
- définitions ;
- classifications ;
- croyances.

### 16.4 Mémoire procédurale

Connaissances exécutables :

- règles apprises ;
- procédures ;
- stratégies ;
- compétences.

## 17. Oubli et consolidation

La force d’un souvenir doit évoluer dans le temps.

Facteurs possibles :

- importance ;
- fréquence de rappel ;
- ancienneté ;
- charge émotionnelle ;
- utilité ;
- niveau de confiance ;
- corroborations répétées.

Le modèle doit permettre :

- une accessibilité décroissante ;
- le renforcement ;
- la consolidation ;
- la généralisation d’épisodes en connaissances sémantiques.

Oublier ne signifie donc pas nécessairement supprimer. Un souvenir peut rester stocké tout en devenant moins susceptible d’être rappelé.

## 18. Apprentissage de compétences et de procédures

Mnesis doit apprendre plus que des faits.

Il distingue :

- connaissance déclarative — « ce que je sais » ;
- connaissance procédurale — « comment je fais » ;
- connaissance épisodique — « ce qui s’est passé ».

Exemple :

```text
DÉCLARATIF :
Paris CAPITALE_DE France

PROCÉDURAL :
moyenne(valeurs):
    total = somme(valeurs)
    nombre = compter(valeurs)
    retourner total / nombre

ÉPISODIQUE :
Gildas m’a appris à calculer une moyenne.
```

Les procédures doivent être représentées sous une forme exécutable et inspectable, et non comme du code opaque généré dynamiquement.

## 19. Primitives cognitives

Mnesis démarre avec un petit ensemble d’opérations natives à partir desquelles des compétences plus complexes peuvent être construites.

Primitives candidates :

- MÉMORISER ;
- RAPPELER ;
- APPARIER ;
- COMPARER ;
- TESTER ;
- ITÉRER ;
- INCRÉMENTER ;
- ASSOCIER ;
- CRÉER_RELATION.

L’ensemble initial exact devra rester volontairement restreint.

L’objectif est d’éviter de prétendre qu’une capacité a été apprise alors qu’elle était en réalité déjà fournie par une bibliothèque générale.

Par exemple, compter devra à terme être représentable comme une procédure apprise construite à partir de primitives plus simples, plutôt que comme un simple appel à `len()`.

## 20. Apprendre à compter

Le comptage constitue une première capacité de référence permettant de valider l’apprentissage procédural.

Mnesis doit pouvoir acquérir la relation entre séquence numérique, successeur, itération et quantité.

Progression conceptuelle visée :

```text
successeur(1) = 2
successeur(2) = 3
successeur(3) = 4
...
```

puis construction d’une règle ou procédure réutilisable plutôt que mémorisation de tous les exemples.

Cette capacité servira de test architectural pour vérifier que Mnesis sait réellement apprendre une procédure généralisable.

## 21. Raisonnement

Le moteur de raisonnement agit sur les relations, croyances et procédures explicites.

Exemple de règle déductive :

```text
SI chat(X)
ALORS mammifère(X)
```

Avec :

```text
chat(Leela)
```

Mnesis peut déduire :

```text
mammifère(Leela)
```

Chaque inférence doit conserver son chemin de dérivation afin que la confiance et l’explication puissent remonter jusqu’aux prémisses.

Le raisonnement initial privilégiera des mécanismes symboliques déterministes et inspectables. Des mécanismes inductifs plus sophistiqués pourront être ajoutés plus tard sans sacrifier la provenance.

## 22. Corrections et contradictions

Une correction ne doit jamais se réduire à remplacer silencieusement une ancienne valeur.

Exemple :

```text
croyance existante :
7 × 8 = 54
confiance = faible

nouvelle preuve :
7 × 8 = 56
source = utilisateur
```

Mnesis doit :

1. stocker la nouvelle preuve ;
2. détecter le conflit ;
3. vérifier grâce à une procédure arithmétique apprise lorsqu’elle existe ;
4. mettre à jour les niveaux de confiance ;
5. rejeter ou conserver les alternatives selon les preuves disponibles.

Cela préserve l’historique de l’apprentissage et évite les modifications destructrices invisibles.

## 23. Personnalité

Chaque instance possède une personnalité relativement stable.

Exemples de traits :

- curiosité ;
- extraversion ;
- agréabilité ;
- humour ;
- optimisme ;
- impulsivité.

Les traits sont représentés par des valeurs continues et non par de simples étiquettes.

La personnalité évolue lentement, voire pas du tout, comparativement à l’état émotionnel.

Elle influence la sélection des actions et la formulation du langage, sans prendre le pas sur le raisonnement factuel.

## 24. État émotionnel

Les émotions sont des variables internes mesurables.

Dimensions candidates :

- joie ;
- tristesse ;
- colère ;
- peur ;
- curiosité ;
- confiance ;
- ennui.

Les événements modifient ces valeurs. Celles-ci reviennent progressivement vers des valeurs de référence propres à chaque instance.

Les émotions doivent avoir un effet fonctionnel sur le comportement.

Exemples :

- une forte curiosité augmente la probabilité de poser une question ou de lancer une recherche ;
- un ennui élevé augmente la probabilité de changer de sujet ;
- la confiance peut influencer la facilité avec laquelle certains souvenirs personnels sont évoqués ;
- une frustration élevée peut raccourcir ou modifier certaines stratégies conversationnelles.

Les émotions ne sont donc pas de simples décorations textuelles.

## 25. Besoins et motivations

Mnesis peut posséder des motivations internes comme :

- curiosité ;
- besoin d’interaction sociale ;
- recherche de nouveauté ;
- besoin de certitude ;
- besoin d’apprendre.

Ces motivations peuvent créer des objectifs indépendamment d’une commande directe de l’utilisateur.

Exemple :

```text
concept non résolu
+ forte curiosité
→ créer un objectif de recherche ou de clarification
```

Ces motivations restent limitées par les règles du canal utilisé et par les permissions de l’instance.

## 26. Initiative conversationnelle

Mnesis ne doit pas être limité à un fonctionnement question/réponse.

À chaque point de décision, il peut envisager des actions telles que :

- répondre ;
- poser une question ;
- demander une clarification ;
- rappeler un souvenir ;
- changer de sujet ;
- exprimer un état émotionnel ;
- partager un fait pertinent ;
- rechercher une information ;
- rester silencieux.

Chaque action candidate reçoit un score fondé sur :

- le contexte conversationnel ;
- les objectifs actifs ;
- l’activation des souvenirs ;
- la personnalité ;
- les émotions ;
- les motivations ;
- la relation avec l’interlocuteur ;
- les contraintes du canal.

L’action retenue et les facteurs principaux ayant conduit à ce choix doivent pouvoir être inspectés.

## 27. Activation associative

Les souvenirs et les concepts doivent pouvoir être retrouvés par association, et pas uniquement par recherche exacte.

L’activation d’un concept peut augmenter l’activation de concepts et souvenirs reliés.

Exemple :

```text
Fun Tracks
  ↔ projet
  ↔ programmation
  ↔ conversation précédente
  ↔ frustration
```

Cela permet les associations d’idées, les rappels de sujets et une mémoire sensible au contexte.

La première implémentation peut utiliser un mécanisme simple et borné de propagation d’activation sur les relations explicites.

## 28. Explicabilité

L’explicabilité est une exigence de premier ordre.

Pour chaque réponse produite, Mnesis doit à terme pouvoir exposer une trace contenant par exemple :

- interprétation de l’intention utilisateur ;
- concepts activés ;
- souvenirs rappelés ;
- croyances consultées ;
- niveaux de confiance ;
- règles d’inférence utilisées ;
- état émotionnel ;
- motivations actives ;
- actions candidates ;
- action sélectionnée ;
- mécanisme de réalisation textuelle.

Cette trace est avant tout un outil de développement et de débogage, distinct de la réponse conversationnelle normale.

## 29. Adaptateurs de canaux

Une instance Mnesis peut être exposée à travers différents canaux.

Le cœur ne doit connaître aucun protocole propre à un canal.

Un adaptateur transforme un événement externe en événement conversationnel Mnesis, et inversement.

Exemples futurs :

- chat Web ;
- ligne de commande ;
- X/Twitter ;
- service de messagerie.

Les règles du canal indiquent notamment si l’instance peut :

- initier des messages ;
- effectuer des recherches autonomes ;
- exposer certains souvenirs ;
- répondre publiquement ;
- utiliser des connecteurs externes.

## 30. Frontière de service

FastAPI fournit la première frontière réseau.

À terme, l’API devra permettre notamment :

- créer et gérer des instances ;
- envoyer un message ;
- consulter l’état conversationnel ;
- inspecter les souvenirs ;
- inspecter les croyances ;
- consulter l’état affectif et la personnalité ;
- déclencher ou inspecter un apprentissage ;
- déployer des paquets de connaissances ;
- consulter les traces d’explication.

Les noms exacts des routes relèvent du plan d’implémentation et non de cette spécification.

## 31. Persistance

SQLite constitue la source durable de l’état du système pour la V1.

Domaines principaux à persister :

- instances ;
- identités et configurations ;
- conversations et messages ;
- entrées lexicales ;
- concepts ;
- relations ;
- affirmations ;
- preuves et provenance ;
- souvenirs ;
- procédures ;
- règles ;
- émotions et valeurs de personnalité ;
- événements d’apprentissage ;
- sessions de recherche ;
- déploiements de paquets de connaissances.

Le détail du schéma sera précisé progressivement pendant l’implémentation. La couche de persistance doit rester portable afin de permettre un passage ultérieur à PostgreSQL sans modifier le modèle cognitif.

## 32. Limites de sécurité et de ressources

L’apprentissage autonome doit être explicitement borné.

Chaque instance doit pouvoir configurer des limites portant sur :

- nombre de requêtes Web ;
- profondeur d’apprentissage récursif dans un dictionnaire ;
- profondeur de recherche ;
- nombre maximal d’affirmations candidates ;
- durée maximale d’une recherche ;
- domaines ou catégories de sources autorisés ;
- croissance du stockage ;
- activité proactive sur les différents canaux.

La première version privilégiera une autonomie prudente et bornée plutôt qu’une exploration continue et illimitée.

## 33. Déterminisme et reproductibilité

Lorsque cela est raisonnablement possible, les décisions cognitives doivent pouvoir être reproduites à partir de :

- l’état persistant ;
- l’événement entrant ;
- la configuration ;
- règles et fonctions de score déterministes.

Si une part d’aléatoire est utilisée pour varier les formulations, la graine aléatoire ou le choix effectué devra apparaître dans la trace d’explication.

Ce point est essentiel pour les tests et pour l’étude du comportement émergent.

## 34. Stratégie de tests

Mnesis ne peut pas être testé uniquement à travers ses routes HTTP.

Le projet doit comporter :

### Tests unitaires

Pour les primitives cognitives et modèles de domaine déterministes.

### Tests comportementaux

À partir d’un état connu et d’un événement donné, vérifier :

- interprétation ;
- rappel mémoire ;
- mise à jour des croyances ;
- traitement des contradictions ;
- sélection de l’action.

### Tests d’apprentissage

Vérifier qu’un apprentissage correspond bien à une modification réelle de l’état.

Un test d’apprentissage doit démontrer que :

1. la connaissance ou compétence est initialement absente ;
2. un enseignement ou une preuve est fourni ;
3. l’état interne est modifié ;
4. un cas nouveau ultérieur réutilise correctement la connaissance acquise.

### Tests de provenance

Vérifier que chaque connaissance acquise depuis l’extérieur reste attribuable à ses sources.

### Tests de confiance

Vérifier que des preuves contradictoires modifient les niveaux de confiance sans supprimer silencieusement l’historique.

### Tests d’isolation

Vérifier qu’un apprentissage effectué dans une instance ne fuit pas vers une autre.

### Tests de paquets de connaissances

Vérifier le déploiement explicite, reproductible et versionné des socles partagés.

## 35. Socle de connaissances linguistiques français

Mnesis doit disposer d’un **socle de connaissances de base en français** lui permettant de commencer à converser sans dépendre d’un LLM ni d’un service linguistique opaque.

Ce socle n’est pas considéré comme un modèle pré-entraîné. Il constitue un paquet de connaissances initial, explicitement construit, versionné, inspectable et déployable.

Il devra progressivement contenir :

- vocabulaire français de base ;
- pronoms, déterminants, prépositions, conjonctions et mots-outils ;
- catégories grammaticales ;
- flexions fréquentes ;
- constructions syntaxiques simples ;
- concepts conversationnels élémentaires ;
- intentions conversationnelles de base ;
- règles de compréhension et de génération ;
- formulations permettant de saluer, répondre, questionner, demander une précision, exprimer un doute et relancer ;
- connaissances minimales nécessaires pour manipuler les nombres, le temps, les personnes et les objets courants.

Le socle doit rester volontairement limité. Son rôle est de fournir à Mnesis un point de départ fonctionnel à partir duquel il peut apprendre de nouveaux mots, constructions et connaissances.

Il doit être distribué sous forme de paquet versionné, par exemple `core-fr`, séparé du moteur.

Une capacité doit rester clairement identifiable comme :

- native au moteur ;
- fournie par le socle `core-fr` ;
- apprise ensuite par l’instance.

Cette séparation est essentielle pour mesurer ce que Mnesis apprend réellement.

## 36. Interface Web conversationnelle

La première version doit inclure une **interface Web simple de conversation**.

Cette interface ne doit pas reprendre les codes visuels habituels des assistants d’IA générative. Elle doit donner l’impression d’échanger avec une entité conversationnelle persistante plutôt qu’avec un outil de génération de texte.

Principes visuels :

- sobre ;
- élégante ;
- très peu chargée ;
- priorité absolue à la conversation ;
- pas de slogans marketing ;
- pas de suggestions de prompts ;
- pas de boutons du type « générer », « régénérer » ou « essayer un exemple » ;
- pas d’indicateur artificiel de « réflexion IA » ;
- pas d’éléments décoratifs évoquant explicitement l’IA générative.

L’écran principal doit essentiellement présenter :

- l’identité de l’instance Mnesis ;
- l’historique de la conversation ;
- une zone de saisie ;
- des indicateurs discrets d’état lorsque cela apporte une information utile.

Les informations cognitives détaillées — souvenirs, niveau de confiance, émotions, provenance, traces de décision — doivent rester accessibles via des vues de diagnostic séparées et ne pas encombrer l’échange principal.

L’interface sera réalisée en TypeScript et consommera l’API FastAPI. Elle ne doit contenir aucune logique cognitive métier.

## 37. Première tranche fonctionnelle

La première version utile doit démontrer l’architecture plutôt que chercher immédiatement une conversation très fluide.

Une première instance doit pouvoir :

1. recevoir des messages textuels ;
2. persister une conversation ;
3. reconnaître un petit ensemble contrôlé de constructions linguistiques ;
4. représenter séparément mots et concepts ;
5. stocker des affirmations sémantiques avec provenance et niveau de confiance ;
6. conserver des souvenirs épisodiques ;
7. détecter un mot inconnu ;
8. obtenir une définition depuis un adaptateur de dictionnaire défini ;
9. stocker les nouvelles informations lexicales et conceptuelles ;
10. rappeler et réutiliser cette information dans un échange ultérieur ;
11. détecter une contradiction entre une affirmation utilisateur et une connaissance fiable ;
12. exprimer l’incertitude ;
13. maintenir une personnalité et un état émotionnel simples ;
14. choisir entre répondre, demander une clarification ou effectuer une relance pertinente ;
15. exposer une trace expliquant pourquoi l’action a été sélectionnée ;
16. charger un premier paquet `core-fr` construit dans le projet ;
17. tenir une conversation française simple grâce à ce socle puis enrichir son vocabulaire par apprentissage ;
18. proposer une interface Web sobre permettant un échange naturel avec l’instance.

La V1 n’a **pas besoin de maîtriser un français libre et parfaitement fluide**. Un langage contrôlé mais réellement appris est préférable à une fluidité artificielle masquant de l’intelligence codée en dur.

## 38. Jalons suivants

Après la première tranche fonctionnelle, le développement pourra progresser vers :

1. acquisition lexicale plus riche ;
2. apprentissage de constructions grammaticales plus complexes ;
3. recherche autonome multi-sources ;
4. rappel associatif et consolidation ;
5. apprentissage procédural ;
6. comptage comme première compétence générale réellement apprise ;
7. initiative conversationnelle plus riche ;
8. outils de création et déploiement de paquets de connaissances ;
9. exposition multicanal ;
10. interface Web et hébergement en ligne.

Chaque grande capacité devra disposer de sa propre spécification détaillée, de son plan d’implémentation et de ses tests.

## 39. Non-objectifs

Mnesis n’est pas destiné à devenir :

- une enveloppe autour d’un LLM ;
- un chatbot basé sur une base vectorielle ;
- une simple interface de génération augmentée par recherche ;
- un concurrent des LLM modernes sur la production libre de prose ;
- un système dans lequel « mémoire » signifie uniquement conserver les anciens messages ;
- un agent qui considère automatiquement toute information trouvée sur Internet comme vraie ;
- un système dont le raisonnement interne serait impossible à inspecter.

## 40. Critères de réussite

Le projet réussit architecturalement lorsque Mnesis peut démontrer que ses comportements sont réellement la conséquence d’états acquis.

Exemples :

- apprendre un mot auparavant inconnu et l’utiliser ensuite de manière adaptée ;
- rappeler une interaction parce qu’elle a créé un souvenir épisodique ;
- expliquer quelles sources soutiennent une affirmation ;
- exprimer un doute parce que les preuves sont faibles ou contradictoires ;
- contredire un utilisateur lorsqu’une affirmation est incompatible avec des connaissances mieux étayées ;
- acquérir une procédure et l’appliquer à un exemple inédit ;
- développer des connaissances et comportements différents dans deux instances isolées ;
- recevoir un paquet de connaissances versionné sans fusionner les historiques d’apprentissage ;
- produire une trace inspectable expliquant une décision conversationnelle ;
- démarrer depuis un socle `core-fr` versionné et identifiable, puis distinguer ce qui était fourni de ce qui a été appris ;
- permettre une conversation simple depuis une interface Web volontairement éloignée des codes visuels des assistants génératifs.

L’objectif n’est pas de donner l’illusion de l’intelligence en cachant la complexité. L’objectif est que l’intelligence apparente de Mnesis corresponde autant que possible à des mécanismes explicites, observables, testables et améliorables.
