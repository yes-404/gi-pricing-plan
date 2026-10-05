---
id: FD-9759
family: finding
title: FR-223's MODEL_REFERENCE_MODE_INCONSISTENT is emitted nowhere, and its "checked at save time" is unreachable
status: active
created: 2026-10-01
owner: auditor
tree: a978dc2297bc8bfcc1c4da09ded37cefdcf92156
corrected_by: []
relates: [FR-223, FR-222, FR-240, WK-675, WK-1178]
---

# FD-9759 — FR-223's named code is never emitted, and its save-time check cannot run

## Finding

**Severity: LOW. Decided by the maintainer, 2026-10-01, received by the lead before 10:23 BST (the maintainer's entry headed "2026-10-01 10:22:24 BST"), verbatim:**

> FD 9759: LOW. The invariant IS enforced (it raises at compile), so nothing inconsistent compiles; the defect is the error contract (generic BUNDLE_COMPILE_FAILED) plus an unreachable 'at save'. Loud, not a mispricing.
> Discharge, all of: (1) a DM rules FR-223's check point (compile + the RL 9767 validate route vs 'save'), verbatim text, recording which side was wrong; (2) a typed error mapped to MODEL_REFERENCE_MODE_INCONSISTENT at compile AND in the validate route, red first; (3) a listed, counted sweep of bare ValueError raises in ALGORITHM_CHECKS / compile_bundle so no other check maps to the generic code.
> Owner: the WK-675 slice that builds RL 9767's validate route (S3's leaf), NOT WK-1178. If S3 is cut to P3 Saturday, it re-homes to WK-1178 by a dated line.

RL 9767 (working id) rules that route; RL 9758 (working id) is the FR-223 ruling. This replaces the auditor's earlier proposal,
kept below as struck text (append-only):

> ~~**Severity: proposed: LOW-MEDIUM; severity is the maintainer's.** Reasoning: a version whose steps disagree with its
> `model_reference_mode` **is** refused (at compile), so no wrong price results. What fails is the specified refusal: the code
> the spec names is never returned, the refusal comes back as a generic `BUNDLE_COMPILE_FAILED`, and the "at save time" limb has
> no code path.~~
> ~~**Owner: proposed WK-1178.** Reason: the defect is in the compile and refusal path, the rating-engine correctness stream
> WK-1178 owns. The alternative was WK-675 Slice 2, which shows the mode read-only in the designer but builds a view and not this
> path.~~ *(Struck 2026-10-01: superseded by the maintainer's decision above.)*

`docs/specs/03-rating-engine.md` FR-223 (§3.2): every `model_call` step's `mode` "must equal [the version's
`model_reference_mode`], **checked at save time** beside FR-227's type check, and a version whose steps disagree with it is
refused with `MODEL_REFERENCE_MODE_INCONSISTENT`."

Found while auditing RL 9767 (working id; PR #1055), whose *Not decided here* section states the first limb as an
observation for the auditor to file.

## Evidence

All at `origin/main` `1dd5e264` (tree `8bd782acbbdde8e3b4195b5a0acb89183b5a0253`).

1. **The code is emitted nowhere.** `grep -rn MODEL_REFERENCE_MODE_INCONSISTENT packages/*/src backend/src frontend/src`
   prints nothing. Its only occurrences are in `docs/` (the spec and the plans quoting it).
2. **The check raises a bare `ValueError`.** `check_model_reference_mode` (`packages/model-schema/src/model_schema/rating.py:173`)
   raises `ValueError(f"model_call step {step.step_id!r} declares mode ... (FR-223)")`, with no code prefix.
3. **It is called only from compile.** `packages/pricing-core/src/pricing_core/rating/compile.py:614`, after `validate_algorithm`
   (`:611`) and the first-issue refusal.
4. **The backend maps it to the wrong code.** `backend/src/app/platform/rating_versions.py:558-564` (as at `1dd5e264`: `:528-536`): any `ValueError` whose
   text does not start with an upper-case `CODE: ` falls to `BUNDLE_COMPILE_FAILED` (422).
5. **"At save time" is unreachable.** Algorithm save (`POST /rating-algorithms`) has no Rating Version, and the check needs
   one (`version.model_reference_mode`). So the save-time limb of FR-223 cannot be implemented where the spec places it.

### Red reproduction (compile path, today's tree)

The existing fixture of `packages/pricing-core/tests/test_rating_compile_bundle.py:234-239`
(`test_a_mode_mismatch_is_refused_at_compile`): the version's mode is set to `approximation` against a `model_call` step in
`exact` mode. Run through `compile_bundle`, then through the mapping of `rating_versions.py:560-563` (as at `1dd5e264`: `:531-534`) copied verbatim:

```
exception text: model_call step 's_rp' declares mode 'exact', but the version declares 'approximation' (FR-223)
code the API returns (rating_versions.py:560-563 logic): BUNDLE_COMPILE_FAILED
```

The expected code is `MODEL_REFERENCE_MODE_INCONSISTENT`. The existing test asserts only `match="FR-223"` on the message, so it
passes while the code is wrong. The mapping was reproduced by copying its four lines, not by calling the route; the route was
not run (no database in this session).

## Disposition

**Owner: WK-675 S3's leaf (the slice that builds RL 9767's validate route), per the maintainer's decision above.** Discharge is
all three of the maintainer's items: (1) a decision-maker rules FR-223's check point, with verbatim text, recording which side
was wrong (item 5 of the evidence is the spec-side gap); (2) a typed error mapped to `MODEL_REFERENCE_MODE_INCONSISTENT` at
compile and in the validate route, red first, asserting the code and not only the message; (3) a listed, counted sweep of bare
`ValueError` raises in `ALGORITHM_CHECKS` and `compile_bundle`, so no other check maps to the generic code.

**Limb (2) amended 2026-10-01 10:30 BST** by the maintainer, `to-lead.md` entry headed "2026-10-01 10:30:00 BST — ACCEPTANCE:
RL 9770 (NFR-490's statistic = p99) as the spec interpretation; FD 9759 limb (2) discharged at the compile site alone; #1060
audit noted": limb (2) is discharged by the compile-site typed error alone; the validate-route clause falls away, because that
route has no rating version, hence no `model_reference_mode` (RL 9758 and RL 9767 (working ids) agree). This supersedes "...
at compile AND in the validate route" above, which is kept as written.

Filed 2026-10-01 as working id 9759.

**Amended 2026-10-05 before mint: citations re-anchored, nothing decided.** Re-read at `origin/main` `ef5dc6e7` (tree
`a978dc2297bc8bfcc1c4da09ded37cefdcf92156`, now the header's `tree:`). The finding holds unchanged: `git grep -n
MODEL_REFERENCE_MODE_INCONSISTENT origin/main -- packages backend/src frontend/src` prints nothing; the check is still a bare
`ValueError`, still called only from `compile_bundle` (`compile.py:573`) at `:614`, after `validate_algorithm` (`:611`); FR-223
is at `03-rating-engine.md:109` and the code is listed among the owned codes at `:936`. Moved cites, found by symbol:
`check_model_reference_mode` `rating.py:172` → `:173`; the mapping at `rating_versions.py:528-536` → `:558-564` (the
`except ValueError` at `:559`, the generic-code fallback at `:563`). The fixture `test_a_mode_mismatch_is_refused_at_compile`
is at `test_rating_compile_bundle.py:235` (the cite `:234-239` still spans it). Evidence 1-5 and the red reproduction were
**not re-run** (a gate slot is held); the 2026-10-01 reproduction output above is a dated reading. `RL 9758`, `RL 9767`
and `RL 9770` are still working ids on main (no minted record carries them), so they stay in working-id form; no other
working id in this record has minted. Evidence's `1dd5e264` base sentence is historical and stays as written.
