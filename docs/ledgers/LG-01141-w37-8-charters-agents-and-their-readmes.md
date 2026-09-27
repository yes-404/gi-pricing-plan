---
id: LG-1141
family: ledger
title: W37-8 — charters, agents and their READMEs
status: active
created: 2026-09-27
owner: executor
tree: 7a519fce5673f7b494ed0304daf27ee013da58c9
phase: P2
work: WK-697
plans: [PL-1071]
corrected_by: []
relates: []
---

# LG-1141 — W37-8 — charters, agents and their READMEs

Executed task by task from `PL-1071` (`status: active`), under `RL-1140`. Cut from
`origin/main` at `7a519fce5673f7b494ed0304daf27ee013da58c9` (#805, RL-1140 + PL-1071
activation). One PR per charter file or file class, per D2 (deputy, 2026-09-26 17:06:12
BST, riders 23:54:10 BST).

## Tasks

### Task 1 — baseline, preconditions, the two exclusions

**Step 1 — gating events.** `docs/closures/CR-01064-...md:632`, *"Maintainer acceptance:
Maintainer decision by delegation (deputy, on the maintainer's instruction of 2026-09-26
17:02:52 BST), 2026-09-26 17:06:12 BST. Accepted as filed..."* — dated, not `_pending_`.
`docs/closures/CR-01065-w37-6-checkpoint-3-close.md` exists on `origin/main`. Both gating
events landed; slice released.

**Step 2 — baseline, at `7a519fce5673f7b494ed0304daf27ee013da58c9`:**

```text
$ python3 scripts/audit-docs.py; echo AUDIT_EXIT=$?
AUDIT_EXIT=0
$ grep -c "check 30: \.claude/agents/" /tmp/w37-8-base.txt
7
$ grep -n "^DISCLOSED" /tmp/w37-8-base.txt
31:DISCLOSED (878, at or under the W37-11 residue ceiling):
$ python3 scripts/doc-id.py check; echo DOCID_EXIT=$?
DOCID_EXIT=0
$ python3 scripts/doc-index.py --check; echo INDEX_EXIT=$?
INDEX_EXIT=0
```

`AUDIT_DISCLOSED_BASE=878`, `AGENT_CHECK30_BASE=7`, cut head =
`7a519fce5673f7b494ed0304daf27ee013da58c9`. The 878 figure differs from `PL-1071`'s filed
957 at `a8b3c39` — read as a trend at the disclosure boundary (`CLAUDE.md` §10, `RFC-789`),
not asserted against the plan's number: intervening slices (W37-7 #795, W37-10 #804) moved
it. This slice is expected to lower the agent-file component of it by up to 7.

**Step 3 — DP-8.6's two exclusions, re-verified at this tree:**

```text
$ grep -n "statusMessage" .claude/settings.json
12:            "statusMessage": "Checking retry cap (RFC-895 C2)..."
$ ls .claude/ | grep -x notes; echo NOTES_DIR_EXIT=$?
NOTES_DIR_EXIT=1
$ grep -c 'notes/0' docs/REDIRECTS.csv
95
```

The `statusMessage` citation names the post-migration id form (`RFC-895 C2`); the stub
directory does not exist; `REDIRECTS.csv` carries 95 rows for `notes/0*` stubs. DP-8.6
still holds (`RL-1140` DP-8.6, "verified now"). Not reopened.

**Step 4 — ownership-matrix invocation.** `scripts/doc-index.py --help` exposes no
dedicated flag; the ownership matrix is part of the default (no-flag) regeneration's
output, function `ownership_matrix()` (`scripts/doc-index.py:958`), rendered into
`docs/INDEX.md`'s `## Ownership matrix` section (`:1258-1263`). The verbatim invocation
this slice's acceptance item 2 is read against:

```bash
python3 scripts/doc-index.py   # regenerates docs/INDEX.md
sed -n '/## Ownership matrix/,/^$/p' docs/INDEX.md
```

Recorded output at this tree (before T6):

```text
| role | owns |
|---|---|
| decision-maker | requirement (FR/NFR/DEP), open question (OQ), workflow (WF), decision (ADR), ruling (RL) |
| maintainer | phase, work (WK), proposal (RFC), ruling (RL), reference: process/, reference: charters |
| planner | work (WK), slice (SL), plan (PL map/leaf) |
| executor | plan (PL handover), ledger (LG), research (RS spike/measurement), reference: contracts/ |
| auditor | plan (PL review), research (RS audit), closure (CR), finding (FD) |
| lead | phase, proposal (RFC), closure (CR), reference: skills, reference: agents |
| reporter |  |
| watcher |  |
```

The last two rows are blank — not yet the *declared*-empty state T6 targets; they are
merely uninverted (no role names them, because the charters do not yet say "owns no
governed document"). T6's acceptance is read against a re-run of this same invocation.

### Task 2

Landed in squash `35c954c1` (#806) — branch commit `c6964a2` (pre-squash branch commit,
reachable via `refs/pull/806/head`) is the fix commit, on branch `w37-8-t1-t2`. Fixes check 30
(`scripts/audit-docs.py`) to consult the family's derived policy for an extra rather than
failing every one unconditionally; declares the four Claude Code harness keys
(`name:`, `description:`, `tools:`, `model:`) in `docs/_templates/REFERENCE.md`'s
top-level `---` block (not the unread commented foot); adds a three-case test in
`tests/test_audit_docs_ids.py` with three new fixtures under
`tests/fixtures/docs-ids/w37-4-checks/`. `scripts/_docid.py`'s `_KNOWN_KEYS` is untouched.

**Broken-input proof (`CLAUDE.md` §13), run at this tree:**

1. Reverted the fix (restored the old unconditional `fail(...)` loop): the new case-1
   fixture (declared harness keys) fails all four, reproducing `RL-1140`'s own probes 1–3.
2. Restored the fix, then inverted the new conditional
   (`if extra_key not in policy.permitted: continue`): the pre-existing unknown-field
   test and all three new tests turn red — 4 failed, 7 passed
   (`uv run pytest tests/test_audit_docs_ids.py -k check_30 -q`).
3. Restored the correct fix: all 11 check-30 tests green.

**Gate evidence for squash `35c954c1` (#806), covering S-11's code
(`scripts/doc-id.py`, `tests/test_doc_id_migrate.py`) — cited at #806's own final
head `1508cd25` (tree == `35c954c1`), not the earlier branch commit below:**

- **Python CI**, run 36290763531: `GATE: pass — 8 of 8`, `3458 passed, 3 skipped, 1
  xfailed`, collected 3462.
- **Docs CI**, run 36290763538: `GATE: pass — 4 of 4`, `migrate --verify` exit 1 (RL-1045
  §1 pass — the standing red with the verdict set unchanged), check 30 = 0.

Both runs are CI evidence at the PR's own final head, read by the deputy at merge ACK
(`to-lead.md`, 2026-09-27 04:33:36 BST).

**Narrative only — an earlier local gate, run at branch commit `c6964a2` (pre-squash
branch commit, reachable via `refs/pull/806/head`), before the fix reached its final
shape:** 7/7 Python stages pass, pytest 3456 passed / 3 skipped / 1 xfailed (baseline
3457 collected/3 skipped + 3 new tests = 3460 collected); frontend 97 files / 602 tests,
6 stages pass. This reading is superseded by the CI evidence above, which covers the
code S-11 records; logs from this earlier run are at
`~/gi-pricing-plan.local/handover/gate-c6964a2/{python,frontend}/` (local, not repo —
`handover-files-are-local-not-repo`), kept as a historical record of the pre-fix branch
state, not as evidence for the squash.

`python3 scripts/audit-docs.py | grep -c 'check 30: \.claude/agents/'` still prints `7` at
this tree (T3/T4 have not merged headers yet); `grep -n '"tools"\|"model"\|"description"'
scripts/_docid.py` has no hit inside `_KNOWN_KEYS`.

**Gate-table note (supersedes the 01:16:48 diagnosis below):** docs run 36281191974 ran at
branch commit `414a9335` (pre-squash branch commit, reachable via `refs/pull/806/head`;
squashed as `35c954c1`): `doc_id_verify` exited 3. The 01:16:48 BST diagnosis — that check
30's headerless `.claude/` lookup was the regression — was **withdrawn**: a direct
comparison of `python3 scripts/audit-docs.py`'s output between `main` and that branch
commit, run in this worktree, was byte-identical, and `_docverify`'s own snapshot metadata
showed `doc_id_verify`'s (h1) row shells the `--ref` tree's *own* frozen copy of
`scripts/audit-docs.py`, never this branch's — so no check-30 edit on this branch could
ever have moved that row. That fix — a local commit on top of that branch commit — was
reset away (`git reset --hard 414a93353bd5252820fee1c3b4b2ae3b8fd1a5c1`; the full SHA of
the same branch commit, `414a9335`, confirmed identical via `gh api
repos/yes-404/gi-pricing-plan/commits/414a93353bd5252820fee1c3b4b2ae3b8fd1a5c1`) before
pushing — the local-only fix attempt itself left no commit of its own to cite; only the
branch commit it was reset back to (`414a9335`, reachable via `refs/pull/806/head`,
squashed as `35c954c1`) is a real commit.

**The re-diagnosed cause, ruled by the deputy (03:00:11, 03:01:09, 03:21:39 BST), proven
by a control pair** (the branch as-is: 27 fatal residue changes; with only
`docs/_templates/REFERENCE.md` reverted: 0): `scripts/doc-id.py`'s `_template_header_lines`
(`:1123-1136`) reads the checkout's `docs/_templates/REFERENCE.md`, and `_stamp_header`
(`:1139-1206`) passed every key that template declares straight through — including T1's
four new placeholder lines (`name:`, `description:`, `tools:`, `model:`). `migrate()`
therefore stamped those four *placeholder* keys into all 31 of the Reference family's real
stamp targets, and the migrated snapshot's own `audit-docs.py` check 30 then rejected the
placeholder values in 27 of those 31 files (`.claude/agents/*.md`, `.claude/skills/*/
SKILL.md` under `_id_scope_documents()`'s scope roots) — 27 files × 4 keys = the migrated
snapshot's h1 `check 30=108`; the same +4-line mismatch is (g)'s provenance mismatch and
(d)'s +124.

Of the 31 Reference files `migrate()` stamped, four were not flagged by check 30 — root
`README.md`, `deploy/README.md`, `packages/README.md`, `examples/fremtpl2/README.md` —
because they lie outside the four post-migration scope roots (`docs/`, `.claude/roles`,
`.claude/skills`, `.claude/agents`); the other 27 each drew 4 hits (108).

**The fix (S-11, `scripts/doc-id.py`, `tests/test_doc_id_migrate.py`; landed in
`35c954c1`):** one module-level constant in `scripts/doc-id.py`,
`_HARNESS_ONLY_TEMPLATE_KEYS`, naming the same four keys; `_stamp_header` skips them
(next to the existing `slice`/`deliverable`/`lands_in`/`trigger` skip); two new tests
in `tests/test_doc_id_migrate.py` — **correcting the name this section previously gave,
which does not exist in the tree** —
`test_reference_stamp_harness_keys_are_skipped_only_while_the_constant_names_them`
("Test A": asserts none of the four keys are ever emitted with the constant active, AND
that emptying the constant (monkeypatched) makes all four re-appear — the broken-input
proof itself, as an assertion rather than a manual step) and
`test_reference_stamp_harness_key_constant_is_not_a_vacuous_skip` ("Test B": non-vacuity —
the constant is non-empty and every name in it is a real key `docs/_templates/
REFERENCE.md`'s own block declares, so Test A's "not emitted" cannot be trivially true for
the wrong reason).

**Broken-input proof:** removed only the new `elif key in _HARNESS_ONLY_TEMPLATE_KEYS:
continue` skip clause (the constant declaration untouched) — the new tests failed, all four
keys present in the rendered stamp. Restored the clause — the new tests, and the full
`tests/test_doc_id_migrate.py` (303 tests) and `tests/test_audit_docs_ids.py -k check_30`
(11 tests), all passed.

## PRs

| # | Branch | Squash SHA on `main` | Tasks | State |
|---|---|---|---|---|
| #806 | `w37-8-t1-t2` | `35c954c1` | T1, T2 (check 30 fix + S-11's harness-only-key stamp fix, `scripts/doc-id.py` + `tests/test_doc_id_migrate.py`) | merged |
| A (#807) | `w37-8-charters` | `6cad8e4d` | T3, T4 | merged |
| B (#808) | `w37-8-t5-readme` | `ff70de2f` | T5 | merged |
| C (#809) | `w37-8-t6-reporter-watcher` | `99355ab0` | T6 | merged |
| D (#810) | `w37-8-t7-auditor` | `954008f8` | T7 | merged |
| E (#811) | `w37-8-t8-decision-maker` | `3ede6495` | T8 | merged |
| F (#812) | `w37-8-t9-executor` | `a24c0a28` | T9, S-8/S-9/S-10 | merged |
| G (#813) | `w37-8-t10-lead` | `d5501e99` | T10, S-5/S-6 | merged |
| H | `w37-8-h-planner-close` | *this PR* | T11, T12, T13 — the closing PR | draft, open |

**Every SHA above passed the reachability sweep** at this ledger's own head:
`git merge-base --is-ancestor <sha> HEAD; echo $?` → `0` for all eight
(`35c954c1`, `6cad8e4d`, `ff70de2f`, `99355ab0`, `954008f8`, `3ede6495`, `a24c0a28`,
`d5501e99`).

### PR-A (#807) — squash `6cad8e4d` — Tasks 3, 4

Closes CR-1065 §2.4's one W37-8-reassigned §7(i) row (`ci-watcher.md`) and RFC-937 §5.3's
remaining agent rows. Files: `.claude/agents/ci-watcher.md` (T3 — merged header, harness
keys first byte-identical, governed keys after, `owner: lead`; rewrote the dangling
legacy-notes-directory example in the docs.yml trigger table), `.claude/agents/spec-reconciler.md`,
`accessibility-tester.md`, `evidence-collector.md`, `gate-runner.md`,
`performance-engineer.md`, `postgres-pro.md` (T4, DP-8.2 (a) — all seven agent files, not
only the two §5.3 names).

Verification: `grep -L "^family: reference" .claude/agents/*.md` → nothing; `check 30:
.claude/agents/` count 7 → 0; `doc-id.py check` 0; `doc-index.py --check` 0 (byte-stable).
Harness-load check (a fresh `ci-watcher` agent dispatch confirmed `tools:`/`description:`
survive intact).

DISCLOSED: 878 → 870 (−8: 7 from the agent-file class closing check 30, 1 from
ci-watcher.md's legacy-notes-path fix clearing one check-36 legacy-path hit).

Gate, evidence for squash `6cad8e4d` (#807), run at branch commit `d5ec4aad`
(pre-squash branch commit, reachable via `refs/pull/807/head`; both halves): 7/7 Python
stages pass, pytest 3458 passed / 3
skipped / 1 xfailed (3462 collected, matches main's 3462). No residue introduced.

### PR-B (#808) — squash `ff70de2f` — Task 5

File: `.claude/agents/README.md` — cites the Reference family, the agents cell (§5.3's
row: README names agents as Reference family owned by the lead).

### PR-C (#809) — squash `99355ab0` — Task 6

Files: `.claude/roles/reporter.md` (+10/−2 — states "owns no governed document"; adds the
fortnightly `WK-` status-entry clause), `.claude/roles/watcher.md` (+5 — states "owns no
governed document"). Verification: `grep -n "owns no governed document"
.claude/roles/reporter.md .claude/roles/watcher.md; echo GREP_EXIT=$?` → two lines,
`GREP_EXIT=0`.

**This executor's fix, same PR, before it merged:** #809's second branch commit
(`d8d6db8f`, pre-squash branch commit, reachable via `refs/pull/809/head`) had drifted
into editing `docs/ledgers/LG-01141-…` directly — breaking the ruled mechanics (no PR C–G
edits the ledger). Reverted with `git revert --no-edit d8d6db8f` → `3d9758eb` (also a
pre-squash branch commit, reachable via `refs/pull/809/head`), pushed as a fast-forward
(no force); both are superseded by the PR's own squash, `99355ab0`. The reverted text
(T6's ownership-matrix evidence) is saved at
`~/gi-pricing-plan.local/handover/w37-8-ledger-notes/d8d6db8f-pr809-ledger.diff` and
reproduced below in the T6 ownership-matrix section, since that evidence belongs in this
ledger regardless of which PR wrote it.

**T6 ownership-matrix evidence — the tool's own output, not a hand-typed
reconstruction.** An earlier version of this section pasted a table that did not match
the tool's real output (wrong row order for `planner`, `auditor` missing `research (RS
audit)` and carrying a `kind:` split the tool does not produce, `reporter`/`watcher` shown
with prose instead of the tool's literal blank cell). Corrected here by actually running
the command and copying its output, at this ledger's own head:

```bash
python3 scripts/doc-index.py   # regenerates docs/INDEX.md; git status --porcelain empty (byte-stable)
awk '/^## Ownership matrix/{f=1} f' docs/INDEX.md | sed -n '1,20p'
```

```text
## Ownership matrix

| role | owns |
|---|---|
| decision-maker | requirement (FR/NFR/DEP), open question (OQ), workflow (WF), decision (ADR), ruling (RL) |
| maintainer | phase, work (WK), proposal (RFC), ruling (RL), reference: process/, reference: charters |
| planner | work (WK), slice (SL), plan (PL map/leaf) |
| executor | plan (PL handover), ledger (LG), research (RS spike/measurement), reference: contracts/ |
| auditor | plan (PL review), research (RS audit), closure (CR), finding (FD) |
| lead | phase, proposal (RFC), closure (CR), reference: skills, reference: agents |
| reporter |  |
| watcher |  |
```

The `reporter` and `watcher` rows print with **nothing** after the pipe — a blank cell,
not prose — which is what "declared empty" means at the tool's own level: no role name
is attached to any governed-thing family for either, the literal absence Acceptance
Standard item 2 asks for, not a placeholder string. Every other role row is non-empty.
Item 2 is satisfied by this real output, not by the corrected description of it.

No residue introduced by T6 itself.

### PR-D (#810) — squash `954008f8` — Task 7

File: `.claude/roles/auditor.md` — four new-obligation clauses: **CR- filing** (files
every closure record — `CR-` of kind `work` or `phase` — under `docs/closures/`);
**FD- lifecycle** (creates the register row + essay for every `FD-`, sets its disposition
`closed`/`retired`); **LG- close** (sets a slice's `LG-` to `closed` at slice close,
verifies acceptance); **S-4** (rider b, the deputy's 2026-09-26 23:06:30 BST finding — a
slice audit's ledger check is a two-way match **and** a reachability check,
`git merge-base --is-ancestor <sha> <PR head>` per matched SHA). Riders **S-3** (rider a —
the retired findings-README citation rewritten to `docs/findings/README.md`) and **S-7**
(rider e — the pre-migration audit tree path citations rewritten to `docs/closures/`/`docs/findings/`) are
path rewrites, not new obligations.

DISCLOSED reconciled by line name: `origin/main` at PR-D's base = 870; PR-D's own head
(isolated checkout, no other slice's drafts present) = 867. Three lines left, none
arrived: `check 36: .claude/roles/auditor.md:26/:33/:35` (legacy pre-migration audit-tree path), each
fixed by S-7's rewrite.

**Residue D introduced** (the deputy's ruling 06:17:27 BST): `.claude/roles/auditor.md:40`,
token `W37-10`, a check-36 alias-class disclosed hit.

D11 evidence: `audit-docs.py` rc 0, `doc-id.py check` rc 0, `doc-index.py --check` rc 0,
full `tests/` (28 files) + the reduced `backend/tests`/`packages/*/tests` subset
(`grep -rlE '\.claude|REPO_ROOT|docs/'` predicate, 17 files) → 1367 passed, 3 skipped.

### PR-E (#811) — squash `3ede6495` — Task 8

File: `.claude/roles/decision-maker.md` — six new-obligation clauses: **RL-** (own file
under `docs/rulings/`, id via `doc-id.py next` — never a shared document entry);
**FR-/NFR-/DEP-** (created and amended via `spec-change`); **ADR-** (authored via
`adr-write`, `draft` status); **WF-** (workflow journeys via `spec-change`; an executor
delivers and owns `test_wfNN_journey`, never amends it); **OQ-** (recorded by anyone,
closed by the decision-maker citing the resolver); **PL- map/leaf** (rules decision points
as `RL-`, never edits the plan). No riders assigned to this file.

DISCLOSED: 870, identical to its own base `origin/main` 870 at the time — no legacy
citation touched. No residue introduced.

D11 evidence: `audit-docs.py` rc 0, `doc-id.py check` rc 0, `doc-index.py --check` rc 0,
same 17-file reduced test set → 1367 passed, 3 skipped.

### PR-F (#812) — squash `a24c0a28` — Task 9

Files: `.claude/roles/executor.md` and `docs/plans/PL-1071-…md` (§1.4 rider rows, same
commit per standing rule (i)) — four new-obligation clauses: T9's own §1.6 clauses (works
from a `PL-` leaf for its `SL-`; appends its `LG-` per task and per PR, `active`; owns
`RS-` spike/measurement via `library-spike`; owns the `WF-` journey tests; new `Never`
bullet against amending a `WF-`), **S-8** (ruled by the deputy 02:29:40 BST, verbatim: *"a
reproduction already filed as a dated record with its run id discharges the reproduce
step of any debugging skill"*), **S-9** (ruled by the deputy 04:38:48 BST, verbatim:
*"Stop a process by pid, after `readlink /proc/<pid>/cwd` names it as yours; never by
pattern (`pkill -f`, `pkill` by name) — a pattern matches every session's processes on
the box"*), **S-10** (ruled by the deputy 05:52:14 BST, verbatim: *"An executor ends its
turn after every report it files and after every commit, so that the lead's messages are
read before the next action; one turn spans one task, never a sequence of them"*).
**Scope rows S-8/S-9/S-10 landed in `a24c0a28`; evidence here.**

One correction commit inside the same PR (`63bc0eda`, pre-squash branch commit,
reachable via `refs/pull/812/head`, superseded by squash `a24c0a28`; no amend): the
S-8/S-9 rider rows in `PL-1071-…md` initially misattributed both rulings to the lead; corrected to the
deputy, and re-verified (audit-docs/doc-id/doc-index all rc 0 unchanged) before the
fast-forward push.

**Residue F introduced**: `.claude/roles/executor.md:48`, token `W37-9`, a check-36
alias-class disclosed hit (from the "(W37-9's)" note in the branch/PR-convention clause).

D11 evidence: `audit-docs.py` rc 0 (DISCLOSED 870, unchanged from base), `doc-id.py check`
rc 0, `doc-index.py --check` rc 0, same 17-file reduced test set → 1367 passed, 3 skipped.

### PR-G (#813) — squash `d5501e99` — Task 10

File: `.claude/roles/lead.md` — new-obligation clauses: dispatches every `SL-` (`active`);
owns every `CR-` of kind `review`; owns the agent files under `.claude/agents/`; the
hand-kept `Tools:` three-path list replaced with a pointer to `doc-index.py`'s generated
`## Ownership matrix` section in `docs/INDEX.md`. **S-5** (rider c; the deputy,
2026-09-19 15:31:23 and 15:33:03 BST — a governed status file is updated by copying it
and writing the copy, never by a truncating overwrite). **S-6** (rider d; `RL-1140`
DP-8.3(a), F97's register row) — remedy shape drafted: the
**halt-protocol-for-the-shared-checkout** clause (the plan's other option, a
successor-side precondition check, was not taken). `grep -n "F97" .claude/roles/lead.md;
echo F97_GREP_EXIT=$?` → clause printed at `:88`, exit 0. Drafting the clause does not
close F97; its register row's own condition governs the auditor setting it `closed`.

**Residue G introduced**: `.claude/roles/lead.md:88`, token `F97`, bare finding id, a
check-36 alias-class disclosed hit.

D11 evidence: `audit-docs.py` rc 0, `doc-id.py check` rc 0, `doc-index.py --check` rc 0,
same 17-file reduced test set → 1367 passed, 3 skipped.

### PR-H (this PR) — Tasks 11, 12, 13 — the closing PR

**Task 11 — `.claude/roles/planner.md`.** New-obligation clauses: owns the plan as a
`PL-` file with an id from `doc-id.py next`, `draft` while a blocking decision point is
open, `active` on freeze; a replan is a new `PL-` carrying `supersedes: [<old id>]`, never
a new dated revision of the same file, with `superseded_by:` set on the old plan in
return; cuts the `SL-` rows in the map plan (`draft` at minting) and re-cuts them on a
replan. The `Tools:` bullet is rewritten: the `CLAUDE.md` §14 phase review is filed as its
own `CR- kind: review` record under `docs/closures/`, not the pre-migration plan-reviews path
(which does not exist post-migration). **S-7** (rider e, a path rewrite, not a new
obligation): `planner.md:50` and `:53`'s pre-migration audit-tree legacy citations rewritten.

DISCLOSED reconciled by line name at this file's own base (`d5501e99`, isolated
worktree): 867 → 865. Exactly the two planner.md legacy-path hits left, none arrived.

**Task 12 — no maintainer charter (verification only, no repository file changed for
this task).**

```
$ ls .claude/roles/
auditor.md  decision-maker.md  executor.md  lead.md  planner.md  reporter.md  watcher.md
$ ls .claude/roles/maintainer.md
ls: cannot access '.claude/roles/maintainer.md': No such file or directory
```

Seven files, no eighth. Both listings confirmed present: `document-ids.md` §1.6
(`:140-162`) and `CLAUDE.md` §12 each state the maintainer's authorities once.

**Step 3, the third-copy sweep — run twice, both in a clean detached worktree (never
`exec-w37-8-t3`, which carries other slices' uncommitted drafts):**

```
$ git worktree add --detach <path> <ref>
$ grep -rln "maintainer" .claude/roles/ .claude/agents/ docs/process/
```

First run at `origin/main` = `3ede6495` (before F and G merged): 16 files. Second run,
**at this PR's own base** `d5501e99` (after F and G merged, per the lead's instruction to
re-run rather than rely on recollection): identical 16 files, byte-for-byte the same set.
Both runs, every hit classified by reading the actual line(s), not by the grep alone:

- **`owner: maintainer`** / **`"decider": "maintainer"`** front-matter/JSON field (a
  single value, not an enumeration): `.claude/roles/{decision-maker,executor,planner,
  reporter,lead,watcher,auditor}.md`, `docs/process/{security-posture,
  checklists/work-item-close,checklists/phase-close,retrofit-impossible}.md`,
  `docs/process/delivery-process.core.json:394`.
- **Prose mentions of one specific maintainer action or instruction**, not an
  enumeration of the full authority set: `.claude/roles/executor.md` (principal/
  attribution note), `.claude/roles/planner.md` (§14 acceptance line),
  `.claude/roles/reporter.md` (a dated instruction, a channel-routing note),
  `.claude/roles/lead.md` (merge authority, dispatch note — re-checked after F/G merged:
  same class, only the line numbers shifted with the new content above them),
  `.claude/roles/auditor.md` (close acceptance is the maintainer's, one line),
  `.claude/agents/spec-reconciler.md` (one sentence: stays with the maintainer),
  `.claude/agents/README.md` (§14 review proposals; skill-install approval — two narrow
  mentions), `docs/process/delivery-process.md` (four narrow mentions).
- **`docs/process/document-ids.md` §1.6 itself** (`:140-162`) — one of the two canonical
  listings named in step 2, not a third copy. Expected, not a finding.

**Result, both runs: no third copy found.** T12 is discharged as **no contradiction
found**; nothing filed as an `FD-`.

**Task 13 — gate, PR, the §7(i) table.**

§7(i) table — one row per §1.2 file, with the commit that closed it:

| # | File | Task | Closing commit (squash SHA on `main`) |
|---|---|---|---|
| 1 | `.claude/roles/auditor.md` | T7 | `954008f8` (PR-D, #810) |
| 2 | `.claude/roles/decision-maker.md` | T8 | `3ede6495` (PR-E, #811) |
| 3 | `.claude/roles/executor.md` | T9 | `a24c0a28` (PR-F, #812) |
| 4 | `.claude/roles/lead.md` | T10 | `d5501e99` (PR-G, #813) |
| 5 | `.claude/roles/planner.md` | T11 | this PR (H) |
| 6 | `.claude/roles/reporter.md` | T6 | `99355ab0` (PR-C, #809) |
| 7 | `.claude/roles/watcher.md` | T6 | `99355ab0` (PR-C, #809) |
| 8 | `.claude/agents/README.md` | T5 | `ff70de2f` (PR-B, #808) |
| 9 | `.claude/agents/ci-watcher.md` | T3 | `6cad8e4d` (PR-A, #807) |
| 10 | `.claude/agents/spec-reconciler.md` | T4 | `6cad8e4d` (PR-A, #807) |
| 11 | Maintainer authorities | T12 | verification recorded above; no file changed |

Gate, DP-6 lines and the CI evidence for this PR are below, under "H's gate".

## H's gate

**The full two-half gate, first run at head `60914ee8`, tree `gate-60914ee/`.** This
directory carries **no `HEAD.txt` and no `--collect-only` output** — corrected here
after this section previously claimed both. Its tree is established instead by the
executor-transcript bracket (the deputy, 2026-09-27 07:17:3x BST): the commands were run
against the worktree at `60914ee8` before the next commit changed it, read from the
session's own tool-call sequence, not from a file inside the directory. Python 7/7
stages pass (`3458 passed, 3 skipped, 1 xfailed` — **3462 is the full-suite sum, 3458 +
3 + 1**, matching `main`'s own collected count, no test added by this docs-only slice);
frontend 6/6 stages pass (install, generate:api, lint, type-check — 97 files / 602
tests, `Errors: no errors` — build). Logs at
`~/gi-pricing-plan.local/handover/gate-60914ee/{python,frontend}/`.

**`HEAD.txt` and `tests/`-only `--collect-only` (1021) live in the later evidence
passes, not here**: `gate-da99181/` (head `da99181e`) and `gate-0a3451c/` (head
`0a3451c5`) each carry their own `HEAD.txt` (tree + UTC date, written first) and their
own `uv run pytest --collect-only -q tests` output — 1021 at both, and also 1021 at
`60914ee8` itself when it was separately measured in an isolated detached worktree for
that comparison (`gate-da99181/python/collect_tests_at_60914ee8.log`). Frontend was re-run in full, with one `.rc` per command, at **both** `da99181e`
(`gate-da99181/frontend/`, the G2 request's own answer) and `0a3451c5`
(`gate-0a3451c/frontend/`) — per the auditor's finding that `60914ee8`'s frontend logs
carried no `.rc` files. Both re-runs are six-stage passes, all rc 0.

**D11 is closed by H** — the reduced per-PR evidence standard (audit-docs, doc-id check,
doc-index --check, the reduced test subset, docs CI standing in for local verify)
governed C–G only; H runs the full two-half gate over the cumulative tree instead, the
passes named above.

## PL-1071 §5 Acceptance Standard item 8 — the FD-1066…FD-1069 re-read

**This item's own text names T1 step 1 as the control** — "the executor re-reads all
four in full at slice start and reports any W37-8 routing to the lead before T2." That
did not happen: T1's own ledger section (above) records the baseline measurement but no
re-read of the four `FD-`s, and T2 landed without one. **The gap was missed at T1 and
found at T3**, per the lead's own tracking — not run at slice start as the item
requires, run later instead. The re-read below is that late re-read, not the on-time
one; it discharges the item's substance (the four are re-read in full, the ledger
records the result) but not its timing.

Verified by this executor at `origin/main` post-#811:

```
$ grep -n "W37-8" docs/findings/FD-01066*.md docs/findings/FD-01067*.md \
    docs/findings/FD-01068*.md docs/findings/FD-01069*.md
(no output)
```

**Result: no W37-8 routing found**, across all four (`FD-1066` idempotence, `FD-1067`
check-35 two-sub-clause, `FD-1068` standing-CI-verify pinned base, `FD-1069` H1 residue
population disagreement). All four are instrument- or corpus-level and none names
`.claude/roles/` or `.claude/agents/` — the plan's own pre-filing risk assessment holds.
Item 8 is satisfied by this negative result, quoted verbatim, not by a broader claim.

## Acceptance Standard items 3, 5, 7, 11 — evidenced

**Item 5 — `ci-watcher.md` is closed by a named commit.**

```
$ /usr/bin/git log --oneline -1 -- .claude/agents/ci-watcher.md
6cad8e4d docs(agents): W37-8 T3+T4 — the seven agent files carry the governed Reference header (#807)
```

Names `6cad8e4d`, a commit in this slice's chain — not `3f41d60`. The commit and the
file appear as row 9 of T13's §7(i) table above.

**Item 3 — a dated maintainer line exists for every charter edit.** Per delegation (the
deputy, D2, on the maintainer's instruction of 2026-09-26 17:02:52 BST), quoted verbatim
on each PR's comments:

| File | Line date (BST) | PR |
|---|---|---|
| `.claude/roles/reporter.md` | 2026-09-27 05:54:22 | #809 |
| `.claude/roles/watcher.md` | 2026-09-27 05:54:22 | #809 |
| `.claude/roles/auditor.md` | 2026-09-27 06:13:29 | #810 |
| `.claude/roles/decision-maker.md` | 2026-09-27 06:27:26 | #811 |
| `.claude/roles/executor.md` | 2026-09-27 06:33:34 | #812 |
| `.claude/roles/lead.md` | 2026-09-27 06:52:13 | #813 |
| `.claude/roles/planner.md` | *pending — H is still under review* | #814 |

Six of seven lines are in hand; `planner.md`'s is requested alongside this PR's own
merge acknowledgement (item 11, below) — H is the PR carrying it, so the line cannot
predate the PR that names the file.

**Item 7 — F97 has a disposition with a date.** Drafted, not declined: `.claude/roles/
lead.md`'s S-6 clause (PR-G, `#813`, squash `d5501e99`) is the halt-protocol-for-the-
shared-checkout remedy shape, with its own dated maintainer line (item 3's row above,
2026-09-27 06:52:13 BST). `grep -n "F97" .claude/roles/lead.md; echo
F97_GREP_EXIT=$?` → clause printed at `:88`, exit 0. Drafting the clause does not close
F97 itself — its register row's own condition (a zero-byte `.git/index.lock` planted on
a clean tree yields a named report) governs the auditor setting it `closed` separately.

**Item 11 — the deputy's merge acknowledgement per PR, before the lead merges.** A
distinct record from item 3's D2 charter lines above — every one of #806–#813 got a
MERGE ACK (including #806–#808, which touch no `.claude/roles/` file and so have no
item-3 line at all), each in `~/gi-pricing-plan.local/channel/to-lead.md`:

| PR | ACK stamp (BST) | Opening line, quoted |
|---|---|---|
| #806 | 2026-09-27 04:33:36 | "Deputy ruling: **ACK.**" — CI + pool reading agreed, T1+T2 |
| #807 | 2026-09-27 05:22:47 | "Deputy ruling: **ACK.**" — T3+T4, agent headers |
| #808 | 2026-09-27 05:41:34 | "Deputy ruling: **ACK.**" — T5, agents README, behind-by-disjoint-merge path |
| #809 | 2026-09-27 06:11:46 | "Deputy ruling: **ACK.**" — T6, reporter/watcher + this executor's revert |
| #810 | 2026-09-27 06:25:56 | "Deputy ruling: **ACK.**" — T7, auditor.md, arrived residue named |
| #811 | 2026-09-27 06:31:32 | "Deputy ruling: **ACK.**" — T8, decision-maker.md |
| #812 | 2026-09-27 06:50:29 | "Deputy ruling: **ACK.**" — T9, executor.md + S-8/S-9/S-10 |
| #813 | 2026-09-27 06:53:34 | "Deputy ruling: **ACK.**" — T10, lead.md + S-5/S-6, arrived residue named |

No row for #814/H: its ACK is recorded on the PR itself at merge, per the deputy's
07:07-area instruction, not pre-recorded here.

