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

**Condition C3 — the 4 stamped-but-not-flagged Reference files (31 stamp targets, 27
flagged):** `README.md`, `deploy/README.md`, `packages/README.md`,
`examples/fremtpl2/README.md` — verified present at this tree, each `family: reference`.
Not flagged because none is under `_id_scope_roots()`'s four post-migration roots
(`scripts/audit-docs.py:1288-1294`: `ROOT` (=`docs/`), `.claude/roles`, `.claude/skills`,
`.claude/agents`) — a repo-root or `deploy`/`packages`/`examples` README is outside every
one, so check 30 never walks it, stamped placeholder keys and all.

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

## PRs

| # | Branch | Head | Tasks | State |
|---|---|---|---|---|
| 1 | `w37-8-t1-t2` | `c6964a2` | T1, T2 | draft, open |
