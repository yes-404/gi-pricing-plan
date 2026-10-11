---
id: RL-1497
family: ruling
title: RL-1401 corrected — the "never compiled" premise was false at its own tree; submission already refuses a version without a passing Regression Run for its compiled bundle, so no finding is filed and the ruling's decisions are unaffected
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: decision-maker
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1401
relates: [RL-1401, RL-1379, FR-257, WK-673]
---

# RL-1497 — RL-1401 corrected: the "never compiled" premise was false at its own tree

*(Minted 2026-10-08 as RL-1497 from working id 9718, in the T8 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

## How this was ruled

- **This record rules nothing new.** The correction text below is the maintainer's, by
  delegation, copied byte for byte from its source. The decision-maker session `dm-9718`
  (`echo $CLAUDE_EFFORT` printed `medium`) drafted the record around it and re-verified its
  two sites.
- **The source.** `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
  "2026-10-05 10:02:28 BST — CORRECTION (mine) to my RL-1401 correction text (in "… FD 9720 NOT filed …"): the lead's two precision points ACCEPTED; #1119 (RL-1497) carries the AMENDED text below instead". Its blockquote, the maintainer's amended text, is the text in **Ruled**. It
  replaces the text first given in the entry headed "2026-10-05 09:54:07 BST — FD 9720 NOT filed (its premise is false, verified by me); RL-1401 gets a DATED CORRECTION LINE (not a note only); e3 LOW stands, with the doubt recorded", on the lead's two precision
  points, which that entry accepts: the false premise row is RL-1401's "An `approved` Rating
  Version can have no compiled bundle", not the adjacent row, and the gate refuses the
  submission, not the approval.
- **The form.** The 09:54:07 entry asked for the text to be appended to RL-1401. The entry headed
  "2026-10-05 09:57:58 BST — CORRECTION (mine), superseding the "append verbatim at the end of
  RL-1401" instruction in "… FD 9720 NOT filed …": option (a), a correcting record RL-1497
  with `corrects: RL-1401`; RL-1401 gains only `corrected_by: [RL-<minted>]`" replaced that
  with this record. Its reason: `docs/process/document-ids.md` §1.5 (the header block, the
  `superseded_by:` and `corrected_by:` comments) allows only `status:`, `superseded_by:` and
  an append to `corrected_by:` after a file freezes, and "the body is never edited".
- **The precedent followed** is RL-1322 (`corrects: RL-1312`), for its front matter and for
  its "How this was ruled" opening. RL-1383 (`corrects: RL-1361`), the precedent the 09:57:58
  entry names, has the same form.
- **The mint.** This is a working-id draft. At the mint, in merge order, RL-1401's header gains
  this record's minted id in `corrected_by:`. That is the only edit to RL-1401, in the same PR,
  and it is the append `audit-docs.py` check 34 allows. This draft does not edit RL-1401.

## Ruled

The maintainer's text, verbatim:

> RL-1401's premise row "An `approved` Rating Version can have no compiled bundle" (marked true) and its paragraph asking the lead to file one finding were already false at RL-1401's own cited tree: `submit_for_review` calls `_regression_run_gate` (rating_versions.py, from #886, 2026-09-29), which refuses a submission without a checked Regression Suite run for the compiled bundle (EVIDENCE_INCOMPLETE), pinned by test_rating_versions.py `test_golden_no_suite_is_refused_as_incomplete_evidence`. A Rating Version therefore cannot reach `approved` without a compiled bundle. The adjacent row "Such a version can never be compiled afterwards" (RL-1379) stays true. No finding is filed. RL-1401's decisions are unaffected.

So:

1. **No finding is filed.** RL-1401's "Findings to file" paragraph (the LOW finding for WK-673)
   is withdrawn. Its working id, FD 9720, was released by the 09:54:07 entry.
2. **RL-1401's decisions are unaffected.** Its refusals of an uncompiled version
   (409 `BUNDLE_COMPILE_FAILED`) and of a retired Environment (409 `VALIDATION_FAILED`), and its
   Author decision, stand as ruled.

## Verified, at `47d770e8fcbd2410fa101019ed8cf3aae69a1baa`

Each site was re-read by symbol, not taken from the relay.

| Site | Where | What the source says |
|---|---|---|
| The gate is called on submission | `backend/src/app/platform/rating_versions.py:317` | `run_id = await _regression_run_gate(`, directly after `_golden_quote_gate`, in the function that checks `Permission.RATING_SUBMIT` and refuses a non-draft version |
| The gate | `backend/src/app/platform/rating_versions.py:648` (`async def _regression_run_gate`) | Refuses `EVIDENCE_INCOMPLETE` (422) unless the golden-quote evidence has `status == "checked"` with results, and unless the latest Regression Run for this version's `bundle.content_hash` and the pinned suite hash is a `pass` |
| The pin | `backend/tests/test_rating_versions.py:1001` (`test_golden_no_suite_is_refused_as_incomplete_evidence`) | Submitting a version with no suite raises `EVIDENCE_INCOMPLETE`, the detail contains "at least one golden quote", and the row stays `draft` with no `golden_quotes` evidence |
| The origin | `git log -S'def _regression_run_gate'` | First added by `6a8b8e70` (2026-09-29T12:26:52+01:00), #886 |
| "At its own tree" | RL-1401's `tree:` `8252741cc3849058b6fc6836967448d88ff9821c` | `6a8b8e70` is its ancestor. At that tree, the call is `rating_versions.py:289`, the definition is `:619`, and the test is `test_rating_versions.py:1001` |
| The false row and the true row | RL-1401 at `47d770e8fcbd2410fa101019ed8cf3aae69a1baa`, `:54` and `:55` | `:54` "An `approved` Rating Version can have no compiled bundle" (marked true, citing `rating_versions.py:250-300` and `:551-578` @14c7e805; `6a8b8e70` is also an ancestor of `14c7e805`). `:55` "Such a version can never be compiled afterwards" cites RL-1379 and stays true |

## What it obliges

- **This draft:** this record only. RL-1401 is not edited.
- **The mint turn (the lead, in merge order):** this record's working id becomes its minted
  id, and RL-1401's header gains `corrected_by: [<this record's minted id>]`. That append is
  RL-1401's only edit, in the same PR.
- **The lead:** files no finding from RL-1401's "Findings to file" paragraph. WK-673 gains no
  obligation from it.

## Acceptance — the violation that must become detectable

- *Violation: after the mint, RL-1401's `corrected_by:` names this record while this
  record's `corrects:` does not name RL-1401.* `audit-docs.py` check 34 reports it
  (`scripts/audit-docs.py` `check_freeze`, the "corrected_by entry … does not
  corrects: back" failure). **The other direction is not checked:** a `corrects:` with no `corrected_by:`
  back passes check 34, which is why this draft is green before the mint. The mint turn's
  read-back of RL-1401's header is the only guard on that direction.
- *Violation: the mint edits any other line of RL-1401.* Check 34 reports a frozen-family diff
  that is not a `status:`, `superseded_by:` or `corrected_by:` change.
- *Violation: a submission of a Rating Version without a passing Regression Run for its
  compiled bundle succeeds.* `test_golden_no_suite_is_refused_as_incomplete_evidence` fails.
