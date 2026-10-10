---
id: PL-1602
family: plan
kind: leaf
title: WK-1178 — the PreToolUse hook runs by absolute path, so a changed working directory cannot block every Bash call: leaf plan
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-10            # original date 2026-10-05, set at the draft; minted 2026-10-10
owner: planner
tree: fe0b0627590307259ec6d56be7f73115cf245092
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-920, RL-1263, RL-1445]
---

# PL-1602 — WK-1178: the PreToolUse hook runs by absolute path, leaf plan

Filed under working id 9617 (this plan) and slice working id 9618 (its `SL-` row under WK-1178 in
[`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead; minted as PL-1602 and SL-1603
on 2026-10-10 in the D8b batch mint PR (the body below was written under the working ids; where it
says "working id" for either, read the minted id).

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
repository-root conftest.py (:20, :31; a bare pytest locks gate-{1,2}) goes into PL-1602's hook slice
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
:201 keeps at 2 verify slots: the executor's cut of it went past the ruling. (2) PL-1602's slice (#1165,
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
Consequences for PL-1602 (#1165): (1) the absolute path is THE fix, and the docs' own pattern is
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

**Ordered built by** the entry headed *"2026-10-10 16:28:30 BST — RULING: FD 9959 (cd slips, MEDIUM, 14
today / 19 since 3 Oct). Fix the ROOT CAUSE: build PL 9617 (absolute hook path) NOW; the cd guard is NOT
built (deferred, conditional)"*, verbatim:

> Your diagnosis: the only PreToolUse hook is invoked by a RELATIVE path. After a persisting `cd`, python exits 2 and the session locks out. That is the defect; the cd is only its trigger. PL-1602 (the absolute path, already accepted) removes it: with an absolute path, a cd no longer breaks the hook at all.
> 1. BUILD PL 9617 NOW, right after the FD-1374 slice frees gate-1 and before PL 9955 A. Proof:
>    (i) a positive control: from a seat, `cd` into a worktree subdirectory, then run a guarded command; the hook still runs (no exit 2, no lock-out);
>    (ii) the same at main without the fix reproduces the exit 2 (red-first);
>    (iii) the hook still refuses what it refused before (its own tables unchanged).
> 2. The no_cd_hook.py guard is NOT built now:
>    - Once the root cause is gone, a cd causes no lock-out, so the guard would treat a symptom.
>    - It would also apply to EVERY Claude session in this repo, including the user's own: refusing cd is a tooling change the user did not ask for.
>    - The subshell form `(cd x && cmd)` does not move the session's cwd, so refusing it would be wrong on the facts.
>    CONDITION to revisit: if, after PL 9617 lands, a slip still WRITES OUTSIDE its worktree (the remaining harm), bring the evidence and a guard proposal, and I put it to the user.
> 3. FD 9959 records the mechanism, the 14/19 count with its predicate, each instance, and remedy (1). It rides D8, and closes when PL-1602's slice merges with the positive control green.

So: proofs (i), (ii) and (iii) are Acceptance 5, 5r and 10 below; **FD-1598 closes when this
slice merges with proof (i) green** (Hand-off item 4). **Out of scope:** the `no_cd_hook.py` guard (FD-1598
option (b)'s second half) and any refusal of `cd`; the charter no-`cd` rule in `.claude/roles/*.md` is
untouched. **Revisit condition**, the ruling's own: a slip that still writes outside its worktree after this
slice lands goes to the lead with the evidence and a guard proposal. FD-1598 is the draft at
`origin/draft/fd-9959-cd-slips` @`6af324b2` (its §"The mechanism", read for this refresh, matches
§"What happens today" below). *(Refresh 2026-10-10 by planner-pl9617, read 16:28–16:38 BST, on that entry: this
paragraph added; the Status, Activation needs, Acceptance 5 and 10, Tasks 0, 1, 3 and 5, DP-3 and DP-4,
§"The root checkout and the settings change", the Write set, Hand-off and Self-review 7 amended to match.
#1165, this plan's PR, was closed on 2026-10-09 as absorbed into process-backlog row "2026-10-09
10:54:55 BST" (`docs/process/process-backlog.md:55` at `fe0b0627`); this branch was kept and is the
plan's only copy.)*

### Refresh 2026-10-10 — what changed since 5 Oct

Re-read at `origin/main` `fe0b0627590307259ec6d56be7f73115cf245092` (fetched 2026-10-10 16:29 BST), read-only:
no test, hook, check or Claude Code session was run. Each changed fact is also marked where it sits.

1. **`.claude/settings.json` is unchanged** (`git diff --stat 809a3794 origin/main -- .claude/settings.json
   scripts/hooks/ tests/test_retry_cap_hook.py conftest.py tests/test_root_conftest.py` prints nothing for
   those five paths). It still holds exactly **one** hook, `PreToolUse`, matcher `Bash`, `:9`
   `python3 scripts/hooks/retry_cap_hook.py hook`, `:10` its `if`. `.claude/settings.local.json` (root,
   untracked) holds only `permissions.deny: []`. **All hook entries, user scope too:**
   `~/.claude/settings.json` registers 13 hook commands (caveman, on `SessionStart`, `UserPromptSubmit`,
   `PreToolUse` ×2, `PostToolUse`, `PostToolUseFailure`, `PreCompact`, `PostCompact`, `SubagentStart`,
   `SubagentStop`, `Stop`, `SessionEnd`), every one by an absolute path (`/home/puzhenhao1989/.caveman/…`,
   `/home/puzhenhao1989/.npm-global/…`), so none depends on the cwd; they are not this slice's.
   `~/.claude/settings.local.json` does not exist.
2. **`RL 9620` is minted as `RL-1445`** (`docs/rulings/RL-01445-…md`, "Minted 2026-10-06 as RL-1445 from
   working id 9620"). Outside verbatim quotes, every `RL 9620` below now reads `RL-1445`.
3. **The dev-commands skill moved** (+45/−1 since `809a3794`): the gate loop is still `:161`; the gate-slot
   text is `:180-184`, the conftest paragraph `:236-240`, the verify wrapper `:283` and `:296`, the budget
   line `:363-364`, `Verified` `:1106`. **New since 5 Oct:** the gate-2 standing rule (`:192`, the entry
   "2026-10-10 03:41:56 BST"): gate-2 may run ONE docs check beside ONE code gate on gate-1; "Two
   concurrent code gates remain NOT allowed". Task 4 is consistent with it: the wrapper and a bare
   `pytest` (both code gates) take gate-1 only; a docs check takes gate-2 by its own `flock`, and the docs
   pytest subset is a targeted run, which `conftest.py` never locks (`_is_bare_full_run`, `conftest.py`
   `:79-103`). Task 4's text edits must keep `:192` true.
4. **A skill now states the `cd` trap with the relative path as its reason:**
   `.claude/skills/mint-and-finish/SKILL.md:28-30` ("Why: the hook path is relative; a `cd` moves the
   guard …"). Task 5 Step 1's 5 Oct claim "no skill states the `cd` trap" is no longer true. After this
   slice the first half of that reason is false, so the slice edits that clause (the rule stays: 16:28:30
   item 2) and refreshes its `Verified` (`CLAUDE.md` §12). The same reason sits in seven role files (`git
   grep -c -i -E 'never .?cd' origin/main -- .claude/roles` = 1 in each of auditor, decision-maker, executor,
   lead, planner, reporter, watcher); a role file is the maintainer's, so that is Hand-off item 5, not
   the write set.
5. **`.claude/roles/lead.md`'s `record` line moved** from `:79` to `:81`.
6. **The docs changed** (re-read 2026-10-10; §"What the Claude Code documentation says"): the hooks
   reference now prefers **exec form** (`args`) for a hook naming a path placeholder; exec form has no
   shell, so DP-1 (c)'s `git rev-parse` fallback cannot be written in it. New DP-3. The page also says
   hooks from settings files run inside subagents, and still says nothing about teammates.
7. **`CLAUDE_PROJECT_DIR` in a teammate:** in this planner's own teammate session the Bash tool's
   environment has it **unset** (`echo "${CLAUDE_PROJECT_DIR-<unset>}"` → `<unset>`, 2026-10-10 16:34:34 BST,
   cwd the root checkout). That is the Bash tool's environment, not a hook process's (the docs export it
   "on the spawned process" of a hook), so it is not Task 0's answer; it is one more reason DP-1's fallback
   is required, and Task 0 Step 2 still measures the hook process.
8. **The root checkout** is on `main` @`8f5a8987` (2026-10-06), behind `origin/main`; it is not on an old
   branch today, and it does not auto-pull. New §"The root checkout and the settings change".
9. **Contention:** `gh pr list --state open` returns **0** open PRs (2026-10-10 16:32 BST). The branch sweep
   of 5 Oct was **not** re-run: both gate slots were held (`flock -n -E 75` rc 75 on gate-1 and gate-2 at 16:32 and again
   16:34:34 BST), and the sweep-pause rule (`planner.md`) pauses any batch. Activation need 5 re-reads at
   dispatch.
10. **The fail-closed constraint meets FD-1598's fail-open proposal**: FD-1598 option (b) item 1 asks for
    a fail-open wrapper ("if the file is not found, exit 0, never 2"); this plan's Global Constraints say
    fail-closed, no `[ -f … ] || exit 0`. The 16:28:30 ruling names PL-1602 ("already accepted") and does
    not rule this. New DP-4.

Planned read-only: no test, no hook and no Claude Code session was run to produce this plan. Every
repository fact below was read at `origin/main` `809a3794af6d3a6ba688663b0d9b59f951190680`
(2026-10-05), and re-read at `fe0b0627` on 2026-10-10 (§"Refresh 2026-10-10"; where a fact changed,
the text says so).

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

**Re-read 2026-10-10** ([hooks reference](https://code.claude.com/docs/en/hooks), fetched 2026-10-10 between 16:29:39 and 16:32:34 BST by
planner-pl9617; the page is long and only its first 100,000 characters were read, so a sentence beyond
them is not ruled out). Changed or new since 5 Oct, each quoted:

- §"Exec form and shell form": "A command hook runs as exec form when `args` is set, and shell form when
  `args` is omitted. Set `args` whenever the hook references a path placeholder". "**Exec form** … There
  is no shell … path placeholders like `${CLAUDE_PLUGIN_ROOT}` are substituted into `command` and into
  each `args` element as plain strings. Special characters such as apostrophes, `$`, and backticks pass
  through verbatim". "**Shell form** runs when `args` is absent. The `command` string is passed to a
  shell: `sh -c` on macOS and Linux". Both forms "export them as the environment variables
  `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`, and `CLAUDE_PLUGIN_DATA` on the spawned process". So exec
  form cannot carry DP-1 (c)'s `$(git rev-parse --show-toplevel)` fallback (DP-3).
- §"Reference scripts by path": "`${CLAUDE_PROJECT_DIR}`: the project root where the session started",
  and "Prefer exec form for any hook that references a path placeholder. In shell form, wrap each
  placeholder in double quotes." The page says nothing about an unset or empty placeholder.
- §"Common fields": "Handlers run in the current directory with Claude Code's environment. If the current
  directory no longer exists, for example a worktree or temp directory that another shell deleted
  mid-session, Claude Code runs command hooks from the first of these that still exists: the directory
  the session started in, the project root, your home directory, or the system temp directory." This
  confirms the hook's cwd is the session's current directory, the mechanism of the lock.
- The `if` and exit-2 sentences quoted above (5 Oct) still read the same, and hooks from settings files
  "also run inside" subagents. **Still not documented:** `CLAUDE_PROJECT_DIR` in a teammate's hook
  process, and whether `!`-prefixed user commands pass through `PreToolUse` (not found in the part read).
  Both stay Task 0 probes.

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
one full gate runs on the box (`RL-1445`, minted from working id 9620). A second gate waits for gate-1; it never takes
gate-2. The `migrate --verify` wrapper keeps its 2 verify slots (Task 4).

## Status

`draft`. DP-1 and DP-2 are accepted as recommended (the 15:33:57 BST entry; §"Decision points",
"Accepted"). The build is **ordered** by the 16:28:30 BST entry of 2026-10-10 (above). DP-3 and DP-4 are
open (new 2026-10-10). No task starts before the GO and the dispatch record.

### Size and lane (2026-10-10)

**Size: about 0.5 lane-day**, by task: Task 0 and Task 3 (the two throwaway-seat probes, red then green)
about 1.5 h; Tasks 1 and 2 (one test file, one JSON line) about 1 h; Task 4 (the gate-slot commit, red
first) about 1.5 h; Task 5 (two skill clauses, the gate, the ledger) about 1 h plus one full gate. The
hook half alone (Tasks 0–3 and 5) is about 0.3 lane-day.

**Lane:** no named serial set. The write set touches neither `compile.py` nor `analysis.py` (the serial
sets named in `docs/roadmap.md`, e.g. `:2156`), and no other plan claims `.claude/settings.json`,
`scripts/hooks/**`, `tests/test_hook_registration.py`, `conftest.py` or `tests/test_root_conftest.py`.
Two cautions, not serial sets: `conftest.py` and `.claude/settings.json` act on **every** run and
**every** session on the box (§"The root checkout and the settings change"), so the slice's own gate is
the only gate that may see a half-changed file; and `.claude/skills/dev-commands/SKILL.md` is edited by
process PRs often (3 commits since `809a3794`: `git log --oneline 809a3794..fe0b0627 -- .claude/skills/dev-commands/SKILL.md`), so it is re-read at dispatch.

### Activation needs, in order

*(Rewritten 2026-10-10 by planner-pl9617 on the 16:28:30 BST entry. The 5 Oct list was: 1 the DP-1/DP-2
ruling and the lead's go with a dispatch record; 2 a lane, "disjoint from every in-flight branch at
`809a3794`"; 3 the re-read at dispatch. Needs 1, 4 and 5 below carry them.)*

1. **DP-1 and DP-2 ruled — MET** (the 15:33:57 BST entry of 2026-10-05, "accepted as recommended").
2. **DP-3 and DP-4 ruled** (new 2026-10-10; §"Decision points"). OPEN.
3. **PL-1602 and SL-1603 minted** in D8 (the 16:28:30 entry, item 3: FD-1598 "rides D8"). By the
   16:29:07 BST split, D8a is `RL 9960` alone, so these mint in **D8b**, unless the lead assembles them
   otherwise; the plan's front matter keeps `status: draft` until the slice PR flips it.
4. **The FD-1374 slice (SL-1536) has merged and gate-1 is free** (the 16:28:30 entry, item 1: "right after
   the FD-1374 slice frees gate-1 and before PL-1599 A").
5. **Re-read at dispatch** (`docs/plans/README.md` convention 4):
   `git diff --name-only fe0b0627 origin/main -- .claude/settings.json scripts/hooks/ tests/test_retry_cap_hook.py conftest.py tests/test_root_conftest.py .claude/skills/dev-commands/SKILL.md .claude/skills/mint-and-finish/SKILL.md`.
   Any output re-derives §"What happens today" and Task 4's line numbers before Task 1. And the in-flight
   sweep this refresh could not run (§"Refresh 2026-10-10" item 9): every open PR's and every `sl-*`
   branch's `git diff --name-only origin/main...<branch>` filtered on the same paths, outside any held gate
   slot. Any match is a lane question for the lead.
6. **The root checkout carries the script**:
   `git -C /home/puzhenhao1989/gi-pricing-plan cat-file -e HEAD:scripts/hooks/retry_cap_hook.py` exits 0
   (§"The root checkout and the settings change").
7. **The GO.** The maintainer's, on `handover/go-request-pl9617-2026-10-10.md`; the slice runs under L1
   (a') (one PR: code, tests, skill clauses, the `SL-1603` status line, one `LG-`; no activation PR; this
   plan was created 2026-10-05, before 8 Oct 11:51:58, so it mints as is). **The GO must also authorise
   the probe `cd`s** of Task 0 Step 4 and Task 3, each in a throwaway seat, never the executor's own
   session: they are the proof the ruling asks for, and every charter forbids a `cd` otherwise.

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
4. **The existing hook suite is unchanged and green:** `uv run pytest -q tests/test_retry_cap_hook.py`,
   and `git diff --name-only origin/main...HEAD -- scripts/hooks/ tests/test_retry_cap_hook.py` prints
   nothing (unless DP-2 (c) is ruled).
5. **Proof (i), the positive control, in a seat (Task 3).** *(Amended 2026-10-10 on the 16:28:30 BST
   entry, item 1 (i): "from a seat, `cd` into a worktree subdirectory, then run a guarded command; the
   hook still runs (no exit 2, no lock-out)". The 5 Oct text used a throwaway session and `cd docs`.)* The
   ledger records, with `date` output and `claude --version`, a **throwaway teammate seat** whose cwd is a
   worktree on the slice's head: it runs `cd <worktree>/docs`, then a **non-parseable** Bash call
   (`echo "$(pwd)" | cat`), then a `record`-form call that the `if` filter matches
   (`python3 <absolute path>/scripts/hooks/retry_cap_hook.py record --help`, or the form Task 0 fixes),
   and both succeed: no exit 2, no refusal. A parseable call alone (`pwd`) does not count: the best-effort
   `if` filter skips it before and after the fix. One more line records the same from a session started
   in the root checkout after the root is fast-forwarded (§"The root checkout and the settings change").
   The seat is never the executor's own session.
   **5r. Proof (ii), red first at main.** Task 0 Step 4: the same seat shape on `main`'s
   `.claude/settings.json`, the same calls, refused: the hook exits 2 with `can't open file …
   scripts/hooks/retry_cap_hook.py`. A red for any other cause does not count.
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

10. **Proof (iii), the hook still refuses what it refused before.** *(Added 2026-10-10 on the 16:28:30
    BST entry, item 1 (iii): "the hook still refuses what it refused before (its own tables
    unchanged)".)* `tests/test_hook_registration.py` runs the **registered** command (read from
    `.claude/settings.json`) with `cwd` = `docs/` and `RUNTIME_STATE_FILE` pointed at a `tmp_path` state
    file seeded at the cap (`retry_cap_hook.py:90` reads the override; the core file is read only), with a
    `record` payload that breaches the cap, and asserts the `deny` decision on stdout
    (`permissionDecision == "deny"`, the shape `tests/test_retry_cap_hook.py:146-161` asserts for the
    script by its absolute path). A within-cap `record` payload is allowed. "Its own tables unchanged" is
    Acceptance 4's empty diff over `scripts/hooks/` and `tests/test_retry_cap_hook.py`.

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
  *(2026-10-10: this constraint is DP-4's option (a); FD-1598's option (b) proposes the opposite
  (fail-open). It holds unless DP-4 is ruled (b).)*
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
- **Other scripts invoked relatively.** `.claude/roles/lead.md:81` (`:79` at `809a3794`; refreshed 2026-10-10) tells the lead to run `python3
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
  two full gates run at once, against `RL-1445`'s one. `tests/test_root_conftest.py`'s
  `test_slot_count_matches_the_dev_commands_gate_wrapper` reads the wrapper's `for i in … ; do` loop in
  `.claude/skills/dev-commands/SKILL.md` and asserts `_SLOT_COUNT == len(loop) == 2` (`:314-325`). So
  the skill's gate loop, `_SLOT_COUNT` and that test can change only together (the 15:37:35 BST
  entry). In the skill at `fe0b0627` (line numbers refreshed 2026-10-10 from `cdaaa573`): the gate loop is `for i in 1 2; do` (`:161`); the gate-slot text
  is `:180-184` ("two non-blocking attempts … at most two gates at once"), `:236-240` (conftest locks
  "`/tmp/slots/gate-{1,2}`") and `:363-364` ("2 gate slots, 2 verify slots"). The `migrate --verify`
  wrapper (`:283`, `:296`) is out of scope: `RL-1445` keeps 2 verify slots.

### Known gap in the dev-commands skill (recorded 2026-10-05, `CLAUDE.md` §12)

**Until this slice lands, `.claude/skills/dev-commands/SKILL.md` is wrong on one point:** its gate
wrapper (`:161`) still offers 2 gate slots, and its text (`:180-184`, `:236-240`, `:363-364`) still says
two gates may run at once. `RL-1445` allows one full gate at a time. Until Task 4 merges,
**the one-gate rule holds by the lead's dispatch** (`RL-1445` :187-194, "held by the lead's dispatch, not by construction"), not by the wrapper or by
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
| `.claude/skills/dev-commands/SKILL.md` | the gate loop `:161` and the gate-slot text `:180-184`, `:236-240`, `:363-364`, `Verified` refreshed (Task 4); a note of the `if` filter's documented best-effort semantics, with the link (Task 5 Step 1). Never the verify wrapper `:283`, `:296` | none in flight (#1162 reverted its fold, `381254c3`) | none |
| `.claude/skills/mint-and-finish/SKILL.md` | `:29-30`, the reason clause "Why: the hook path is relative; a `cd` moves the guard …" only: the lock-out half is removed by this slice, the spawn-cwd half stays; the rule "Never `cd`" (`:28`) is unchanged (16:28:30 item 2); `Verified` refreshed (Task 5 Step 1). *(Row added 2026-10-10.)* | not re-swept (§"Refresh 2026-10-10" item 9) | re-read at dispatch (need 5) |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md`; the `SL-1603` row's status line in `docs/roadmap.md` | added; regenerated; one line (L1 (a')) | every PR | registry, exempt |

**Re-read 2026-10-10 (planner-pl9617).** Open PRs: **0** (`gh pr list --state open`, 16:32 BST). The
branch sweep was not re-run: both gate slots were held (§"Refresh 2026-10-10" item 9); it runs at dispatch
(activation need 5). The rows above that say "none in flight" are the 5 Oct reading until then.

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

### The root checkout and the settings change (added 2026-10-10)

**Facts.** The root checkout `/home/puzhenhao1989/gi-pricing-plan` is on `main` @`8f5a8987`
(2026-10-06), behind `origin/main` `fe0b0627`; it does not auto-pull, and it has been on old branches
before (memory `the-root-checkout-is-pinned-to-an-old-branch`, which records 39 commits behind on
2026-09-18). It carries `scripts/hooks/retry_cap_hook.py` (added by `9e8783de`, #516, an ancestor of its
HEAD). A session's project settings are the `.claude/settings.json` of the directory it starts in; which
copy a session started in a worktree loads is not documented (Task 0 Step 3).

**What the merge does to a session started from the root.**
1. **Until the root is fast-forwarded,** a session started there still reads the old relative command.
   Nothing new can lock it, but nothing is fixed for it either: a `cd` still locks it as today. So proof
   (i) in a root-started session waits for the fast-forward (Hand-off item 6).
2. **After the fast-forward,** the command resolves to `<root>/scripts/hooks/retry_cap_hook.py`, which the
   root has carried since #516. No lock-out.
3. **The new risk — a missing script locks out every session, from every cwd.** Under DP-1 (c) and DP-2
   (a), every session whose project directory is the root runs the root's copy. If the root checkout were
   moved to a commit that has the new `settings.json` but no `scripts/hooks/retry_cap_hook.py`, or to a
   branch where the script is renamed, `python3` exits 2 on every Bash call in every such session: today's
   lock-out, but without needing a `cd`. No such commit exists today (the script predates the change), so
   this needs a deliberate later rename or a checkout of a broken branch. The same holds when
   `CLAUDE_PROJECT_DIR` is unset **and** the cwd is outside any repository (`cd /tmp`): the fallback
   expands to empty and the path becomes `/scripts/hooks/retry_cap_hook.py` (DP-1's residual, stated on 5
   Oct for option (b), still true under (c)).
4. **Running sessions.** Whether a session that is already running re-reads `settings.json` when the root's
   copy changes under it is not documented in the part of the hooks reference read here. Task 0 Step 6
   records it; until then, assume the old command stays in force for a running session until it restarts.

**Mitigation.** (a) Activation need 6: the root carries the script before dispatch. (b) Hand-off item 6:
the lead fast-forwards the root to the merge commit at once, and discloses it in the channel (memory
`the-root-checkout-is-pinned-to-an-old-branch`, "Face, 2026-09-28"), then runs proof (i)'s root-started
line. (c) The registration test (Acceptance 3) also asserts that the file the command names exists
relative to the repository root, so a rename of the script reds the gate in the PR that renames it. (d)
A rename or move of `scripts/hooks/retry_cap_hook.py` is a change to `.claude/settings.json` in the same
commit; Task 5 Step 1 adds this sentence to the dev-commands skill. (e) DP-4 option (b) (fail-open) would
remove the risk at the cost stated there. The recovery, if a lock-out happens anyway, is today's: the
user's `! cd <root>` does not help (the path is no longer cwd-relative); the user restores the script
or reverts `.claude/settings.json` in the root from a shell outside Claude Code.

## Decision points

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-1 | What anchors the path? | (a) `python3 "$CLAUDE_PROJECT_DIR"/scripts/hooks/retry_cap_hook.py hook`, as the backlog entry names. (b) `python3 "$(git rev-parse --show-toplevel)"/scripts/hooks/retry_cap_hook.py hook`: the checkout the cwd is in. Fails if the cwd is outside any repository (`cd /tmp`), the same lock again. (c) (a) with (b) as a fallback: `"${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"`. | **(c)**. (a) is the form the docs give for project hook scripts, and the form this repository already uses (`planning-with-files`). But the docs do not say that a teammate's or a subagent's hook process gets the variable, and this team runs mostly as teammates. The fallback costs one expansion and covers that gap. **The fallback is required, not optional** (the 16:47:09 BST entry, consequence (2)): a Task 0 reading that the variable is set in every process kind today does not remove it, because the docs do not promise it for teammates. Under (c) the test (Acceptance 1) also runs one case with `CLAUDE_PROJECT_DIR` unset. |
| DP-2 | **Which copy runs in a worktree?** Today the relative path resolves in the cwd, so a session working in `.claude/worktrees/<x>` runs **that worktree's** `retry_cap_hook.py`. The docs say `CLAUDE_PROJECT_DIR` "stays put" at "the project root where the session started", so a session started in the root checkout that then enters a worktree runs the **root checkout's** copy under DP-1 (a). A teammate whose process *starts* in a worktree may get the worktree as its project root (not documented; Task 0 Step 3). The root checkout is not kept on `main` (it was on `main` at `809a3794` when read today, but it has been pinned to old branches before). | (a) Accept it: the root checkout's copy runs. The script changes rarely (last changed by `71f5a220`, 2026-09-17), and both copies read the same state file (`DEFAULT_STATE_FILE` is under `~`, `:77`). (b) Anchor on the cwd's checkout first (`git rev-parse --show-toplevel`), and use `CLAUDE_PROJECT_DIR` only when that fails: the worktree's copy runs, as today, but a `cd /tmp` would then fall back. (c) Keep (a)'s command, and have the script hand off to the cwd's checkout's copy when one exists (edits the script). | **(a)**, recorded in the ledger. The hook's behaviour is one decision function; a copy that differs between checkouts is a slice changing the hook, and that slice's executor tests by absolute path (`tests/test_retry_cap_hook.py:31`), which is not affected. (b) puts the old dependence on the cwd back in, the defect this slice removes. (c) adds code for a case with no recorded failure. Task 0 records which directory `CLAUDE_PROJECT_DIR` holds in each kind of worktree session; where it is the worktree, DP-2 does not arise for that kind, and the ledger says so. |
| DP-3 | *(New 2026-10-10.)* **Shell form or exec form?** The hooks reference now says "Prefer exec form for any hook that references a path placeholder", and exec form (`args`) has no shell. | (a) **Shell form**, as DP-1 (c) was ruled: `"command": "python3 \"${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}\"/scripts/hooks/retry_cap_hook.py hook"`, the placeholder double-quoted as the page requires for shell form. (b) **Exec form**: `"command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/scripts/hooks/retry_cap_hook.py", "hook"]`. No quoting risk, but no fallback: if the variable is unset in a teammate's hook process, the path is literal or empty and every call exits 2. | **(a)**. The fallback is ruled required (the 16:47:09 BST entry, consequence (2)), exec form cannot express it, and the page still allows shell form with the placeholder quoted. Under (a) the unset-variable case is Acceptance 1's extra case. If Task 0 Step 2 shows the variable set in every process kind, (b) becomes possible later; that is not a reason to change the ruled form now. |
| DP-4 | *(New 2026-10-10.)* **Fail-closed or fail-open when the resolved script is missing?** FD-1598 option (b) item 1 proposes fail-open ("if the file is not found, exit 0, never 2"); this plan's Global Constraints say fail-closed; the 16:28:30 ruling names PL-1602 "already accepted" and does not rule it. | (a) **Fail-closed** (as planned): a missing script blocks every Bash call, mitigated by activation need 6, Acceptance 3's existence assert and Hand-off item 6 (§"The root checkout and the settings change"). The C2 retry cap (`F61`) cannot be switched off by a missing file. (b) **Fail-open**: `P=…; [ -f "$P" ] \|\| exit 0; python3 "$P" hook`. No lock-out from a missing script; but a missing or renamed script silently turns the C2 retry-cap layer off, a new way to bypass a layer `F61` already calls bypassable, and the hook's refusals (proof (iii)) stop without any signal. | **(a)**, with the four mitigations. The failure (b) prevents has no recorded instance and needs a rename or a broken checkout; the failure (b) causes is silent. If (b) is ruled, the plan adds a stderr line on the exit-0 path and an Acceptance item proving it, and the Global Constraint changes. **Open: the lead's or the maintainer's.** |

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
  Run one Bash call. Record the line. *(Caution added 2026-10-10: a hook in the **root's**
  `.claude/settings.local.json` runs in every session started from the root, the lead's included.
  Prefer a throwaway worktree's `.claude/settings.local.json` and a session started there; if the root's
  file is used, tell the lead before and after, keep the hook append-only with exit 0, and remove it in
  the same step.)*
- [ ] **Step 2.** The same from a teammate process and from an in-session subagent (DP-1).
- [ ] **Step 3.** The same in a worktree session (`EnterWorktree`, and a teammate spawned with a
  worktree cwd) (DP-2).
- [ ] **Step 4. The red probe** (the 16:47:09 BST entry, consequence (3)). Remove the scratch hook
  first; `git -C <root> status --porcelain .claude/` prints nothing tracked. Then, in a **throwaway
  teammate seat** whose cwd is a worktree on `main` (proof (ii) of the 16:28:30 BST entry: "the same at
  main without the fix reproduces the exit 2"; amended 2026-10-10, the 5 Oct text said a throwaway
  session and `cd docs`), run `cd <worktree>/docs`, then one **non-parseable** Bash call, for
  example `echo "$(pwd)" | cat`. **Expected red:** the call is refused, the hook having run despite the
  `if` filter and exited 2 (`can't open file … scripts/hooks/retry_cap_hook.py`). Record both outputs,
  `date` and `claude --version`. A parseable call (`pwd`) is not the probe: it is matched and skipped,
  so it passes on `main` too. Free the throwaway session from outside it (it is locked by design).
- [ ] **Step 5.** Send the table to the lead before Task 1 if any answer differs from the
  recommendation's premise (DP-1: the variable is set everywhere; DP-2: it holds the root checkout),
  or if Step 4 is not red by its cause. DP-1's `git rev-parse` fallback stays in every case. A
  different answer changes the ruled option, not the task list.
- [ ] **Step 6.** *(Added 2026-10-10.)* Whether a **running** session picks up a changed
  `.claude/settings.json`: with Step 1's scratch hook, start a throwaway session, then change the scratch
  hook's output line, run one Bash call, and record which line was written. This fixes Hand-off item 6's
  instruction (restart the seats, or not) after the merge.

### Task 1: The registration test, red first (Acceptance 1, 2, 3, 10)

**Files:** add `tests/test_hook_registration.py`.

- [ ] **Step 1.** Write the test. It loads `.claude/settings.json` with `json`, takes every
  `hooks.PreToolUse[*].hooks[*].command`, and for each one runs
  `subprocess.run(["sh", "-c", command], input=<payload>, cwd=ROOT / "docs", env=<ruled env>, …)`.
  The payload is `{"tool_name": "Bash", "tool_input": {"command": "pwd"}}`. The state and core files
  are not passed: a non-`record` command returns before either is read (`cmd_hook`,
  `retry_cap_hook.py:294-306`), so the test writes nothing outside `tmp_path`. Assert `returncode == 0`
  and `"allow"` in the decision on stdout. Add the root-cwd case (Acceptance 2) and the static walk
  (Acceptance 3). Under DP-1 (c), add the `CLAUDE_PROJECT_DIR`-unset case. *(Added 2026-10-10:)* the
  refusal case of Acceptance 10 (`RUNTIME_STATE_FILE` = a `tmp_path` state seeded at the cap, a breaching
  `record` payload, `deny` asserted) and its within-cap twin, both from `docs/`; and, in the static walk,
  an assert that the script each command names exists under the repository root (§"The root checkout
  and the settings change", mitigation (c)). If DP-3 is ruled (b), the test runs `[command, *args]`
  without `sh -c`.
- [ ] **Step 2.** Run `uv run pytest -q tests/test_hook_registration.py` on `main`'s settings.
  **Expected:** the `docs/`-cwd case fails with exit 2 and stderr `can't open file …
  scripts/hooks/retry_cap_hook.py`; the root case passes; the static walk fails naming `:9`'s
  command; the `docs/`-cwd refusal case fails the same way (exit 2, no `deny` on stdout). Record the
  failure lines in the ledger.

### Task 2: The registered command, per DP-1 (Acceptance 1, 2, 3, 4)

**Files:** edit `.claude/settings.json:9` only.

- [ ] **Step 1.** Replace the command with the DP-1 form; the path is double-quoted, so a project
  path containing a space still works.
- [ ] **Step 2.** `uv run pytest -q tests/test_hook_registration.py tests/test_retry_cap_hook.py`:
  all pass.
- [ ] **Step 3.** Broken-input proof (Acceptance 3): copy the settings to `tmp_path` with the old
  relative form, point the static walk at it, and see it fail. Record the line.

### Task 3: The live check — proof (i) (Acceptance 5)

- [ ] **Step 1. The green half of Task 0 Step 4's probe** (proof (i) of the 16:28:30 BST entry; amended
  2026-10-10, the 5 Oct text said a throwaway session and `cd docs`). A **throwaway teammate seat** whose
  cwd is a worktree on the slice's branch runs `cd <worktree>/docs`, then the same non-parseable call
  as Task 0 Step 4 (`echo "$(pwd)" | cat`), then the `record`-form call of Acceptance 5, then `pwd`.
  Record the outputs, `date` and `claude --version`. The non-parseable call must succeed: a `pwd` alone
  proves nothing, because the `if` filter skips it on `main` too. Under DP-2 (a), also record which
  copy ran (Task 0 Step 3's answer). The seat is ended from outside when done; it never writes.
- [ ] **Step 2.** *(Added 2026-10-10.)* After the merge and the root fast-forward (Hand-off item 6), the
  same three calls in a session started from the root checkout; recorded as a dated line in the
  ledger's build log. This is the line FD-1598's close reads (Hand-off item 4).

### Task 4: One gate slot — the skill's gate loop, `conftest.py` and the test together, red first (Acceptance 8, 9)

**Files, all in ONE commit:** edit `.claude/skills/dev-commands/SKILL.md` (gate only); edit
`conftest.py` (repository root); edit `tests/test_root_conftest.py`. Never the skill's `migrate
--verify` wrapper (`:283`, `:296`) or its verify-slot words: `RL-1445` keeps 2 verify slots. Line
numbers are at `fe0b0627` (refreshed 2026-10-10 from `cdaaa573`; the gate-2 standing rule at `:192` is new and stays true: Step 3 says "one code gate on gate-1; gate-2 is for one docs check only, `:192`").

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
  shape: one non-blocking attempt, then the blocking wait on `gate-1`). The gate-slot text: `:180-184`
  (one non-blocking attempt; at most one gate at once, `RL-1445`), `:236-240` (`/tmp/slots/gate-1`),
  `:363-364` ("1 gate slot, 2 verify slots", citing `RL-1445`). Refresh `Verified` (`:1106`) with the tree.
- [ ] **Step 4. `conftest.py`.** `_SLOT_COUNT = 1` (`:70`; its comment cites `RL-1445`, the minted
  id); the docstring's `/tmp/slots/gate-{1,2}` and "the same two slots" (`:19-24`) name the one slot.
  The wait message's format is unchanged.
- [ ] **Step 5. Green.** `uv run pytest -q tests/test_root_conftest.py`: all pass. Then the broken-input
  proof (Acceptance 9): `_SLOT_COUNT = 2` in a scratch edit, the rewritten test fails by its cause,
  record the line, revert. Commit Steps 1, 3 and 4 as one commit.

### Task 5: The gate and the ledger (Acceptance 6, 7)

- [ ] **Step 1.** ~~No skill states the `cd` trap at `809a3794` (`grep -rn -i -E 'hook path is
  relative|never .?cd' .claude` prints nothing), so no skill is edited for it.~~ *(Struck 2026-10-10: at
  `fe0b0627`, `git grep -n -i -E 'hook path is relative|never .?cd' origin/main -- .claude/skills` prints
  `dev-commands/SKILL.md:427` ("Never `cd` inside the wrapper", a rule with no hook reason; unchanged)
  and `mint-and-finish/SKILL.md:28-29`, whose reason "the hook path is relative" this slice makes half
  false.)* **Edit `mint-and-finish/SKILL.md:29-30`'s reason clause only**: keep "Never `cd`" and the
  spawn-cwd reason ("a `cd` moves … every agent spawned after you"); replace "the hook path is relative"
  with the fact after this slice (the hook runs by absolute path, so a `cd` no longer locks the session;
  the rule stands, 16:28:30 BST item 2); refresh its `## Verified` (`:178`). The briefs and the role
  files are the lead's and the maintainer's (Hand-off items 2 and 5). **Beside Task 4's gate-slot edit,
  one more skill edit:** `.claude/skills/dev-commands/SKILL.md` and the ledger record the **documented**
  semantics of `.claude/settings.json:10`'s `if`, with the link
  (<https://code.claude.com/docs/en/hooks#bash-if-matching>): the filter is best-effort, and a Bash
  call Claude Code cannot parse statically runs the hook regardless of the pattern. So the hook
  command must work from any cwd, which this slice's absolute path gives. They record it as documented
  behaviour, never as a Claude Code bug, with Task 0 Step 4's red and `claude --version`, and the
  skill's `Verified` date refreshed (Hand-off item 3). *(Added 2026-10-10:)* the same skill gains one
  sentence: a rename or move of `scripts/hooks/retry_cap_hook.py` changes `.claude/settings.json` in the
  same commit, because every session runs the root checkout's copy by absolute path (§"The root
  checkout and the settings change", mitigation (d)). Its words contain no `verify-` (Acceptance 9).
- [ ] **Step 2.** The two-half gate through the gate-runner, then the ledger.

## Hand-off

1. The lead minted PL-1602 and SL-1603 in D8b (activation need 3), and dispatches after
   activation needs 1 to 7. *(Amended 2026-10-10: was "at the merge turn … needs 1 to 3".)*
2. ~~On merge, the "never `cd`" line that every brief carries since the 15:24:59 BST entry can be lifted.
   That is the maintainer's (by delegation) call, on the ledger's Acceptance 5 line.~~ *(Struck
   2026-10-10 on the 16:28:30 BST entry, item 2: the `cd` guard is not built and the rule is not
   relaxed by this slice. Whether the brief line or the charter rule changes after the merge is the
   maintainer's, and no part of this plan proposes it.)*
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
4. *(Added 2026-10-10.)* **FD-1598 closes when this slice merges with proof (i) green** (16:28:30 BST
   item 3). The slice's ledger carries Acceptance 5's seat line (Task 3 Step 1) and, after the root
   fast-forward, Task 3 Step 2's root-started line; the lead closes FD-1598 citing both. The **revisit
   condition** (16:28:30 item 2): if, after this slice lands, a slip still writes outside its worktree,
   the lead brings the evidence and a guard proposal to the maintainer. This plan builds no guard.
5. *(Added 2026-10-10.)* **The role files' reason clause.** Seven role files give "the session's hook path
   is relative" as the reason for "Never `cd`" (`planner.md:63` is one). After the merge that half of the
   reason is false; the spawn-cwd half stands. A role file is the maintainer's (`CLAUDE.md` §12); the lead
   puts the one-clause correction to the maintainer. Not in this slice's write set.
6. *(Added 2026-10-10.)* **The root checkout.** At the merge read-back, the lead fast-forwards the root
   checkout to the merge commit and discloses it in the channel; seats running at the merge are restarted
   if Task 0 Step 6 showed a running session keeps the old command. Then Task 3 Step 2.

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
   ids were written as working ids, never hyphenated in prose, until the mint of 2026-10-10.
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
7. *(Added 2026-10-10.)* **Against the 16:28:30 BST entry, item by item.** 1 "BUILD PL-1602 NOW, right
   after the FD-1374 slice frees gate-1 and before PL-1599 A": activation need 4, and the GO request's
   order. (i) "from a seat, `cd` into a worktree subdirectory, then run a guarded command; the hook
   still runs": Acceptance 5, Task 3 Step 1. (ii) "the same at main without the fix reproduces the exit
   2 (red-first)": Acceptance 5r, Task 0 Step 4, and Task 1 Step 2's test red. (iii) "the hook still
   refuses what it refused before (its own tables unchanged)": Acceptance 10 and Acceptance 4's empty
   diff. 2 "The no_cd_hook.py guard is NOT built now": the scope paragraph at the top; no guard file is in
   §"Write set"; the "CONDITION to revisit" is Hand-off item 4. 3 "closes when PL-1602's slice merges with
   the positive control green": Hand-off item 4. Every fact changed since 5 Oct carries a dated note
   where it sits, and §"Refresh 2026-10-10" lists them.
