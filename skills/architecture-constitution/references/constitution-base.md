# Base constitution

The default articles a project's constitution (`.specify/memory/constitution.md`) starts from. Each is a rule,
why it holds, and how a breach is caught; the `#n` refer to the [catalog](principles.md). The
[`architecture-constitution`](../SKILL.md) skill writes a project's
constitution and its checks from it (`write`), and reviews plans and diffs against the result (`review`).

## Profiles

- **lean**: scripts, CLIs, automations, a single deployable with one owner. Articles I–VIII.
- **full**: products with several components, personal or customer data, or outside consumers. All articles.

A project keeps its own articles next to these, makes each rule concrete for its paths and tools, and drops
what doesn't apply, with a reason. For repos without a constitution, Articles I and III–VI, in short, make a
good set of design rules for an `AGENTS.md`.

## Articles

### I. Precedence (lean)

- **Rule:** When principles conflict, the higher one wins: security > correctness > simplicity > ease of
  change > performance > reuse. Correctness includes behaviour under failure. The plan or PR names the
  principle given up.
- **Why:** Without an order, every session settles the same conflict differently.
- **Check:** Plan: the Constitution Check, and Complexity Tracking for every justified exception.

### II. The simplest thing that works (lean; #25, #26, #27, #36)

- **Rule:** Build only what the current spec needs: no options, hooks or layers for foreseen needs. A new
  dependency, language, database or service is named and justified in the plan, and needs the owner's
  approval.
- **Why:** Every mechanism is understood, operated and changed for as long as it exists.
- **Check:** Plan: Complexity Tracking. Review: speculative generality, the lockfile and manifest diff.

### III. Fail loudly, never game a check (lean; #69, #116)

- **Rule:** Validate early, exit non-zero on failure, never swallow an error or carry on with bad state.
  Never weaken a test, add a skip or raise a threshold to get green.
- **Why:** Silent failure spreads bad state and hides the cause; a gamed check stops measuring.
- **Check:** CI: lint against bare and empty `except` (e.g. ruff `E722`, `S110`), shellcheck, `set -euo
  pipefail` in shell. Review: diffs that loosen tests.

### IV. Bounded waits, safe retries (lean; #70, #71, #78)

- **Rule:** Every outbound call (HTTP, database, queue, subprocess) has a timeout. Only idempotent operations
  are retried, with backoff and a cap. Every job and script is safe to run twice.
- **Why:** An unbounded wait turns a slow dependency into an outage; naive retries amplify one; deliveries
  and runs repeat.
- **Check:** CI: e.g. ruff `S113` for HTTP calls without a timeout (a semgrep rule for other clients);
  review for the calls no rule covers; a test that runs the operation twice.

### V. One source of truth (lean; #29, #43)

- **Rule:** Each rule, schema, constant and data element has one authoritative place; everything else
  references it or is generated from it.
- **Why:** Copies drift.
- **Check:** Review: the same rule or value defined twice. CI: generated files checked for drift.

### VI. Parse at the boundary (lean; #23, #90)

- **Rule:** Input from outside (requests, files, environment, other services, model output) is parsed once at
  the entry point into typed, validated values; the inside never handles raw input. Malformed input is
  rejected.
- **Why:** Validation scattered inward gets skipped somewhere.
- **Check:** CI: strict type checking, schema validation tests at each entry point.

### VII. Least privilege, no secrets in code (lean; #97, #100, #111)

- **Rule:** Every process, token and pipeline gets the narrowest scope and shortest lifetime that works.
  Access is denied by default and fails closed. Plaintext secrets never go into git (encrypted files, such as
  SOPS, may); at runtime, secrets come from the environment or a secret store.
- **Why:** It limits what a mistake or a compromise can reach.
- **Check:** CI: secret scanning (e.g. gitleaks). Review: every scope, grant and token in the PR.

### VIII. Tested, automated, observable (lean; #109, #114, #117, #119)

- **Rule:** Tests come with the change, most of them fast unit tests. CI runs every check on every PR and
  gates the merge. Every failure in operation reaches someone: logs, and an alert or error handler.
- **Why:** Defects caught early are cheap; a failure nobody sees isn't handled.
- **Check:** CI required for merge. Review: a new component without tests, logs or an alert.

### IX. Dependencies point inward (full; #5, #6, #14)

- **Rule:** `<domain path>` imports no framework, database driver, HTTP client or vendor SDK. Adapters in
  `<adapters path>` implement ports the domain defines. No dependency cycles between components.
- **Why:** Business rules outlive their infrastructure and test without it.
- **Check:** CI: an import contract (e.g. import-linter, dependency-cruiser, ArchUnit).

### X. Contexts own their data (full; #38, #41, #42)

- **Rule:** Each bounded context owns its schema; others go through its API or events, never its tables.
  External models are translated at the adapter. Schema changes are planned in `data-model.md`.
- **Why:** A shared schema couples everyone to every change, and data outlives code.
- **Check:** CI: import rules or database grants per context. Review: every migration.

### XI. Design for failure (full; #67, #73, #74, #82)

- **Rule:** The plan lists, per external dependency, what happens when it is slow, wrong or down, and the
  blast radius. Security paths fail closed; other features degrade by design.
- **Why:** Everything fails; the answer is cheapest before it happens.
- **Check:** Plan: the failure table. CI: a test with a faked fault for each listed case.

### XII. Explicit, additive contracts (full; #89, #91, #92)

- **Rule:** Every interface between deployables or to outside consumers has a schema in the repo. Changes
  are additive (expand, migrate, contract); a breaking change needs a new version. Readers ignore fields they
  don't use.
- **Why:** Contracts are the most shared and least reversible part of a system.
- **Check:** CI: a breaking-change check on the schemas (e.g. `oasdiff breaking`, `buf breaking`).

### XIII. Consistency decided per data (full; #40, #46, #77)

- **Rule:** The plan states, per data store, the transactional boundary, what wins under partition, and how
  steps across boundaries are compensated. No distributed transactions.
- **Why:** Different data needs different guarantees, and the choice is hard to reverse.
- **Check:** Plan.

### XIV. Privacy and threats by design (full; #107, #108)

- **Rule:** A feature touching personal data, auth, secrets or outside input has a threat model and a data
  inventory (purpose, retention, access) in its plan. Development and tests use synthetic data. Logs hold no
  personal data or secrets.
- **Why:** Fixes are cheapest at design time; data you don't hold can't leak.
- **Check:** Plan. CI: no real personal data in fixtures.

### XV. One way of doing things, decisions recorded (full; #57, #59, #61)

- **Rule:** Follow the patterns the repo already uses; a second way of doing the same thing comes only as a
  planned replacement of the first. Irreversible decisions get an ADR; reversible ones are recorded in the PR
  as assumptions.
- **Why:** A coherent design is easier to change than many good, uncoordinated parts.
- **Check:** Review: a new pattern next to an existing one; a one-way door without an ADR.

## Governance

This constitution overrides the project's other conventions. It changes through a PR with a short rationale
and a version bump. An article whose check a tool can run has that check in CI.
