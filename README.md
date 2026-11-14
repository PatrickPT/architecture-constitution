# architecture-constitution

**Architecture rules your coding agents follow and your CI enforces.**

A coding agent follows the rules a repository states and guesses the rest. [spec-kit](https://github.com/github/spec-kit)
gives a project a constitution for those rules, but it starts from a blank page, and nothing checks it. This skill
starts from a tested base, makes each rule concrete for your repository (real paths, real tools), and adds the
check that enforces it to CI. Then it reviews plans and diffs against the result.

It is one skill in the open Agent Skills format (`SKILL.md`), for any harness that reads it. The `lean` profile
works without spec-kit; `full` expects a repository set up with it.

## What's inside

[`skills/architecture-constitution/`](skills/architecture-constitution/) holds the skill and what it reads:

- [`SKILL.md`](skills/architecture-constitution/SKILL.md): two modes, `write` and `review`.
- [`references/constitution-base.md`](skills/architecture-constitution/references/constitution-base.md): 15
  articles in two profiles. `lean` (Articles I–VIII) is for scripts, CLIs and a single deployable with one owner;
  `full` for products with several components, personal data or outside consumers.
- [`references/principles.md`](skills/architecture-constitution/references/principles.md): 119 principles in 12
  themes, each as rule, why, check and conflicts. Agents read the themes a change touches, never the whole file.

When principles conflict, the higher one wins: security > correctness > simplicity > ease of change >
performance > reuse. A project's constitution can set its own order.

## Install

```sh
npx skills add PatrickPT/architecture-constitution
```

To pin it, add `#<full commit sha>` to the source. Or copy the skill's folder into your harness's skills folder.

## Use

```text
/architecture-constitution write lean     # or full: one PR with the constitution, its CI checks and AGENTS.md
/architecture-constitution review main    # the diff since main, or a spec-kit plan; read only
```

A review of an invented shop service:

```text
## Constitution
| Article | Result | Evidence |
|---|---|---|
| III. Fail loudly, never game a check | pass | ruff E722 and S110 run in CI |
| IV. Bounded waits, safe retries | fail | `src/shop/payments/client.py:41` posts without a timeout |
| IX. Dependencies point inward | fail | `src/shop/domain/order.py:3` imports `sqlalchemy` |
| XII. Explicit, additive contracts | n/a | no schema changed |

## Findings
- **blocker** · IX / #5 · `src/shop/domain/order.py:3` imports `sqlalchemy` · move the query behind the repository port
- **blocker** · IV / #70 · `src/shop/payments/client.py:41` has no timeout · pass one, and add ruff `S113` to CI
- **minor** · #44 · `src/shop/cart.py:12` keeps carts in a module-level dict · move them into the cart store

Verdict: changes
```

## Contributing

Principle numbers are stable, so constitutions can cite them. See [CONTRIBUTING.md](CONTRIBUTING.md), and
[SECURITY.md](SECURITY.md) for reporting a vulnerability. Everyone who takes part follows the
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

[Apache-2.0](LICENSE).
