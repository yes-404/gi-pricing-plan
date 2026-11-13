---
id: FD-8434
family: finding
title: CR-2110 G3 read "Rows with no resolution: none" at T while 24 open rows had none; the join never tested the register's owner cell against roadmap status
status: active
created: 2026-11-13
owner: auditor
tree: 2ba0d0d53142
corrected_by: []
relates: [CR-2110, WK-2114]
---

# FD-8434 — The G3 join let 24 open rows through

*Working id FD-8434, allocated by lead 34 (`from-lead` 2026-11-13); unminted on this branch. Drafted by the auditor (aud-b35, `scratch/aud-b35/stage3-fd-draft.md`, sha256 prefix `8e6741f62e29`), re-verified by aud-b35v at tree `2ba0d0d53142`, ruled by the maintainer, `to-lead` "2026-11-13 19:56:23 GMT" (G3-JOIN FD, working id 8434).*

## Finding

`CR-2110` G3 read "Rows with no resolution: none" at T (`fcfd7746c6e9`) while 24 open register rows had no resolution (the register lines at `2ba0d0d53142` are L47 L48 L49 L50 L51 L52 L53 L64 L83 L84 L88 L89 L90 L96 L98 L109 L111 L112 L115 L122 L218 L295 L323 L350). The set came from `python3 scripts/register-owed.py 2` (297 owed) plus Table C (8). G3 (c) and (d) then classed each row from the closure draft's own Resolution cell, and "carried, named owner" was counted by residual, with the owner read as the `CR-2103` Appendix A target. Nothing tested the register row's own owner cell against `docs/roadmap.md` status.

**Severity: MEDIUM** (accepted by the maintainer, `to-lead` "2026-11-13 19:56:23 GMT"). A phase close was signed on a record that said "none"; that is a record let through, the first limb of the process-finding exception. No wrong number follows: `FD-1495`'s price limb is a separate finding, and the severity reading of the other five "fix before close" rows found no live wrong-number path.

## Mechanisms of record (counts: M1 2, M2 6, M3 16 = 24)

Predicates ran read-only at T (`scratch/aud-b35/stage3.py`, output `stage3.out`) and again at `2ba0d0d53142` (`scratch/aud-b35v/stage3.rerun.out`, byte-identical).

- **M1, outside the set by the phase cell (2 rows): L52 (F14), L53 (F17).** `scripts/register-owed.py` `_matches_phase` splits the phase cell on `/` and tests the phase against the parts. Their phase cell is `1b`, so `2` is never in it. Neither row is in `g3join.json`.
- **M2, in the set; the draft cell said "fixed" or "decided", the register row was never opened as closed (6 rows): L49, L50, L64, L83, L323, L350.** `scripts/register-lint.py` `_opens_with_status` still read all six open. For L323 and L350 the closure sits behind `***Closed in place` or inside `*( … **CLOSED** …)*`, mid-cell, where neither `STATUS_PREFIXES` nor `_STATUS_MARKER` (`resolved|fixed` only) reads it.
- **M3, in the set; the draft cell said "carry → Appendix A target", counted as carried "with a named owner", never re-owned on the register (16 rows): L47, L48, L51, L84, L88, L89, L90, L96, L98, L109, L111, L112, L115, L122, L218, L295.** Their Work cells name W-ids (`W7-4` ×2, `W11-1.5`), `—` (×7), WK-671 (×5), WK-674 (L295) and WK-675 (L218). Batch 34's re-owning predicate (the Work cell with struck spans removed matches `WK-1178\b`) matched 0 of the 24.

**The maintainer's hypothesis is refuted for 22 of the 24.** The order of `to-lead` "2026-11-11 12:42:25 GMT" (3)(d) said the set "excluded rows with old W-ids, "—" Work cells, and owners that closed after T". In phase mode `register-owed.py` keys the phase cell, not the Work cell: all 22 Phase-2 rows print `in register-owed-2 owed set=True`. No row's Work cell names a Work that closed after T (WK-671, 673, 674 and 675 all read `closed` at T). Only M1's two rows were outside the set.

## Why "none" read true

The join compared the register to the closure record's own proposals. Every row had a draft cell, so every row "had a resolution". The owner test ran against Appendix A targets, which exist by construction. `CR-2110` carries its own caveat beside the count: "Counts are this seat's classing of the draft … a proposal".

## Evidence

The per-row mechanism is the output of `scratch/aud-b35/stage3.py`, named above. The second, differently built instrument: `scratch/aud-rejoin/join.py` at main `2ba0d0d53142` tests each open row's Work-cell and Decision-cell tokens against roadmap status. It is the instrument that found the 24. Its own limit (the marker does not match `***Closed in place` or a `*(… **CLOSED** …)*` line) is why L323 and L350 were in the 24 at all.

## Disposition

Register decision: **fix before close with an owner: WK-2114** (P3-D, process and instruments); not built in this batch. **The fix owed:** the phase-close join runs the shipped open predicate (`register-lint.py` `_opens_with_status`, by symbol) over ALL register rows and tests each row's owner, as written on the row, against `docs/roadmap.md` status (`draft` or `active`). It is `join.py` promoted to `scripts/`, with a red-first test over a fixture register of six open rows, each of which the join must report or pass as stated:

1. a closed-Work owner (reported);
2. a `—` owner (reported);
3. a W-id owner (reported);
4. a draft-Work owner (passes);
5. a row whose closure sits mid-cell behind `***` or inside `*( … )*` (the L323 and L350 shape: M2's limit);
6. a `1b` phase row (the L52 and L53 shape: M1).

Rows 5 and 6 are the extra the maintainer accepted (`to-lead` "2026-11-13 19:56:23 GMT", the fixture addition): without them two of the three mechanisms stay untested. Reverting the owner-status test must turn the test red on rows 1 to 3. After batch 35 merges, `join.py` at main prints 0; that line is the READY-FOR-P3 of record (`to-lead` 2026-11-11 12:42:25 GMT (4)).
