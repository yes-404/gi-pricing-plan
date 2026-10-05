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

Planned read-only: no test, no hook and no Claude Code session was run to produce this plan. Every
repository fact below was read at `origin/main` `809a3794af6d3a6ba688663b0d9b59f951190680`
(2026-10-05).

**What the Claude Code documentation says, read 2026-10-05.** Each sentence below is quoted from the page named, as the docs stood on that date:

- [Hooks reference](https://code.claude.com/docs/en/hooks.md): `${CLAUDE_PROJECT_DIR}` is the
  "Project root". Path placeholders "are substituted in hook commands and available as environment
  variables on spawned processes". On exit codes: "Exit 2: Blocking error; action is prevented.
  Other codes: Non-blocking error". It documents `"if"` as an "Optional permission rule" filter. It
  does not say which version added `if`.
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

## Status

`draft`. DP-1 and DP-2 are open, and the decision-maker rules them. Both have a recommendation that the
facts below support. No task starts before the ruling and the lead's go.

### Activation needs, in order

1. **The decision-maker's ruling on DP-1 and DP-2, merged**, and the lead's go, with a dispatch record in the form SL-1409's row
   cites (`DISPATCH-WK-1178-SL1409-2026-10-04`).
2. **A lane.** It is a small slice: one JSON line and one test file. The write set (§"Write set") is
   disjoint from every in-flight branch at `809a3794`, so it can run beside any other build under
   `RL-1263` (exempt / no shared path). It is a WK-1178 build, so the lead checks the same-Work rule in
   force at dispatch.
3. **Re-read at dispatch** (`docs/plans/README.md` convention 4): `git diff --name-only 809a3794
   origin/main -- .claude/settings.json scripts/hooks/retry_cap_hook.py tests/test_retry_cap_hook.py`.
   Any non-empty output: re-derive §"What happens today" before Task 1.

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
   in which `cd docs` is run and the next Bash call (`pwd`) succeeds. The executor runs it in a
   throwaway session, not its own.
6. **The two-half gate** (`CLAUDE.md` §11) passes on the head, through the gate-runner.
7. **Write set:** `git diff --stat origin/main...HEAD` lists only §"Write set" paths.

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
  If that filter were applied, a non-`record` command would never run the hook, and neither lock could
  have happened. **The locks show the hook ran for non-`record` commands.** Task 0 records why
  (whether the installed build, `claude --version` 2.1.289 on this VM at planning time, honours
  `if`). The answer does not change the fix: a `record` call after a `cd` would still be blocked.
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

### Write set, and its contention (`RL-1263`)

| Path | Change | Other work touching it | Consequence |
|---|---|---|---|
| `.claude/settings.json` | edited: `:9`, the command string, per DP-1 | none in flight (below) | none |
| `tests/test_hook_registration.py` | added | none | none |
| `scripts/hooks/retry_cap_hook.py` | **read only**, unless DP-2 (c) | none in flight | a DP-2 (c) edit is re-checked at dispatch |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry, exempt |

**In-flight branches read 2026-10-05.** Every `refs/remotes/origin/*` branch with commits ahead of
`origin/main` `809a3794` (237 branches; 60 open PRs), `git diff --name-only origin/main...<branch>`,
filtered on `^\.claude/settings|^scripts/hooks/|^tests/test_retry_cap_hook|^\.claude/skills/dev-commands|^\.claude/skills/README`.
Two branches match: `sl-1377-fd-1357-multi-factor-seed` (`.claude/skills/README.md`; PR #1087,
**merged**) and `wk1178-hold-hook-template` (`.claude/skills/dev-commands/SKILL.md`; PR #895,
**closed**). Neither is in flight. **No in-flight branch touches `.claude/settings.json`**, which
confirms the brief. Re-read at dispatch (activation need 3).

## Decision points

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-1 | What anchors the path? | (a) `python3 "$CLAUDE_PROJECT_DIR"/scripts/hooks/retry_cap_hook.py hook`, as the backlog entry names. (b) `python3 "$(git rev-parse --show-toplevel)"/scripts/hooks/retry_cap_hook.py hook`: the checkout the cwd is in. Fails if the cwd is outside any repository (`cd /tmp`), the same lock again. (c) (a) with (b) as a fallback: `"${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"`. | **(c)**. (a) is the form the docs give for project hook scripts, and the form this repository already uses (`planning-with-files`). But the docs do not say that a teammate's or a subagent's hook process gets the variable, and this team runs mostly as teammates. The fallback costs one expansion and covers that gap. If Task 0 shows the variable is set in every process kind, (a) is enough, and the ruling can say so. Under (c) the test (Acceptance 1) also runs one case with `CLAUDE_PROJECT_DIR` unset. |
| DP-2 | **Which copy runs in a worktree?** Today the relative path resolves in the cwd, so a session working in `.claude/worktrees/<x>` runs **that worktree's** `retry_cap_hook.py`. The docs say `CLAUDE_PROJECT_DIR` "stays put" at "the project root where the session started", so a session started in the root checkout that then enters a worktree runs the **root checkout's** copy under DP-1 (a). A teammate whose process *starts* in a worktree may get the worktree as its project root (not documented; Task 0 Step 3). The root checkout is not kept on `main` (it was on `main` at `809a3794` when read today, but it has been pinned to old branches before). | (a) Accept it: the root checkout's copy runs. The script changes rarely (last changed by `71f5a220`, 2026-09-17), and both copies read the same state file (`DEFAULT_STATE_FILE` is under `~`, `:77`). (b) Anchor on the cwd's checkout first (`git rev-parse --show-toplevel`), and use `CLAUDE_PROJECT_DIR` only when that fails: the worktree's copy runs, as today, but a `cd /tmp` would then fall back. (c) Keep (a)'s command, and have the script hand off to the cwd's checkout's copy when one exists (edits the script). | **(a)**, recorded in the ledger. The hook's behaviour is one decision function; a copy that differs between checkouts is a slice changing the hook, and that slice's executor tests by absolute path (`tests/test_retry_cap_hook.py:31`), which is not affected. (b) puts the old dependence on the cwd back in, the defect this slice removes. (c) adds code for a case with no recorded failure. Task 0 records which directory `CLAUDE_PROJECT_DIR` holds in each kind of worktree session; where it is the worktree, DP-2 does not arise for that kind, and the ledger says so. |

## Tasks

### Task 0: Record the hook environment (no committed code)

- [ ] **Step 1.** In a throwaway session started from the root checkout, register a scratch
  `PreToolUse` hook in `.claude/settings.local.json` (untracked; removed in Step 4) that appends
  `date -u`, `pwd` and `${CLAUDE_PROJECT_DIR-<unset>}` to a file in the executor's own `mktemp -d`.
  Run one Bash call. Record the line.
- [ ] **Step 2.** The same from a teammate process and from an in-session subagent (DP-1).
- [ ] **Step 3.** The same in a worktree session (`EnterWorktree`, and a teammate spawned with a
  worktree cwd) (DP-2).
- [ ] **Step 4.** Run one non-`record` Bash call and check whether the scratch hook carrying the same
  `if` filter as `:10` fired. Record the answer and the version (`claude --version`). Remove the scratch
  hook; `git -C <root> status --porcelain .claude/` prints nothing tracked.
- [ ] **Step 5.** Send the table to the lead before Task 1 if any answer differs from the
  recommendation's premise (DP-1: the variable is set everywhere; DP-2: it holds the root checkout).
  A different answer changes the ruled option, not the task list.

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

- [ ] **Step 1.** A throwaway session on the slice's branch runs `cd docs`, then `pwd`. Record both
  outputs and `date`. Under DP-2 (a), also record which copy ran (Task 0 Step 3's answer).

### Task 4: The gate and the ledger (Acceptance 6, 7)

- [ ] **Step 1.** No skill states the `cd` trap at `809a3794` (`grep -rn -i -E 'hook path is
  relative|never .?cd' .claude` prints nothing), so no skill is edited. The trap lives in briefs and in
  memory, and lifting it there is the lead's (Hand-off item 2).
- [ ] **Step 2.** The two-half gate through the gate-runner, then the ledger.

## Hand-off

1. The lead mints PL 9617 and SL 9618 (working ids) at the merge turn, and dispatches after activation
   needs 1 to 3.
2. On merge, the "never `cd`" line that every brief carries since the 15:24:59 BST entry can be lifted.
   That is the maintainer's (by delegation) call, on the ledger's Acceptance 5 line.
3. If Task 0 finds that `if` is not honoured by the installed build, the lead routes it to WK-1178 as a
   separate item. It does not block this slice.

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
