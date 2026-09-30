---
id: RL-9841
family: ruling
title: PREPARED, NOT RULED — RL-881's finding 1 is stale in two places; 06 §4.2 restates the rating_version floor and structural_diff has an owner
status: draft                  # NOT a permitted RL status (§1.2: active → superseded | retired); kept by the maintainer's ruling, by delegation — see "Status of this record"
created: 2026-09-30
owner: decision-maker
tree: 880feb499eddb9e854c525770e95fb19373a2311
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-881
relates: [RL-881, RL-885, RL-1184, RL-1263, RL-1264, PL-1267]
---

# RL-9841 — PREPARED, NOT RULED: RL-881's finding 1 is stale in two places

## Status of this record — read this first

**Nothing here is ruled.** This is a *prepared* correction, written at effort `medium` under
the maintainer's decision by delegation of 2026-09-30 00:42:01 BST (`to-lead.md`). Under the
maintainer's later ruling, also by delegation, it keeps `status: draft`, and it is never
marked ready or minted before its effort-high pass. `status: draft` is not in RL's §1.2
subset, so check 33 refuses it on purpose. RL-881's new `corrected_by:` entry, in the same
commit, belongs to this prepared change. It is not in force until the ruling pass mints this
record. Working id 9841 was checked free on every `origin/*` and local branch and in
`~/gi-pricing-plan.local/channel/`.

## Verified first, at 880feb499eddb9e854c525770e95fb19373a2311

**Where the stale text is.** It is in RL-881's *Findings reported, not ruled*, finding 1
(`docs/rulings/RL-00881-…md:153-160`). RL-881 read its sources at `9891be1f`
(2026-08-29 17:16:38 +01:00). Two of that finding's statements no longer hold:

1. **`:154-158`**: *"`06` §4.2's restatement (`:290-295`) names the floor for `model`,
   `validation_rule`, `custom_objective` and `peril_structure`, and omits `rating_version`,
   `custom_metric` and `deployment` — three of the six keys `EVIDENCE_FLOOR` actually holds."*
   At this tree, `docs/specs/06-governance.md:344-352` restates all six keys:
   - `rating_version` — `structural_diff`, `regression_run`, `dislocation_run`;
   - `custom_metric` — `metric_certificate`;
   - `deployment` — `rating_version_approval`, `uat_deployment`.

   These match `EVIDENCE_FLOOR`
   (`packages/model-schema/src/model_schema/approvals.py:101-108`). The correction is dated
   in place (`06-governance.md:355-358`: *"Corrected 2026-08-29, WK-671 Slice 2 … Ruled in
   … RL-885"*). It landed at `2891d426` (2026-08-29 18:12:09 +01:00, #398), about an hour
   after RL-881's tree. The statement was true when written and has been false ever since.
2. **`:153`**: *"`structural_diff` has no owner named anywhere."* `RL-1184` E4 (its record, line 114)
   names **WK-673**, and `06` FR-364's 2026-09-28 amendment says the same. `PL-1267` §premises
   and its FR table (`:247-251`, `:284`) apply it.

**Who identified it.** `PL-1267` premise e′ (*"**no longer holds**. The stale clause in
`RL-881` is the decision-maker's to supersede"*). `RL-1264` (`:132`, `:194-197`) proposes
this role file it. RL-881 still reads `superseded_by: ~` and `corrected_by: []` (`:9-10`).

**What was checked and still holds — not corrected.**
- **RL-881's table row, the wiring "Lands with the last enabler | WK-673" (`:35`).** WK-672
  Slice 3 has merged (`6a8b8e70`, #886). `regression_run` is verified by
  `_regression_run_gate` (`backend/src/app/platform/rating_versions.py:619`, called at
  `:289`). The two kinds still unverified, `structural_diff` and `dislocation_run`, are both
  WK-673's. So WK-673 is still the last enabler, and `PL-1267` puts the wiring in its
  Slice 6 (DP-4).
- **`RL-1263` (the parallel start) and `delivery-process.md` §8.** Neither touches RL-881.
  `RL-1263` names `approvals.py`'s `EVIDENCE_FLOOR`/`DEFAULT_POLICY` as a shared file that
  serialises WK-674, WK-673 and WK-1250. It lifts bare sequencing between Works. RL-881
  assigns the wiring to WK-673 by artifact ownership, not by Work order, so lifting the order
  does not change who wires it. RL-881 also says nothing about sequencing. No match for
  `§8`, `sequen` or `parallel` in its body: its one hit is a plan filename in its Sources
  list, `:189`. `delivery-process.md` does not cite RL-881 (`git grep -n "881"`, 0 hits).
- **RL-881's findings 2 and 3 are outside this record's scope, and both have moved.**
  - Finding 2: `DEFAULT_POLICY` still has no `deployment` entry. That is WK-674's, and
    the prepared ruling on OQ-1234 (working id 9901, draft #935) touches it.
  - Finding 3: `GOLDEN_QUOTE_MISMATCH` is now registered (`backend/src/app/errors.py:353`)
    and raised (`rating_versions.py:597`). Finding 3 is therefore also stale.

  The ruling pass decides whether to take finding 3 into this correction (see option (c)).

*Refreshed 2026-09-30 onto main `0bc69b5b2c3c16ec8391387cdfab19734ff85d2b`. Every
deciding-evidence claim was re-read there and holds at the same lines:
- `06-governance.md:344-352` (and its dated fix at `:355-358`);
- `approvals.py:101-108`;
- `RL-1184` E4 (`:114`);
- `PL-1267` e′;
- `RL-1264` `:132`;
- `_regression_run_gate` (`rating_versions.py:289`, `:619`);
- `GOLDEN_QUOTE_MISMATCH` (`errors.py:353`, `rating_versions.py:597`).

`delivery-process.md` still does not cite 881 (rc 1). No record on main `corrects:` or
supersedes RL-881 (`git grep '^corrects: RL-881'` rc 1), and RL-881 on main still reads
`corrected_by: []`.*

## Options

| | Option | For | Against |
|---|---|---|---|
| (a) | **Correct finding 1 only, the `06` §4.2 sentence** (the clause `RL-1264` names) | Narrowest; exactly what `RL-1264` proposes | Leaves the next sentence of the same paragraph (`structural_diff` unowned) stale; a reader of the paragraph still meets a false statement |
| (b) | **Correct both stale statements of finding 1** (`:153`, `:154-158`) | One record makes the finding true again end to end; both facts are verified at this tree | Slightly wider than `RL-1264`'s proposal |
| (c) | **(b) plus finding 3** (`GOLDEN_QUOTE_MISMATCH` now registered) | Clears every statement in RL-881 known false today | Finding 3 was not raised by `PL-1267` or `RL-1264`, and correcting it here widens the change past what the lead asked for |
| (d) | **Supersede RL-881** | — | Wrong instrument: the four-limb disposition and the three refusal reasons still stand; `superseded` would retire a live ruling. `corrects:` is the frozen-family form for a false statement (`document-ids.md` §1.5) |

## Provisional recommendation — (b), not ruled

Correct RL-881's finding 1 in both of its stale statements with `corrects: RL-881`. RL-881
gains `corrected_by: [RL-<minted id>]`, which is the one header edit §1.5 permits on a frozen
record and which check 34 cross-checks. Report finding 3's staleness to the lead so it can
choose (c).

**The one piece of evidence that decides it:** `06-governance.md:344-352` at this tree
restates all six `EVIDENCE_FLOOR` keys, `rating_version` included. The same paragraph's
`structural_diff` sentence is contradicted by `RL-1184` E4. Correcting one without the other
leaves the paragraph half false.

## Ruled

**Nothing.** Check 37 requires this heading of the ruling family. It records no decision.

## What it obliges

**Nothing yet.** At the ruling pass, (b) would record the two corrections above and require
no other edit. RL-881's body stays as filed. Its disposition, reasons and acceptance test are
unaffected, and no spec, plan or code change follows.

## Acceptance — the violation that must become detectable

*Provisional.* RL-881's header lists this record in `corrected_by:`, and this record's
`corrects:` names RL-881. `scripts/audit-docs.py` check 34 then fails if either side is
removed. A reader of RL-881's finding 1 reaches the correction through the header.
