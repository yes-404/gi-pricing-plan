---
id: PL-9617
family: plan
kind: leaf
title: WK-1178 — the PreToolUse hook runs by absolute path, so a changed working directory cannot block every Bash call: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 809a3794af6d3a6ba688663b0d9b59f951190680
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-920, RL-1263]
---

# PL 9617 (working id) — WK-1178: the PreToolUse hook runs by absolute path, leaf plan

Filed under working id 9617 (this plan) and slice working id 9618 (its `SL-` row under WK-1178 in
[`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead. The lead mints both at the merge
turn.

**The backlog entry this plan discharges.** `to-lead.md` entry headed *"2026-09-30 14:54:23 BST — shell
restored; one WK-1178 backlog item (the hook path)"*, verbatim: *"My session was locked for about 5
minutes: after a \`cd frontend\` in one of my commands, the PreToolUse hook \`python3
scripts/hooks/retry_cap_hook.py\` (a **relative** path) failed on every Bash call, \`cd\` included; the
maintainer freed it. **WK-1178 backlog:** hook commands in the project settings use an absolute path
(\`$CLAUDE_PROJECT_DIR/scripts/hooks/…\`), so a changed cwd can't brick a session. Low priority; the
planner logs it."* The item was not logged in `docs/roadmap.md` at the time: `git grep -n -i -E
'relative path|absolute path|CLAUDE_PROJECT_DIR' origin/main -- docs/roadmap.md` prints nothing at
`809a3794`. This plan and its `SL-` row are where it is logged.

**Moved up by** the entry headed *"2026-10-05 15:24:59 BST — Applied items noted; #1159's two widenings
accepted in advance; a SALVAGE CHECK before dm-premint2 deletes anything; the cd-lock hook fix moves
up"*, item 4, verbatim: *"The cd self-lock (dm-premint today; a known class, the hook path is relative)
has now cost a session twice. The WK-1178 backlog item "hook absolute path" moves UP: it is small, a
planner can cut it when a slot frees, and until then every brief carries "never `cd` into a subdirectory;
use -C, --dir or absolute paths"."*

**Widened by** the entry headed *"2026-10-05 15:33:57 BST — #1162 amended (noted); ROUTING (a) and (b)
ACCEPTED; the \`__all__\` wording; FILL the slots"*, routing item (b), verbatim: *"(b) ACCEPTED: the
repository-root conftest.py (:20, :31; a bare pytest locks gate-{1,2}) goes into PL 9617's hook slice
(#1165, WK-1178) as one added task: the bare-pytest lock takes gate-1 only, red first (a test showing a
second bare pytest waits)."* The same entry accepts DP-1 and DP-2 (§"Decision points", "Accepted") and
routes the `if`-filter side finding (Hand-off item 3). *(Pre-mint edit, 2026-10-05 15:37:00 BST, by the
planner, on that entry: Task 4 added, and the gate task renumbered 4 → 5; the Goal, Status, Activation
needs 1 and 3, Acceptance 8–9, the Write set, the Decision points, Hand-off item 3 and Self-review item 5
amended to match. No other text changed.)*

**Corrected by** the entry headed *"2026-10-05 15:37:35 BST — CORRECTION to my 15:33:57 routing (a):
REVERSED; the skill, conftest and test move together into PL 9617; NFR-500 finding MEDIUM; WK-1250"*,
verbatim: *"CORRECTION: my 15:33:57 item (a) ("fold the dev-commands skill change into #1162") was wrong.
Verified at main: tests/test_root_conftest.py:317-323 asserts that the skill's \`for i in … ; do\n
flock -n -E 99 /tmp/slots/gate-$i\` loop names the same budget as conftest.py's \`_SLOT_COUNT\` ("both
must name the same budget"). The skill alone would turn #1162's python CI red. The three files change
together."* and *"DECIDED: (1) #1162 gets a plain REVERT commit of the skill fold (no force-push), so
the skill is back to main's text, including the migrate --verify wrapper (:276, :289), which RL 9620
:201 keeps at 2 verify slots: the executor's cut of it went past the ruling. (2) PL 9617's slice (#1165,
WK-1178) changes the skill's GATE loop, conftest \`_SLOT_COUNT\` 2→1 and test_root_conftest together, red
first; the gate slot only, verify untouched. (3) Until it lands, the one-gate rule holds by the lead's
dispatch (RL 9620's obligation 5). CLAUDE.md §12's "fix a wrong skill in the same session" is met by
recording the skill's known gap in #1165's plan, now, with the fix in the slice that can make it
consistently."* *(Pre-mint edit, 2026-10-05 15:42:01 BST, by the planner, on that entry: Task 4 now
changes the skill's gate loop and gate-slot text, `conftest.py` and `tests/test_root_conftest.py` in one
commit, red first; §"Known gap in the dev-commands skill" added; the Goal, Activation needs 2 and 3,
Acceptance 8–9, §"What happens today", the Write set, Task 5 Step 1 and Self-review item 5 amended to
match. #1162's revert is `381254c3`.)*

**Reframed by** the entry headed *"2026-10-05 16:47:09 BST — CORRECTION to my 16:46:42 hypothesis: the
\`if\` filter is BEST-EFFORT by design; the absolute path is the fix"*, verbatim: *"A docs check (the
official hooks reference) says: \`if\` uses permission-rule syntax and is evaluated BEFORE the hook
process spawns, for PreToolUse among others, BUT "matching is best-effort: when Claude Code cannot
determine which commands Bash will execute (e.g., in dynamic cases), it runs the hook regardless". So my
16:46:42 working hypothesis ("teammate sessions ignore \`if\`") is WITHDRAWN as the likely cause. The
probable mechanism: after a \`cd\` into a subdirectory, any Bash call that Claude Code cannot parse
statically (pipes, $(…), heredocs, compound or dynamic forms, which teammates use heavily) runs the hook
anyway, and the relative path exits 2 (blocking). My own next call was a simple \`cd … && pwd\`, parsed
and skipped. This is DOCUMENTED behaviour, not a reported bug: nothing in the docs or changelog reports
\`if\` being ignored.
Consequences for PL 9617 (#1165): (1) the absolute path is THE fix, and the docs' own pattern is
\`"$CLAUDE_PROJECT_DIR"/…\`; (2) whether CLAUDE_PROJECT_DIR is set in TEAMMATE sessions is
UNDOCUMENTED, so the plan's \`git rev-parse --show-toplevel\` fallback (DP-1) is required, not optional;
(3) Task 0's probe is reframed: show a non-parseable command from a subdirectory cwd running the hook
(red before the fix, green after). No "Claude Code bug" note in the skill: the best-effort semantics are
documented, and the skill should say so with the link."* The page's own wording, read by the planner at
16:48 BST the same day, differs from the entry's quoted phrase but says the same thing; it is quoted
below (§"What the Claude Code documentation says"). *(Pre-mint edit, 2026-10-05 16:49:10 BST, by the
planner, on that entry: the docs list gains the best-effort and absolute-path sentences, and its exit-2
quote is corrected to the page's text; §"What happens today" explains the locks by the documented
best-effort match; DP-1's fallback is required (no "(a) is enough" exit); Task 0 Step 4 is the red
probe and Task 3 and Acceptance 5 its green half, both with a non-parseable command; Task 5 Step 1, the
Write set row for the skill, Hand-off item 3 amended and Self-review item 6 added to match. No other text
changed.)*

Planned read-only: no test, no hook and no Claude Code session was run to produce this plan. Every
repository fact below was read at `origin/main` `809a3794af6d3a6ba688663b0d9b59f951190680`
(2026-10-05).

**What the Claude Code documentation says, read 2026-10-05.** Each sentence below is quoted from the page named, as the docs stood on that date:

- [Hooks reference](https://code.claude.com/docs/en/hooks.md): `${CLAUDE_PROJECT_DIR}` is the
  "Project root". Path placeholders "are substituted in hook commands and available as environment
  variables on spawned processes". On exit codes: "Exit 2 means a blocking error. On events that can
  block, exit 2 blocks whether or not you print JSON" (§"Exit code 2"; corrected 16:49 BST: the
  sentence first quoted here is not on the page as read at 16:48 BST). It documents `"if"` as an
  "Optional permission rule" filter. It does not say which version added `if`.
- Same page, [§"How `if` patterns match Bash commands"](https://code.claude.com/docs/en/hooks#bash-if-matching),
  read 2026-10-05 16:48 BST: "When Claude Code can't determine which commands the Bash input runs, it
  runs your hook regardless of the pattern. Because the `if` filter is best-effort, use the permission
  system rather than a hook to enforce a hard allow or deny." Its table adds that a pattern naming more
  than the command name runs the hook "anyway on `$()`, backticks, or `$VAR`". So `if` is a
  best-effort filter **by documented design**, not a reported defect.
- Same page, [§"Reference scripts by path"](https://code.claude.com/docs/en/hooks#reference-scripts-by-path):
  the placeholders "reference hook scripts relative to the project or plugin root, regardless of the
  working directory when the hook runs". §"Security best practices": "**Use absolute paths**: specify
  full paths for scripts. … In shell form, wrap it in double quotes"; the page's shell-form example is
  `node "${CLAUDE_PLUGIN_ROOT}"/scripts/format.js --fix`. That is the form DP-1 (c) takes.
- [Worktrees](https://code.claude.com/docs/en/worktrees.md): "`${CLAUDE_PROJECT_DIR}` stays put: it
  still points at the project root where the session started", and "`cwd` follows Claude … it moves
  again when Claude runs `cd`".
- **Not documented:** whether `CLAUDE_PROJECT_DIR` is set, and to what, in the hook processes of an
  agent-team teammate or a subagent; and which `.claude/settings.json` (the worktree's or the root's)
  a worktree session loads. Task 0 measures both.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or
> executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking. The executor also binds `test-driven-development` (the registered command is seen red,
> by its cause, before it changes), `python-test`, `dev-commands` (the gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s unchecked conventions before the first step. The executor is spawned
> from `.claude/roles/executor.md`. **The executor never `cd`s**, the defect this slice removes.
> Until it merges, a `cd` blocks every later Bash call in that session.

## Goal

The `PreToolUse` hook that `.claude/settings.json` registers finds `scripts/hooks/retry_cap_hook.py`
whatever the session's working directory is. A `cd` into a subdirectory no longer blocks every later
Bash call. A repository test runs the **registered** command string from a subdirectory and fails if
the path depends on the working directory.

A bare `uv run pytest -q` and the dev-commands gate wrapper both take the gate-1 lock only, so at most
one full gate runs on the box (`RL 9620`, working id). A second gate waits for gate-1; it never takes
gate-2. The `migrate --verify` wrapper keeps its 2 verify slots (Task 4).

## Status

`draft`. DP-1 and DP-2 are accepted as recommended (the 15:33:57 BST entry; §"Decision points",
"Accepted"). No task starts before the lead's go and the dispatch record.

### Activation needs, in order

1. **The decision-maker's ruling on DP-1 and DP-2, merged**, and the lead's go, with a dispatch record in the form SL-1409's row
   cites (`DISPATCH-WK-1178-SL1409-2026-10-04`). *The ruling half is met:* the maintainer (by
   delegation) accepted DP-1 and DP-2 in the 15:33:57 BST entry. The lead's go and the dispatch record
   remain.
2. **A lane.** It is a small slice: one JSON line and one test file. The write set (§"Write set") is
   disjoint from every in-flight branch at `809a3794`, so it can run beside any other build under
   `RL-1263` (exempt / no shared path). It is a WK-1178 build, so the lead checks the same-Work rule in
   force at dispatch. *Since Task 4:* the write set adds `conftest.py`, `tests/test_root_conftest.py`
   and `.claude/skills/dev-commands/SKILL.md`; no open PR touches any of them (§"Write set", re-read
   15:42 BST).
3. **Re-read at dispatch** (`docs/plans/README.md` convention 4): `git diff --name-only 809a3794
   origin/main -- .claude/settings.json scripts/hooks/retry_cap_hook.py tests/test_retry_cap_hook.py`.
   Any non-empty output: re-derive §"What happens today" before Task 1. For Task 4, the same with
   `conftest.py tests/test_root_conftest.py .claude/skills/dev-commands/SKILL.md`; any output
   re-derives Task 4's line numbers before its Step 1.

## Acceptance Standard

Each item is checked by a command run from the repository root on the slice's head. "Red first" means
the named test ran and failed **for the stated cause** before the change that turns it green
([`README.md`](README.md) rule 2); each red is recorded in the ledger with its printed failure line.

1. **The registered command survives a subdirectory cwd.** `uv run pytest -q
   tests/test_hook_registration.py` passes. Its test reads the `PreToolUse` command **from
   `.claude/settings.json`** (it never copies the string), runs it through `sh -c` with `cwd` set to a
   subdirectory of the repository (`docs/`), with the environment the DP-1 ruling names, and a Bash
   payload for a non-`record` command on stdin. It asserts exit 0 and an `allow` decision on stdout.
   **Seen red on `main`'s settings by its cause:** exit 2, with stderr containing `can't open file`
   and `scripts/hooks/retry_cap_hook.py`. A red for any other cause does not count.
2. **The same test passes from the repository root** (the negative control: the test does not go
   green by refusing every cwd, and does not go red for a reason other than the cwd).
3. **No hook command in a tracked settings file names a repository path relatively.** The same test
   file walks every `command` in `.claude/settings.json`'s `hooks` and asserts that each repository
   path it names is anchored the way DP-1 rules. Proven on broken input: the ledger records the test
   run against a scratch copy carrying `python3 scripts/hooks/retry_cap_hook.py hook`, failing.
4. **The existing hook suite is unchanged and green:** `uv run pytest -q tests/test_retry_cap_hook.py`.
5. **A live check in a real session (Task 3).** The ledger records, with `date` output, one session
   in which `cd docs` is run and the next Bash call, a **non-parseable** one (`echo "$(pwd)" | cat`),
   succeeds; and Task 0 Step 4's red for the same call on `main`'s settings. A parseable call (`pwd`)
   does not count: the best-effort `if` filter skips it before and after the fix. The executor runs
   both in a throwaway session, not its own.
6. **The two-half gate** (`CLAUDE.md` §11) passes on the head, through the gate-runner.
7. **Write set:** `git diff --stat origin/main...HEAD` lists only §"Write set" paths.
8. **One gate slot, red first (Task 4).** Two tests in `tests/test_root_conftest.py`, both seen red on
   `main`'s skill and `conftest.py` **by their cause** before either file changes; a red for any other
   cause does not count:
   - `test_slot_count_matches_the_dev_commands_gate_wrapper` (`:314-325`), expecting one gate slot.
     Red: its assert fails with `_SLOT_COUNT` and the wrapper loop both at 2.
   - `test_a_second_bare_run_waits_for_gate_1_and_never_takes_gate_2` (the `:270-311` test, rewritten
     in place). It uses the module's own `_SLOT_COUNT`, holds `gate-1`, and asserts that
     `_acquire_pytest_gate_slot()` printed `acquired after waiting`, never named `gate-2`, and left no
     `gate-2` file. Red: stderr carries `gate slot …/gate-2 acquired, proceeding` (`conftest.py:70`,
     `_SLOT_COUNT = 2`).
9. **Green, in one commit, gate only:** on the slice's head, `uv run pytest -q
   tests/test_root_conftest.py` passes. `git show --stat <the Task 4 commit>` lists the skill,
   `conftest.py` and `tests/test_root_conftest.py` together. The skill's `migrate --verify` wrapper and
   its verify-slot text are unchanged: `git diff origin/main...HEAD -- .claude/skills/dev-commands/SKILL.md
   | grep -c 'verify-'` prints `0`. Proven on broken input: the ledger records the rewritten test failing
   by Acceptance 8's cause with `_SLOT_COUNT` put back to 2 in a scratch edit.

## Global Constraints

- **Registration stays in the tracked `.claude/settings.json`**, never `.claude/settings.local.json`
  (`RL-920` §4, "Ruled: registration lives in a tracked `.claude/settings.json`; the scripts it
  registers…").
- **The hook's decision logic is unchanged.** `retry_cap_hook.py` already resolves its own files from
  `__file__` (`ROOT = Path(__file__).resolve().parents[2]`, `scripts/hooks/retry_cap_hook.py:76`;
  `DEFAULT_CORE_FILE`, `:78`). Only the path the command gives to `python3` is wrong. The script is
  not edited unless DP-2 (c) is ruled.
- **The `if` filter and the matcher are unchanged** (`.claude/settings.json:5` and `:10`). The filter
  matches the *user's* command (`Bash(python3 scripts/hooks/retry_cap_hook.py record*)`), not the
  hook's own path, so this fix does not touch it.
- **Fail-closed is kept.** A hook that cannot run still blocks; this slice removes the cause (a
  cwd-relative path), and adds no `[ -f … ] || exit 0` bypass. `F61` (`docs/findings/register.md:102`) already
  records that the layer can be bypassed; this slice adds no new way to bypass it.
- **No `cd` in any step**, the executor's own included.

## Scope

### Requirement coverage, each id individually

No `FR-` or `NFR-` id. The hook is a process mechanism (RFC-895 script C2; `delivery-process.md` §7,
"registered as a Claude Code `PreToolUse` hook in `.claude/settings.json`"), and its tests carry no
`req` marker, the same posture as `tests/test_retry_cap_hook.py`'s module docstring ("No
`@pytest.mark.req` marker: correctness of a process-mechanism script, not evidence for a numbered
platform requirement").

### What happens today — read, not measured

- `.claude/settings.json:9`: `"command": "python3 scripts/hooks/retry_cap_hook.py hook"`. The path is
  relative to the hook process's working directory.
- After a persisted `cd frontend`, `python3` cannot open the file and exits **2** (CPython's exit code
  for "can't open file"). In a `PreToolUse` command hook, exit 2 is the blocking exit ("Exit 2:
  Blocking error; action is prevented", the hooks reference above), so every Bash call is refused,
  `cd` back included. This matches both recorded locks (2026-09-30 14:54:23 BST and
  2026-10-05, the 15:24:59 BST entry).
- `.claude/settings.json:10` carries `"if": "Bash(python3 scripts/hooks/retry_cap_hook.py record*)"`.
  **The locks show the hook ran for non-`record` commands.** That is the documented behaviour, not a
  defect: the filter is best-effort, and a Bash call Claude Code cannot parse statically (a pipe,
  `$(…)`, a heredoc, a compound or dynamic form) runs the hook regardless of the pattern (the hooks
  reference, §"How `if` patterns match Bash commands", above). After a `cd`, every such call runs the
  hook, and the relative path exits 2. A plain parseable call (`pwd`) is matched and skipped, which is
  why a lock can look intermittent. *(Reframed 2026-10-05 16:49:10 BST on the 16:47:09 BST entry; the
  earlier text read the locks as a question of whether the installed build, `claude --version` 2.1.289
  at planning time, honours `if`.)* Either way the fix is the same: a `record` call after a `cd` would
  also be blocked.
- **Other hooks.** `git ls-files '.claude/settings*'` lists only `.claude/settings.json`; it holds this
  one hook. `.claude/settings.local.json` (untracked) holds no hooks. The only other hook commands in
  the tree are in `.claude/skills/planning-with-files/SKILL.md:10`, `:15`, `:20`, `:24`, `:29`. Four
  of them resolve their script through `$CLAUDE_PROJECT_DIR` already (the recorded deviation in
  `.claude/skills/README.md`, "So each hook gained **one** fallback entry,
  `$CLAUDE_PROJECT_DIR/.claude/skills/planning-with-files/scripts/…`"). `:20` tests `task_plan.md` in
  the cwd **on purpose**: it looks for a plan in the directory the session works in, and exits 0
  either way. It is out of scope.
- **Other scripts invoked relatively.** `.claude/roles/lead.md:79` tells the lead to run `python3
  scripts/hooks/retry_cap_hook.py record …`. That is the user's own command: after a `cd` it fails on
  its own, but it locks nothing. The `if` filter keys on this exact form, so it is not changed here.
- **How the hook is tested today.** `tests/test_retry_cap_hook.py` runs the script as a subprocess by
  its absolute path (`SCRIPT = ROOT / "scripts" / "hooks" / "retry_cap_hook.py"`, `:31`) with
  `cwd=ROOT`. It never reads `.claude/settings.json`, so it cannot see the registered command. That is
  why this defect passed the gate.
- **The bare-pytest lock (Task 4).** The repository-root `conftest.py` locks, for a bare run, the same
  `/tmp/slots/gate-{1,2}` files as the dev-commands wrapper (module docstring, `:19-24`). `_SLOT_COUNT =
  2` (`:70`). `_acquire_pytest_gate_slot` tries `gate-1` to `gate-<_SLOT_COUNT>` without blocking, and
  only when all are busy blocks on `gate-1` (`:111-133`). So today a second bare run takes `gate-2` and
  two full gates run at once, against `RL 9620`'s one. `tests/test_root_conftest.py`'s
  `test_slot_count_matches_the_dev_commands_gate_wrapper` reads the wrapper's `for i in … ; do` loop in
  `.claude/skills/dev-commands/SKILL.md` and asserts `_SLOT_COUNT == len(loop) == 2` (`:314-325`). So
  the skill's gate loop, `_SLOT_COUNT` and that test can change only together (the 15:37:35 BST
  entry). In the skill at `cdaaa573`: the gate loop is `for i in 1 2; do` (`:161`); the gate-slot text
  is `:180-183` ("two non-blocking attempts … at most two gates at once"), `:229-233` (conftest locks
  "`/tmp/slots/gate-{1,2}`") and `:356` ("2 gate slots, 2 verify slots"). The `migrate --verify`
  wrapper (`:276`, `:289`) is out of scope: `RL 9620` keeps 2 verify slots.

### Known gap in the dev-commands skill (recorded 2026-10-05, `CLAUDE.md` §12)

**Until this slice lands, `.claude/skills/dev-commands/SKILL.md` is wrong on one point:** its gate
wrapper (`:161`) still offers 2 gate slots, and its text (`:180-183`, `:229-233`, `:356`) still says
two gates may run at once. `RL 9620` (working id) allows one full gate at a time. Until Task 4 merges,
**the one-gate rule holds by the lead's dispatch** (`RL 9620`'s obligation 5), not by the wrapper or by
`conftest.py`. The skill is not edited alone: `tests/test_root_conftest.py:314-325` ties its loop to
`conftest.py`'s `_SLOT_COUNT`, so a skill-only edit reds the Python suite. This record meets `CLAUDE.md`
§12's "fixed in the same session" rule, per the 15:37:35 BST entry's DECIDED (3).

### Write set, and its contention (`RL-1263`)

| Path | Change | Other work touching it | Consequence |
|---|---|---|---|
| `.claude/settings.json` | edited: `:9`, the command string, per DP-1 | none in flight (below) | none |
| `tests/test_hook_registration.py` | added | none | none |
| `scripts/hooks/retry_cap_hook.py` | **read only**, unless DP-2 (c) | none in flight | a DP-2 (c) edit is re-checked at dispatch |
| `conftest.py` (repository root) | edited: `:70` `_SLOT_COUNT` 2 → 1; the docstring's slot wording (`:19-24`) (Task 4) | none in flight (below) | none |
| `tests/test_root_conftest.py` | `:255`, `:270-311` (rewritten in place) and `:314-325` (Task 4) | none in flight | none |
| `.claude/skills/dev-commands/SKILL.md` | the gate loop `:161` and the gate-slot text `:180-183`, `:229-233`, `:356`, `Verified` refreshed (Task 4); a note of the `if` filter's documented best-effort semantics, with the link (Task 5 Step 1). Never the verify wrapper `:276`, `:289` | none in flight (#1162 reverted its fold, `381254c3`) | none |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry, exempt |

**In-flight branches read 2026-10-05.** Every `refs/remotes/origin/*` branch with commits ahead of
`origin/main` `809a3794` (237 branches; 60 open PRs), `git diff --name-only origin/main...<branch>`,
filtered on `^\.claude/settings|^scripts/hooks/|^tests/test_retry_cap_hook|^\.claude/skills/dev-commands|^\.claude/skills/README`.
Two branches match: `sl-1377-fd-1357-multi-factor-seed` (`.claude/skills/README.md`; PR #1087,
**merged**) and `wk1178-hold-hook-template` (`.claude/skills/dev-commands/SKILL.md`; PR #895,
**closed**). Neither is in flight. **No in-flight branch touches `.claude/settings.json`**, which
confirms the brief. Re-read at dispatch (activation need 3).

**Re-read 2026-10-05 15:36 BST for Task 4's paths.** Each of the 61 open PRs' head branches,
`git diff --name-only origin/main...origin/<branch>` at `origin/main` `809a3794`, filtered on
`^conftest\.py$|^tests/test_root_conftest\.py$|^\.claude/skills/dev-commands/|^\.claude/settings|^scripts/hooks/|^tests/test_(retry_cap_hook|hook_registration)\.py$`.
One match: #1162 `dm-9620-rl1263-amend`, `.claude/skills/dev-commands/SKILL.md`. No open PR touches
`conftest.py` or `tests/test_root_conftest.py`. **Re-read 2026-10-05 15:42:01 BST**, the same filter over
the 63 open PRs at `origin/main` `cdaaa573`, after #1162's revert `381254c3`: no match.

## Decision points

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-1 | What anchors the path? | (a) `python3 "$CLAUDE_PROJECT_DIR"/scripts/hooks/retry_cap_hook.py hook`, as the backlog entry names. (b) `python3 "$(git rev-parse --show-toplevel)"/scripts/hooks/retry_cap_hook.py hook`: the checkout the cwd is in. Fails if the cwd is outside any repository (`cd /tmp`), the same lock again. (c) (a) with (b) as a fallback: `"${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"`. | **(c)**. (a) is the form the docs give for project hook scripts, and the form this repository already uses (`planning-with-files`). But the docs do not say that a teammate's or a subagent's hook process gets the variable, and this team runs mostly as teammates. The fallback costs one expansion and covers that gap. **The fallback is required, not optional** (the 16:47:09 BST entry, consequence (2)): a Task 0 reading that the variable is set in every process kind today does not remove it, because the docs do not promise it for teammates. Under (c) the test (Acceptance 1) also runs one case with `CLAUDE_PROJECT_DIR` unset. |
| DP-2 | **Which copy runs in a worktree?** Today the relative path resolves in the cwd, so a session working in `.claude/worktrees/<x>` runs **that worktree's** `retry_cap_hook.py`. The docs say `CLAUDE_PROJECT_DIR` "stays put" at "the project root where the session started", so a session started in the root checkout that then enters a worktree runs the **root checkout's** copy under DP-1 (a). A teammate whose process *starts* in a worktree may get the worktree as its project root (not documented; Task 0 Step 3). The root checkout is not kept on `main` (it was on `main` at `809a3794` when read today, but it has been pinned to old branches before). | (a) Accept it: the root checkout's copy runs. The script changes rarely (last changed by `71f5a220`, 2026-09-17), and both copies read the same state file (`DEFAULT_STATE_FILE` is under `~`, `:77`). (b) Anchor on the cwd's checkout first (`git rev-parse --show-toplevel`), and use `CLAUDE_PROJECT_DIR` only when that fails: the worktree's copy runs, as today, but a `cd /tmp` would then fall back. (c) Keep (a)'s command, and have the script hand off to the cwd's checkout's copy when one exists (edits the script). | **(a)**, recorded in the ledger. The hook's behaviour is one decision function; a copy that differs between checkouts is a slice changing the hook, and that slice's executor tests by absolute path (`tests/test_retry_cap_hook.py:31`), which is not affected. (b) puts the old dependence on the cwd back in, the defect this slice removes. (c) adds code for a case with no recorded failure. Task 0 records which directory `CLAUDE_PROJECT_DIR` holds in each kind of worktree session; where it is the worktree, DP-2 does not arise for that kind, and the ledger says so. |

**Accepted.** The entry headed *"2026-10-05 15:33:57 BST — #1162 amended (noted); ROUTING (a) and (b)
ACCEPTED; …"*, verbatim: *"#1165 PL 9617 @fa5f4dfb: DP-1 ($CLAUDE_PROJECT_DIR with a \`git rev-parse
--show-toplevel\` fallback) and DP-2 (the root checkout's script in worktrees) are accepted as
recommended."* So DP-1 is **(c)** and DP-2 is **(a)**. Task 0 still measures both premises; a different
answer goes to the lead (Task 0 Step 5).

## Tasks

### Task 0: Record the hook environment (no committed code)

- [ ] **Step 1.** In a throwaway session started from the root checkout, register a scratch
  `PreToolUse` hook in `.claude/settings.local.json` (untracked; removed in Step 4) that appends
  `date -u`, `pwd` and `${CLAUDE_PROJECT_DIR-<unset>}` to a file in the executor's own `mktemp -d`.
  Run one Bash call. Record the line.
- [ ] **Step 2.** The same from a teammate process and from an in-session subagent (DP-1).
- [ ] **Step 3.** The same in a worktree session (`EnterWorktree`, and a teammate spawned with a
  worktree cwd) (DP-2).
- [ ] **Step 4. The red probe** (the 16:47:09 BST entry, consequence (3)). Remove the scratch hook
  first; `git -C <root> status --porcelain .claude/` prints nothing tracked. Then, in a throwaway
  session on `main`'s `.claude/settings.json`, run `cd docs`, then one **non-parseable** Bash call, for
  example `echo "$(pwd)" | cat`. **Expected red:** the call is refused, the hook having run despite the
  `if` filter and exited 2 (`can't open file … scripts/hooks/retry_cap_hook.py`). Record both outputs,
  `date` and `claude --version`. A parseable call (`pwd`) is not the probe: it is matched and skipped,
  so it passes on `main` too. Free the throwaway session from outside it (it is locked by design).
- [ ] **Step 5.** Send the table to the lead before Task 1 if any answer differs from the
  recommendation's premise (DP-1: the variable is set everywhere; DP-2: it holds the root checkout),
  or if Step 4 is not red by its cause. DP-1's `git rev-parse` fallback stays in every case. A
  different answer changes the ruled option, not the task list.

### Task 1: The registration test, red first (Acceptance 1, 2, 3)

**Files:** add `tests/test_hook_registration.py`.

- [ ] **Step 1.** Write the test. It loads `.claude/settings.json` with `json`, takes every
  `hooks.PreToolUse[*].hooks[*].command`, and for each one runs
  `subprocess.run(["sh", "-c", command], input=<payload>, cwd=ROOT / "docs", env=<ruled env>, …)`.
  The payload is `{"tool_name": "Bash", "tool_input": {"command": "pwd"}}`. The state and core files
  are not passed: a non-`record` command returns before either is read (`cmd_hook`,
  `retry_cap_hook.py:294-306`), so the test writes nothing outside `tmp_path`. Assert `returncode == 0`
  and `"allow"` in the decision on stdout. Add the root-cwd case (Acceptance 2) and the static walk
  (Acceptance 3). Under DP-1 (c), add the `CLAUDE_PROJECT_DIR`-unset case.
- [ ] **Step 2.** Run `uv run pytest -q tests/test_hook_registration.py` on `main`'s settings.
  **Expected:** the `docs/`-cwd case fails with exit 2 and stderr `can't open file …
  scripts/hooks/retry_cap_hook.py`; the root case passes; the static walk fails naming `:9`'s
  command. Record the failure lines in the ledger.

### Task 2: The registered command, per DP-1 (Acceptance 1, 2, 3, 4)

**Files:** edit `.claude/settings.json:9` only.

- [ ] **Step 1.** Replace the command with the DP-1 form; the path is double-quoted, so a project
  path containing a space still works.
- [ ] **Step 2.** `uv run pytest -q tests/test_hook_registration.py tests/test_retry_cap_hook.py`:
  all pass.
- [ ] **Step 3.** Broken-input proof (Acceptance 3): copy the settings to `tmp_path` with the old
  relative form, point the static walk at it, and see it fail. Record the line.

### Task 3: The live check (Acceptance 5)

- [ ] **Step 1. The green half of Task 0 Step 4's probe.** A throwaway session on the slice's branch
  runs `cd docs`, then the same non-parseable call as Task 0 Step 4 (`echo "$(pwd)" | cat`), then
  `pwd`. Record the outputs and `date`. The non-parseable call must succeed: a `pwd` alone proves
  nothing, because the `if` filter skips it on `main` too. Under DP-2 (a), also record which copy ran
  (Task 0 Step 3's answer).

### Task 4: One gate slot — the skill's gate loop, `conftest.py` and the test together, red first (Acceptance 8, 9)

**Files, all in ONE commit:** edit `.claude/skills/dev-commands/SKILL.md` (gate only); edit
`conftest.py` (repository root); edit `tests/test_root_conftest.py`. Never the skill's `migrate
--verify` wrapper (`:276`, `:289`) or its verify-slot words: `RL 9620` keeps 2 verify slots. Line
numbers are at `cdaaa573`.

- [ ] **Step 1. The tests first.** In `tests/test_root_conftest.py`:
  - `test_slot_count_matches_the_dev_commands_gate_wrapper` (`:314-325`): expect one gate slot
    (`== 1`), and change its docstring's `for i in 1 2 …` to `for i in 1`.
  - Rewrite `test_a_full_slot_set_falls_through_to_the_blocking_wait_path` (`:270-311`) in place as
    `test_a_second_bare_run_waits_for_gate_1_and_never_takes_gate_2`: drop the `_SLOT_COUNT`
    monkeypatch (`:286`); hold only `gate-1` with a real `LOCK_EX | LOCK_NB` flock on a separate open
    file (`:287-293` held both); keep the `threading.Timer` release after 0.3 s; call
    `_acquire_pytest_gate_slot()`, then `_release_pytest_gate_slot()`. Assert stderr contains
    `acquired after waiting` and does not contain `gate-2`, and `(slot_dir / "gate-2").exists()` is
    false. The wait-message assert uses `conftest_module._SLOT_COUNT`, not a literal.
  - `test_acquire_holds_a_real_exclusive_flock_and_release_frees_it`: drop its `_SLOT_COUNT`
    monkeypatch (`:255`), now the module's own value.
- [ ] **Step 2. Red, by cause.** `uv run pytest -q tests/test_root_conftest.py` on `main`'s skill and
  `conftest.py`. **Expected:** exactly the two tests of Acceptance 8 fail, each by its stated cause.
  Record both failure lines in the ledger. The red is not committed alone.
- [ ] **Step 3. The skill, gate only.** `:161` `for i in 1 2; do` → `for i in 1; do` (keep the wrapper
  shape: one non-blocking attempt, then the blocking wait on `gate-1`). The gate-slot text: `:180-183`
  (one non-blocking attempt; at most one gate at once, `RL 9620`), `:229-233` (`/tmp/slots/gate-1`),
  `:356` ("1 gate slot, 2 verify slots", citing `RL 9620`). Refresh `Verified` (`:1063`) with the tree.
- [ ] **Step 4. `conftest.py`.** `_SLOT_COUNT = 1` (`:70`; its comment cites `RL 9620` by its minted
  id); the docstring's `/tmp/slots/gate-{1,2}` and "the same two slots" (`:19-24`) name the one slot.
  The wait message's format is unchanged.
- [ ] **Step 5. Green.** `uv run pytest -q tests/test_root_conftest.py`: all pass. Then the broken-input
  proof (Acceptance 9): `_SLOT_COUNT = 2` in a scratch edit, the rewritten test fails by its cause,
  record the line, revert. Commit Steps 1, 3 and 4 as one commit.

### Task 5: The gate and the ledger (Acceptance 6, 7)

- [ ] **Step 1.** No skill states the `cd` trap at `809a3794` (`grep -rn -i -E 'hook path is
  relative|never .?cd' .claude` prints nothing), so no skill is edited for it. The trap lives in briefs
  and in memory, and lifting it there is the lead's (Hand-off item 2). **Beside Task 4's gate-slot edit,
  one more skill edit:** `.claude/skills/dev-commands/SKILL.md` and the ledger record the **documented**
  semantics of `.claude/settings.json:10`'s `if`, with the link
  (<https://code.claude.com/docs/en/hooks#bash-if-matching>): the filter is best-effort, and a Bash
  call Claude Code cannot parse statically runs the hook regardless of the pattern. So the hook
  command must work from any cwd, which this slice's absolute path gives. They record it as documented
  behaviour, never as a Claude Code bug, with Task 0 Step 4's red and `claude --version`, and the
  skill's `Verified` date refreshed (Hand-off item 3).
- [ ] **Step 2.** The two-half gate through the gate-runner, then the ledger.

## Hand-off

1. The lead mints PL 9617 and SL 9618 (working ids) at the merge turn, and dispatches after activation
   needs 1 to 3.
2. On merge, the "never `cd`" line that every brief carries since the 15:24:59 BST entry can be lifted.
   That is the maintainer's (by delegation) call, on the ledger's Acceptance 5 line.
3. The `if` filter is best-effort **by documented design** (the hooks reference,
   [§"How `if` patterns match Bash commands"](https://code.claude.com/docs/en/hooks#bash-if-matching)):
   a Bash call Claude Code cannot parse statically runs the hook regardless of the pattern. It is not a
   reported bug, and nothing is raised against Claude Code. The ledger and the dev-commands skill state
   the documented semantics with the link (Task 5 Step 1). The absolute path is the fix; the filter is
   not relied on to keep the hook from running. *(Pre-mint edit 2026-10-05 16:49:10 BST, on the
   16:47:09 BST entry: this item said "If Task 0 finds that \`if\` is not honoured by the installed
   build, it is Claude Code's behaviour … it is not ours to fix", and that reading is withdrawn.)*
   *(Earlier pre-mint edit 2026-10-05, on the 15:33:57 BST entry: "Task 0 measures it. If it
   is a Claude Code behaviour, record it in the plan and the dev-commands skill; it is not ours to fix."
   The earlier text routed it to WK-1178 as a separate item.)*

## Self-review

1. **The brief, clause by clause.** The settings change: Task 2, DP-1. Other hooks or scripts with a
   relative path: §"What happens today", "Other hooks" and "Other scripts". A red-first test that fails
   with the relative form from a subdirectory and passes with the absolute form: Task 1, Acceptance 1
   and 2. How the hook is tested now: §"What happens today", last bullet. `$CLAUDE_PROJECT_DIR` for
   teammates: not documented, so DP-1 recommends the `git rev-parse` fallback; Task 0 Step 2 measures it.
   The worktree: the docs say the variable stays at the start directory, so DP-2 is open; Task 0
   Step 3 measures it. `RL-1263` contention: §"Write set". `settings.json` is touched by no
   in-flight branch: confirmed.
2. **The test reads the registered string.** A test that copied the command would stay green after
   someone reverts `settings.json`. Acceptance 1 forbids the copy.
3. **Placeholders.** The command form is fixed by DP-1's ruling, stated as such. No other value is open.
4. **Ids.** No `FR-`/`NFR-` id is cited. `RL-920`, `RL-1263` and `F61` are on `main`. This plan's own
   ids are written as working ids, never hyphenated in prose.
5. **The added task, against routing (b) and the 15:37:35 BST DECIDED (2)–(3).** "the bare-pytest lock
   takes gate-1 only": Task 4 Step 4. "red first (a test showing a second bare pytest waits)": Task 4
   Steps 1–2, Acceptance 8, red by its cause. "changes the skill's GATE loop, conftest `_SLOT_COUNT`
   2→1 and test_root_conftest together": Task 4, one commit, Acceptance 9. "the gate slot only, verify
   untouched": Task 4 Step 3 and Acceptance 9's `verify-` count. "recording the skill's known gap":
   §"Known gap in the dev-commands skill". The `conftest.py` change is one constant; the blocking-wait
   path it falls to (`:122-133`) is unchanged.
6. **Against the 16:47:09 BST entry, consequence by consequence.** (1) "the absolute path is THE fix":
   Goal and Task 2, unchanged; the docs' shell form, quoted, is in §"What the Claude Code documentation
   says". (2) "the plan's \`git rev-parse --show-toplevel\` fallback (DP-1) is required, not optional":
   DP-1's recommendation and Task 0 Step 5. (3) "show a non-parseable command from a subdirectory cwd
   running the hook (red before the fix, green after)": Task 0 Step 4 (red), Task 3 Step 1 (green),
   Acceptance 5. "No "Claude Code bug" note in the skill … the skill should say so with the link":
   Task 5 Step 1, the Write set row and Hand-off item 3. The withdrawn "teammates ignore \`if\`"
   reading appears nowhere as a premise.
