# W6b-8 — Peril Structure Library and Detail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the two Peril Structure views `02` §5.3 registers — the library at
`/peril-structures` and the per-structure detail at `/peril-structures/{id}` — against backend
routes that already exist, so a pricing actuary can find a structure and read its composition,
its large-loss treatment and its reconciliation verdict.

**Architecture:** Frontend-only. Five backend routes are built and registered
(`backend/src/app/api/peril_structures.py`, `main.py:117`); nothing here needs a backend or a
spec change. A new API module `frontend/src/api/perils.ts` wraps the two reads, the library
reuses W6b-7's `ArtifactLibraryTable` after that component is widened to a column set, and the
detail view composes three panels over `PerilStructure`'s generated type.

**Tech Stack:** Vue 3 `<script setup lang="ts">`, vue-router function-mode props, Pinia not
required, Vitest + `@vue/test-utils`, types generated from OpenAPI into
`frontend/src/api/generated` (never hand-written).

**Spec:** [`docs/specs/02-modelling.md`](../specs/02-modelling.md) — §3.9 (FR-MODEL-58..61,
74), §4.10 `PerilStructure`, §5.1:1736-1740, §5.3:2595-2596.

**Precondition — W6b-8 executes after W6b-7.** Task 2 modifies
`frontend/src/components/ArtifactLibraryTable.vue`, which W6b-7 creates and which does not
exist on `main`. This is the correct cut rather than an inconvenience: `CLAUDE.md` §2 forbids
defining a shape twice, and a second library table built to avoid the wait is precisely the
divergence that rule names. The plan may be reviewed and merged before W6b-7 builds — a plan is
the design step — but its execution is ordered. Trap 1 gives the executor the one-command check.

---

## Global Constraints

Copied verbatim from the specs; every task's requirements implicitly include these.

- **Never hand-write an API type.** `frontend/src/api/generated` is VCS-ignored, generated from
  `docs/contracts/`, and **cannot be cited as evidence**. Import
  `components["schemas"]["PerilStructure"]`; do not restate a field list.
- **Money is integer pence/cents, or Decimal in the rating path — never float** (`CLAUDE.md`
  §7, FR-OVR-7).
- **Vue 3 Composition API with `<script setup lang="ts">` only** — never Options API, JSX, React.
- **A static segment outranks a dynamic one from either position**
  (`frontend/src/router/index.ts:96-98`); tests assert *resolution*, not declaration order.
- **`usage_count` must not appear on a peril row.** FR-MODEL-127: the count is of Model Specs
  referencing the artifact, the reference runs the other way for a Peril Structure (§4.10), so
  it is *"undefinable on a peril row rather than merely unimplemented"* and *"an implementation
  must not invent a peril usage count to make the three shapes symmetric."*
- **FR-OVR-21 is not a licence to drop an item.** A view is an obligation because it has a row
  in a §5.3 table, not because a requirement names it (`02`:2647 — *"Forty-seven of the fifty-one
  registered views have no FR"*). FR-OVR-21 decides whether a *listed affordance* binds, never
  whether the row does. Every cell item below carries a §13 verdict and an owner.
- **The contract is the floor** (OQ-MODEL-15, decided 2026-08-21). Anything a view needs beyond
  the generated contract is a **new requirement raised at build time**, brought to the manager,
  never a silent addition.
- **Every "Expected: FAIL" below names its cause, and the cause is the assertion.** A test that
  fails for a different reason than the one written has **not** confirmed the step, even though
  the red is the same colour — treat it as a defect in this plan and say so, rather than
  proceeding. `docs/plans/README.md` records the episode: a step predicted a 422, got one, and
  the status hid a second fault the plan itself had introduced.

---

## Scope, derived from the specification

Derived from `02` §5.3 and §5.1 first, then evidenced — never from the slice map, whose row for
this slice is one line and, per the manager, the stale side.

| Requirement | What it binds here |
|---|---|
| **FR-MODEL-58** | Per-peril `frequency × severity` or `burning_cost`, **model references pinned by version**; the risk premium is the sum over perils. |
| **FR-MODEL-59** | Large-loss handling per peril — `none`, `capped`, `separate_model`, `flat_loading` — *"recorded with its calibration evidence."* |
| **FR-MODEL-60** | Coherence: **every peril either modelled or explicitly excluded with a reason**; modelled burning cost reconciles to observed within a declared tolerance; the reconciliation is persisted. |
| **FR-MODEL-61** | The structure is an approvable artifact in its own right, with its own lifecycle. |
| **FR-MODEL-74** | The reconciliation **accounts for the treatment** — modelled cost is compared *after* restoration, and the treatment is stated alongside. |
| **FR-MODEL-90** | `GET /peril-structures/{id}` returns the structure with its reconciliation or a 404 naming it; `POST /{id}/submit` moves `reconciled → review`. |
| **FR-MODEL-127** | `GET /peril-structures` lists, cursor-paginated, filterable by `status` and `slug`. **No `usage_count` on the peril row.** |

### The two §5.3 cells

| Cell | Route | Contents, verbatim |
|---|---|---|
| `02`:2595 Peril structure library | `/peril-structures` | *"List with status and slug, each row linking into the per-structure detail view below. Backed by `GET /peril-structures` (FR-MODEL-127). **No usage count** — that requirement's count is of Model Specs referencing the artifact, and the reference runs the other way for a Peril Structure (§4.10), so the column is absent by specification rather than pending"* |
| `02`:2596 Peril structure | `/peril-structures/{id}` | *"Per-peril model pins, large-loss treatment, reconciliation panel"* |

Both cells are in scope. `:2595` says each row links *"into the per-structure detail view
below"*, so the spec joins them: a library shipped without the detail builds rows linking
nowhere.

---

## The four questions this plan was dispatched to settle

**1. Do the backend routes exist?** **Yes, and they are real, not merely declared.**
`backend/src/app/api/peril_structures.py` implements all five of §5.1:1736-1740 and
`backend/src/app/main.py:117` registers the router. The list route is
`list_peril_structures_route` returning `Page[PerilStructure]`, with a filter type whose
docstring pins it to *"`02` §5.1's two filters, and no more."* **W6b-8 is frontend-only**, the
same finding W6b-7 reached and for the same reason — checked rather than assumed.

**2. Does the map's "no usage count" claim hold? CONFIRMED, and it is stronger than the map
states.** FR-MODEL-127's 2026-08-24 amendment (third correction) does not merely omit the
count; it rules the quantity **undefinable** on a peril row — a Model Spec cannot reference a
Peril Structure, the reference runs the other way (a structure pins models, §4.10) — and states
that *"§5.1's peril list row omitting it is correct as written."* The amendment also
pre-empts the obvious counter-argument: a Peril Structure *does* have a blast radius (`03`
FR-RATE-22 pins one per `model_call`), *"so the absent `/usage` route is a separate question
and not evidence for this one."* Do not reach for that to justify a count.

**3. Is `02`:2595/2596 among FR-OVR-21's seven carve-outs? No — neither cell is.** The seven
are `01` Validation report's banner; `01` §5.3's unnumbered Interaction requirement paragraph;
`02` Diagnostics; `02` Objective certificate; `03` DAG designer; `05` Drift; `07` Jobs. So
FR-OVR-21 applies in full and both cells are **prose binding nothing**.

**Where that precedent bears — and it bears here more than anywhere.** FR-OVR-21's closing
sentence: *"the contract-is-the-floor half is OQ-MODEL-15's decided rule of 2026-08-21;
OQ-MODEL-15 says nothing about a cell being prose, and that half rests on the `02` §5.3 Peril
structure library precedent alone."* **This slice builds the cell that is the sole precedent
for half of FR-OVR-21.** Two consequences an executor must not miss:

- The library cell's load-bearing content is a **negative** — "no usage count" — and OQ-OVR-10
  singled this row out as the one that *"enumerates its negative space."* Under FR-OVR-21 that
  negative binds nothing **as a cell**. It binds anyway, because **FR-MODEL-127 independently
  makes the absence a specification.** The prose-ness of the cell is not a licence to add the
  column; the requirement forbids it. Getting this backwards is the whole trap.
- Because this cell is the precedent, **an implementation that contradicts it weakens
  FR-OVR-21 itself.** If the built library renders a usage count, the sole support for
  contract-is-the-floor is a cell the code disagrees with.

**4. §13 verdict and owner per cell item** — the table below.

---

## Findings

### Finding 1 — `ArtifactLibraryTable`'s row shape cannot express a Peril Structure

W6b-7 (`docs/plans/2026-08-25-w6b-7-objective-library-and-certificate.md`, Task 4) creates
`frontend/src/components/ArtifactLibraryTable.vue` with the row shape:

```
{ id, slug, version, status, applicability, usageCount, href? }
```

**A Peril Structure has neither `applicability` nor `usageCount`.** `applicability` is
FR-MODEL-44's objective/metric concept — which responses, which backends, whether an offset is
required — and `PerilStructure` carries no such field. `usageCount` is forbidden by
FR-MODEL-127. Two of the six row fields are structurally absent, and the component was designed
against two libraries that both have them.

**Options.** (a) Give the peril library its own table component. (b) Make `applicability` and
`usageCount` optional on the row and render blank cells. (c) Give `ArtifactLibraryTable` an
explicit **column set**, so a caller declares which columns exist and the component renders
exactly those.

**Recommendation: (c).** (a) duplicates a table that is otherwise identical, and duplication of
a shape is the defect `CLAUDE.md` §2 names. (b) is the dangerous one and must be rejected
explicitly: **a blank cell is indistinguishable from a zero, a null and a failed fetch.** For a
column FR-MODEL-127 rules *undefinable*, rendering an empty cell asserts that a usage count
exists and happens to be unknown — the opposite of the specification. The column must be
**absent**, not empty. (c) is also what makes the component honest for the two W6b-7 libraries,
which genuinely have both columns.

**This is a modification to a component another slice creates.** See Trap 1.

### Finding 2 — the cell's three nouns name six of the contract's twenty-five fields

The instruction was to derive `:2596`'s contents from `PerilStructure`'s shape and to treat a
noun with no contract field as a finding. **All three nouns have contract fields** — *per-peril
model pins* is `PerilComponent.{frequency_model, severity_model, burning_cost_model}`;
*large-loss treatment* is `PerilComponent.large_loss`; *reconciliation panel* is
`PerilStructure.reconciliation`. The expected finding did not occur.

**It runs the other way, and not in one field.** Sweeping the whole contract against the cell —
because a finding reported as one symbol strands its list-mates:

| Type | Field | Named by a noun? | Ground for showing it |
|---|---|---|---|
| `PerilStructure` | `slug`, `version` | no | The artifact's identity; `peril_structure:{slug}@{version}` (ID-3) |
| | `perils` | partly | FR-MODEL-58 |
| | `excluded_perils` | **no** | **FR-MODEL-60** — *"either modelled or explicitly excluded with a reason"* |
| | `reconciliation` | yes | FR-MODEL-60 |
| | `status` | **no** | **FR-MODEL-61** — the structure's own lifecycle |
| | `created_at` | no | Ordinary provenance |
| `PerilComponent` | `peril` | implied | FR-MODEL-58 |
| | `method` | **no** | **FR-MODEL-58's two routes** — which one this peril takes |
| | the three model refs | yes | FR-MODEL-58 |
| | `large_loss` | yes | FR-MODEL-59 |
| `LargeLossTreatment` | `kind` | yes | FR-MODEL-59 |
| | `cap_minor`, `attachment_minor` | no | FR-MODEL-59's parameters — see Finding 3 |
| | `restoration_loading` | **no** | **FR-MODEL-74** — the reconciliation compares *after* restoration, so this is what makes the ratio mean what it means |
| | `excess_model`, `loading_factor` | no | FR-MODEL-59's parameters for the other two kinds |
| | `evidence_blob` | no | FR-MODEL-59's calibration evidence — deferred, §13 |
| `ExcludedPeril` | `peril`, `reason` | **no** | FR-MODEL-60 |
| `Reconciliation` | `part` | **no** | **FR-MODEL-60 reconciles *on the holdout*** — `part` is what says whether this verdict is one |
| | `tolerance` | no | FR-MODEL-60's *"declared tolerance"* |
| | `ratio`, `status` | no | FR-MODEL-60's verdict — `computed_field`s, Trap 6 |
| | `dataset_version_id`, `computed_at` | no | Which data, and when |
| | the two `*_burning_cost_minor` | no | Deferred — Findings 3 and 4 |
| | `perils[].modelled_burning_cost_minor` | no | As share of total — Finding 3 |

*(`PerilStructure.ref` is a plain `@property`, not a `computed_field`, so it is **not** on the
wire. Compose the canonical string in the view from `slug` and `version`, or do not show it.)*

**Two independent grounds, and both must be named.**

*The contract.* OQ-MODEL-15's decided rule of 2026-08-21 makes the generated contract the
floor and the Contents cell prose that binds nothing. A field in `PerilStructure` and absent
from the cell is therefore **in scope by the contract**, not optional because a noun omits it.
**This slice is where that rule gets exercised for the first and only time.** FR-OVR-21
(`00-overview.md:227`) closes: *"the contract-is-the-floor half is OQ-MODEL-15's decided rule
of 2026-08-21; OQ-MODEL-15 says nothing about a cell being prose, and that half rests on the
`02` §5.3 Peril structure library precedent alone."* The precedent is not being set on
`excluded_perils`; it is being set on **the whole unnamed set above**, which is most of the
contract. An executor who builds the three nouns and stops does not merely ship a thin view —
they leave the sole support for half of FR-OVR-21 contradicted by the code written under it.

*The requirements.* Independently of any of that, five of the unnamed fields are required by
numbered requirements — `excluded_perils` and `part` by FR-MODEL-60, `status` by FR-MODEL-61,
`method` by FR-MODEL-58, `restoration_loading` by FR-MODEL-74. These bind whatever one
concludes about cells and contracts, and they would bind if FR-OVR-21 were repealed tomorrow.
**Neither ground is a fallback for the other**: the contract ground reaches the whole set and
the requirement ground reaches only five, so dropping the first would quietly re-narrow scope
to those five while looking fully justified.

### Finding 3 — the reconciliation panel has no route to a currency, and it is OQ-OVR-14's fourth view

`Reconciliation` carries `observed_burning_cost_minor` and `modelled_burning_cost_minor`
(`MoneyMinor` integers), and `ReconciledPeril.modelled_burning_cost_minor` per peril.
Formatting a minor-unit amount needs a currency: `formatMinor(minor, currency)`
(`frontend/src/api/versions.ts:77`).

**There is no route to one.** `Reconciliation` carries `dataset_version_id`, and OQ-OVR-14
records verbatim that a view holding a dataset *version* id has **no route** to the currency —
*"`DatasetVersion` carries no currency, and `/datasets/{dataset_id}` is PATCH-only"* — so
option (b), fetching by slug, does not reach it. That is the factor workbench's position
exactly, and **the reconciliation panel is a fourth view in it.** OQ-OVR-14 is **open and
maintainer-owned**; this plan does not decide it.

**Two repository precedents govern what to do meanwhile.** `W6b-5b` **omitted the incurred
column rather than guess**. `W6b-9` made `OneWayChart`'s `currency` prop **required** so the
hardcoded `"GBP"` default could not propagate further. Both refuse to print a currency symbol
the view cannot source.

**Recommendation: render the verdict, omit the absolute amounts.** `ratio`, `tolerance` and
the derived `status` are **dimensionless**, and they are precisely what FR-MODEL-60 makes the
requirement — *"reconciles to observed burning cost within a declared tolerance."* The
per-peril breakdown FR-MODEL-74 asks for is preserved as each peril's **share of the modelled
total**, also dimensionless, shown beside its `large_loss_kind`. Nothing requirement-backed is
lost, and no view prints `£` over a euro-denominated structure. The absolute amounts return
when OQ-OVR-14 is decided; this plan proposes adding the panel to that question's view list.

*(Note for the executor: `ratio` and `status` on `Reconciliation` are `computed_field`s —
derived, not stored, per the module docstring. Read them; never recompute them client-side. A
second computation of a persisted verdict is the "two statements of one fact disagree
eventually" defect the contract was written to avoid.)*

**The large-loss panel is a second instance, and the omission answer does not transfer.**
Finding 2's sweep surfaced `LargeLossTreatment.cap_minor` and `.attachment_minor` — both
`MoneyMinor`, both landing in the detail view, and both missed when this finding was written
about the reconciliation panel alone. They differ from the burning-cost fields in two ways that
change the answer:

- **They are unambiguously money.** A cap on a loss and an attachment point are amounts, not
  statistics, so OQ-OVR-12's classification question does not touch them. `validate.py:983-986`
  is the standing example of the distinction — a threshold that genuinely *is* money, which
  must not be swept along with the statistic beside it.
- **Omitting them removes requirement content, where omitting the burning costs does not.**
  FR-MODEL-60's verdict survives in `ratio`; FR-MODEL-59's treatment does not survive in `kind`.
  A panel saying `capped` without saying capped *at what* has not recorded the treatment — it
  has recorded that there is one.

**Recommendation: render them as integer minor units, labelled by the contract's own field
name, with no currency symbol.** `cap_minor 500000` states a contract fact and asserts no
denomination; `£5,000.00` asserts one the view cannot source. This is the same refusal as the
reconciliation panel's, reached by a different route because the cost of omission differs — and
it is why OQ-OVR-14's fourth view is **two panels, only one of which can drop its amounts.**
Bring that to the manager when the question is costed; it is the sort of asymmetry that a view
count hides.

### Finding 4 — `OQ-OVR-12` is open on the very fields this view renders

`Reconciliation.observed_burning_cost_minor` and `ReconciledPeril.modelled_burning_cost_minor`
are named in OQ-OVR-12 as one side of a live divergence: burning cost is typed as strict
`MoneyMinor` here and as `float | None` without a suffix on `OneWayRow.mean_burning_cost`, and
FR-OVR-7's boundary now forbids both standings at once. The open recommendation is (b) — burning
cost is a statistic, the `..._minor` **suffix** is the defect and the integer stays.

**Consequence for this slice: render, do not rename, and do not label.** Do not print "minor
units" beside these figures, and do not introduce a UI label asserting a denomination the
repository has not settled. Finding 3's recommendation already keeps the absolute figures off
the screen, which makes this cost nothing today — but an executor who reverses Finding 3 must
not reintroduce the label. `01`'s `validate.py:1079` shipped exactly that string about a
statistic and it took a separate sweep to find.

### Finding 5 — `separate_model` and `flat_loading` render but do not compute

`LargeLossKind` has four members and the contract has carried all four from the start, but
`pricing_core.modelling.perils` **refuses `separate_model` and `flat_loading` by name**. The
detail view can therefore receive a structure declaring a treatment the platform cannot compute
a reconciliation for.

This is not a defect to fix here — it is FR-MODEL-87's staged-contract rule working as
intended. The view must render all four `large_loss.kind` values **by name** rather than
switching on the two that compute; a `v-if` over the computable pair would render a blank
treatment for a structure that declares one, which reads as "no large-loss handling" when the
structure says otherwise. Renders by name, and says nothing about computability — the refusal
surfaces on the reconcile path, not here.

---

## §13 disposition — every item in both cells

`CLAUDE.md` §13: every requirement without evidence gets one of four verdicts, and silence is
not one of them. FR-OVR-21 makes these cells prose, which is why each item is dispositioned
rather than assumed.

| Cell item | Verdict | Owner / note |
|---|---|---|
| Library: list with **status** | **Delivered** — Task 3 | `PerilStructureStatus`, six members, rendered by name |
| Library: list with **slug** | **Delivered** — Task 3 | With `version`; the pair is the artifact's identity (`peril_structure:{slug}@{version}`, ID-3) |
| Library: each row **links into the detail view** | **Delivered** — Task 3 | `href` to `/peril-structures/{id}`; the join `:2595` states |
| Library: **no usage count** | **Delivered as an absence** — Task 2 | The column does not exist in the peril column set. Tested as an absence (Task 2 Step 1), because an untested negative is the one that regresses silently |
| Library: `status`/`slug` **filtering** | **Delivered but untested at the UI** — Task 1 | The API module exposes both filters and they are unit-tested; no filter *control* is built. FR-MODEL-127 requires the endpoint be filterable, not that the view expose controls. Owner: the slice that needs one |
| Detail: **per-peril model pins** | **Delivered** — Task 5 | `ArtifactRef` rendered as the canonical `model:slug@version`; FR-MODEL-58's pinning is visible or it is not pinned |
| Detail: per-peril **method** (FR-MODEL-58) | **Delivered** — Task 5 | Unnamed by any cell noun; Finding 2. Which of the two routes this peril takes decides which model refs are even meaningful |
| Detail: large-loss **parameters** — `cap_minor`, `attachment_minor`, `restoration_loading`, `loading_factor`, `excess_model` | **Delivered** — Task 5 | Unnamed by any noun. `restoration_loading` is FR-MODEL-74's; the two `*_minor` are rendered currency-free per Finding 3 |
| Detail: reconciliation **`part`** (FR-MODEL-60) | **Delivered** — Task 4 | FR-MODEL-60 reconciles *on the holdout*; without `part` the reader cannot tell whether this verdict is one |
| Detail: **large-loss treatment** | **Delivered** — Task 5 | All four `LargeLossKind` by name (Finding 5); `cap_minor`/`restoration_loading` shown where present |
| Detail: large-loss **calibration evidence** (FR-MODEL-59) | **Deferred, owner: the maintainer** | `LargeLossTreatment.evidence_blob` is an opaque blob with no contract-declared shape. Rendering it needs a declared shape first — a new requirement under OQ-MODEL-15's floor rule, not a guess at a call site. Proposed to the roadmap |
| Detail: **reconciliation panel** — ratio, tolerance, derived status | **Delivered** — Task 4 | FR-MODEL-60's verdict, read from the `computed_field`s |
| Detail: reconciliation **per-peril breakdown with treatment** (FR-MODEL-74) | **Delivered** — Task 4 | As dimensionless share of modelled total, beside each peril's `large_loss_kind` |
| Detail: reconciliation **absolute burning-cost amounts** | **Deferred, owner: the maintainer** | Blocked on OQ-OVR-14 (no currency route) and touched by OQ-OVR-12. Finding 3 |
| Detail: **excluded perils with reason** (FR-MODEL-60) | **Delivered** — Task 5 | Named by no cell noun; required by FR-MODEL-60. Finding 2 |
| Detail: **status / lifecycle** (FR-MODEL-61) | **Delivered** — Task 5 | Rendered; `reconciliation` is `None` in `draft` and that is a state, not an error (Trap 3) |
| Detail: **submit** affordance (FR-MODEL-90) | **Not started, owner: W6b or its successor** | `POST /{id}/submit` exists and is unbuilt in the UI. A submit control needs the `reconciled → review` guard, an approval-request surface and an error path; it is a slice, not a button. Booked explicitly rather than left silent. Proposed to the roadmap |
| Detail: **reconcile** affordance | **Not started, owner: as above** | `POST /{id}/reconcile` is a 202 → Job; needs `07`'s job-progress surface |

---

## Traps

1. **This plan depends on W6b-7 having *executed*, not merged.** `ArtifactLibraryTable.vue` and
   `ArtifactStatusBadge.vue` do not exist on `main` — W6b-7 is a filed plan whose PR (#218,
   `756fb77`) contains the plan document and no frontend code. **Before starting Task 2, run
   `ls frontend/src/components/ArtifactLibraryTable.vue`.** If it is absent, stop and tell the
   manager: this slice is blocked on W6b-7's execution, not on anything in it. Do not build a
   second library table to route around the absence — that is Finding 1's rejected option (a),
   arrived at by accident.
2. **`usageCount` must be absent, not blank.** Finding 1. The test in Task 2 asserts the header
   is not rendered, not that the cell is empty.
3. **`reconciliation` is `None` for a `draft` structure, and that is correct.** The model
   validator requires a reconciliation only in `reconciled`, `review` and `approved`. A detail
   view that treats `null` as a fetch failure will show an error over a perfectly valid draft.
   Render an explicit "not yet reconciled" state keyed on `status`, not on the null.
4. **`draft → review` is not an edge in this lifecycle.** The module docstring: FR-MODEL-61
   makes the structure approvable and FR-MODEL-60 makes the reconciliation its evidence, so a
   structure reaching an approver without one *"is not a state to refuse later — it is a state
   with no edge into it."* Any future submit control reads `reconciled`, never `draft`. Also
   `review → reconciled`, never `review → draft`; and `approved → archived` does not exist.
5. **Peril codes are `UPPER_SNAKE`, not slugs** (`PerilCode`, `perils.py:68`). Do not
   slugify them for display or for a DOM id; `TP_BI` is the identifier a user recognises from
   their own data.
6. **`ratio` and `status` are `computed_field`s.** Finding 3's note. They arrive on the wire and
   are read-only; `Reconciliation`'s `_drop_derived` validator discards them on the way in.
7. **Route ordering.** `/peril-structures` (static) and `/peril-structures/:id` (dynamic) —
   a static segment outranks a dynamic one from either position, so the tests assert
   **resolution**, following `router/index.ts:96-98`'s stated convention.
8. **An `ArtifactRef` is a string on the wire, not an object.** `frequency_model`,
   `severity_model` and `burning_cost_model` arrive as `"model:ad-freq@4"` — the canonical
   `{type}:{slug}@{version}` of ID-3 — because `refs.py` overrides
   `__get_pydantic_json_schema__` to emit `{"type": "string", "pattern": …}`. Its docstring
   says why, and names this exact mistake: *"Without this the schema describes the Python
   object — three properties — and a frontend generated from it would expect an object where
   every spec, trace and audit row carries a string."* **Do not destructure it, and do not
   parse it to re-render the parts.** The canonical string is the display form — it is what
   appears in traces and audit rows and what a user pastes into a ticket, so a view that
   splits it into "ad-freq (v4)" makes the pinned reference unsearchable against every other
   surface. *(This plan's first draft wrote the object form into a fixture from memory. The
   caught version is above; the trap is recorded because the wire form is not visible from
   `perils.py`, only from `refs.py`.)*

---

## File structure

| File | Responsibility |
|---|---|
| Create `frontend/src/api/perils.ts` | The two reads, the page cap, the status constants. Mirrors `objectives.ts`'s shape so a reader who knows one knows the other |
| Create `frontend/src/api/__tests__/perils.test.ts` | Paging, truncation, filter pass-through |
| Modify `frontend/src/components/ArtifactLibraryTable.vue` | Add the column set (Finding 1) |
| Modify `frontend/src/components/__tests__/ArtifactLibraryTable.test.ts` | The absence test |
| Create `frontend/src/components/ReconciliationPanel.vue` | FR-MODEL-60's verdict and FR-MODEL-74's breakdown |
| Create `frontend/src/components/__tests__/ReconciliationPanel.test.ts` | |
| Create `frontend/src/views/PerilStructureLibraryView.vue` | `:2595` |
| Create `frontend/src/views/PerilStructureDetailView.vue` | `:2596` — composition, large loss, excluded perils, reconciliation |
| Create `frontend/src/views/__tests__/PerilStructureDetailView.test.ts` | |
| Modify `frontend/src/router/index.ts` | Two routes |

---

## Task 1: The API module

**Files:**
- Create: `frontend/src/api/perils.ts`
- Test: `frontend/src/api/__tests__/perils.test.ts`

**Interfaces:**
- Consumes: `pageThrough`, `Paged` from `./paging`; `components` from `./generated/schema`.
- Produces: `PerilStructure`, `PerilStructureStatus`, `PERIL_STRUCTURE_PAGE_CAP`,
  `listPerilStructures({status?, slug?})` → `Promise<Paged<PerilStructure>>`,
  `getPerilStructure(id: string)` → `Promise<PerilStructure>`.

- [ ] **Step 1: Write the failing test**

```typescript
import { describe, expect, it, vi, beforeEach } from "vitest";
import { listPerilStructures, PERIL_STRUCTURE_PAGE_CAP } from "../perils";
import * as paging from "../paging";

describe("listPerilStructures", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("passes both of FR-MODEL-127's filters through, and no others", async () => {
    const spy = vi.spyOn(paging, "pageThrough").mockResolvedValue({ items: [], truncated: false });
    await listPerilStructures({ status: "reconciled", slug: "motor-2026" });
    expect(spy).toHaveBeenCalledWith(
      "/peril-structures",
      { status: "reconciled", slug: "motor-2026" },
      PERIL_STRUCTURE_PAGE_CAP,
    );
  });

  it("caps the sweep and reports truncation rather than logging it", async () => {
    vi.spyOn(paging, "pageThrough").mockResolvedValue({ items: [], truncated: true });
    const page = await listPerilStructures({});
    expect(page.truncated).toBe(true);
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `pnpm --dir frontend test -- perils.test.ts`
Expected: FAIL — cannot resolve `../perils`.

- [ ] **Step 3: Write the module**

```typescript
import { pageThrough, type Paged } from "./paging";
import { request } from "./client";
import type { components } from "./generated/schema";

export type PerilStructure = components["schemas"]["PerilStructure"];
export type PerilStructureStatus = components["schemas"]["PerilStructureStatus"];

/**
 * How many pages `listPerilStructures` will fetch before it stops and says so.
 *
 * Matches `OBJECTIVE_PAGE_CAP` deliberately: the two libraries are the same screen over
 * different artifacts, and a reader who learns one cap should not find a second number here.
 * `truncated` is part of the return type rather than a log line for the reason `objectives.ts`
 * gives — an empty page under a truncated sweep is indistinguishable from an empty library.
 */
export const PERIL_STRUCTURE_PAGE_CAP = 5;

export async function listPerilStructures(
  options: { status?: PerilStructureStatus | undefined; slug?: string | undefined } = {},
): Promise<Paged<PerilStructure>> {
  return pageThrough<PerilStructure>(
    "/peril-structures", { status: options.status, slug: options.slug }, PERIL_STRUCTURE_PAGE_CAP,
  );
}

export async function getPerilStructure(id: string): Promise<PerilStructure> {
  return request<PerilStructure>(`/peril-structures/${encodeURIComponent(id)}`);
}
```

*`request` and the `encodeURIComponent` on the path segment both follow
`frontend/src/api/diagnostics.ts:35`, which is the house form for a single-resource read.
`pageThrough`'s query parameter is typed `Record<string, string | number | undefined>`
(`paging.ts:38`), so passing `undefined` for an unset filter is the intended call, not a
workaround — it drops out of the query string rather than sending an empty value.*

- [ ] **Step 4: Run the test**

Run: `pnpm --dir frontend test -- perils.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/perils.ts frontend/src/api/__tests__/perils.test.ts
git commit -m "feat(w6b-8): read peril structures, with FR-MODEL-127's two filters"
```

---

## Task 2: Widen `ArtifactLibraryTable` to a column set

**Files:**
- Modify: `frontend/src/components/ArtifactLibraryTable.vue`
- Modify: `frontend/src/components/__tests__/ArtifactLibraryTable.test.ts`

**Interfaces:**
- Consumes: the component as W6b-7 built it.
- Produces: `<ArtifactLibraryTable :rows="…" :columns="…" :truncated="…" :empty-label="…" />`
  where `columns` is `readonly ArtifactColumn[]`, `ArtifactColumn =
  "slug" | "version" | "status" | "applicability" | "usageCount"`. A row keeps its existing
  shape with `applicability` and `usageCount` optional. **Rendering is driven by `columns`, not
  by whether a row's value is present.**

**Check Trap 1 before starting this task.**

- [ ] **Step 1: Write the failing test**

```typescript
const PERIL_COLUMNS = ["slug", "version", "status"] as const;
const PERIL_ROWS = [
  { id: "p1", slug: "motor-2026", version: 3, status: "reconciled" as const,
    href: "/peril-structures/p1" },
];

describe("ArtifactLibraryTable column set", () => {
  it("omits the usage-count column entirely when it is not in the column set", () => {
    const table = mount(ArtifactLibraryTable, {
      props: { rows: PERIL_ROWS, columns: PERIL_COLUMNS, truncated: false, emptyLabel: "none" },
    });
    const headers = table.findAll("th").map((h) => h.text().toLowerCase());
    expect(headers.some((h) => h.includes("usage"))).toBe(false);
    expect(headers.some((h) => h.includes("applicab"))).toBe(false);
  });

  it("renders one cell per declared column, so no row can be ragged", () => {
    const table = mount(ArtifactLibraryTable, {
      props: { rows: PERIL_ROWS, columns: PERIL_COLUMNS, truncated: false, emptyLabel: "none" },
    });
    expect(table.findAll("tbody td")).toHaveLength(PERIL_COLUMNS.length);
  });
});
```

The first test is the one that matters. **A blank cell would pass a "no usage count is shown"
test written naively** — asserting the *header* is absent is what distinguishes an undefinable
column from an unknown value, which is the whole of FR-MODEL-127's third correction.

- [ ] **Step 2: Run it and watch it fail**

Run: `pnpm --dir frontend test -- ArtifactLibraryTable.test.ts`
Expected: FAIL — `columns` is not a declared prop; the usage header renders regardless.

- [ ] **Step 3: Add the column set**

Make `columns` a required prop typed as above; drive both `<th>` and `<td>` from it; make
`applicability` and `usageCount` optional on the row type. Update W6b-7's two callers
(`ObjectiveLibraryView`, `MetricLibraryView`) to pass the full five-column set so their
behaviour is unchanged.

- [ ] **Step 4: Run the whole component and view suite**

Run: `pnpm --dir frontend test -- ArtifactLibraryTable ObjectiveLibraryView MetricLibraryView`
Expected: PASS — including W6b-7's original three tests, unmodified.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ArtifactLibraryTable.vue \
  frontend/src/components/__tests__/ArtifactLibraryTable.test.ts \
  frontend/src/views/ObjectiveLibraryView.vue frontend/src/views/MetricLibraryView.vue
git commit -m "feat(w6b-8): a library table renders its declared columns, not its present values"
```

---

## Task 3: The library view

**Files:**
- Create: `frontend/src/views/PerilStructureLibraryView.vue`
- Modify: `frontend/src/router/index.ts`
- Test: `frontend/src/views/__tests__/PerilStructureLibraryView.test.ts`

**Interfaces:**
- Consumes: `listPerilStructures`, `PERIL_STRUCTURE_PAGE_CAP` (Task 1); `ArtifactLibraryTable`
  with `columns` (Task 2).
- Produces: route `{ path: "/peril-structures", name: "peril-structure-library" }`.

- [ ] **Step 1: Write the failing test**

```typescript
it("renders slug, version and status, and never a usage column", async () => {
  // mock listPerilStructures to resolve one structure, mount, flush
  expect(wrapper.text()).toContain("motor-2026");
  expect(wrapper.findAll("th").map((h) => h.text().toLowerCase())
    .some((h) => h.includes("usage"))).toBe(false);
});

it("links each row into the detail view", async () => {
  expect(wrapper.find("a[href='/peril-structures/p1']").exists()).toBe(true);
});
```

The second test is `:2595`'s own words — *"each row linking into the per-structure detail view
below"* — and it is why this slice cannot ship the library alone.

- [ ] **Step 2: Run it and watch it fail.** Expected: FAIL — view does not resolve.

- [ ] **Step 3: Write the view.** Map `PerilStructure` onto the row shape; pass
  `columns={["slug", "version", "status"]}`; pass `truncated` straight through.

- [ ] **Step 4: Add the route and assert resolution**

```typescript
it("resolves the library and the detail route", () => {
  expect(router.resolve("/peril-structures").name).toBe("peril-structure-library");
  expect(router.resolve("/peril-structures/abc").name).toBe("peril-structure-detail");
});
```

- [ ] **Step 5: Run and commit**

```bash
pnpm --dir frontend test -- PerilStructureLibraryView router
git add frontend/src/views/PerilStructureLibraryView.vue frontend/src/router/index.ts \
  frontend/src/views/__tests__/PerilStructureLibraryView.test.ts
git commit -m "feat(w6b-8): the peril structure library, without a count that cannot be defined"
```

---

## Task 4: The reconciliation panel

**Files:**
- Create: `frontend/src/components/ReconciliationPanel.vue`
- Test: `frontend/src/components/__tests__/ReconciliationPanel.test.ts`

**Interfaces:**
- Consumes: `PerilStructure["reconciliation"]` (Task 1).
- Produces: `<ReconciliationPanel :reconciliation="…" />`. Renders `ratio`, `tolerance`, the
  derived `status`, and one line per `ReconciledPeril` giving its `peril`, its
  `large_loss_kind` and its **share of the modelled total**. Renders **no absolute amount and
  no currency symbol** (Finding 3).

- [ ] **Step 1: Write the failing test**

```typescript
const RECONCILIATION = {
  dataset_version_id: "11111111-1111-1111-1111-111111111111",
  part: "holdout",
  perils: [
    { peril: "AD", large_loss_kind: "capped", modelled_burning_cost_minor: 7500 },
    { peril: "TP_BI", large_loss_kind: "separate_model", modelled_burning_cost_minor: 2500 },
  ],
  observed_burning_cost_minor: 10200,
  modelled_burning_cost_minor: 10000,
  tolerance: "0.05",
  computed_at: "2026-08-25T00:00:00Z",
  ratio: "0.9804",
  status: "pass",
};

it("shows FR-MODEL-60's verdict as it arrived, not as recomputed", () => {
  const panel = mount(ReconciliationPanel, { props: { reconciliation: RECONCILIATION } });
  expect(panel.text()).toContain("pass");
  expect(panel.text()).toContain("0.9804");
  expect(panel.text()).toContain("0.05");     // the declared tolerance the verdict is against
});

it("says which part the verdict is over (FR-MODEL-60's holdout)", () => {
  const panel = mount(ReconciliationPanel, { props: { reconciliation: RECONCILIATION } });
  expect(panel.text()).toContain("holdout");
});

it("states each peril's treatment beside its share (FR-MODEL-74)", () => {
  const panel = mount(ReconciliationPanel, { props: { reconciliation: RECONCILIATION } });
  expect(panel.text()).toContain("TP_BI");
  expect(panel.text()).toContain("separate_model");
  expect(panel.text()).toContain("75");   // AD's share of the modelled total, per cent
});

it("prints no currency symbol and no raw minor amount", () => {
  const panel = mount(ReconciliationPanel, { props: { reconciliation: RECONCILIATION } });
  expect(panel.text()).not.toMatch(/[£$€]/);
  expect(panel.text()).not.toContain("10000");
  expect(panel.text()).not.toContain("minor units");
});
```

The third test is the one that keeps Finding 3 honest. Without it, a later change that threads
a `currency` default in would pass every other assertion — and `"GBP"` over a euro structure is
invisible exactly because it looks right.

*Executor: `ratio` and `tolerance` are `DecimalStr` — strings on the wire, never floats. Do not
`parseFloat` them for display. Computing a percentage share is arithmetic on the integer minor
values, which is exact.*

- [ ] **Step 2: Run and watch it fail.** Expected: FAIL — component does not resolve.
- [ ] **Step 3: Write the component.**
- [ ] **Step 4: Run the test.** Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ReconciliationPanel.vue \
  frontend/src/components/__tests__/ReconciliationPanel.test.ts
git commit -m "feat(w6b-8): the reconciliation verdict, in the units it can source"
```

---

## Task 5: The detail view

**Files:**
- Create: `frontend/src/views/PerilStructureDetailView.vue`
- Modify: `frontend/src/router/index.ts`
- Test: `frontend/src/views/__tests__/PerilStructureDetailView.test.ts`

**Interfaces:**
- Consumes: `getPerilStructure` (Task 1), `ReconciliationPanel` (Task 4),
  `ArtifactStatusBadge` (W6b-7).
- Produces: route `{ path: "/peril-structures/:id", name: "peril-structure-detail",
  props: (route) => ({ id: route.params.id }) }`.

- [ ] **Step 1: Write the failing tests**

```typescript
it("pins each model reference by version (FR-MODEL-58)", async () => {
  // structure with perils[0].frequency_model = "model:ad-freq@4" — a string, see Trap 8
  expect(wrapper.text()).toContain("model:ad-freq@4");
});

it("names every excluded peril and its reason (FR-MODEL-60)", async () => {
  // excluded_perils: [{ peril: "COURTESY_CAR", reason: "Bundled service cost" }]
  expect(wrapper.text()).toContain("COURTESY_CAR");
  expect(wrapper.text()).toContain("Bundled service cost");
});

it("renders a large-loss kind the platform cannot compute (Finding 5)", async () => {
  // perils[1].large_loss = { kind: "flat_loading", loading_factor: "1.15", evidence_blob: … }
  expect(wrapper.text()).toContain("flat_loading");
  expect(wrapper.text()).toContain("1.15");
});

it("states the treatment's parameters, not just its kind (FR-MODEL-59, Finding 3)", async () => {
  // perils[0].large_loss = { kind: "capped", cap_minor: 500000,
  //                          restoration_loading: "1.08", evidence_blob: … }
  expect(wrapper.text()).toContain("500000");   // integer minor units, no symbol
  expect(wrapper.text()).toContain("1.08");     // FR-MODEL-74's restoration
  expect(wrapper.text()).not.toMatch(/[£$€]/);
});

it("names each peril's method, which decides what its refs mean (FR-MODEL-58)", async () => {
  expect(wrapper.text()).toContain("frequency_severity");
});

it("shows a draft structure as unreconciled rather than as an error", async () => {
  // status: "draft", reconciliation: null
  expect(wrapper.text().toLowerCase()).toContain("not yet reconciled");
  expect(wrapper.text().toLowerCase()).not.toContain("error");
});
```

The second test is Finding 2 — the panel no cell noun asked for. The fourth is Trap 3.

- [ ] **Step 2: Run and watch them fail.** Expected: FAIL — view does not resolve.
- [ ] **Step 3: Write the view.** Four sections, and Finding 2's sweep table is the field list
  — build from it, not from the cell's three nouns. Composition (per peril: `peril`, `method`,
  and whichever model refs its method makes meaningful, as canonical strings); large-loss
  treatment per peril (`kind` plus the parameters that kind requires — the contract's own
  `_fields_match_the_kind` says which, and a parameter present for a kind that does not use it
  is refused at the source, so the view never has to decide); excluded perils with reasons; and
  `<ReconciliationPanel>` gated on `status` rather than on `reconciliation === null`. Header
  carries `slug`, `version`, `status` and `created_at`.
- [ ] **Step 4: Run the tests.** Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/PerilStructureDetailView.vue frontend/src/router/index.ts \
  frontend/src/views/__tests__/PerilStructureDetailView.test.ts
git commit -m "feat(w6b-8): the peril structure detail, including the perils it excludes"
```

---

## Task 6: Gate and hand-off

- [ ] **Step 1: Run both halves of the gate**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

**Both halves.** A Python-only "gate" has been green here while the frontend was red
(`CLAUDE.md` §11).

- [ ] **Step 2: Confirm the absence that FR-MODEL-127 specifies**

```bash
grep -rn "usage_count\|usageCount" frontend/src/views/PerilStructureLibraryView.vue
```

Expected: **no output.** If this prints anything, the sole precedent supporting FR-OVR-21's
contract-is-the-floor half now contradicts the code built against it.

- [ ] **Step 3: Take the roadmap proposals below to the manager.** They are proposals, never
  changes (`CLAUDE.md` §14).

---

## Roadmap proposals

`CLAUDE.md` §14: the output is a proposal, with a maintainer acceptance line and a date. Each
of these is a deferral recorded in a plan that §2 freezes, which is a deferral nobody reads
again unless it also lands somewhere live.

1. **OQ-OVR-14 gains a fourth view.** The peril reconciliation panel holds a
   `dataset_version_id` and has no route to a workspace currency — the factor workbench's
   position exactly. Proposed: add it to the question's view list so the option set is costed
   against four views rather than three. Owner: maintainer.
2. **`LargeLossTreatment.evidence_blob` has no declared shape.** FR-MODEL-59 requires the
   treatment be *"recorded with its calibration evidence"*, and no view can render an opaque
   blob. Proposed: a requirement declaring its shape, or an explicit statement that it is
   operator-facing and not rendered. Owner: maintainer. Until then the detail view shows the
   treatment and not its evidence, which is half of FR-MODEL-59.
3. **The submit and reconcile affordances are unbuilt and unowned.** FR-MODEL-90 makes the
   structure submittable and §5.1 declares both routes; neither has a UI. Proposed as a
   follow-on slice, not folded here — submit needs the `reconciled → review` guard and an
   approval surface, reconcile is a 202 needing `07`'s job progress. Owner: W6b's successor.

**Maintainer acceptance:** ______________________  **Date:** ______________

---

## Self-review

**Spec coverage.** Every requirement in the scope table maps to a task: FR-MODEL-58 → Task 5
test 1; FR-MODEL-59 → Task 5 test 3, with its evidence half deferred and proposed; FR-MODEL-60
→ Task 4 test 1 and Task 5 test 2, both limbs (tolerance verdict, and excluded-with-reason);
FR-MODEL-61 → Task 5's status rendering, with the submit half booked not-started; FR-MODEL-74 →
Task 4 test 2; FR-MODEL-90's read half → Task 1, its submit half booked; FR-MODEL-127 → Tasks 1,
2 and 3, including its negative limb tested as an absence in Task 2 and re-checked in Task 6.

**Placeholder scan.** No TBDs. One place names a check rather than pre-writing it — Trap 1's
`ls` on W6b-7's component — because it is a verification against a moving tree, which a frozen
plan cannot do for the executor.

**The sweep, and why it was not done once.** Finding 2 began as a single reported field,
`excluded_perils`. Reported that way it invites fixing that field — so the whole
`PerilStructure` field set was swept against the cell afterwards, and the unnamed set turned
out to be most of the contract, including `method`, `part` and `restoration_loading`, each
backed by its own requirement. The sweep also caught a defect in **this plan's own Finding 3**:
the currency problem was written up for the reconciliation panel while `cap_minor` and
`attachment_minor` sat unnoticed in the large-loss panel, where the same question has a
different answer. A finding reported as one symbol strands its list-mates, and that holds for
the reporter as much as for the reader.

**What this review caught.** `docs/plans/README.md`'s three unenforced conventions were run
against the draft, and rule 1 fired twice. The API module called a `client.get` that does not
exist (`diagnostics.ts:35` uses `request`), and the Task 5 fixture wrote `frequency_model` as
`{ type, slug, version }` — the Python-side object — where the wire carries the string
`"model:ad-freq@4"`. Both were written from memory about a *neighbouring* file: the peril
literals were all read from `perils.py` and all correct, but `ArtifactRef`'s wire form is only
visible in `refs.py`, and reading the type that *holds* a field is not reading the field.
Recorded as Trap 8 rather than merely fixed, because the object form is what a reader of
`perils.py` alone will infer.

**Type consistency.** `PerilStructure`, `PerilStructureStatus`, `Paged` are used with the same
names in Tasks 1, 3 and 5. `ArtifactColumn` and the `columns` prop are introduced in Task 2 and
consumed in Task 3 with the same three-member set. `ReconciliationPanel`'s single
`reconciliation` prop is produced in Task 4 and consumed in Task 5. Field names in every fixture
were read from `packages/model-schema/src/model_schema/perils.py` rather than recalled —
`peril`, `method`, `frequency_model`, `severity_model`, `burning_cost_model`, `large_loss`,
`kind`, `cap_minor`, `restoration_loading`, `excluded_perils`, `reason`, `dataset_version_id`,
`part`, `perils`, `observed_burning_cost_minor`, `modelled_burning_cost_minor`, `tolerance`,
`computed_at`, `large_loss_kind` — and the enum literals likewise (`draft`, `reconciled`,
`review`, `approved`, `superseded`, `archived`; `none`, `capped`, `separate_model`,
`flat_loading`; `pass`, `fail`; `frequency_severity`, `burning_cost`).

**Line numbers.** Citations to `02-modelling.md` are given with their content quoted, so a
reader whose line numbers have moved can re-find them:
`grep -n "Peril structure library" docs/specs/02-modelling.md`.
