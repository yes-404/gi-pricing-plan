# W6b-5b — The Suggestion Panel and the Workbench Remainder — Implementation Plan

**Slice:** `W6b-5b` — `02` §5.3's factor workbench remainder: intent and monotonic-direction
controls, interaction suggestions, inline one-ways.
**Base:** `8d0dcf4` on `main` — W6b-5a (#209) merged, its example-test defect fixed (#210).
**Owner:** `w6b-executor`, arbitrated by `w6b-manager` 2026-08-25.
**Map row:** [`2026-08-24-w6b-slice-map-revised.md`](2026-08-24-w6b-slice-map-revised.md):153
(`W6b-5`), split into `5a`/`5b` at backend-versus-panel on 2026-08-25.

**Highest ids in use: `FR-MODEL-128`, `OQ-MODEL-38`, `OQ-OVR-15`, `OQ-PLAT-16`.**
This plan proposes **`OQ-MODEL-39`**, **`OQ-MODEL-40`** and **`OQ-MODEL-41`**, and no
requirement. Next free after them: `OQ-MODEL-42`.

**This slice carries FR-MODEL-128's owner clause** — description-anchored to "the slice that
builds the factor workbench's suggestion panel". `W6b-5a` built the backend half and recorded
so in the requirement's own row; the discharge is across both.

---

## Global Constraints

- **No backend change and no `model-schema` change.** Three findings below want one and none
  may have it here.
- **`docs/roadmap.md` and `docs/plans/` are untouched.**
- **A suggestion is never an addition** (FR-MODEL-79). Adding an interaction stays an
  authored decision carrying an intent and a rationale.
- **No threshold anywhere** (FR-MODEL-128): ranked evidence, never an admission test.
- The gate runs both halves, every exit code read separately (§11).

---

## 1. Scope, derived from the specification first

`02` §5.3:2587 names five things for `/factors/:datasetVersionId`. **The cell is prose** —
FR-OVR-21 makes a §5.3 cell non-binding unless it declares itself exhaustive, and the factor
workbench is not among the seven carve-outs. Scope is the requirements; the cell indexes them.

| Cell item | State |
|---|---|
| Column list with profile one-ways (`01` FR-DATA-26) | **missing** — this slice |
| Banding editor with live band stats | built |
| Grouping editor with relativity-ordered levels | built |
| Monotonic-direction and **intent** controls | **missing** — this slice |
| Interaction suggestions ranked by SHAP strength, with FR-MODEL-128's ratio beside each | **missing** — this slice |

**Building the intent control discharges an already-recorded §14 q4 finding.** FR-MODEL-116
records that §5.3 claims an intent control the built view does not have; `git grep intent --
frontend/src` outside `generated/` returns zero.

**The cell is not the whole of §5.3, and the rest of it does bind.** `02` §5.3 also carries
an unnumbered **Interaction requirement** paragraph (`:2599-2603`): the banding and grouping
editors must show an edit's consequence *before* it is saved. FR-OVR-21's rule is
**cell-scoped**, so it does not reach a paragraph, and the seven carve-outs name `01`'s
equivalent paragraph rather than `02`'s. So it binds — and it is **outside this slice**,
because it governs the banding and grouping editors, which are built. Stated because "scope
is the requirements; the cell indexes them" is right for 5b and a reader could take it as
disposing of all of §5.3, which it does not.

---

## 2. Findings

### F1 — the view is scoped to a dataset version; suggestions live on a model

`/factors/:datasetVersionId` addresses a Dataset Version. Interaction candidates live on a
per-**Model** transparency artifact, and `GET /models` filters by `family`, `status`,
`cursor` and `limit` — **not** dataset version. `Model.dataset_version_id` is a top-level
field, so a client can filter.

**Filed as `OQ-MODEL-40`, cross-referencing `OQ-MODEL-35` as its sibling.** These are the
same shape — a list route whose filters omit the axis a view needs — and they are the only
two: a sweep of `docs/` found `OQ-DATA-9` and `OQ-OVR-15` to be missing *fields* rather than
a missing filter *axis*, `02`:1747 a parameter-name mismatch already fixed, and
`OQ-MODEL-37` a missing machine-readable set. An earlier draft of this plan called F1 the
third instance and declined to file on that basis; the count was wrong and so was the
conclusion.

### F2 — `FactorIntent` publishes four arms and the platform honours two

The generated enum is `risk | control | offset | diagnostic`. FR-MODEL-116 supersedes
`offset` and FR-MODEL-120 supersedes `diagnostic`, both **keeping the arm in the published
contract deliberately**, on a layer argument: offsetness and diagnosis are properties of one
*fit*, while `Factor.intent` belongs to a Factor defined against a Dataset and reused by
every spec naming it.

So the enum will **never** narrow to match. A control keyed naively on it offers two intents
the platform will not honour, and waiting for the type to say which are live is waiting for
ever. This is the mirror of W6b-4b's error: there the plan offered fewer statuses than the
fit accepted; here the enum offers more than the requirements permit.

**And "let the backend refuse" is not a fallback that exists.** `POST /factors` accepts all
four — `REFUSED_FACTOR_INTENTS` has **zero** references anywhere under `backend/`, and the
only refusal is `resolve_factors` (`pricing-core/modelling/factors.py`:162), on the
fit/predict/diagnostics/transparency path. A superseded intent is therefore accepted, stored
and audited, and detonates at fit.

### F3 — an all-`null` set of ratios is indistinguishable from a pre-5a artifact

`TransparencyArtifactRow.payload` stores the artifact whole as JSONB and is insert-only, so a
pre-5a artifact carries no `holdout_strength_ratio` key while a post-5a one carries `null`
where no quotient exists. `to_artifact` validates the payload into `TransparencyArtifact`
before it leaves the platform layer, so both reach the panel as `None`.

Narrowed and verified: `_ratio` returns `None` iff the pair's in-sample `strength` is `0.0`,
because the sole production call passes a dict. **Any candidate carrying a float proves the
artifact post-dates 5a**; only an all-`null` artifact is undecidable. That reading rests on
the **call site, not the type** — nothing in `_ratio`'s signature stops a future path passing
`None`, which would produce an all-`null` artifact with positive strengths and read as pre-5a.

Filed as **`OQ-MODEL-39`**.

---

## 3. Decisions

### Decision 1 — the intent control is on the creation path only, and there is no edit

**A Factor's intent is immutable.** `Factor` is `frozen=True`
(`model_schema/modelling.py`:129); `/factors` carries **GET and POST only**, no `PATCH` or
`PUT`, and the contract agrees; there is no `FactorUpdate` and no `update_factor`. A `POST`
with an existing slug allocates version N+1 (`platform/modelling.py`:229-235, **FR-MODEL-7**).

So the control sets intent **at creation**. There is **no edit control on an existing
Factor**, and deliberately **no "re-version to change intent" affordance**: re-versioning
changes what every future model fits on, which is a separate capability and not this slice's.

### Decision 2 — how the intent control is typed (F2)

**A `Record<FactorIntent, Label>` over all four arms**, so the compiler pins exhaustiveness
against the generated union — a new arm becomes a **build error**, not a silent omission.
Then a **hand-written refused set**, `satisfies readonly FactorIntent[]`, pinned by a
text-reading test against `REFUSED_FACTOR_INTENTS` (`pricing-core/modelling/factors.py`:63).
**Offered = the Record's keys minus the refused set.**

The hand-written fact is then the *refusal* — which is where the permanence lives, and which
has an **executable authority to pin against**. A hand-written *permitted* pair would have
neither: prose in `02` is the wrong pin, and a newly live arm would vanish from the picker
with no test firing.

The generated union is a type and carries no runtime values, which is why this is a `Record`
and not a derived array.

**No CI change is needed**: `frontend.yml` already carries
`packages/pricing-core/src/pricing_core/modelling/**` on **both** triggers — the same path
`builtinObjectives.test.ts` relies on — so `factors.py` is covered. That also means
**`OQ-MODEL-37`(c)'s prerequisite is already shipped**, recorded as a dated append in both
its mirrors by this slice.

### Decision 3 — how the panel reaches a model (F1)

**A model selector**, populated by `GET /models` filtered client-side on
`dataset_version_id`, honouring a `?model=` query param when present so arriving from model
detail preselects.

**The interim mirrors `OQ-MODEL-35`'s rather than inventing one.** The same cursor pagination
applies, so a client-side filter over one page renders "no models" while matches sit on a
later page — indistinguishable from none, which is the exact failure that question exists to
record. So: page to a stated bound and **surface the limit visibly** when a cursor survives
it. **No silent filter.**

**`flags` is not read off the list**: `list_models` returns `flags: []` for every row by
design (`api/models.py`:562-566).

### Decision 4 — which model's candidates the panel shows by default

Named rather than left implicit. **The most recently created model on that dataset version**,
with the selector letting an actuary choose another.

Highest-status was the alternative and is rejected: it surfaces an older analysis while newer
work exists, and an actuary opening the workbench has usually just fitted something. Status
belongs in the selector's labels — where it informs the choice — not in the default, where it
would silently override a fresher artifact.

**The mechanism is the route's ordering, not a field, and that is the fragile part.**
`Model` has thirteen fields, is frozen with `extra="forbid"`, and carries **no timestamp of
any kind** — `created_at` exists on `ModelRow` but does not reach the contract. What makes
"most recent" available at all is that `list_models` orders by `ModelRow.id.desc()` and ids
are UUIDv7, whose leading 48 bits are a millisecond timestamp, so the route returns
newest-first.

Nothing in the type system defends that. A client-side `sort`, a `Map` or `Set` round-trip,
or fetching pages out of order silently loses the ordering and degrades the default to an
arbitrary model — with no error anywhere. **So the client-side filter must be
order-preserving, and a test pins it**: the assertion is that the filtered result's order
matches the response's, not merely that it contains the right models.

Two ids minted in the same millisecond order arbitrarily with respect to each other
(`ids.py`:36-37), so at millisecond resolution the default is ambiguous. That is acceptable
here for the reason that file gives — nothing derives ordering *within* a millisecond — and
it is recorded so a later reader does not mistake the ambiguity for a defect.

### Decision 5 — what the panel says when every ratio is `null` (F3)

**Wording true of both facts** — "not available for this artifact", never "no structure
found" — with a rebuild offered as an action but **not promised to yield a value**, since a
genuine all-zero artifact recomputes to all-`null`. A per-candidate `null` beside floats needs
no such care: that pair had zero in-sample strength, which is a finding and can be said
plainly.

---

## 4. Interactions this slice touches but does not resolve

1. **`OQ-MODEL-38`** — the ratio's null is below `1` because the denominator is a selected
   maximum. The panel must not imply `1` is the neutral point; that interpretive sentence is
   FR-MODEL-128's and the maintainer's.
2. **`OQ-MODEL-41`** files the intent surface as **one** question with two named surfaces:
   creation accepts superseded arms, and the contract publishes no live/superseded
   distinction. One remedy space, so one question.
3. **FR-MODEL-128's rebuild clause** stays unsatisfied with an owner, recorded in 5a.
4. **The row cap is untested** — "delivered but untested" for the closure record.
5. **§5.3's Interaction requirement paragraph cites FR-MODEL-15, which does not carry it —
   but a numbered requirement does.** FR-MODEL-15's predicate is what a Grouping *stores*
   (method, parameters, source and target Level statistics, change in fit) and says nothing
   about showing a consequence before save. Review proposed that the obligation therefore
   either needs a number or should be struck; **checked, and neither is so**. **FR-MODEL-83**
   carries it explicitly — "§5.3's interaction requirement — that an edit's consequence is
   visible *before* it is saved — is otherwise unmeetable" — and was added 2026-08-15 (W5)
   for that purpose, giving Bandings and Groupings an evaluate-without-persisting route. The
   paragraph's FR-MODEL-15 citation is narrow and correct as far as it goes: FR-MODEL-15 is
   the source of the deviance/df evidence being shown, not of the obligation to show it. So
   there is no gap and nothing to file. Recorded because the opposite reading is a plausible
   one that a future sweep will reach again.

---

## 5. Tasks

1. **Inline one-ways** on the column list, read from the Profile the view already loads and
   never computed in the browser. The tighter authority is **FR-DATA-26**'s "are computed
   once, here"; **FR-DATA-27** is cited alongside it but its predicate is recomputing *a
   profile*, which is a wider claim than this one needs.
2. **Intent and monotonic-direction controls** on the creation path (Decisions 1 and 2),
   with the refused-set divergence test against `factors.py`.
3. **The model selector** (Decisions 3 and 4).

   **What is reused is the pattern, not the function.** `listObjectives`
   (`api/objectives.ts`) is not a generic composable: it hard-codes the `/custom-objectives`
   route, the `ObjectivePage` response type, the `CustomObjective` item type and a single
   `status` axis, and `OBJECTIVE_PAGE_CAP`'s name and doc bind it to objectives and to
   OQ-MODEL-35's applicability problem. What transfers is the **discipline** — page to a
   stated bound, and return truncation *in the return type* rather than logging it, so a
   caller cannot fail to handle it.

   So: **extract a generic paging helper both callers use** — preferred, since two callers
   is where extraction pays and the shape is now known from a second instance — or, if that
   proves not small, write a sibling with **its own cap constant**. Either way
   `OBJECTIVE_PAGE_CAP` is **not** imported into a factor path: a constant whose name says
   "objective" appearing in model paging reads as deliberate to whoever finds it next.

   The selector's filter is order-preserving and tested as such (Decision 4).
4. **The suggestion panel** — ranked by strength, ratio beside each, no threshold, and
   "add as an explicit Factor" as an authored action carrying intent and rationale
   (FR-MODEL-79). Decision 5's wording for the all-`null` case.
5. **`OQ-MODEL-39`, `OQ-MODEL-40`, `OQ-MODEL-41`** in both mirrors, plus the dated append to
   `OQ-MODEL-37` recording that (c)'s CI prerequisite is shipped.
6. **The gate**, §13 mutations, PR, CI read per-workflow, merge verified by state.

---

## 6. What would make this plan wrong

1. **If §5.3's cell is later declared exhaustive.** It is prose under FR-OVR-21 today.
2. **If `GET /models` at scale makes Decision 3 untenable.** The bound makes truncation
   visible rather than silent, but a workspace with thousands of models would show a
   selector honestly incomplete on every visit — which is `OQ-MODEL-40`'s point.
3. **If re-versioning to change intent is expected of this slice.** Decision 1 excludes it
   as a separate capability; a maintainer who reads §5.3's "intent controls" as including
   re-version would scope it back in.
