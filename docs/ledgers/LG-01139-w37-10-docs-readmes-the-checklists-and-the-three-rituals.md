---
id: LG-1139
family: ledger
title: W37-10 — docs/ READMEs, the checklists, and the three rituals
status: active
created: 2026-09-26
owner: executor
tree: 4ff075aba2b90fffebd857c5b05059f21a4959e6
phase: P2
work: WK-697
plans: [PL-1073]
corrected_by: []
relates: []
---

# LG-1139 — W37-10 — docs/ READMEs, the checklists, and the three rituals

Executed task by task from `PL-1073`. Commits are on branch `w37-10-docs`, cut from
`origin/main` at `20d922dd3ac40678ecd003787fbc27360a77c688`. No `slice:` id exists for
W37-10 yet (DP-4); the slice is cited in prose here, per that ruling.

## Tasks

| Task | Commit | Verified |
|---|---|---|
| 1 — `docs/README.md` as the map | `22ef73f5` | `audit-docs.py` EXIT=0; `adr/` grep empty; both check commands named |
| 2 — `docs/research/README.md` | `e41ecab0` | `doc-id.py check` EXIT=0; `audit-docs.py` EXIT=0; `docs/INDEX.md` regenerated in the same commit |
| 3 — retire the audit tree's `findings/README.md` | `73db1e3e` | `git ls-files docs/audit \| wc -l` = 1 (DP-1 option A); `audit-docs.py` EXIT=0; hand-off recorded below. **Note (D10, deputy, 2026-09-26 19:50:59 BST):** this task's DP-1 retirement surfaced a coupling in `tests/test_audit_docs_ids.py::test_id_scope_documents_excludes_the_w37_11_residue_ceiling_record` — its own positive control assumed a second file survived under the old audit tree. Routed to a separate tests-only PR outside every slice, written by `exec-ci-hotfix`, which merges before this slice's own PR is requested. `RL-1138` bars this executor from `tests/`; the fix is not this ledger's. *PR number pending — cite it here once it exists.* |
| 4 — both checklists: id, gate, family, register, path lines | `167980cd` | Both files' verify commands (no reference to the old audit tree's work/phases destinations, no "No new id family", `has an id` present) all as expected; `audit-docs.py` EXIT=0 |
| 5 — `phase-close.md` freeze-gate and generated-report lines | `4ff075ab` | Lines present, `audit-docs.py` EXIT=0. **Step 4's runtime proof is open** — see "Open items" below |
| 6 — `delivery-process.md` rituals (a)/(b) + core extract digest | `02d9a22a` | `fortnight`/`freeze` greps hit; no section renumbered (`^## ` heading list unchanged in count and order); check 27 green at the new digest |
| 7 — `CR.md` phase-report body rule | `7f45e426` | Line present; check 37 unaffected (91 shape-checked, 0 new failures) — the heading carries a placeholder marker so it is not required for `work`/`review` kind |
| 8 — the two roadmap proposals (below) | this file | Drafted, not applied |
| 9a — verify the five "landed" rows | this file, §Task 9a | All five confirmed landed by direct read |
| 9b — sweep, index, gate, this ledger | this file, §Task 9b | see below |
| 10 — D4's two acceptance feet | `6c74b83c` | Both `_pending_` feet replaced; header/table rows untouched; `audit-docs.py` EXIT=0 |
| 11 — `PL-1070`'s scope-table amendment | `1759b0b4` | Planner's text landed verbatim at the named anchor; all six SHAs verified ancestors of `refs/pull/795/head`; `audit-docs.py` EXIT=0 |
| 12 — the correction at `LG-1137:20` | `ea9bcde4` | Original line unchanged; both salvage refs and both range-diff successors re-verified; `audit-docs.py` EXIT=0 |
| 13 — the phase-1b register grammar rows | `b34a37cf` (#801) | Auditor's file, auditor instance's commit, not this ledger's own work. `#801` merged 2026-09-26 20:40:57 BST: all 120 register rows parse |
| S-6 — `register.md`'s 8 raw-`\|` rows | `b34a37cf` (#801) | Found by the executor at Task 5 step 4 (`doc-index.py --phase` raised a coverage-mismatch `ValueError`). Lead ruling 2026-09-26 19:17 BST: fix landed in the auditor instance's own commit inside `#801`, `docs/findings/register.md` being the auditor's file. §1.4 scope row S-6 amended to cite `b34a37cf` and `#801`. **Discharged:** `python3 scripts/doc-index.py --phase P1b; echo EXIT=$?` now prints `EXIT=0` and a full report at this branch's rebased head — Task 5 step 4 and Acceptance Standard item 11 are both satisfied |

## Task 8 — the two roadmap proposals (drafted here, applied by the lead)

No edit to `docs/roadmap.md` is made by the executor — `.claude/roles/planner.md`: a roadmap
edit is a proposal applied by the lead or decision-maker.

### Task 8a — the per-phase freeze-gate dates (proposal)

`docs/roadmap.md`'s `## P2 — Rating Engine` milestone section currently reads `gates: ~`.
Proposed, in the section's existing field shape (`docs/_templates/PHASE.md`):

```
gates: plan freeze 2026-09-19 · code freeze 2026-10-03 · docs freeze 2026-10-10
```

**Basis, stated so the lead can correct it rather than have to reverse-engineer it.** Phase
P2 opened 2026-08-14 and is well past its plan stage — Stage 3 of WK-697 alone (W37-7 through
W37-11) is mid-execution — so a **plan freeze in the past** (2026-09-19, the date review 13
closed the W37-6 checkpoint) records what already happened rather than inventing a future
date for a plan already frozen in substance. **Code** and **docs** freeze are proposed as
one and two weeks out from this slice's own filing, giving W37-8, W37-9 and W37-11 room to
land; both are the executor's estimate, not a measurement, and the lead is the one with
visibility into the actual remaining Stage 3 and W37-11 work. Hand to the lead with the
`phase-close.md` freeze-gate line quoted (this slice's Task 5 commit `4ff075ab`), so the
declaration and its check arrive together, per the plan's step 2.

### Task 8b — the `SL-` rows for WK-697's eleven slices (proposal)

**Step 1, re-measured at this tree:** `grep -c 'SL-[0-9]' docs/roadmap.md` = **0**;
`grep -rn '^slice:' docs/plans/ | wc -l` = **0**. Both unmoved since the plan's own
measurement at `d63f765`/`4ed1f88`; the lead reconciles if either has moved by apply time.

**Step 2, the eleven ids.** This ledger itself took `LG-1139` from `python3 scripts/doc-id.py
next` at this tree. The eleven `SL-` ids are proposed as the **next** eleven after it,
**base 1140, range 1140–1150** — re-derive with `python3 scripts/doc-id.py next` at apply
time rather than trusting this base, because another slice may allocate against the same
sequence first (the plan's own Risk 4).

**Step 3, status derived from the record, not recalled.** Read from the WK-697 roadmap row's
own Progress paragraph (`docs/roadmap.md:754` block) and the closure records it cites — not
from memory:

**Fenced, because none of these ids is allocated yet** — a proposal id is a specimen of
the form, not a citation, and check 32 would otherwise try (and fail) to resolve it in
`docs/INDEX.md`:

```text
Proposed id | Slice                                                  | Status | Basis
SL-1140     | W37-1 — the standard and templates                    | closed | Progress paragraph: "S1 complete"
SL-1141     | W37-2 — doc-id.py                                      | closed | Progress paragraph: "S1 complete"
SL-1142     | W37-3 — doc-index.py                                   | closed | Progress paragraph: "S1 complete"
SL-1143     | W37-4 — audit-docs.py checks 30-39                     | closed | Progress paragraph: "S1 complete"
SL-1144     | W37-5 — migrate, built and proven on a fixture corpus  | closed | "W37-5 merged"; CR-1004, CR-1005 (W37-5b/5c)
SL-1145     | W37-6 — the supervised migration run                  | closed | "the real migration — merged to main 2026-09-17", CR-1065 (checkpoint 3 close)
SL-1146     | W37-7 — the remaining creating and reading instruments| closed | Squash-merged as #795 (4ed1f88ee89deeddca04565cc1f07cdbaf02dba4); this slice's own Task 11 lands its four-scope-row correction against it
SL-1147     | W37-8 — the charters                                   | draft  | No branch or PR found (git ls-remote origin 'refs/heads/*' has none matching); the deputy's D2 (to-lead.md 17:06:12 BST) "released to start now under the ruled order (after W37-10)" — queued, not begun
SL-1148     | W37-9 — CLAUDE.md and the public face                  | draft  | Same basis as W37-8: D3, released to start, no branch found
SL-1149     | W37-10 — docs/ READMEs, the checklists, the three rituals | active | This slice, in progress at the time of this ledger
SL-1150     | W37-11 — the residue, the census and the close        | active | Roadmap prose names live, ongoing items owned by it (finding ids in the F1xx range, the check-35 shape, the pinned-base read, the docstring mismatch) and its first item (#757) already landed
```

**Step 4, the hand-off.** Once these rows exist on `main`, adding `slice:` fields to the
Stage 3 leaf plans is **not this slice's** — a frozen plan is not edited to acquire a field.
That is a separate, later act for whoever the lead assigns it to.

## Task 9a — verify the rows recorded "landed"

Each of §1.2's five verify-only rows, read to the clause carrying the obligation, not to
its last-touching commit (R-7):

| Row | Verdict |
|---|---|
| `closures/README.md`, `findings/README.md`, `rulings/README.md`, `ledgers/README.md` (new) | **Confirmed landed.** All four present, headed with a valid `family: reference` header, each carrying substantive content in its own voice, not a stub |
| `plans/README.md`'s README limb | **Confirmed landed.** `docs/plans/README.md`'s naming/kinds content is a pointer to `document-ids.md` (§"Naming, and the kinds of plan"); the nine writing conventions survive as "Writing one so it passes the audit" (4) and "The conventions the audit cannot check" (5) |
| `docs/findings/README.md` — the old audit README dissolved | **Confirmed landed.** Carries a `was:` field naming the old audit tree's own top-level README, and its own substantive content, split with `closures/README.md` |
| `closures/INDEX.md#closure-recordsmd` / `#plan-reviewsmd` preambles → `closures/README.md` | **Confirmed landed.** `closures/README.md`'s `## Conventions` block carries the register-currency, checklist-versioning, write-once-evidence, phase-tag and ISO-date rules these preambles held |

No row required a verdict other than "delivered" — none needed reassignment.

## Task 9b — the sweep, the index, and the gate

**Step 1 — the restricted sweep**, re-run at this tree (`4ff075ab` plus this ledger):

```bash
python3 scripts/audit-docs.py 2>&1 | grep "legacy audit path" | grep -c "form survives"
```

**210** hits, across **71** distinct files (`grep -oP '^\s*- check 36: \K[^:]+' | sort -u | wc -l`
over the same filtered output) — down from the plan's own **220 / 74** measurement at
`4ed1f88` (§1.4 note 3's predicate). The reduction is this slice's own: the two checklists'
four-plus-four hits (Task 4) and the retired findings README's three hits (Task 3, removed
with the file) are gone; `delivery-process.md`'s edits (Task 6) added no new hit — the
ritual text names no legacy form. **The residual 210/71 is W37-11's**, per the plan's own
disposition: overwhelmingly frozen `CR-`, `FD-`, `RL-`, `LG-` and filed `PL-` write-once
evidence, plus a small remainder under `scripts/` and `.claude/` this slice has no authority
to edit (DP-1).

**Step 2 — regenerate the index.** `python3 scripts/doc-index.py` then
`python3 scripts/doc-index.py --check` — `OK (byte-stable)`, EXIT=0. Committed alongside
this file.

**Step 3 — both gate halves.** See the table below; run at this branch's head before each
push, per the executor charter and `dev-commands`' wrapped gate body.

| Gate | Command | Result |
|---|---|---|
| Docs audit | `python3 scripts/audit-docs.py; echo EXIT=$?` | `EXIT=0` (per-commit; see each task's own verify above) |
| Id check | `python3 scripts/doc-id.py check; echo EXIT=$?` | `EXIT=0` |
| Index | `python3 scripts/doc-index.py --check` then `git status --porcelain docs/INDEX.md` | `EXIT=0`; empty once this commit lands |
| Full local gate (7 stages) | `dev-commands`' gate body (ruff, mypy, lint-imports, audit-docs, req-coverage, contracts, pytest) | run once per PR before push, table pasted in the PR body per the executor's report to the lead |
| CI | green by head SHA (`gh run list --branch <branch>`) | reported per PR, not here |

**Step 4 — hand-offs and open items, named rather than left silent:**

1. **`.claude/roles/auditor.md:33,35`** name the retired findings README's path (the old
   audit tree's own, now deleted). That charter is W37-8's to rewrite (`RL-1138` DP-2
   condition 3). The interim resolution is the `docs/REDIRECTS.csv` row added in Task 3's
   commit (`73db1e3e`).
2. **The 210/71 legacy-form residual** (Task 9b step 1) is W37-11's, which owns the fuller
   §7(i) walk (`CR-1065:339-341`).
3. **§1.4 row S-5** — `RL-1046` §B's check-30 class (the §5.1/§5.3/§5.4 content rows) —
   is a **proposed verdict: reassigned, to W37-11**, per the plan's own §1.4 measurement.
   This ledger does not decide it; the lead rules it.
4. **A gate-blocking defect found doing Task 5, reported to the lead 2026-09-26, ruled on
   2026-09-26 19:17 BST as §1.4 row S-6 (above):** `python3 scripts/doc-index.py --phase
   P1b` raises `ValueError: findings/register.md: parsed 112 of 120 data row(s) —
   coverage mismatch (RL-982 acceptance item 2)`, reproducing identically and unrelated to
   any edit in this slice, at `origin/main` (`20d922dd`). Root cause: 8 register rows
   contain a literal, unescaped `|` and so fail `_parse_register`'s five-cell shape check
   silently — a `\|` does not fix it, since `_parse_register`
   (`scripts/doc-index.py:1061`) splits on an escaped pipe identically to a bare one; the
   fix is an HTML entity or a rewording. **Ruled: the auditor instance made the fix in
   its own commit inside `#801`** — `docs/findings/register.md` is the auditor's file,
   not this ledger's executor's. **Discharged:** `#801` merged as `b34a37cf` (2026-09-26
   20:40:57 BST); at this branch's rebased head, `python3 scripts/doc-index.py --phase
   P1b; echo EXIT=$?` prints `EXIT=0` and the full report reproduced below. Acceptance
   Standard item 11 and Task 5 step 4's runtime proof are both satisfied.

   ```text
   $ python3 scripts/doc-index.py --phase P1b; echo EXIT=$?
   # Phase report — P1b

   1. Works closed and retired: 4 closed (WK-661, WK-664, WK-665, WK-692), 1 retired (WK-662)
   2. Slices planned versus delivered: 0 planned, 0 delivered
   3. Plans superseded per Work:
      - WK-661: 0
      - WK-662: 0
      - WK-664: 0
      - WK-665: 0
      - WK-692: 0
   4. Rulings per Work:
      - WK-661: 0
      - WK-662: 0
      - WK-664: 0
      - WK-665: 0
      - WK-692: 0
   5. Findings opened versus discharged, from the register: 0 opened in P1b, 0 discharged,
      0 unowned-decay in P1b, plus 0 unowned-decay carried in from an earlier phase
   6. Documents with no inbound citation outside INDEX.md: —
   7. Days from a plan reaching active to its closure record being filed:
      - (none)
   EXIT=0
   ```
5. **A second gate-blocking defect found running the full local gate, reported to the
   lead 2026-09-26, escalated rather than fixed** (`RL-1138` bars this executor from any
   file under `tests/`): `tests/test_audit_docs_ids.py::test_id_scope_documents_excludes_
   the_w37_11_residue_ceiling_record`'s own positive control — a check, under the widened
   scope roots, that some path in the resolved set still starts with the old audit tree's
   own prefix:

   ```text
   any(r.startswith("docs/audit/") for r in rels)
   ```

   — depended on the old audit tree holding a file *other than* the W37-11 record. Task 3's
   ruled deletion of the retired findings README (DP-1/DP-2) leaves exactly one file under
   the old audit tree, and it is the excluded one, so the positive control now has nothing
   left to be true of and fails. **Routed (D10, deputy, 2026-09-26 19:50:59 BST):** a
   separate tests-only PR outside every slice, written by `exec-ci-hotfix`, fixes the
   positive control; it merges before this slice's own PR is requested, and this branch
   rebases onto the new `main` afterward. See Task 3's row above for the citation.

## PRs

To be filled once the PR is opened (`gh pr create`, `gh api -X PATCH` for the body,
`gh run list --branch` for CI by SHA), per the executor charter.
