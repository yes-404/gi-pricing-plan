---
id: PL-786
family: plan
kind: leaf
title: WK-664 — the revised slice map
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-24
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-24-w6b-slice-map-revised.md
---

# WK-664 — the revised slice map

> **This supersedes [`PL-00753-wk-664-and-wk-692-the-slice-map.md`](PL-00753-wk-664-and-wk-692-the-slice-map.md) for WK-664, and
> nothing else.** That file is frozen at its date per [`README.md`](README.md) and is *not*
> edited by this one — including the rows this map contradicts. It remains the record of what
> was believed on 2026-08-22; this is the record of what is believed on 2026-08-24, after WK-692
> closed and after all eleven of its specification-backlog items were discharged.

**Written:** 2026-08-24, immediately after WK-692 closed (`e2ae7c6`, PR #165).

**Every `:NNNN` citation on this page is against `e2ae7c6`.** A line number without a tree is
not a locator: two sessions cited the WK-692 scope row correctly on 2026-08-24 and read each
other as disagreeing, because W32-7 had moved it 63 lines. Reproduce a citation against this
SHA before treating a mismatch as a disagreement.

**Scope:** everything [`../roadmap.md`](../roadmap.md) and [`../specs/`](../specs/) assign to
WK-664. WK-692's half of the 2026-08-22 map is closed and is not restated here.

---

## 1. Why a revision rather than an amendment

Three things changed under the 2026-08-22 map, and each changes the decomposition rather than
merely its status.

**WK-692 closed, so WK-664's dependency graph is now entirely internal.** All twelve WK-692 slices
merged. Every `Depends on WK-692-N` column in the frozen map is satisfied, and no WK-664 slice waits
on anything outside WK-664.

**All eleven specification-backlog items are discharged**, so the frozen map's §4 — the gate
that blocked eight of its thirteen slices — no longer gates anything. What replaced those
items is not nothing: four became requirements, and **two of those deposited new build work on
WK-664 at the moment they cleared it.** A cleared blocker is not automatically a smaller slice.

**The frozen map's gate rows have aged, one of them dangerously.** Its **line 192** tells
`W6b-11` it *"waits only on WK-692 building the header half"*. WK-692 built it, and left a
different, narrower residue. The roadmap records this deliberately at `:1076` and declines to
edit the plan: *"an edit that makes a filed plan more accurate destroys the record of what was
believed at its date, and does so invisibly, because the improved text reads as though it was
always right."* **This map is the correction's proper vehicle** — a new document that
supersedes, not an edit that overwrites.

### Slice ids are not free to renumber

`WK-664-N` ids are cited **outside this directory**: 39 citations of six ids across
[`../specs/`](../specs/) and [`../roadmap.md`](../roadmap.md) — `W6b-11` 19, `W6b-13` 11,
`W6b-3` 4, `W6b-7` 2, `W6b-1` 2, `W6b-5` 1.

Those 39 could in principle be updated. **The binding constraint is the other 55.** There are
55 further citations of WK-664 slice ids inside [`this directory`](.) itself, in filed plans that
[`README.md`](README.md) forbids editing to agree with today's repository. **Those can never
be renumbered.** So where this map splits a slice, the original id survives as an anchor and
the halves take letter suffixes — `W6b-1` becomes `W6b-1a`/`W6b-1b`, `W6b-13` becomes
`W6b-13`/`W6b-13b`. This is not a courtesy to live citations; it is forced, because the
alternative silently dangles 55 frozen ones. It is also the form WK-692 already used for `W32-1b`.

**The suffix form creates a prefix trap in both directions, and the obvious guard is the worse
half.** Anyone sweeping for a slice id must use the third form:

| Pattern | Matches | Verdict |
|---|---|---|
| `grep -E 'W6b-1'` | `W6b-1`, `-11`, `-12`, `-13`, `-13b`, `-1a`, `-1b` | noise — 7 ids where 3 were wanted |
| `grep -E 'W6b-1([^0-9a-z]\|$)'` | `W6b-1` only | **false null** — misses `W6b-1a` and `W6b-1b` |
| `grep -E 'W6b-1[a-z]?([^0-9a-z]\|$)'` | `W6b-1`, `W6b-1a`, `W6b-1b` | correct |

The guarded form is the dangerous one because **it fails to zero**, which is the shape of a
true negative. This is the same defect the WK-692 closure gate was built around — `[a-z]?` is
coverage, the separator class is safety, and neither substitutes for the other.

---

## 2. What the frozen map got wrong, and what it could not have known

Stated as findings rather than tidied away, because a revision that silently improves its
predecessor destroys the record of which was believed.

**`W6b-13`'s description no longer names its work.** The slice is titled *"Rule set threshold
editing"*, and §4 item 7 asked whether a threshold edit is a new rule version or a third
set-level override. **`FR-56` answered: a new rule version, and a Rule Set entry "gains
no third" override.** So set-level threshold editing does not exist and will not be built —
the screen is a rule *versioning* path, not an inline editor. The slice's title describes a
capability the spec has since forbidden.

**`W6b-13` then accreted three more items, three of the four now backend.** Review 4 records
the mechanism at `:564`: the WK-692 boundary was drawn by *subject matter*, but each later slice
booked its remainder onto the row that owns the **screen**, because that is the row a reader
looking for "thresholds" would search. No single booking was wrong. **The generalisation
review 4 states, and the authority for the re-cut in §3:** *"`:4455` describes the workstream;
the slice map determines the slices — description is not constraint."*

**`W6b-5`'s owner clause is description-anchored, not id-anchored.** `02:232`'s `FR-168`
reads *"Owner: the slice that builds the factor workbench's suggestion panel"* and contains
**zero** occurrences of `WK-664`. It therefore re-resolves onto whatever slice builds that panel,
whatever it is numbered. It also **spans** a view and a backend precondition: the holdout
strength ratio needs a TreeSHAP holdout pass that does not exist, and until it lands the
artifact publishes `strength` alone.

**Two cleared blockers deposited new WK-664 build scope.** `FR-398` (`07:81`) ends *"Owned by
**WK-664**"* — a local OIDC provider behind a compose profile with a checked-in realm, which is
not a Vue view and had no slice. `FR-56`'s tail declares a consequence *"unbuilt, owner
`W6b-13`"*. **"Disposed" and "no longer my problem" are different predicates.**

**A code/spec disagreement found while writing this map, and not resolved here.** `01:844`
reads *"Typed 2026-08-23 (backlog item 6)"*. The **spec** was typed that day — §4.9 gained
`DatasetLineage`. The **code** was not: `DatasetLineage` occurs in no file outside
[`../specs/01-data-management.md`](../specs/01-data-management.md), and the handler at
`backend/src/app/api/dataset_versions.py:377` still returns `dict[str, Any]`. Read as a spec
amendment the row is coherent; read as a statement about the repository it is false. **What it
undersells is the main work**: putting the shape into `model-schema` and changing the return
type, which §2's architecture rule requires and which the row's three named defects do not
cover. Recorded, not fixed — §0 reserves it, and it is proposal **P3** in §5.

**The third of those three defects is verified true on the asserts, not on the prose.**
`lineage_of` (`backend/src/app/platform/datasets.py:874-885`) returns exactly `version_id`,
`built_from` and `depends_on_this`. The handler filters on `descendants` and `ancestors`
(`:385`, `:387`) — keys it never produces — so **all three `direction` values return an
identical dict**. The filter has never filtered anything.

---

## 3. The slices

**Seventeen**, and the arithmetic is stated here rather than in §1 so that it sits beside the
number it produces — separating a count from its derivation is exactly how the first version
of this line was wrong:

> 13 from the frozen map **+1** (`W6b-1` splits) **+1** (`W6b-11` splits) **+1** (`W6b-13`
> splits) **+1** (`W6b-14`, new) = **17**

The lineage reassignment moves work between existing slices and adds none. **Re-derive this
from the table below rather than trusting the sentence** — count the rows, do not add to a
remembered total:

```
grep -cE '^\| \*\*WK-664-[0-9]+[a-z]?\*\*' docs/plans/PL-00786-wk-664-the-revised-slice-map.md
```

*Corrected 2026-08-24, before filing. The first draft said sixteen and enumerated only three
additions, omitting the `W6b-11` split — so `13 + 3 = 16` was internally consistent and simply
counted a slice that the same page had already introduced. A filed plan freezes; a wrong
self-count in one becomes the next §1 line 192, a frozen sentence a later reader has no way to
know was false. The fix is recorded rather than tidied away for that reason.*

**No slice depends on anything outside WK-664.** The `Depends on` column is now internal only.

| # | Slice | Depends on | Blocked by |
|---|---|---|---|
| **W6b-1a** | **Model detail, the non-GLM arms** — GBM, quantile intervals, the surrogate link, EBM. Narrows nothing: `ModelDetailView.vue:21-28` already declares itself the GLM arm only and names this slice | — | — |
| **W6b-1b** | **The diagnostics view** — one route, `GET /models/{slug}/diagnostics?version=` (`02` §5.1:1695), already served at `backend/src/app/api/models.py:639`; one `Diagnostics` artifact; eight charts | W6b-1a | — |
| **W6b-2** | **Model comparison** `/models/compare?ids=` | W6b-1a | — |
| **W6b-3** | **Dataset list Contents** — status badge, last validated, owner. `FR-55` landed **three** derived fields, not two: `last_validated_version` travels with `last_validated_at` and a validator refuses either alone | — | — |
| **W6b-4** | **Model spec builder** `/models/new` | W6b-1a | — |
| **W6b-5** | **Factor workbench remainder** — intent controls, interaction suggestions, inline one-ways. Carries `FR-168`, which spans this view *and* the TreeSHAP holdout pass it needs | — | — |
| **W6b-6** | **Backtest and prediction views** — both rows registered in `02` §5.3 on 2026-08-23 | W6b-1a | — |
| **W6b-7** | **Objective library and certificate** — four `CheckStatus` values, not three; `violated` is an ordinary result, not a failure | — | — |
| **W6b-8** | **Peril structure view** — and it carries **no usage count**: `FR-167` defines that quantity as Model Specs referencing the artifact, and for a Peril Structure the reference runs the other way | — | — |
| **W6b-9** | **Tabular chart fallback** (`NFR-463`) | — | — |
| **W6b-10** | **Browser authentication** (`FR-393`) — the PKCE flow in the SPA | W6b-14 | — |
| **W6b-11** | **Workspace selector, the shell** — `FR-395`, `FR-396` obligations 1–3 and `FR-397` are delivered; the selector consumes them | W6b-10 | — |
| **W6b-11b** | **The switch audit** — `FR-396` obligation 4 | W6b-11 | **OQ-652**, undecided |
| **W6b-12** | **Lineage graph** — *plus* the typed handler and the three defects moved here from `W6b-13` | — | **P3**, undecided |
| **W6b-13** | **Rule set rule-versioning screen**, and the `profiles.ts` PSI bands | W6b-13b | — |
| **W6b-13b** | **The catalogue chain** — `FR-68`'s dropped `catalogue_id` and `FR-56`'s default thresholds in the catalogue entry, replacing the seed's empty `params` for all 38 rules | — | — |
| **W6b-14** | **The local OIDC provider** (`FR-398`) — a compose profile and a checked-in realm | — | — |

### Why each split, on reviewability — never on scheduling

The mandate is strictly serialized: one executor, one slice at a time, each through planner,
arbitration, executor, arbitration, PR, merge. **So splitting never buys parallelism, and
every split costs a full cycle.** The `writing-plans` criterion is the only one that applies:
*split only where a reviewer could meaningfully reject one task while approving its neighbor.*

- **`W6b-1a`/`W6b-1b`** — a reviewer can accept the GBM/EBM detail arms while rejecting the
  diagnostics view's chart set, and the reverse. They share a type seam and nothing else.
  **`W6b-1b` is not split further**, and was tested against the objection that it is too large:
  it is one built endpoint, one artifact, and two acceptance properties that are *whole-view*
  by construction — "train/holdout side-by-side **throughout**" and a tabular equivalent per
  chart. Splitting it by chart would ship a view rendering nothing for exactly the models
  `W6b-1a` unlocks. Its size is handled by task decomposition **inside** the slice: a slice is
  the review unit, a task is the execution unit.
- **`W6b-11`/`W6b-11b`** — split by **decision state**, not by size. The shell is buildable
  today; the audit half is blocked on a maintainer decision (§5, **P1**). A reviewer can accept
  a working selector while the audit question is still open, and must be able to.
- **`W6b-13`/`W6b-13b`** — a reviewer can accept the catalogue and seed change while rejecting
  the screen. The dependency runs one way and is real: `FR-56` says the seed's empty
  `params` *"leaves the frontend re-deriving the PSI bands it should be served"*, so the
  browser fix cannot land first.
- **Lineage moving to `W6b-12`** — re-argued at its true price, which is higher than tidiness
  because it now costs a spec amendment in the same commit (§5, **P3**). It still carries: §2
  forbids hand-writing a shape that belongs in `model-schema`, so **the typed handler is a
  precondition of the graph view, not a neighbour of the threshold screen.** Leaving it on
  `W6b-13` makes `W6b-12` depend on a slice it shares no artifact with. A reviewer can accept
  the typed lineage handler while rejecting the rule-versioning screen; that is the test, and
  it passes.
- **`W6b-14`** — different artifact set, no Vue at all. A reviewer can accept the provider while
  rejecting the PKCE flow. `W6b-10` depends on it: `FR-387` claims a local provider ships
  with the compose stack and none does.

### The eight charts, enumerated

`02` §5.3:2572's Contents cell is **six comma-separated items, two carrying conjunctions**.
Both counts are used below and each is labelled, because a bare number here is ambiguous:

| # | Chart | From |
|---|---|---|
| 1 | A/E by factor | item 1 |
| 2 | Lift | item 2 |
| 3 | Double-lift | item 2 |
| 4 | Calibration | item 3 |
| 5 | Residuals | item 4 |
| 6 | GBM eval curves | item 5 |
| 7 | GBM importances | item 5 |
| 8 | CV fold dispersion | item 6 |

**Six task units, eight charts.** The eight is the number that binds `W6b-9`, because
`NFR-463` attaches a tabular equivalent to *each chart*: double-lift is not the same chart
as lift, nor importances the same as eval curves.

### What can start today

Eight slices have no unsatisfied dependency and no open blocker: **`W6b-1a`, `W6b-3`,
`W6b-5`, `W6b-7`, `W6b-8`, `W6b-9`, `W6b-13b`, `W6b-14`** — and `W6b-12` becomes a ninth if
**P3** is decided.

**`W6b-1a` first.** `W6b-2`, `W6b-4` and `W6b-6` all wait on it, so it is the only startable
slice that unblocks three others — and under a serialized mandate the head of the longest
chain is worth doing first for a reason that survives the serialization: it is not about
parallelism, it is that three slices cannot be reviewed at all until its type seam exists.

**`W6b-9` is deliberately not first**, despite being unblocked and small. It retrofits a
tabular fallback onto charts, and `W6b-1b` adds eight. Doing it first means doing it twice, and
a fallback proven against the two charts that exist today (`OneWayChart.vue`,
`HistogramChart.vue`) is a positive control run on the easy case — it goes green because of
what it does not cover.

---

## 4. The specification backlog is discharged

The frozen map's §4 gated eight of its thirteen slices. **All eleven items are resolved**; the
roadmap's dated block *"2026-08-23 — the WK-664 slice map's specification backlog is resolved"*
carries the detail. Four became requirements (`07` `FR-398`, `FR-395`, `FR-396`;
`01` `FR-56`; `02` `FR-167`), four were the spec being wrong and are corrected on
the spec's side, two were shapes that escaped the contract, and three new questions came out of
the work (`OQ-601`, `OQ-647`, `OQ-648`, all since decided).

**No WK-664 view gets a requirement, and this is settled rather than open.** `02` §5.3's amendment
block of 2026-08-23 establishes that **a view is an obligation because it has a row in a §5.3
table, not because a requirement names it** — 47 of the 51 registered views have no FR. Backlog
item 10 asked for requirements for the model detail and diagnostics views; the answer is that
the §5.3 rows already are the obligation. Writing FRs for them would invent a second register.

---

## 5. Proposals — every one with an owner slot

Under [`../../CLAUDE.md`](../../CLAUDE.md) §14 a review's output is a proposal, never a change.
**Review 4's finding 5 binds this section**: *every accepted §14 proposal gets an owning row in
the same edit that accepts it, or is explicitly marked unowned.* `scope-audit.py --params` was
accepted on 2026-08-22, given no row, and built by nobody. Where no owner can be named below,
the cell reads **unowned** in that word.

| # | Proposal | Proposed owner | Accepted |
|---|---|---|---|
| **P1** | **Decide `OQ-652`** — what tells the API a workspace selection *changed*. Its recommendation is **(b) reached through (c)'s surface**: store the previous selection *and* add an explicit `POST /api/v1/me/workspace`. That is a schema change plus a new endpoint. **Neither this map nor the work lead may pick it** (§10) | maintainer; then `W6b-11b`, **or a WK-692 successor** if decided as recommended, since the recommended shape is not browser work | *pending* |
| **P2** | **The slice re-cut in §3** — the `W6b-1` and `W6b-13` splits, the lineage reassignment, and `W6b-14`. **The `W6b-11` split is deliberately not in this row; it is P8**, because it can be rejected on its own. Authorised in principle by review 4's *"the slice map determines the slices"*; recorded here for a signature rather than assumed | this map | *pending* |
| **P3** | **Amend `01:844` in the same commit as the reassignment.** The row says *"Three code defects go with it, owner `W6b-13`"* about work §3 gives `W6b-12`. Map-only would leave spec and plan disagreeing, which §0 forbids resolving silently. **The amendment appends a dated note; it does not rewrite the clause** — an owner clause names the remainder *at the time*, and overwriting it destroys what was believed on 2026-08-23. The same note should record that `DatasetLineage` is spec-only and that typing the handler is `W6b-12`'s primary work, not a fourth defect | `W6b-12` | *pending* |
| **P4** | **The modelling PII guard is not WK-664's and must not be absorbed into it.** A column classified `direct_identifier` is fittable today: `modelling_forbidden_columns` has one runtime caller (ingestion), and nothing derives `Factor.prohibited` from the column classification. It sits on `FR-39` and `FR-90`, **outside WK-692's 27 ids**, so booking it *reassigned* would assert a custody WK-692 never had. It needs a new id and a new unit. Not a raw-PII breach — ingestion still refuses and values are tokenised — but **a stable token is a perfect-fit per-customer feature**, so it is a modelling defect and not only a governance one | **unowned** — pending a maintainer line | *pending* |
| **P5** | **`W6b-13`'s title is wrong and should be restated as rule versioning**, since `FR-56` forbids the set-level editing the title names | `W6b-13` | *pending* |
| **P6** | **Give `scope-audit.py --params` a row.** Accepted 2026-08-22; `grep -c params scripts/scope-audit.py` returns 0. Carried forward because review 4 proposed only *"give it an owner"* and named none | **unowned** | *pending* |
| **P7** | **`WK-678` owns `FR-358`**, corrected with a dated note. Carried unchanged from the frozen map's §2; the roadmap already reads this way at `:2556` | `WK-678`, Phase 3 | *pending* |
| **P8** | **The `W6b-11` split** into the selector shell and `W6b-11b`, the switch audit. Separated from **P2** rather than folded into it, because it is the one split whose justification is **expected to expire**: the other three are cut on artifact boundaries that do not move, while this one is cut on `OQ-652` being undecided. If **P1** resolves such that the audit work is not browser work at all, this split does not merely become unnecessary — `W6b-11b` **vacates**, and its obligation moves with the decision. A reviewer must therefore be able to accept the re-cut and still keep `W6b-11` whole, which a single P2 signature cannot express | `W6b-11` | *pending* |

**Highest ids in use**, verified 2026-08-24 at `e2ae7c6` by scanning [`../specs/`](../specs/) —
a maximum, not the last id read, because the tables are not in numeric order. For whoever
writes **P4**:

Highest ids in use: FR-22, NFR-464. Next free: `FR-23`, `NFR-OVR-12`.
Highest ids in use: FR-56, NFR-474. Next free: `FR-57`, `NFR-DATA-11`.
Highest ids in use: FR-168, NFR-488. Next free: `FR-169`, `NFR-MODEL-15`.
Highest ids in use: FR-397, NFR-535. Next free: `FR-394`, `NFR-PLAT-12`.
Highest ids in use: FR-362, NFR-525. Next free: `FR-GOV-46`, `NFR-GOV-9`.

---

## 6. What will bite at closure

**Frontend requirement traceability still does not exist**, and WK-664 is the workstream it will
be judged by. Backend tests carry `@pytest.mark.req`, which `scripts/req-coverage.py` reads;
the frontend convention is prose in the `it(...)` string, which nothing machine-reads. Carried
forward from the frozen map's §5 unchanged, because **that half was never discharged** — the
2026-08-24 instruction reached the other hazard and not this one. §13 rule 1 accepts a closure
record stating why a test is the wrong instrument there. It does not accept silence.

**`FR-396`'s eventual test must assert the rule, not the symptom.** The obligation is *"a
switch is audited into both chains"*. A test asserting that `record_switch` has a call site
**goes green on the first call site anyone adds**, leaving the guarantee false. This is the
convention adopted at WK-692's close, and `W6b-11b` is the slice it was written for.

**`NFR-488` is booked forward as *delivered but untested*** and is not WK-664's, but whoever
touches the partial-dependence path should know the budget rests on a WK-661 bench from 2026-08-22
(0.0480 fits per pass against a 0.06 ceiling) taken before W32-5 changed how `exposure_share`
is computed. Also: `test_gbm.py:1879` mentions the id in a **docstring, not a
`@pytest.mark.req` marker**, so a grep finds it and it binds nothing.

---

## 7. Maintainer acceptance

Nothing on this page binds until accepted. The frozen map's own acceptance table is not
restated here and is not superseded by this one; where the two overlap, that file records
2026-08-22's decisions and this one records what is proposed now.

| Proposal | Accepted |
|---|---|
| The seventeen-slice decomposition in §3 (**P2**) | *pending* |
| **P8** the `W6b-11` split — separable from P2, and **vacates** if P1 goes the other way | *pending* |
| The sequencing in §3, and `W6b-1a` first | *pending* |
| **P1** `OQ-652` — and it may not be decided by a session | *pending* |
| **P3** the `01:844` amendment, landing in the same commit as the reassignment | *pending* |
| **P4** the PII guard as a new unit — **unowned** until this line names one | *pending* |
| **P5**, **P6** and **P7** | *pending* |
