---
id: FD-1220
family: finding
title: A coded pricing-core error inside a Job is stored as JOB_HANDLER_FAILED, so a caller cannot branch on its code
status: active
created: 2026-09-29
owner: auditor
tree: 633c6f34b7e841e09c7f108cd4696658c524fcfc
corrected_by: []
relates: [FD-1217, WK-1178]
---

# FD-1220 — A coded pricing-core error inside a Job is stored as JOB_HANDLER_FAILED, so a caller cannot branch on its code

**Severity: low.** The auditor filed this finding on 2026-09-29, on the lead's instruction and the deputy's
ruling DP-889-CODE (his entry "2026-09-29 00:02:01 BST · deputy · DP-889-CODE: (A); my 00:00:45 premise corrected;
the job-path code loss goes to a LOW FD", `to-lead.md`). executor-s1 found it while building the sanitiser in
#889 (commit `c5699f45`). It is low because the message still carries the code as text, and no caller has been
shown to need the field.

## Finding

A pricing-core error that follows the `CODE: message` convention (for example `INPUT_CONTRACT_VIOLATION`, raised by
`_raise_named` as a `ValueError`), when raised inside a Job handler, reaches the worker's generic clause and is
stored with the code `JOB_HANDLER_FAILED` and the message `ValueError: INPUT_CONTRACT_VIOLATION: …`. A caller reading the
Job's error cannot branch on the real code. Only the batch scoring path parses the convention back into a typed code.

## Evidence

At `origin/main` `633c6f34`:

- **The Job path.** `backend/src/app/worker/tasks.py:228`–`:230`:
  `JobError(code="JOB_HANDLER_FAILED", message=f"{type(exc).__name__}: {exc}", retryable=False, trace_id=…)`.
- **The batch path, the only parser.** `packages/pricing-core/src/pricing_core/rating/score.py:881`–`:892`
  (`_batch_error_code`): it partitions the message at `": "`, and if the head is an upper-case identifier returns it as
  the code, else `(type(exc).__name__, message)`. Its docstring says it parses *"the `_raise_named` convention
  (`f"{code}: {message}"`) back into its parts, so an `"error"` output row carries the same typed code FR-255 names"*.
- **The requirement.** `docs/specs/07-platform.md:92`, FR-403: *"Failed Jobs record a typed error code, a human message,
  and — where the failure is deterministic (bad spec, invalid rule) — the field-level cause. Infrastructure failures are
  retried with exponential backoff; deterministic failures are not retried."* The words "the code is the contract" are
  not in FR-403. They are the worker's own comment (`tasks.py:191`, in the `PlatformError` clause: *"FR-403 makes the *code* the contract"*), which reads FR-403 that way.
- **The precedent.** OQ-646 (decided 2026-08-22) already gave a `PlatformError` its own clause so its `.code` survives
  storage, and left `JOB_HANDLER_FAILED` for a genuinely unexpected exception. A coded pricing-core `ValueError` is not
  a `PlatformError`, so it falls through to the generic clause.
- **What #889 builds, per the deputy's correction.** #889 (`c5699f45`, read at the commit) keeps both forms as they are:
  on the Job path `JOB_HANDLER_FAILED` with `ValueError: INPUT_CONTRACT_VIOLATION: <input-free text>`, on the batch path
  `INPUT_CONTRACT_VIOLATION` with input-free text. It adds a `CodedError` class in `pricing_core/safe_error.py` and
  changes no behaviour, by the deputy's decision DP-889-CODE = (A).

## Disposition

**Deferred with an owner — WK-1178**, confirmed by the deputy. The fix is new behaviour: the Job path maps a
`CodedError` (#889's class) to its own code, and FR-403 gets a dated clarification saying so. It is out of #889's scope.
Event: that mapping and clarification merge with a test that a coded error inside a Job is stored under its own code.
