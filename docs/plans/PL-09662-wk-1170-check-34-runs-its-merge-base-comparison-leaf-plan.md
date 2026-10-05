---
id: PL-9662
family: plan
kind: leaf
title: WK-1170 — check 34 runs its merge-base comparison, so a frozen file's body cannot change with the gate green (FD-1282; FD-1323 duplicate): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 99afcde215c0817c5ac4db55332ab7a69e4752a0
phase: P2
work: WK-1170
slice: SL-9655
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1282, FD-1323, SL-9655, PL-1276, RL-1263]
---

# PL 9662 (working id) — WK-1170: check 34 runs its merge-base comparison (FD-1282), leaf plan

Filed under working id 9662 (this plan) and slice working id 9655 (its `SL-` row
under WK-1170 in [`../roadmap.md`](../roadmap.md), `draft`). The lead reserved both in the
handover `eta.md`. Both are replaced at the mint by `python3 scripts/doc-id.py next`.
Where this plan's sample code, comments and commit messages say `PL 9662`, the executor
writes the minted `PL-` id.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `test-driven-development` (each acceptance
> item is seen red, by its cause, before the code that turns it green), `python-test` (no
> `req` marker: this tests the audit tool, as `tests/test_audit_docs_ids.py:29` says),
> `code-quality`, `docs-audit`, `dev-commands` (the two-half gate and the slot wrapper),
> `reproducing-ci-locally` (Task 4's CI-event refs) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor is
> spawned from `.claude/roles/executor.md`.

## Goal

`check_freeze` (`scripts/audit-docs.py:2382`) calls `frozen_diff_is_permitted` (`:2142`) on
every frozen-family file that the change under audit modifies, renames or deletes. It compares
each one against the merge-base with a named base ref. CI names that ref per event. A body
edit, a backward `status:` move or a blanked `corrected_by:` on a frozen file then exits
`audit-docs.py` with rc 1, in the PR, before an ACK is requested.

**Architecture.** One new function, `freeze_violations(base)`, sits next to the predicate. It
runs `git merge-base <base> HEAD`, then `git diff --name-status -z -M <merge-base> -- docs`
against the working tree. It parses the old side's header with `_docid.parse_header_text`.
For a frozen family it judges old against new with the shipped predicate. `check_freeze`
reads the base from the environment variable `AUDIT_DOCS_FREEZE_BASE`. When the variable is
unset the base is `origin/main`. The value `none` turns the comparison off and prints that it
did. When the base does not resolve, the check fails loudly; it never skips. The predicate
gains a forward-only `status:` rule, as §1.2a and §1.11 row 34 already state.

**Tech stack.** Python 3.12 stdlib (`subprocess`, `os`), git, pytest, GitHub Actions.

**Spec.** [`../process/document-ids.md`](../process/document-ids.md) §1.2 (the family
table: Plan, Ruling, Research, Closure, Finding, Decision and Proposal are frozen or
write-once), §1.2a (forward-only transitions), §1.5 (the header comments at `:134-135`),
§1.6 (the PL row at `:158`), §1.11 row 34 (`:230`). As amended by the activation need A1
below. The findings: [`../findings/FD-01282-check-34-does-not-run-its-merge-base-comparison-on-the-real-tree-so-a-frozen-file-s-body-can-change-with-the-gate-green.md`](../findings/FD-01282-check-34-does-not-run-its-merge-base-comparison-on-the-real-tree-so-a-frozen-file-s-body-can-change-with-the-gate-green.md)
and [`../findings/FD-01323-check-34-is-vacuous-on-real-trees-a-frozen-family-file-s-body-changes-with-the-gate-green-and-a-plan-s-activation-does-it.md`](../findings/FD-01323-check-34-is-vacuous-on-real-trees-a-frozen-family-file-s-body-changes-with-the-gate-green-and-a-plan-s-activation-does-it.md).

## The decisions this plan rests on, quoted

1. **The maintainer, 2026-09-30** (by delegation; `to-lead.md` "2026-09-30 06:00:41 BST —
   MERGE-ACK #947 (FD-1280..1282, the F-W10-2 owner); DECISIONS on FD-1280 and FD-1282", as
   quoted in `docs/findings/register.md:215`): *"options (a), then (b) — deferred with an
   owner — WK-1170 … (a) First reconcile the rule with practice in writing … the rule and the
   practice are made to agree, never enforced against practice unannounced. (b) Then
   `check_freeze` calls `frozen_diff_is_permitted` against `origin/main` in CI, proven red on
   a body edit to a closure. Event: (a)'s amendment merged, then (b) merged."* Amended the
   same day (08:50:02 BST): *"Option (b) must also be proven red on a blanked `corrected_by`
   back-link, not only on a body edit."*
2. **The maintainer, 2026-09-30** (`to-lead.md` "2026-09-30 14:48:52 BST — DECISIONS: check
   34 is vacuous on real trees → a new FD (MEDIUM, WK-1170); PL-1299 accepted; the activation
   practice from now on", as quoted in FD-1323 §"Decisions on record" and
   `register.md:223`): *"plan activation is the `status:` flip only … From now on no prose is
   added to a plan already on main"*; *"(a) also amends `document-ids.md` :158's 'active on
   freeze' wording to agree with :69"*; and (b) is *"red on a body edit to an active plan, a
   closure and a draft plan, and on a blanked `corrected_by:` back-link."*
3. **The maintainer (by delegation), 2026-10-05** (`to-lead.md` "2026-10-05 13:24:56 BST — Freeze-check
   findings: FD-1323 closes as a duplicate; owner stays WK-1170; fix scheduled after FD
   9707/9708"): *"It runs after the '(a) first' freeze-rule amendment and goes to the first
   build lane free after FD 9707 and FD 9708."* Three points, quoted whole:
   > 1. The live scope is the PR's changed frozen files against the merge-base with the PR's
   > BASE ref, not all 492 files. On a push to main the comparison base must be the previous
   > main commit, or the check is vacuous again. The plan states which ref it uses in each CI
   > event.
   > 2. Docs CI already checks out with `fetch-depth: 0` (.github/workflows/docs.yml:45), so
   > the merge-base is reachable there. If the check runs in any other workflow, that one
   > needs it too.
   > 3. Red first on real broken input: a body line appended to a frozen PL; a status moved
   > backwards; a blanked `corrected_by:`. Each must print a failure before the fix is called
   > done. Positive cases too: a living register row, a ledger append, a forward status move.
   > Before going live, a dry run over the last 20 merged PRs reports which would have failed;
   > the true escapes (#986's kind, CR-838:46) are listed, not silently allowed.

## Status

**Draft.** Activation need A1 (below) is not met at `99afcde2`, and DP-1 is open. The plan is
written to DP-1's recommended outcome. If A1 rules otherwise, the planner files a superseding
plan before dispatch. Frozen from its first merge to main, whatever its `status:`
(`document-ids.md:69`).

## Activation needs

| # | Need | State at `99afcde215c0817c5ac4db55332ab7a69e4752a0` | Owner |
|---|---|---|---|
| A1 | **The "(a) first" freeze-rule amendment is merged.** | **Not done.** Searched with `git grep -ln "FD-1282\|FD-1323" -- docs .github scripts`: the hits are the two essays, `docs/INDEX.md`, `docs/findings/register.md` and `docs/roadmap.md` (the WK-1170 2026-09-30 line). There is no `RFC-` or `RL-` for it. `git log origin/main -- docs/process/document-ids.md` shows no change after `a380aa7a` (2026-09-29) except `0c5fcb5c` (#1103, ledger mint), and neither touches the freeze rule. No open PR carries it (`gh pr list --state open`, read 2026-10-05 13:3x BST). | **The maintainer.** `document-ids.md` §1.6, row "Reference — `process/`": *"maintainer; amendments arrive as `RFC-` + `RL-`"*. Any role drafts on instruction (RFC row). |
| A2 | A build lane is free after the FD 9707 fix (PL 9688) and the FD 9708 fix (PL 9683), and a gate slot is granted. | Lanes per RL-1263; see **Contention** below. | The lead. |
| A3 | DP-1 resolved by A1's ruling, and DP-2 to DP-5 confirmed or overridden. | Open. | A1's resolver; then the lead (DP-2 to DP-5). |

**Pre-mint check of 2026-10-05 15:57 BST, at `origin/main` `cdaaa57345cb765f96034ce1ec2733c338f1c3cd`.**
The table above is as filed at `99afcde2`. Since then:

- **A1** is drafted but not merged: RFC 9653 + RL 9654 (working ids), draft PR #1147, branch
  `dm-9654-freeze-reconcile`. `document-ids.md` and `findings/README.md` are unchanged at
  `cdaaa573`, so A1 is still **not done**.
- **A3** was answered by the `to-lead.md` entry headed *"2026-10-05 13:43:31 BST — PL 9662 / SL 9655
  (check_freeze fix, #1146 @c35b67b7): conditions met; DP-3 = the spec; one guard on the "none"
  switch; DP-4 gets an owner"*. Its item 3: *"DP-2 (a deleted frozen file is red) and DP-5 (a
  standalone slice): OK at their defaults."* Its item 2 decides DP-3 inside A1 (RL 9654). Its item
  5 places the lane: *"Its build lane follows my 13:12:56 priority rule (after the HIGH G2
  blockers)."*
- **Owed at this plan's dispatch, not edited here:** a dispatch-record delta carrying the entry's
  items 1 and 2, verbatim:
  > 1. The "none" value (visible-off): ACCEPTED for local use only, with a guard. CI must never run the check off. The workflow sets the base explicitly; a test or CI step fails if AUDIT_DOCS_FREEZE_BASE is "none" while `CI=true`; and every run prints the base sha it compared against, so a log shows what was checked. An unresolvable base stays a loud fail.
  > 2. DP-3 (the predicate refuses only a move away from a terminal status; §1.2a and row 34 say forward-only): THE SPEC is right. The check enforces forward-only status moves. It is decided inside A1 (RL 9654), and the slice implements it with a red test for a backwards move between non-terminal states (e.g. active → draft).

  Item 4's owner for DP-4 (*"ledgers' append-only rule is not mechanically checked"*, a WK-1170
  backlog item) is A1's or the slice ledger's, not this plan's.
- **Cites re-checked at `cdaaa573`.** Every file this plan cites is byte-unchanged since
  `99afcde2`, except `docs/findings/register.md`. Its FD-1282 row (`:215`) gained a 2026-10-05
  note (#1139) and no line moved. Four cites were imprecise at filing, and are corrected in place:
  `check_freeze` ends at `:2424`; `frozen_diff_is_permitted` ends at `:2192`, with the new code
  inserted above `_inverse_token_pattern`'s decorator (`:2195`); the `doc-id verify` block is
  `docs.yml:120-138`, including its exit-1 tail; and Task 3 Step 1's end string is *"live over
  whatever is in scope."* (`grep -cF` = 1). P3's window is as measured at `99afcde2`. The 8
  first-parent merges since then modify no frozen-family file. The dry run (Task 5) re-measures
  at its own tree.

**What A1 must contain**, so that this plan can enforce it without going red on lawful work.
Items (i) to (iv) come from the two decisions quoted above. Items (v) to (vii) are what this
plan needs to be correct.

- (i) **Which families are frozen, and from when.** Mutability is a family property
  (`:69`). A frozen-family file is frozen from its **first merge to main**, whatever its
  `status:`. `:158`'s PL row, *"`draft` while decision points are open, `active` on freeze"*,
  is reworded to agree.
- (ii) **What may change after freeze**: `status:` forward only (§1.2a), `superseded_by:`,
  an append to `corrected_by:`, and nothing else. A ledger may also append to `plans:`. Plan
  activation is the `status:` flip only.
- (iii) **Whether a dated appended note is permitted on a frozen body.** This is DP-1.
  Practice and rule disagree today. `docs/findings/README.md:60` says *"An essay file is
  write-once, amended in place … A correction is appended and dated"*. FD-1282's own
  *"Amendment, 2026-09-30"* section was appended after its merge (`14e9b9d5`, #955).
  `document-ids.md:134-135` says *"the body is never edited"*. A1 rules it, and amends
  whichever text loses.
- (iv) **How a frozen record is corrected**: a correcting record (`corrects:`) plus an
  appended `corrected_by:` entry on the corrected file. This is already `:135`, and RL-1290
  → RL-881 and RL-1383 → RL-1361 are on main.
- (v) **The comparison base, per event**, written into §1.11 row 34 (`:230`), which says
  *"the merge-base"* and names no ref:
  - on a pull request, the merge-base with the PR's base commit;
  - on a push to main, the previous main tip;
  - on a local run, the merge-base with `origin/main`.

  The code role does not write `process/` (§1.6 Principles: *"the role that writes code never
  amends the document the code is checked against"*). So the ref rule is A1's to write. This
  plan implements it.
- (vi) **A deleted frozen file is a violation** (DP-2's recommendation), or A1 says it is
  not.
- (vii) **History is not re-judged.** The check reads only the change under audit. The 42
  pre-ruling body edits measured below (PL-1299's activation among them, which the maintainer
  accepted on 2026-09-30) stay as they are, and nothing reds them.

**ETA.** Planning: this draft, 2026-10-05. Build: the maintainer's (by delegation) estimate is *"M, ≈4–6 h"*, plus
the dry run and one gate. It starts when A1 merges and A2's lane opens. The date depends on
A1, which has no owner action at `99afcde2`.

## Acceptance Standard

Each item can be run by a fresh reviewer. "rc" means the process exit code, read with
`; echo $?` directly after the command, never through a pipe (`dev-commands`).

1. **Unit tests, red first.** `uv run pytest -q tests/test_audit_docs_freeze.py` passes, with
   all 14 tests from Task 1 present. The ledger records the earlier red run, and every test
   failed by the cause the step names (no `freeze_violations` attribute; then the specific
   assertion). A test that failed for a different reason is a plan defect, not a pass.
2. **Real-tree broken input, red, by cause.** In a scratch worktree at the slice head, each
   probe is one uncommitted edit, reverted afterwards, and run with
   `AUDIT_DOCS_FREEZE_BASE=origin/main python3 scripts/audit-docs.py`. For each, rc is 1 and a
   `check 34:` line names the file and the reason below. The same probe at
   `99afcde215c0817c5ac4db55332ab7a69e4752a0` gives rc 0, which reproduces the escape.
   - (a) A body line appended to `docs/plans/PL-01276-wk-1170-the-create-read-retire-audit-map-plan.md`
     (a `draft` plan; #986's kind). Reason: `the body changed`.
   - (b) `docs/plans/PL-01408-*.md` `status: active` → `status: draft`. Reason:
     `status: moved backwards`.
   - (c) `docs/rulings/RL-00881-*.md` `corrected_by: [RL-1290]` → `corrected_by: []`. Reason:
     `corrected_by: entries were removed or reordered`.
   - (d) One word inserted in the body of `docs/closures/CR-01212-*.md` (a closure). Reason:
     `the body changed`.
   - (e) One sentence edited in the body of `docs/plans/PL-01408-*.md` (an `active` plan).
     Reason: `the body changed`.
3. **Real-tree positives, green.** Same harness. Each gives rc 0, or rc 1 with no `check 34:`
   failure line (record any other check's line verbatim). The check-34 note reports at least 1
   compared file where one was changed.
   - (a) A row appended to `docs/findings/register.md`, the living register, which has no
     front matter.
   - (b) A line appended to `docs/ledgers/LG-01412-*.md`. Ledger is not a frozen family
     (`_FROZEN_FAMILIES`, `scripts/audit-docs.py:2130-2132`).
   - (c) `docs/plans/PL-01276-*.md` `status: draft` → `status: active` (a forward move).
   - (d) A new plan file added under `docs/plans/` and staged with `git add`: a copy of
     PL-1276 with a working id, for example.
4. **No silent skip.** `AUDIT_DOCS_FREEZE_BASE=no-such-ref python3 scripts/audit-docs.py`
   exits 1 with a `check 34:` line naming the base. `AUDIT_DOCS_FREEZE_BASE=none` prints the
   note `merge-base comparison NOT RUN`.
5. **CI states its ref per event, and runs it.** `.github/workflows/docs.yml`'s `audit-docs`
   step sets `AUDIT_DOCS_FREEZE_BASE` as follows:
   - on `pull_request`: `github.event.pull_request.base.sha`;
   - on `push`: `github.event.before`.

   The slice PR's docs CI job log carries the check-34 note naming that PR's base SHA (40
   hex). The first docs run on main after the merge names the previous main tip.
   `grep -n "audit-docs.py" .github/workflows/*.yml` lists every workflow that runs the
   script, and each one checks out with `fetch-depth: 0`. At `99afcde2` there are two:
   `docs.yml:45` (the script directly) and `python.yml:144` (via pytest).
6. **Dry run before going live** (Task 5): the shipped `freeze_violations` is run over the
   last 20 first-parent merges on `origin/main` at the slice head, over PR #986's head
   `9d8199a7f887b0e00b5f6941f4897e5324b1c4cc`, and over `40739df0` (the CR-838 edit). Every
   red is listed in the ledger with its merge, its file and its reason. #986 → PL-1276 and
   `40739df0` → CR-838 are among them. The list goes to the lead before the PR's ACK request.
7. **`doc-id.py migrate --verify` unchanged.** The docs.yml `doc-id verify` command, run
   before and after the change on the same tree, prints the same row table (`diff` of the two
   outputs is empty). Task 6 applies the `_docverify` line only if it is not.
8. **The words match the code.** `check_freeze`'s docstring no longer says the comparison
   *"finds nothing to run against"*. The module docstring's item 34 (`scripts/audit-docs.py:81`)
   names the base rule and `AUDIT_DOCS_FREEZE_BASE`. `.claude/skills/docs-audit/SKILL.md`'s
   check-34 paragraph says the same.
9. **The full two-half gate** of `CLAUDE.md` §11 exits 0 on the slice head, each command's rc
   recorded: `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`,
   `uv run pytest -q`, `python3 scripts/audit-docs.py`, `uv run python scripts/req-coverage.py`,
   `uv run python scripts/generate-contracts.py --check`, and the five `pnpm --dir frontend`
   commands. Run it in the granted slot with the `dev-commands` wrapper.

## Global Constraints

- `scripts/audit-docs.py` stays stdlib-only, Python 3.12; `mypy --strict` and `ruff` cover it
  (`.claude/skills/repo-architecture`).
- Every `fail()` message starts with a literal `check 34: ` (the f-string's own text), because
  `tests/test_audit_docs_check_prefixes.py:43` (`_CHECK_PREFIX_RE`) reads the literal. So
  write `fail(f"check 34: {msg}")`, never `fail(msg)`.
- One predicate, not two: the live comparison calls `frozen_diff_is_permitted` itself
  (RL-989 §3, quoted in its docstring: *"implementing it twice is how the two drift apart"*).
- The executor does not edit `docs/process/document-ids.md`, `docs/findings/README.md` or
  any finding (§1.6 Principles; the FD row). A1 writes the first two.
- No new dependency; no workflow other than `docs.yml` changes, unless Task 4 Step 1 finds
  another caller.

## Scope

| Item | Source | Task |
|---|---|---|
| `check_freeze` runs the merge-base comparison on the real tree | FD-1282 Finding; FD-1323 Finding; decision 1 (b) | 2, 3 |
| Red on a body edit to a closure, an active plan and a draft plan | decision 1; decision 2 | 1, 3 (Acc. 2a, 2d, 2e) |
| Red on a blanked `corrected_by:` back-link | FD-1282 Amendment 2026-09-30; decision 1 | 1, 3 (Acc. 2c) |
| Red on a backward status move | decision 3, point 3; §1.2a | 1, 2 (Acc. 2b) |
| Base ref per CI event; `fetch-depth: 0` wherever it runs | decision 3, points 1 and 2 | 4 |
| Positives: register row, ledger append, forward status, new file | decision 3, point 3; FD-1323 Disposition (*"green on a status flip alone, and on a file that is new in the PR"*) | 1, 3 |
| Dry run over the last 20 merged PRs, #986 and CR-838:46 | decision 3, point 3 | 5 |

**Not in scope:**
- The `(a)` amendment itself (A1; the maintainer's).
- Ledger append-only body enforcement (DP-4).
- FD-1280's draft-RL guard. It is WK-1170 too, also on `audit-docs.py` (`_STATUS_SUBSET`,
  `:2017`), but it is another slice.
- Closing FD-1282 and FD-1323 (the auditor's, after the merge).

### Measured premises (at `99afcde215c0817c5ac4db55332ab7a69e4752a0`)

**P1 — the check is vacuous today.** `check_freeze` (`scripts/audit-docs.py:2382-2424`)
never calls the predicate. `grep -n frozen_diff_is_permitted scripts/audit-docs.py` gives the
definition and docstring mentions only. `grep -n "sys.argv\|subprocess" scripts/audit-docs.py`
prints nothing, so the script takes no base ref and runs no git.

**P2 — the predicate is narrower than its spec on status.** `frozen_diff_is_permitted`
refuses only a move *away from* a terminal word (`:2169-2171`). `active → draft` returns
`(True, '')`. §1.2a says *"Transitions run forward only"*, and §1.11 row 34 says
*"`status:` (forward only)"*. Code and spec disagree; see DP-3.

**P3 — the dry run, done once at planning time with the shipped predicate.**

- Instrument: a scratch script that loads `scripts/audit-docs.py` by path. For each range it
  runs `git diff --name-status -M <base> <head> -- docs` and skips `A` and `D` rows. It parses
  both sides with `_docid.parse_header_text`, keeps files whose new header family is in
  `_FROZEN_FAMILIES`, and calls `frozen_diff_is_permitted(old, new, old_body=…, new_body=…)`.
  The body is the text after the closing `---` line.
- Corpus: first-parent commits `c~1..c` on `origin/main`.
- Results:
  - **The last 20 merges** (`99afcde2` back to `8252741c`): 3 frozen-family modifications.
    All 3 pass: the activations of PL-1408, PL-1382 and PL-1403, each a `status:` flip.
    **0 reds.**
  - **PR #986** (`caa4e411..9d8199a7`): **1 red**, PL-1276, `the body changed`.
  - **All 239 merges after the W37-6 migration** (`71f5a220..99afcde2`): 71 modifications,
    29 pass and **42 red**, every one `the body changed`, across 31 merges. By family: finding
    17, plan 15, closure 5, ruling 4, proposal 1. The newest red is `22fe674b`
    (2026-09-30, PL-1299's activation, accepted by decision 2). **No red after the
    maintainer's 2026-09-30 14:48:52 direction.**
  - CR-838 is red at `40739df0` (2026-09-29, FD-1241), which is the maintainer's (by delegation) "CR-838:46".
- This count is body changes, not violations: none was classified, and A1's ruling on DP-1
  decides which of them the rule allowed.

**P4 — callers.** `grep -rn "audit-docs" .github/workflows` shows `docs.yml:68` running the
script, with `fetch-depth: 0` at `:45`. `python.yml:302` runs `uv run pytest -q`, and its
tests run the script by subprocess (for example `tests/test_audit_docs_ids.py:1547`). That
checkout is `fetch-depth: 0` at `:144`. `scripts/_docverify.py:3244-3245` runs a snapshot's
own `audit-docs.py` inside `migrate --verify` (`_run_script`, `:755`). `scripts/doc-id.py:1120`
loads the module but never calls `main()`. `history-policy.yml` does not run it.

## Decision points

Kind, blocking status and resolver per RFC-937 §1.7.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | May a frozen body take a dated appended note (FD essay, CR, RL)? P3: 17 FD, 5 CR and 4 RL body edits since the migration, none since 2026-09-30 14:48. | (a) No. Every frozen body is byte-identical after its first merge. Corrections go through a correcting record and `corrected_by:`. `findings/README.md:60` is amended. (b) A per-family append-only body: the new body starts with the old body byte for byte, and the addition opens with a dated heading. The predicate gains that allowance for the named families. (c) As (a), but FD essays only are append-only. | **(a).** It is the rule as written (`:134-135`). It is the maintainer's direction for plans (*"no prose is added to a plan already on main"*). The lead applied it to RL-1401 on 2026-10-05. It needs no new predicate clause. Under (b) or (c) this plan is superseded with one more predicate clause and test. | decision point | **yes** | A1's `RL-` (pending) |
| DP-2 | Is deleting a frozen-family file a check-34 violation? | (a) Yes: `D` of a file whose base header is a frozen family fails. (b) No: another check's concern. | **(a).** §1.6's FD row says *"never removed"*. A deleted record breaks every citation to it, and P3 finds no deletion of a merged frozen file. | design unknown | no. Default (a) until A1 or the lead says otherwise. | the lead at dispatch |
| DP-3 | The predicate refuses only a move away from a terminal status. §1.2a and §1.11 row 34 say "forward only". Which is right? | (a) The spec. The predicate gains a rank (`draft` 0, `active` 1, `closed`/`retired`/`superseded` 2) and refuses a lower rank. (b) The code. The spec is amended to "never from a terminal word". | **(a).** The spec says it twice, and decision 3 point 3 requires *"a status moved backwards"* to fail. This is a code-vs-spec question, so it is the decision-maker's to rule (`delivery-process.md` §3). The planner only recommends. | spec-vs-code | no. Default (a), which decision 3 already requires. | the decision-maker at dispatch, or A1 |
| DP-4 | Should check 34 also enforce append-only on ledgers (body and `plans:`)? | (a) Not in this slice. Ledgers stay outside the comparison, as `_FROZEN_FAMILIES` has them today. (b) Add ledgers with an append-only body variant. | **(a).** Neither finding asks for it, and decision 3 wants a ledger append green. §1.11 row 34's *"ledgers only — an append to `plans:`"* stays unenforced. The executor lists that in the ledger as a residual, for the auditor to file or not. | scope | no. Default (a). | the lead at dispatch |
| DP-5 | This slice and PL-1276, WK-1170's `draft` map plan, whose 2026-09-30 roadmap line says it *"takes them into its scope at activation"* | (a) A standalone slice under WK-1170, `relates: [PL-1276]`. PL-1276 is frozen and not edited. Its successor or its dispatch delta records this slice as already cut. (b) Hold this slice until PL-1276 is activated or superseded. | **(a).** The maintainer's (by delegation) 13:24:56 entry schedules the fix on its own lane. PL-1276 is frozen (#986 was closed for editing it). | scope | no. Default (a). | the lead |

## Contention (RL-1263) and write set

**Write set** (every path the slice changes):
- `scripts/audit-docs.py`:
  - `frozen_diff_is_permitted`: one status-rank clause;
  - new `_STATUS_RANK`, `_FREEZE_BASE_*` constants, `FreezeBaseError`,
    `_front_matter_body`, `_git` and `freeze_violations`, beside it;
  - `check_freeze`: body and docstring;
  - the module docstring, item 34;
  - two `import`s (`os`, `subprocess`).
- `tests/test_audit_docs_freeze.py`, a new file.
- `.github/workflows/docs.yml`: the `audit-docs` step only.
- `.claude/skills/docs-audit/SKILL.md`: the check-34 paragraph (`:309`).
- `scripts/_docverify.py` `_run_script` (`:779-788`): one line, **only if** Task 6 Step 2
  finds a change.
- Existing tests that run check 34 over a non-git `tmp_path` tree, if any go red. Candidates:
  `tests/test_audit_docs_ids.py:1071`, `:1145`, `tests/test_audit_docs_w37_11_ceiling.py:770`.
  The fix is one `monkeypatch.setenv("AUDIT_DOCS_FREEZE_BASE", "none")` line each, and no
  assertion is weakened.
- The slice ledger under `docs/ledgers/`, the `SL-` row's status (the lead's), and
  `docs/INDEX.md` (regenerated).

*Snapshot: open PRs at `99afcde215c0817c5ac4db55332ab7a69e4752a0`, 2026-10-05; working ids as then.*
*Pre-mint check of 2026-10-05 15:57 BST, at `cdaaa573`:* SL-1409 has merged (`cdaaa573`, #1157);
its row's "None" holds. PL 9688 is now draft PR #1145 (`2f3269c8`). The same grep finds only two
`audit-docs.py` runs (its gate list and one Step 2). **None.**

**Against the six slices named for this lane** (each plan read for my write set with
`grep -E 'audit-docs\.py|\.github/workflows|tests/test_audit_docs|document-ids\.md|findings/README|_docid\.py|check_freeze'`):

| Slice | Plan read | Overlap |
|---|---|---|
| SL-1409 | PL-1408 on main | Runs `audit-docs.py` (`:1069`, `:277`) and edits none of it. **None.** |
| SL-1391 | PL 9716, #1127 diff | Runs it only. **None.** |
| WK-675 S2 | PL 9713, #1131 diff | Runs it only. **None.** |
| SL-1387 | PL 9689, #1138 diff | Runs it only. **None.** |
| FD 9708 fix | PL 9683, #1140 diff | Runs it only. **None.** |
| FD 9707 fix | PL 9688 | No PR found (`gh pr list --state all --search 9688`). **Not read.** The lead checks it at dispatch. |

Shared paths: `docs/roadmap.md` (different rows; the lead writes row status) and
`docs/INDEX.md` (generated, exempt under RL-1263's option (c)). **No existing function is
shared with any of the six**, so the slice may run beside any one of them.

**Behaviour, not files: one cross-lane effect at go-live.** From the merge on, any PR whose
diff edits a frozen body goes red in docs CI. That is the purpose, and the maintainer's (by delegation) interim
ACK diff becomes the check. A branch cut before the merge is judged only on its own diff, so
there is nothing to rebase for. **Serialise with WK-1170's other `audit-docs.py` work.** The
register rows for FD-1280 and FD-1282 say *"serialised on `audit-docs.py`"*. At `99afcde2`
none of that is dispatched (PL-1276 and PL-1277 are `draft`).

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Quote A1's merged `RL-` (its id, its DP-1 option and the §1.11 row 34 text
  naming the base) into the ledger. If DP-1 ruled (b) or (c), **stop**: the plan is
  superseded before dispatch.
- [ ] **Step 2:** Quote the lead's dispatch record: lane, gate slot, DP-2 to DP-5 as ruled or
  defaulted.
- [ ] **Step 3:** `git -C <worktree> rev-parse HEAD origin/main` and `uv sync --all-packages`
  (`dev-commands`; a fresh worktree needs it).
- [ ] **Step 4 (the escape, before any code):** in the scratch worktree, apply Acceptance
  2(a). Run `AUDIT_DOCS_FREEZE_BASE=origin/main python3 scripts/audit-docs.py; echo $?` and
  record **0**: the variable is ignored and the escape reproduces. Revert, and confirm with
  `git status --short` (empty).

### Task 1: The tests, red

**Files:**
- Create: `tests/test_audit_docs_freeze.py`

**Interfaces:**
- Consumes: `audit.freeze_violations(base: str) -> tuple[str, int, list[str]]` (Task 2):
  `(merge_base_sha, compared_count, messages)`. Each message reads `"<repo-relative path>:
  <reason>"`, without the `check 34: ` prefix. It reads `audit.REPO` and raises
  `audit.FreezeBaseError` when the base or git fails. Also `audit.frozen_diff_is_permitted`.

- [ ] **Step 1: Write the test file.**

```python
"""Check 34's live half: the merge-base comparison (PL 9662; FD-1282, FD-1323).

No `@pytest.mark.req` marker: this tests the audit tool, not a requirement (same reason as
tests/test_audit_docs_ids.py:29). Each test builds a two-commit git repository under tmp_path
and points `audit.REPO` at it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"

PLAN = """---
id: PL-1000
family: plan
kind: leaf
title: t
status: {status}
created: 2026-10-01
owner: planner
tree: abc1234
phase: P2
work: WK-1170
supersedes: []
superseded_by: ~
corrected_by: []
relates: []
---

# PL-1000 - t

Body line.
"""

RULING = """---
id: RL-1001
family: ruling
title: t
status: active
created: 2026-10-01
owner: decision-maker
tree: abc1234
supersedes: []
superseded_by: ~
corrected_by: {corrected_by}
corrects: ~
relates: []
---

# RL-1001 - t

Ruling body.
"""

LEDGER = """---
id: LG-1002
family: ledger
title: t
status: active
created: 2026-10-01
owner: executor
plans: [PL-1000]
corrected_by: []
relates: []
---

# LG-1002 - t

Entry 1.
"""

REGISTER = "# Global register of open findings\n\n| row |\n"

PL_PATH = "docs/plans/PL-01000-t.md"
RL_PATH = "docs/rulings/RL-01001-t.md"
LG_PATH = "docs/ledgers/LG-01002-t.md"
REG_PATH = "docs/findings/register.md"


def _load(name: str, path: pathlib.Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout


def _write(repo: pathlib.Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """One base commit on `main` with a frozen plan, a ruling with a back-link, a ledger
    and the headerless register; edits are made on top, uncommitted unless a test commits."""
    _git(tmp_path, "init", "--initial-branch=main", "--quiet")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "Test")
    _write(tmp_path, PL_PATH, PLAN.format(status="draft"))
    _write(tmp_path, RL_PATH, RULING.format(corrected_by="[RL-1003]"))
    _write(tmp_path, LG_PATH, LEDGER)
    _write(tmp_path, REG_PATH, REGISTER)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "--quiet", "-m", "base")
    return tmp_path


@pytest.fixture
def audit(repo: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = _load("audit_docs_freeze_under_test", SCRIPT)
    monkeypatch.setattr(module, "REPO", repo)
    return module


def _messages(audit: types.ModuleType) -> list[str]:
    _sha, _n, messages = audit.freeze_violations("main")
    return messages


# --- red: what the freeze rule refuses ------------------------------------------------


def test_body_line_appended_to_a_frozen_plan_is_refused(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, PL_PATH, PLAN.format(status="draft") + "Appended after merge.\n")
    (msg,) = _messages(audit)
    assert msg.startswith(f"{PL_PATH}: ") and "the body changed" in msg


def test_body_edit_to_an_active_plan_is_refused(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, PL_PATH, PLAN.format(status="active"))
    _git(repo, "commit", "--quiet", "-am", "activate")
    _git(repo, "branch", "base2")
    _write(repo, PL_PATH, PLAN.format(status="active").replace("Body line.", "Body EDITED."))
    _sha, _n, messages = audit.freeze_violations("base2")
    assert len(messages) == 1 and "the body changed" in messages[0]


def test_status_moved_backwards_is_refused(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, PL_PATH, PLAN.format(status="active"))
    _git(repo, "commit", "--quiet", "-am", "activate")
    _git(repo, "branch", "base2")
    _write(repo, PL_PATH, PLAN.format(status="draft"))
    _sha, _n, messages = audit.freeze_violations("base2")
    assert len(messages) == 1 and "status: moved backwards" in messages[0]


def test_blanked_corrected_by_is_refused(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, RL_PATH, RULING.format(corrected_by="[]"))
    (msg,) = _messages(audit)
    assert msg.startswith(f"{RL_PATH}: ") and "corrected_by: entries were removed" in msg


def test_committed_edit_is_refused_as_well_as_uncommitted(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _git(repo, "checkout", "--quiet", "-b", "pr")
    _write(repo, PL_PATH, PLAN.format(status="draft") + "Appended.\n")
    _git(repo, "commit", "--quiet", "-am", "edit")
    (msg,) = _messages(audit)
    assert "the body changed" in msg


def test_deleting_a_frozen_file_is_refused(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:  # DP-2 (a)
    (repo / PL_PATH).unlink()
    (msg,) = _messages(audit)
    assert msg.startswith(f"{PL_PATH}: ") and "deleted" in msg


def test_unresolvable_base_raises_never_skips(audit: types.ModuleType) -> None:
    with pytest.raises(audit.FreezeBaseError):
        audit.freeze_violations("no-such-ref")


# --- green: what the freeze rule permits ----------------------------------------------


def test_forward_status_flip_alone_is_permitted(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, PL_PATH, PLAN.format(status="active"))
    _sha, compared, messages = audit.freeze_violations("main")
    assert messages == [] and compared == 1


def test_corrected_by_append_is_permitted(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, RL_PATH, RULING.format(corrected_by="[RL-1003, RL-1004]"))
    assert _messages(audit) == []


def test_living_register_row_is_not_compared(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, REG_PATH, REGISTER + "| new row |\n")
    _sha, compared, messages = audit.freeze_violations("main")
    assert messages == [] and compared == 0


def test_ledger_append_is_not_refused(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:  # DP-4 (a)
    _write(repo, LG_PATH, LEDGER + "Entry 2.\n")
    assert _messages(audit) == []


def test_new_file_in_the_change_is_permitted(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    _write(repo, "docs/plans/PL-01005-new.md", PLAN.replace("PL-1000", "PL-1005").format(status="draft"))
    _git(repo, "add", "-A")
    assert _messages(audit) == []


def test_merge_base_not_tip_is_the_comparison_point(
    audit: types.ModuleType, repo: pathlib.Path
) -> None:
    """A base branch that moved on after the fork must not make its own later edits
    look like this change's (the maintainer's (by delegation) point 1: the merge-base, not the base tip)."""
    _git(repo, "checkout", "--quiet", "-b", "pr")
    _git(repo, "checkout", "--quiet", "main")
    _write(repo, PL_PATH, PLAN.format(status="active"))
    _git(repo, "commit", "--quiet", "-am", "main moves on")
    _git(repo, "checkout", "--quiet", "pr")
    merge_base, _n, messages = audit.freeze_violations("main")
    assert messages == []
    assert merge_base == _git(repo, "rev-parse", "main~1").strip()


# --- the predicate's new clause, on constructed headers (DP-3 (a)) ----------------------


def test_predicate_refuses_active_to_draft(audit: types.ModuleType) -> None:
    old = audit._docid.parse_header_text(PLAN.format(status="active"))
    new = audit._docid.parse_header_text(PLAN.format(status="draft"))
    ok, reason = audit.frozen_diff_is_permitted(old, new, old_body="b\n", new_body="b\n")
    assert ok is False and "moved backwards" in reason
```

- [ ] **Step 2: Run it, expect red by cause.**
  Run: `uv run pytest -q tests/test_audit_docs_freeze.py; echo $?`
  Expected: rc 1. Thirteen tests fail with `AttributeError: module
  'audit_docs_freeze_under_test' has no attribute 'freeze_violations'`, or
  `'FreezeBaseError'` for `test_unresolvable_base_raises_never_skips`.
  `test_predicate_refuses_active_to_draft` fails on `assert ok is False`, because the shipped
  predicate returns `(True, '')` (P2). Any other failure text is a defect in the test or the
  plan. Record it and stop.

- [ ] **Step 3: Commit.**

```bash
git add tests/test_audit_docs_freeze.py
git commit -m "test(audit-docs): check 34's merge-base comparison, red first (PL 9662)"
```

### Task 2: The predicate's forward-only status clause and `freeze_violations`

**Files:**
- Modify: `scripts/audit-docs.py`:
  - the imports at `:112-128` (add `import os`, `import subprocess`);
  - `frozen_diff_is_permitted` (`:2142-2192`);
  - the new code goes directly after it, before the `@functools.lru_cache(maxsize=8)` decorator of `_inverse_token_pattern` (`:2195-2196`).

**Interfaces:**
- Produces: `_STATUS_RANK: Final[dict[str, int]]`, `FreezeBaseError(Exception)`,
  `_front_matter_body(text: str) -> str | None`, `freeze_violations(base: str) -> tuple[str,
  int, list[str]]`, and the constants `_FREEZE_BASE_ENV = "AUDIT_DOCS_FREEZE_BASE"`,
  `_FREEZE_BASE_DEFAULT = "origin/main"` and `_FREEZE_BASE_OFF = "none"`.

- [ ] **Step 1: The status clause.** In `frozen_diff_is_permitted`, directly after the
  existing terminal check (`if old.status != new.status and old.status in terminal: …`), add
  the code below. Add `#: §1.2a: "Transitions run forward only; closed, retired and
  superseded are terminal."` above a module-level `_STATUS_RANK`, next to `_FROZEN_FAMILIES`.
  Amend the docstring bullet to *"`status:` may only move forward (§1.2a), never from a
  terminal word"*.

```python
_STATUS_RANK: Final = {"draft": 0, "active": 1, "closed": 2, "retired": 2, "superseded": 2}
```

```python
    old_rank = _STATUS_RANK.get(old.status)  # type: ignore[attr-defined]
    new_rank = _STATUS_RANK.get(new.status)  # type: ignore[attr-defined]
    if old_rank is not None and new_rank is not None and new_rank < old_rank:
        return False, f"status: moved backwards, {old.status!r} to {new.status!r}"  # type: ignore[attr-defined]
```

  A word outside the vocabulary is check 33's job, so the rank returns `None` for it and this
  clause ignores it.

- [ ] **Step 2: The live comparison.** Insert after `frozen_diff_is_permitted`:

```python
#: Check 34's comparison base (PL 9662). Unset: `origin/main`, for a local run. CI sets the
#: PR's base commit on `pull_request` and the previous main tip on `push`
#: (.github/workflows/docs.yml). `none` turns the comparison off, and the note says so: it
#: is for a tree with no git history, never for CI.
_FREEZE_BASE_ENV: Final = "AUDIT_DOCS_FREEZE_BASE"
_FREEZE_BASE_DEFAULT: Final = "origin/main"
_FREEZE_BASE_OFF: Final = "none"


class FreezeBaseError(Exception):
    """The comparison base, or git itself, failed. Check 34 fails loudly on it and never
    skips (FD-1282 option (c): *"it must fail loudly rather than skip"*)."""


def _front_matter_body(text: str) -> str | None:
    """Everything after the closing `---` line, byte-exact (a trailing newline counts);
    `None` when `text` has no front-matter block."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    return None if end == -1 else text[end + len("\n---\n") :]


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=False
    )


def freeze_violations(base: str) -> tuple[str, int, list[str]]:
    """Check 34's live half. Every file under `docs/` that differs between
    `git merge-base <base> HEAD` and the working tree, whose header **at the merge-base**
    is a frozen family, judged by `frozen_diff_is_permitted`. Returns `(merge_base, compared,
    messages)`. Each message is `"<repo-relative path>: <reason>"`, and the caller adds
    the `check 34: ` prefix.

    The working tree, not `HEAD`, is the new side, so an uncommitted edit is caught locally
    (FD-1282 measured both). Additions are not compared: a file new in the change has no
    frozen past. A deletion is a violation (DP-2 (a)). The old side's family decides scope,
    so a change of `family:` is caught by the predicate's field loop.
    """
    found = _git("merge-base", base, "HEAD")
    if found.returncode != 0:
        raise FreezeBaseError(
            f"`git merge-base {base} HEAD` exited {found.returncode}: {found.stderr.strip()}"
        )
    merge_base = found.stdout.strip()
    diff = _git("diff", "--name-status", "-z", "-M", merge_base, "--", "docs")
    if diff.returncode != 0:
        raise FreezeBaseError(f"`git diff {merge_base}` exited {diff.returncode}: {diff.stderr.strip()}")

    tokens = diff.stdout.split("\0")
    compared = 0
    messages: list[str] = []
    i = 0
    while i < len(tokens) and tokens[i]:
        status = tokens[i]
        if status[0] in "RC":
            old_path, new_path, i = tokens[i + 1], tokens[i + 2], i + 3
        else:
            old_path = new_path = tokens[i + 1]
            i += 2
        if status[0] == "A":
            continue
        shown = _git("show", f"{merge_base}:{old_path}")
        if shown.returncode != 0:
            raise FreezeBaseError(f"`git show {merge_base}:{old_path}` exited {shown.returncode}")
        old_text = shown.stdout
        try:
            old_header = _docid.parse_header_text(old_text)
        except _docid.HeaderError:
            continue  # unparseable at the base: check 30's concern, not a freeze verdict
        if old_header is None or old_header.family not in _FROZEN_FAMILIES:
            continue
        compared += 1
        if status[0] == "D":
            messages.append(f"{old_path}: a frozen-family file was deleted")
            continue
        new_text = (REPO / new_path).read_text(encoding="utf-8")
        try:
            new_header = _docid.parse_header_text(new_text)
        except _docid.HeaderError as exc:
            messages.append(f"{new_path}: the front matter no longer parses ({exc})")
            continue
        if new_header is None:
            messages.append(f"{new_path}: the front matter was removed")
            continue
        ok, reason = frozen_diff_is_permitted(
            old_header,
            new_header,
            old_body=_front_matter_body(old_text) or "",
            new_body=_front_matter_body(new_text) or "",
        )
        if not ok:
            messages.append(f"{new_path}: {reason}")
    return merge_base, compared, messages
```

- [ ] **Step 3: Run Task 1's tests.**
  Run: `uv run pytest -q tests/test_audit_docs_freeze.py; echo $?`. Expected: rc 0, 14 passed.
  If `-M` pairs a deleted frozen file with an unrelated added one in a fixture, read it as a
  test-fixture collision, not a pass. Record it.
- [ ] **Step 4:** `uv run pytest -q tests/test_audit_docs_ids.py -k check_34; echo $?`, then
  rc 0. The existing predicate tests still pass, `test_check_34_permits_a_forward_status_change`
  among them.
- [ ] **Step 5: Commit.** `git commit -am "fix(audit-docs): check 34 compares frozen files
  against their merge-base; status forward only (PL 9662, FD-1282)"`

### Task 3: `check_freeze` runs it

**Files:**
- Modify: `scripts/audit-docs.py`:
  - `check_freeze` (`:2382-2424`);
  - the module docstring, item 34 (`:81-84`).

- [ ] **Step 1:** Replace the docstring's second paragraph (`:2387-2392`, from *"No in-scope file is ever a
  frozen-family instance during S1"* to *"live over whatever is in scope."*) with one that
  says three things. The merge-base comparison runs on every invocation against
  `AUDIT_DOCS_FREEZE_BASE` (default `origin/main`; `none` turns it off, visibly). It covers
  the files the change under audit modifies, renames or deletes. The pair cross-check runs
  over everything in scope.
- [ ] **Step 2:** At the end of `check_freeze`, replace the final `notes.append(...)` with:

```python
    base = os.environ.get(_FREEZE_BASE_ENV, _FREEZE_BASE_DEFAULT)
    if base == _FREEZE_BASE_OFF:
        notes.append(
            f"check 34: {frozen_checked} frozen-family file(s) in scope; "
            f"merge-base comparison NOT RUN ({_FREEZE_BASE_ENV}={_FREEZE_BASE_OFF})"
        )
        return
    try:
        merge_base, compared, messages = freeze_violations(base)
    except FreezeBaseError as exc:
        fail(f"check 34: {_FREEZE_BASE_ENV}={base!r}: no comparison is possible — {exc}")
        return
    for message in messages:
        fail(f"check 34: {message}")
    notes.append(
        f"check 34: {frozen_checked} frozen-family file(s) in scope; {compared} changed "
        f"against merge-base {merge_base} of {base}"
    )
```

- [ ] **Step 3:** Module docstring item 34: append *"The comparison base is
  `AUDIT_DOCS_FREEZE_BASE` (default `origin/main`). CI sets the PR's base commit, or on a
  push the previous main tip. The value `none` turns it off, visibly."*
- [ ] **Step 4 (Acceptance 2, 3 and 4 on the real tree):** in a scratch worktree at the
  task's commit, run each probe of Acceptance 2(a) to 2(e) and 3(a) to 3(d). Then run the two
  commands of Acceptance 4. Record each command, its rc and the `check 34` lines verbatim.
  Revert after each one and confirm with `git status --short`. Expected: as Acceptance 2, 3
  and 4 state. Probe 2(b) may also print a check 33 line. Record it, but the check-34 line
  is the one that counts.
- [ ] **Step 5:** `python3 scripts/audit-docs.py; echo $?` on the clean slice head gives rc 0
  (or only check 31, while the ledger carries a working id). The note reads `… 0 changed
  against merge-base <40 hex> of origin/main`, or the count of frozen files the branch
  modifies.
- [ ] **Step 6:** `uv run pytest -q tests/test_audit_docs_check_prefixes.py
  tests/test_audit_docs_ids.py tests/test_audit_docs_w37_11_ceiling.py; echo $?`. If a test
  that runs check 34 over a non-git `tmp_path` now fails with the `no comparison is
  possible` line, add `monkeypatch.setenv("AUDIT_DOCS_FREEZE_BASE", "none")` to that test
  only. List each one in the ledger. Change no assertion.
- [ ] **Step 7: Commit.** `git commit -am "fix(audit-docs): check_freeze runs the comparison;
  AUDIT_DOCS_FREEZE_BASE (PL 9662)"`

### Task 4: CI names the base per event

**Files:**
- Modify: `.github/workflows/docs.yml` (the `audit-docs` step, `:65-68`)

- [ ] **Step 1:** `grep -rn "audit-docs" .github/workflows/ .claude/settings.json
  .claude/hooks/ 2>/dev/null` lists every runner of the script. For each workflow job that
  runs it (directly or through `pytest`), confirm that the job's `actions/checkout` has
  `fetch-depth: 0`. At `99afcde2`, those are `docs.yml:45` and `python.yml:144`. A new runner
  without it is a stop: report it to the lead.
- [ ] **Step 2:** Replace the step with the version below. Keep the comment block, and add a
  three-line comment naming the per-event ref and the maintainer's (by delegation) point 1. Pass the value
  through `env:`, never inline in `run:`. The value is a SHA either way, and `env:` is the
  hardening pattern the 2026-09-28 security review set for workflow expressions.

```yaml
      - name: audit-docs
        id: auditdocs
        continue-on-error: true
        env:
          AUDIT_DOCS_FREEZE_BASE: ${{ github.event_name == 'pull_request' && github.event.pull_request.base.sha || github.event.before }}
        run: python3 scripts/audit-docs.py
```

  On `pull_request`, `actions/checkout` checks out the merge ref, whose first parent is
  `base.sha`. So the merge-base is `base.sha`, and the diff is exactly the PR's change. On
  `push` to `main`, `github.event.before` is the previous main tip. The workflow's `on:`
  block has no other event.
- [ ] **Step 3 (local CI-event rehearsal; `reproducing-ci-locally`):** emulate both events.
  For `pull_request`, `AUDIT_DOCS_FREEZE_BASE=$(git merge-base origin/main HEAD) python3
  scripts/audit-docs.py`. For `push`, check out the slice head in a scratch worktree and run
  `AUDIT_DOCS_FREEZE_BASE=HEAD~1 …`. Record both notes.
- [ ] **Step 4: Commit.** `git commit -am "ci(docs): check 34's base is the PR base commit, or
  the previous main tip on push (PL 9662)"`
- [ ] **Step 5 (after push):** read the slice PR's docs job log. The check-34 note names the
  PR's `base.sha`. Get it with `gh pr view <n> --json baseRefOid`, which equals `base.sha`
  only for a run triggered at that base. Name the run id. A mismatch is explained or the job
  is re-run, never assumed.

### Task 5: The dry run, before going live

**Files:** none committed. The output goes in the ledger.

- [ ] **Step 1:** Write a scratch script under `$CLAUDE_JOB_DIR/tmp`, outside the tree. It
  loads `scripts/audit-docs.py` by path (the `_load` idiom of Task 1) and calls the shipped
  `freeze_violations`, never a copy. For each target commit `c`, it runs a scratch
  `git worktree add --detach <dir> c` and sets `REPO = <dir>`. It calls
  `freeze_violations(f"{c}~1")` for a merge on main. For #986 it calls
  `freeze_violations("<its merge-base with origin/main>")` on a worktree at
  `9d8199a7f887b0e00b5f6941f4897e5324b1c4cc`; fetch it first with
  `git fetch origin pull/986/head`. Then it removes the worktree.
- [ ] **Step 2:** The targets:
  - `git log --first-parent --format=%H -20 origin/main` at the slice's base;
  - #986's head;
  - `40739df0` (CR-838's body edit, the maintainer's (by delegation) "CR-838:46").
- [ ] **Step 3:** In the ledger, record per target: the SHA, the PR number, the compared
  count and every message. Expected: #986 gives one message for PL-1276 (`the body
  changed`), and `40739df0` gives one for CR-838. For the 20, P3 measured 0 reds over
  `99afcde2`'s window. Any red in a later window is listed, not filtered.
- [ ] **Step 4:** Send the list to the lead (≤50 words, plus the ledger path) **before** the
  ACK request. Going live is the merge of Task 4's change.

### Task 6: `migrate --verify` is unchanged

- [ ] **Step 1:** In the granted gate slot, never during another lane's gate (`dev-commands`),
  run the docs.yml `doc-id verify` command block verbatim (`docs.yml:120-138`). Run it once on
  the slice's base and once on the slice head, with `RUNNER_TEMP` set to two scratch
  directories. Save both outputs and `diff` them.
- [ ] **Step 2:** If the diff is empty, record that and stop: the snapshots run their own
  pre-fix `audit-docs.py` (P4), so no code change is needed. If it is not empty and the cause
  is check 34 inside a snapshot, add one line to `_run_script`
  (`scripts/_docverify.py:779-788`) after `env["PYTHONDONTWRITEBYTECODE"] = "1"`:

```python
    # A migration snapshot has no merge-base to compare against; the migration's own
    # allowance is `frozen_file_matches_after_migration_stamp` (PL 9662).
    env["AUDIT_DOCS_FREEZE_BASE"] = "none"
```

  Then re-run Step 1 and expect an empty diff. Commit with `fix(docverify): snapshots run
  check 34 without a merge-base (PL 9662)`.

### Task 7: Skill text, gate, ledger

- [ ] **Step 1:** In `.claude/skills/docs-audit/SKILL.md`, at the check-34 paragraph (`:309`),
  say:
  - the comparison now runs, and against what;
  - how to set `AUDIT_DOCS_FREEZE_BASE`;
  - that `none` is for trees without history and is never set in CI.

  Refresh its `## Verified` date with the tree. Commit with
  `docs(skills): docs-audit — check 34's base (PL 9662)`.
- [ ] **Step 2:** The full two-half gate (Acceptance 9) in the granted slot. Record every rc.
- [ ] **Step 3:** The ledger lists:
  - Acceptance 1 to 9, each with its evidence;
  - the DP-4 residual (§1.11 row 34's ledger `plans:` clause stays unenforced);
  - every test given `none` in Task 3 Step 6.

## Hand-off

Executor → slice audit (the auditor, against this plan's Acceptance Standard and the range
`origin/main...<slice branch>`) → the lead's merge. After the merge, the auditor closes FD-1282
in place, citing the PR. FD-1323 closes as a duplicate at the next batch (the maintainer's (by delegation)
13:24:56 item (b)), and nothing in this slice writes it.

## Self-review

1. **Spec coverage.** Every row of the Scope table has a task. Decision 1's "(b) … proven red
   on a body edit to a closure" is Acceptance 2(d). Its blanked back-link is 2(c). Decision 2's
   active plan, closure and draft plan are 2(e), 2(d) and 2(a). Decision 3:
   - point 1 is Task 4 and Acceptance 5;
   - point 2 is Task 4 Step 1;
   - point 3's reds are 2(a) to 2(c), its positives are 3(a) to 3(c), and its dry run is
     Task 5.

   FD-1323's "a file that is new in the PR" is 3(d).
2. **Placeholder scan.** None. The slice working id 9655 is the lead's reservation in
   `eta.md` (5 Oct 13:32:42), and it is replaced at the mint with the plan's own id.
3. **Type consistency.** `freeze_violations(base: str) -> tuple[str, int, list[str]]` is used
   with that shape in Task 1 (`_sha, compared, messages`), Task 3 and Task 5. Messages carry
   no prefix in Task 2, and `check_freeze` adds `check 34: ` in Task 3, which the prefix test
   requires.
4. **Literals checked against the source at `99afcde2`**:
   - `_FROZEN_FAMILIES` (`:2130`), `frozen_diff_is_permitted` (`:2142`), `check_freeze`
     (`:2382`), `fail`/`notes` (`:251-255`), `_docid.parse_header_text` and `HeaderError`;
   - `_CHECK_PREFIX_RE` (`tests/test_audit_docs_check_prefixes.py:43`);
   - `_run_script`'s `env` (`scripts/_docverify.py:779-788`);
   - `docs.yml:45`, `:65-68` and `python.yml:144`;
   - RL-881's `corrected_by: [RL-1290]`, PL-1408's `status: active`, PL-1276's
     `status: draft`, LG-1412's `family: ledger` and CR-1212's `status: active`.

   The three fixture headers in Task 1 were parsed with `_docid.parse_header_text` at this
   tree: plan, ruling, and a headerless register returning `None`.
