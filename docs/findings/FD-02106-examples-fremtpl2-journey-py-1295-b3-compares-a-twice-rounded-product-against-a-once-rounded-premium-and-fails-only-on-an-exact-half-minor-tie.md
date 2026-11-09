---
id: FD-2106
family: finding
title: examples/fremtpl2/journey.py:1295 B3 compares a twice-rounded product against a once-rounded premium, and fails only on an exact half-minor tie
status: active
created: 2026-11-09
owner: auditor
tree: 2ecdd7a302b9b1ed5746f90531085169e279469f   # the head the B3 diagnostic ran at (scratch/exec-rehdry/b3diag.log line 1); examples/fremtpl2/journey.py has 0 commits between 374a22bf and this branch
corrected_by: []
relates: []
---

# FD-2106 — examples/fremtpl2/journey.py:1295 B3 compares a twice-rounded product against a once-rounded premium, and fails only on an exact half-minor tie

## Finding

B3 of the freMTPL2 journey (`examples/fremtpl2/journey.py`, check name `LOADING_NOT_MULTIPLIED_INTO_THE_PREMIUM`, raised at `:1297`) asserts that a quote dated after the loading rise is the earlier quote's premium times the new loading. At `:1295` it forms that expectation as `_minor(Decimal(self.result.prod_premium_minor) * Decimal(LOADING_AFTER))`. `prod_premium_minor` is the earlier quote's `value_minor`, which the product has **already rounded** to a whole minor unit. The check therefore multiplies a rounded value and rounds again, while the product multiplies the earlier **unrounded** value by the loading and rounds **once** (FR-2082, D-1's rule). Where the two roundings disagree the check reports a loading that was applied as not applied. They disagree only when the once-rounded product lands on an exact half minor unit. The check is wrong; the product is right.

**Severity LOW; owner P3-C, the check's limb**, per the maintainer's "2026-11-09 14:02:10 GMT" entry (`to-lead.md`, outcome (a)). LOW because the product prices correctly and only a journey check misreads a tie. **Fix direction:** compare against the later quote's own `unrounded_minor`, not made before Wed 18 (no code before then).

## Evidence

The 200,000-row sample diagnostic of 2026-11-09 (`scratch/exec-rehdry/b3diag.log`, local, not in the repository, sha256 prefix `20c6b3b60a58`, lines 5943-5945, run at head `2ecdd7a302b9`) printed both sides of B3's comparison:

1. Earlier quote, `payable_premium` rung: `value_minor` 65670, `unrounded_minor` 65669.8996027643040000, half-even at 0 dp.
2. Later quote, same rung: `value_minor` 68953, `unrounded_minor` 68953.3945829025192000, half-even at 0 dp.
3. B3's line: `later_rung 68953 expected 68954 prod_premium_minor 65670 LOADING_AFTER 1.05 exact 68953.50`.

The maintainer re-computed it at `to-lead` "2026-11-09 14:02:10 GMT": 65669.8996027643040000 × 1.05 = 68953.3945829025192, which equals the later quote's `unrounded_minor`, and rounded once half-even gives 68953 = the later `value_minor`. The journey's `:1295` multiplies the rounded 65670 × 1.05 = 68953.50, an exact tie, which half-even rounds to 68954. So the product applied the loading and rounded once, 68953; the check rounded twice, 68954. No under-pricing and no product change. The same code passes with "B3 ok" on the full seed in the freeze gate (`demo.log:198`), where the tie does not arise.

Read at this branch: `examples/fremtpl2/journey.py:1295` (the expectation) and `:1297` (the raise); `git log --oneline 374a22bf..HEAD -- examples/fremtpl2/journey.py | wc -l` = 0.

## Disposition

Open, owner P3-C, the check's limb. Not fixed before Wed 18: the journey is rehearsal and demo code and the product is right. On a B3 failure with the full seed, the runbook line of the same 14:02:10 entry applies: if the earlier `unrounded_minor` × loading equals the later `unrounded_minor` to the minor unit, it is this finding's tie, the product is right, log it as an instance of FD-2106 and continue; any other difference is a product fault. Remedy at P3-C: have B3 read the later quote's own `unrounded_minor` as the comparand instead of re-deriving the product from a rounded value.
