# Contributing

This file is for a second team that works on the project beside the first: its contributor
and the Claude session that leads her team ("team B"). It also holds the rules for anyone
who opens an issue. **Read [`CLAUDE.md`](CLAUDE.md) first, all of it.** It is the binding
contract; this file points to it and does not restate it.

## What the project is

An open-source general insurance pricing platform for the UK/EU market: data preparation,
risk modelling (GLM and machine learning), rating algorithm design, scoring, monitoring and
governance. It is a Python and TypeScript monorepo. The specifications in `docs/` are the
contract the code is written against: read the spec for the area you change before you write
code. Start at [`README.md`](README.md), then [`docs/README.md`](docs/README.md).

## Issues

Bug reports, questions and suggestions are welcome: use a template in
`.github/ISSUE_TEMPLATE/`. The team triages a substantiated issue into the findings register
([`docs/findings/register.md`](docs/findings/register.md)), an open question or a task. After
that the issue points to the record that owns the work.

## Set up

You need Python 3.12, [`uv`](https://docs.astral.sh/uv/), Node 22 or later, `pnpm` and Docker.

```bash
uv sync --all-packages --dev
pnpm --dir frontend install --frozen-lockfile
docker compose -f deploy/docker-compose.yml up -d    # postgres, redis, minio
```

**`--all-packages` is not optional.** A plain `uv sync` installs only the dev tools, and
`mypy` and `pytest` then fail with `No module named 'pydantic'`.

**Backend tests need a database.** Set `GIP_TEST_DATABASE_URL` to a database made for tests
(compose credentials are `gipricing`/`gipricing`):

```bash
export GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/<your_test_db>
```

Without it, the tests look for a database named after your checkout and stop with an error
that prints its name. Each checkout needs its own test database, because the test teardown
empties it. The commands to create it (`createdb` runs inside the container) are in
[`.claude/skills/dev-commands/SKILL.md`](.claude/skills/dev-commands/SKILL.md), which also
lists the other setup traps.

## The gate

Run both halves before you push. A Python-only run has been green while the frontend was red.
Check each command's own exit code: `cmd | tail -1 && echo ok` reports the exit code of
`tail`, not of `cmd`.

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

## How the two teams work together

These rules (T1 to T6) are the maintainer's decision of 2026-10-08. They take effect when
team B starts.

- **T1. Team B owns whole Works, not shared slices.** A team-B Work is one whose code is
  disjoint from the first team's hot files. The proposed first Work is `WK-675` (the
  frontend), from slice S3 onward, after the first team's S2 merges. A question above team
  B's lead (a decision point, a scope move, a STOP) goes to the maintainer. **A team-B slice
  starts only on the maintainer's GO.** Request it in the coordination issue and list the
  slice's write set; the first team checks it against its own in-flight write sets. The
  slice's `LG-` quotes the GO.
- **T2. One merger, one id allocator: the first team's lead.** Team B never merges and never
  picks a minted id. At the merge turn, the lead posts "merge turn" on the PR, and the first
  team's finisher pushes **one** commit to your branch (the minted ids re-pointed and
  `docs/INDEX.md` regenerated, through "Allow edits by maintainers"). **From that comment
  on, team B pushes nothing more to the branch** until it merges or the lead hands it back:
  two writers on one branch are how a CI run was cancelled. The maintainer approves; the lead
  merges. Before the merge turn, team B writes **working ids from the block 7000 to 7999 only**, in the space
  form (`FD 7012`, not `FD-7012`). **The hyphen form is allowed only where a tool must read
  it:** the bold id cell of a requirement row and `@pytest.mark.req`. The first team's
  working ids stay at 9000 or above, so the two never collide.
- **T3. Every team-B PR needs the maintainer's approval (a MERGE-ACK), with the same evidence
  as the first team's.** Put it in the PR, or a comment on it:
  1. the full head SHA;
  2. the `git merge-tree` result and its tree, against `origin/main`;
  3. `git diff --name-status origin/main...<branch>`;
  4. the gate's exit-code table, with the pytest totals;
  5. CI for each workflow, read from its log, not only the green check. Rely only on runs
     **completed with success**, read per workflow: a cancelled run is not green. Push nothing
     to the branch while a run the approval relies on is in flight;
  6. a count of zero for the one word the repository bars in added text (the charter files
     in `.claude/roles/` name it).

  The rule is `.claude/roles/lead.md` rule 4: no merge without the approval, and an approval
  is valid only against the `main` it names. If `main` moves, ask again.
- **T4. The channel is GitHub only.** Use the one pinned coordination issue for questions and
  STOPs. Put an approval request as a comment on the PR itself. The first team's watcher
  polls GitHub and relays; the lead reads each PR before asking for an approval. Never put a
  Claude session link in GitHub.
- **T5. Shared limits.** Keep **under 30 open PRs across both teams**. A new governed-record draft
  is a pushed branch with **no PR**; a PR is opened for a slice, an activation or an urgent
  fix, or as a batch the first team's lead asks for. Run **one full gate at a time per
  machine**: do not start a second gate, or a heavy check, beside a running one. Until the
  P2 exit demo, a finding about the process itself is a dated row in
  [`docs/process/process-backlog.md`](docs/process/process-backlog.md), not an `FD-`. The
  exception: it lets a wrong merge, a wrong number or data loss through, or it blocks work
  today.
- **T6. Start from a fork.** Push to your fork and open PRs from it with **"Allow edits by
  maintainers" on**, so the first team's finisher can push the mint commit to your branch.
  The maintainer approves the first run of the Actions workflows. Collaborator access is
  reconsidered after a trial.

## What a slice PR contains

One PR is one slice. It holds the code; the tests, written first and seen to fail (red) before
the code makes them pass (green); any spec change the code needs; and the slice's one status
change in its `SL-` row of `docs/roadmap.md`, plus one ledger file, an `LG-` under
`docs/ledgers/` (template: `docs/_templates/LG.md`). A capability the spec does not yet cover
needs a spec change first: follow `.claude/skills/spec-change`. Commits use
[Conventional Commits](https://www.conventionalcommits.org/); a PR title names its slice
(`SL-<n>: <title>`). The first team mints your ids and regenerates `docs/INDEX.md` in
its one mint commit at the merge turn (T2). The PR template asks for evidence: name the command, its totals and the tree
it ran against, never "tests pass".

## Never edit by hand

| Path or thing | Why |
|---|---|
| `docs/contracts/` | Generated from the `model-schema` package. Run `uv run python scripts/generate-contracts.py`; CI fails on drift. |
| `docs/INDEX.md` | Generated index of every governed document. The first team regenerates it at the merge turn. |
| `docs/findings/register.md` | Rows are added only by the first team's minter or auditor. If your batch touches it, the first team merges the rows at the merge turn. |
| `frontend/src/api/generated` | Generated from the OpenAPI contract by `pnpm --dir frontend generate:api`; not committed. |
| A minted id (`FD-`, `RL-`, `SL-`, `LG-`, a requirement id) | Ids are permanent and come from one sequence, held by the first team's lead (T2). Never renumber or reuse one. |

A filed plan under `docs/plans/` is frozen at its date. Do not edit it. **A merged governed
record is frozen too:** only `status:`, `superseded_by:` and `corrected_by:` may change. A
correction is a new correcting record.

## Rules that bind every change

These are in `CLAUDE.md`, by pointer only:

- **Spec first** (§0). Where code and spec disagree, stop and ask.
- **Money is never a float** (§7): integer pence or cents, or `Decimal` in the rating path.
- **Vue 3 Composition API with `<script setup lang="ts">` only** (§3).
- **No pandas in new code**, except at an unavoidable library boundary (§3).
- **Never hand-write a shape that exists in `model-schema`**, or an API type (§2, §3).
- **A Work, Phase or Project close is accepted by the maintainer** (§13).

The delivery process is [`docs/process/delivery-process.md`](docs/process/delivery-process.md);
the term definitions are in [`docs/specs/00-overview.md`](docs/specs/00-overview.md).
