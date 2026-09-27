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

Landed in `c6964a2` (fix commit), on branch `w37-8-t1-t2`. Fixes check 30
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

**Gate, at `c6964a2` (both halves):**

| stage | result |
|---|---|
| ruff | pass |
| mypy | pass |
| import_linter | pass |
| audit_docs | pass |
| req_coverage | pass |
| contracts | pass |
| pytest | pass — 3456 passed, 3 skipped, 1 xfailed (baseline 3457 collected/3 skipped + 3 new tests = 3460 collected) |
| frontend install | pass |
| frontend generate:api | pass |
| frontend lint | pass |
| frontend type-check | pass |
| frontend test | pass — 97 files / 602 tests |
| frontend build | pass |

`GATE: pass — 7 of 7 stages passed` (Python half). Logs and rc files at
`~/gi-pricing-plan.local/handover/gate-c6964a2/{python,frontend}/` (local, not repo —
`handover-files-are-local-not-repo`).

`python3 scripts/audit-docs.py | grep -c 'check 30: \.claude/agents/'` still prints `7` at
this tree (T3/T4 have not merged headers yet); `grep -n '"tools"\|"model"\|"description"'
scripts/_docid.py` has no hit inside `_KNOWN_KEYS`.

**Gate-table note (supersedes the 01:16:48 diagnosis below):** docs run 36281191974 at
414a9335: `doc_id_verify` exited 3. The 01:16:48 BST diagnosis — that check 30's headerless
`.claude/` lookup was the regression — was **withdrawn**: a direct comparison of
`python3 scripts/audit-docs.py`'s output between `main` and 414a9335, run in this
worktree, was byte-identical, and `_docverify`'s own snapshot metadata showed
`doc_id_verify`'s (h1) row shells the `--ref` tree's *own* frozen copy of
`scripts/audit-docs.py`, never this branch's — so no check-30 edit on this branch could
ever have moved that row. That fix — a local commit on top of `414a9335` — was reset away
(`git reset --hard 414a93353bd5252820fee1c3b4b2ae3b8fd1a5c1`) before pushing; its SHA is
not an ancestor of this ledger's own tree and is not cited by number for that reason.

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

**The fix (commit below):** one module-level constant in `scripts/doc-id.py`,
`_HARNESS_ONLY_TEMPLATE_KEYS`, naming the same four keys; `_stamp_header` skips them
(next to the existing `slice`/`deliverable`/`lands_in`/`trigger` skip); the new test
`test_reference_stamp_emits_none_of_the_four_harness_only_keys` in
`tests/test_doc_id_migrate.py` asserts none of the four are ever emitted, read against the
real `docs/_templates/REFERENCE.md`.

**Broken-input proof:** removed only the new `elif key in _HARNESS_ONLY_TEMPLATE_KEYS:
continue` skip clause (the constant declaration untouched) — the new test failed, all four
keys present in the rendered stamp. Restored the clause — the new test, and the full
`tests/test_doc_id_migrate.py` (303 tests) and `tests/test_audit_docs_ids.py -k check_30`
(11 tests), all passed.

### Addendum to Task 1 — Acceptance Standard item 8, discharged

**Not recorded when T1 first landed (#806) — discharged here, appended rather than
inserted into Task 1's own entry above.** `PL-1071` §5 item 8 requires the four
`FD-1066`…`FD-1069` disclosures to be re-read **in full** after `CR-1065` merged, and the
ledger to record either "no W37-8 routing found" or the routing taken.

```text
$ ls docs/findings/ | grep -E '01066|01067|01068|01069'
FD-01066-pl960-909-idempotence-second-migrate-run-zero-diff-not-proven.md
FD-01067-check-35-two-sub-clauses-fire-on-one-non-markdown-file-after-f87s-widening.md
FD-01068-standing-ci-verify-reads-the-w37-11-record-from-a-pinned-base-forever.md
FD-01069-h1-residue-by-file-and-tracked-files-docstrings-disagree-on-population.md
$ grep -n '\.claude/roles\|\.claude/agents' docs/findings/FD-01066*.md docs/findings/FD-01067*.md docs/findings/FD-01068*.md docs/findings/FD-01069*.md
(no output)
```

All four read in full, not by title alone (`PL-1071` §4.1's own caution against exactly
that). **No W37-8 routing found.** `FD-1066` is `PL-960:909`'s idempotence gap
(a second `migrate` run's zero-diff not proven) — instrument-level, names no charter or
agent file. `FD-1067` is check 35's two-sub-clause double-fire on one non-Markdown file
after F87's widening — a check-scope defect, not a charter-content one. `FD-1068` is the
standing CI `doc_id_verify` step reading `w37-11-record.md` from a pinned base tree
forever — a CI-instrument gap, W37-11's ceiling record, not this slice's files. `FD-1069`
is the H1 residue count disagreeing between a by-file breakdown and the tracked-files
docstring's stated population — a reconciliation gap in the residue accounting itself,
again naming no `.claude/roles/` or `.claude/agents/` file. Acceptance Standard item 8 is
discharged.

## PRs

| # | Branch | Head | Tasks | State |
|---|---|---|---|---|
| 1 | `w37-8-t1-t2` | `c6964a2` | T1, T2 | **merged as PR #806** — this row's "draft, open" was the state when the row was first written; corrected here rather than edited in place, per `gh api repos/yes-404/gi-pricing-plan/pulls/806` (`merged: true`) |
| 2 | `w37-8-charters` | `d5ec4aad` | T3, T4 | draft, open, PR #807 — CI confirmed `CLEAN` (docs + history-policy both `success`; python/frontend correctly did not fire) |
| 3 | `w37-8-t5-readme` | `f41ae954` | T5 | draft, open, PR #808 — both gate halves green (7/7 python, 6/6 frontend) |
| 4 | `w37-8-t6-reporter-watcher` | `4ae3c499` | T6 | in progress |

### Task 6 — the ownership-matrix invocation, re-run and recorded

**The generated matrix is unaffected by charter prose, and that is by design, not a
miss.** Read `scripts/doc-index.py:958-969` (`ownership_matrix()`): the function's own
docstring states *"`reporter` and `watcher` are named in no cell (verified: neither
string appears anywhere in `_OWNERSHIP_TABLE`'s second column), so both come out as `()`
— the two deliberately empty rows, produced by derivation rather than special-cased."*
The matrix is built from the `_OWNERSHIP_TABLE` constant (`document-ids.md` §1.6's table,
transcribed into the script), never from a live read of `reporter.md`/`watcher.md`'s own
text. So Acceptance Standard item 2's "declared empty, not blank" is a property this
matrix has held **since before T6's edit** — T6's own acceptance criterion is item 6
(the charters' own sentence), not a change in this table's shape.

```text
$ python3 scripts/doc-index.py; echo EXIT=$?
EXIT=0
$ /usr/bin/git status --porcelain docs/INDEX.md
(empty — byte-stable)
$ sed -n '/## Ownership matrix/,/^$/p' docs/INDEX.md
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

Acceptance item 6, the charter-side check that actually changed with this task's commit:

```text
$ grep -n "owns no governed document" .claude/roles/reporter.md .claude/roles/watcher.md; echo GREP_EXIT=$?
.claude/roles/reporter.md:15:- **The reporter owns no governed document** ...
.claude/roles/watcher.md:13:- **The watcher owns no governed document** ...
GREP_EXIT=0
```
