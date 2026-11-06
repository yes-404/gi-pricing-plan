---
id: FD-2029
family: finding
title: The NFR-499 error-sink census does not see an exception passed bare to a logging call, repr(exc) or exc.args
status: active
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8384, minted 2026-11-06
owner: lead
tree: bdad1322   # the tree of the lead's check below; origin/main when drafted is cded9f0e1953f2db6a6a1375892257a1a4822fc3
corrected_by: []
relates: [FD-1507, NFR-499, WK-1178]
---

# FD-2029 — the census finds `str(exc)` and `{exc}`, not the other ways an exception's text is stored or logged

*(Minted 2026-11-06 as FD-2029 from working id 8384, in the docs batch 12 PR.)*

## Finding

**LOW, owner WK-1178**, as DP-H3 of PL 8333 was ruled (to-lead "2026-11-05 10:31:31 GMT"), **on one check** (to-lead "2026-11-05 16:52:49 GMT" item 2). The census (`_sinks`, `backend/tests/test_error_sinks.py`) identifies an exception by binding (an `except … as` name, or a parameter named `exc`) but counts two shapes of use only: `str(<name>)` and `{<name>}` in an f-string. FD-1507's essay, step 4, measured that `_log.warning("failed: %s", exc)` and `return repr(exc)` pass it; `<name>.args` is the same class. NFR-499 is guarded for two shapes of an exception's text, not for the family.

## Evidence

The check, and why LOW stands:

The lead ran the live-tree scan at `bdad1322`: `~/gi-pricing-plan.local/scratch/fd8384/fd8384.py`, an AST scan over `backend/src`, `packages/pricing-core/src` and `packages/model-schema/src` (**203 files, tests excluded**) for names bound by an except handler or a parameter named `exc` that reach `repr(name)`, `name.args`, `!r` in an f-string, or a logging-call argument. **0 hits.** The instrument was proved red on a planted multi-line file (`scratch/fd8384/planted.py`): **3 of 3** shapes found. `exc_info` appears on 6 lines; all 6 are sanitised (see the maintainer's reply, to-lead "2026-11-05 16:52:49 GMT"). None today means LOW stands; a real hit would have made it MEDIUM and a fix.

## Not claimed

That no quote input is logged by another route; this is the guard's scope and one scan's corpus, not a proof over all code.

## Remedy (proposed, not built)

Extend `_sinks` with the three shapes; list each hit in `_SINKS` with a verdict read from its raise sites; prove both directions in `test_the_census_sees_an_injected_sink`.

## Disposition

Open, owner WK-1178; event that next discharges it: that extension merging with its verdicts, or a dated ruling accepting the narrower census. Filed by the auditor of SL 8334 (`scratch/aud-slh/FD-new-census-shapes.md`) as working id 8384.
