# WF-02 — Approved Models to approved Rating Version

**Modules:** `02-modelling` · `03-rating-engine` · `06-governance`
**Primary actors:** Pricing Actuary, Analyst, Approver
**Trigger:** An approved Peril Structure exists and needs to become a price.
**Outcome:** An `approved`, fully-pinned Rating Version ready for deployment (WF-04).

---

## 1. Preconditions

| Condition | Refs |
|---|---|
| An `approved` Peril Structure with a passing reconciliation | `02` FR-MODEL-60/61 |
| Reference Table Versions for every `lookup` are `approved` and cover the effective period | `01` FR-DATA-30, VR-REF-3 |
| A portfolio Dataset Version exists for dislocation | `01` §7.2 |
| The actor holds `rating_algorithm:write`, `rate_table:write`, `rating_version:submit` | `06` FR-GOV-4 |

---

## 2. Main sequence

### Phase A — From technical estimate to rate tables (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| A1 | Pricing Actuary | `POST /rate-tables/{slug}/seed-from-model` on the AD frequency model — its relativity table becomes the starting rate table, with `seeded_from` recorded. | `03` FR-RATE-16 |
| A2 | Pricing Actuary | Repeats for every rateable factor across perils. The technical rate is now the baseline, explicitly. | `03` FR-RATE-16 |
| A3 | Pricing Actuary | Edits cells with commercial judgement — softens `17-20` from 1.92 to 1.84. The editor shows the change against **both** the previous version and the technical seed, with the exposure weight behind each cell. | `03` FR-RATE-17 |
| A4 | Pricing Actuary | Applies a bulk operation: +2 % across the expense table. It is recorded as a parameterised operation, not 40 unexplained cell edits. | `03` FR-RATE-18 |
| A5 | Backend | Validates on save: complete key coverage, no nulls, values within declared bounds, no duplicate keys. | `03` FR-RATE-19 |
| A6 | Pricing Actuary | Saves each as a new Rate Table Version with a mandatory change note. | `03` FR-RATE-15 |

**Checkpoint:** Rate tables carry both diffs — "what changed since last time" and "how far
we have moved from what the models say". The second is the one that gets asked about in
committee and is normally the one nobody can answer.

### Phase B — Rating algorithm (Pricing Actuary / Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| B1 | Pricing Actuary | Opens the DAG designer on `rating_algorithm:motor-gb@13`, forks to `@14`. | `03` §5.3 |
| B2 | Pricing Actuary | Declares the input contract: types, ranges, enum domains, nullability, descriptions. | `03` FR-RATE-2 |
| B3 | Pricing Actuary | Adds a `lookup` step: outcode → rating area, as at `effective_date` — not "now". | `03` FR-RATE-9 |
| B4 | Pricing Actuary | Adds a `model_call` step referencing the Peril Structure, `mode: exact`, with an explicit feature map. | `03` FR-RATE-10 |
| B5 | Pricing Actuary | Adds `table` steps for each rate table, `expression` steps for the loading chain, and `constraint` steps for minimum premium and the maximum year-on-year increase, each with a `reason_code`. | `03` FR-RATE-8/11 |
| B6 | Frontend | Flags an error **on the node**: `s_office` consumes `commission_factor`, which nothing produces. The graph cannot be saved. | `03` FR-RATE-1, §5.3 |
| B7 | Pricing Actuary | Mounts the reusable `sub_graph:ncd-ladder@4` rather than re-drawing it. | `03` FR-RATE-6 |
| B8 | Pricing Actuary | Adds `output` steps with explicit rounding (`half_even`, 0 dp on pence). Rounding happens exactly once. | `03` FR-RATE-12 |
| B9 | Backend | Type-checks on save. An `expression` step multiplying a `money_minor` by a float-typed value is refused: `MONETARY_FLOAT_REFUSED`. | `03` FR-RATE-13/29, R2 |

### Phase C — Compile and pin (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| C1 | Pricing Actuary | `POST /rating-versions` — declares the algorithm version and every pin: rate tables, peril structure, reference tables. | `03` FR-RATE-22 |
| C2 | Pricing Actuary | `POST /rating-versions/{id}/compile` → `202` + Job (`rating.compile`). | `07` FR-PLAT-7 |
| C3 | Worker → pricing-core | `compile_bundle` validates everything at once: DAG structure, reference resolvability, artifact maturity, type compatibility, no `control`-intent factor in a rateable path, no unapproved custom objective transitively reachable. | `03` FR-RATE-25 |
| C4 | Worker | First attempt fails: `PIN_NOT_APPROVED` — the windscreen burning-cost model is still `review`. | `03` FR-RATE-25, FR-OVR-14 |
| C5 | Pricing Actuary | Waits for that model's approval (WF-01 phase E), recompiles. | — |
| C6 | Worker | Produces the Bundle: content hash, 84 MB, self-contained. It will score with no database access at all. | `03` FR-RATE-24, NFR-RATE-3 |

### Phase D — Evidence (Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| D1 | Analyst | `POST /rating-versions/{id}/regression-runs` — golden quotes plus generated property assertions over the input contract. | `03` FR-RATE-43/44 |
| D2 | Worker | 118 of 120 golden quotes reproduce exactly. Two fail: the minimum-premium change moved them. | `03` FR-RATE-43 |
| D3 | Analyst | Confirms the two failures are intended, updates their expected values, and records why in the golden quote's note. **A golden quote is only updated deliberately.** | `03` FR-RATE-43 |
| D4 | Worker | A property assertion fails: `monotone_in_age` breaks between 63 and 64 because two rate tables band age differently. Hypothesis shrinks it to a minimal counterexample. | `03` FR-RATE-44 |
| D5 | Pricing Actuary | Fixes the banding mismatch — a genuine defect that a golden-quote suite alone would have missed. | `03` FR-RATE-44 |
| D6 | Analyst | `POST /dislocation-runs` against the current live version over the portfolio. | `03` FR-RATE-46 |
| D7 | Worker → pricing-core | Re-rates 1.28 M policies under both bundles: change distribution, per-segment breakdown, largest movers, and **attribution** decomposing the change into peril-structure, rate-table, and minimum-premium effects. | `03` FR-RATE-46/47/49 |
| D8 | Pricing Actuary | Reviews. Total +1.95 %, but 2.9 % of policies move more than +10 % — driven by the minimum premium, not by the model refit. The attribution says so directly. | `03` FR-RATE-49 |
| D9 | Pricing Actuary | Runs a GIPP check where enabled (detailed in WF-03). | `04` FR-OPT-18 |

### Phase E — Approval (Pricing Actuary → Approver ×2)

| # | Actor | Action | Refs |
|---|---|---|---|
| E1 | Pricing Actuary | Writes the change summary. It is drafted automatically from the structural and rate diffs and then edited — the actuary explains *why*, the platform states *what*. | `03` FR-RATE-27 |
| E2 | Pricing Actuary | `POST /approval-requests`. Evidence completeness is checked at submission: structural diff, rate diffs, regression run, dislocation run, GIPP check, change summary. | `03` FR-RATE-40, `06` FR-GOV-10/19 |
| E3 | Backend | Submission is rejected once — `EVIDENCE_INCOMPLETE`, the dislocation run predates the last rate table edit and is therefore stale. | `06` FR-GOV-14 |
| E4 | Pricing Actuary | Re-runs dislocation, resubmits. | — |
| E5 | Approver #1 | Reviews inline: structural diff, rate-table heat maps, dislocation histogram, attribution waterfall, GIPP distribution. Approves. | `06` FR-GOV-16 |
| E6 | Approver #2 | Rating Versions require two approvers by default policy. Requests changes: the +10 % movers need a communication plan. | `06` §4.2, FR-GOV-13 |
| E7 | Pricing Actuary | Adds the plan as a Commentary Block in the dossier, resubmits. Both the change request and its resolution stay in the trail. | `06` FR-GOV-13/28 |
| E8 | Approver #2 | Approves. | `06` FR-GOV-11 |
| E9 | Backend | Transitions to `approved`, pins the decision to the exact version and evidence ids, emits Audit Events. | `06` FR-GOV-14, R2 |

---

## 3. Failure and exception paths

| Situation | Behaviour | Refs |
|---|---|---|
| Graph has a cycle or an unresolved reference | Rejected at save time, shown on the node | `03` FR-RATE-1, `RATING_GRAPH_CYCLIC` |
| Monetary value would be float-typed | `MONETARY_FLOAT_REFUSED` at save | `03` R2, FR-RATE-13 |
| A pinned artifact is not yet approved | `PIN_NOT_APPROVED` at compile | `03` FR-RATE-25 |
| A `control`-intent factor reaches a rate table | `CONTROL_FACTOR_IN_RATEABLE_PATH` | `02` FR-MODEL-3, `03` FR-RATE-25 |
| Rate table has a gap in key coverage | `RATE_TABLE_INCOMPLETE` at save | `03` FR-RATE-19 |
| Golden quote mismatch | Promotion blocked until each mismatch is deliberately accepted | `03` FR-RATE-43 |
| Evidence stale relative to the artifact | `EVIDENCE_INCOMPLETE` at submission | `06` FR-GOV-14 |
| Submitter tries to approve | `SUBMITTER_CANNOT_APPROVE` | `06` R1 |
| Referenced model later flagged `dataset_invalidated` | Flag propagates to the Rating Version and to the inbox; approval blocked | `01` FR-DATA-23, `06` FR-GOV-17 |

---

## 4. Postconditions

- `rating_version:motor-gb@27` — `approved`, every dependency pinned, bundle hash fixed.
- A regression suite that passes against exactly this bundle.
- A dislocation artifact with attribution, citable in committee.
- Two approval decisions with comments, one change request and its resolution.
- A dossier assembled from all of the above (`06` FR-GOV-27).

---

## 5. Traceability

| Phase | Requirements exercised |
|---|---|
| A — Rate tables | `03` FR-RATE-14..21 |
| B — Algorithm | `03` FR-RATE-1..13, 28..33 |
| C — Compile | `03` FR-RATE-22..27; FR-OVR-14 |
| D — Evidence | `03` FR-RATE-40..49; `04` FR-OPT-18 |
| E — Approval | `06` FR-GOV-9..21, 28 |

## 6. Timing

| Phase | Elapsed |
|---|---|
| A — Rate table work | days (this is where the commercial judgement happens) |
| B — Algorithm edits | hours, or minutes for a pure rate change |
| C — Compile | < 60 s (NFR-RATE-4) |
| D — Regression + dislocation | 30–60 min compute; hours of review |
| E — Approval | 1–5 days, dominated by committee cadence |

A **pure rate change** — no algorithm edit, no new model — skips phases A2 and B entirely
and completes C–E in a day. The specification supports that path being genuinely short;
it is the most common change an insurer makes.
