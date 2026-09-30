---
id: FD-1348
family: finding
title: The contract guard does not compare the objective-certificate check-name enum against the code's check vocabulary
status: active
created: 2026-09-30
owner: auditor
tree: ee5de4438c84cb76ba1343012dcf4bca3444cad7
corrected_by: []
relates: [WK-690]
---

# FD-1348 — The contract guard does not compare the objective-certificate check-name enum

**Minted 2026-10-01 as FD-1348** (`python3 scripts/doc-id.py next --ref f689c7828cb05eb2298f3fec505a4638c4437a11` printed `1346`, and the lead allocated `1348` in mint batch 13, after RL-1346 and RL-1347). It was filed under working id 9803. Source: executor-690s2 found it in WK-690 Slice 2
(ledger LG working id 9979, Task 5, draft PR #1025, branch `sl-1272-symbolic-derivation`); auditor-690s2 proposed it;
this record is the auditor's.

## Finding

**Severity: MEDIUM; owner WK-690 (the lead's adoption, `DISPATCH-WK-690-S2-2026-09-30.md` Delta 4, local, outside the
repository).** The hand-authored `name` enum in `docs/contracts/schemas/objective-certificate.schema.json`
(`result.checks[].name`) is not compared against `OBJECTIVE_CERTIFICATE_CHECKS` or `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC`
in `packages/model-schema/src/model_schema/objectives.py`. Either side can change and the guard stays green. Slice 2
adds two names (`symbolic_vs_numeric_gradient`, `symbolic_vs_numeric_hessian`), so the published vocabulary an external
reader builds against is now 11 names held by hand against a 9-plus-2 code vocabulary.

## Evidence

**1. Reproduction.** Tree: detached checkout of `origin/sl-1272-symbolic-derivation` at
`ee5de4438c84cb76ba1343012dcf4bca3444cad7` (the names arrive with #1025, so `main` does not show it), after
`uv sync --all-packages`. Baseline, unmodified:
`uv run pytest -q backend/tests/test_contracts.py -p no:cacheprovider` → `144 passed, 2 skipped`, rc 0.
Broken input: in `docs/contracts/schemas/objective-certificate.schema.json` replace `symbolic_vs_numeric_gradient`,
`symbolic_vs_numeric_hessian`, `finiteness`, `convexity` and `smoke_fit` with `"BOGUS"` (a python string replace; `git diff
--stat`: 1 file, 3 insertions, 3 deletions; `grep -n BOGUS` shows lines 29, 30 and 32). The same pytest command →
`144 passed, 2 skipped`, rc 0 (replacing all 11 names gives the same result, reproduced by auditor-1029). **Identical to the baseline.** Reverted with `git checkout --`; `git status --short` empty.

**2. Cause: no comparison reaches the enum.** The generated side gives `name` as a bare string:
`docs/contracts/schemas/generated/objective-certificate.schema.json`, `"name": {"title": "Name", "type": "string"}`
(from `CertificateCheck.name: str`, `objectives.py` line 603). The vocabulary lives in two tuples that the model checks
only at validation time (`battery_is_exactly`). So the guard has no code-side enum to compare: the type walker
(`_type_map`) sees `string` on both sides, and the one enum comparison that exists
(`test_job_status_and_kind_enums_agree_with_the_contract`) names `job` fields only. `.claude/skills/contract-guard/SKILL.md`
says every walker is scoped to the intersection of what both generated and authored declare, and that a path carrying a
keyword on one side only is outside the comparison by construction (OQ-649 owns the general question). This is that case.
Absent: a comparison that reads the two tuples (the code's vocabulary) and sets them against the authored enum.

## Exposure

A name added, renamed or dropped on one side only makes the published contract and the emitter disagree with no red
test: an external reader validating against the enum rejects a real certificate, or accepts a name the platform never
emits. The certificate is a governed artifact (FR-146 blocks submission on it), so the vocabulary is an audit surface.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** The lead's decision: adopted at **MEDIUM, owner WK-690**; a
follow-up slice adds the guard comparison per `.claude/skills/contract-guard` (measure first, name the expected result,
prove it red on broken input as in Evidence 1, add its meta-guard) and lands **before WK-690 closes**.

**Event that next confirms or discharges it:** that slice merges, with Evidence 1's broken input turning the guard red.

## Decision

Adopted by the lead at MEDIUM, owner WK-690 (`DISPATCH-WK-690-S2-2026-09-30.md` Delta 4). Discharged when the follow-up slice's guard comparison merges and Evidence 1's broken input turns it red.
