# CLAUDE.md — Open Source General Insurance Pricing Platform

**Binding rules live here; the procedures and reasoning that satisfy them live in
`.claude/skills/`, which this file points at rather than restates.** Read it fully.

## 0. CURRENT PROJECT PHASE: 1b — MODELLING WORKBENCH (read this before anything else)

**Phase 1b is active, and writing application code is the expected default** for work
inside its scope (§9). **Which workstreams are open is `docs/roadmap.md` §6's to state, not
this file's**, as are the phase closure dates. The `docs/` suite is the contract Phase 1
builds against: **read the relevant spec before writing the code that implements it** —
guessing is never the faster path.

| Request | Deliverable |
|---|---|
| Inside the current phase's scope (§9) | **Code**, plus any spec change it proves necessary |
| A capability not yet specified | **Spec change first**, then code — the spec is the design step |
| A later phase (rating, optimisation, monitoring, governance UI) | **Spec change only** — never build ahead of the phase |
| A design choice the specs leave open | Options + a recommendation in `docs/open-questions.md`, never a silent pick |

**When code and spec disagree, stop and resolve it** rather than quietly making either match
the other. Which one is wrong is a real question and the answer has often been the spec;
changing one silently destroys the record of which was believed, the thing a governed system
cannot afford to lose.

Three rules survive every phase change:

- **Requirement IDs and section numbers are permanent** (§5). Never renumber; append, mark
  superseded, or leave a tombstone.
- **Counts and status that change are not written in this file.** `req-coverage.py` prints
  requirement counts; `docs/roadmap.md` holds workstream and component status. Four
  incidents of the copy here going stale:
  [`NT-0003`](.claude/notes/0003-duplicated-status-goes-stale.md).
- **Every spec change runs `python3 scripts/audit-docs.py` before commit.**

## 1. Project Mission

An open-source general insurance pricing platform for the UK/EU market — an alternative to
WTW Radar/Emblem. Full lifecycle: data preparation → risk modelling (GLM/ML) → rating
algorithm design → deployment/scoring → monitoring → governance. Primary users: pricing
actuaries and analysts — technical (Python/notebooks) but expecting a polished UI. Every
design decision favours reproducibility, auditability, and transparency of the maths.

## 2. Repository Layout — *the annotated tree and the reasoning are `.claude/skills/repo-architecture`*

**Component status — exists, partial, scheduled — belongs to `docs/roadmap.md` §6 and only
there** ([`NT-0003`](.claude/notes/0003-duplicated-status-goes-stale.md)). Three entries
carry a rule: **`uv.lock` is committed** — a lockfile, not an environment; **`docs/contracts/`
is generated and never hand-edited**; **a filed plan under `docs/plans/` is frozen at its
date**. **It is a polyglot monorepo and neither language is the "main" one** — the root
`pyproject.toml` configures Python tooling only, and CI is three path-filtered workflows.

**One contract joins backend and frontend, and it flows one way.** ADR-0002's
`model-schema`, the single source of truth, generates `docs/contracts/` — JSON Schema +
OpenAPI 3.1, committed, a published spec artifact rather than a build output, CI failing on
drift (FR-PLAT-48) — which generates `frontend/src/api/generated`, VCS-ignored and never
hand-written.

**The specification is the contract the code is written against**, not a parallel track. A
change spanning both lands as **one commit** — spec, code, tests, any skill update — or the
audit reports a consistency the repository does not have.

Standing architecture rules (decided — do not reopen without an ADR):
- **Nobody hand-writes a shape that already exists in `model-schema`** — not the backend,
  not the frontend, not a test fixture. A shape defined twice will diverge, and in a pricing
  platform a diverged shape is a mispricing.
- `pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis deps.
- Model and rating definitions are declarative JSON artifacts, never pickles.

## 3. Tech Stack (specs must be written against this stack)

Python 3.12 + `uv` · FastAPI + Pydantic v2 · SQLAlchemy 2.x async + Alembic · PostgreSQL 16 ·
Celery + Redis · Polars + DuckDB · `glum` · XGBoost + LightGBM + interpret/EBM · GoRules ZEN ·
Vue 3 + Vite + Pinia + Tailwind + ECharts, pnpm. **`docs/skills-map.md` maps each component
to where it is used and what to read; each spec's §8 names what that module depends on.**

Three choices already made *against*, which a session otherwise breaks by default:

- **No pandas in new code**, except at unavoidable library boundaries.
- **Never hand-write an API type** in the frontend; generate it from OpenAPI.
- **Vue 3 Composition API with `<script setup lang="ts">` only** — never Options API, JSX, React.

`.claude/skills/repo-architecture` carries the rest — why `statsmodels` and pandera are not
dependencies despite one stale spec row naming the first, the monotonic-constraint
requirement on both boosters, what `mypy --strict` and `ruff` cover. **Custom objectives
are first-class** (`02-modelling.md` §4.4 catalogues the permitted forms); a spec introducing
one is incomplete until it satisfies `.claude/skills/spec-change`'s four governance rules for
arbitrary code — declaration, validation, versioning, audit.

## 4. Documentation Suite — the module map

[`docs/README.md`](docs/README.md) indexes the suite and says what each spec covers: `00`
overview and glossary · `01` data management · `02` modelling · `03` rating engine · `04`
optimisation · `05` monitoring · `06` governance · `07` platform.

`workflows/wf-01…05` are the **cross-module journeys** — dataset-to-model,
model-to-rating-version, rate-change impact, deploy-and-monitor, custom-objective lifecycle.
A module spec says what one module does; a workflow says what actually happens across all
of them.

## 5. Spec Document Standard

**Every spec keeps all ten sections** — purpose & scope, concepts & glossary, functional
requirements, data contracts, interfaces, workflows, cross-module dependencies, tech
dependencies, non-functional requirements, open questions. What each must contain is in
`.claude/skills/spec-change`: **the procedure for touching `docs/`, read it first**.

**Requirement IDs are permanent: never renumber, only append or mark superseded.** Section
numbers here obey it too: §6 and §8 are tombstones, §2, §11, §13 and §14 keep their rules
and point at the skill with the procedure, and no number is ever reused.

## 6. Dataset Validation — *superseded by `01-data-management.md`*

Read that spec. The number is kept, not reclaimed (§5 covers section numbers).

## 7. Domain Model — *`00-overview.md` §2 is authoritative*

It defines every term. Use its names in every doc and identifier; a new
term goes there before first use. Four rules worth stating twice, because breaking one is
silent:

- A **Dataset** is a named container and holds no data; a **Dataset Version** is the
  immutable snapshot carrying its validation report, profile and status
  (`draft → validated → archived`).
- **Modelling references a Dataset Version, never a Dataset.**
- **Money is integer pence/cents, or Decimal in the rating path — never float.**
- **The actuarial correctness defaults are numbered requirements, not conventions** —
  family, link, offset and weight per response type, the GBM objectives and exposure
  handling, monotonic constraints, the transparency artifact and surfaced uncertainty:
  `02-modelling.md` FR-MODEL-19, 21, 26, 27, 28 and 33, where the amendments and the
  empirical verification are.

## 8. skills-map.md — *folded into §10*, which carries its one binding instruction.

## 9. Roadmap — *the plan lives in `docs/roadmap.md`*

**Phase 1b — Modelling Workbench is current.** Exit: `wf-01` end to end on freMTPL2.
The phase list, workstream rows, closure records, decision gates, which workstreams are open
and the retrofit-impossible list are written **only** there
([`NT-0003`](.claude/notes/0003-duplicated-status-goes-stale.md) records the four times this
file restated it). Two things change how you work rather than what is planned:

- **The retrofit-impossible foundations of `docs/roadmap.md` §5 landed in Phase 1a.** They
  are invariants to preserve, not work to schedule: regressing one is the same rewrite that
  deferring it would have been.
- **Do not build ahead of the phase** (§0's table). A later phase's capability is a spec
  change, not code.

## 10. How You (Claude) Work

§0 decides the deliverable; these apply to whichever it is.

- **Documents.** `.claude/skills/spec-change` is the procedure — glossary first, append-only
  IDs, ten sections, open questions mirrored both ways, and `skills-map.md` updated in the
  same PR whenever a **tech dependency** changes.
- **When a design choice is genuinely open, do not silently pick one**: record options,
  trade-offs and a recommendation in `open-questions.md`, or an ADR if it must be decided now.
- **Code.** `.claude/skills/python-package` and `python-test` hold the conventions; run the
  full gate locally before pushing (`.claude/skills/reproducing-ci-locally` has the why).
- All PRs: Conventional Commits, short-lived branches from `main`, squash-merge, branch
  auto-delete. `.claude/skills/git-hygiene` covers the traps.

**Context discipline — a turn costs what the context weighs**, because every turn re-reads
the whole accumulated context. Measured once over 2026-08-14 → 08-19 and not maintained
since: **73% of spend came from calls carrying more than 200k tokens of context.** Two rules
follow:

- **Delegate noisy investigation to a subagent** — grep sweeps, log trawls, broad searches.
  Keep the conclusion, not the file dumps: a subagent's context is discarded when it returns,
  the main thread's is not.
- **Read bounded ranges, not whole files** — `sed -n '100,160p'`, `grep -n -C3`, `head`, and
  a `wc -l` before anything large. A whole file read to find one function stays in context
  permanently, re-read every turn thereafter.
- **A boundary metric reads zero by construction.** "Zero calls above 200k" reports where the
  compaction cap sits, not how light the usage was — a heavy session and a disciplined one
  produce the same zero. Read trends at the boundary (the share of calls near the cap, and
  the spend those calls carry), never absence above it.
  ([`NT-0007`](.claude/notes/0007-context-bound-measures-cap-not-discipline.md))

## 11. Commands Reference — *every command is in `.claude/skills/dev-commands`*

**Every command has a trap that makes the obvious form wrong** — the exit-code pitfall, the
load-contention factor that reads as a regression, the alembic DSN, the pnpm install, the
`--all-packages` that is not optional. The rule rather than the command: **the gate has two
halves and both must pass locally before pushing** — a Python-only "gate" has been green
here while the frontend was red.

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

## 12. Skills

Project procedures live in `.claude/skills/`, versioned with the repo. **Its `README.md` is
the index**, `.claude/agents/README.md` the same for the delegable specialists. **This
section keeps no second list**
([`NT-0003`](.claude/notes/0003-duplicated-status-goes-stale.md)).

- **Discovered a non-obvious procedure** (build quirk, test setup, data format rule, deploy
  step)? Write or update a skill, update the README, commit both with the work.
- **A skill that turns out to be wrong is fixed in the same session**, `Verified` date
  refreshed. Never leave a known-stale skill in place.
- **Never install an external skill without the maintainer's approval**, and never take one
  teaching an approach §3 decided against. The same test governs `.claude/agents/`; the
  READMEs record each refusal.
- **Vendored files stay as upstream wrote them**, excluded from `ruff`, every deviation
  recorded in the README rather than made silently.
- Monthly, or on "skill audit": re-run the gap analysis, propose additions and removals.
- Never modify `~/.claude/skills/` (personal/global) as part of project work.

**Team process.** How this repository's Claude Code team does the work — the Project →
Phase → Work → Slice layering, roles, escalation guards, and the monitoring loop — is
`docs/process/delivery-process.md` and its companion `docs/process/agent-settings.md`.
Distinct from `docs/workflows/wf-01…05`, the cross-module *domain* journeys (§4) — one
describes how the team works, the other what the platform does.

**Evidence is delegated, verdicts are not.** A subagent runs in its own context and returns
a conclusion — what §10 asks for — but **skills outrank agents on procedure** and the
**verdict stays in the main thread**: §13's four verdicts, §14's proposals, §0's decision
about which of spec and code was wrong, slice design, every edit to `docs/`.

**Precedence — superpowers first.** When a superpowers skill and any other both apply,
follow the superpowers one. Read `using-superpowers` when a task starts;
`.claude/skills/README.md` §Precedence has the working order and the narrow carve-out where
a repo fact outranks a superpowers procedure. **Nothing in superpowers overrides §0, §5 or
§13.**

## 13. Workstream Closure Standard — *the standard is `.claude/skills/close-workstream`*

**A workstream is closed only when that skill's checklist passes and the result is recorded
in `docs/roadmap.md`** — closing without it produces a roadmap reporting progress the
repository does not have, which the next workstream is then planned against. Three rules
bind wherever anything here is audited, not only at a close:

- **Scope is derived from the specification first, then evidenced** — never from
  recollection of what was built. Reversed, an audit is silent about what is missing.
- **Every requirement without evidence gets one of four verdicts** — delivered but untested,
  deferred with an owner, reassigned, not started. Silence is not one of them, and the
  verdict is the main thread's (§12), never a subagent's.
- **NFRs are measured, not asserted; enforcement is proven on deliberately broken input.** A
  check that has never printed a failure has not been tested, and a generated artifact
  matching its source proves neither correct.
- **A reference carries its scope and its measurement.** A count carries the tree *and* the
  corpus it counted over; a schema or contract name carries its full path; a `Verified` date
  carries the tree; a word with two scopes (`shape`, `slug`, `contract`, `variant`) says which
  it means. The test: would it still resolve for a reader holding none of your open context?
  ([`NT-0004`](.claude/notes/0004-a-reference-that-resolves-only-for-the-writer.md))
- **Name the range, not the tip; verify the claim, not just the citation.** A review or gate
  names `origin/main...branch`, never the branch's tip SHA — a tip is the record of the last
  edit, not the change set. And a citation can be correct while the content it vouches for is
  wrong: read to the part of the cited artifact that carries the claim — a requirement's
  clauses including its dated amendments, a test's asserts, a function's body.
  ([`NT-0006`](.claude/notes/0006-two-rules-for-reading-an-artifact.md))

## 14. Phase Review Standard — *the standard is `.claude/skills/phase-review`*

§13 audits **one workstream against its own scope**. This audits **the plan** — whether the
phase boundaries, workstream cuts and requirement set still make sense now that some of the
work is real. The plan is a working hypothesis, re-tested while the phase is still open.
*(Raised as [`NT-0001`](.claude/notes/0001-phase-boundary-plan-review.md), 2026-08-15.)*
**Trigger: at each workstream close, and again before a phase's exit demo** — fixed, not
"sometime". The five questions are in the skill; three rules bind outside it:

- **The output is a proposal, never a change** — recommendation, rationale, and an explicit
  maintainer acceptance line with a date. A review that edits the roadmap on its own
  authority is re-planning.
- **A later phase's finding is a spec change only** (§0's table).
- **Nothing starts in the next phase while an open finding from the current phase lacks a
  resolution.** A finding has a resolution when the close fixes it, carries it forward with
  a named owner, or accepts it. The phase closure record lists every open finding with its
  resolution.
