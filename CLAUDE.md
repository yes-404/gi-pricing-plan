# CLAUDE.md — Open Source General Insurance Pricing Platform

This file gives Claude Code the context, conventions, and roadmap to develop this project
continuously and consistently. Read it fully before making changes.

## 0. CURRENT PROJECT PHASE: 1a — DATA WORKBENCH (read this before anything else)

**Phase 0 (Specification) closed 2026-08-14. Phase 1a is active, and writing application
code is now the expected default** for work inside its scope (§9).

The specification suite in `docs/` is the contract that Phase 1 builds against. It is
finished, audited, and authoritative: 8 module specs, 5 workflow journeys, 5 ADRs, and the
artifact contracts and numbered requirements they define. **Read the relevant spec before
writing the code that implements it** — the specs are precise enough that guessing is never the faster
path, and a divergence between code and spec is a defect in whichever is wrong.

### What this means for the default deliverable

| Request | Deliverable |
|---|---|
| Implement something inside Phase 1a's scope (§9) | **Code**, plus any spec change the implementation proves necessary |
| Add a capability not yet specified | **Spec change first**, then code — the spec is the design step, not paperwork |
| Something in a later phase (rating, optimisation, monitoring, governance UI) | **Spec change only.** Do not build ahead of the phase |
| A design choice the specs leave open | Record it in `docs/open-questions.md` with options and a recommendation; do not silently pick one |

When code and spec disagree, **stop and resolve it** rather than quietly making the code
match or the spec match. Which one is wrong is a real question, and this project's history
shows it is often the spec: five defects were found by running spikes against it — including
one that would have rejected every valid custom objective — and implementation has since
found more, among them a memory budget smaller than the interpreter and an invariant that
left a report's ordinary state unnamed.

Quietly changing one to match the other destroys the record of which was believed, which is
the thing a governed system cannot afford to lose.

### The rules that survive the phase change

- Requirement IDs are permanent (§5). Never renumber; append or mark superseded.
- **Counts that change are not written here.** `uv run python scripts/req-coverage.py`
  prints how many requirements exist and how many carry evidence. Two of the three totals
  this file used to state were stale within a fortnight, from requirements added the same
  afternoon — the same reason FR-PLAT-54 makes the demo guide derived rather than written.
- Every spec change runs `python3 scripts/audit-docs.py` before commit (21 checks).
- `.claude/skills/` holds the procedures for this repo; §12's maintenance rules apply.
- The retrofit-impossible foundations (`docs/roadmap.md` §5) land in Phase 1a. Audit writes
  share the caller's transaction, artifacts are immutable, money is integer minor units,
  `model-schema` is the single source of truth (§2). **These are not deferrable to a later
  phase** — retrofitting any of them is a rewrite, and Phase 1a is where they are cheap.

## 1. Project Mission

An open-source general insurance pricing platform for the UK/EU market — an alternative
to WTW Radar/Emblem. Full pricing lifecycle: data preparation → risk modelling (GLM/ML) →
rating algorithm design → deployment/scoring → monitoring → governance.

Primary users: pricing actuaries and analysts. Technical (Python/notebooks) but expect a
polished UI. All design decisions favour: reproducibility, auditability, transparency of
the maths.

## 2. Repository Layout (Monorepo)

`✔` exists · `◐` partial · `…` arrives in the phase shown.

```
/
├── CLAUDE.md                 ✔ this file — phase, conventions, roadmap
├── LICENSE                   ✔ Apache-2.0 (OQ-OVR-2)
├── .gitignore                ✔ see .claude/skills/git-hygiene
├── pyproject.toml            ✔ uv workspace root; ruff, mypy, pytest config
├── uv.lock                   ✔ COMMITTED — a lockfile, not an environment
├── .importlinter             ✔ ADR-0001/0002/DEP-3 — 3 contracts, enforced in CI
│
├── docs/                     ✔ the specification suite — still authoritative
│   ├── specs/                ✔ 00–07, the contract code is written against
│   ├── workflows/            ✔ wf-01…05, the end-to-end journeys
│   ├── adr/                  ✔ architecture decisions
│   ├── contracts/            ◐ JSON Schema + OpenAPI. `openapi/generated.json` and 6
│   │                           schemas are generated; ~20 are Phase-0 hand-written
│   ├── research/             ✔ spike findings, with what each one changed
│   ├── roadmap.md            ✔ phases, workstreams, decision gates
│   ├── open-questions.md     ✔ every unresolved choice, gated by phase
│   ├── skills-map.md         ✔ stack component → where used → skills (§10)
│   └── phase-0-status.md     ✔ what the specification phase closed with
│
├── packages/
│   ├── model-schema/         ✔ shapes crossing a boundary (ADR-0002)   [W1, W2, W4]
│   └── pricing-core/         ◐ progress + money + the `data/` maths, and `modelling/`:
│                               factors, bandings, groupings, GLM     [W1, W4, W5]
│
├── backend/                  ◐ API + worker: jobs, blobs, auth, RBAC, approvals,
│                               datasets, validation, profiling, reference,
│                               the demo guide, factors/bandings/groupings/models
│                                                     [W2✔ W3✔ W4✔ W7b✔ W5]
├── pipelines/                … Dagster ingestion and scheduling      [deferred to W7]
├── frontend/                 ◐ Vue 3 SPA — `01` §5.3's 7 views routed, plus `/demo`
│                               and `02` §5.3's factor workbench     [W6a✔ W7b✔ W5 W6b]
├── examples/                 ◐ freMTPL2 seed — data half done  [W7a✔] rest [1b W7]
│
├── deploy/                   ✔ compose stack verified, 21 s cold start    [W1]
├── tests/                    ✔ repository invariants — enforcement the audit can see
├── scripts/                  ✔ audit-docs · req-coverage · scope-audit · generate-
│                               contracts · bench-data · demo (§11 runs them)
├── .claude/notes/            ✔ maintainer notes, `NT-NNNN` (audit checks 16–20)
└── .claude/skills/           ✔ 39 skills — 12 written here, 27 external (§12)
```

### Component map — who owns what, and what CI runs

This is a **polyglot monorepo**: Python and TypeScript live side by side, and neither is
the "main" language. The root `pyproject.toml` configures Python tooling only; it does not
make the repository a Python project.

| Component | Language | Governed by | Tooling config | CI workflow |
|---|---|---|---|---|
| `packages/model-schema` | Python | `00` §4.3, FR-OVR-1/6/7 | root `pyproject.toml` | `python.yml` |
| `packages/pricing-core` | Python | `02`–`05` — the maths | root `pyproject.toml` | `python.yml` |
| `backend/` | Python | `01`, `06`, `07` | root `pyproject.toml` | `python.yml` |
| `pipelines/` *(deferred to W7)* | Python | `01` ingestion, `05` scheduling | root `pyproject.toml` | `python.yml` |
| `frontend/` | TypeScript | each spec's §5.3 views | `frontend/package.json`, `tsconfig.json` | `frontend.yml` |
| `docs/` | Markdown | itself — the specification | — | `docs.yml` |
| `scripts/`, `.github/`, `deploy/`, `.claude/` | mixed | operational | — | as their target |

**CI is path-filtered per component.** GitHub applies `paths:` at workflow level, not per
job, so each component gets its own workflow file. A docs-only change must not spend two
minutes resolving Python dependencies, and once the frontend lands neither side should wait
on the other's toolchain.

> **If branch protection is ever enabled**, do not mark a path-filtered workflow as a
> required check. A required check that does not run on a given PR blocks it forever. Add a
> always-running aggregator job instead.

### The seam between backend and frontend

One contract joins them, and it flows in one direction:

```
packages/model-schema      ← the single source of truth (ADR-0002)
        │  generated
        ▼
docs/contracts/            ← JSON Schema + OpenAPI 3.1, committed; CI fails on drift
        │  consumed                                        (FR-PLAT-48)
        ▼
frontend/src/api/generated ← openapi-typescript output, git-ignored, never hand-written
```

`docs/contracts/` living under `docs/` is deliberate rather than accidental: the contract
is a **published specification artifact** that external consumers read, not merely a build
output. FR-PLAT-48 pins it there. The frontend generates from it; it never defines types of
its own (`CLAUDE.md` §3).

**The rule that keeps this honest:** nobody hand-writes a shape that already exists in
`model-schema`. Not the backend, not the frontend, not a test fixture. A shape defined
twice will diverge, and in a pricing platform a diverged shape is a mispricing.

### How code and documents relate

They are not parallel tracks that occasionally sync. **The specification is the contract
the code is written against.** Two scripts keep that honest rather than aspirational:

- **`scripts/audit-docs.py`** — 21 checks: requirement IDs, cross-references, dependency
  direction, glossary single-sourcing, money discipline and schema validity over the suite
  (1–15), the `.claude/notes/` working notes (16–20), and the workflow journeys' citations
  against the interfaces the specs declare (21, FR-OVR-17).
- **`scripts/req-coverage.py`** — turns `@pytest.mark.req` marks into a report of which
  requirements the suite covers, failing when a test claims one that does not exist.

**When code and spec disagree, stop and resolve it — §0 has the rule and the reason.** The
document is not automatically the authority, and neither is the code.

### Working rhythm

A change that spans both lands as **one commit**: the spec change, the code, the tests, and
any skill update that captures a non-obvious procedure (§12). Splitting them means the spec
merges and the code does not, or vice versa — and the audit then reports a consistency the
repository does not have.

Standing architecture rules (already decided — do not reopen without an ADR):
- `pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis deps.
- `model-schema` is the single source of truth for shared data shapes; frontend types
  are generated from it. Never define a shared shape anywhere else.
- Model and rating definitions are declarative JSON artifacts, never pickled objects.

## 3. Tech Stack (specs must be written against this stack)

### Backend
- Python 3.12+ with `uv` workspaces; FastAPI + Pydantic v2; SQLAlchemy 2.x (async) +
  Alembic; PostgreSQL 16; Celery + Redis for long-running jobs
- Data engine: Polars (dataframes) + DuckDB (ad-hoc aggregation). No pandas in new code
  except at unavoidable library boundaries.
- GLM fitting: `glum` (primary), `statsmodels` (fallback diagnostics)
- **Gradient boosting: XGBoost (primary GBM) and LightGBM (secondary), both with
  monotonic constraint support.** interpret/EBM for transparent ML.
- **Custom objectives are a first-class capability**: user-defined objective and eval
  functions for XGBoost/LightGBM (gradient + hessian interface), and custom loss
  specifications where the standard families don't fit (e.g. Tweedie variance-power
  tuning, capped/large-loss-adjusted losses, asymmetric pricing losses). Specs must
  define how a custom objective is declared, validated, versioned, and audited — an
  arbitrary-code objective is a governance risk, so the spec must cover sandboxing or
  a restricted expression form.
- Dataset validation: a dedicated validation module over Polars
  (`01-data-management.md` §3.3, and §4.4's catalogue of 38 rules). **Not pandera** —
  §4.4 records why, and the repository depends on it nowhere
- Rating execution: GoRules ZEN Engine (JSON decision graphs) wrapped by pricing-core
- Ruff (line 100), mypy --strict on packages/, pytest + hypothesis

### Frontend
- Vue 3 Composition API (`<script setup lang="ts">` only), Vite, TS strict, Pinia,
  Vue Router, pnpm, Tailwind
- ECharts via vue-echarts (diagnostics), TanStack Table (factor/rate tables),
  Vue Flow (rating DAG designer)
- API client generated from OpenAPI (`openapi-typescript`); never hand-written types
- Vitest + Vue Testing Library; Playwright E2E later

## 4. Documentation Suite — the module map

**§2 has the layout.** This is what each document is *for*, which nothing else states in
one place.

| Spec | Covers |
|---|---|
| `00-overview.md` | System context, module map, glossary, the API conventions every module obeys |
| `01-data-management.md` | Ingestion, datasets, versioning, **the four-layer validation gate** |
| `02-modelling.md` | GLM, XGBoost/LightGBM, custom objectives, factors/bandings/groupings, diagnostics |
| `03-rating-engine.md` | Rating DAG, rate tables, scoring APIs |
| `04-optimisation.md` | Demand models, optimisation, GIPP checks |
| `05-monitoring.md` | Drift, PSI, A/E monitoring, dashboards |
| `06-governance.md` | RBAC, approvals, audit, model documentation |
| `07-platform.md` | Auth, jobs, blobs, deployment, environments, observability |

`workflows/wf-01…05` are the **cross-module journeys** — dataset-to-model, model-to-rating-
version, rate-change impact, deploy-and-monitor, custom-objective lifecycle. A module spec
says what one module does; a workflow says what actually happens, across all of them.

`contracts/` holds JSON Schema and OpenAPI **generated from `model-schema`** and committed;
CI fails on drift (FR-PLAT-48). It is a published artifact, not a draft — never hand-edit it.

`skills-map.md` maps stack component → where it is used → skills to research (§10).
`open-questions.md` carries every unresolved choice, gated by phase.

## 5. Spec Document Standard (every spec must contain these sections)

1. **Purpose & scope** — what the module does and explicitly does not do
2. **Concepts & glossary** — domain terms (must match §7 vocabulary)
3. **Functional requirements** — numbered `FR-<module>-<n>` for traceability
4. **Data contracts** — entities, fields, types, invariants; reference or define the
   JSON Schema in `docs/contracts/`
5. **Interfaces** — API endpoints (method, path, request/response shape), pricing-core
   function signatures, frontend views touched
6. **Workflows** — sequence of steps with actors (user / frontend / backend / worker /
   pricing-core); link to the relevant `docs/workflows/` journey
7. **Cross-module dependencies** — what this module consumes from and provides to others
8. **Tech dependencies** — which stack components it uses and for what (feeds
   `skills-map.md`)
9. **Non-functional requirements** — performance, audit, security where relevant
10. **Open questions** — mirrored into `docs/open-questions.md`

Requirement IDs are permanent: never renumber, only append or mark superseded.

## 6. Dataset Validation — *superseded by `01-data-management.md`*

This section was the **brief** for writing that spec, in the phase before it existed: "the
spec must define these layers…". It is now written, with 40 `FR-DATA` requirements, the
four layers in §3.3, and a catalogue of 38 named rules in §4.4 — all of them implemented.

A brief that outlives its deliverable becomes a second, vaguer statement of the same thing,
and the two drift. Read `docs/specs/01-data-management.md`.

The number stays here rather than being reclaimed: **section numbers are cited from twelve
other files** and behave like every other identifier in this repository (§5) — assigned
once, never renumbered, never reused.

## 7. Domain Model (shared vocabulary — use these names in every doc)

- **Dataset**: immutable versioned snapshot of policy/claims/exposure data; carries its
  validation report and status (`draft → validated → archived`).
- **Factor / Level / Banding / Grouping**: rating variables and their transformations;
  groupings are first-class auditable operations.
- **Model**: fitted statistical model for one peril/response. Types: `glm`, `xgboost`,
  `lightgbm`, `ebm`. Stores family/objective (including custom objective reference),
  link, offset, weights, factors, coefficients or booster artifact + GLM approximation,
  diagnostics, dataset reference, parent model (lineage).
- **Custom Objective**: named, versioned definition of a non-standard loss (declarative
  parameters or reviewed code), reusable across models, with its own approval status.
- **Peril structure → Risk Premium**: frequency × severity (or burning cost) per peril.
- **Rating Algorithm / Rate Table / Rating Version**: DAG of calculation steps; rating
  versions are immutable deployable bundles moving `draft → review → approved → live →
  retired`.
- **Scoring**: real-time (single quote, target p99 < 50 ms) and batch (portfolio
  re-rate, dislocation analysis).

Actuarial correctness defaults (specs must not contradict these):
- Frequency: Poisson (or NB), log link, exposure offset. Severity: Gamma, log link,
  claim-count weights. Burning cost: Tweedie (1 < p < 2), log link, exposure weights.
- XGBoost/LightGBM insurance use: `count:poisson` / `reg:gamma` / `reg:tweedie` (or
  custom objective) with exposure handled via `base_margin` (log-exposure offset);
  monotonic constraints where actuarially required; always accompanied by a
  transparency artifact (GLM approximation or SHAP-based factor summary).
- Standard errors / uncertainty surfaced with every estimate; money is integer
  pence/cents or Decimal in the rating path, never float.

## 8. skills-map.md — *folded into §10*

Its one binding instruction — **update `docs/skills-map.md` in the same PR as any spec
change that adds or alters a tech dependency** — is stated in §10 among the other document
rules, where a reader looking for "what must I update?" will actually find it. The examples
that filled the rest of this section were the file's own content, restated.

## 9. Roadmap — *the plan lives in `docs/roadmap.md`*

**Phase 1a — Data Workbench is current.** Exit: a freMTPL2 dataset version reaches
`validated`, having been through the failure loop at least once.

Everything else about the plan — the phase list, workstream rows, closure records, decision
gates, the retrofit-impossible list, and which workstreams are closed — is in
[`docs/roadmap.md`](docs/roadmap.md), and **only** there.

This section used to restate it. It went stale within a fortnight: it still described Phase
1a as though nothing had shipped, while the roadmap carried eight closure records it knew
nothing about. Status duplicated in two places disagrees, and the copy nobody updates is the
one that gets read first.

The two things worth keeping here, because they change how you work rather than what is
planned:

- **The retrofit-impossible foundations land in Phase 1a** (`docs/roadmap.md` §5) —
  audit-in-transaction, artifact immutability, integer money, the Job model,
  `model-schema` as SSOT. Not deferrable: retrofitting any of them is a rewrite.
- **Do not build ahead of the phase** (§0's table). A later phase's capability is a spec
  change, not code.

## 10. How You (Claude) Work

§0 decides the deliverable for a given request. The rules below apply to whichever it is.

- **Documents.** Before editing a spec, read `00-overview.md`, the target spec, and any
  workflow that references it.
  After editing, check cross-references in both directions and update `open-questions.md`
  in the same PR — and `docs/skills-map.md` whenever the change adds or alters a **tech
  dependency**, with every row citing at least one spec section or requirement id.
- Keep terminology exactly consistent with §7; if a new term is needed, add it to the
  glossary in `00-overview.md` first.
- Prefer precise, implementation-ready language: named entities, typed fields, numbered
  requirements, explicit status enums, sequence-of-steps workflows. Avoid vague phrases
  ("the system should handle…") — say who does what, with what data, and what changes.
- When a design choice is genuinely open, do not silently pick one: record options,
  trade-offs, and a recommendation in `open-questions.md` (or an ADR if it must be
  decided now).
- Small illustrative snippets (an XGBoost custom objective signature, a rule definition,
  a JSON contract example) inside specs are encouraged; full implementations are not.
- **Code.** `.claude/skills/python-package` and `python-test` hold the conventions. Run the
  full gate locally before pushing — `.claude/skills/reproducing-ci-locally` explains why
  "CI will tell me" is the expensive way to find out.
- All PRs: Conventional Commits, short-lived branches from `main`, squash-merge, branch
  auto-delete. `.claude/skills/git-hygiene` covers the traps.

## 11. Commands Reference

```bash
# Setup. --all-packages is not optional: the root sets `package = false` and depends on no
# member, so a plain `uv sync` installs the dev tools and none of the workspace packages —
# mypy and pytest then fail on `No module named 'pydantic'` in a venv that looks fine.
uv sync --all-packages --dev

# The gate — **both halves**. This repository is polyglot and CI runs two workflows;
# a "gate" that covers only Python has been green while the frontend was red.
#
# Python (.github/workflows/python.yml) and docs (docs.yml):
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py                # 21 checks over docs/ and .claude/notes/
uv run python scripts/req-coverage.py        # requirement traceability
uv run python scripts/generate-contracts.py  # regenerate; --check fails CI on drift

# Frontend (.github/workflows/frontend.yml). `--frozen-lockfile` from a clean
# `node_modules` is what CI does, and a populated one hides a missing dependency.
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api        # then type-check: the client is git-ignored,
                                        # so a diff against it can never fail
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build

# Read each command's **own** exit code. `cmd | tail -1 && echo ok` reports tail's, and
# has produced a false "clean" here more than once.

# Closure audit (§13 step 1): expected scope from the specs, then evidence.
uv run python scripts/scope-audit.py PLAT --sections 3.1,3.2,3.3,3.7,3.8
uv run python scripts/scope-audit.py DATA --endpoints    # §5.1 table vs the contract
uv run python scripts/scope-audit.py DATA --catalogue VR # a spec's named-item catalogue

# ADR-0001's promise, made usable (OQ-OVR-4, decided 2026-08-14). `pricing-core` is not
# published to PyPI in Phase 1 — publishing would force semver stability on an API still
# being discovered — so this is how a reviewer runs the maths outside the platform.
# From Phase 2 it publishes as `0.x` with an explicit no-stability-guarantee notice.
uv venv .venv-review && uv pip install --python .venv-review/bin/python \
    -e packages/pricing-core               # a reviewer's own venv or notebook kernel
#
# `uv venv` ships no pip, so a bare `pip install -e` fails with "No such file or
# directory" — use `uv pip install --python <venv>/bin/python`, or a `python -m venv`
# environment if pip is wanted inside it.

# The demo entrance (FR-PLAT-53). One command from a clean checkout to a browser: compose,
# migrations, freMTPL2 seeded through the real Job path, the API and the frontend, with a
# development identity for the seeded workspace. Ctrl-C stops everything it started.
uv run python scripts/demo.py                # then open http://localhost:5173/demo
uv run python scripts/demo.py --rows 60000   # a sample; the full seed is 678 013 rows
#
# It refuses outside local/dev, before starting anything — the whole path hangs off
# `dev_auth_enabled`, which is False by default and raises at startup in a deployed
# environment. There is no second switch to leave on.

# Local infrastructure (deploy/README.md has the credentials and ports).
docker compose -f deploy/docker-compose.yml up -d --wait
docker compose -f deploy/docker-compose.yml down
```

Arriving with the workstream that needs them:

```bash
# Worker and outbox relay (W2). The relay is what moves a committed job to the broker —
# without beat running, jobs stay `queued` and nothing explains why.
celery -A app.worker.entrypoint worker --queues compute,default,io,scoring
celery -A app.worker.entrypoint beat

# W6a setup. pnpm is not on this image and `corepack enable pnpm` fails on it, so the way
# in is `npm config set prefix ~/.npm-global && npm i -g pnpm`, with that bin on PATH.
# The frontend gate itself is above, with the rest of the gate.
pnpm --dir frontend dev                      # proxies /api to localhost:8000

# The API the frontend talks to. Compose brings up postgres/redis/minio only — there is no
# app container, because a Dockerfile for it is deployment (W14) rather than a dev loop.
GIP_DEV_AUTH_ENABLED=true uv run uvicorn app.main:create_app \
    --factory --reload --app-dir backend/src --port 8000

uv run alembic upgrade head                  # W2
```

## 12. Skills

Project-specific procedures live in `.claude/skills/`, versioned with the repo so they
travel with it. `.claude/skills/README.md` is the index — read it when starting work on an
unfamiliar part of the suite.

**Written for this repo:** `spec-change`, `docs-audit`, `close-workstream`, `phase-review`,
`adr-write`, `contract-schema`, `library-spike`, `git-hygiene`, `python-package`,
`python-test`, `fastapi-service`, `vue-frontend`.

**Vendored** from [`wdm0006/python-skills`](https://github.com/wdm0006/python-skills) (MIT,
security-reviewed 2026-08-14): `reproducing-ci-locally`, `security-audit`,
`testing-strategy`, `code-quality`, `secret-hygiene`.

**Vendored** from [`yes-404/vue3-skills`](https://github.com/yes-404/vue3-skills), a fork of
`vuejs-ai/skills` (MIT, security-reviewed 2026-08-15): `vue-best-practices`,
`vue-router-best-practices`, `vue-pinia-best-practices`, `vue-testing-best-practices`,
`vue-debug-guides`, `create-adaptable-composable`. Two of the eight were **not** taken —
`vue-jsx-best-practices` and `vue-options-api-best-practices` document approaches §3 has
decided against, and a skill teaching a rejected approach is worse than a missing one.

**Vendored** from [`obra/superpowers`](https://github.com/obra/superpowers) (MIT,
security-reviewed 2026-08-16, upstream v6.3.0): all fourteen — `using-superpowers`,
`brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`,
`dispatching-parallel-agents`, `systematic-debugging`, `test-driven-development`,
`verification-before-completion`, `requesting-code-review`, `receiving-code-review`,
`using-git-worktrees`, `finishing-a-development-branch`, `writing-skills`. These are
*process* skills — how work is approached — where the other two sets are subject matter.

**Vendored** from
[`OthmanAdi/planning-with-files`](https://github.com/OthmanAdi/planning-with-files) (MIT,
security-reviewed 2026-08-16, upstream v3.10.1): `planning-with-files` — plan state on disk
that survives `/clear`, compaction and session death. The English canonical skill only; the
six-language, eighteen-agent mirrors and the bundled Pi extension were not taken.

**Installed** from [`Graphify-Labs/graphify`](https://github.com/Graphify-Labs/graphify)
(Apache-2.0, security-reviewed 2026-08-16, CLI 0.9.45): `graphify` — the repository as a
traversable knowledge graph, triggered by `/graphify`. Unlike the three sets above it is
not hand-vendored: the skill payload is written by the tool's own
`graphify install --project --platform claude`, so it is refreshed by re-running that, not
by editing the files. Its output directory `graphify-out/` is git-ignored.

Two things the installer does are **deliberately not committed**, and re-running it
reintroduces both — `.claude/skills/README.md` has the detail and the reason:
its `PreToolUse` hooks carry an absolute path from the installing machine and belong in
`.claude/settings.local.json`, and its `## graphify` append to *this* file asserts a
knowledge graph exists that a fresh clone does not have. The conditional version lives in
`.claude/CLAUDE.md`.

**The semantic pass over docs, PDFs and images calls a configured LLM provider.** Code
extraction is local tree-sitter and always safe; the semantic pass must never be pointed at
real policy, claims or exposure data. `examples/`'s freMTPL2 is public and is the exception.

All vendored skills are kept as upstream wrote them and excluded from `ruff` — with one
recorded exception. `planning-with-files`' five hook commands search `${CLAUDE_SKILL_DIR}`,
`~/.claude/skills/` and `~/.claude/plugins/marketplaces/`, none of which reaches a
project-level `.claude/skills/` checkout, so as shipped the hooks register and silently do
nothing. Each gained one `$CLAUDE_PROJECT_DIR/...` fallback, and the body's
`${CLAUDE_PLUGIN_ROOT}` became `${CLAUDE_SKILL_DIR}`. `.claude/skills/README.md` carries the
evidence, including why substitution does not reach a hook command string.

`.claude/skills/README.md` is the index and records why each was added.

### Precedence — superpowers first

**When a superpowers skill and any other skill both apply, follow the superpowers one.**
It sets the *approach*; the others supply this repository's *facts*. Upstream's
`using-superpowers` states the same rule from its own side — process skills before
implementation skills — but it also says user instructions outrank skills, so the rule
only actually binds by being written here.

The order to work in:

1. **`using-superpowers`** — the router. Read it when a task starts.
2. **The superpowers process skill for the shape of the work** — `brainstorming` before
   creative work, `systematic-debugging` before any fix, `writing-plans` /
   `executing-plans` / `subagent-driven-development` for multi-step work,
   `test-driven-development` before implementation code, and
   `verification-before-completion` before claiming anything passes.
3. **This repo's skill for the specifics** — it carries the paths, commands, requirement
   ids and conventions a general skill cannot know.

The one carve-out is narrow and factual, not a licence to prefer the local skill: where
superpowers gives a *procedure* and a repo skill states a *fact about this repository*,
the fact wins, because superpowers does not contain it and cannot. `git-hygiene`'s
`.gitignore` rules and squash-merge-with-auto-delete flow, `python-test`'s
`@pytest.mark.req` markers and §11's gate commands are facts of that kind —
`finishing-a-development-branch` still decides *how* a branch ends.

Nothing in superpowers overrides §0, §5 or §13. The phase table, permanent requirement
ids and the closure standard are this project's contract, not a default behaviour a
general skill is entitled to replace.

### Skill maintenance rules

- After completing any task, if you discovered a non-obvious procedure (build quirk, test
  setup, data format rule, deploy step), write or update a skill in `.claude/skills/`
  capturing it — then update `.claude/skills/README.md` and commit both together with the
  work.
- If a documented skill turns out to be wrong or outdated during a task, **fix the skill in
  the same session** and refresh its `Verified` date. Never leave a known-stale skill in
  place.
- Once a month (or when the maintainer says "skill audit"): re-check installed external
  skills for upstream updates, re-run the gap analysis from the project's current state,
  and propose additions/removals — but **never install external skills without the
  maintainer's approval**.
- Never modify skills under `~/.claude/skills/` (personal/global) as part of project work;
  project knowledge belongs in `.claude/skills/` so it travels with the repo.

## 13. Workstream Closure Standard

A workstream is closed only when every item below is true **and recorded in
`docs/roadmap.md`**. Closing without this produces a roadmap that reports progress the
repository does not have.

The procedure is in `.claude/skills/close-workstream`; this section is the standard it
implements.

### 1. Derive the expected scope from the specification — before looking at anything built

**Enumerate what the specification requires, then search for evidence of each item.** In
that order, and never the reverse.

Auditing from what was built can only confirm what was built. It is silent about everything
the workstream was supposed to cover and did not, which is precisely the part a closure
record exists to state. The same applies to recollection: an audit that begins "I
implemented jobs, blobs and settings" has already chosen its own answer.

```bash
# Sections a workstream's named areas cover, plus any individual requirements it owns.
uv run python scripts/scope-audit.py PLAT --sections 3.1,3.2,3.3,3.7,3.8 \
    --extra FR-PLAT-47,FR-PLAT-48
```

Both of its inputs are documents — requirements from `docs/specs/`, evidence from
`@pytest.mark.req` markers — so the result does not depend on who runs it. It exits non-zero
while any in-scope requirement lacks evidence.

**It is a closure tool, not a CI gate.** Most requirements belong to phases that
have not started, so running it unscoped will always fail; that is the correct behaviour for
an audit and the wrong behaviour for a build.

**Reconcile the derived count against the roadmap's claim; a disagreement is itself a
finding.** W2's row said "~35 of 60 `PLAT` requirements" and the sections it names total
exactly 35 — but the spec holds 61, not 60, because FR-PLAT-51 was appended after that row
was written.

**Every requirement without evidence needs a verdict**, one of: delivered but untested,
deferred with an owner, reassigned to another workstream, or not started. Silence is not
one of them. An independent audit of W2 found six unevidenced in-scope requirements where
the roadmap acknowledged two, and four of the six were mentioned nowhere in the
documentation at all.

**A marker is a claim, not a proof.** It says a test asserts *something* about a
requirement, not that it covers it. Read the ones that matter.

**Requirement coverage is not interface coverage, and not catalogue coverage.** Markers sit
on unit and service tests, so a module can satisfy every requirement it owns and still
expose no HTTP route — W4 stood at 49 of 50 requirements with **0 of 28** endpoints
published, and nothing said so. A requirement can also *summarise* a catalogue it does not
enumerate: FR-DATA-16 says "validation covers four layers", which one test evidences
honestly, while `01` §4.4's catalogue of 38 named rules behind it stood at 12.

Both are now derivable, and the same audit answers them:

```bash
uv run python scripts/scope-audit.py DATA --endpoints --catalogue VR
```

The endpoint check compares the spec's §5.1 table against the **published contract** rather
than the running app, because the contract is the artifact external consumers read. The
catalogue check scans **source only** — it counted a rule named nowhere but in a test as
implemented until a deliberately-broken run failed to notice a deleted id, which is the
inversion of what the check exists for.

**Evidence is not only markers.** A requirement can be enforced by an import-linter
contract, a database privilege, a migration, or a recorded measurement — none of which the
script can see, so all of which read as unevidenced. Re-auditing W1 reported half its scope
missing while the enforcement was working perfectly in CI, because W1's whole deliverable
*is* enforcement machinery.

The answer is to make the enforcement visible rather than to trust it silently: a test that
runs the check and names the requirement (`tests/test_repository_invariants.py`) links the
two, so the audit finds it. Where a test genuinely is the wrong instrument — NFR-PLAT-4
would have CI start containers to assert a number that varies with the runner — record the
measurement and say why it is not a test.

### 2. Deliverables — audited against the definition, not memory

Re-read the workstream's row in `roadmap.md` §6 and check each named deliverable **exists
and works**. Those are different claims: W1's compose file existed for days before anyone
ran it, and NFR-PLAT-4 was unverified the whole time.

### 3. Gates — all green, run locally with the real toolchain

**§11 has the commands**, both halves, and closing a workstream runs all of them — with
`generate-contracts.py --check` rather than the plain regenerate, because at closure the
question is whether the committed contract already matches, not whether it can be made to.

Run them **locally**, not merely "CI passed". CI proves the runner; local proves the result
is reproducible and that you can debug it — and read each command's own exit code, for the
reason §11 gives.

### 4. Enforcement is proven, not assumed

Any check the workstream introduces must be shown to **fail on deliberately broken input**
before it is trusted. A silently-passing check is worse than no check, because it is
mistaken for coverage.

*This is not hypothetical.* The import-linter config was dead for a day — `root_packages`
was comma-separated on one line, so the parser split it into characters — and it reported
success the whole time, while the contract enforcing ADR-0001 checked nothing.

**A generated artifact matching its source proves neither is correct.** W2's contract drift
check passed while the published OpenAPI advertised an error model the platform never emits
and omitted the one it does — the contract faithfully described the code, and both were
wrong together. Check generated output against the **requirement**, not only against the
thing it was generated from.

### 5. NFRs — measured, not asserted

If the workstream claims an NFR, record **the measurement and the budget**: "21 s cold
start against NFR-PLAT-4's 300 s", never "starts quickly". An unmeasured NFR is an opinion.

### 6. Scope honesty — state what was *not* delivered

Every requirement from step 1 that has no evidence appears here with its verdict and its
owner. So does §5 of the roadmap, the retrofit list: which items landed, which are
type-level only, and which workstream owns the remainder.

"Partial" is an acceptable verdict and often the honest one — but say *how* it is partial.
FR-PLAT-14's retention window is a declared setting with the 13-month floor enforced, while
nothing purges beyond it; the floor therefore holds by default rather than by design, and
recording only "delivered" would have hidden that.

**"W1 closed" must not be readable as "the retrofit list is handled."** It was not, and
that list is the one thing this project cannot fix cheaply later.

### 7. Documents updated in the same PR

The roadmap status table and closure evidence; `CLAUDE.md` §2's layout marks; and any spec
the implementation proved wrong — when code and spec disagree, resolve it rather than
quietly changing one (§0).

**And the demo guide** (FR-PLAT-54). It exists, and it is **derived at request time** from
the specs' §5.3 view tables, the frontend router, the published contract and this
roadmap's status table — so it cannot describe the previous state, and there is nothing to
update. What a closure must do instead is *check that it still derives*: a renamed spec
heading or a restructured status table breaks the derivation silently, and a guide that
lost a section reads as a platform that lost a capability.

`uv run pytest backend/tests/test_demo_guide.py` is that check, and it runs in the gate.

### 8. Repository clean

No open PRs for the workstream; no tracked build artifacts; branch deleted after merge —
**verify by content** (`git diff --stat main <branch>`), because squash-merge rewrites
history and `git branch -d` refuses even when the work is fully merged.

### Tests that must exist before closing

- A **negative test for every invariant** the workstream introduced. For a governed system
  the suite must prove the wrong thing *cannot* happen, not that the right thing can.
- A `@pytest.mark.req` marker on each test, naming the requirement it satisfies.
- A round-trip or property test wherever the workstream persists or transforms data.

---

## 14. Phase Review Standard

§13 audits **one workstream against its own scope**. Nothing there audits **the plan** —
whether the phase boundaries, the workstream cuts and the requirement set still make sense
now that some of the work is real.

The roadmap was written before any application code existed, and code has since contradicted
it more than once: W4's `pipelines/` mark, six `PLAT` endpoints missing from a closed
workstream, a spec that required a version timeline and offered no way to fetch one. Treat
the plan as a working hypothesis and re-test it **while the phase is still open**, early
enough that the answer can change what the phase does.

*(Raised by the maintainer as `NT-0001`, 2026-08-15. The note is the raw material; this
section is the standard.)*

### When

At **each workstream close**, and again **before a phase's exit demo**. A fixed trigger, not
"sometime" — a review that happens when someone remembers is one that happens after the
mis-cut is expensive.

### The five questions, in this order

1. **Completion.** Which of the phase's planned tasks are actually done — derived from the
   specs, then evidenced, never from recollection. **This is §13's machinery, not a second
   audit:** `scope-audit.py` with `--sections`, `--endpoints` and `--catalogue`, plus
   `req-coverage.py`. If it disagrees with the roadmap, the disagreement is the finding.
2. **Omission.** What the phase plainly needs that no workstream row names. Distinct from
   unfinished work: `pipelines/` was marked 1a W4 and belonged to W7; the blob endpoints
   were declared in `07` §5.1 and owned by nobody. Both were absent from the plan rather
   than behind schedule.
3. **Skills and research.** Which entries `docs/skills-map.md` and `.claude/skills/README.md`
   are now missing, and which have gone stale against the code. **Re-run the gap analysis**
   rather than appending to a list — a list only ever grows.
4. **Specification accuracy — the review's main target, not a tidy-up.** Whether each
   module spec still describes the code that was written against it: the §5.1 endpoint
   tables *in both directions*, the §5.2 signatures, the §5.3 view Contents columns, the
   named catalogues, and the params a caller would copy from the page. Then
   `docs/roadmap.md`, `docs/open-questions.md` and §2's layout marks.

   **The spec is where a stage's findings land**, because it is what the next stage is
   built against: a divergence left in it is a defect the next workstream inherits and
   builds on. The first audit to look found pandera named as the structural mechanism in
   four places while being a dependency of nothing, a rule-format table whose params would
   make an authored rule fail, and a reference publish lifecycle that existed in the
   database, the API and no document — which is why the endpoint audit reported a complete
   surface, since it compares the spec against the contract and an endpoint missing from
   both is invisible to it.

   **Resolve, never soften** (§0). Where the code is right, amend the spec with a dated
   note saying which side was wrong and why. Where the *spec* is right and the code does
   not meet it, the spec gains the precise obligation — an appended requirement, an owner,
   and a verdict — rather than being edited down to what was built. FR-DATA-41 and
   FR-DATA-42 are what that looks like.
5. **Shape.** Whether the remaining phases, workstreams and requirements are still cut in
   the right place — split, merge, add, or supersede.

### Four rules that keep a review a review

- **The output is a proposal, never a change.** Recommendation, rationale, and an explicit
  maintainer acceptance line with a date — the precedent the 1a/1b split set. A review that
  edits the roadmap on its own authority is re-planning, not reviewing.
- **Requirement IDs are permanent** (§5). "Remove a requirement" means *mark superseded*;
  renumbering is never the answer. An accepted ADR is amended by addendum, not edited.
- **A later phase's finding is a spec change only** (§0's table). It does not become work
  now because a review noticed it — mid-phase re-planning is how scope churn and building
  ahead of the phase both start.
- **Every question gets a written answer, "no change" included.** A silent question is
  indistinguishable from one nobody asked.

### Output

Proposals land in `docs/roadmap.md` and `docs/open-questions.md`, each either accepted with
a date or recorded as an open question with options and a recommendation.

It has now run twice — reviews 1 and 2, both 2026-08-15 — so the procedure **is**
`.claude/skills/phase-review`, alongside `close-workstream` (§12). This section stays the
standard; the skill is how to satisfy it, including what each of the two runs actually
found, which was in neither case what the question's author expected.
