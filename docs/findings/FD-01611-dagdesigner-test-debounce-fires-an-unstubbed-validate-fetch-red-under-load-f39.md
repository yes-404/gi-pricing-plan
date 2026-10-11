---
id: FD-1611
family: finding
title: The DagDesigner live-validation debounce can fire an unstubbed /rating-algorithms/validate fetch inside a test, so F39 reds a loaded gate
status: active
created: 2026-10-11
owner: auditor
tree: 99f22479
corrected_by: []
relates: [WK-675, SL-1526, SL-1600]
---

# FD-1611 — the DagDesigner debounce fires an unstubbed `validate` fetch under load

**Minted 2026-10-11 from a working id, in the D10 batch.** Drafted in the D10 docs batch, at the maintainer's ruling (`to-lead.md`, "2026-10-11 10:38:57 BST —
DagDesigner F39 reds: an FD against WK-675 at D10 ADOPTED, with a small fix slice queued; no synthetic-load
reproduction needed; interim classification adopted", item 2). Every line number is at `origin/main`
`99f22479`, read for this record.

## Evidence

- The guard is `frontend/src/test-setup.ts:22`: a test that reaches `fetch` without stubbing it fails, by name,
  in `afterEach`: `F39: this test called fetch without stubbing it: <urls>`. (The F39 register row, W11-1.5, is
  the original instance: an unexplained connection to port 3000. This is a second, explained cause.)
- The source is S3's (`#1271`) live validation: `frontend/src/components/dag/useGraphValidation.ts` takes
  `delayMs = 400`; a `watch` on the draft sets a `setTimeout` (`:34`) that calls `validateRatingAlgorithm`, a
  `fetch` to `/api/v1/rating-algorithms/validate`. `onBeforeUnmount` cancels the timer (`:56-59`), but a test that
  mounts `DagDesigner` and does not unmount it before 400 ms of real time pass lets the timer fire into the
  test's `afterEach`.
- The reds, as the lead reported them (`from-lead` 10:36:54, `to-lead` 10:38:57): two **different** tests in
  `DagDesigner.test.ts` went red in two loaded gates, each with the same guard text naming
  `…/api/v1/rating-algorithms/validate`: `SL-1526` at `e00c71c1` ("opens the inspector …") and `SL-1600` at
  `8f674476` ("emits an edited draft …"). On `main` `99f22479` the file run alone ×3 at load 1.07 passed 4/4 each
  time (the lead). I did not re-run it for this record.

## Finding

Whether the 400 ms timer lands inside a test depends on how slow the box is, so the defect appears only in
loaded gates and is invisible alone. The guard text is its own proof (the maintainer, 10:38:57 item 1), so no
synthetic-load reproduction is owed.

**Severity (proposed by the auditor): LOW.** The reason: it pollutes every loaded gate and costs a gate re-run.
No product behaviour is wrong; a user's browser stubs nothing and the fetch is intended.

## Remedy (ruled, 10:38:57 item 3)

A small fix slice under WK-675, not folded into S4 (whose write set is backend): stub
`/rating-algorithms/validate` for the whole file, and flush or cancel the debounce in teardown; red-first with
the timers advanced past the debounce after the assertions (F39 on base, green after). Slice: SL 9916 (working
id; the executor's brief names it).

**Interim (10:38:57 item 4):** a gate whose only frontend red is a DagDesigner F39 un-stubbed-validate failure
is classified WK-675's; it does not block the slice under test, and CI at the minted head decides.

## Disposition

**Owner: WK-675**, discharged by the fix slice above. Decision: `fix before close with an owner: WK-675`. Event
that next confirms or discharges it: the fix slice's merge and a loaded gate that no longer prints the F39 line.
Filed by the auditor, 2026-10-11; the lead gives the verdict.
