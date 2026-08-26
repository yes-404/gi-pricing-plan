# W6b — the slice map, revised again

> **This supersedes [`2026-08-24-w6b-slice-map-revised.md`](2026-08-24-w6b-slice-map-revised.md) for
> W6b, and nothing else.** [`README.md`](README.md) freezes that file at its date. This map does
> not edit that file. The rows this map contradicts stay in that file. That file records what was
> believed on 2026-08-24. This file records what is believed on 2026-08-26. Four decisions landed
> since 2026-08-24. Each decision changes the decomposition, not only its status.

**Written:** 2026-08-26, after the `OQ-OVR-12`, `OQ-PLAT-12` and `OQ-MODEL-34` rulings, the
W6b-12 plan (PR #244) and the W6b-14 merge (PR #245).

**Every `:NNNN` citation on this page is against `70934c1`.** A line number without a tree is not
a locator. Reproduce a citation against this SHA first. Treat a mismatch as a disagreement only
after reproduction.

**Scope:** this map covers everything [`../roadmap.md`](../roadmap.md) and [`../specs/`](../specs/)
assign to W6b. This map does not restate the previous revision's scope statement. The 2026-08-24
map and its frozen predecessor stay the record of their dates.

---

## 1. Why a revision rather than an amendment

Four things changed since 2026-08-24. Three of them change the decomposition, not only its status.

**The `_minor` rename became mechanical work.** `OQ-OVR-12` decision (b) landed 2026-08-25 via
PR #235 (squash `2010d50`). Burning cost is a statistic. The integer type stays. The suffix is the
defect, not the type. The decision releases the rename as mechanical work. No slice existed for
this work. This map attaches `W6b-15`.

**`OQ-PLAT-12` was decided, and `W6b-11b` vacates exactly as the previous map predicted.** The
previous map's P8 wrote the vacate in words: *"if P1 resolves such that the audit work is not
browser work at all, this split does not merely become unnecessary — `W6b-11b` vacates, and its
obligation moves with the decision"*. The decision matches that text. A switch is a human act.
`POST /api/v1/me/workspace` audits through `record_switch`. The decision text leaves the slice
assignment to this revision. The rest of obligation 4 is the endpoint, the switcher's call,
and the first-selection routes. The W6b-11 plan's header says the same in as many words. That plan
files under the manager's disposition. This revision formalises what that plan already records.
The work is `W6b-11`'s.

**`OQ-MODEL-34` was ruled, and the change set needs a slice.** Ruling (c) landed 2026-08-26. The
server derives the surrogate slug at reservation. The 64-char refusal moves with the derivation.
`FR-MODEL-102` gets an amendment. The version half becomes `OQ-MODEL-43`. The change set merged
as one PR (spec + code + tests, PR #246, squash `70934c1`). No map row carried the change set.
This map attaches `W6b-16`.

**The allocation aid was stale in three families.** The corrected line now has a published form.
The 08-24 map's "Highest ids in use" block says `FR-DATA-55` is next free. `#197` minted
`FR-DATA-56` before that line. The W6b-12 plan header publishes the corrected line. Next free: `FR-DATA-57`, `NFR-DATA-11`, `OQ-DATA-16`. The OVR and PLAT families moved too. `FR-OVR-19` became
`FR-OVR-22`. `FR-PLAT-65` became `FR-PLAT-66`. Decisions minted `FR-OVR-20/21/22` and
`FR-PLAT-66`. A DM sweep confirms that the map before 08-24 carried the same stale aid.
§5 re-derives every family.

**Since the 08-24 map, seventeen slices merged.** The previous map's table is a historical
record. §3 carries each row's state.

**One thing this revision is *not*: the gap-list revision.** The auditor's gap list arrives at
the all-slices completeness audit. That audit happens at close. The gap list folds into the map
then. This page is filed from the four attachments above. §5's **P10** records that boundary. The
acceptance table then knows what it signs.

### Slice ids are not free to renumber

The constraint from the previous map is unchanged. It still binds. `W6b-N` ids appear in
`../specs/` and `../roadmap.md`. They also appear in filed plans inside this directory.
`README.md` forbids the amendment of filed plans to agree with today's repository. That half is the binding
half. A split keeps the original id as an anchor. The halves take letter suffixes
(`W6b-4a`/`W6b-4b`). An id is never reused. The suffix form creates the same prefix trap in both
directions. The guarded form is still the dangerous one. It fails to zero:

| Pattern | Matches | Verdict |
|---|---|---|
| `grep -E 'W6b-1'` | `W6b-1`, `-11`, `-12`, `-13`, `-13b`, `-1a`, `-1b` | noise — 7 ids where 3 were wanted |
| `grep -E 'W6b-1([^0-9a-z]\|$)'` | `W6b-1` only | **false null** — misses `W6b-1a` and `W6b-1b` |
| `grep -E 'W6b-1[a-z]?([^0-9a-z]\|$)'` | `W6b-1`, `W6b-1a`, `W6b-1b` | correct |

---

## 2. What the 08-24 map did not record

This section states findings. It does not tidy them away. A revision that silently improves its
predecessor destroys the record of which was believed.

**P1's recommendation is not what the decision chose.** The 08-24 map's P1 recommended
*"(b) reached through (c)'s surface"*. That option stores the previous selection and adds
`POST /api/v1/me/workspace`. The decision is (c) alone. A switch is a human act. The endpoint
audits through `record_switch`. `require_caller` audits nothing. The per-request `Workspace-Id`
header (`FR-PLAT-65`) already carries selection. Both readings refuse the stored-selection half.
A principal-level "current workspace" cannot represent two open tabs. `FR-PLAT-65` made the
selection per-request to support that case. The map's own P8 row read the risk correctly. That
split cut on a decision state. The decision came down on the side that vacates it.

**The map's rows split further at plan time.** The `W6b-5` split matches the frozen map's own
finding. `W6b-4` became `W6b-4a`/`W6b-4b`. That split separates the builtin arm from the custom
objective arm. `W6b-5` became `W6b-5a`/`W6b-5b`. `W6b-6` became `W6b-6`/`W6b-6b`. That split
separates the backtest view from the prediction view. The `W6b-5` split is the one that matters.
The 08-24 map found that `FR-MODEL-128` "spans a view *and* a backend precondition". The holdout
strength ratio needs a TreeSHAP holdout pass. That pass did not exist. The plans drew the boundary
exactly there. `W6b-5a` is the holdout pass. `W6b-5b` is the suggestion panel. The requirement's
owner clause names that surface: *"the slice that builds the factor workbench's suggestion
panel"* (`02:232`, zero `W6b` occurrences). The clause re-resolves onto `W6b-5b`. Both merged.

**`OQ-PLAT-12`'s second amendment added routes to obligation 4's remainder.** The first-selection
ruling (PR #237, squash `d93cdf9`) found a deadlock. The SPA's first selection was impossible.
Memberships come from the platform database. `/me` sits behind `require_caller`. The list the
choice comes from was unreadable until the choice existed. The ruling added an unscoped
`GET /api/v1/me/workspaces`. That route is list-only. The switch endpoint accepts an absent
`Workspace-Id` as `left=None`. The first selection writes one event. Those routes join
the rest of obligation 4. They join `W6b-11` with it.

**The id-ceiling lines aged in three families.** §5 re-derives all of them. The pattern is the
point here. A ceiling is a fact about the tree at a SHA. The 08-24 map's lines were the fact at
`e2ae7c6`.

**The roadmap's slice-state rows drifted.** Three rows contradict merged builds. §6 quotes and
corrects each row. The roadmap is not the slice inventory. This map is. A close audit will read
the roadmap. Phantom "not started" rows will hide progress the repository has.

---

## 3. The slices

Twenty-one live slices, plus one tombstone. The arithmetic sits beside the number it produces:

> The 08-24 map has 17 slices. The plan-time splits add 3 (`W6b-4`, `W6b-5`, `W6b-6`, each +1).
> The new slices add 2 (`W6b-15`, `W6b-16`). The table has 22 rows. `W6b-11b` vacates and stays as
> a tombstone row. The live count is 21.

Re-derive this from the table below. Do not trust the sentence. Count the rows. Do not add to a
remembered total:

```
grep -cE '^\| \*\*W6b-[0-9]+[a-z]?\*\*' docs/plans/2026-08-26-w6b-slice-map-revised-2.md
```

No slice depends on anything outside W6b. The `Depends on` column is internal only. It was
internal in the previous revision too. `State` is as of the anchor SHA. "Merged" means the build's
squash is on `main`.

| # | Slice | Depends on | Blocked by | State |
|---|---|---|---|---|
| **W6b-1a** | **Model detail, the non-GLM arms** — GBM, quantile intervals, the surrogate link, EBM | — | — | merged |
| **W6b-1b** | **The diagnostics view** — one route, one `Diagnostics` artifact, eight charts | W6b-1a | — | merged |
| **W6b-2** | **Model comparison** `/models/compare?ids=` | W6b-1a | — | merged |
| **W6b-3** | **Dataset list Contents** — status badge, last validated, owner | — | — | merged |
| **W6b-4a** | **Model spec builder, the builtin arm** | W6b-1a | — | merged |
| **W6b-4b** | **Custom objective arm** | W6b-1a | — | merged |
| **W6b-5a** | **The TreeSHAP holdout pass** — `FR-MODEL-128`'s backend precondition | — | — | merged |
| **W6b-5b** | **The suggestion panel** — `FR-MODEL-128`'s owner clause names this surface | W6b-5a | — | merged |
| **W6b-6** | **Backtest view** | W6b-1a | — | merged |
| **W6b-6b** | **Prediction view** | W6b-1a | — | merged |
| **W6b-7** | **Objective library and certificate** | — | — | merged |
| **W6b-8** | **Peril structure view** | — | — | merged |
| **W6b-9** | **Tabular chart fallback** (`NFR-OVR-10`) | — | — | merged |
| **W6b-10** | **Browser authentication** — `FR-PLAT-55`'s PKCE flow and `FR-PLAT-66`'s `/api/v1/auth/config` channel | W6b-14 | — | plan merged (`88a9c3e`, amended `845f298`). Build in progress |
| **W6b-11** | **Workspace selector, the shell** — plus obligation 4's remainder (the switch endpoint, the unscoped memberships route, the switcher's call and the `x-dev-workspace-id` removal), formalised here from the manager's disposition | W6b-10 | — | plan merged (`11cadbd`). Build queued behind W6b-10 |
| **W6b-11b** | **The switch audit** — `FR-PLAT-63` obligation 4 | — | — | **vacated** — `OQ-PLAT-12` decided (c). Obligation 4 folded into W6b-11 |
| **W6b-12** | **Lineage graph** — the typed handler, the graph view, the `01:844` amendment (P3, landed in the plan's own commit) | — | — | plan merged (`5496c3e`). Build queued behind W6b-10/11 |
| **W6b-13** | **Rule set rule-versioning screen**, and the `profiles.ts` PSI bands | W6b-13b | — | merged |
| **W6b-13b** | **The catalogue chain** — `FR-DATA-53`'s dropped `catalogue_id` and `FR-DATA-54`'s default thresholds | — | — | merged |
| **W6b-14** | **The local OIDC provider** (`FR-PLAT-58`) — a compose profile and a checked-in realm, seeded `workspace_members` | — | — | plan merged (`dcb0823`). Build merged (`bc1d880`) |
| **W6b-15** | **The `_minor` rename** — `OQ-OVR-12` decided (b): statistics mislabelled `_minor` drop the suffix under `FR-OVR-20`. The integer type stays. Known members: `observed_burning_cost_minor`/`modelled_burning_cost_minor` (`model-schema/perils.py:290,306-307`, `pricing-core/modelling/perils.py:85,93-94`) and the `validate.py` names `FR-OVR-20` cites (`:1072-1073`, `:1077-1078`). The plan sweeps the class. `claim_amount_minor` (a column name) and `total_negative_minor` (`int(...)`-cast) conform and stay | — | — | plan not started — released mechanical work |
| **W6b-16** | **The surrogate slug derivation** — `OQ-MODEL-34` ruled (c): `reserve_model` derives `source_family_slug + "-approx"` at reservation and overrides the caller's. The 64-char refusal moves with the derivation. `FR-MODEL-102` amended. The version half raised as `OQ-MODEL-43` | — | — | merged (`70934c1`) — the change set shipped as PR #246 (spec + code + tests) |

### Why the two new slices pass the reviewability test

The mandate is strictly serialized. One executor runs one slice at a time. Each slice passes
planner, arbitration, executor, arbitration, PR, merge. A split never buys parallelism. The
`writing-plans` criterion is the only one that applies. Split only where a reviewer can reject one
task and approve its neighbor.

- **`W6b-15`** — a reviewer can accept the rename's class sweep. There is nothing else near it.
  It touches `model-schema`, `pricing-core` and the generated contracts. No other live slice
  shares that artifact set.
- **`W6b-16`** — its review unit already exists as PR #246. A reviewer can accept the derivation
  and the refusal move. That reviewer can reject any other slice. The change ships as one PR. The
  repo rule says a change across spec and code lands as one commit. The slice and the PR are
  the same boundary.

### What can start today

The executor's queue follows the manager's disposition. This map does not re-open it. `W6b-14`'s
build merged as PR #245. `W6b-10`'s build is in progress. `W6b-11` builds after it. `W6b-12`'s
build is queued behind them. `W6b-16`'s change set merged as PR #246. It had no plan gate.
`W6b-15` is the one slice whose plan a writer can write at any time. It is unblocked and
mechanical. Its class definition (`FR-OVR-20`) is already in the spec.

---

## 4. The four decisions, each with its slice consequence

**`OQ-OVR-12` decided (b) — PR #235, squash `2010d50`.** Burning cost is a statistic. The integer
stays. The rounded-parts sum at `model-schema/perils.py:364-367` is the reason. The suffix is
`FR-OVR-20`'s defect, not a value defect. The released work is mechanical. This map attaches it as
**`W6b-15`**. §3's row carries the known members and the exceptions that conform.

**`OQ-PLAT-12` decided (c) — PR #231 (squash `8d778ed`), amended by PR #237 (squash `d93cdf9`).**
A switch is a human act. `POST /api/v1/me/workspace` audits through `record_switch`.
`require_caller` audits nothing. `W6b-11b` vacates. The previous map's P8 said the vacate follows
a decision that makes the audit work not-browser-work. The decision did that. The rest of obligation 4
goes to **`W6b-11`**. That work is the endpoint, the unscoped
`GET /api/v1/me/workspaces`, and the switch that accepts absent `Workspace-Id` as `left=None`.
The plan already records the fold. It names this revision as the vehicle that formalises it.

**`OQ-MODEL-34` ruled (c) — PR #246, squash `70934c1`.** The server derives the slug
at reservation. The slug is `source_family_slug + "-approx"`. The 64-char refusal moves with the
derivation. No extra query results. The mismatch guard already fetches the source spec. The
worker's refusal becomes unreachable belt-and-braces. `FR-MODEL-102` reads "at reservation". This
map attaches the change set as **`W6b-16`**. The version half is not part of it. It is
`OQ-MODEL-43`, open.

**The ceiling correction, next free: `FR-DATA-57`.** The 08-24 map's `FR-DATA-55` next-free line predated
`#197`'s `FR-DATA-56`. §5 publishes the corrected lines for every family. The DATA line matches
the W6b-12 plan's header.

**The gap list folds in at close.** The auditor's completeness findings land at the all-slices
audit. They do not land in this page. **P10** records that. A later reader then knows what this
map was filed from.

---

## 5. Proposals — every one with an owner slot

Under [`../../CLAUDE.md`](../../CLAUDE.md) §14 a review's output is a proposal, never a change.
Review 4's finding 5 binds this section. Every accepted §14 proposal gets a row and an owner in the
same edit that accepts it. Or the row is explicitly marked unowned. Where no owner can be named
below, the cell reads **unowned** in that word.

| # | Proposal | Proposed owner | Accepted |
|---|---|---|---|
| **P1** | **Decide `OQ-PLAT-12`** — **decided 2026-08-25 (c)**, not as recommended. `POST /api/v1/me/workspace` audits through `record_switch`. `require_caller` audits nothing. The stored-selection half is refused. Consequence: `W6b-11b` vacates. Obligation 4 goes to `W6b-11` (this map's §3/§4) | maintainer, then `W6b-11` | *decided* |
| **P2** | **The 08-24 re-cut in that map's §3** — superseded. This map's §3 is the re-cut now in force. It awaits signature as **P9** | this map | *superseded* |
| **P3** | **Amend `01:844` in the same commit as the lineage reassignment** — **signed**. It landed with the W6b-12 plan (PR #244, squash `5496c3e`). The typed handler is that plan's Task 2 | `W6b-12` | *signed* |
| **P4** | **The modelling PII guard is not W6b's and must not be absorbed into it** — carried unchanged. No maintainer line has landed since 08-24. Nothing in the roadmap names it. A column classified `direct_identifier` is still fittable. It sits on `FR-DATA-13`/`FR-MODEL-5`. It needs a new id and a new unit | **unowned** — pending a maintainer line | *pending* |
| **P5** | **`W6b-13`'s title restated as rule versioning** — **adopted**. The plan is `2026-08-25-w6b-13-rule-versioning-screen.md`. The slice's name and its plan agree | `W6b-13` | *adopted* |
| **P6** | **Give `scope-audit.py --params` a row** — carried unchanged. `grep -c params scripts/scope-audit.py` returns 0 at the anchor SHA. Accepted 2026-08-22. Still no row. Still built by nobody | **unowned** | *pending* |
| **P7** | **`W18` owns `FR-GOV-16`** — resolved by the record. The roadmap's own dated correction (2026-08-23) stands at `:2564`. The Phase 3 workstream table reads "Phase 3, W18" at `:2248`. The correction stands where the wrong owner stood. Nothing further to sign | `W18`, Phase 3 | *resolved* |
| **P8** | **The `W6b-11` split** — vacated with P1. Its own wording predicted this. The audit work turned out not to be browser work. `W6b-11b` is a tombstone. The obligation moved with the decision | — | *vacated* |
| **P9** | **The re-cut in §3** — 21 live slices, the `W6b-11b` tombstone, the two new slices, and the obligation-4 assignment to `W6b-11`. The assignment formalises what its plan already records. Review 4's *"the slice map determines the slices"* authorises it in principle. This map records it for a signature rather than assumes it | this map | *pending* |
| **P10** | **The gap list folds into the close-time completeness audit, not into this revision** — the auditor's findings arrive at the all-slices audit at close. They enter the slice inventory then. This map is filed from the four attachments of §4 | the close (W6b close slice), maintainer | *pending* |

**Highest ids in use**, verified 2026-08-26 at the anchor SHA with a scan of
[`../specs/`](../specs/). Use a maximum, not the last id read. The tables are not in numeric
order. Each line carries its correction to the 08-24 map's block in parentheses:

Highest ids in use: FR-OVR-22, NFR-OVR-11, OQ-OVR-16. Next free: `FR-OVR-23`, `NFR-OVR-12`, `OQ-OVR-17`. *(08-24 said FR-OVR-19 — `FR-OVR-20/21/22` were minted by decided questions.)*
Highest ids in use: FR-DATA-56, NFR-DATA-10, OQ-DATA-15. Next free: `FR-DATA-57`, `NFR-DATA-11`, `OQ-DATA-16`. *(08-24 said FR-DATA-55. `#197` minted `FR-DATA-56`. The W6b-12 plan's header first published the corrected line.)*
Highest ids in use: FR-MODEL-128, NFR-MODEL-14, OQ-MODEL-43. Next free: `FR-MODEL-129`, `NFR-MODEL-15`, `OQ-MODEL-44`. *(OQ-MODEL-43 minted with PR #246. The 08-24 block carried no OQ lines.)*
Highest ids in use: FR-PLAT-66, NFR-PLAT-11, OQ-PLAT-17. Next free: `FR-PLAT-67`, `NFR-PLAT-12`, `OQ-PLAT-18`. *(08-24 said FR-PLAT-65 — `OQ-PLAT-17` decided (a) as `FR-PLAT-66`.)*
Highest ids in use: FR-GOV-45, NFR-GOV-8, OQ-GOV-8. Next free: `FR-GOV-46`, `NFR-GOV-9`, `OQ-GOV-9`. *(unchanged.)*

---

## 6. What will bite at closure

**Three rows of the roadmap contradict merged builds.** A close audit that reads the roadmap will
report phantom "not started" rows. Quoted against the anchor SHA, with the correction:

- The `/peril-structures/{id}` row reads *"Not started. Owner: W6b, unchanged"* — the W6b-8
  build (peril structure views) is merged. Correction: delivered.
- The accessibility row reads *"`NFR-OVR-10`'s tabular fallback for charts is **not** built;
  owner W6b"* — the W6b-9 build (chart-table retrofit) is merged. Correction: delivered.
- The W6b-11 gate text reads *"now waits only on W32 building the header half"*. That amendment
  is dated 2026-08-23, the day before W32 closed. W6b-11 does not wait on W32. It waits on
  `W6b-10`. `FR-PLAT-63`'s amendment says so. Correction: dependency is internal.

The roadmap is not the slice inventory. This map is. The close's §13 audit derives scope from the
specification first. The roadmap is a specification artifact. The drift is recorded here. The
close then does not re-derive it as a finding about the builds.

**Carried from the previous revision. Still in force.** Frontend requirement traceability does
not exist. Backend `@pytest.mark.req` markers are machine-read. Frontend `it(...)` prose is not.
W6b is the workstream closure will judge it by. §13 rule 1 accepts a closure record that states
why a test is the wrong instrument. It does not accept silence. `FR-PLAT-63`'s test must assert
the rule, not the symptom. Obligation 4's build now belongs to `W6b-11`. The test asserts that a
switch writes into **both** chains. It never asserts that `record_switch` has a call site. That
assertion goes green on the first call site anyone adds. `NFR-MODEL-14` stays booked forward as
*delivered but untested*. It is a W5 bench from 2026-08-22, not W6b's. `test_gbm.py:1879` mentions
it in a docstring rather than a marker.

**`OQ-MODEL-43` stays open.** The W6b-16 change set resolves the slug half of `OQ-MODEL-34`
only. `approximates_model_id` still has no companion version field. A slug-derived link can land
on a source version the surrogate does not approximate. Closure must not book the change set as the row's
resolution.

---

## 7. Maintainer acceptance

Nothing on this page binds until accepted. This page does not restate the previous revision's
acceptance table. This page does not supersede it. Where the two overlap, that file records
2026-08-24's decisions. This one records what is proposed now.

| Proposal | Accepted |
|---|---|
| The twenty-one-slice decomposition in §3 (**P9**), with the `W6b-11b` tombstone and the two new slices | *pending* |
| The obligation-4 assignment to `W6b-11` — it formalises what its plan already records | *pending* |
| The sequencing in §3 — `W6b-10` in build, then `W6b-11`, then `W6b-12`. `W6b-15`'s plan can land at any time | *pending* |
| **P10** the gap-list fold-in at close — this revision is filed from the four attachments, not from the gap list | *pending* |
| **P4** the PII guard as a new unit — **unowned** until this line names one | *pending* |
| **P6** `scope-audit.py --params` — **unowned** | *pending* |
