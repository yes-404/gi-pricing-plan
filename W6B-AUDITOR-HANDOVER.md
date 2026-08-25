# W6b work auditor — handover of open findings

Written 2026-08-25 at stand-down, by the `w6b-auditor` session, against `origin/main` at the
SHAs cited per finding. **Nothing here is a verdict.** Under `CLAUDE.md` §12 the four §13
verdicts belong to the workstream owner; this file is evidence and open findings only.

Placed at the repository root deliberately: `scripts/audit-docs.py` sets `ROOT = REPO / "docs"`,
so a file here is outside its scan and cannot break the gate. It is not a plan and does not
belong under `docs/plans/`. **Delete or relocate it once its contents are absorbed** — it is a
handover, not a durable document.

Each finding states its own limit. Where I did not verify something, it says so.

---

## 1. The platform's single most important rule carries no requirement id

`01-data-management.md` §1.3 (`:42-47`) states, as the document's own "single most important
rule":

> **A Model may only be fitted on a Dataset Version whose status is `validated`.**
> There is no override, no "force fit", and no admin bypass.

**Lines 42–48 carry no FR, NFR or OQ.** Positive control: `:40`, the §1.2 row immediately above,
carries `VR-ACT-14` and `OQ-DATA-4`, so the probe reaches this region.

Restated unnumbered a second time at `02-modelling.md:40` — *"**R1** — Fitting requires a
`validated` Dataset Version. No override (`01` §1.3)."*

**Why it survives every instrument.** The hard-rules blocks are a **mixed population**: R3 →
FR-MODEL-33, R4 → FR-OVR-14, and `06`'s R1 → FR-GOV-11 are all backed. Only the fit gate is not.
An id-derived audit therefore covers the rules on either side of it and is silent about this one.
`FR-DATA-17` governs the transition **into** `validated` — a different predicate; it does not
say a fit requires it.

Verified across three vocabularies (requirement-ese, identifier-ese, positional-ese).

**Disposition:** pre-existing, outside W6b's goal, books to future work. Does not touch the
close.

---

## 2. `02` §5.3's Custom metric library cell — an obligation already repealed with no record

`02-modelling.md:2594` promises *"a link to the metric certificate (FR-MODEL-108)"*.

- **FR-MODEL-108** (`02:226`) is *"create, read, certify, read the certificate, submit for
  approval, and list usage"* — API operations. It carries **no link or view obligation**.
- **§5.3 registers no metric-certificate view** for a link to point at. Controlled: the same
  probe finds the *objective* certificate view at `:2593`, the exact analogue, so it reaches the
  population.
- The cell is **not among FR-OVR-21's seven carve-outs**, so FR-OVR-21 reaches it and the cell is
  prose binding nothing.

**Ordering, verified by the manager:** `946725f` (#157, registers the cell) is an **ancestor** of
`f838662` (#183, lands FR-OVR-21). Same day, cell first.

**Consequence, which inverts the obvious reading:** the obligation is not merely unowned, it is
**already repealed, silently and with no record** — the exact outcome FR-OVR-21's own text says
`CLAUDE.md` §0 forbids (*"a migration clause that misses one repeals it exactly as silently"*).

Note the **W6b-7 plan reaches the right outcome by a different route** — it defers the item as
finding 4 — but on the **wrong record**: it treats the obligation as live. Two docs artifacts
disagreeing is §0's resolve-never-silently-reconcile case.

**Disposition:** maintainer's, not a W6b blocker. Should not be discovered at the close.

---

## 3. `ingestion.py` tells users the remedy set is closed at three

`backend/.../ingestion.py:517-519` (at `f902e3a`) says reclassification *"is **the** other way
through"* — definite article, singular, asserting the enumeration is complete at three: drop,
pseudonymise, reclassify. **FR-OVR-9 specifies a fourth** — a passthrough key excluded from all
Factors.

Two consequences, independent of how the FR-OVR-9 open question resolves:

1. If the fourth route is intended design, **the running system tells users it is unavailable.**
   A §0 code-vs-spec divergence **no test can fail on**, because the divergence is in prose.
2. The only "keep the column" route the platform offers is **reclassification, the least safe of
   the four**: FR-OVR-9's clause 3 keeps the classification and constrains use, while
   reclassification **deletes the classification and constrains nothing**. The error text
   normalises it as *"an audited change"*.

**Disposition:** outside W6b's goal, no urgent fix, books to future work.

---

## 4. FR-MODEL-102's slug rule holds only on the worker path

**Filed as `OQ-MODEL-34` (PR #176) by the then-lead. I have not verified that filing against the
artifact.** What follows is my evidence, which I did verify.

**The defect is internal inconsistency.** FR-MODEL-102 (`02-modelling.md:200`) asserts
unconditionally that *"the surrogate's `model_family_slug` is the source model's own family slug
with `-approx` appended"*, but its enforcement clause is scoped — refused by name *"before the
transparency Job spends any compute fitting it"*. The requirement names the Job in its
enforcement half while stating the property universally.

**Still true:** the headline holds via the type-level iff at `model-schema/modelling.py:1118`.
You can tell **that** a model is a surrogate; you cannot find **whose**.

Evidence, verified by me at `origin/main` and independently re-verified by the then-lead:

- The create path is `fit_model → enforce_complexity → reserve_model`. It **never** checks
  `response_column` or the slug. `modelling.py:426` persists `model_family_slug=spec.model_family_slug`
  verbatim, flushed before any Job is queued.
- `validate_spec`'s **only** caller is `api/models.py:688` (`POST /model-specs/validate`), which
  persists nothing. **The `model_specs.py:232` surrogate carve-out is *not* the gap** — it shows
  intent only. I originally mis-cited it as the gap and corrected it.
- **Decisive structural proof — sibling guards in one file.** The interval guard's mismatch list
  has **four** fields including `model_family_slug` (`modelling.py:583`); the approximation
  guard's has **three**, omitting it (`:670-672`). The field is **absent, not hidden**.
- No Model Family entity exists. The slug is a bare `str` (`model-schema/modelling.py:824`)
  behind `String(64)` with no pattern — while a constrained `Slug` type exists and is used at
  `objectives.py:778`.
- **No worker-only seam:** worker and API call the same `reserve_model`, whose audit hardcodes
  `source=JobSource.API`, while `modelling.py:831` elsewhere does
  `JobSource.SYSTEM if job_id else JobSource.API`.

Three options: (a) enforce the suffix on create; (b) scope the FR to the Job; (c) derive the slug
server-side for any spec carrying `approximates_model_id`.

**My two contributions, which must survive into the OQ:**

1. **Option (c) resolves the *slug* half only.** The **version half is untouched** —
   `approximates_model_id` has no companion version field (`interval_for` has `model_version`),
   and `/models/:slug` defaults to latest, so a derived link still lands on the source family's
   *current* version. **A companion version field is needed regardless of which option wins.**
2. **Option (c) costs no extra query.** `_refuse_mismatched_approximation` is called at
   `modelling.py:377` and already fetches the source spec; the slug is written at `:426`. Same
   function (`reserve_model`, `:340`), same transaction.
3. The 64-character *"refused by name"* limit **must move with any derivation**, or an over-long
   derived slug hits `String(64)` at the DB layer instead of being refused by name.

**To verify at the close:** open `OQ-MODEL-34` and confirm (i) it exists and #176 merged;
(ii) option (c) reads *"resolves the slug half; the version half needs a companion field
regardless"* — **not** "resolves the link gap"; (iii) the no-extra-query line is present; (iv) the
64-character move-with-derivation note is present; (v) the `model_specs.py:232` reading trap is
recorded; (vi) **no option was silently picked** (§0).

---

## 5. The W32 closure record labels the wrong SHA as closing

`docs/roadmap.md:707` calls `60f6e46` *"the closing SHA"*. It is the last **feature** SHA
(`feat(w32-7)`, #164). The **closing** commit is `e2ae7c6` (#165), which wrote the record.

Proof: the closure heading returns **0** hits at `60f6e46` and **1** at `origin/main`; the file
is 4880 lines at `60f6e46` and 5564 at `origin/main`.

**Keep this narrow.** The citation *scheme* is correct and must not be touched: citing the
pre-record tree is deliberate, and the passage that **refuses to write down its own line-number
offset** — because a self-referential offset is a fixed point — is the most careful thing in the
file. **The defect is one appositive at `:707`.** A fix aimed at the wrong half would damage a
good passage.

---

## 6. Two user-visible prose defects in `validate.py`, with **opposite** dispositions

Both are rendered verbatim by `RuleResultRow.vue`. Verified at `8673bab`.

### 6a. `validate.py:1079` — survives the OQ-OVR-11 sweep untouched

```
detail=f"mean severity is {severity:,.0f} minor units"
```

Missed by every instrument on **two independent grounds**: `audit-docs.py` check 12 matches
`"(\w*_minor)"\s*:\s*(-?\d+\.\d+)` over markdown and schemas, and this is (i) Python source and
(ii) carries **no `_minor` token at all** — *"minor units"* is two words with a space.
FR-OVR-20 governs *names*; a formatted string is not a name.

**Substantively wrong:** *"minor units"* asserts money for **mean severity**, which OQ-OVR-7
settled as a statistic on 2026-08-17 and which FR-OVR-7 calls *"the one classification this
requirement is surest of"*. `{:,.0f}` renders it formatted as an amount.

**Disposition: OQ-OVR-11's option (a) — type the payload — is a ZERO fix here, not a partial
one.** Nothing in the rename sweep touches this string, because it carries no name. **It needs
its own line item.**

### 6b. `validate.py:987-990` — dies with the sweep, no line item needed

```
detail=f"{large.height} claim(s) at or above {absolute:,.0f} minor units — ..."
```

The filter at `:973` is `values.filter(pl.col(column) >= absolute)` on the raw float while the
display rounds, so the printed figure is not the cut.

- **Branch-specific.** `absolute` is fractional only in the quantile branch (`:959-961`,
  `interpolation="linear"`). The declared branch (`:970`) takes an integer minor-unit threshold,
  so `:,.0f` is exact.
- **Severity depends on the column's dtype.** On an **integer** minor-unit column the true cut is
  `ceil(absolute)` while `:,.0f` rounds to *nearest*: a fraction below `.5` prints one **below**
  the cut and names a value no row was tested against; a fraction above `.5` coincides with ceil
  and is **correct by coincidence**. On a **float** money column — reachable, the integer dtype
  being unenforced — the cut is `absolute` exactly, so **both halves diverge**. My original
  "half the values" claim silently assumed integer dtype; an unenforced invariant was doing
  load-bearing work.
  **Trap: a reproduction picking a `.6` fraction goes green and reads as disproof** on an integer
  column. The control must come from the sub-`.5` half.
- **Not an independent prose bug.** The divergence exists only because the filter reads an
  unrounded float while the display reads a rounded one. Round `absolute` itself — either
  direction — and the string becomes correct automatically. **FR-OVR-7 (`00:213`) already
  requires that rounding**, noting the check's own verdict moves with the direction. So this and
  the OQ-OVR-11 type fix are **one decision**.
  **Load-bearing condition:** the rounding must be applied to `absolute` **before the filter**,
  not only to the published payload. If the fix touches only the payload, the string stays wrong.

---

## 7. `W6b-13b`'s phantom `W6b-13a` — half discharged, inert

`docs/plans/2026-08-24-w6b-13b-catalogue-chain.md:84` says the map re-cut `W6b-13` into
**`W6b-13a`/`W6b-13b`**. `W6b-13a` exists nowhere: the revised map kept `W6b-13` (`:162`)
alongside `W6b-13b` (`:163`). **The parent id was retained, not dissolved**, which makes the
plan's staleness argument weaker than stated.

The other half **is discharged by the work itself** — FR-DATA-53 and FR-DATA-54 now both name
`W6b-13b` and read *Fixed / Built 2026-08-24*.

**No remedy required.** The plan is frozen at its date, and the erroneous premise drove a correct
action. Recorded as an accuracy note only; **not grounds to edit a frozen plan.**

---

## 8. Instrument notes — repo-wide, held for the close

These are not defects in anyone's work. They are ways an audit gets a **confident wrong answer**
here, each observed in this session.

1. **A `expect(`-count sweep scores every `*.test-d.ts` file zero.** `predictions.test-d.ts`
   contains **no** occurrences of `expect(`; its assertions are `expectTypeOf<T>()` and
   `assertType<T>()`. Such a file reads as untested to any assert-counting instrument.
2. **§5.1 route tables put the verb and the path in separate cells** —
   `` | `POST` | `/api/v1/custom-objectives/{id}/submit` | `` — so **any pattern spanning both
   matches nothing there** and everything in the surrounding prose. My own sweep returned a
   plausible **six** routes where the spec declares **eight**: not an undercount of the
   population, a complete count of a different one. Grep §5.1 **by path fragment alone**.
3. **A control drawn from wherever the probe already succeeds proves only that it runs.** It must
   be an instance you know the probe **must** catch, chosen from the authoritative artifact
   before running it.
4. **`req-coverage.py` cannot see the frontend at all**, so the whole Vue surface is dark to the
   instrument a close normally leans on.
5. **An id in a test file is a locator, not coverage.** In this repo ids land in docstrings
   essentially always, so an id-level sweep reads the narrative register by construction. Read to
   the asserts.
6. **A test written to close a citation gap closes the citation by construction** — the id in the
   title is the one thing guaranteed to pass.

---

## 9. Frontend evidence gathered for the close

At `7a9741c` unless stated. **`req-coverage.py` cannot see any of this.**

- **8 of the revised map's 17 rows have a feature commit** (`4a`+`4b` = row 4, `5a`+`5b` = row 5).
  Outstanding: 6, 7, 8, 10, 11, 11b, 12, 13, 14. *(Rows 7 and 8 have since moved — W6b-7 merged
  as #223 and W6b-8 was in build at stand-down.)*
- **All 13 views have a test file — 13 for 13.** Leading with this rather than only the gaps is
  deliberate: an auditor reporting only defects is a biased instrument.
- **3 of 31 components have no test file:** `AcknowledgeDialog`, `RuleResultRow`,
  `ValidationBanner`. **Structural only** — file layout, not asserts; a view test may exercise
  them. Two converge with findings above: `ValidationBanner` implements FR-OVR-21's carve-out 1
  (dark to two instruments at once), and `RuleResultRow` is what makes finding 6a user-visible.
- **Element-3 evidence, the strongest the frontend has:** the `.test-d.ts` type tests
  (`SpecProblemList`, `StatusBadge`, `objectiveVocabulary`, plus `builtinObjectives`). Two of
  those are not components — they guard the custom-objective surface `CLAUDE.md` §3 calls
  first-class.
  **Verified they run:** `frontend/vitest.config.ts:45-49`, `typecheck.enabled: true`.
  **Cite the config comment, not a summary** — it carries the completed broken-input proof:
  *"`expectTypeOf` is erased at runtime. Without this block a type assertion is a test that can
  never fail — proven by asserting `exposure_years` is a `number` and watching it pass."*
  **Agreed record wording:** *"enforced twice, by `vitest` typecheck and by `tsconfig.app.json`'s
  include; verified by configuration, not by mutation."* The mutation was declined and booked
  optional pre-close; **it is not the auditor's to run** — editing config to prove an audit point
  changes the thing under audit.

### W6b-6b (`ccd93c7`, #219) — read-to-asserts pass

Manager's verdicts (theirs, §12): **FR-MODEL-63 and FR-MODEL-98 are both delivered but
untested.**

- **FR-MODEL-63** — the slice's headline requirement — is **comment-only**. Its sole occurrence
  is an in-test comment at `PredictionUncertainty.test.ts:127`, whose enclosing test asserts only
  `expect(screen.getByText(/no reason/i))`. Its predicate is *expectation **plus** an uncertainty
  measure, per family*. The expectation-is-shown property **is** asserted, at `:105` — but cited
  to **FR-MODEL-93**. Discharged by a docstring and its neighbour's test.
- **FR-MODEL-98** — predicate is *"exactly **one** interval kind"*. The tests assert what the
  kind *says* but **nothing pins the enumeration**. `predictions.test-d.ts` has exactly four
  blocks: `UnavailableReason` exhaustive, `UncertaintyBasis` exhaustive, FR-101's exclusions, one
  negative. **No `UncertaintyKind` enumeration test.** The asymmetry is the control — the only
  exhaustiveness predicate without an exhaustiveness test, both siblings having one.
- Seven hold, FR-MODEL-100 strongest ((ii) and (iii) each asserted twice, once over whole rendered
  copy with a `.not.toMatch` guard).
- **Worth preserving:** `predictions.test-d.ts:26` deliberately asserts the type **cannot**
  express FR-101's exclusions, with the behaviour covered at runtime instead
  (`PredictionUncertainty.test.ts:76-82`). Recording what a type *fails* to guarantee is the
  honest form.
- **FR-MODEL-92 was not a W6b-6b citation** — a file-scoping artifact of my own probe. It sits in
  the *shared* router test over the `model-backtest` route. Withdrawn.
- `predictionInputs.test.ts`: 5 tests, 7 asserts, **no requirement id at all** — invisible to an
  id-derived pass, not a defect.

**`PredictionView` is unreachable.** `model-predict` appears only at `router/index.ts:102` and in
its own router test — no `RouterLink`, no `router.push`, no path-string navigation. Control:
`RouterLink` is the idiom (`App.vue:9-35`, `ModelRefLink.vue:14`). **Filed by the manager as
instance two of a class** (`/models/compare` is instance one); the class sweep is theirs.

---

## 10. Two checks queued against work that had not landed at stand-down

1. **FR-MODEL-63's new test.** Criteria **pre-registered before the test existed**, and ratified
   by the manager against `02:278` and its blockquote `:309`, so the judgement cannot be fitted
   to whatever arrives. FR-63 is a **conjunction** — expectation **plus** an uncertainty measure,
   per family, GBM's `unavailable` branch included.
   **FAIL if:** only the expectation is asserted (that is FR-93's `:105` renamed); only a reason
   or `/no reason/` is asserted (that is the existing `:127` test); the id lives only in the
   title; one family is exercised and the other left to a sibling's test; or the two limbs are
   asserted in **separate** tests — a conjunction is not satisfied by two single-limb asserts.
   **Do NOT fail on:** the absence of a server-side guarantee. `reason` is contract-nullable, so a
   component test proves the *view* renders a reason, never that the server always sends one.
2. **W6b-8's peril absence test.** See finding 11 below; the test must fail on a rendered **`0`**,
   not only on a rendered number.

---

## 11. W6b-8's own verification step is disarmed by its own Task 2

Raised pre-build and adopted by the manager; recorded here because the reasoning is worth keeping.

**The half checks out.** FR-OVR-21 (`00:227`) closes by resting its *contract-is-the-floor* half
on the `02` §5.3 Peril structure library precedent **alone**. The load-bearing negative is
**triply specified**: FR-MODEL-127 (`02:231`) says `usage_count` *"holds for those same two
libraries and **not for the peril list**"*; §5.1 `:1763` omits it where `:1748` and `:1756` carry
it; `02:2621` says **"No usage count"**; and `docs/contracts/openapi/generated.json:21309`
documents the absence. Contract, requirement and cell agree.

**The gap.** The plan's Step 2 (`docs/plans/2026-08-25-w6b-8-peril-structure-views.md:802`) is:

```bash
grep -rn "usage_count\|usageCount" frontend/src/views/PerilStructureLibraryView.vue
```

with `:806-807` treating a hit as proof the precedent is contradicted. But `usageCount` is not
rendered in a view — it is rendered in the shared component (`ArtifactLibraryTable.vue:19`, and
`:70` `<td>{{ row.usageCount }}</td>`) — and **Task 2 (`:501`) widens that component to a column
set**, so the peril view will pass a column config and contain the token **by construction,
never**.

**So Step 2 returns "no output" whether or not a usage-count column renders.** Its success
condition is satisfied by the refactor rather than by the property — a structural probe on the
wrong file, disarmed by the remedy of the finding immediately beside it (Finding 1, `:137`). The
manager added that it is vacuous **today** as well, since `PerilStructureLibraryView.vue` does not
yet exist: §13 rule 3, never printed a failure, therefore never tested.

**The enforcement that works is already listed and is not the grep:** the absence test at `:393`.
It should assert that **no usage column renders for the peril column set** — behaviour, with a
failing case.

**The equivalence the guard assumes, and the concrete failure mode:** `MetricLibraryView.vue:28`
and `ObjectiveLibraryView.vue:36` both carry `usageCount: <artifact>.usage_count ?? 0`, so the
token-in-view equivalence is real for the two libraries that legitimately have it — and Task 2
breaks it for perils. The idiom is **`?? 0`**: copied to perils, an undefined quantity renders as
**`0`**, which is *worse than blank* because it asserts a count exists and is zero, while
FR-MODEL-127 says the quantity is undefined there (a Model Spec cannot reference a Peril
Structure; the reference runs the other way). `usageCount` appears in **4 non-test files, 6
including tests**.

---

## 12. Standing method notes for whoever runs the close

- **Re-derive the obligation set at the close.** My earlier derivation is **superseded, not a
  baseline** — the set moved twice (the 08-24 slice-map re-cut, then FR-OVR-21/#183 unblocking
  `W6b-1b` and `W6b-9`), and again as slices landed.
- **Audit `origin/main` after an explicit `git fetch`,** never the shared checkout, and **quote
  the resolved SHA beside every answer.** The shared checkout was stale at `e2ae7c6` for this
  entire session — a ref containing none of W6b. A stale ref **manufactures findings against the
  work**, because absence reads as non-delivery.
- **The closure standard has five elements**, not one (`docs/roadmap.md`, the paragraph ending
  *"A closure record without those is an assertion, not evidence"*): every deliverable re-verified
  against its row; the gate run locally; **each new check proven to fail on broken input**; NFRs
  **measured** against their budget; and **what was *not* delivered stated explicitly**. The last
  two are the ones that go missing.
- **A §14 plan review runs at the same moment as the close**, and its output is a proposal with a
  maintainer acceptance line — never an edit.
- **Closure records are per workstream, never per slice.** "Has a feature commit" is the only
  per-slice predicate available; it is a trigger, not evidence of completeness.
