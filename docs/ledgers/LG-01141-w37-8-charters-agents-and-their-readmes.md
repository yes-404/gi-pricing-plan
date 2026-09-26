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

Folded into the same commit/PR as Task 1's ledger entry, per the lead's mechanics: "T1 then
T2 first, the code PR". Details recorded in this ledger's PR-1 row and in the PR body's
broken-input proof.

## PRs

| # | Branch | Head | Tasks | State |
|---|---|---|---|---|
| 1 | `w37-8-t1-t2` | _pending — recorded after push_ | T1, T2 | draft, open |
