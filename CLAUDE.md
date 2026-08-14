# CLAUDE.md — Open Source General Insurance Pricing Platform

This file gives Claude Code the context, conventions, and roadmap to develop this project
continuously and consistently. Read it fully before making changes.

## 0. CURRENT PROJECT PHASE: 1a — DATA WORKBENCH (read this before anything else)

**Phase 0 (Specification) closed 2026-08-14. Phase 1a is active, and writing application
code is now the expected default** for work inside its scope (§9).

The specification suite in `docs/` is the contract that Phase 1 builds against. It is
finished, audited, and authoritative: 8 module specs, 5 workflow journeys, 5 ADRs, 31
artifact contracts, 417 numbered requirements. **Read the relevant spec before writing the
code that implements it** — the specs are precise enough that guessing is never the faster
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
shows it is often the spec — five specification defects were found by running spikes against
it, including one that would have rejected every valid custom objective.

### The rules that survive the phase change

- Requirement IDs are permanent (§5). Never renumber; append or mark superseded.
- Every spec change runs `python3 scripts/audit-docs.py` before commit (14 checks).
- `.claude/skills/` holds the procedures for this repo; §12's maintenance rules apply.
- The retrofit-impossible foundations (`docs/roadmap.md` §5) land in Phase 1a. Audit writes
  share the caller's transaction, artifacts are immutable, money is integer minor units,
  `model-schema` is the single source of truth. **These are not deferrable to a later
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
│   ├── contracts/            ✔ JSON Schema + OpenAPI (generated from Phase 1)
│   ├── research/             ✔ spike findings, with what each one changed
│   ├── roadmap.md            ✔ phases, workstreams, decision gates
│   └── open-questions.md     ✔ every unresolved choice, gated by phase
│
├── packages/
│   ├── model-schema/         ✔ shapes crossing a boundary (ADR-0002)   [W1, W2]
│   └── pricing-core/         ◐ skeleton only — progress + money        [W1]
│
├── backend/                  ◐ API + worker: jobs, audit, blobs, auth, settings [W2 ✔]
├── pipelines/                … Dagster ingestion and scheduling           [1a W4]
├── frontend/                 … Vue 3 SPA                                  [1a W6a]
├── examples/                 … freMTPL2 demo dataset and seed             [1b W7]
│
├── deploy/                   ✔ compose stack verified, 21 s cold start    [W1]
├── scripts/                  ✔ audit-docs.py, req-coverage.py
└── .claude/skills/           ✔ 13 skills — 8 written here, 5 vendored (§12)
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
| `pipelines/` *(W4)* | Python | `01` ingestion, `05` scheduling | root `pyproject.toml` | `python.yml` |
| `frontend/` *(W6a)* | TypeScript | each spec's §5.3 views | `frontend/package.json`, `tsconfig.json` | `frontend.yml` *(add with the code)* |
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

- **`scripts/audit-docs.py`** — 14 checks over the suite: requirement IDs, cross-references,
  dependency direction, glossary single-sourcing, money discipline, schema validity.
- **`scripts/req-coverage.py`** — turns `@pytest.mark.req` marks into a report of which
  requirements the suite covers, failing when a test claims one that does not exist.

**When code and spec disagree, stop and resolve it** (§0). Which is wrong is a real
question: five specification defects were found by running spikes against the specs, so the
document is not automatically the authority — but neither is the code, and quietly changing
one to match the other destroys the record of which was believed.

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
- Dataset validation: `pandera` schemas + a dedicated validation module (see §6)
- Rating execution: GoRules ZEN Engine (JSON decision graphs) wrapped by pricing-core
- Ruff (line 100), mypy --strict on packages/, pytest + hypothesis

### Frontend
- Vue 3 Composition API (`<script setup lang="ts">` only), Vite, TS strict, Pinia,
  Vue Router, pnpm, Tailwind
- ECharts via vue-echarts (diagnostics), TanStack Table (factor/rate tables),
  Vue Flow (rating DAG designer)
- API client generated from OpenAPI (`openapi-typescript`); never hand-written types
- Vitest + Vue Testing Library; Playwright E2E later

## 4. Documentation Suite (the deliverable of this phase)

```
docs/
├── adr/                        # Architecture decision records (numbered)
├── specs/
│   ├── 00-overview.md          # System context, module map, glossary
│   ├── 01-data-management.md   # Ingestion, datasets, versioning, VALIDATION
│   ├── 02-modelling.md         # GLM, XGBoost/LightGBM, custom objectives,
│   │                           #   factors/bandings/groupings, diagnostics
│   ├── 03-rating-engine.md     # Rating DAG, rate tables, scoring APIs
│   ├── 04-optimisation.md      # Demand models, optimisation, GIPP checks
│   ├── 05-monitoring.md        # Drift, PSI, A/E monitoring, dashboards
│   ├── 06-governance.md        # RBAC, approvals, audit, model documentation
│   └── 07-platform.md          # Auth, jobs, deployment, environments
├── workflows/                  # ★ Cross-module, end-to-end user journeys
│   ├── wf-01-dataset-to-model.md
│   ├── wf-02-model-to-rating-version.md
│   ├── wf-03-rate-change-impact.md
│   ├── wf-04-deploy-and-monitor.md
│   └── wf-05-custom-objective-lifecycle.md
├── contracts/                  # Draft API + schema definitions (OpenAPI stubs,
│                               #   JSON Schema for model/rating artifacts)
├── skills-map.md               # Tech stack → skills/knowledge needed (see §8)
└── open-questions.md           # Unresolved design questions, owner, status
```

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

## 6. Dataset Validation (spec priorities for 01-data-management.md)

Validation is a gate between ingestion and modelling: a dataset version must reach status
`validated` before any model can be fitted on it. The spec must define these layers:

- **Structural**: column presence, dtypes, encodings, key uniqueness (policy id ×
  exposure period), date parsing — expressed as pandera schemas stored with the dataset.
- **Referential**: values resolve against reference tables (postcodes, vehicle groups,
  occupation codes) with effective-date awareness.
- **Actuarial sanity**: exposure > 0 and reasonable (period-consistent), claim dates
  inside exposure periods, no negative claim counts, severity outliers flagged against
  configurable thresholds, claim–policy linkage completeness.
- **Distributional / stability**: one-way distributions and PSI vs a reference dataset
  version, to catch mix shifts and broken feeds before they poison a model.
- **Outcome model**: every run produces a persisted, versioned validation report
  (pass / warn / fail per rule) attached to the dataset version and visible in the UI;
  fails block modelling, warns require an actuary's explicit acknowledgement (audited).
- **Extensibility**: users can define custom validation rules declaratively; the spec
  must define that rule format and its governance (same review/audit trail as models).

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

## 8. skills-map.md (supports the maintainer's next step)

Maintain `docs/skills-map.md` as a living table: **stack component → where it is used
(spec/FR references) → skills to research → learning resources**. Whenever a spec adds
or changes a tech dependency, update this file in the same PR. Example rows: glum (GLM
API, formula interface, regularisation), XGBoost (custom objective gradient/hessian
interface, base_margin, monotone constraints), ZEN Engine (JDM graph format, Python
bindings), Vue Flow (custom nodes/edges, validation), pandera (schema definition,
lazy validation reports).

## 9. Roadmap

- **Phase 0 — Specification: COMPLETE (closed 2026-08-14)**. Every module spec meets the
  §5 standard, all five workflow docs are complete, 31 contracts are drafted, and every
  open question is **gated** — assigned to the phase that needs it (`docs/roadmap.md` §10).
  Exit criterion met: an engineer could start Phase 1 from docs alone.

  *Exit criterion amended 2026-08-14.* It previously required `open-questions.md` to be
  "empty or explicitly deferred". That is now read as **gated rather than emptied**: each
  question is answered before the phase that depends on it, not before any code is written.
  Answering Phase 4 optimisation questions today would be speculation — and this project's
  own record argues against it, since three of the questions that *were* answered by
  reasoning had to be corrected once a spike tested them.
- **Phase 1a — Data Workbench (CURRENT)**: dataset upload, preparation, the four-layer validation
  gate, profiling, reference data. Exit: a freMTPL2 dataset version reaches `validated`,
  having been through the failure loop at least once. The cross-cutting foundations that
  cannot be retrofitted (audit-in-transaction, artifact immutability, the Job model,
  decimal money, `model-schema` as SSOT) land here.
- **Phase 1b — Modelling Workbench**: factor management incl. bandings and groupings, GLM
  and XGBoost fitting (incl. custom objectives), diagnostics, transparency artifacts, model
  versioning. Exit: `wf-01` end to end on freMTPL2.

  *(Phase 1 was split on the `DATA`/`MODEL` boundary — accepted 2026-08-14. As one phase it
  was ~47 % of the platform's requirement surface with no intermediate demo. The split costs
  nothing structurally and means only 4 of the 7 Phase 1 decisions gate the start of work.
  See `docs/roadmap.md` §6.)*
- **Phase 2 — Rating Engine**: DAG designer, rate tables, reference data, real-time +
  batch scoring, dislocation.
- **Phase 3 — Governance**: RBAC, approvals, audit UI, model documentation generation.
- **Phase 4 — Optimisation & Monitoring**: demand models, constrained optimisation,
  drift monitoring, GIPP consistency.

## 10. How You (Claude) Work

§0 decides the deliverable for a given request. The rules below apply to whichever it is.

- **Documents.** Before editing a spec, read `00-overview.md`, the target spec, and any
  workflow that references it.
  After editing, check cross-references in both directions and update `skills-map.md` and
  `open-questions.md` in the same PR.
- Keep terminology exactly consistent with §7; if a new term is needed, add it to the
  glossary in `00-overview.md` first.
- Prefer precise, implementation-ready language: named entities, typed fields, numbered
  requirements, explicit status enums, sequence-of-steps workflows. Avoid vague phrases
  ("the system should handle…") — say who does what, with what data, and what changes.
- When a design choice is genuinely open, do not silently pick one: record options,
  trade-offs, and a recommendation in `open-questions.md` (or an ADR if it must be
  decided now).
- Small illustrative snippets (an XGBoost custom objective signature, a pandera schema,
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

# The gate. Same commands CI runs (.github/workflows/python.yml), in the same order.
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py                # 14 checks over docs/
uv run python scripts/req-coverage.py        # requirement traceability
uv run python scripts/generate-contracts.py  # regenerate; --check fails CI on drift

# Closure audit (§13 step 1): expected scope from the specs, then evidence.
uv run python scripts/scope-audit.py PLAT --sections 3.1,3.2,3.3,3.7,3.8

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

pnpm install --dir frontend                  # W6a
pnpm --dir frontend lint && pnpm --dir frontend test && pnpm --dir frontend type-check
pnpm --dir frontend generate:api             # regenerate TS types from OpenAPI
uv run alembic upgrade head                  # W2
```

## 12. Skills

Project-specific procedures live in `.claude/skills/`, versioned with the repo so they
travel with it. `.claude/skills/README.md` is the index — read it when starting work on an
unfamiliar part of the suite.

**Written for this repo:** `spec-change`, `docs-audit`, `close-workstream`, `adr-write`,
`contract-schema`, `library-spike`, `git-hygiene`, `python-package`, `python-test`,
`fastapi-service`.

**Vendored** from [`wdm0006/python-skills`](https://github.com/wdm0006/python-skills) (MIT,
security-reviewed 2026-08-14): `reproducing-ci-locally`, `security-audit`,
`testing-strategy`, `code-quality`, `secret-hygiene`. Kept as upstream wrote them and
excluded from `ruff`.

`.claude/skills/README.md` is the index and records why each was added.

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

**It is a closure tool, not a CI gate.** Most of the 417 requirements belong to phases that
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

### 2. Deliverables — audited against the definition, not memory

Re-read the workstream's row in `roadmap.md` §6 and check each named deliverable **exists
and works**. Those are different claims: W1's compose file existed for days before anyone
ran it, and NFR-PLAT-4 was unverified the whole time.

### 3. Gates — all green, run locally with the real toolchain

```bash
uv sync --all-packages --dev                 # see §11 — a plain `uv sync` is not enough
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
uv run python scripts/generate-contracts.py --check
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
```

Run them **locally**, not merely "CI passed". CI proves the runner; local proves the result
is reproducible and that you can debug it.

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

### 8. Repository clean

No open PRs for the workstream; no tracked build artifacts; branch deleted after merge —
**verify by content** (`git diff --stat main <branch>`), because squash-merge rewrites
history and `git branch -d` refuses even when the work is fully merged.

### Tests that must exist before closing

- A **negative test for every invariant** the workstream introduced. For a governed system
  the suite must prove the wrong thing *cannot* happen, not that the right thing can.
- A `@pytest.mark.req` marker on each test, naming the requirement it satisfies.
- A round-trip or property test wherever the workstream persists or transforms data.
