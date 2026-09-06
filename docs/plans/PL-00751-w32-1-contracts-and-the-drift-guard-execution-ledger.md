---
id: PL-751
family: plan
kind: leaf
title: W32-1 — contracts and the drift guard: execution ledger
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-22
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-22-w6b-contracts-and-drift-guard-ledger.md
---

# W32-1 — contracts and the drift guard: execution ledger

What executing
[`PL-00752-w32-1-contracts-and-the-drift-guard-implementation-plan.md`](PL-00752-w32-1-contracts-and-the-drift-guard-implementation-plan.md)
actually did, on 2026-08-22, the same day the plan was written.

The plan is **not** edited to agree with this file — [`README.md`](README.md) has that rule.
Where the plan was wrong, this record says so and the correction lives here.

**Executed by three subagents plus the main thread.** Tasks 1–3 and Task 8 ran in parallel
(disjoint files); Tasks 4–7 ran as one unit afterwards, because all four edit
`backend/tests/test_contracts.py` and would otherwise have collided. The plan's fan-out
potential is one seam wide, and pretending otherwise would have produced merge conflicts
rather than speed.

---

## Result

| | Before | After |
|---|---|---|
| `backend/tests/test_contracts.py` | 55 passed | **99 passed** |
| `packages/pricing-core/tests/test_groupings.py` | 29 passed | **30 passed** |
| Contract defects outstanding | 6 known | **5 fixed, 1 escalated** |

All eight tasks delivered. Nine commits. **Three of the four constraint axes** plan review 3
assigned are built; arm-level attribution is out of scope as the plan states, and remains
`W32-1b`.

### The six defects, and what happened to each

| Defect | Verdict |
|---|---|
| `GroupingEvidence.source_level_stats` absent from the Python | **Fixed** — the value was already computed at the one construction site |
| `grouping` evidence rows hand-copied a four-field subset of `OneWayRow` with an invented `relativity` | **Fixed** — both halves now `$ref` one `$defs` entry; nine identical paths per side |
| `model.fit_result.terms.[]` — contract marked `bin_weights` and `standard_deviations` optional | **Fixed in the contract**; `EbmTerm` has no default for either |
| `custom-objective.params` — model admits `integer\|number`, contract only `number` | **Fixed in the contract**; `ObjectiveParams` is `dict[str, int \| float]` |
| `grouping.evidence.source_level_count` / `target_level_count` — `minimum` 0 against 1 | **Fixed in the model** (`ge=1`); here the spec stated the real invariant |
| `objective-certificate.result.checks` — `minItems` 8 against 1 | **Escalated as `OQ-600`** — see below |

---

## `OQ-600`, and why it was not a fix

The plan said not to pick a side here, and the evidence found on the day shows why that was
right. **Neither published number is correct.**

`02` §4.7's dated 2026-08-18 amendment says *"All nine checks are emitted for every template,
always"*, and the authored contract's own `$comment` from that same amendment calls
`branch_discontinuity` a **ninth** named check and adds it to the `name` enum — while leaving
`minItems: 8` untouched. So 8 is a stale pre-amendment count contradicted by the file it sits
in.

But the model's `1` cannot simply become `9`. `CertificateResult` is **shared** between
`ObjectiveCertificate` and `MetricCertificate`, and `FR-157` gives a metric certificate
**four** checks. A `min_length=9` on the shared type would refuse every metric certificate the
spec requires. That makes it a design decision — where the obligation lives — rather than a
bound, which is exactly the shape `CLAUDE.md` §0 reserves for the maintainer.

Scoped out of the guard by `(path, keyword)` pair, not by slug, and
`test_the_escalated_constraint_disagreements_are_still_unresolved` fails the moment either
side moves — so the carve-out cannot outlive the question it was taken for.

---

## Where the plan was wrong

Six items. The first is the serious one.

### 1. Task 2's test failed unconditionally and said nothing about the contract

The test collected `path.rsplit(".", 1)[-1]` and rebuilt `f"{block}.{name}"` — valid only
where every leaf sits one level below the block. `OneWayRow` carries two `tuple[float, float]`
fields; Pydantic emits a tuple as `prefixItems`, so they arrive as `…frequency_ci.[]` and
`…severity_ci.[]`, whose last segment is `[]`. The reassembly then asserted
`…source_level_stats.[].[]`, a path neither side can produce.

**The contract half of Task 2 was correct throughout** — verified independently: nine
identical paths per side, `relativity` gone, all six previously-undeclared model fields
present. Only the test was broken.

Fixed by comparing whole path sets directly, which is simpler as well as correct, and
**re-proved on broken input in both directions** before the green was accepted — a test
rewritten until it passes is worth nothing unless it still catches what it was written for.

The instructive part: the plan's own measurement section names `prefixItems` as the trap that
blinded the original `_type_map`, and the plan then wrote it again. Recorded in
`.claude/skills/contract-guard` with the rule that would have prevented it — **never rebuild a
path from a segment; compare whole paths as sets** — because knowing the trap demonstrably did
not.

### 2. Every restore line omits `docs/contracts/openapi/generated.json`

`generate-contracts.py` rewrites it alongside the schemas. A `git checkout` naming only the
schema silently drops the field from the OpenAPI contract, and `--check` then fails at the end
of the slice — after the step that caused it has scrolled away.

### 3. `git checkout` as a restore destroys uncommitted work

Not a plan defect so much as a gap in its ordering: the injection proofs restore with
`git checkout <file>`, which also reverts *unrelated uncommitted edits to that file*. This
destroyed Task 2's contract work once and it had to be reconstructed from the plan's own JSON.
**Commit the task, then inject.** The plan's Task 7 already says to prefer `git stash` for the
walker proof; the same reasoning applies to every proof in the slice.

### 4. Task 5's break command targets the wrong path

It uses `d['properties']['params']`; `params` actually lives at
`allOf[1].then.properties.params`. It raised `KeyError` and wrote nothing — a proof that
fails to break anything reads as a passing proof if nobody checks the exit code.

### 5. Task 7's `sed` pattern matches nothing

Its keyword ordering exists in no walker. The plan named the manual equivalent as a fallback
and that is what ran.

### 6. Two predictions that did not fire

Task 4's prose says "it found four" where the plan's own measurement table and the observed run
both say **two** — a leftover from the pre-measurement draft. And Task 6 predicted that
tightening the grouping counts to `ge=1` would break a fixture building an empty evidence; none
did, all 30 grouping tests passed. Recorded because a prediction that did not fire is evidence
about the codebase, not just about the plan.

---

## What the meta-guards proved

Task 7's control was checked by breaking the walker rather than the data: `_required_map` was
stopped from descending into `properties`, and
`test_the_contract_never_marks_optional_what_the_model_requires` **stayed green** while the
meta-guard went red naming both anchors. That is the silent-walker failure the control exists
for, demonstrated rather than asserted.

---

## Follow-on work this slice names

- **`OQ-600`** — the certificate check floor, maintainer's call.
- **`W32-1b`** — arm-level attribution, out of scope here by the plan's own statement. A
  GLM-only field declared on the GBM arm still passes, because `_type_map` unions every arm's
  contribution onto one dotted path.
- **The 14 authored schemas with no generated counterpart**, compared against nothing. Three
  of them — `dataset-version`, `validation-report`, `validation-rule` — describe artifacts
  Phase 1a built. Named in the slice map §5 and in `contract-guard`.
