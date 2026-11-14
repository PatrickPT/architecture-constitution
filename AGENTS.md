# AGENTS.md

`architecture-constitution` is an agent skill: a catalog of architecture principles, a base constitution built
from them, and a `SKILL.md` that writes a project's constitution with its CI checks (`write`) and reviews plans
and diffs against it (`review`). Everything here is Markdown that agents read, plus one consistency check.

## Checks

Run them before you hand over; CI runs the same.

```sh
make check         # everything below
make consistency   # scripts/check.py: references, ranges, complete rows, article order, counts, links
make test          # python3 -m unittest: the check catches each kind of drift
```

## Rules of this project

- Principle numbers never change, because constitutions cite them. A new principle takes the next free number
  and goes into its theme's table; the theme index and the skill's theme table list it. A number is never
  reused.
- Every principle has a rule, a why, a check and its conflicts. Every article has a rule, a why and a check.
- One fact in one place. The base cites principles by `#n` instead of repeating them; counts and ranges stated
  in prose are checked by `scripts/check.py`.
- The skill reads only files in its own folder, by relative path. No harness-specific paths.
- Examples use invented repositories and paths. No real names, hosts or customer data.
- Write for agents: short sentences, concrete checks, no quotes or anecdotes.

## Structure

- `skills/architecture-constitution/SKILL.md`: the skill.
- `skills/architecture-constitution/references/`: the base constitution and the catalog.
- `scripts/check.py`, `tests/`: the consistency check and its tests. Standard library only.

## Working here

- One change per branch and pull request.
- Never weaken a test or a check to get green. Fix the cause, or say in the pull request why the check is wrong.
