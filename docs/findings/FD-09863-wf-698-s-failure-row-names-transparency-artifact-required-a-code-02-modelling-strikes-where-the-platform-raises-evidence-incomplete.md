---
id: FD-9863
family: finding
title: WF-698's failure row names TRANSPARENCY_ARTIFACT_REQUIRED, a code 02-modelling strikes, where the platform raises EVIDENCE_INCOMPLETE
status: active
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-1178, WK-661, WF-698, FR-211]
---

# FD-9863 — a struck error code still in a workflow row

Filed from the lead's brief of 2026-10-12. Every line was re-read at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12.

## Evidence

- `docs/workflows/WF-00698-dataset-to-approved-model.md:129`: the failure row *"GBM submitted without a transparency artifact | `TRANSPARENCY_ARTIFACT_REQUIRED` at submission | `02` R3"*.
- `docs/specs/02-modelling.md:2117` shows the code struck (`~~TRANSPARENCY_ARTIFACT_REQUIRED~~`), and `:2144` states it is struck: *"`TRANSPARENCY_ARTIFACT_REQUIRED` and `PICKLE_PERSISTENCE_REFUSED` are struck"*.
- What the platform raises: `backend/src/app/platform/modelling.py:1273-1291` (`_require_evidence`) raises `PlatformError("EVIDENCE_INCOMPLETE", …, 422, …)` for a non-GLM model with no transparency artifact (`:1280`).

## Finding

**Severity LOW (proposed by the executor; the lead rules): doc drift, no behaviour is wrong.** A reader writing a test from WF-698 expects a code the platform never returns.

## Disposition

**Owner proposed: WK-1178** (the P2 fix tail) as the carrier of the correction; the Work that delivered the step is `WK-661` (Modelling, closed 2026-08-27), and `WF-698`'s owner role is the decision-maker (its front matter). Remedy: a dated correction to the WF-698 row naming `EVIDENCE_INCOMPLETE` (the amendment is the decision-maker's, `CLAUDE.md` §0 and `executor.md`: an executor does not amend a `WF-`). Event that next confirms or discharges it: `git grep -n TRANSPARENCY_ARTIFACT_REQUIRED -- docs/workflows` printing no unstruck hit. Filed by the executor, 2026-10-12.
