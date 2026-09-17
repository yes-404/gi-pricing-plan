---
id: PL-780
family: plan
kind: leaf
title: W32-11 ledger — certificate floors and two generated sides
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-24
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-24-w32-11-certificate-floors-and-two-generated-sides-ledger.md
---

# W32-11 ledger — certificate floors and two generated sides

**Filed 2026-08-24.** Records what the slice delivered, every `CLAUDE.md` §0 verdict it reached,
and a §13 verdict for each finding. The plan beside this file is frozen at its date and is not
edited; where execution falsified it, that is written here rather than corrected there.

Measured on the W32-11 branch, which is `946725f` (`origin/main`, 2026-08-24) plus this slice.
Every count below is a measurement of that tree at that moment and is worth re-taking rather
than quoting.

---

## What was delivered

| Task | Outcome |
|---|---|
| 1 | `CertificateResult.checks` unbound; `battery_is_exactly` enforces the nine-name battery (`ObjectiveCertificate`, `02` §4.7) and the four-name one (`MetricCertificate`, FR-157) **by name, not by count**. Authored `objective-certificate.schema.json` `minItems` 8 → 9. `UNRESOLVED_CONSTRAINT_DISAGREEMENTS` emptied. FR-158 / OQ-600 |
| 2 | `dataset-version` gains a generated side |
| 3 | `validation-report` gains a generated side; its authored contract gains the `id` it always required |
| 4 | Counts recomputed and `contract-guard` corrected; this ledger; five open-question rows; the roadmap slice record |

`COMPARED_SLUGS` 13 → **15**. Authored-without-generated 14 → **11**. The corpus is 26 authored,
25 generated, **15 both-sided**, 11 authored-only, 10 generated-only, 36 distinct.
`COMPARED_SLUGS` equals the both-sided set exactly — nothing eligible is unaccounted for.

**The Phase-1a gap named in `contract-guard` is closed.** It listed `dataset-version`,
`validation-report` and `validation-rule` as shapes describing artifacts Phase 1a built that
nothing compared; **W32-2 closed `validation-rule`** (`a23e16b`) and **this slice closed
`dataset-version` and `validation-report`** (`9ab14d6`). That set is now empty and the sentence
naming it is retired rather than reworded.

*(Corrected 2026-08-24, after this ledger was filed and merged. It first read "W32-2 closed the
first and this slice closed the other two" — `validation-rule` is third in the list above, not
first, so the attribution was inverted in both this file and `docs/roadmap.md`. The closed set
was right in both, so nothing downstream was wrong. Corrected in place rather than appended,
because a reader who reaches only this sentence would otherwise still take the wrong slice.
`.claude/skills/contract-guard/SKILL.md` had it right throughout and is what surfaced the
disagreement; the file-addition history of each generated schema settled it.)*

---

## §0 verdicts

`CLAUDE.md` §0: when code and spec disagree, say which was wrong and why, never quietly make
either match the other.

| # | Disagreement | Verdict |
|---|---|---|
| V1 | `CertificateResult` carried `min_length=1` — a count floor standing in for a battery | **Both sides were wrong about the question.** A count cannot express "these nine checks"; a nine-long battery with one check missing and another duplicated passes it and reads as complete to an approver. Decided at OQ-600 option (a), specified FR-158 |
| V2 | `validation-report.schema.json` declared **no `id` at all**; `ValidationReport.id` is a required `UUID` | **The contract was wrong, by omission.** Never ambiguous: `dataset-version.schema.json` references `validation_report_id`, so a report demonstrably has identity. `id` added directly rather than by composing the envelope — the route `diagnostics` and `transparency-artifact` took — because composing it would import the nine unbuilt envelope fields `ENVELOPE_GAP_IS_RECORDED_NOT_FIXED` records |
| V3 | `results.[].offending_sample.[]` is `string` on the model, `object` in the contract | **Neither side is obviously right, so no side was picked.** §0 forbids a silent choice; recorded as `OQ-567` with a recommendation, and the type comparison pinned at that one path with a companion test. Reasoning below |
| V4 | `DatasetVersion` and its contract diverge on 22 of 48 paths, all one-sided | **The contract is ahead of the model on the flat fields; the three structural fields are a real shape question.** Recorded as `OQ-568`. Trimming the contract to match the code was rejected outright — that is deleting the specification to make the tooling agree |

### Why V3 was not decided

The model's `string` is what `_sample` in `pricing_core.data.validate` emits: composite key values
joined with `|`, no escaping, `None` rendered as the empty string and so indistinguishable from
one, column names dropped. No specification defines that encoding. The contract's
`{"type": "object"}` is bare — no properties, so it constrains nothing a validator could check.
FR-49 and the `01` §2 glossary both say "primary keys of rows" without choosing; §4.6's only
example prints `"offending_sample": []`, which is evidence for neither.

The recommendation is the keyed object, because the sample exists to be traced back to rows and
the string form is lossy in three independent ways at exactly that job. It was not *done* because
deciding it changes `pricing-core`'s validation engine, **13 assertions across three test
modules** — `test_validate.py`, `test_catalogue.py` and `test_api_datasets.py`, measured
2026-08-24 — the published contract, the generated frontend type
and §4.6's example — a data-model change across the suite, in a slice scoped to certificate floors
and two generated sides.

**On pinning it rather than fixing or failing.** `test_generated_and_authored_agree_on_scalar_types`
refuses exemption lists in its own docstring, and that refusal was taken seriously rather than
worked around. It is a refusal of a *curated* list — entries nobody can date or justify — not of a
single path held open against a written question with an owner. That is precisely what
`diagnostics.aliasing` was until `OQ-587` was decided and its pin was deleted rather than
relaxed. `UNRESOLVED_TYPE_DISAGREEMENTS` follows that precedent and dies the same way.

---

## Findings

### The three the plan named

| # | Finding | §13 verdict | Where it lives |
|---|---|---|---|
| F1 | With the shared type unbounded, the floor is published on the authored side only; the generated side and the OpenAPI component carry none | **Delivered.** FR-158 asks for enforcement where each certificate is constructed and never asked the generated client to carry a floor. The limit — enforcement is server-side — is published, not implied | The requirement, satisfied as written |
| F2 | No authored-keyword completeness check exists: a keyword declared on the authored side alone is compared against nothing | **Deferred with an owner.** This is the keyword case of a more general finding and is **subsumed by `OQ-649`**, named there so it is not filed twice | `OQ-649` |
| F3 | `metric-certificate` has no authored contract at all | **Deferred with an owner.** Its four-check floor is enforced model-side, which is what FR-157 asks; only the comparison and the publication are outstanding | `OQ-651` |

### The five execution found

| # | Finding | §13 verdict | Where it lives |
|---|---|---|---|
| F4 | Nothing revalidates artifacts already stored under a looser shape when a shape is tightened; the failure surfaces on the read path, to a user who did nothing | **Deferred with an owner.** Two real instances: `OQ-547`'s decimal narrowing and this slice's own battery change | `OQ-650` |
| F5 | `test_the_escalated_constraint_disagreements_are_still_unresolved` reads both sides through `.get(...)`, so a keyword present on one side alone compares a value against `None`, is unequal, and reads as *still disagreeing* — a pin can outlive its question silently | **Delivered but untested → now fixed by construction in the successor.** Left standing in the constraint companion rather than fixed mid-slice; `UNRESOLVED_TYPE_DISAGREEMENTS`' companion tests membership before value, and that is proven on four deliberately broken pins | Tombstone in `test_contracts.py`; amended Task 1 commit message |
| F6 | Every layer of the contract guard is scoped to the **intersection** of its two sides, including the completeness check, which defines an eligible schema as one having both — so it is defined over the complement of the problem | **Deferred with an owner.** Nothing is wrong today and the residual is bounded; what is missing is any way to keep knowing that | `OQ-649` |
| F7 | `generate-contracts.py`'s comment beside `peril-structure` still read "No hand-authored Phase-0 counterpart" six days after #133 added one | **Delivered.** Corrected in this slice, with the stale sentence kept beside the correction because the drift is the evidence | `scripts/generate-contracts.py` |
| F8 | `DatasetVersion` diverges from its contract on 22 of 48 paths with every comparison green | **Deferred with an owner** | `OQ-568` |

**F6 is the finding this slice will be remembered for, and it is worth stating plainly.** Task 1
made two sides agree partly by not comparing them, which the plan already suspected. Measuring it
showed the property is not local to certificates: the type comparison intersects paths, the
constraint comparison intersects paths and then keywords, and `test_every_eligible_schema_is_compared`
defines *eligible* as generated ∩ authored. So the guard is silent in **exactly the same way**
whether a shape is one-sided on purpose or by accident, and no reader or test can tell those apart.

The two new slugs demonstrate it on the day they were added. `dataset-version` passes every
comparison — 26 shared paths, zero disagreements — while 22 of its paths are one-sided.
`validation-report` has 24 shared paths, 8 one-sided, and its single genuine disagreement is the
one now pinned.

**Any published count must say which frame it means.** Both of these are true of the same tree:
the guard compares 15 of 15 shapes it defines as in scope, with none unaccounted for; and 21 of
the 36 distinct shapes in the corpus are out of scope by construction.

---

## Where the plan was wrong

The plan is frozen and unedited; these are recorded here.

1. **It predicted that leaving the `UNRESOLVED_CONSTRAINT_DISAGREEMENTS` entry in place would turn
   its companion test red, making removal impossible in the intuitive direction.** Execution
   falsified this: the companion stayed green, because unbinding the type removed `minItems` from
   the model side entirely and `None != 9` reads as *still disagreeing*. The carve-out could have
   been removed on its own, silently, at any time. That is F5, and the accurate statement is that
   the pair stopped being **comparable**, not that it stopped disagreeing. The Task 1 commit
   message was amended to say so.
2. **Task 4 step 1 predicted the merged `contract-guard` would say "13 and two", and instructed a
   stop-and-reconcile otherwise.** It said *twelve* and *14 authored*. Reconciled: the 13/two
   figures describe W32-1b, which had not landed — the peer session branched it off `946725f`
   after this slice began. No assumption was made; the merged figures were corrected to the
   measured 15 and 11.
3. **It listed three findings; execution found five more.** All eight carry a §13 verdict above.

---

## Requirement evidence

| Requirement | Evidence |
|---|---|
| FR-158 | `battery_is_exactly` called from both certificate constructors; tests for missing, unexpected and duplicated names |
| FR-157 | `MetricCertificate`'s four-name battery enforced by name |
| FR-451 | `generate-contracts.py --check` exit 0, 26 generated contracts match the models; `COMPARED_SLUGS` 15, equal to the both-sided set |
| FR-49 | Unresolved as to encoding — `OQ-567`, dispositioned not delivered |

**NFR / enforcement proven on deliberately broken input** (§13): the new
`test_the_escalated_type_disagreements_are_still_unresolved` was run against four bad pins — a path
where both sides agree, a path present on neither side, a path present on the model side only, and
the real pin. The first three go red with distinct messages; the real pin stays green. A check that
has never printed a failure has not been tested, and this one has.
