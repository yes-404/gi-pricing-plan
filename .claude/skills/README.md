# Project skills

Procedures specific to **this** repository, versioned with it so they travel with the code.
Each captures something non-obvious that was learned the hard way — a convention that is
easy to break silently, or a trap that a passing check would hide.

Personal/global skills live in `~/.claude/skills/` and are **never** modified as part of
project work (`CLAUDE.md` §12).

## Index

| Skill | Purpose | Source | Last verified |
|---|---|---|---|
| [`git-hygiene`](git-hygiene/SKILL.md) | Branch and PR flow, `.gitignore` rules (including what must **not** be ignored), squash-merge cleanup, and the merge-order trap that strands work | self-written | 2026-08-14 |
| [`spec-change`](spec-change/SKILL.md) | Add or modify a requirement, section, or open question in `docs/specs/` — append-only IDs, ten-section standard, both-direction cross-referencing, and what recording a *decision* touches | self-written | 2026-08-15 |
| [`docs-audit`](docs-audit/SKILL.md) | Verify suite integrity before a commit or PR — 20 checks (8 bookkeeping, 7 structural, 5 over the `.claude/notes/` working notes) plus the decision-gate invariant the script does not cover | self-written | 2026-08-15 |
| [`close-workstream`](close-workstream/SKILL.md) | Audit a workstream against `CLAUDE.md` §13 before writing "closed" into the roadmap — **scope derived from the specs first**, then evidence; gate run locally, new checks proven non-trivial, NFRs measured, every gap given a verdict | self-written | 2026-08-14 |
| [`phase-review`](phase-review/SKILL.md) | Run `CLAUDE.md` §14's plan review — five questions in order, each answered including "no change"; proposals with a maintainer acceptance line, never edits. Written after the procedure had run twice, as §14 requires | self-written | 2026-08-15 |
| [`adr-write`](adr-write/SKILL.md) | Create, supersede, or annotate an architecture decision record — including the addendum-versus-edit rule that keeps accepted ADRs immutable | self-written | 2026-08-14 |
| [`contract-schema`](contract-schema/SKILL.md) | Add or modify a JSON Schema contract in `docs/contracts/` — money conventions, `invariants` annotation, duplicate-key and `$ref` traps, and why hand-authored schemas are patched as text | self-written | 2026-08-15 |
| [`python-package`](python-package/SKILL.md) | Write Python in the uv workspace — where code belongs, the import-linter boundaries, and the Pydantic v2 idioms the contracts depend on | self-written | 2026-08-14 |
| [`fastapi-service`](fastapi-service/SKILL.md) | Backend conventions and traps — app factory, RFC 9457 problem responses, the Starlette middleware-ordering trap that drops `trace_id` from 500s, liveness vs readiness, typed settings, and the persistence traps: three-layer append-only enforcement, Alembic ENUM cleanup, async fixture scope | self-written | 2026-08-14 |
| [`python-test`](python-test/SKILL.md) | Testing discipline — requirement-traceability markers, the negative-test emphasis, pytest config, running without pip, and **why a green run with no database is a partial one** | self-written | 2026-08-15 |
| [`library-spike`](library-spike/SKILL.md) | Empirically verify library behaviour where pip is unavailable — wheel fetching, version pinning, missing native libs — then land the finding across the suite | self-written | 2026-08-14 |
| [`vue-frontend`](vue-frontend/SKILL.md) | Frontend conventions specific to **this** platform — the generated-client seam, how money and exact decimals cross into TypeScript, the RFC 9457 error shape, cursor pagination, and the 202-plus-Job model, and the dev-identity proxy without which a browser gets 401 on everything | self-written | 2026-08-15 |

## External skills

Five vendored from [`wdm0006/python-skills`](https://github.com/wdm0006/python-skills)
(MIT, © 2025 Will McGinnis) on 2026-08-14, after a security review: no network calls of
their own, no credential access, no filesystem reach outside a target project. The one
bundled script (`security-audit/scripts/security_scan.py`) shells out only to `bandit`,
`pip-audit`, `semgrep` and `detect-secrets` in list form with timeouts. **Note:**
`semgrep --config auto` fetches rules from Semgrep's registry, so that scanner does reach
the network.

| Skill | Fills | Note |
|---|---|---|
| [`reproducing-ci-locally`](reproducing-ci-locally/SKILL.md) | Running the CI gate locally | Immediately found 21 ruff errors and a dead import-linter config |
| [`security-audit`](security-audit/SKILL.md) | NFR-OVR-8 / NFR-PLAT-8 dependency and CVE scanning | Bundles a scanner script |
| [`testing-strategy`](testing-strategy/SKILL.md) | pytest technique — fixtures, parametrization, Hypothesis | Complements this repo's `python-test` |
| [`code-quality`](code-quality/SKILL.md) | ruff/mypy depth and refactoring | Complements this repo's `python-package` |
| [`secret-hygiene`](secret-hygiene/SKILL.md) | Secrets and build artifacts in git | **Renamed** from upstream `git-hygiene` to avoid colliding with this repo's own |

Six vendored from [`yes-404/vue3-skills`](https://github.com/yes-404/vue3-skills), a fork
of [`vuejs-ai/skills`](https://github.com/vuejs-ai/skills) (MIT, © 2025 hyf0 & SerKo) on
2026-08-15, at the maintainer's request and after a security review: **markdown only** —
no scripts, no executables, nothing under `skills/` that is not a `.md`. No instructions
aimed at the agent beyond their subject; every outbound link points at `vuejs.org`,
`github.com`, MDN, `vitest.dev`, `playwright.dev` or `nuxt.com`. The apparent
credential hits are an example `useLogin` composable, and the apparent install commands are
`npm install -D vitest` in prose.

| Skill | Fills | Note |
|---|---|---|
| [`vue-best-practices`](vue-best-practices/SKILL.md) | Composition API, `<script setup>`, reactivity, SFC, Suspense/Teleport/Transition, list performance | The core reference; agrees with §3 on Composition API + TS |
| [`vue-router-best-practices`](vue-router-best-practices/SKILL.md) | Router 4 guards, params, route-component lifecycle | |
| [`vue-pinia-best-practices`](vue-pinia-best-practices/SKILL.md) | Store setup and reactivity with stores | §3 chose Pinia; `vue-frontend` records that so its "lightweight composables" option is not read as open |
| [`vue-testing-best-practices`](vue-testing-best-practices/SKILL.md) | Vitest, Vue Test Utils, component testing, Playwright E2E | Matches §3's runner choices exactly |
| [`vue-debug-guides`](vue-debug-guides/SKILL.md) | 140 diagnosis notes — hydration, async, reactivity, animation, form binding | The largest, and reference-only: the `SKILL.md` is an index and the notes load on demand |
| [`create-adaptable-composable`](create-adaptable-composable/SKILL.md) | `MaybeRefOrGetter` inputs normalised with `toValue()` | Small and specific |

**Two were deliberately not vendored.** `vue-jsx-best-practices` and
`vue-options-api-best-practices` document approaches `CLAUDE.md` §3 has decided against
(`<script setup lang="ts">` and the Composition API only). A skill that teaches a rejected
approach is worse than a missing one, because an agent may follow it and the review that
catches it is a human one.

Vendored files are kept **as upstream wrote them** and are excluded from `ruff` — linting
someone else's code to our rules produces churn and breaks that promise.

Not installed, worth revisiting when the phase needs them: `github-actions` (CI cost and
trigger hygiene), `performance` (Phase 2, NFR-RATE-1), `api-design` and
`web-app-architecture` (W2's FastAPI surface).

### Original discovery passes

**None installed.** Two discovery passes against `anthropics/skills` (18 skills) and
`claude-plugins-official`:

- **2026-08-14, Phase 0** — nothing fitted a documentation-first phase with highly
  repo-specific conventions; the closest candidate (`doc-coauthoring`) overlaps
  `CLAUDE.md` §5/§10, which is more specific and already binding.
- **2026-08-14, Phase 1a re-run** (§12's rule: re-run the gap analysis when project state
  changes) — writing Python changed the calculus, so this was worth redoing. It still found
  nothing: no external skill covers `uv` workspaces, this repo's Pydantic money idioms, or
  requirement-traceability markers. Those became `python-package` and `python-test`.

Several become relevant in later phases and are recorded so the next gap analysis does not
have to rediscover them:

| Skill | Becomes relevant | For |
|---|---|---|
| `xlsx` | Phase 2 | Rate table CSV/XLSX import-export round-tripping (FR-RATE-20) |
| `pdf` | Phase 3 | Dossier PDF rendering, deterministic output (FR-GOV-29) |
| `webapp-testing` | Phase 1–2 | Frontend and DAG designer testing |
| `skill-creator` | when this library grows | Skill evals and description tuning; heavyweight (spawns nested `claude -p`) |

External skills are **never installed without the maintainer's approval** (`CLAUDE.md` §12).

## Conventions

- Kebab-case folder, one capability per skill, no overlap between skills.
- Frontmatter `name:` must equal the folder name; `description:` controls triggering, so
  it names the concrete artifacts and file paths involved, not just a topic.
- Every skill ends with a `## Verified` line: the date and **how** the procedure was
  confirmed — ideally citing a failure it actually caught.
