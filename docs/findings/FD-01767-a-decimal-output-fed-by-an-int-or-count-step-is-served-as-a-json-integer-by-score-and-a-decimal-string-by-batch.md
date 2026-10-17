---
id: FD-1767
family: finding
title: A declared decimal output fed by an int or count step is served as a JSON integer by /score and as a decimal string by batch
status: active
created: 2026-10-17
owner: auditor
tree: cf509df89dbebff329bb6b319bcc9bcd2a2c2352
corrected_by: []
relates: [WK-1178, SL-1563, RL-1343, RL-1567, OQ-1334, FD-1561]
---

# FD-1767 — A declared decimal output fed by an int or count step is served as a JSON integer by /score and as a decimal string by batch

*(Minted 2026-10-17 as FD-1767 from working id 8084, in the D19 batch mint PR.)*

## Finding

**MEDIUM; owner WK-1178; verdict `fix before close`** (severity by the contracts rule below).
`FR-214` (`docs/specs/03-rating-engine.md`, the `RL-1343` amendment) says a declared output of
type `decimal` is served as a JSON string on every scoring path, `/score` included. The
compiler accepts an `int` or `count` step into a declared `decimal` output (an allowed
widening), and the two paths then disagree: `/score` (`score_one`) serves the JSON integer
(`18`, `22`, `25`, Python `int`), the batch path serves the decimal string (`"18"`, `"22"`,
`"25"`). A client that reads one output name through both paths sees two JSON types.

## Evidence

The SL-1563 executor's read-only comparison, item 11 of `PL-1562`, recorded in the slice's
ledger (working id 8083, branch `origin/sl-1563-wk1178-fd1424-prep-2026-10-16`, section
"Item 11: /score vs batch, read-only", head `713d296a`): a probe built from
`test_rating_score_batch_outputs.py` `_probe_payload` (`result_type` set to the producer type,
output declared `decimal`, expression `driver_age`), compiled (accepted at save), then
`score_one` and `score_batch` over three rows. Script
`~/gi-pricing-plan.local/scratch/sl1563-dbwin/item11.py`, rc 0. This author did not re-run it.
No stored refused pair is involved.

**The severity rule's input, read at `origin/main` `cf509df89dbebff329bb6b319bcc9bcd2a2c2352`.**
The lead's brief relays the maintainer's rule (`to-lead.md` around 13:53:30; the verbatim
entry text was not found there, so it is the relay): HIGH if the integer violates the schema
`docs/contracts/openapi/generated.json` declares for the `/score` output, MEDIUM if that
schema allows both. The declaration: `POST /api/v1/score` 200 is
`#/components/schemas/ScoringResult`, whose `outputs` property is
`{"additionalProperties": true, "title": "Outputs", "type": "object"}`;
`docs/contracts/schemas/scoring.schema.json:60` is `"outputs": {"type": "object"}`. Neither
types a value, so a JSON integer and a JSON string both validate: **the schema allows both,
MEDIUM.** The defect is against `FR-214`'s text (which says "the contract admits no
non-integer number there", a statement about non-integers and not about integers), not
against the declared schema. Batch (`POST /api/v1/score/batch` 202) returns a `Job`; its
per-row `outputs_json` form is `03` §4's column, not an OpenAPI response schema.

## Disposition

Fix with an owner: WK-1178 (it delivers `FR-214`'s decimal-string form on `/score`; until it
does `/score` serves the engine's value). The fix is either that `/score` serializes by the
declared output type, as batch does, or that the compiler refuses the widening; that choice
is the owner's and is not made here. The event that next discharges it: the merge of the
WK-1178 slice that makes `/score` serialize by declared type, with a test over an `int` step
into a `decimal` output on both paths.
