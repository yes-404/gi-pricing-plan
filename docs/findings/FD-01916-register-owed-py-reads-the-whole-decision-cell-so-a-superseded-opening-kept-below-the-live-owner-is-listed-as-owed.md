---
id: FD-1916
family: finding
title: register-owed.py reads the whole Decision cell, so a superseded opening kept below the live owner is listed as owed
status: closed
created: 2026-10-25   # drafted 2026-10-25 under working id 8230; minted 2026-10-25 as FD-1916
owner: auditor
tree: ff976406f1bf133cfe040d2c44d383011503988a
corrected_by: []
relates: [CR-1907, WK-1178, CR-1247, FD-1165, FD-1166, SL-2066, LG-2067, PL-2065]
---

# FD-1916 — register-owed.py reads the whole Decision cell

*(Filed under working id 8230, reserved by the lead. Authority: the maintainer's entry "2026-10-25 11:47:10 GMT" (to-lead.md), item T1 (1): "keep, owner WK-1178, filed as an `FD-` with a broken-input proof"; the lead may re-point it to WK-1170 by a dated line if that Work is open at the review tree. At `ff976406` WK-1170 left Phase 2 on 2026-10-08 (`docs/roadmap.md`, the WK-1169 and WK-1170 move line), so the owner stays WK-1178.)*

## Finding

**Severity: LOW (auditor's proposal, the lead gives the verdict).** The defect makes the owed list too long, never too short. A reader sees extra rows and each one is visibly a resolved or owned row. No price, no hash and no stored artifact is affected. It costs review time at each §14 review, and it hides the real owed rows among false ones.

`scripts/register-owed.py` decides that a row "names the §14 review" by searching the **whole** Decision cell. The register's convention is that an amended row keeps its superseded opening in the same cell, below the live decision, and says so with "This supersedes the opening kept below" (or "…the owner and event of the opening kept below"). The generator cannot tell the live text from the kept opening. A row whose live owner and event are settled still matches if its kept opening says "the next `CLAUDE.md` §14 plan review".

`CR-1247` Proposal 9 (`docs/closures/CR-01247-…`, the "Proposal 9" section) named this for 20 rows. At `ff976406` it is **21 of 33** owed rows.

## Mechanism

- `scripts/register-owed.py:102` — `_REVIEW_MARKER = re.compile(r"§14")`.
- `scripts/register-owed.py:145-146` — `_matches_review(row)` returns `bool(_REVIEW_MARKER.search(row.fields[4]))`. `fields[4]` is the whole Decision cell.
- `scripts/register-owed.py:139-142` — `_matches_work_id` has the same shape for a Work id: it searches `fields[2]` and the whole `fields[4]`. A row whose live owner is another Work, and whose kept opening names this one, is listed under this one.
- `scripts/register-owed.py:125-130` — `_is_resolved` is **prefix**-based (`register_lint._opens_with_status`), so it already reads only the start of the cell. The selection predicates are the only two that read all of it.

## Evidence

Counted at `ff976406`, in my own worktree, with `python3 scripts/register-owed.py review` (via the gate-2 flock) and a read-only probe over `register_lint.parse_register` and `register-owed.py`'s own `select_matches`. The probe is `~/gi-pricing-plan.local/scratch/aud-review-2026-10-25/probe.py`. Its predicate: an owed row (not `excluded_resolved`) whose Decision cell matches `supersedes[^.]{0,80}opening kept below` (case-insensitive) and whose text **before** that match contains no `§14`.

- `register-owed.py review` prints **33 owed rows, 6 excluded** (log `owed-review-base.log`, `head=ff976406…`, `rc=0`).
- The probe: owed 33; 21 carry the marker; **21 of 21 contain `§14` only after the marker** (log `probe-base.log`).
- The 21 rows: FR-240 (F-W9-3), F27, F28, F29, F31, F33, F48, F101, F114, and twelve unlabelled rows (the C2 PreToolUse row, the `register-owed.py WK-671` row, the reporter Mechanism row, the "never end your turn" row, the RL-909 decay row, the five-fixtures row, the check-37 row, the RFC-937 §1.5 row, the ruling-heading census row, the `PL-` migration row, the shared-checkout row, the PL-1070 freeze row).
- `CR-1247` Proposal 9 counted 20 rows at `1c8762d9` and listed 20 ids; the two sets differ in membership (it names F63, F74, F75, F86, F89, F90, F93, F94, F96, F97 and F113, which this probe does not list, and this probe lists twelve unlabelled rows it does not name), and I did not trace why each row differs (the trees differ). The mechanism is the one it named.

## Disposition

### Remedy (proposed, not built here)

Cut the Decision cell at the first match of the marker before either predicate searches it. One helper in `register-owed.py`: `_live_text(decision)` returns `decision[:m.start()]` when `_SUPERSEDED_OPENING` matches, else the whole cell. `_matches_review` and `_matches_work_id` search `_live_text(fields[4])`. `_is_resolved` keeps reading the whole cell's prefix.

The marker is the register's own phrase; keep one regex, `supersedes[^.]{0,80}opening kept below`, and have `register-lint.py` own it if lint ever needs it (one definition, FD-1165's reason). Two limits to state in the fix: a row that has no marker is read whole, as now; a live text that names §14 **before** the marker still matches, correctly.

### Broken-input proof the fix must carry

In `tests/test_register_owed.py`, a register fixture with three rows:

1. live owner WK-A, no §14, a kept opening that says "decays to the next §14 plan review" — must **not** match `review`, and must **not** match `WK-B` when the opening names WK-B;
2. live text naming §14 before the marker — must match (control: the fix does not blind the predicate);
3. no marker, §14 anywhere — must match (control).

Red first: on `ff976406` row 1 matches `review`. Then run the real register: the owed count under `review` must drop by the 21 rows above (to 12, before any other register change), each of the 21 shown to carry its live owner before the marker.

### Owner and event

Owner **WK-1178** (the maintainer, "2026-10-25 11:47:10 GMT", T1 (1)). Event that discharges it: the fix's merge with the red in row 1 shown on the base tree by its cause, and `register-owed.py review` re-run on the merged tree with the count quoted.

***Resolved 2026-11-07*** — closed in place 2026-11-07 by the auditor's closing act (the audit of 2026-11-05, adopted by the lead in from-lead "2026-11-05 17:08:05 GMT"; the slice minted 2026-11-07), as the closing act of the audit of SL-2066 (WK-1178, LG-2067, PL-2065; this PR; its number, squash commit and merge date are written at the merge's date-of-record), on the lead's brief, the maintainer's GO "2026-11-05 09:58:58 GMT" and the acceptance of the plans "2026-11-05 10:36:35 GMT" (T folded onto the FD-1484 branch and gate) (`to-lead.md`, a local channel file). Delivered remedy: `scripts/register-owed.py` gains `_SUPERSEDED_OPENING` (once) and `_live_text`, which cuts the Decision cell at the register's "supersedes … opening kept below" marker; `_matches_review` and `_matches_work_id` search the live text (the work-item cell unchanged), a row with no marker is read whole, and a live text naming `§14` before the marker still matches; `_is_resolved` and `register-lint.py` are untouched by this slice. Red first, by cause, in LG-2067 at base `c8d85227` (re-run by the auditor): T1 failed because row 1 matched `review`, T2 because row 1 matched `WK-B`; T3 and T4 are green controls at base and head. The real register, `python3 scripts/register-owed.py review`, auditor-run: base `c8d85227` 31 owed, 11 excluded; slice tree `5748acc7` 11 owed, 1 excluded; the 20 rows that left each open "deferred with an owner" above the marker, none names `§14` before it (the essay's 21 of 33 to 12 were at `ff976406`; the numbers had moved). Re-run after this closing act, `python3 scripts/register-owed.py review` through the gate-2 flock on the audit commit's tree (`scratch/exec-mint8343/register-owed-after.log`, `rc=0`): **14 owed, 1 excluded**, the same as the gated tree before the closing act; this row is among the 14, because the FD-1842 form appends the resolution at the end of the Decision cell and `_is_resolved` reads the cell's prefix (the precedent the audit measured), and the 14 are the ruled 11 plus the three rows LG-2070 names under (c). Gate evidence: the full code gate, both halves, SOLO, at `1208ba28` (tree `8f6dab4f`), END 2026-11-06 11:45:10 GMT: the pytest failures are 15, all in the eight docs-audit files and named in LG-2070 (item 31); ruff rc 0, import-linter rc 0, req-coverage rc 0, generate-contracts rc 0, frontend 138 files / 919 tests passed, build rc 0, demo `wf-699` PASS in 1728 s. Its one `mypy` error line (rc 1, two diagnostics at `tests/test_audit_docs_ids.py:2451`) is fixed at `723e5fca`, mypy rc 0 over 255 files.
