# Contributing

Thank you for helping. This project is small on purpose, and a small, focused change is the easiest to review.
Taking part in this project means following the [Code of Conduct](CODE_OF_CONDUCT.md).

## Set up

Clone the repository and run `make check`. It needs Python 3.10 or newer and nothing else.

## A good first contribution

- **A sharper check.** Many principles name a tool for one stack. A tool for another stack (a linter rule, an
  import contract, a schema diff) in the principle's `Check` column helps everyone on that stack.
- **A conflict the catalog misses.** Two principles that pull apart in practice, added to both rows' `Conflicts`.
- **A report of the skill going wrong.** A constitution it wrote that didn't fit, or a review that missed or
  invented a finding. Describe it with an invented repository.

A new principle or article, or a change to the profiles, changes what every user's agents are told. Open an issue
first so that we can agree on it before you write it.

## Rules a change must keep

[AGENTS.md](AGENTS.md) lists them: stable principle numbers, rule, why, check and conflicts for every principle,
one fact in one place, and invented examples only. `make check` fails when references, ranges, counts or links
drift.

## Open a pull request

One change per pull request. In the description, say:

- **What** changed.
- **Why**: the problem or the need.
- **How you checked**: `make check`, and anything else you ran.

Never weaken a test or a check to get green. If a check is wrong, say why in the pull request.

## License

The project is under the Apache-2.0 license (see [LICENSE](LICENSE)). By submitting a contribution you license it
under the same terms, as section 5 of the license says. There is no separate agreement to sign.
