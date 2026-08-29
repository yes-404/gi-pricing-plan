# Project skills

Procedures specific to **this** repository, versioned with it so they travel with the code.
Each captures something non-obvious that was learned the hard way — a convention that is
easy to break silently, or a trap that a passing check would hide.

Personal/global skills live in `~/.claude/skills/` and are **never** modified as part of
project work (`CLAUDE.md` §12).

## Precedence

**Superpowers first** (`CLAUDE.md` §12). The fourteen skills vendored from
[`obra/superpowers`](https://github.com/obra/superpowers) set *how work is approached*;
everything else here supplies *what is true about this repository*. When both apply,
follow superpowers for the procedure and the repo-local skill for the facts — paths,
commands, requirement ids — that a general skill cannot contain.

Start a task by reading [`using-superpowers`](using-superpowers/SKILL.md); it is the
router, and it points at the rest. Then read the superpowers process skill for the *shape*
of the work, and only then the repo-local skill for the specifics:

| Shape of the work | Read first |
|---|---|
| Creative or open-ended design | [`brainstorming`](brainstorming/SKILL.md) |
| Any fix | [`systematic-debugging`](systematic-debugging/SKILL.md) |
| Multi-step work | [`writing-plans`](writing-plans/SKILL.md) · [`executing-plans`](executing-plans/SKILL.md) · [`subagent-driven-development`](subagent-driven-development/SKILL.md) |
| Implementation code | [`test-driven-development`](test-driven-development/SKILL.md) |
| Claiming anything passes | [`verification-before-completion`](verification-before-completion/SKILL.md) |

The carve-out is narrow and factual: where superpowers gives a *procedure* and a repo skill
states a *fact about this repository*, the fact wins, because superpowers does not contain
it and cannot. `git-hygiene`'s `.gitignore` rules and squash-merge flow and `python-test`'s
`@pytest.mark.req` markers are facts of that kind — `finishing-a-development-branch` still
decides *how* a branch ends. Nothing in superpowers overrides `CLAUDE.md` §0, §5 or §13:
the phase table, permanent requirement ids and the closure standard are this project's
contract, not a default behaviour a general skill is entitled to replace.

## Index

| Skill | Purpose | Source | Last verified |
|---|---|---|---|
| [`git-hygiene`](git-hygiene/SKILL.md) | Branch and PR flow, `.gitignore` rules (including what must **not** be ignored), squash-merge cleanup — both `git branch -d` and `ExitWorktree`, which refuse for the same ancestry reason and say different things about it — how a squash title and body are composed, the merge-order trap that strands work, how a stacked PR survives the merge below it, and **why bare `git stash` is unsafe here** — one stash stack is shared by every worktree, and why an amended SHA must name its delta rather than inherit review clearance | self-written | 2026-08-25 |
| [`spec-change`](spec-change/SKILL.md) | Add or modify a requirement, section, or open question in `docs/specs/` — append-only IDs, ten-section standard, both-direction cross-referencing, what recording a *decision* touches, and the four things a spec introducing a custom objective must say | self-written | 2026-08-23 |
| [`docs-audit`](docs-audit/SKILL.md) | Verify suite integrity before a commit or PR — 23 checks (8 bookkeeping, 6 structural, 6 over the register and the `.claude/notes/` working notes, 1 over the journeys' interface citations, 1 over table-row cell counts, 1 over the §10 mirror rows' status) plus the decision-gate invariant the script does not cover | self-written | 2026-08-26 |
| [`close-workstream`](close-workstream/SKILL.md) | Audit a workstream against `CLAUDE.md` §13 before writing "closed" into the roadmap — **scope derived from the specs first**, then evidence; gate run locally, new checks proven non-trivial, NFRs measured, every gap given a verdict. Also: a check's design note must say which half **fails open**, which **fails closed** and **what it cannot see at all**; a metric a script computes is **run, never re-derived**, and a repository population is counted with **`git grep`**, whose index excludes ignored output by construction; and a **retraction is verified against the artifact it retracts**, never against the retractor's account of it | self-written | 2026-08-24 |
| [`phase-review`](phase-review/SKILL.md) | Run `CLAUDE.md` §14's plan review — five questions in order, each answered including "no change"; proposals with a maintainer acceptance line, never edits. Written after the procedure had run twice, as §14 requires | self-written | 2026-08-15 |
| [`adr-write`](adr-write/SKILL.md) | Create, supersede, or annotate an architecture decision record — including the addendum-versus-edit rule that keeps accepted ADRs immutable | self-written | 2026-08-14 |
| [`contract-schema`](contract-schema/SKILL.md) | Add or modify a JSON Schema contract in `docs/contracts/` — money conventions, `invariants` annotation, duplicate-key and `$ref` traps, why hand-authored schemas are patched as text, and registering a new schema's slug so the type comparison actually reads it | self-written | 2026-08-19 |
| [`contract-guard`](contract-guard/SKILL.md) | Write or extend the schema-drift guard in `backend/tests/test_contracts.py` — what each walker reaches, why `if` is not followed, why `required` is compared in one direction only, the four defects found inside the guards themselves, and why a comparison that counts paths cannot catch a walker that stopped descending | self-written | 2026-08-22 |
| [`python-package`](python-package/SKILL.md) | Write Python in the uv workspace — where code belongs, the import-linter boundaries, the Pydantic v2 idioms the contracts depend on, **the compiled dependencies that abort rather than raise**, and **why `model_copy(update=...)` silently skips a cross-field validator**, and **why path-scoping `mypy` invents ~113 errors the gate does not have** | self-written | 2026-08-22 |
| [`fastapi-service`](fastapi-service/SKILL.md) | Backend conventions and traps — app factory, RFC 9457 problem responses, the Starlette middleware-ordering trap that drops `trace_id` from 500s, liveness vs readiness, typed settings, and the persistence traps: three-layer append-only enforcement, Alembic ENUM cleanup, async fixture scope, and the alembic credential mismatch every automated path routes around. Plus the two RBAC facts that only bite an "Admin **or** owner" rule: `admin` holds no write permission, and the `system` principal fails every permission check | self-written | 2026-08-23 |
| [`python-test`](python-test/SKILL.md) | Testing discipline — requirement-traceability markers, the negative-test emphasis, pytest config, running without pip, **why a green run with no database is a partial one**, the **forced write order for a fitted model row**, **choosing a metric that responds to what the fixture changed**, **how a journey test pins the steps it cannot drive**, **why a gate run needs a tree that holds still**, **why a value four declarations agree on can still not work**, **why loosening a tolerance means pinning the other side of it in the same commit**, and **why `git checkout --` on a file mid-edit destroys more than the injected defect**, **why seventeen tables refuse `TRUNCATE` and the suite empties itself at session end instead**, and **why a fixture that cannot express the failure is not coverage — one dense `interaction` book hid two defects four days apart**, **why counting calls in a worker handler must patch the source module rather than the handler**, and **why pinning a refusal code through a Job needs the handler's wrap checked first**, and **why two concurrent runs of the suite destroy each other through the one shared DSN** | self-written | 2026-08-24 |
| [`repo-architecture`](repo-architecture/SKILL.md) | How the monorepo is shaped and why — the annotated tree, the polyglot component map and why CI is three path-filtered workflow files rather than one, why the generated contract is committed under `docs/` while the frontend client is ignored, how `audit-docs.py` and `req-coverage.py` hold spec and code consistent, and the dependency-level stack choices decided against. `CLAUDE.md` §2 and §3 keep the rules only | self-written | 2026-08-23 |
| [`dev-commands`](dev-commands/SKILL.md) | Every command that builds, gates, migrates, benchmarks or demos this repo, each with the trap that makes the obvious form wrong — `uv sync --all-packages`, the **two-halved** gate, the exit-code pitfall **including vitest exiting 1 while printing every test as passed**, the 2.3x load-contention factor that reads as a regression, the alembic DSN the bare command does not use, and the pnpm-without-corepack way in. `CLAUDE.md` §11 keeps the bare invocations only | self-written | 2026-08-24 |
| [`library-spike`](library-spike/SKILL.md) | Empirically verify library behaviour where pip is unavailable — wheel fetching, version pinning, missing native libs — then land the finding across the suite | self-written | 2026-08-14 |
| [`vue-frontend`](vue-frontend/SKILL.md) | Frontend conventions specific to **this** platform — the generated-client seam, how money and exact decimals cross into TypeScript, the RFC 9457 error shape, cursor pagination, and the 202-plus-Job model, and the dev-identity proxy without which a browser gets 401 on everything | self-written | 2026-08-19 |
| [`reporter-cycle`](reporter-cycle/SKILL.md) | The team's 15-minute Slack status cycle and lead-staleness nudge — the outage flag that stops a token failure from spamming the log, why the token is read from disk on every call, quarter-mark cycle timing, the bare-timestamp marker format, and why the nudge is detected here but sent by the agent's own `SendMessage`, never the script | self-written | 2026-08-29 |
| [`balance-watch`](balance-watch/SKILL.md) | The DeepSeek balance poller — the endpoint, the BEGIN CLOSE and recovery-rearm thresholds and why each, the 15-minute elapsed heartbeat and why wall-clock quarter-hours are unreachable from a 90s poll, and the durable token source versus its ephemeral extracted cache | self-written | 2026-08-29 |

## External skills

### superpowers — the process set, and the one with precedence

Fourteen vendored from [`obra/superpowers`](https://github.com/obra/superpowers) (MIT,
© 2025 Jesse Vincent) on 2026-08-16 at the maintainer's request, from upstream v6.3.0
(`b36e082`, 2026-08-12), after a security review. **All fourteen were taken** — unlike the
Vue set, none teaches an approach `CLAUDE.md` has decided against, and the set is designed
to be read as one: `using-superpowers` routes to the others by name.

| Skill | Fills | Note |
|---|---|---|
| [`using-superpowers`](using-superpowers/SKILL.md) | The router — find and invoke a skill before responding | Read first. Its own "user instructions outrank skills" line is why the precedence rule had to be written into `CLAUDE.md` §12 to bind |
| [`brainstorming`](brainstorming/SKILL.md) | Turning an idea into a design before implementation | Bundles an optional local visual companion — see the security note below |
| [`writing-plans`](writing-plans/SKILL.md) | A written implementation plan, bite-sized, for an engineer with no context | Pairs with this repo's `spec-change`: the spec is the design, the plan is the execution order. Saves to `docs/plans/`, where the audit reads it — see the deviation below |
| [`executing-plans`](executing-plans/SKILL.md) | Executing a written plan in a fresh session, with review checkpoints | Upstream never named a plan location; here it reads from `docs/plans/` |
| [`subagent-driven-development`](subagent-driven-development/SKILL.md) | Fresh implementer subagent per task, review after each | Three bundled shell scripts; writes to an untracked `.superpowers/sdd/` |
| [`dispatching-parallel-agents`](dispatching-parallel-agents/SKILL.md) | 2+ independent tasks with no shared state | |
| [`systematic-debugging`](systematic-debugging/SKILL.md) | Root cause before any fix — symptom fixes are failure | The rule this repository already lives by: a spec/code disagreement is *resolved*, never quietly matched (`CLAUDE.md` §0) |
| [`test-driven-development`](test-driven-development/SKILL.md) | Test first, watch it fail, then implement | Complements `python-test` (markers, negative tests) and `testing-strategy` (technique) |
| [`verification-before-completion`](verification-before-completion/SKILL.md) | Evidence before any "it passes" claim | The generalisation of §13's "measured, not asserted" and §11's read-each-exit-code rule |
| [`requesting-code-review`](requesting-code-review/SKILL.md) | Dispatching a reviewer subagent with crafted context | |
| [`receiving-code-review`](receiving-code-review/SKILL.md) | Verify feedback before implementing it | |
| [`using-git-worktrees`](using-git-worktrees/SKILL.md) | Isolated workspace before feature work | Prefers the harness's native worktree tool over raw `git worktree` |
| [`finishing-a-development-branch`](finishing-a-development-branch/SKILL.md) | Deciding how completed work integrates | Decides *how* a branch ends; `git-hygiene` still supplies this repo's squash-merge, auto-delete and merge-order facts |
| [`writing-skills`](writing-skills/SKILL.md) | Creating and verifying skills — TDD applied to process docs | Supersedes nothing in *Conventions* below; read both when adding a skill |

**Where it overlaps a skill already here**, superpowers gives the procedure and the local
skill gives the facts:

| Superpowers | Local counterpart | Split |
|---|---|---|
| `test-driven-development` | `python-test`, `testing-strategy` | TDD sets the loop; `python-test` supplies `@pytest.mark.req`, the negative-test emphasis, and why a run without a database is partial |
| `systematic-debugging` | `contract-guard` | Root cause before a fix — and in the drift guard the *instrument* is a suspect: four defects were in the walkers rather than in the schemas, each reporting success while blind |
| `verification-before-completion` | `reproducing-ci-locally`, `close-workstream` | Evidence-before-claims is the rule; §11's two-halved gate and §13's audit are the commands |
| `finishing-a-development-branch`, `using-git-worktrees` | `git-hygiene` | Integration procedure vs this repo's `.gitignore`, branch and squash-merge specifics |
| `writing-plans`, `brainstorming` | `spec-change`, `adr-write` | How to reach a design vs where a decision is recorded and how its id behaves |
| `writing-skills` | *Conventions*, below | Authoring method vs this file's naming and `## Verified` requirements |

**Security review, 2026-08-16.** Skills only — the plugin's `hooks/`, `scripts/`, `tests/`
and packaging were not vendored. Across the fourteen: no network egress, no credential
access, no writes outside the invoking project. Every outbound URL in the prose points at
`platform.claude.com`, Anthropic's docs CDN, `code.claude.com`, `github.com`,
`agentskills.io` or the author's site. Four findings worth knowing:

- **`brainstorming` bundles a local web server** (`scripts/server.cjs`, ~26 KB) that binds
  `127.0.0.1` by default, gates requests on a per-session key and an `Origin` check, and
  launches a browser through `execFile` with the URL as an argv element rather than a
  shell string. It is opt-in — the skill works without it — and its host is overridable by
  `BRAINSTORM_HOST`, so **do not set that to a non-loopback address**.
- **`subagent-driven-development` writes into the working tree**: `.superpowers/sdd/` with
  a self-ignoring `.gitignore`, so it stays out of `git status` without touching a tracked
  file. Nothing to add to this repo's `.gitignore`; nothing should ever be committed
  from it.
- **`stop-server.sh` does `rm -rf "$1"`** on a caller-supplied session directory. The
  caller is the skill, passing the path `start-server.sh` printed — but it is an
  unqualified recursive delete, so never invoke it by hand with a path you assembled.
- **`using-superpowers` is written to compel** (`<EXTREMELY-IMPORTANT>`, "you do not have
  a choice"). That is upstream's mechanism for making skills fire rather than an attempt
  to redirect the agent, it defers explicitly to `CLAUDE.md`, and it is exactly the
  behaviour the maintainer asked for. Noted because prior reviews here recorded "no
  instructions aimed at the agent beyond their subject" — this set does not meet that
  description, deliberately.

**One deviation from upstream: where a plan is saved.** `CLAUDE.md` §12 keeps vendored
files as upstream wrote them; this is the third recorded exception, and the first that is a
project convention rather than a path that fails to resolve. Upstream saves plans to
`docs/superpowers/plans/`, and `executing-plans` never says where to find one at all. This
repository files them in `docs/plans/`, so five lines changed across four skills:
`writing-plans` (the save path, and the handoff sentence that quotes it back to the user),
`executing-plans` (step 1.2 now names the directory), and the worked examples in
`subagent-driven-development` and `requesting-code-review`.

The directory is load-bearing rather than a preference. `docs/plans/` sits inside
`scripts/audit-docs.py`'s scope, so a filed plan's links, requirement citations and tables
are checked like every other document in the suite — the 20 plans filed on 2026-08-22 cite
116 distinct requirements between them, and three real defects surfaced the moment they
moved in. `writing-plans` also gained a three-line pointer to `docs/plans/README.md`, which
carries the conventions — widened on 2026-08-24, when that file gained a section for the
three conventions the audit cannot check. Nothing else in the four skills changed; neither
`.superpowers/sdd/` nor `.planning/` moved, both still hold live scratch and both stay
git-ignored.

**Second deviation, 2026-08-29: `subagent-driven-development/scripts/task-brief` could not
read this repo's own plan format.** Confirmed empirically (exit 3 on every task) before
touching anything: this repo's `writing-plans` house pattern numbers tasks as `### 1.1 —
Title` (`docs/plans/2026-08-29-w11-scoring.md`, citing `docs/plans/2026-08-22-w5-
audit-remediation.md` as its precedent), grouping several tasks per `## Slice N` section in
one file; upstream's script only recognised a heading containing the literal word "Task"
followed by a bare integer, and had no rule to stop at a non-task heading, so the *last*
task in a slice ran on into the next slice's content once the missing-word bug was fixed
naively. Two changes to the vendored script: recognise `### N.M` headings too
(regex-escaping the task number's `.` so `1.1` cannot match `1x1`), and end collection at
any H1/H2 heading even when it is not itself a task heading — verified against Task 1.1
(stops before 1.2's heading), Task 1.5 (the last task in Slice 1; previously ran into
`## Slice 2`, now stops at the `---` before it), and Task 2.1 (a task in a different slice
section, to confirm the fix generalises rather than being fitted to one boundary).

**Correction, same day: this entry's "both additive (upstream's own `Task N` heading still
matches unchanged)" claim was false, caught by the lead running the control this entry
described but never actually showed.** Upstream's own `# Task N` heading is itself an H1 —
so the boundary rule above, written as a second, unconditional
`!infence && /^##?[ \t]/ { intask = 0 }` pattern-block, fired on that exact line and
immediately cleared the flag the task-match block had just set on the *same* record (awk
runs every matching block against a line, in order; the second undid the first). Reproduced
independently before changing anything: a synthetic `# Task 1` / `# Task 2` plan gave exit 3
on the version this entry originally shipped. Fixed by making the two rules mutually
exclusive — a single `if (task-heading) {…} else if (H1/H2) { intask = 0 }` inside one
pattern-block, rather than two separate always-evaluated ones — and re-verified: the same
synthetic plan now gives exit 0 with the correct body for both a mid-file task and the last
task in the file (running to EOF), and all three house-pattern checks above (Task 1.1, 1.5,
2.1) still pass unchanged. The lesson generalises past this one script: "additive, so X is
unchanged" is a claim about the *old* input still working, which self-tests, written and
run, are the only way to have actually checked before writing it down.

**Not installed: the SessionStart hook.** Upstream's plugin injects `using-superpowers`
into every session through `hooks/hooks.json`. That is plugin configuration rather than a
skill, it would run a command at the start of every session for anyone who clones this
repo, and `CLAUDE.md` §12's precedence rule achieves the same priority through a file the
agent already loads. Install the plugin separately if the automatic injection is wanted.

### python-skills — Python craft

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

### vue3-skills — frontend subject matter

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

**Recorded deviations** — where a vendored skill is hazardous *in this repository's conditions*
without being wrong upstream. §12 requires these written here rather than edited into the
vendored file.

| Skill | What it says | Why it does not hold here | Follow instead |
|---|---|---|---|
| `testing-strategy` | The "prove the guard fails" recipe reverts a fix with `git stash` | This repo runs parallel sessions in `.claude/worktrees/*`, and **the stash stack is shared by every worktree**. A bare `stash`/`stash pop` can pop a peer's entry into your tree. Upstream assumes one worktree, where the advice is sound | `git-hygiene`'s stash section — a WIP commit, or `stash push -m <tag>` and `apply <sha>`. The same sentence's *hand-edit* branch is also safe |

Not installed, worth revisiting when the phase needs them: `github-actions` (CI cost and
trigger hygiene), `performance` (Phase 2, NFR-RATE-1), `api-design` and
`web-app-architecture` (W2's FastAPI surface).

### planning-with-files — working memory on disk

One vendored from
[`OthmanAdi/planning-with-files`](https://github.com/OthmanAdi/planning-with-files)
(MIT, © 2026 Ahmad Adi) on 2026-08-16, at the maintainer's request, pinned at **v3.10.1
(`9b7d0a0`)**. Upstream's `LICENSE` is kept inside the skill directory.

| Skill | Fills | Note |
|---|---|---|
| [`planning-with-files`](planning-with-files/SKILL.md) | Plan state that survives `/clear`, compaction and session death — `task_plan.md`, `findings.md`, `progress.md` on disk, re-injected each turn | Five lifecycle hooks in its frontmatter; the templates and the Stop gate are the mechanism, not the prose |

**Only the English canonical skill was vendored.** Upstream ships 149 skill files — six
languages × mirrors for eighteen agents (`.codex/`, `.cursor/`, `.gemini/`, `.pi/`, …) —
plus its own test suite, packaging and a bundled Pi extension carrying a `package-lock.json`
with the AWS, Google and Mistral SDKs. None of that is reachable from Claude Code, and a
vendored copy is read by people as *the* copy. `commands/` was not taken either: those files
invoke `planning-with-files:planning-with-files`, the plugin-namespaced form, which does not
resolve for a project skill. The skill is `user-invocable`, so `/planning-with-files` is the
entry point here.

**Security review, 2026-08-16.** No network egress, no credential access, no writes outside
the invoking project — plan state goes to `./task_plan.md`, `./findings.md`, `./progress.md`
and `./.planning/`, all now gitignored at the repo root. No `eval`, and no shell string is
assembled from model output. Three things worth knowing:

- **`session-catchup.py` reads other agents' local transcripts** — `~/.claude/projects/`,
  `~/.codex/sessions/`, and an OpenCode SQLite store — to reconstruct what happened before a
  `/clear`. Read-only and local, but it is the one script that reaches outside the project,
  and what it reads is summarised straight into the model's context.
- **The Stop gate can refuse to let a session stop.** It is opt-in per plan via a `.mode`
  file; with no `.mode` present `check-complete --gate` never blocks, and `PLANNING_DISABLED=1`
  is a per-invocation escape. Verified here: in legacy mode it prints advice and exits 0.
- **Injected plan text is fenced** — the hook wraps it in `===BEGIN PLAN DATA===` and tells
  the model to treat the contents as data, not instructions. That is the right shape for a
  file the agent both writes and re-reads.

**Hooks fire only after the skill is invoked**, not at session start — Claude Code registers
skill-frontmatter hooks on invocation and keeps them for the rest of the session. Nobody who
never runs `/planning-with-files` pays for it. This is the material difference from the
superpowers `SessionStart` hook declined above, which would have run for anyone who cloned.

**One deviation from upstream, and why.** `CLAUDE.md` §12 keeps vendored files as upstream
wrote them; this file is the exception, recorded rather than silent. Upstream's five hook
commands resolve their script through `${CLAUDE_SKILL_DIR}`, then fall back to
`~/.claude/skills/…` and `~/.claude/plugins/marketplaces/…`. **All three miss a project-level
`.claude/skills/` checkout**, so as shipped the hooks register and then do nothing:

- `${CLAUDE_SKILL_DIR}` is substituted into the skill body and into `allowed-tools`, but not
  into hook command strings — in the v2.1.x build the skill constructor applies the
  replacement to the allowed-tools array and the prompt text while passing `hooks` through
  untouched;
- it is not exported to the hook process either. A hook receives `CLAUDE_PROJECT_DIR`, plus
  `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` for plugins. There is no `CLAUDE_SKILL_DIR`.

Measured: with `CLAUDE_SKILL_DIR` unset the command resolves to the empty string and exits 0
with no output — upstream's own README calls this being "silently hook-less". So each hook
gained **one** fallback entry, `$CLAUDE_PROJECT_DIR/.claude/skills/planning-with-files/scripts/…`,
ahead of the two upstream paths, and the body's `${CLAUDE_PLUGIN_ROOT}` references became
`${CLAUDE_SKILL_DIR}` — which *is* substituted, at every scope including plugins. Nothing else
changed. Verified after patching: resolves via `CLAUDE_PROJECT_DIR`, silent with no plan
present, injects the plan block when one exists, and the Stop gate stays non-blocking.

Worth reporting upstream: the same gap breaks every project-level install, not just this one.

### graphify — the repository as a knowledge graph

One vendored from [`Graphify-Labs/graphify`](https://github.com/Graphify-Labs/graphify)
(Apache-2.0) on 2026-08-16 at the maintainer's request, installed by the tool's own
`graphify install --project --platform claude` at CLI version **0.9.45**, after a security
review. It is not a hand-copied skill: the payload is regenerated by re-running the
installer, and `.graphify_version` records which CLI wrote it.

| Skill | Fills | Note |
|---|---|---|
| [`graphify`](graphify/SKILL.md) | Answering "where does X connect to Y" across a monorepo without grepping — a traversable graph of code, docs and papers, with every edge tagged `EXTRACTED` or `INFERRED` | Trigger `/graphify`. Output lands in `graphify-out/`, which is **git-ignored**: it is derived, and stale the moment code changes |

**Security review, 2026-08-16.** Markdown only under `.claude/skills/graphify/` — one
`SKILL.md`, eight `references/*.md`, and a `.graphify_version` stamp. No scripts, no
executables. The behaviour that needs stating is in the CLI it drives, not the skill text:

- **Code extraction is local.** tree-sitter AST parsing, deterministic, no LLM, no network.
  This is the pass that matters for this repository and it costs nothing.
- **The semantic pass over docs, PDFs, images and video is not.** It calls whichever LLM
  provider is configured through `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY`
  and friends, at that provider's own base URL. There is **no graphify-owned telemetry or
  upload endpoint** in the package — the only `graphify.com` references are in the README's
  marketing copy. `security.py` routes its own fetches through an SSRF-guarded connection.
- **Therefore: never point the semantic pass at real policy, claims or exposure data.**
  `examples/` carries freMTPL2, which is public. Nothing else in a deployment is.

**Two things the installer wrote were corrected rather than committed as-is**, and a
re-install will reintroduce both:

1. It registers `PreToolUse` hooks (`Bash|Grep` → `hook-guard search`, `Read|Glob` →
   `hook-guard read`) in **`.claude/settings.json`**, which this repo commits — and it
   resolves the command to an **absolute path** on the installing machine
   (`/home/<user>/.local/bin/graphify`). Committed, that hook is broken for every other
   clone and for CI. It lives in **`.claude/settings.local.json`** instead, which
   `.gitignore` already excludes. Each developer re-runs the installer to get their own.
2. It appends a `## graphify` section to the **root `CLAUDE.md`**, after §14, stating
   as fact that "this project has a knowledge graph at graphify-out/" — which is false
   until someone runs it, and false again in any clone. The root file is the governed
   project contract; that text lives in `.claude/CLAUDE.md`, phrased conditionally on the
   artifact existing.

**Running it on this repo: the docs half is parsed, not prompted.** `scripts/graphify-docs-extract.py`
emits graphify's semantic-extraction JSON for `docs/**/*.md` deterministically, because the
spec suite's structure is *written down* — requirement ids, ADR and `OQ-` citations, `§`
references — so parsing beats asking a model to infer them, and every edge is honestly
`EXTRACTED` at confidence 1.0. It also reads every `@pytest.mark.req` marker and emits a
requirement←test `implements` edge, which is what fuses the spec half of the graph to the
code half. Three things it took a wrong turn on first, all worth keeping:

- **Node ids must match the AST extractor's exactly** — full repo-relative path, extension
  dropped, each segment lowercased with non-alphanumerics collapsed to `_`. Get it wrong and
  the doc nodes do not dedupe onto the code nodes; they become orphan ghost duplicates and
  the graph silently gains a parallel, disconnected universe. Verify the overlap before
  building, not after.
- **Only the register defines an id.** `open-questions.md` defines each `OQ-`; a spec's §10
  mirrors it. Treating both as definitions produced 95 open questions where the repo has 52.
  Likewise an ADR *is* its document — a concept node beside it splits the citations in two.
- **Cross-check the result against `scripts/req-coverage.py`.** The first run reported 147
  evidenced requirements against the tool's 148; the missing one was `FR-PLAT-37`, whose
  marker lives in `examples/` — a directory the scan roots had omitted. A graph that
  disagrees with the authoritative tool is the failure this whole exercise exists to catch,
  so the diff is the check.

Run order for a full rebuild is graphify's own Steps 1–9 with this script standing in for
Part B. `graphify-out/` is git-ignored, so the graph is rebuilt rather than shared.

**Fourth pass, 2026-08-16 — installed on request, not from a gap analysis.** Worth saying
plainly: the three passes above searched for a skill and found (or rejected) one. This one
arrived as a maintainer instruction. The gap it happens to fill is real — `docs/` holds
eight specs, five journeys and five ADRs that cross-reference each other by requirement id,
and `audit-docs.py` checks those references exist without ever showing their *shape*.

### ui-ux-pro-max — design intelligence for the frontend

One vendored from
[`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
(MIT, © 2024 Next Level Builder) on 2026-08-17 at the maintainer's request, pinned at
**v2.15.0 (`a38d04c`, 2026-08-14)**. Upstream's `LICENSE` is kept inside the skill
directory.

| Skill | Fills | Note |
|---|---|---|
| [`ui-ux-pro-max`](ui-ux-pro-max/SKILL.md) | The design decisions no skill here covered — colour, typography, spacing, accessibility, chart choice — as a searchable local database rather than prose: 119 UX guidelines, 192 palettes, 74 font pairings, 25 chart types and 22 stacks | `vue-frontend` has the platform seams and `vue-best-practices` the Vue idiom; **neither says what a dense actuarial table or a diagnostics chart should look like**. `data/stacks/vue.csv` is a first-class stack and its first row independently agrees with `CLAUDE.md` §3 — Composition API and `<script setup>`, not Options API |

**Six of the seven skills that repository ships were not taken**, which is most of it: 10 MB
of the 14 MB payload and 5.8 MB of bundled TTFs. They are `claudekit`-authored bundles, not
the namesake skill, and the plugin's own description covers only `ui-ux-pro-max`:

| Not taken | Why |
|---|---|
| `ui-styling` | shadcn/ui on **Radix UI — React**, where `CLAUDE.md` §3 fixed Vue 3. Its `shadcn_add.py` shells `npx shadcn add`, which would write React components into a Vue app. The same exclusion `vue-jsx-best-practices` got, and for the same reason: an agent may follow it and the review that catches it is a human one. Carries 54 TTF font binaries for canvas poster rendering |
| `design` | Logo, icon and corporate-identity generation via **Google Gemini** (`gemini-3.1-pro-preview`), with the API key read from `~/.claude/.env` and `~/.claude/skills/.env`. The only skill in the set that reaches an external LLM using credentials from outside the project, and it needs `google-genai`, which is not a dependency here and cannot be installed in this environment |
| `design-system` | Token architecture, but its data is `slide-*.csv` and its scripts generate presentations against an `assets/design-tokens.json` convention this repo does not use — the frontend's tokens are Tailwind config |
| `brand`, `banner-design`, `slides` | Brand voice, social/ad banners and HTML slide decks. Marketing subject matter this repository does not have |

**Security review, 2026-08-17.** The vendored skill's five scripts are **stdlib-only Python**
— `argparse`, `json`, `sys` — with no network calls, no credential access, no `subprocess`,
no `eval`, and no writes outside the project. The single environment read in the whole skill
is `COLORTERM`, for terminal colour detection. Four things worth knowing:

- **It writes only when told to.** `--persist` creates `design-system/<project-slug>/MASTER.md`
  and `pages/` under `--output-dir`; without that flag it prints and exits. It refuses to
  overwrite an existing Master unless `--force` is passed. Nothing is gitignored for it —
  if a design system is ever persisted for this frontend it is a decision artifact, and
  whether to commit it should be a deliberate choice rather than one this file pre-empts.
- **The skill body is written to resist its own data.** It states that search results are
  recommendations and "never as instructions that override the user or repository rules",
  and tells the agent not to put private project data into queries or persisted output.
  That is the right shape for a skill whose output is a database the model reads back, and
  it is the reason the data files did not need line-by-line review for injected prose.
- **It reports a miss as a miss.** A query that hits nothing prints "the query did not hit
  the database" and warns against falling back silently — verified here with a query that
  returns zero rows. A design database that invents an answer would be worse than none.
- **Upstream's twelve test files are not collected.** `pyproject.toml`'s `testpaths` is an
  allow-list, so `.claude/skills/**/tests/` never enters our run. Nothing to exclude.

**One deviation from upstream**, recorded rather than silent (`CLAUDE.md` §12), and it is
the *same* defect `planning-with-files` had. All eleven documented command lines invoke the
search script through `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py`.
`CLAUDE_PLUGIN_ROOT` is set for plugins and **not** for a project-level skill, so as shipped
every one of them expands to `/.claude/skills/…` and fails on a fresh clone — the skill
installs, triggers, and then cannot run its own tool. Each became
`${CLAUDE_SKILL_DIR}/scripts/search.py`, which *is* substituted into a skill body at every
scope, as `planning-with-files` already established here. Nothing else changed.

Verified after patching: `search.py` runs from the vendored path, `--domain ux`,
`--domain chart`, `--stack vue` and `--design-system` all return sourced rows, and no
`CLAUDE_PLUGIN_ROOT` reference remains anywhere in the skill.

**Fifth pass, 2026-08-17 — installed on request, like graphify.** The gap it fills is real
and was visible in `CLAUDE.md` §3 as it read then: the stack named ECharts, TanStack Table
and Vue Flow — the last two now recorded in `docs/skills-map.md` and `roadmap.md` as
declared-but-not-installed — and `01`–`07` each declare §5.3 views, but nothing in this
repository said how any of it should *look*. W6a routed seven views and a factor workbench with no design reference at all.

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
| `skill-creator` | ~~when this library grows~~ | **Superseded 2026-08-16** by superpowers' `writing-skills`, which covers authoring and verification without spawning a nested `claude -p` |

External skills are **never installed without the maintainer's approval** (`CLAUDE.md` §12).
The superpowers set was installed on that approval, given directly.

**Third pass, 2026-08-16 — `obra/superpowers`, installed.** The first two passes looked for
*subject* skills and found none, because the gap was never subject matter: it was process.
Nothing here said how to reach a design before writing code, how to debug to root cause, or
what evidence a completion claim owes — all of which this repository had already learned the
expensive way and written into `CLAUDE.md` §0, §13 and §14 as standards for *documents*
rather than as a working method. Superpowers is that method, and it is pinned at v6.3.0
(`b36e082`) so the monthly upstream check has something to compare against.

## Conventions

- Kebab-case folder, one capability per skill, no overlap between skills.
- Frontmatter `name:` must equal the folder name; `description:` controls triggering, so
  it names the concrete artifacts and file paths involved, not just a topic.
- Every skill ends with a `## Verified` line: the date and **how** the procedure was
  confirmed — ideally citing a failure it actually caught.
