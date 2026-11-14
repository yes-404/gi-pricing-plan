---
id: FD-2058
family: finding
title: a tolerance past the write bound is accepted at 202 and fails the Job after the compute
status: active
created: 2026-11-06   # original date 2026-11-06, set at the draft; working id 8400, minted 2026-11-06
owner: auditor
tree: ebc45f5fc22a35be22521c6e7f6a06ed0045f2cb   # the head the probe ran at (the slice branch, before the merge of origin/main)
corrected_by: []
relates: [WK-1178, SL-2056, LG-2057, FR-21, NFR-499]
---

# FD-2058 — a tolerance past the write bound is accepted at 202 and fails the Job after the compute

*(Minted 2026-11-06 as FD-2058 from working id 8400, born open, in the PR of SL-2056. Severity LOW and owner WK-1178 are the lead's, to-lead "2026-11-06 07:47:44 GMT".)*

## Finding

`POST /peril-structures/{id}/reconcile` accepts a `tolerance` with any exponent (FR-21: validation takes any exponent; the route checks only `> 0`). `reconcile_payload` (`platform/perils.py`) carries `str(tolerance)` into the Job, which is committed, and the route answers 202. The worker runs `reconcile()`, then `record_reconciliation` writes `Reconciliation.model_dump(mode="json")`; the writer (`money.py` `_positional`, bound 308) raises `DecimalMagnitudeError` inside the unit of work, which rolls back, and the Job ends FAILED. The caller learns of the refusal only after the compute.

Nothing stored wrong: no row is poisoned, no read is affected. The cost is the wasted compute and a late failure.

## Evidence

DB-free probe at `ebc45f5f` (`~/gi-pricing-plan.local/scratch/sl8340f-probe/probe_tol.py`, log `probe.log`): payload tolerance `1E+400`; `Reconciliation(... tolerance=Decimal("1E+400"))` constructs; `model_dump(mode="json")` raises `PydanticSerializationError`; the text the worker's `except Exception` arm stores (`safe_job_error_text`) is `'PydanticSerializationError'`, which holds no `1E+400` and no digit run (NFR-499 holds). Control: the same script reading `str(exc)` instead fails the digit-run assert, so the assertion can fail.

## Disposition

LOW. No fix before freeze: a bound at the request needs a dated decision, since FR-21 says validation takes any exponent. Carried to the P2 closure record's carry-forward list.
