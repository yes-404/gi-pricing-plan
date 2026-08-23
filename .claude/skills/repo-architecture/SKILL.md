---
name: repo-architecture
description: How this monorepo is laid out and why — the annotated tree, the polyglot component map and why CI is path-filtered into three workflow files, the one-way model-schema → docs/contracts → frontend seam and why the generated contract is published under docs/ rather than treated as a build output, how the specification and the code are held consistent by audit-docs.py and req-coverage.py, and the stack choices decided against that bind when a dependency is chosen (no statsmodels, no pandera, monotonic constraints on both boosters, what mypy --strict covers). Use when adding a component or a dependency, adding or changing a CI workflow, deciding where a shared shape belongs, or wondering why a generated artifact is committed. CLAUDE.md §2 and §3 carry the rules; this carries the tree and the reasons.
---

# Why the repository is shaped this way

`CLAUDE.md` §2 states the rules — where status lives, the three layout entries that carry
one, the one-way seam, the standing architecture rules — and §3 the three stack
prohibitions a session breaks by default. This file is the tree itself and the reasoning
behind all of them, kept out of the file that loads into every session.

## The annotated layout

`CLAUDE.md` §2 carries the bare tree. This is the same tree with what each entry is for.
**Component status — what exists, what is partial, what is scheduled — is not here and not
there: it belongs to `docs/roadmap.md` §6 and only there**
([`NT-0003`](../../notes/0003-duplicated-status-goes-stale.md)).

```
/
├── CLAUDE.md               phase, conventions, binding rules — loaded into every session
├── LICENSE                 Apache-2.0 (OQ-OVR-2)
├── alembic.ini             migrations — dev-commands has the DSN it does *not* default to
├── pyproject.toml          uv workspace root; ruff, mypy, pytest config
├── uv.lock                 COMMITTED — a lockfile, not an environment
├── .importlinter           ADR-0001/0002/DEP-3 — 3 contracts, enforced in CI
├── .gitignore              see .claude/skills/git-hygiene
├── .github/workflows/      python.yml · frontend.yml · docs.yml, path-filtered
│
├── docs/                   the specification suite — authoritative
│   ├── README.md           the fuller index of the suite (CLAUDE.md §4 is the one-line version)
│   ├── specs/              00–07, the contract code is written against
│   ├── workflows/          wf-01…05, the end-to-end journeys
│   ├── adr/                architecture decisions
│   ├── contracts/          JSON Schema + OpenAPI, generated from model-schema, published
│   ├── research/           spike findings, with what each one changed
│   ├── plans/              filed implementation plans and their execution ledgers
│   ├── roadmap.md          phases, workstreams, decision gates, component status
│   ├── open-questions.md   every unresolved choice, gated by phase
│   ├── skills-map.md       stack component → where used → skills
│   └── phase-0-status.md   what the specification phase closed with
│
├── packages/model-schema/  shapes crossing a boundary (ADR-0002)
├── packages/pricing-core/  progress + money + the data/ maths, and modelling/: factors,
│                           bandings, groupings, GLM, GBM, diagnostics, transparency,
│                           custom objectives
├── backend/                API + worker: jobs, blobs, auth, RBAC, approvals, datasets,
│                           validation, profiling, reference, the demo guide,
│                           factors/bandings/groupings/models, GBM fits, transparency
│                           artifacts and custom objectives
├── pipelines/              scheduled ingestion (07 FR-PLAT-61)
├── frontend/               Vue 3 SPA — the routed views, /demo, the factor workbench
├── examples/               freMTPL2 seed
│
├── deploy/                 compose stack
├── tests/                  repository invariants — enforcement the audit can see
├── scripts/                audit-docs · req-coverage · scope-audit · generate-contracts ·
│                           bench-data · bench-model · demo · graphify-docs-extract
├── .claude/notes/          maintainer notes, `NT-NNNN` (audit-docs checks them)
├── .claude/skills/         project procedures, written and vendored
└── .claude/agents/         delegable specialists — own context, not the turn's
```

Three entries carry a rule rather than a description, and those stay in `CLAUDE.md` §2:
`uv.lock` is committed, `docs/contracts/` is never hand-edited, and a filed plan under
`docs/plans/` is frozen at its date (`docs/plans/README.md` has that rule and the four
conventions that keep a plan passing the audit).

## It is a polyglot monorepo, and neither language is the main one

Python and TypeScript live side by side. The root `pyproject.toml` configures Python
tooling only; it does **not** make the repository a Python project. `frontend/` carries its
own `package.json` and `tsconfig.json`, and those are the authority for the TypeScript half.

| Component | Language | Governed by | Tooling config | CI workflow |
|---|---|---|---|---|
| `packages/model-schema` | Python | `00` §4.3, FR-OVR-1/6/7 | root `pyproject.toml` | `python.yml` |
| `packages/pricing-core` | Python | `02`–`05` — the maths | root `pyproject.toml` | `python.yml` |
| `backend/` | Python | `01`, `06`, `07` | root `pyproject.toml` | `python.yml` |
| `pipelines/` | Python | `01` ingestion, `05` scheduling | root `pyproject.toml` | `python.yml` |
| `frontend/` | TypeScript | each spec's §5.3 views | `frontend/package.json`, `tsconfig.json` | `frontend.yml` |
| `docs/` | Markdown | itself — the specification | — | `docs.yml` |
| `scripts/`, `.github/`, `deploy/`, `.claude/` | mixed | operational | — | as their target |

### Why three workflow files rather than one with three jobs

**GitHub applies `paths:` at workflow level, not per job.** A single workflow filtered on
the union of all paths would run every job for every change: a docs-only edit would resolve
Python dependencies and install pnpm, and each side would wait on the other's toolchain.
Splitting into `python.yml`, `frontend.yml` and `docs.yml` is what makes the filter
effective.

The consequence to remember when running the gate: **it has two halves**, and the Python
half has been green while the frontend half was red. `.claude/skills/dev-commands` has both.

## The seam between backend and frontend

One contract joins them, and it flows in one direction:

```
packages/model-schema      ← the single source of truth (ADR-0002)
        │  generated
        ▼
docs/contracts/            ← JSON Schema + OpenAPI 3.1, committed; CI fails on drift
        │  consumed                                        (FR-PLAT-48)
        ▼
frontend/src/api/generated ← openapi-typescript output, VCS-ignored, never hand-written
```

### Why the generated contract is committed, and why it lives under `docs/`

A generated artifact is normally a build output and normally ignored. This one is not,
for two reasons:

- **It is a published specification artifact.** External consumers read
  `docs/contracts/` to integrate against the platform. That makes it part of the
  specification suite, not a by-product of building it. FR-PLAT-48 pins the location.
- **Committing it is what makes drift detectable.** `generate-contracts.py --check`
  regenerates and compares; without a committed copy there is nothing to compare against,
  and a schema change could reach the frontend without anyone reviewing it.

The frontend's generated client is the opposite case: it is VCS-ignored, because it is a
consumer-side build output with no external reader. `pnpm generate:api` must run before
`type-check`, or the type-check passes against a stale or absent client — see
`.claude/skills/dev-commands`.

### Why nobody hand-writes a shape that already exists in `model-schema`

Not the backend, not the frontend, not a test fixture. A shape defined twice will diverge,
and **in a pricing platform a diverged shape is a mispricing** — the two sides agree about
a field's name and disagree about its type, its units or its nullability, and the disagreement
surfaces as a wrong premium rather than as an error.

`.claude/skills/contract-guard` covers the guard that catches this, including the section
on why a hand-copy of a shared shape is where divergence starts.

## How the specification and the code are held consistent

They are not parallel tracks that occasionally sync. **The specification is the contract
the code is written against.** Two scripts keep that honest, and both are in the gate:

- **`scripts/audit-docs.py`** — structural checks over the spec suite: requirement IDs,
  cross-references in both directions, dependency direction, glossary single-sourcing,
  money discipline, schema validity. It also checks the `.claude/notes/` working notes,
  and the `docs/workflows/` journeys' citations against the interfaces the specs declare
  (FR-OVR-17).
- **`scripts/req-coverage.py`** — turns `@pytest.mark.req` marks into a report of which
  requirements the suite covers, failing when a test claims a requirement that does not
  exist. This is why the marker is checked rather than decorative.

Neither script can tell you *which side is wrong* when they disagree. That decision is
`CLAUDE.md` §0's, it stays in the main thread, and the answer has often been the spec:
spikes and implementation have found defects in it repeatedly, including one that would
have rejected every valid custom objective.

### Why a spanning change is one commit

A change that touches both the spec and the code lands as **one commit** — the spec change,
the code, the tests, and any skill update capturing a non-obvious procedure. Split them and
the spec merges while the code does not, or the reverse; `audit-docs.py` then reports a
consistency the repository does not have, which is worse than reporting none.

## The stack, and the choices already made against it

`CLAUDE.md` §3 carries the one-line stack and the three prohibitions a session breaks by
default when writing code — no pandas, no hand-written API types, no Options API.
`docs/skills-map.md` maps each component to where it is used and what to read, and each
spec's §8 names what that module depends on. The rest of the decided-against set lives here
because it binds when a *dependency* is chosen rather than on every keystroke.

**`statsmodels` is not a dependency and never has been.** `02-modelling.md` §8 names it for
FR-MODEL-51, but the type-III block was built on `glum` refits instead. That spec row is
stale, and correcting it is a `CLAUDE.md` §0 resolution — the record of which side was
believed — rather than a silent edit to either side.

**Dataset validation is not pandera.** It is a dedicated validation module over Polars:
`01-data-management.md` §3.3, with §4.4's catalogue of named rules, which records why. The
repository depends on pandera nowhere, and `phase-review`'s worked example is the one place
it is even scored.

**XGBoost and LightGBM are both used, and both need monotonic constraint support** — the
constraint is actuarially required in places, so a gradient booster without it cannot be
substituted for either. interpret/EBM covers transparent ML.

**`mypy --strict` covers `packages/*/src` *and* `backend/src`.** The backend half is easy to
omit when adding a path to the config; ruff runs at line length 100 over everything except
the vendored files.

## Verified

2026-08-23 — written when `CLAUDE.md` §2 was cut to its binding rules during the
restructure that took that file from 41 KB to under 15 KB. Every claim here was moved in
substance from §2 and §3; no reasoning is new. **Four rules did leave `CLAUDE.md`** — the
`statsmodels`, pandera, monotonic-constraint and `mypy --strict` scope decisions in "The
stack, and the choices already made against it". They bind when a dependency is chosen
rather than on every keystroke, which is why they are loaded on demand; §3 keeps the three
that a session breaks by default and points here for these. If that trade turns out wrong,
the fix is to move them back, not to restate them in both places.
