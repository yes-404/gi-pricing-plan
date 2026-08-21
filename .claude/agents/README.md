# Project subagents

Delegable specialists for **this** repository, versioned with it. A subagent is not a skill:
a skill loads *into* the current turn, a subagent runs in **its own context** and returns
only a conclusion. That difference is the reason these exist — `CLAUDE.md` §10 measures the
cost of a turn in the context it carries, and an investigation delegated here never lands in
the main thread.

Personal/global agents live in `~/.claude/agents/` and are **never** modified as part of
project work, by the same rule `CLAUDE.md` §12 applies to skills.

## The dividing line: evidence is delegated, verdicts are not

Every agent here gathers or verifies. **None of them decides.** That is not squeamishness —
it is what this repository's own standards require:

- §13 step 1 gives four verdicts for an unevidenced requirement (delivered-but-untested,
  deferred-with-an-owner, reassigned, not-started). Choosing among them is a judgment about
  intent, and a wrong one is written into the roadmap as fact.
- §14's first rule: *the output is a proposal, never a change.*
- §0: when code and spec disagree, **stop and resolve it** — never quietly edit either.

So the split is: **the long, mechanical, high-output half of a task goes to an agent; the
judgment stays in the main thread.** That is also where the context saving is, which is
convenient rather than coincidental — the noisy work and the mechanical work are the same
work.

## Model tiers

Three tiers, assigned by *how much judgment the output requires*, not by how long the task
takes.

### Immaterial — `haiku`

Fixed commands, exit codes, tabulation. The output is checkable by anyone; a weaker model
cannot get it subtly wrong, only visibly wrong. All three are **read-only or run-only** —
none carries `Edit` or `Write`.

| Agent | Runs | Returns |
|---|---|---|
| [`gate-runner`](gate-runner.md) | §11's full gate, **both halves** — ruff, mypy, lint-imports, pytest, audit-docs, req-coverage, contract drift; then pnpm install/generate/lint/type-check/test/build | Per-command exit-code table + the failing excerpt only, ~60 lines |
| [`evidence-collector`](evidence-collector.md) | `scope-audit.py` across **all three axes** (requirements, `--endpoints`, `--catalogue`) plus `req-coverage.py`, then one bounded grep per unevidenced id | Axis totals, the unevidenced list with what each grep found, and any disagreement with the roadmap's claimed count |
| [`ci-watcher`](ci-watcher.md) | Bounded foreground polling of `gh pr view --json mergeStateStatus` to a terminal state, disambiguated through `gh run list --json status,conclusion` (the token reads the run list; it cannot read check details, and `UNSTABLE` while runs are in-flight is not a failure) | The terminal state once every expected run is `completed`, which workflows the diff *should* have fired, and a pointer to `gate-runner` for the cause |

### Material but bounded — `sonnet`

Real judgment inside a narrow frame. Each reads the relevant skill rather than restating it.

| Agent | Use it for | The gap it fills |
|---|---|---|
| [`spec-reconciler`](spec-reconciler.md) | §14 question 4 — does the module's spec still describe the code? §5.1 **in both directions**, §5.2 signatures, §5.3 Contents columns, catalogues, copyable params | §14 calls this "the review's main target, not a tidy-up", and it is wide, slow reading. Read-only, so it cannot re-plan |
| [`postgres-pro`](postgres-pro.md) | Query and index design, execution plans, schema and Alembic migration review, pooling against async SQLAlchemy | No skill covers the **database layer**. `fastapi-service` covers the app and its persistence traps; nothing covered PostgreSQL 16 itself |
| [`performance-engineer`](performance-engineer.md) | Profiling a slow path, load-testing against a p99 target, baselining before an optimisation | §13 step 5 requires NFRs **measured, not asserted** — but no skill covers how to take the measurement |
| [`accessibility-tester`](accessibility-tester.md) | Verifying `frontend/` against WCAG 2.2 AA — keyboard, focus, ARIA, contrast, and the non-colour channel diagnostic and PSI charts need | `ui-ux-pro-max` is design-side, `vue-frontend` is platform facts. Neither *verifies* a built view |

### Judgment — stays in the main thread, no agent

Deliberately unfilled. Half of a work breakdown is naming what must **not** be handed off:

| Work | Why it stays |
|---|---|
| **§13 closure verdicts** | A wrong verdict is written into the roadmap as fact, and the next workstream is planned against it. `close-workstream` skill, main thread, on `evidence-collector`'s output |
| **§14 review proposals** | The output is a maintainer-facing proposal with an acceptance line. `phase-review` skill, main thread, on `spec-reconciler`'s output |
| **§0 spec-vs-code resolution** | Deciding *which side was wrong* is the record a governed system cannot afford to lose |
| **Slice design** — which requirement, what the failing test asserts | `test-driven-development` and `python-test`; the `@pytest.mark.req` marker is a traceability claim, not a formality |
| **Spec and roadmap edits** | `spec-change`, `adr-write`, `git-hygiene`. No agent here holds `Write` on `docs/` |

## Where they fit in a W5 slice

The working rhythm is a slice: one requirement (or a small set) from spec to merged PR.
Delegation points are steps 4, 5 and 8.

| # | Step | Who |
|---|---|---|
| 1 | Read the governing spec section for the requirement | main thread — bounded ranges (§10) |
| 2 | Write the failing test, `@pytest.mark.req` naming the requirement | main thread — `test-driven-development`, `python-test` |
| 3 | Implement | main thread — `python-package`, `fastapi-service`, `vue-frontend` |
| 4 | **Run the gate** | → `gate-runner` |
| 5 | **Check coverage / endpoints / catalogue** | → `evidence-collector` |
| 6 | Write the slice record and any dated spec note | main thread — `spec-change`, §0 |
| 7 | Branch, commit, PR | main thread — `git-hygiene` |
| 8 | **Watch CI** | → `ci-watcher` |
| 9 | Review | `/code-review`, `requesting-code-review` |

Broad multi-file searches at any step go to the built-in **`Explore`** agent, which is what
§10's "delegate noisy investigation" asks for. At a workstream close, run
`evidence-collector` and `spec-reconciler` **first**, then take their output into
`close-workstream` and `phase-review` in the main thread.

## Precedence

**Skills outrank these agents on procedure.** `CLAUDE.md` §12 fixes the order — superpowers
for *how work is approached*, then this repo's skills for *what is true here*. A subagent
supplies a bounded specialism inside that order; it does not replace either.

Nothing here overrides `CLAUDE.md` §0, §5 or §13.

## Provenance

**Self-written (2026-08-21):** `gate-runner`, `evidence-collector`, `ci-watcher`,
`spec-reconciler`. Each encodes facts a general agent cannot know — the gate's exact env
block from `.github/workflows/python.yml`, the three scope-audit axes, the `gh` token's
inability to read `statusCheckRollup` **and the fact that the failing commands still exit
`0`**, §14's both-directions rule. Each was verified against this checkout, not recalled.
Amended the same day from PR #126's merge: `mergeStateStatus` reports in-flight runs as
`UNSTABLE`, and `gh run list --json status,conclusion` is the disambiguator the token
does grant — a fourth trap recorded on `ci-watcher`.

**Vendored (2026-08-21):** `postgres-pro`, `performance-engineer`, `accessibility-tester`,
from [`VoltAgent/awesome-claude-code-subagents`](https://github.com/VoltAgent/awesome-claude-code-subagents)
(MIT, © 2025 VoltAgent) at `c9e51ec`, 2026-08-12.

**Security review, 2026-08-21.** The three vendored files are prompt text only — no network
calls, no shell substitution, no credential handling, no instruction to read outside the
repository. `postgres-pro` and `performance-engineer` carry `Read, Write, Edit, Bash, Glob,
Grep`; `accessibility-tester` is read-only plus `Bash`. Upstream's tool lists were kept. The
four self-written agents hold **no `Write` or `Edit`** at all.

## Why only three of upstream's 158

Upstream is broad and generic. Most of it is unusable here for reasons `CLAUDE.md` already
decided, and installing it anyway would have created a second, vaguer source of truth beside
skills that are deeper and repo-specific.

- **Contradicts §3's stack.** `python-pro` prescribes pandas, Poetry and black — this project
  uses Polars, uv and ruff, and §3 excludes pandas by name. `typescript-pro` teaches React;
  `sql-pro`, `database-optimizer` and `database-administrator` are half MySQL/Oracle/MongoDB.
  §12's rule is explicit: **a skill teaching a rejected approach is worse than a missing one.**
- **Duplicates a deeper skill.** `fastapi-developer` (287 generic lines) against
  `fastapi-service` (569 lines of this repo's actual traps); likewise `vue-expert` against the
  `vue-*` set, `code-reviewer`/`debugger`/`qa-expert`/`security-auditor`/`refactoring-specialist`
  against `code-review`, `systematic-debugging`, `testing-strategy`, `security-audit`,
  `code-quality`, and `architect-reviewer` against `phase-review` and `adr-write`.
- **Wrong domain despite the name.** `quant-analyst` is derivatives and HFT — Black-Scholes,
  Greeks, market making. This is **general insurance pricing**: GLM frequency/severity,
  Tweedie burning cost, exposure offsets (§7). `risk-manager` is enterprise VaR;
  `fintech-engineer` is payments and PCI. None of the three touches actuarial work.
- **Ahead of the phase** (`CLAUDE.md` §0). `data-engineer` is Airflow/Spark/dbt and
  `pipelines/` is deferred to W7; `ml-engineer` and `mlops-engineer` are model serving, which
  is Phase 2+. A later phase's capability is a spec change, not an installed agent.

The actuarial gap upstream cannot fill — GLM families, link functions, banding and grouping
discipline, custom objectives — stays with `docs/specs/02-modelling.md` and `pricing-core`,
which is where it belongs.

## Local modifications to the vendored three

Upstream's body text is otherwise kept as written. Four changes were made to each file,
because upstream ships them for a different setup:

1. **An `## In this repository` block** after the persona paragraph — the stack, the governing
   specs, the commands, the invariants that are not tradeable (integer money,
   audit-in-transaction, artifact immutability), and the phase boundary. This is the half a
   general agent cannot know, and without it the file is a checklist.
2. **`description:` rewritten** to route accurately. Upstream's `postgres-pro` advertised
   "high-availability replication, backup strategies, enterprise deployments" — out of phase
   here, and a description that oversells is a description that gets invoked wrongly.
3. **The `context-manager` protocol removed.** All three opened by querying a
   `context-manager` agent and emitting a `requesting_agent` JSON envelope to it. That agent
   is **not installed** (it is upstream's `09-meta-orchestration` set, an orchestration layer
   this repo does not use), so the block instructed the agent to address something that does
   not exist. Replaced with the repository files each one should actually read first.
4. **The trailing "Integration with other agents" roster replaced.** Upstream lists agents
   that are not installed here (`backend-developer`, `sre-engineer`, `ui-designer`, …).
   Replaced with real routing: the skills to read, the `Explore` agent for broad searches,
   and `CLAUDE.md` §0 for a code/spec disagreement.

One further change, to `accessibility-tester` only: `model: haiku` → `model: sonnet`. Judging
whether a diagnostic chart carries meaning in colour alone is not a mechanical check.

## Maintenance

The rules in `CLAUDE.md` §12 apply here unchanged: fix an agent in the same session it is
found wrong and refresh its `Last verified` date; re-check upstream at the monthly skill
audit; **never install more without the maintainer's approval**.

Re-running upstream's `install-agents.sh` would overwrite all four modifications above.
Update by hand against a fresh clone instead.

**Last verified:** all seven, 2026-08-21.
