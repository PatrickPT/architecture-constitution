---
name: architecture-constitution
description: "Write a project's architecture constitution, or review against it. write: create or update .specify/memory/constitution.md from the bundled base (lean or full profile, every rule concrete for this repo) and add each article's check to pre-commit or CI. review: check a spec-kit plan or a diff against that constitution and the bundled architecture principles, read only, ending in one Verdict line. Use when a project gets or changes its constitution, when asked for an architecture review, or in the review step for changes to structure, data, contracts, infrastructure or security. Prefer it over /speckit-constitution, which it calls itself, when a constitution should start from the base or get its CI checks."
license: Apache-2.0
---

# Architecture constitution

Two modes over the same sources. `write` gives a project its constitution and the checks that enforce it;
`review` holds a plan or a diff to it. Take the mode from the request (`/architecture-constitution write full`,
`/architecture-constitution review main`); if it isn't clear, ask.

## Sources

The base and the catalog ship with this skill, in `references/` next to this file.

| What | Where | Weight |
|---|---|---|
| The project's constitution | `.specify/memory/constitution.md` | binding |
| The base: profiles and 15 articles | [`references/constitution-base.md`](references/constitution-base.md) | the default where the project has none |
| The catalog: 119 principles as rule, why, check, conflicts | [`references/principles.md`](references/principles.md) | advisory |

When principles conflict, the constitution's own order wins; without one: security > correctness > simplicity >
ease of change > performance > reuse.

Read the catalog by theme, never whole. What the input touches decides the themes:

| The input touches | Themes (#) |
|---|---|
| modules, packages, imports, layers | structure 1–9, object design 10–17 |
| public functions, types, config, parsing input | abstraction 18–24 |
| a new dependency, tool, service or abstraction | simplicity 25–37 |
| schemas, migrations, data ownership, models | domain & data 38–49 |
| calls to other services, queues, retries, jobs | distributed systems 67–82 |
| load, caching, concurrency | scalability 83–88 |
| APIs, events or schemas others consume | integration 89–96 |
| auth, tokens, secrets, personal data, outside input | security 97–108 |
| CI, deploys, infrastructure, logging, tests | delivery 109–119 |
| ownership, story boundaries, hard-to-reverse decisions | socio-technical 50–54, decisions 55–66 |

## write

The result is one PR in the project: the constitution, the checks that enforce it, and the project's
`AGENTS.md` where its checks change. No feature code.

1. **Read the repo**: `AGENTS.md` (checks, structure), the manifests (`pyproject.toml`, `package.json`, …), the
   CI workflows, the pre-commit config, the directory layout and the existing constitution. Without `.specify/`:
   for a `full` project, stop, it needs [spec-kit](https://github.com/github/spec-kit)'s `specify init` first; for a `lean`
   one, write `.specify/memory/constitution.md` directly in step 4, and say in the PR that only CI and review
   then enforce it.
2. **Pick the profile** by the base's criteria and say why. If it's unclear, ask; unattended, take `full` and
   record it as an assumption.
3. **Draft the articles.** Keep, adapt or drop each base article of the profile, with a reason.
   - Make every rule concrete: real paths and tools, not principle names. Not "dependencies point inward" but
     "`src/domain/` imports nothing from `src/adapters/`, `fastapi` or `sqlalchemy`".
   - Keep the project's own articles. Where one already covers a base article, merge them: one rule, one place.
   - Every article ends with its check: the tool that enforces it, or the review question that catches it.
4. **Write the constitution with `/speckit-constitution`**, the draft as its input. It keeps the version, the
   dates and the sync report; don't edit the file around it. Without spec-kit, write the file yourself in the
   same shape: articles, governance, a version line.
5. **Add the checks.** `/speckit-constitution` changes nothing but the constitution, so this step adds the
   gates. For each article a tool can check:
   - already enforced (Makefile, CI, pre-commit)? Leave it.
   - otherwise add the smallest config in the repo's stack (an import contract, a lint rule, a secret scan, a
     breaking-change check on a schema) to the checks CI already runs, and to `AGENTS.md`'s checks.
   - run it. If existing code fails, fix it when that's small and inside the article. Otherwise keep the rule
     strict, list the existing breaches as known exceptions with an issue each, and say so in the PR. Never
     loosen a rule to get green.
6. **Hand over**: commit, push and open the PR, with the project's checks green. The PR body lists, per
   article, kept, adapted or dropped and why, and per check, the tool and where it runs.

## review

Read only: never edit, commit or push. Run it as the second agent, not in the session that wrote the plan or
the code.

1. **Pin the input.**
   - A plan: `specs/NNN-<name>/plan.md`, with `spec.md`, `data-model.md` and `contracts/` where they exist.
   - A diff: `git diff <fixed point>...HEAD` and `git log <fixed point>..HEAD --oneline`. Confirm the ref
     resolves and the diff isn't empty before going on.
2. **Load the constitution.** If there is none, review against the base (`full` for several deployables,
   personal data or outside consumers, otherwise `lean`) and say so; "no constitution" is then a finding.
3. **Check every article**: pass, fail or n/a, with the evidence (`file:line` or the plan's section).
   - A breach the plan's Complexity Tracking justifies passes, if it names the simpler alternative and why it
     was rejected.
   - An article whose tool check CI doesn't run is a finding of its own.
4. **Ask the catalog** for the themes the input touches: each principle's `Check` is the question.
5. **Resolve conflicts** by precedence: when a finding trades one principle for another, say which wins and
   why. Skip what green CI already enforces.

Severity:

- **blocker**: fails an article of the project's constitution, or breaks security or correctness.
- **major**: fails a base article where the project has no constitution, a ★ principle or a ranked quality
  attribute; an article without its check; no constitution in a `full` project.
- **minor**: any other judgement call; no constitution in a `lean` project.

The report, under 500 words:

```text
## Constitution
| Article | Result | Evidence |

## Findings
- **blocker** · IX / #5 · `src/domain/order.py:3` imports `sqlalchemy` · move the query behind the repository port

Verdict: changes
```

End with exactly one line: `Verdict: pass` (no blocker or major), `Verdict: changes` (any blocker or major) or
`Verdict: unsure` (something material couldn't be checked). When it runs next to a code review, both
reports go into one PR comment: leave this report's Verdict line out and end the comment with one line for
both, `changes` if either report has a blocker or major, else `unsure` if something material couldn't be
checked, else `pass`.
