# W6b — the slice map, revised a third time

> **This supersedes [`2026-08-26-w6b-slice-map-revised-2.md`](2026-08-26-w6b-slice-map-revised-2.md) for
> W6b, and nothing else.** [`README.md`](README.md) freezes that file at its date. This map does
> not edit that file. The rows this map contradicts stay in that file. That file records what was
> believed on 2026-08-26 before the OQ filing. This file records what is believed on 2026-08-26
> after it. Eight decisions landed since that revision. Each decision changes the decomposition,
> not only its status.

**Written:** 2026-08-26, after the OQ filing (PR #255, squash `7400846`) and the manager's
disposition of the eight build slices.

**Every `:NNNN` citation on this page is against `7400846`.** A line number without a tree is not
a locator. Reproduce a citation against this SHA first. Treat a mismatch as a disagreement only
after reproduction.

**Scope:** this map covers everything [`../roadmap.md`](../roadmap.md) and [`../specs/`](../specs/)
assign to W6b. This map does not restate the previous revision's scope statement. The earlier
revisions stay the record of their dates.

### Slice ids are not free to renumber

The constraint from the previous map is unchanged. It still binds. `W6b-N` ids appear in
[`../specs/`](../specs/) and [`../roadmap.md`](../roadmap.md). A split keeps the original id as an
anchor. The halves take letter suffixes (`W6b-4a`/`W6b-4b`). An id is never reused.

---

## 1. Why a revision rather than an amendment

The OQ filing closed all thirty questions and four confirmations. The register rows carry the
strikes. The §10 mirrors carry the DECIDED markers. The gate table reads 0 open. Most of those
decisions carry no build work. Eight carry build work. The filing's own queued-slice summary
classifies that work. No slice-map row existed for any of it. This map attaches the eight slices
the manager named: the MODEL-43 contract, DATA-12, DATA-13, OVR-14, OVR-15 (a), PLAT-10, PLAT-11
and PLAT-16.

**The attachment has a boundary.** The filing's queued-slice summary names more than eight items.
The items the manager did not attach stay in that queue: OQ-DATA-14's two halves, OQ-DATA-15's
report projection and badge, OQ-MODEL-42's selection-time validation, OQ-PLAT-15's coverage fix,
the shared-trigger group and the trigger-specific group. This map does not attach them. A close
audit reads them from the filing, not from this page.

**The #136 build precedes the eight.** The route-reachability plan (PR #254) merged at `790f661`.
Its build has no slice-map row and mints no ids. The eight new slices queue after that build.

---

## 2. What the 08-26 map did not record

This section states findings. It does not tidy them away. A revision that silently improves its
predecessor destroys the record of which was believed.

**The OQ build surface had no rows.** The filing struck the questions. It did not attach the
builds. The 08-26 map's §3 table ends at `W6b-16`. The queued-slice summary classifies the
build work, and the manager's disposition attaches eight of it. This map records the attachment.

**The filing left the substantive spec amendments to the builds.** The register rows and the
mirrors now carry the decision text and the DECIDED markers. The amendments that carry builds
did not land with the filing: the new 02 FR for MODEL-43, the FR-DATA-51 sentence for OVR-15 (a),
00 §5.3's currency sentence for OVR-14, 01 §4.6's example for DATA-12, 01 §5.2 for DATA-13, and
the 07 texts for PLAT-10, PLAT-11 and PLAT-16. One amendment did land: OQ-DATA-15's FR-DATA-57
filed with the strike (`01:121`). A close audit that greps the specs for these amendments finds
nothing until the slices file them.

**The next-free line for the DATA family is spent.** The 08-26 map published FR-DATA-57 as next
free. The filing minted it at `01:121`. §5 re-derives every line.

**The DATA-13 sequencing premise does not match the W6b-12 build state.** The decision says
"sequenced with W6b-12 (the lineage handler types against it)". At this anchor the W6b-12 build's
lineage handler types against `DatasetVersionRow` (`backend/src/app/platform/datasets.py:31`),
not the schema `DatasetVersion`. The build sits at its final gate. The executor must verify the
real dependency at slice start. The slice row carries this flag.

---

## 3. The slices

Twenty-nine live slices, plus one tombstone. The arithmetic sits beside the number it produces:

> The 08-26 map has 21 live slices and one tombstone. The new slices add 8 (`W6b-17` to
> `W6b-24`). The table has 30 rows. `W6b-11b` stays a tombstone. The live count is 29.

Re-derive this from the table below. Do not trust the sentence. Count the rows. Do not add to a
remembered total:

```
grep -cE '^\| \*\*W6b-[0-9]+[a-z]?\*\*' docs/plans/2026-08-26-w6b-slice-map-revised-3.md
```

No slice depends on anything outside W6b. The `Depends on` column is internal only. It was
internal in the previous revision too. `State` is as of the anchor SHA. "Merged" means the
build's squash is on `main`.

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
| **W6b-10** | **Browser authentication** — `FR-PLAT-55`'s PKCE flow and `FR-PLAT-66`'s `/api/v1/auth/config` channel | W6b-14 | — | merged (`c56ec75`, PR #250) |
| **W6b-11** | **Workspace selector, the shell** — plus obligation 4's remainder (the switch endpoint, the unscoped memberships route, the switcher's call and the `x-dev-workspace-id` removal) | W6b-10 | — | merged (`fb7e722`, PR #252) |
| **W6b-11b** | **The switch audit** — `FR-PLAT-63` obligation 4 | — | — | **vacated** — `OQ-PLAT-12` decided (c). Obligation 4 folded into W6b-11 |
| **W6b-12** | **Lineage graph** — the typed handler, the graph view, the `01:844` amendment (P3, landed in the plan's own commit) | — | — | plan merged (`5496c3e`). Build in progress — final gate at the anchor |
| **W6b-13** | **Rule set rule-versioning screen**, and the `profiles.ts` PSI bands | W6b-13b | — | merged |
| **W6b-13b** | **The catalogue chain** — `FR-DATA-53`'s dropped `catalogue_id` and `FR-DATA-54`'s default thresholds | — | — | merged |
| **W6b-14** | **The local OIDC provider** (`FR-PLAT-58`) — a compose profile and a checked-in realm, seeded `workspace_members` | — | — | plan merged (`dcb0823`). Build merged (`bc1d880`) |
| **W6b-15** | **The `_minor` rename** — `OQ-OVR-12` decided (b): statistics mislabelled `_minor` drop the suffix under `FR-OVR-20`. The integer type stays. Known members: `observed_burning_cost_minor`/`modelled_burning_cost_minor` (`model-schema/perils.py:290,306-307`, `pricing-core/modelling/perils.py:85,93-94`) and the `validate.py` names `FR-OVR-20` cites (`:1072-1073`, `:1077-1078`). The plan sweeps the class. `claim_amount_minor` (a column name) and `total_negative_minor` (`int(...)`-cast) conform and stay | — | — | plan merged (`47d1375`, PR #251). Build queued |
| **W6b-16** | **The surrogate slug derivation** — `OQ-MODEL-34` ruled (c): `reserve_model` derives `source_family_slug + "-approx"` at reservation and overrides the caller's. The 64-char refusal moves with the derivation. `FR-MODEL-102` amended. The version half raised as `OQ-MODEL-43` | — | — | merged (`70934c1`) — the change set shipped as PR #246 (spec + code + tests) |
| **W6b-17** | **The GlmSpec companion address** — `OQ-MODEL-43` decided (a): a `slug@version` pair on GlmSpec that follows IntervalFor (`FR-MODEL-78`/`FR-MODEL-100`) and joins `spec_hash` (`FR-MODEL-86`). The id stays the lookup key. `SPEC_HASH_VERSION` bumps v10 to v11 with a lineage comment (`backend/src/app/platform/modelling.py:146`). The 02 FR text files with this slice | — | — | not started — queued after the #136 build |
| **W6b-18** | **The Offending Sample item shape** — `OQ-DATA-12` decided (b): the item is a keyed object, the item shape written out. `pricing-core` emits it. 01 §4.6's example, the tests and the contract regen land with it | — | — | not started — queued after the #136 build |
| **W6b-19** | **DatasetVersion catches up to its contract** — `OQ-DATA-13` decided (c): 14 flat fields adopt the contract's scalars, 3 structural fields adopt its object forms. A migration carries the shape change. 01 §5.2 updates with it. The decision sequences it with W6b-12. The executor verifies that premise at slice start (§2) | W6b-12 | — | not started — queued after the #136 build |
| **W6b-20** | **The views read the dataset's currency** — `OQ-OVR-14` decided (b): `getDataset(slug)` supplies the currency. The `?? "GBP"` fallbacks delete. 00 §5.3 records the rule | — | — | not started — queued after the #136 build |
| **W6b-21** | **The owner display, interim** — `OQ-OVR-15` decided (c) with (a) as the near-term step: the list endpoint resolves `owner_id` beside `latest_version_status`. FR-DATA-51 gains the resolved-name sentence. The (c) route defers with the shared trigger | — | — | not started — queued after the #136 build |
| **W6b-22** | **The one-sidedness registry** — `OQ-PLAT-10` decided (b): a slug one-sided on purpose declares it in one registry. Anything one-sided and undeclared fails. The stale `peril-structure` comment fixes. F2 subsumes | — | — | not started — executor small fix, queued after the #136 build |
| **W6b-23** | **The revalidation sweep** — `OQ-PLAT-11` decided (c) now: a script parses every stored artifact against today's models. The report names what no longer reads. 07 records the migration-event rule | — | — | not started — executor small fix, queued after the #136 build |
| **W6b-24** | **Two generated type sets** — `OQ-PLAT-16` decided (c): `generate:api` runs twice over the same OpenAPI, once with `--default-non-nullable` and once without. Request bodies alias the permissive set, responses keep the strict set. The three `as unknown as ModelSpec` casts remove. 07 documents the flag | — | — | not started — queued after the #136 build |

### Why the eight new slices pass the reviewability test

The mandate is strictly serialized. One executor runs one slice at a time. Each slice passes
planner, arbitration, executor, arbitration, PR, merge. A split never buys parallelism. The
`writing-plans` criterion is the only one that applies. Split only where a reviewer can reject one
task and approve its neighbor.

- **`W6b-17`** — one contract field, one `spec_hash` bump, one spec text, one regen. No other
  live slice shares that artifact set.
- **`W6b-18`** — the emission change, its tests and one example. `pricing-core` is its own
  package.
- **`W6b-19`** — a model-schema shape change plus a migration. The migration is the unit a
  reviewer can accept or reject.
- **`W6b-20`** — two views and their tests. The money defect is one slice's.
- **`W6b-21`** — one list endpoint, one column, one FR-DATA-51 sentence. The (c) route is not
  part of it.
- **`W6b-22`** — the guard, one comment, one registry. Its test asserts the declared-versus-
  undeclared rule.
- **`W6b-23`** — one script, one report, one 07 rule sentence.
- **`W6b-24`** — one `package.json` change, one VCS-ignored artifact, one view. A reviewer can
  accept the type sets and reject a cast.

### What can start today

The executor's queue follows the manager's disposition. This map does not re-open it. The eight
new slices queue after the #136 build. Within the eight, `W6b-17`, `W6b-18` and `W6b-19` precede
`W6b-24`, so its second generation reads the final contract.
`W6b-19` verifies the W6b-12 sequencing premise before it plans. The executor small fixes
(`W6b-22`, `W6b-23`) run where the manager places them.

---

## 4. The eight decisions, each with its slice consequence

**`OQ-MODEL-43` decided (a) — register row 107, struck at `7400846`.** GlmSpec gains a companion
`slug@version` address that follows IntervalFor and joins `spec_hash`. The id stays the lookup
key. The queued slice names the executor: 02's new FR text, `packages/model-schema/src/model_schema/modelling.py`, `backend/src/app/platform/modelling.py`, and the contract regen. This map attaches it as **`W6b-17`**. The 02 FR id is allocated in §5. The id stays undefined until the slice files it.

**`OQ-DATA-12` decided (b) — register row 56, struck at `7400846`.** The Offending Sample item is
a keyed object, the item shape written out. The queued slice names the executor:
`packages/pricing-core` (sample emission), the pricing-core tests (`test_validate.py`,
`test_catalogue.py`), 01 §4.6's example, and the contract regen. This map attaches it as
**`W6b-18`**.

**`OQ-DATA-13` decided (c) — register row 57, struck at `7400846`.** 14 flat fields adopt the
contract's scalars. `derived_from`, `period_*` and `source_fingerprint` adopt the contract's
object forms. The queued slice names the executor and sequences it with W6b-12:
`packages/model-schema` (DatasetVersion), a migration, 01 §5.2, tests. This map attaches it as
**`W6b-19`**. §2 records the sequencing flag.

**`OQ-OVR-14` decided (b) — register row 37, struck at `7400846`.** The views read the dataset's
currency via `getDataset(slug)`. The `?? "GBP"` fallbacks delete. The queued slice names the
executor: `frontend/src/views/ProfileView.vue`, `frontend/src/views/VersionDetailView.vue`,
tests. This map attaches it as **`W6b-20`**.

**`OQ-OVR-15` decided (c), with (a) as the near-term step — register row 38, struck at
`7400846`.** The interim step is the owner display: the list endpoint resolves `owner_id` beside
`latest_version_status`. FR-DATA-51 gains the sentence that the owner column renders the
principal's resolved display name, never the raw id. The queued slice names a W6b slice for
(a) interim. The (c) route defers with the shared trigger. This map attaches (a) as
**`W6b-21`**.

**`OQ-PLAT-10` decided (b) — register row 167, struck at `7400846`.** One-sidedness declares in a
registry. Anything one-sided and undeclared fails. The stale `peril-structure` comment fixes.
F2 subsumes: the authored-keyword completeness check lands with the registry. The queued slice
names an executor small fix: the guard script and test, the `generate-contracts.py` comment, the
registry. This map attaches it as **`W6b-22`**.

**`OQ-PLAT-11` decided (c) now — register row 168, struck at `7400846`.** A revalidation sweep
parses every stored artifact against today's models and reports what no longer reads. 07 records
the rule that a narrowing change to a stored shape is a migration event, not a model edit. The
queued slice names an executor small fix: the sweep script and report, the 07 rule text. This map
attaches it as **`W6b-23`**.

**`OQ-PLAT-16` decided (c) — register row 173, struck at `7400846`.** `generate:api` runs twice
over the same OpenAPI, once with `--default-non-nullable` and once without. Request-body types
alias from the permissive set, responses keep the strict set. The three casts in
`ModelSpecBuilderView.vue` remove. 07 documents the flag and the asymmetry. The queued slice
names a W6b slice: `frontend/package.json`, `frontend/src/api/generated` (VCS-ignored),
`ModelSpecBuilderView.vue`, the 07 note. This map attaches it as **`W6b-24`**.

---

## 5. Proposals — every one with an owner slot

Under [`../../CLAUDE.md`](../../CLAUDE.md) §14 a review's output is a proposal, never a change.
Review 4's finding 5 binds this section. Every accepted §14 proposal gets a row and an owner in
the same edit that accepts it. Or the row is explicitly marked unowned. Where no owner can be
named below, the cell reads **unowned** in that word.

| # | Proposal | Proposed owner | Accepted |
|---|---|---|---|
| **P1** | **Decide `OQ-PLAT-12`** — **decided 2026-08-25 (c)**, not as recommended. `POST /api/v1/me/workspace` audits through `record_switch`. `require_caller` audits nothing. The stored-selection half is refused. Consequence: `W6b-11b` vacates. Obligation 4 goes to `W6b-11` (this map's §3/§4) | maintainer, then `W6b-11` | *decided* |
| **P2** | **The 08-24 re-cut in that map's §3** — superseded. This map's §3 is the re-cut now in force. It awaits signature as **P9** | this map | *superseded* |
| **P3** | **Amend `01:844` in the same commit as the lineage reassignment** — **signed**. It landed with the W6b-12 plan (PR #244, squash `5496c3e`). The typed handler is that plan's Task 2 | `W6b-12` | *signed* |
| **P4** | **The modelling PII guard is not W6b's and must not be absorbed into it** — carried unchanged. No maintainer line has landed since 08-24. A column classified `direct_identifier` is still fittable. It sits on `FR-DATA-13`/`FR-MODEL-5`. It needs a new id and a new unit | **unowned** — pending a maintainer line | *pending* |
| **P5** | **`W6b-13`'s title restated as rule versioning** — **adopted**. The plan is `2026-08-25-w6b-13-rule-versioning-screen.md`. The slice's name and its plan agree | `W6b-13` | *adopted* |
| **P6** | **Give `scope-audit.py --params` a row** — carried unchanged. `grep -c params scripts/scope-audit.py` returns 0 at the anchor SHA. Accepted 2026-08-22. Still no row. Still built by nobody | **unowned** | *pending* |
| **P7** | **`W18` owns `FR-GOV-16`** — resolved by the record. The roadmap's own dated correction (2026-08-23) stands at `:2564`. The Phase 3 workstream table reads "Phase 3, W18" at `:2248`. The correction stands where the wrong owner stood. Nothing further to sign | `W18`, Phase 3 | *resolved* |
| **P8** | **The `W6b-11` split** — vacated with P1. Its own wording predicted this. The audit work turned out not to be browser work. `W6b-11b` is a tombstone. The obligation moved with the decision | — | *vacated* |
| **P9** | **The re-cut in §3** — **superseded by this map.** The 08-26 map's 21 live slices plus the `W6b-11b` tombstone are carried here with their states. This map's §3 is the re-cut now in force. It awaits signature as **P11** | this map | *superseded* |
| **P10** | **The gap list folds into the close-time completeness audit, not into this revision** — carried unchanged. The auditor's findings arrive at the all-slices audit at close. They enter the slice inventory then | the close (W6b close slice), maintainer | *pending* |
| **P11** | **The eight-slice attachment in §3** — `W6b-17` to `W6b-24` attach the eight OQ build slices the manager named. The states read "not started — queued after the #136 build". The DM's classification (executor small fix for `W6b-22` and `W6b-23`) stays visible in the rows | this map | *pending* |
| **P12** | **The DATA-13 sequencing verification** — the executor verifies the real dependency at slice start. The decision's premise ("the lineage handler types against it") does not match the build state at the anchor (§2). `W6b-19` files the finding with its plan | `W6b-19` | *pending* |
| **P13** | **The unattached OQ build items stay queued per the filing** — OQ-DATA-14's halves, OQ-DATA-15's build halves, OQ-MODEL-42, OQ-PLAT-15, the shared-trigger group, the trigger-specific group. The manager's queue disposes them. The close reads them from the filing | maintainer (the queue) | *pending* |

**Highest ids in use**, verified 2026-08-26 at the anchor SHA with a scan of
[`../specs/`](../specs/) and [`../open-questions.md`](../open-questions.md). Use a maximum, not
the last id read. The tables are not in numeric order. Each line carries its correction to the
08-26 map's block in parentheses:

Highest ids in use: FR-OVR-22, NFR-OVR-11, OQ-OVR-16. Next free: `FR-OVR-23`, `NFR-OVR-12`, `OQ-OVR-17`. *(unchanged.)*
Highest ids in use: FR-DATA-57, NFR-DATA-10, OQ-DATA-15. Next free: `FR-DATA-58`, `NFR-DATA-11`, `OQ-DATA-16`. *(08-26 said FR-DATA-57. The filing minted it with the OQ-DATA-15 strike at `01:121`.)*
Highest ids in use: FR-MODEL-128, NFR-MODEL-14, OQ-MODEL-43. Next free: `FR-MODEL-129`, `NFR-MODEL-15`, `OQ-MODEL-44`. *(Unchanged. `W6b-17` files the 02 FR when it plans. The OVR-15 (c) route files a 07 FR when the shared trigger fires. The number stays unallocated at the anchor.)*
Highest ids in use: FR-PLAT-66, NFR-PLAT-11, OQ-PLAT-17. Next free: `FR-PLAT-67`, `NFR-PLAT-12`, `OQ-PLAT-18`. *(unchanged.)*
Highest ids in use: FR-GOV-45, NFR-GOV-8, OQ-GOV-8. Next free: `FR-GOV-46`, `NFR-GOV-9`, `OQ-GOV-9`. *(unchanged.)*

---

## 6. What will bite at closure

**The roadmap's W6b rows still contradict merged builds.** The close's §13 audit derives scope
from the specification first. The roadmap is a specification artifact. Quoted against the anchor
SHA, with the correction:

- The accessibility row reads *"`NFR-OVR-10`'s tabular fallback for charts is **not** built"*,
  with owner W6b (`:1774`) — the W6b-9 build (chart-table retrofit) is merged. Correction:
  delivered. The 08-26 map first recorded this. The row still stands at the anchor.
- The browser authentication row reads *"**Not started, and correctly so.** OQ-PLAT-6 was open
  when W6a closed"* (`:1770`) — the W6b-10 build merged as PR #250 (`c56ec75`). Correction:
  delivered. The row's rationale is a historical record. Its verdict is stale.

The roadmap is not the slice inventory. This map is. The drift is recorded here. The close then
does not re-derive it as a finding about the builds.

**The filing closed the questions. It did not close the builds.** Every OQ row and gate-table
row reads 0 open at the anchor. A struck row is a decision, not a build. `W6b-17` to `W6b-24`
carry their own evidence. The close must not book a decided row as a delivered build.

**The MODEL-43 FR stays undefined until `W6b-17` files it.** The §5 next-free line is the only
place this page cites it. A close audit that greps 02 for the requirement finds nothing before
that slice's plan lands. The slice and the spec text land in one commit (§0's rule).

**The OQ-MODEL-43 version half stays open until `W6b-17` builds.** The W6b-16 change set
resolves the slug half of `OQ-MODEL-34` only. `approximates_model_id` still has no companion
version field. The decision attaches this half to the new slice. Closure must not book the W6b-16
change set as the row's resolution.

**Carried from the previous revision. Still in force.** Frontend requirement traceability does
not exist. Backend `@pytest.mark.req` markers are machine-read. Frontend `it(...)` prose is not.
W6b is the workstream closure will judge it by. §13 rule 1 accepts a closure record that states
why a test is the wrong instrument. It does not accept silence. `FR-PLAT-63`'s test must assert
the rule, not the symptom. The test asserts that a switch writes into **both** chains. It never
asserts that `record_switch` has a call site. That assertion goes green on the first call site
anyone adds. `NFR-MODEL-14` stays booked forward as *delivered but untested*. It is a W5 bench
from 2026-08-22, not W6b's. `test_gbm.py:1879` mentions it in a docstring rather than a marker.

---

## 7. Maintainer acceptance

Nothing on this page binds until accepted. This page does not restate the previous revision's
acceptance table. This page does not supersede it. Where the two overlap, that file records
2026-08-26's earlier decisions. This one records what is proposed now.

| Proposal | Accepted |
|---|---|
| The twenty-nine-slice decomposition in §3 (**P11**), with the `W6b-11b` tombstone and the eight new slices `W6b-17` to `W6b-24` | *pending* |
| The execution order — the eight queue after the #136 build. `W6b-17`, `W6b-18` and `W6b-19` precede `W6b-24` | *pending* |
| **P12** the DATA-13 sequencing verification at slice start | *pending* |
| **P13** the unattached OQ build items stay queued per the filing | *pending* |
| **P10** the gap-list fold-in at close — this revision is filed from the OQ filing and the manager's disposition, not from the gap list | *pending* |
| **P4** the PII guard as a new unit — **unowned** until this line names one | *pending* |
| **P6** `scope-audit.py --params` — **unowned** | *pending* |
