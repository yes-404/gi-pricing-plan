---
id: LG-725
family: ledger
title: WK-661 — spec validation, and the half of FR-185 the last slice missed
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-16
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — spec validation, and the half of FR-185 the last slice missed, 2026-08-16 *(in progress, not closed)*

The fifth slice, and it opens by correcting the fourth. **FR-185 was recorded as
delivered and was half delivered:** the diagnostics slice recorded factor counts,
parameter counts and the two ratios, and shipped **no gate** —
`MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT` was registered nowhere and neither
`POST /model-specs/validate` nor `POST /models` refused anything. The requirement counted
as evidenced because a test marked it, which is exactly `CLAUDE.md` §13's "a marker is a
claim, not a proof" — found by reading the requirement rather than the marker, one slice
later than it should have been.

| Delivered | Evidence |
|---|---|
| `POST /model-specs/validate` (FR-153, `WF-698` D2) | **200 with `ok: false`**, not a 4xx: a spec that cannot be fitted is a complete answer to the question asked, and §5.3's live validation would otherwise error on every keystroke. A version that does not exist *is* a 404 — a bad reference rather than an invalid spec |
| Every problem, not the first | A spec with a missing factor, an unresolvable one and a bad response column reports all three. A validator that stopped at the first would make a ten-factor spec a ten-round conversation |
| **The FR-185 gate, on both entry points** | The requirement names `/model-specs/validate` **and** `POST /models`; a gate on the validator alone is advisory, because a caller can skip validation and post. Both call one `complexity_or_refuse`, so they cannot drift apart |
| The refusal is audited | `model_spec.refused_for_complexity`, asserted from the audit table. Only the complexity refusal — auditing every keystroke of a live-validating form would bury the governance events |
| Unset by default, and proved so | OQ-580 refused a platform-wide constant. Both settings resolve to `None`, and with neither set the gate returns before reading the version or its profile |
| **It costs nothing** | The parameter count comes from the stored profile's `distinct_count` and the exposure from the version's recorded totals — no parquet is read, which is what makes "before any compute is spent" true rather than aspirational |

**The estimate is named an estimate.** A banded factor is counted at its *unbanded* levels,
so the gate is conservative in the direction that refuses a spec which would have fitted.
Reading the data to count exactly would be the compute the gate exists to avoid; the
diagnostics record the true count after the fit, and that is the number a reviewer reads.

**Both directions are tested.** The same spec is accepted, then refused once the limit
moves below it — a test that only saw the refusal would pass against a gate that refused
everything, and one that only saw the acceptance would pass against a gate that never
fired.

**Not delivered.** FR-153's *objective applicability* half — which responses and
backends an objective admits — is unbuilt, because no custom objective exists to be
applicable or not. Owned by the custom-objective slice (FR-150/151).
