# Mnesis — Cognitive Conversational Agent Design Specification

**Status:** Draft for review  
**Date:** 2026-09-27  
**Project:** Mnesis  
**Repository:** Karlos-fr/mnesis

## 1. Purpose

Mnesis is an experimental, non-LLM cognitive conversational agent that progressively learns language, knowledge, skills, concepts, and conversational behavior from text and interaction.

The project is not intended to imitate an LLM with handcrafted prompts. Its purpose is to explore an explicit and inspectable cognitive architecture in which knowledge, memories, learned language, reasoning, uncertainty, emotions, personality, and behavior are represented directly and can be examined, tested, and explained.

A core design principle is:

> If Mnesis claims to have learned, remembered, inferred, forgotten, doubted, or decided something, the internal state must contain an inspectable representation explaining why.

## 2. Product Vision

Mnesis should eventually behave as a persistent conversational entity whose abilities and knowledge are shaped by its history.

It must be able to:

- converse through text without relying on a large language model;
- learn new words and linguistic constructions;
- learn facts and concepts from conversations and text sources;
- independently seek information on the Internet when it identifies a knowledge gap;
- preserve source provenance and confidence for learned claims;
- doubt uncertain information and communicate that uncertainty;
- detect contradictions between claims;
- treat users as information sources rather than unquestionable authorities;
- protect high-confidence deployed knowledge from casual contradictory input;
- learn rules and procedures rather than only memorizing answers;
- acquire skills such as counting from simpler cognitive primitives;
- retain episodic memories of interactions and semantic knowledge derived from them;
- forget, reinforce, and consolidate information over time;
- maintain measurable emotions that influence behavior;
- maintain a relatively stable personality;
- act from internal motivations such as curiosity;
- initiate or resume topics without waiting for a direct question;
- explain why it produced a response or holds a belief.

## 3. Initial Scope

The first major development phase is deliberately **text-only**.

### Included

- textual conversation;
- lexical learning;
- semantic knowledge acquisition;
- rule-based and procedural learning;
- episodic and semantic memory;
- uncertainty and belief management;
- autonomous textual web research;
- personality and emotional state;
- conversational initiative;
- multiple isolated Mnesis instances;
- deployable shared knowledge packs;
- HTTP API for future online use.

### Explicitly deferred

- speech recognition;
- speech synthesis;
- vision;
- robotics;
- embodied physical interaction;
- autonomous computer control;
- unrestricted natural-language understanding of arbitrary web pages;
- LLM-based fallback generation.

These may be added in later phases without changing the core cognitive model.

## 4. Technology Direction

The initial implementation uses:

- **Python 3.13+** for the cognitive engine;
- **FastAPI** for the service/API boundary;
- **PostgreSQL** for durable storage;
- **TypeScript** for a future browser client.

The cognitive engine must not depend on the web interface. It should be usable from tests, a CLI, the HTTP API, or future adapters.

The first implementation should prefer simple relational persistence and explicit domain models over introducing a dedicated graph database. Knowledge is graph-shaped conceptually, but PostgreSQL is sufficient for the first version and makes transactions, provenance, testing, and deployment simpler.

## 5. High-Level Architecture

```text
                     External text sources
                dictionary / web / encyclopedia
                            |
                            v
+-------------+      +--------------------+
| User /      |----->| Language Pipeline  |
| Channel     |      +---------+----------+
+-------------+                |
                               v
                     +--------------------+
                     | Cognitive Engine   |
                     |                    |
                     | interpretation     |
                     | reasoning          |
                     | goals / drives     |
                     | action selection   |
                     +----+----+----+------+
                          |    |    |
             +------------+    |    +-------------+
             v                 v                  v
      +-------------+   +-------------+    +-------------+
      | Memory      |   | Knowledge   |    | Affect      |
      | episodic    |   | concepts    |    | emotions    |
      | working     |   | relations   |    | personality |
      | procedural  |   | beliefs     |    | drives      |
      +------+------+   +------+------+    +------+------+
             |                 |                  |
             +-----------------+------------------+
                               |
                               v
                     +--------------------+
                     | Response Planning  |
                     +---------+----------+
                               |
                               v
                     +--------------------+
                     | Surface Realizer   |
                     +--------------------+
```

## 6. Instance Model

Mnesis is not tied to one user and does not use a mandatory one-agent-per-user model.

The runtime can host multiple independent **Mnesis instances**.

Examples:

- a private personal instance;
- a public social-network instance;
- a laboratory/testing instance;
- a family or community instance.

Every instance has its own:

- identity;
- configuration;
- personality;
- emotional state;
- memories;
- learned vocabulary;
- learned knowledge;
- learned procedures and skills;
- conversation history;
- trust relationships;
- permissions;
- channel adapters;
- research policy.

All instances execute the same Mnesis core.

### 6.1 Isolation

Instance-local learned state is isolated by default. Knowledge learned by one instance does not automatically propagate to another.

This prevents accidental contamination and allows two instances to develop different histories, personalities, vocabularies, beliefs, and behavior.

## 7. Knowledge Packs

Shared knowledge is distributed through explicit, versioned **Knowledge Packs**.

A knowledge pack may contain:

- concepts;
- lexical entries;
- semantic relations;
- verified claims;
- rules;
- procedures;
- source provenance;
- confidence metadata;
- compatibility/version metadata.

Example packs could eventually include:

- `core-fr`;
- `basic-mathematics-fr`;
- `general-knowledge-fr`.

Knowledge pack deployment is always intentional.

An instance may learn additional knowledge after receiving a pack, but that learning remains local until explicitly exported, reviewed, packaged, and deployed elsewhere.

### 7.1 Knowledge Origin

Every stored item must identify its origin, for example:

- deployed knowledge pack;
- user conversation;
- dictionary lookup;
- web source;
- encyclopedia;
- internal inference;
- learned procedure;
- system primitive.

Imported/deployed knowledge and locally learned knowledge must remain distinguishable.

## 8. Knowledge Representation

Mnesis separates words from concepts.

For example:

```text
"voiture" ----+
"automobile" -+--> CONCEPT: automobile
"auto" -------+
```

Concepts participate in semantic relations:

```text
cat IS_A mammal
mammal IS_A animal
Paris CAPITAL_OF France
apple PRODUCED_BY apple_tree
```

The initial implementation uses explicit entities and relations stored in PostgreSQL.

Each claim must support:

- subject;
- predicate;
- object/value;
- confidence;
- provenance;
- evidence;
- status;
- timestamps;
- owning instance or knowledge pack.

## 9. Beliefs, Evidence, and Doubt

Mnesis must distinguish between information and certainty.

A proposition is not automatically considered true simply because it was encountered.

Each claim has a confidence value and evidence set.

Suggested semantic states are:

- **tentative** — weak or insufficient evidence;
- **accepted** — sufficiently supported for ordinary use;
- **trusted** — strongly supported, usually from trusted deployed knowledge or strong corroboration;
- **conflicted** — materially incompatible evidence exists;
- **rejected** — evidence strongly contradicts the claim.

The exact confidence calculation is implementation detail, but it must be deterministic, inspectable, and source-aware.

### 9.1 Expressing uncertainty

Language generation must reflect confidence.

Conceptually:

```text
high confidence
→ "X is ..."

moderate confidence
→ "Several sources indicate that X ..."

low confidence
→ "I'm not certain, but I found ..."

unverified/conflicted
→ "I found conflicting information about this."
```

The linguistic form is not fixed to those templates, but confidence must influence the response.

## 10. Users as Sources

A user is a source of information, not an absolute authority.

If a user states something that conflicts with trusted knowledge, Mnesis should:

1. detect the contradiction;
2. preserve the user statement as evidence rather than silently overwrite trusted knowledge;
3. evaluate the relative confidence of the claims;
4. optionally trigger research;
5. communicate disagreement when warranted.

Example:

```text
User: "Bats are birds."

Trusted knowledge:
bat IS_A mammal
confidence = high

Result:
- contradiction detected
- user claim recorded as conflicting evidence
- verification may be triggered
- Mnesis can disagree and explain why
```

The same principle applies to information obtained from web pages.

## 11. Autonomous Research

An instance may autonomously search for information when it identifies a knowledge gap, contradiction, or insufficiently supported claim.

Research follows a pipeline:

```text
knowledge gap
    ↓
research goal
    ↓
source discovery
    ↓
source retrieval
    ↓
candidate fact extraction
    ↓
cross-source comparison
    ↓
confidence assignment
    ↓
knowledge integration
```

Research must never equate “found on the Internet” with “true.”

### 11.1 Provenance

At minimum, externally learned knowledge records:

- source URI;
- source type;
- retrieval time;
- extracted statement;
- supporting and contradicting sources;
- confidence;
- learning event identifier.

### 11.2 Source trust

Source trust is contextual and configurable.

A deployed core knowledge pack starts with stronger authority than an arbitrary web page or unsupported user assertion.

Mnesis can revise even strong beliefs when sufficient evidence accumulates, but the threshold is intentionally higher.

## 12. Lexical Learning

Mnesis maintains a lexical memory separate from semantic concepts.

A lexical entry can include:

- surface form;
- lemma;
- language;
- part of speech;
- morphology;
- meanings;
- associated concepts;
- synonyms;
- antonyms;
- usage examples;
- source provenance;
- confidence;
- learning stage.

Suggested learning stages:

```text
UNKNOWN
SEEN
PARTIALLY_UNDERSTOOD
UNDERSTOOD
USABLE
MASTERED
```

A newly discovered word should not automatically become a word Mnesis confidently uses in conversation.

Repeated independent evidence, successful interpretation, and correct usage can reinforce mastery.

## 13. Dictionary Learning

When Mnesis encounters an unknown word it may query a structured dictionary source.

Wiktionary is a preferred early source because it exposes lexical information that can be transformed into explicit lexical and semantic structures.

Example:

```text
arboricole
definition: "qui vit dans les arbres"

possible semantic interpretation:
arboricole → property
property relation → lives_in(tree)
```

Definitions can contain unknown words. These become learning candidates.

Recursive learning must be bounded by configuration, for example:

- maximum recursion depth;
- maximum new words per learning session;
- maximum external requests per learning session.

This avoids uncontrolled vocabulary expansion.

## 14. Text Understanding

The language pipeline transforms text into explicit internal structures.

The long-term target is:

```text
text
 ↓
tokens / lexical forms
 ↓
syntactic constructions
 ↓
concepts and roles
 ↓
semantic relations
 ↓
reasoning / memory / action
```

Mnesis should progressively acquire linguistic constructions rather than relying entirely on hard-coded sentence templates.

Example:

```text
"X is a Y"
    ↓
IS_A(X, Y)
```

Later stages can learn constructions such as:

```text
"X owns Y"       → HAS(X, Y)
"X is in Y"      → LOCATED_IN(X, Y)
"X gave Y to Z"  → TRANSFER(agent=X, object=Y, recipient=Z)
```

The initial implementation may bootstrap with a controlled set of constructions. The architecture must allow learned constructions to be stored and applied like other knowledge.

## 15. Text Generation

Mnesis must not depend on an LLM to produce responses.

The first generation system uses:

- response intentions;
- grammatical constructions;
- lexical selection;
- morphology;
- flexible realization patterns;
- discourse context;
- personality;
- affect;
- confidence.

Example internal intent:

```text
ASK_ABOUT_PREVIOUS_TOPIC(topic)
```

Possible realizations:

```text
"Tu m'avais parlé de {topic}. Ça a avancé ?"
"Au fait, qu'est devenu {topic} ?"
"Je repensais à {topic}. Où en es-tu ?"
```

Over time, Mnesis should be able to learn additional constructions and preferred phrasings from text.

## 16. Memory Architecture

Mnesis uses distinct but connected forms of memory.

### 16.1 Working memory

Temporary conversational/cognitive context:

- active topic;
- current discourse entities;
- unresolved questions;
- recent utterances;
- currently activated concepts.

### 16.2 Episodic memory

Events and experiences:

- conversations;
- teaching events;
- corrections;
- research sessions;
- emotional events;
- significant interactions.

An episode records contextual metadata such as time, participants, importance, affect, and retrieval history.

### 16.3 Semantic memory

Generalized knowledge:

- concepts;
- relations;
- facts;
- definitions;
- classifications;
- beliefs.

### 16.4 Procedural memory

Executable knowledge:

- learned rules;
- procedures;
- strategies;
- skills.

## 17. Forgetting and Consolidation

Memory strength must evolve over time.

Factors may include:

- importance;
- frequency of retrieval;
- recency;
- emotional significance;
- usefulness;
- confidence;
- repeated corroboration.

The model must permit:

- fading accessibility;
- reinforcement;
- consolidation;
- generalization from episodes into semantic knowledge.

Deletion is not the only form of forgetting. A memory may remain stored but become less likely to be recalled.

## 18. Skill and Procedure Learning

Mnesis must learn more than facts.

It distinguishes:

- declarative knowledge — “what I know”;
- procedural knowledge — “how I do something”;
- episodic knowledge — “what happened.”

Example:

```text
DECLARATIVE:
Paris CAPITAL_OF France

PROCEDURAL:
average(values):
    total = sum(values)
    n = count(values)
    return total / n

EPISODIC:
Gildas taught me how to calculate an average.
```

Procedures must be represented in an inspectable executable form rather than opaque code generated at runtime.

## 19. Primitive Cognitive Operations

Mnesis begins with a minimal set of native operations from which more complex skills can be constructed.

Candidate primitives include:

- STORE;
- RECALL;
- MATCH;
- COMPARE;
- TEST;
- ITERATE;
- INCREMENT;
- ASSOCIATE;
- CREATE_RELATION.

The exact bootstrap set will be intentionally small.

The objective is to avoid pretending that a capability was learned when it was actually hidden in a general-purpose implementation library.

For example, counting should eventually be representable as a learned procedure built from simpler primitives rather than merely delegating to Python's `len()`.

## 20. Learning to Count

Counting is an early reference capability for validating procedural learning.

Mnesis should be able to acquire the relationship between a number sequence, successor, iteration, and quantity.

A target conceptual progression is:

```text
successor(1) = 2
successor(2) = 3
successor(3) = 4
...
```

followed by a reusable rule or procedure rather than memorization of every example.

This capability acts as an architectural test that Mnesis can learn a generalizable procedure.

## 21. Reasoning

The reasoning system operates over explicit relations, beliefs, and procedures.

Example deductive rule:

```text
IF cat(X)
THEN mammal(X)
```

Given:

```text
cat(Leela)
```

Mnesis may infer:

```text
mammal(Leela)
```

Inferences must record their derivation so that confidence and explanation can be traced back to premises.

Reasoning initially focuses on deterministic, inspectable symbolic mechanisms. More sophisticated induction may be added later without replacing provenance.

## 22. Corrections and Contradictions

Corrections do not simply mutate a value.

Example:

```text
existing belief:
7 × 8 = 54
confidence = low

new evidence:
7 × 8 = 56
source = user
```

Mnesis should:

1. store the new evidence;
2. detect the conflict;
3. verify against learned arithmetic procedure when available;
4. update belief confidence;
5. reject or retain alternatives according to evidence.

This preserves learning history and avoids hidden destructive updates.

## 23. Personality

Each instance has a relatively stable personality.

Possible traits include:

- curiosity;
- extraversion;
- agreeableness;
- humor;
- optimism;
- impulsiveness.

Traits are continuous values, not labels.

Personality changes slowly, if at all, compared with emotional state.

Personality influences action selection and language realization but does not override factual reasoning.

## 24. Emotional State

Emotions are measurable internal state variables.

Candidate dimensions include:

- joy;
- sadness;
- anger;
- fear;
- curiosity;
- trust;
- boredom.

Events modify these values. Values decay toward instance-specific baselines over time.

Emotion must affect behavior.

Examples:

- high curiosity increases the likelihood of asking questions or researching;
- high boredom increases the probability of changing topic;
- trust may affect willingness to surface personal memories;
- frustration may shorten or alter conversational strategies.

Emotions are functional state, not merely decorative text.

## 25. Drives and Motivations

Mnesis can possess internal drives such as:

- curiosity;
- social interaction;
- novelty;
- certainty;
- learning.

These produce goals independent of direct user commands.

Example:

```text
unresolved concept
+ high curiosity
→ create research or clarification goal
```

Drives are bounded by channel policy and instance permissions.

## 26. Conversational Initiative

Mnesis should not be limited to request/response behavior.

At each conversational decision point it may consider actions such as:

- answer;
- ask;
- clarify;
- recall;
- change topic;
- express affect;
- share a relevant fact;
- investigate;
- remain silent.

Candidate actions are scored from:

- conversation context;
- active goals;
- memory activation;
- personality;
- emotions;
- drives;
- relationship context;
- channel constraints.

The selected action and its major contributing factors must be inspectable.

## 27. Associative Activation

Memories and concepts should support association rather than exact-key lookup only.

Activating one concept can increase activation of related concepts and memories.

Example:

```text
Fun Tracks
  ↔ project
  ↔ programming
  ↔ previous conversation
  ↔ frustration
```

This enables topic recall, spontaneous associations, and context-sensitive memory retrieval.

The first implementation can use a simple bounded spreading-activation algorithm over explicit relations.

## 28. Explainability

Explainability is a first-class requirement.

For a generated answer, Mnesis should eventually expose a trace containing information such as:

- interpreted user intent;
- activated concepts;
- recalled memories;
- consulted claims;
- confidence values;
- inference rules;
- emotional state;
- active drives;
- candidate actions;
- selected action;
- response realization.

The trace is primarily a development/debugging facility and must be separable from the conversational output.

## 29. Channel Adapters

A Mnesis instance may be exposed through different channels.

The core must not know channel-specific protocols.

A channel adapter converts between a channel event and a Mnesis conversation event.

Future examples:

- browser chat;
- CLI;
- X/Twitter;
- messaging service.

Channel policy controls whether the instance may:

- initiate messages;
- perform autonomous research;
- expose memories;
- reply publicly;
- use external connectors.

## 30. Service Boundary

FastAPI provides the first network boundary.

The API will ultimately expose capabilities such as:

- create/manage instances;
- send an utterance;
- retrieve conversation state;
- inspect memories;
- inspect beliefs;
- inspect affect/personality;
- trigger or inspect learning;
- deploy knowledge packs;
- inspect explanation traces.

Exact endpoint names belong in the implementation plan, not this design specification.

## 31. Persistence

PostgreSQL is the source of durable state.

Major persisted domains include:

- instances;
- identities/configuration;
- conversations and utterances;
- lexical entries;
- concepts;
- relations;
- claims;
- evidence and provenance;
- memories;
- procedures;
- rules;
- emotions and personality baselines;
- learning events;
- research sessions;
- knowledge-pack deployments.

Schema details will be specified incrementally during implementation.

## 32. Safety and Resource Boundaries

Autonomous learning requires explicit limits.

Each instance configuration should be able to bound:

- web requests;
- recursive dictionary learning;
- background research depth;
- number of candidate claims;
- maximum research duration;
- permitted domains/source categories;
- storage growth;
- proactive channel activity.

The first version should favor conservative bounded autonomy over continuous unrestricted crawling.

## 33. Determinism and Reproducibility

Where practical, cognitive decisions should be reproducible from:

- persisted state;
- incoming event;
- configuration;
- deterministic scoring/rules.

If random variation is used for conversational diversity, the random seed or selected alternative should be available in the explanation trace.

This is important for testing and for studying how behavior emerges.

## 34. Testing Strategy

Mnesis requires more than endpoint tests.

The project should use:

### Unit tests

For deterministic cognitive primitives and domain models.

### Behavioral tests

Given a known state and event, verify:

- interpretation;
- memory retrieval;
- belief update;
- contradiction handling;
- selected action.

### Learning tests

Verify genuine state change.

A learning test should demonstrate:

1. the capability/knowledge is initially absent;
2. teaching or evidence is provided;
3. internal state changes;
4. a later novel case uses the acquired knowledge.

### Provenance tests

Verify that externally acquired knowledge remains attributable to its evidence.

### Confidence tests

Verify that contradictory evidence changes confidence without silently destroying history.

### Instance isolation tests

Verify that learning in one instance does not leak into another.

### Knowledge pack tests

Verify repeatable, explicit deployment and version tracking.

## 35. V1 Product Slice

The first useful vertical slice should prove the architecture rather than maximize conversational sophistication.

A V1 instance should be able to:

1. receive textual messages;
2. persist a conversation;
3. recognize a controlled set of linguistic constructions;
4. represent words separately from concepts;
5. store semantic claims with provenance and confidence;
6. remember episodic events;
7. detect an unknown word;
8. acquire a dictionary definition through a defined source adapter;
9. store the newly learned lexical/conceptual information;
10. recall and use that information in a later exchange;
11. detect a contradiction between a user statement and trusted knowledge;
12. communicate uncertainty;
13. maintain basic personality and emotional state;
14. choose between answering, asking for clarification, or initiating a related follow-up;
15. expose an explanation trace showing why the action was selected.

The V1 does **not** need fluent unrestricted French. Controlled but genuinely learned language is preferable to fluent output hiding hard-coded intelligence.

## 36. Subsequent Milestones

After the first vertical slice, development can expand incrementally toward:

1. richer lexical acquisition;
2. broader grammatical construction learning;
3. autonomous multi-source research;
4. associative retrieval and consolidation;
5. procedural learning;
6. counting as the first learned generalizable skill;
7. richer conversational initiative;
8. knowledge-pack tooling;
9. multi-channel deployment;
10. browser UI and online hosting.

Each major capability should have its own implementation plan and tests.

## 37. Non-Goals

Mnesis is not intended to be:

- an LLM wrapper;
- a vector-database chatbot;
- a retrieval-augmented generation frontend;
- an attempt to compete with modern LLMs on unrestricted prose fluency;
- a system where “memory” means only storing prior chat messages;
- an agent that treats arbitrary Internet content as truth;
- a system whose internal reasoning cannot be inspected.

## 38. Success Criteria

The project succeeds architecturally when Mnesis can demonstrate behaviors that are genuinely consequences of acquired state.

Examples include:

- learning a previously unknown word and later using it appropriately;
- recalling an interaction because it formed an episodic memory;
- explaining which sources support a claim;
- expressing doubt because evidence is weak or conflicting;
- rejecting a user's incorrect assertion because stronger evidence exists;
- acquiring a procedure and applying it to a novel input;
- developing different knowledge and behavior across two isolated instances;
- receiving a versioned knowledge pack without merging all runtime history;
- producing an inspectable explanation for a conversational action.

The objective is not to make Mnesis appear intelligent by hiding complexity. The objective is to make its apparent intelligence correspond as closely as possible to explicit mechanisms that can be observed, tested, and improved.
