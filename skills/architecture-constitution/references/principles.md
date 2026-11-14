# Architecture principles

119 principles in 12 themes, written for agents: each as **rule**, **why**, **check** and **conflicts**. Read
the theme your task touches, not the whole file. ★ marks the core 20, which the
[base constitution](constitution-base.md) turns into articles.

- **A project's constitution binds; this catalog advises.** Where `.specify/memory/constitution.md` says
  otherwise, the constitution wins.
- **When principles conflict, the higher one wins:** security > correctness > simplicity > ease of change >
  performance > reuse. Correctness includes behaviour under failure. Name the principle you gave up in the plan
  or the PR.
- **Check** says how a breach is found. `CI`: a tool can fail the build (tools are examples; use the one the
  stack has). `Plan`: decided in the plan or an ADR and checked by the Constitution Check. `Review`: a question
  for the reviewer.
- Numbers are stable: refer to a principle as `#n`.

| Theme | # |
|---|---|
| [Structure & modularity](#structure--modularity) | 1–9 |
| [Object & component design](#object--component-design) | 10–17 |
| [Abstraction & interface design](#abstraction--interface-design) | 18–24 |
| [Simplicity & economy](#simplicity--economy) | 25–37 |
| [Domain & data](#domain--data) | 38–49 |
| [Socio-technical](#socio-technical) | 50–54 |
| [Decisions & evolution](#decisions--evolution) | 55–66 |
| [Distributed systems & reliability](#distributed-systems--reliability) | 67–82 |
| [Scalability & performance](#scalability--performance) | 83–88 |
| [Integration & contracts](#integration--contracts) | 89–96 |
| [Security & privacy](#security--privacy) | 97–108 |
| [Delivery, operations & quality](#delivery-operations--quality) | 109–119 |

## Structure & modularity

Cut the system so each change stays local.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 1 | **Separation of Concerns** ★ Give each module one concern (UI, domain, persistence, transport, security), in its own files. | Mixed concerns make every change touch everything. | Review: does one file change for several concerns? (Divergent Change) | #27: don't pre-split a small script |
| 2 | **High Cohesion, Loose Coupling** ★ Keep together what changes for the same reason; between modules share a narrow interface and no mutable state. | Cohesion keeps a change local; coupling sets how far it ripples. | Review: one change edits many files (Shotgun Surgery) | #29: merging look-alike code couples unrelated callers |
| 3 | **Information Hiding** ★ Name the decisions likely to change (vendor, format, storage, algorithm) and hide each behind one module. | A hidden decision changes in one place. | Review: does a vendor type, SQL or file format appear outside its module? | #18: each wall is a layer |
| 4 | **Layering** A layer calls only the layer below it: never upward, never skipping one. | Each level can be understood and replaced alone. | CI: layer contract (import-linter, dependency-cruiser, ArchUnit) | #88: a measured hot path may skip, documented |
| 5 | **Dependency Rule** ★ Dependencies point inward: the domain imports no framework, database driver, HTTP client or vendor SDK; those are adapters behind ports the domain defines. | Business rules outlive their infrastructure; swapping an adapter leaves them untouched. | CI: forbidden imports from the domain package to adapters and frameworks | #27, #28: a script with no domain needs no ports |
| 6 | **Acyclic, Stability-Directed Dependencies** No cycles between components; depend toward more stable ones; the most stable are the most abstract. | A cycle makes components break and release together. | CI: cycle check (dependency-cruiser `no-circular`, import-linter, madge) | — |
| 7 | **Component Cohesion** Package what changes and is reused together; don't make consumers take what they don't use. | Otherwise unrelated changes force consumers to update. | Review: a consumer pulls a package for one function | #2 |
| 8 | **Law of Demeter / Tell, Don't Ask** Call only direct collaborators; tell an object to act instead of pulling its data to decide for it. | Chains like `a.b().c()` couple the caller to a structure it doesn't own. | Review: Message Chains, Feature Envy | #17: plain queries and data records are fine |
| 9 | **Separate Mechanism from Policy** Keep the how (scheduler, retry engine, renderer) apart from the what and when (rules, thresholds, schedules). | Policies change more often than machinery. | Review: thresholds, rules or schedules hard-coded inside the machinery | #27: one policy needs no plug-in point |

## Object & component design

Make components replaceable and safe to extend.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 10 | **Single Responsibility** A module answers to one actor (one group of stakeholders); split it when two groups ask for its changes. | A change for one actor breaks the other. | Review: Divergent Change; `git log` shows edits for unrelated reasons | #27 |
| 11 | **Open/Closed** Once a variation point has proven real, add a variant as new code (strategy, plugin, implementation), not by editing working code. | Editing working code risks regressions. | Review: Repeated Switches on the same type | #27, #30: no extension point before the second variant |
| 12 | **Liskov Substitution** A subtype works wherever its supertype does: no stronger preconditions, no weaker guarantees, no new failure modes. | Callers rely on the contract, not the type. | CI: run the supertype's contract tests against every implementation | — |
| 13 | **Interface Segregation** Clients depend only on the methods they call; prefer small role interfaces to one fat one. | Fat interfaces couple clients to changes they don't use. | Review: test fakes stubbing methods nobody calls | #27 |
| 14 | **Dependency Inversion** Policy and detail both depend on an abstraction, and the policy side owns it. | The class-level mechanism behind #5. | CI: same forbidden-import rule as #5 | #18, #27 |
| 15 | **Program to an Interface** Depend on a contract where implementations vary or must be faked in tests. | Implementations can be swapped, faked or moved across a network. | Review: a test needs the real database because the code names it | #27: an interface with one implementation and no test need is Speculative Generality |
| 16 | **Composition over Inheritance** Assemble behaviour from parts; inherit only for a true is-a that passes #12. | Inheritance couples you to a parent's internals. | Review: Refused Bequest; inheritance deeper than two levels | — |
| 17 | **Command–Query Separation** A function changes state or returns an answer, not both. | Queries become safe to call, cache and retry. | Review: a getter with a side effect | Atomic operations (pop, compare-and-swap, create returning an ID) are accepted exceptions |

## Abstraction & interface design

Hide the right things, leak little, make misuse hard.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 18 | **Indirection** Add a layer only for a named problem (swap, test, hide a decision); remove layers that only delegate. | Every layer is a hop to read and debug. | Review: Middle Man | #3, #5 vs #25 |
| 19 | **Leaky Abstractions** Know the failure modes under what you use (ORM queries, RPC latency, service limits) and handle them where you call it. | They surface in production. | Review: RPC or ORM calls in a loop (N+1), no handling of rate limits | — |
| 20 | **Rule of Least Power** Use the least powerful mechanism that works: data or config before a DSL, a DSL before code. | Less power is easier to validate, analyse and secure. | Review: logic hidden in config, or code where a table would do | #35 |
| 21 | **Least Astonishment** Name things for what they do; no hidden side effects; defaults are what a user expects. | People act on what they expect. | Review: Mysterious Name; a name that hides a write | — |
| 22 | **Easy to Use Correctly** Make the obvious call the right one: explicit required arguments, safe defaults, types that reject misuse. | Misuse that compiles ships. | Review: boolean flags, same-typed positional arguments, required call order | — |
| 23 | **Make Illegal States Unrepresentable** Parse outside input once at the boundary into types that can't hold invalid data; pass those inward, never raw strings or dicts. | Validation scattered inward gets skipped somewhere. | CI: strict type checking; schema validation at every entry point. Review: Primitive Obsession | #92: ignore unknown fields, validate the ones you use |
| 24 | **Conservation of Complexity** Complexity that can't be removed goes into the platform or library once, not into every caller. | One owner carries it instead of every user. | Review: the same workaround in several callers | #27, #30 |

## Simplicity & economy

Every mechanism is understood, operated and changed for years: add only what the problem needs.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 25 | **Keep It Simple** ★ Choose the simplest design that meets the spec; justify every extra mechanism in the plan. | Each mechanism costs for as long as it exists. | Plan: Constitution Check; extras go into Complexity Tracking | Ranks above ease of change, performance and reuse |
| 26 | **Gall's Law** Start from a simple system that works end to end and grow it in small working steps. | A complex system designed from scratch doesn't work and can't be patched into working. | Plan: the first task is a thin end-to-end slice | — |
| 27 | **YAGNI** ★ Build only what the current story needs: no options, hooks or abstractions for foreseen needs. | Foreseen needs are often wrong, and unused code still costs. | Review: Speculative Generality; behaviour the spec didn't ask for | #11, #15, #62: YAGNI wins unless the decision is a one-way door (#61) |
| 28 | **Monolith First** Start as one well-modularised deployable; extract a service only for a stated reason (scale, isolation, ownership) and a boundary that has proven stable. | Distribution costs network failures, deploys and consistency. | Plan: a new deployable names its reason | #113 |
| 29 | **DRY** ★ Each piece of knowledge (rule, schema, constant, config value) has one authoritative place; the rest references or is generated from it. Code that only looks alike is not knowledge. | Two copies of a rule drift. | Review: one rule or constant defined twice. CI: generated files in sync | #2, #30: don't merge code that only looks alike |
| 30 | **Rule of Three** Abstract duplicated code on the third occurrence, not the second. | Duplication is cheaper than the wrong abstraction. | Review: an abstraction with one or two callers | #29: duplicated knowledge is merged at once |
| 31 | **Minimise Accidental Complexity** Each tool, layer or pattern must earn its place against the problem; remove what only serves the tooling. | The problem's complexity is given; the rest is chosen. | Plan: each new dependency or tool justified | — |
| 32 | **Simple ≠ Easy** Prefer fewer intertwined parts over familiar designs that entangle (shared state, implicit ordering, global config). | Entanglement compounds; familiarity doesn't. | Review: understanding one part requires reading another | #36: pick what is both boring and simple |
| 33 | **Worse Is Better** Ship the simple implementation for the main case; fail loudly on rare cases until they're needed. | Simple things ship, get used and improve. | Plan: scope of the first slice | Never for a case that corrupts or leaks data (security, correctness rank higher) |
| 34 | **Kernighan's Law** Write code a tired reader can debug: no clever tricks, no dense one-liners where a few plain lines do. | Debugging takes twice the cleverness of writing. | Review: can this line be explained in one sentence? | #88 |
| 35 | **Convention over Configuration** Follow the framework's and the repo's conventions; add an option only for a real exception, with a default that works. | Every option is a decision and a chance to differ. | Review: a new option without a user | #20 |
| 36 | **Choose Boring Technology** Use what the repo and stack already use; a new language, database, framework or service needs a reason in the plan and the owner's approval. | Known tools have known failure modes; spend the few innovation tokens where you differentiate. | Plan: technology list. Review: lockfile and manifest diff | — |
| 37 | **Make It Work, Make It Right, Make It Fast** In that order; optimise only where a measurement says so. | Optimising wrong or unclear code wastes the work. | Review: optimisation without numbers | #88 |

## Domain & data

Model boundaries and data ownership outlive the code: make them explicit.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 38 | **Bounded Contexts & Data Ownership** ★ Draw module and service boundaries along domain boundaries; each context owns its schema; others use its API or events, never its tables. | A shared database couples everyone to every schema change. | CI: import rules or database grants per context. Plan: context map | #28: in a monolith, separate modules and schemas suffice |
| 39 | **Ubiquitous Language** Use the domain's terms in code, APIs, docs and specs, one term per concept, defined in the spec. | Every translation between business and code breeds defects. | Review: two names for one concept; code terms the spec doesn't use | — |
| 40 | **Aggregates as Consistency Boundaries** Enforce an invariant inside one small aggregate in one transaction; reference other aggregates by ID and reconcile eventually. | Large transactional boundaries contend and don't scale. | Review: one transaction updating several aggregates | #46 |
| 41 | **Anti-Corruption Layer** Translate external and legacy models into your own types at the adapter; their names and quirks don't pass it. | Foreign concepts leak and spread. | CI: vendor SDK types imported only in the adapter (as #5) | #18 |
| 42 | **Data Dominates** Design the data model (entities, keys, ownership, lifecycle) before the code, and review schema changes hardest. | Data outlives code; schema changes are among the least reversible. | Plan: `data-model.md`. Review: every migration | — |
| 43 | **Single Source of Truth** Each data element has one authoritative owner; copies are derived, marked as copies and refreshable from it. | Two writable copies diverge. | Plan: owner per entity. Review: a second writer | #87 |
| 44 | **Minimise Mutable State** Keep state in few places; prefer immutable values; where history matters, append facts and derive current state. | State is the main source of complexity and bugs. | Review: mutable module-level globals; in-place updates that destroy needed history | #25: event sourcing only where history is a requirement |
| 45 | **Separate Reads from Writes (CQRS)** Split read and write models only when their shape or scale clearly differ. | The write side protects invariants, the read side serves queries; the split adds moving parts. | Plan: justified in Complexity Tracking | #25 |
| 46 | **Sagas over Distributed Transactions** Across services, chain local transactions with compensating actions; no two-phase commit. | Two-phase commit ties every participant's availability together. | Plan: each step names its compensation | #28: inside one deployable, use one local transaction |
| 47 | **Data as a Product** Data published for others has an owner, a schema, docs and quality checks, like an API. | Unowned data rots and breaks consumers silently. | CI: schema and data-quality tests on published datasets | #27: internal data needs none of this |
| 48 | **Changing Anything Changes Everything** In ML systems, version data, features, models and config together, and monitor input drift. | Entangled inputs make no change local. | CI: versions pinned together. Plan: drift monitor | — |
| 49 | **Don't Start with ML** Ship a rule or heuristic baseline first; add a learned model, an LLM included, only where it measurably beats the baseline. | The baseline gives data, a pipeline and a benchmark. | Plan: baseline and metric named | — |

## Socio-technical

Structure follows who works on it, agents included.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 50 | **Conway's Law** ★ Align module boundaries with ownership and hand-over: one owner per module, and a story that touches one module where possible. | The system copies the communication structure that builds it. | Plan: which owner or story owns each module | — |
| 51 | **Inverse Conway Maneuver** Set repos, owners and story boundaries to match the architecture you want. | Otherwise the organisation's shape wins. | Plan | — |
| 52 | **Limit Cognitive Load** Size each module or service so one owner, or one agent session, can hold it whole; split by domain when it outgrows that. | What nobody can hold, nobody owns. | Review: a story needs reading most of the repo | #28 |
| 53 | **You Build It, You Run It** Whoever builds a component also ships its health check, alerts and runbook; operating it is part of done. | Owners who operate what they build design for operability. | Review: a new component without health check, alerts or logs | — |
| 54 | **Brooks's Law** Don't speed up a late story by adding agents or people to it; cut scope or split it into independent stories. | Ramp-up and n(n−1)/2 communication paths cost more than they add. | Plan | — |

## Decisions & evolution

Decide explicitly, record why, keep expensive decisions few.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 55 | **Everything Is a Trade-off** ★ For every significant decision, name its downside and the alternative you rejected; settle conflicts by the precedence order above. | A decision without a known downside isn't understood. | Plan or ADR: the consequences name the costs | Arbitrates all others |
| 56 | **Why Matters More Than How** Record why, not only what: in ADRs, PRs and code comments. | The reasoning outlasts the implementation. | Review: a decision without a reason | — |
| 57 | **Document Decisions (ADRs)** Record each hard-to-reverse or cross-cutting decision as a short ADR (context, decision, consequences); supersede, never rewrite. | Later sessions need the context. | Review: a one-way door without an ADR | #27: two-way doors need none |
| 58 | **Quality Attributes Drive Architecture** Name and rank the three to five qualities that matter (e.g. security, availability, modifiability) in the plan, and design for them. | The qualities, not the functions, shape the structure; you can't maximise all. | Plan: ranked list | — |
| 59 | **Conceptual Integrity** ★ Follow the patterns the repo already uses; a second way of doing the same thing (HTTP client, error style, config loader) comes only as a planned replacement of the first. | One coherent design beats many good, uncoordinated ones. | Review: a new pattern next to an existing one | #64: two ways during a migration, with an end |
| 60 | **Optimise for Cost of Change** ★ Spend design effort where change is expensive (data model, public contracts, boundaries, security) and keep the rest cheap to change. | Architecture is the decisions that are costly to change. | Plan: what here is hard to reverse | #27 |
| 61 | **One-Way vs. Two-Way Doors** Classify each decision. Reversible: decide fast and record it as `Assumed X because Y`. Irreversible: slow down, plan, write an ADR, ask. | Treating two-way doors as one-way stalls work; the reverse breaks things. | Review: assumptions in the PR; ADR for one-way doors | — |
| 62 | **Last Responsible Moment** Defer an irreversible choice until not deciding costs more than deciding; keep it open with a cheap seam meanwhile. | Later decisions have more information. | Plan | #27: the seam itself must be cheap |
| 63 | **Evolutionary Architecture** Protect each key quality with an automated fitness function in CI (dependency rules, latency budget, security scan). | Rules nobody checks erode. | CI: each checkable constitution article has its check | #116 |
| 64 | **Migrate Incrementally (Strangler Fig)** Replace a system piece by piece behind a facade; no big-bang rewrite. | A rewrite loses the knowledge in the old code and ships late. | Plan: each migration step ships on its own | #59 |
| 65 | **Lehman's Laws** Keep reducing complexity as part of ongoing work; leave touched code no more complex than you found it. | A system in use grows more complex unless work reduces it. | Review | Stay inside the story: wider clean-ups get their own PR |
| 66 | **Manage Technical Debt Deliberately** Take debt visibly: every shortcut gets an issue, and a `TODO` names it; pay it down continuously. | Hidden debt compounds. | CI or review: `TODO` without an issue reference | #65 |

## Distributed systems & reliability

Every call can be slow, lost, duplicated or wrong: decide in advance what happens then.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 67 | **Design for Failure** ★ For every dependency, decide in the plan what happens when it's slow, wrong or down: timeout, retry, fallback, or an error the user sees. | Everything fails eventually. | Plan: failure table per dependency | #25: scale the handling to the blast radius |
| 68 | **Fallacies of Distributed Computing** Treat every network call as unreliable, slow, insecure and costly, never like a local call. | The eight fallacies cause most distributed bugs. | Review: remote calls in loops, unhandled errors, plaintext transport | — |
| 69 | **Fail Fast / Let It Crash** Validate early, fail loudly with a clear error, never swallow exceptions or carry on with bad state; let a supervisor (systemd, the scheduler) restart. | Limping on spreads corruption and hides the cause. | CI: lint against bare and empty `except` (ruff `E722`, `S110`), `set -euo pipefail` with shellcheck | #74: degrade only by design, never by swallowing |
| 70 | **Bound Every Wait** Every outbound call (HTTP, database, queue, subprocess) has an explicit timeout; deadlines propagate down the chain. | An unbounded wait turns a slow dependency into your outage. | CI: e.g. ruff `S113` (requests without timeout), semgrep. Review | — |
| 71 | **Retry Safely** Retry only idempotent operations, with exponential backoff, jitter and a cap; retry at one layer only. | Naive retries amplify an outage. | Review: retry loops without backoff or cap; retried non-idempotent writes | #78 |
| 72 | **Circuit Breakers** Around a dependency that keeps failing, stop calling for a while, fail fast, then probe. | Protects caller and callee. | Plan: for high-volume dependencies | #25: for low volume, a timeout and a capped retry suffice |
| 73 | **Bulkheads & Blast Radius** Give each dependency or tenant its own pool or limit, so one failure can't exhaust shared resources; state the blast radius in the plan. | Contains a failure to its compartment. | Plan: one blast-radius line per component | #25 |
| 74 | **Graceful Degradation** Decide in advance which features may go dark, and serve reduced function (cached, default, off) instead of nothing, telling the user. | Partial service beats none. | Plan; Review | #69; #100: security paths fail closed, never open |
| 75 | **No Single Point of Failure** Where availability is a ranked quality, make every layer redundant and test failover regularly. | Untested redundancy fails when needed. | Plan; a failover test exists | #25: a single server is an accepted, documented SPOF with tested backups |
| 76 | **Backpressure & Load Shedding** Bound every queue and buffer; when full, slow the producer or reject early. | Unbounded queues turn overload into latency and memory exhaustion. | Review: queues or buffers without a maximum size | — |
| 77 | **CAP / PACELC** ★ For each replicated store, write down what wins under partition (consistency or availability) and otherwise (latency or consistency). | A ledger and a feed need different answers. | Plan: per data store | #43 |
| 78 | **Idempotency** ★ Make every operation that can be retried or redelivered safe to repeat: idempotency keys, upserts, dedupe by message ID; scripts safe to re-run. | Messages get lost and duplicated; idempotent consumers turn at-least-once into effectively-once. | CI: a test that runs the operation twice and compares | — |
| 79 | **End-to-End Argument** Implement integrity, delivery and dedupe guarantees at the endpoints, not in transport or middleware. | Lower layers can only optimise them. | Review | #94 |
| 80 | **Avoid Coordination** Prefer local decisions that merge later (commutative operations, CRDTs, one owner per key) over locks, consensus and distributed transactions. | Coordination caps scale and availability. | Plan | Correctness ranks higher: coordinate where an invariant demands it |
| 81 | **Don't Trust Clocks** Never order events or elect leaders by wall-clock time across machines; use sequence numbers, version vectors or fencing tokens, and monotonic clocks for durations. | Wall clocks drift and jump. | Review: wall-clock time used for durations or ordering | — |
| 82 | **Chaos Engineering** Test failure handling by injecting faults (dependency down, added latency) before trusting it. | Failure paths that never run don't work. | CI: tests with faked faults for each case in the failure table | #25: production chaos only where availability is ranked |

## Scalability & performance

Scale comes from statelessness and partitioning; optimisation starts with a measurement.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 83 | **Statelessness & Shared Nothing** ★ Keep processes stateless: state lives in stores built for it (database, queue, object store), not in process memory or local disk. | Stateless processes scale out, crash and redeploy freely. | Review: in-memory sessions, local files used as state | #87: caches are derived and may be lost |
| 84 | **The Scale Cube** When one node isn't enough, clone behind a load balancer first (X); split by function (Y) or by data (Z) only where a measured bottleneck needs it. | Cloning is cheapest once processes are stateless. | Plan: the measured bottleneck | #28 |
| 85 | **Amdahl & Universal Scalability** Measure the serial fraction and contention before parallelising; stop adding workers when throughput stops rising. | Speedup is capped and can even fall. | Plan: load-test numbers | — |
| 86 | **Little's Law** Size pools, queues and concurrency limits with L = λW (in flight = arrival rate × time in system). | Guessed limits waste resources or overload. | Plan: the calculation | — |
| 87 | **Locality & Caching** Cache only with a stated invalidation rule and TTL; a cache is a derived copy (#43), never the source. | Caches are a correctness risk. | Review: a cache without TTL or invalidation | #43, #37 |
| 88 | **Measure Before You Optimise** Optimise only with a profile or benchmark in the PR, but settle architectural costs (network hops, data locality, N+1) in the plan. | Guesses about hot spots are mostly wrong; the expensive ones are architectural. | Review: optimisation without numbers | #34, #25 |

## Integration & contracts

Interfaces are the most shared and least reversible parts: make them explicit, evolve them without breaking
consumers.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 89 | **Explicit, Evolvable Contracts** ★ Every interface between deployables or to outside consumers has a schema in the repo (OpenAPI, AsyncAPI, protobuf, JSON Schema), written before the code, versioned, changed additively (expand, migrate, contract), deprecated with notice. | Contracts are the most shared and least reversible part of a system. | CI: breaking-change check (e.g. `oasdiff breaking`, `buf breaking`) | #27: calls inside one deployable need no schema |
| 90 | **Robustness Principle** Send strictly valid output; accept leniently only what the contract allows, and reject malformed input. | Too much leniency hardens bugs into standards (RFC 9413). | CI: output validated against its schema in tests | #23, #92; security ranks higher: reject the malformed |
| 91 | **Hyrum's Law** Treat everything consumers can observe (timing, order, error texts, undocumented fields) as contract, and change it with the same care. | Somebody depends on it. | Review: the PR names every change to observable behaviour | — |
| 92 | **Tolerant Reader** Read only the fields you need and ignore unknown ones. | Providers can evolve without breaking you. | Review: deserialisers that fail on unknown fields outside a security boundary | #23, #90 |
| 93 | **Consumer-Driven Contracts** Where both sides are yours, the consumer's expectations run as tests in the provider's CI. | Breaking changes are caught before release. | CI: contract tests (e.g. Pact, or shared schema fixtures) | #25: one consumer in the same repo needs none |
| 94 | **Smart Endpoints, Dumb Pipes** Business logic lives in services; queues, gateways and workflow glue only transport and route. | Logic in middleware is hidden and shared by everyone. | Review: business rules in a gateway, bus or flow definition | — |
| 95 | **Decouple in Time** Use events or queues where producer and consumer must fail, scale or deploy independently; accept eventual consistency and trace across the hop. | Synchronous chains fail together. | Plan | #25, #114 |
| 96 | **Uniform Interface** In HTTP APIs, use resources with standard methods and status codes: GET is safe and cacheable, PUT and DELETE are idempotent. | Generic semantics give interoperability and caching for free. | CI: API linter (e.g. Spectral) | — |

## Security & privacy

Design security in; most of these are Saltzer & Schroeder's (1975).

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 97 | **Least Privilege** ★ Every process, token, service account and pipeline gets the narrowest permission and the shortest lifetime that works. | It limits what a compromise can do. | Review: every scope and grant in the PR. CI: IaC policy scan | Ranks first |
| 98 | **Defense in Depth** Layer independent controls (network, identity, application, data) so no single failure is a breach. | Every control fails sometimes. | Plan: the threat model names the layers | #102: each layer stays simple |
| 99 | **Zero Trust** Authenticate and authorise every request, internal ones too; network location grants nothing. | Internal networks get breached. | Review: an endpoint without auth "because it's internal" | — |
| 100 | **Fail-Safe Defaults** Deny by default; an error in an auth or permission path fails closed; ship with secure settings on. | An omission then denies instead of grants. | CI: tests that unauthenticated and unauthorised requests are refused | #74 |
| 101 | **Complete Mediation** Check authorisation on every access to every resource, at the resource, not only at login or the gateway. | Front-door-only checks get bypassed. | CI: per-endpoint authorisation tests. Review: an ID from the request used without an ownership check | #87: don't cache authorisation decisions past a change |
| 102 | **Economy of Mechanism** Keep security code small and use vetted libraries; never write your own crypto, auth or session handling. | Small mechanisms can be verified. | Review | — |
| 103 | **Open Design** Security rests on keys, never on a secret design, hidden URL or obscure endpoint. | The attacker knows the system. | Review | — |
| 104 | **Separation of Privilege** Critical actions (merge, deploy, delete, payment, secret change) need two parties or conditions: an agent proposes, a human approves. | One compromised party isn't enough. | Branch protection and required approvals | — |
| 105 | **Least Common Mechanism** Minimise what users or tenants share (pools, caches, temp files, credentials); isolate per tenant where data is sensitive. | Every shared path can leak. | Review: cache keys without tenant, shared temp files | #24, #25 |
| 106 | **Psychological Acceptability** Make the secure path the easiest one: one helper for secrets, auth on by default. | Security that's hard to use gets bypassed. | Review | — |
| 107 | **Threat-Model Early** For a feature touching auth, secrets, personal data or outside input, list in the plan what can go wrong (e.g. STRIDE) and the mitigation. | Fixes are cheapest at design time. | Plan: threat section | #25: scale it to the risk |
| 108 | **Privacy by Design & Data Minimisation** Collect only the personal data the purpose needs, keep it only as long as needed, restrict access by purpose; use synthetic data in development and tests. | Data you don't hold can't leak (GDPR Article 25). | Plan: data inventory with purpose and retention. CI: no real personal data in fixtures | — |

## Delivery, operations & quality

A system is only as good as your ability to change, run and observe it safely.

| # | Rule | Why | Check | Conflicts |
|---|---|---|---|---|
| 109 | **Automate (Almost) Everything** ★ Every repeated step (build, test, deploy, migrate, release) runs as code in CI or a script; do painful steps more often, not less. | Small automated changes are cheap and boring. | CI runs every check; Review: manual steps in a README | — |
| 110 | **Infrastructure as Code** Define servers, config and infrastructure in version-controlled code, change them through a PR, and replace rather than patch by hand. | Reproducible, reviewable, disposable. | Review: a manual change on a server; drift detection | — |
| 111 | **Build Once, Configure per Environment** Build one artifact and promote it through every stage; config and secrets come from the environment, never from the code. | What you tested is what you ship. | CI: secret scanning (e.g. gitleaks); no environment names in code | — |
| 112 | **Separate Deployment from Release** Ship risky changes dark (feature flag, disabled schedule) and switch them on separately; roll back with the switch. | Deploys become safe and releases reversible. | Plan | #25: remove a flag once released |
| 113 | **Independent Deployability** Each deployable ships on its own; a change that forces several to deploy together is a design defect. | Lock-step deploys are a distributed monolith. | Plan; CI contract checks (#89) | #28 |
| 114 | **Observability** ★ From the first deploy, emit structured logs and key metrics, and traces with correlation IDs across services; every failure reaches someone. | You can answer questions you didn't anticipate. | Review: a new component without logs, health check or alert | #108: no personal data or secrets in logs |
| 115 | **SLOs & Error Budgets** Where availability is ranked, set SLOs from the user's view; when the budget is spent, harden before adding features. | It makes the speed-reliability trade explicit. | Plan; a dashboard | #116 |
| 116 | **Goodhart's Law** Never game a check: don't weaken a test, add a skip, raise a threshold or special-case code to get green; fix the cause or say in the PR why the check is wrong. | A measure that becomes a target stops measuring. | Review: diffs that loosen tests, add skips or raise thresholds | — |
| 117 | **Build Quality In** Prevent defects with types, tests written with the change, and fast checks in pre-commit and CI, not with a late test phase. | Inspection at the end finds defects late and expensively. | CI on every PR; tests in the same PR | — |
| 118 | **Design for Testability** Keep the domain core free of I/O so it tests without mocks; inject dependencies at the edges; code that is hard to test is badly coupled, so fix the design. | Testable code is decoupled code. | Review: tests of pure logic that need network or database | #5 |
| 119 | **Test Pyramid** Many fast unit tests, fewer integration tests, few end-to-end tests; catch each bug at the lowest level that can. | Fast suites run often; slow ones get skipped. | Review: a bug fix whose only test is end-to-end | — |
