# Contributing

Thank you for looking. This file is for a person who wants to change the project. It says
how to set up, what must pass before you push, what you must never edit by hand, and who
decides what merges.

## What the project is

An open-source general insurance pricing platform for the UK/EU market: data preparation,
risk modelling (GLM and machine learning), rating algorithm design, scoring, monitoring and
governance. It is a Python and TypeScript monorepo, and the specifications in `docs/` are
the contract the code is written against. Start at [`README.md`](README.md), then
[`docs/README.md`](docs/README.md) (the map of the specification suite). Read the spec for
the area you change before you write code.

## Issues and pull requests

- **Issues are welcome.** Bug reports, questions and suggestions: use a template in
  `.github/ISSUE_TEMPLATE/`, or a blank issue.
- **Open an issue before a pull request.** If the change is wanted, the maintainer invites a
  PR, or the team picks it up. Unsolicited PRs may sit unmerged.
- **Every merge needs the maintainer's approval.** The team's agents never merge a
  contributor's PR without it.
- **Ask questions** in a GitHub issue, or as a comment on your PR.
- A substantiated issue is triaged by the team into the findings register
  ([`docs/findings/register.md`](docs/findings/register.md)), an open question or a task.
  After that the issue is a pointer to the internal record, so expect a link, not a running
  commentary.

## Set up

You need Python 3.12, [`uv`](https://docs.astral.sh/uv/), Node 22 or later, `pnpm` and Docker.

```bash
uv sync --all-packages --dev
pnpm --dir frontend install --frozen-lockfile
docker compose -f deploy/docker-compose.yml up -d    # postgres, redis, minio
```

**`--all-packages` is not optional.** The root project depends on no workspace package, so a
plain `uv sync` installs only the dev tools. `mypy` and `pytest` then fail with
`No module named 'pydantic'` in an environment that looks fine.

**Backend tests need a database.** Without `GIP_TEST_DATABASE_URL`, the tests look for a
database named after your checkout and stop with an error that prints its name if it does
not exist. Either set the variable to a database you made for tests:

```bash
export GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/<your_test_db>
```

or create the per-checkout database once (`createdb` runs inside the container; the compose
credentials are `gipricing`/`gipricing`). The name logic is `_worktree_database_name()` in
`backend/tests/conftest_db.py`; the exact commands are in
[`.claude/skills/dev-commands/SKILL.md`](.claude/skills/dev-commands/SKILL.md). Do not run
tests against a database another checkout also uses: the test teardown empties it.

## The gate

Run both halves before you push. A Python-only run has been green while the frontend was red.

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

Check each command's own exit code. For example, `cmd | tail -1 && echo ok` reports the
exit code of `tail`, not of `cmd`. `dev-commands` explains the other traps.

## What a slice PR contains

One PR delivers one slice of work. It holds:

- the code;
- the tests, written first and seen to fail before the code makes them pass (red, then
  green);
- any spec change the code needs. A capability the spec does not yet describe gets a spec
  change first. See `.claude/skills/spec-change` for the procedure.

The team adds the rest: the slice's ledger record (`LG-`), document ids and the generated
`docs/INDEX.md`. A change with no slice yet gets one at triage. Branches and PR titles name
the slice: `sl-<n>-<slug>` and `SL-<n>: <title>`. Commits use
[Conventional Commits](https://www.conventionalcommits.org/). The PR template asks for
evidence: name the command, its totals and the tree it ran against, not "tests pass".

## Never edit by hand

| Path or thing | Why |
|---|---|
| `docs/contracts/` | Generated from the `model-schema` package. Regenerate with `uv run python scripts/generate-contracts.py`; CI fails on drift. |
| `docs/INDEX.md` | Generated index of every governed document. |
| `frontend/src/api/generated` | Generated from the OpenAPI contract by `pnpm --dir frontend generate:api`; not committed. |
| Any minted id (`FD-`, `RL-`, `SL-`, `LG-`, requirement ids) | Ids are permanent and come from one sequence (`python3 scripts/doc-id.py next`). Never renumber or reuse one. |

A filed plan under `docs/plans/` is frozen at its date. Do not edit it.

## Rules that bind every change

These are in [`CLAUDE.md`](CLAUDE.md); read it. In short, and by pointer only:

- **Spec first.** A capability the spec does not cover needs a spec change before code
  (`CLAUDE.md` §0). Where code and spec disagree, stop and ask; do not make either match
  the other silently.
- **Money is never a float.** Integer pence or cents, or `Decimal` in the rating path
  (§7).
- **Vue 3 Composition API with `<script setup lang="ts">` only.** No Options API, no JSX
  (§3).
- **No pandas in new code**, except at an unavoidable library boundary (§3).
- **Do not hand-write an API type or a shape that already exists in `model-schema`** (§2,
  §3).

## Where to read next

[`docs/specs/00-overview.md`](docs/specs/00-overview.md) defines every term. The repository
layout and its reasons are in `.claude/skills/repo-architecture`, and the delivery process
the team follows is [`docs/process/delivery-process.md`](docs/process/delivery-process.md).
