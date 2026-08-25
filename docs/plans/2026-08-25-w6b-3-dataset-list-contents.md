# W6b-3 — Dataset List Contents Implementation Plan

**Slice:** `W6b-3` — Dataset list Contents: status badge, last validated, owner.
**Base:** `bf92059` on `main` — W6b-9 (#198) merged.
**Owner:** `w6b-executor`, dispatched and arbitrated by `w6b-lead` 2026-08-25.
**Map row:** [`2026-08-24-w6b-slice-map-revised.md`](2026-08-24-w6b-slice-map-revised.md):151 —
dependency `—`, blocker `—`, **readiness independently re-derived by the lead: no blocker**.
The row's dependency was `W32-3` in the previous map, and a cleared dependency is exactly the
case that deposits new scope on the waiting slice; what W32-3 deposited is §2 below.

**Highest ids in use: `OQ-OVR-14`, `OQ-DATA-15`, `FR-DATA-56`. Next free: `OQ-OVR-15`.**

**Arbitration folded in (2026-08-25).** The lead's rulings are applied in place below rather
than appended, so this document reads as the plan being executed and not as a plan plus a
correction log. In order: **owner renders the uuid, and name resolution is filed rather than
built** (Decision 1, *decided against this plan's first recommendation* — see there);
**`StatusBadge` is extracted, keyed on the generated enum** (Decision 2); **the version is
named only on disagreement** (Decision 3); **the two `01` §5.1 route rows are amended** (F5);
and **`put_dictionary` is reassigned to the backend** (§Interactions 4).

Every ruling was verified against the artifact before folding, per §2's evidence rule — not as
distrust but because a dispatched citation is still a citation. Twice that mattered: the §0
divergence turned out to span **two** rows rather than the one flagged (F5), and the tracking
reference given for the reassigned backend defect **cannot be right** (§Interactions 4).

---

## Global Constraints

- **No requirement id is renumbered.** This plan proposes one open question, no new
  requirement, and one dated amendment to an existing §5.1 row (`CLAUDE.md` §5).
- **`docs/roadmap.md` is not edited by this plan** — not its W6b row, not §6. A slice close is
  not a §13 workstream close; the lead ruled this at W6b-9's accept.
- **Nothing hand-writes a shape `model-schema` already defines.** `frontend/src/api/datasets.ts`:4
  types `Dataset` as `components["schemas"]["Dataset"]` and stays that way.
- **The gate runs both halves, every exit code read separately**, before any push (§11).
- **No backend change.** Every field rendered here was delivered by W32-3 and is already on the
  wire; §2 evidences that rather than assuming it.

---

## What this slice is, and what it is not

The Dataset list at `/data` renders five columns today — Name, Line of business, Territory,
Currency, Latest version (`DatasetListView.vue`:96-140). Three things `01` §5.3 names are
missing, and all three of their data sources landed on 2026-08-23 in W32-3 and have had **no
reader since**. This slice is the reader.

It is **not** the ownership *editor*. FR-DATA-51 delivered `PATCH /api/v1/datasets/{dataset_id}`
as the Admin-or-owner change path; no requirement asks the *list* to offer it, the rendering
half of FR-DATA-51 is the single clause "it is what §5.3's owner column displays", and putting
an RBAC-gated mutation behind a table cell is a different slice with a different test surface.
Verdict on the change route, per §13's four: **delivered but not surfaced** — reassigned to
whichever slice builds Dataset settings, not left silent.

It is **not** principal name resolution. That is a capability no requirement specifies, which
§0's table makes a spec change rather than code. See Decision 1.

---

## Scope, derived from the specification first

§13: scope comes from the spec, then evidence — never from reading the view and listing what
looks absent.

**`01` §5.3's Contents cell does not bind.** FR-OVR-21 (`00-overview.md`:227) made a §5.3
Contents cell prose unless it declares itself exhaustive, with a per-cell carve-out for seven
named cells. **The Dataset list cell is not one of the seven** — I read the enumeration rather
than assuming, because FR-OVR-21 warns that an id-matching sweep reports all seven green. So
the cell's four words are not a checklist, and scope is the two requirements below.

**One carve-out does live in `01` §5.3 and is not this slice's.** The seven include "`01`
§5.3's own unnumbered *Interaction requirement* ordering paragraph, which is not a cell and
which a cell-scoped sweep does not reach", and FR-OVR-21 says each discharge "falls due at
that slice's plan". I read it (`01`:989-991) to find out whether it fell due here: it governs
**the validation view** — "the validation view is the module's centrepiece … overall banner →
failing rules → warnings → everything else". It says nothing about the list. **Not W6b-3's
discharge**; it falls to the slice that builds the validation report view. Recorded so the
next reader does not re-derive it.

| Source | What it binds here |
|---|---|
| **`FR-DATA-50`** (`01`:117) | Two columns — a status badge from `latest_version_status`, a last-validated date from `last_validated_at` — plus a **rendering rule**: "where the two refer to different versions the list states which, so the pair cannot be read as one fact." |
| **`FR-DATA-51`** (`01`:212) | One column: "it is what §5.3's owner column displays." |
| **`NFR-OVR-10`** (`00`) | The SPA meets WCAG 2.2 AA. No chart is added, so the tabular-equivalent half is not engaged; the badge and date must still be readable without colour. |

**The wire is real, not assumed.** `Dataset` carries `latest_version_status?: DatasetStatus | null`,
`last_validated_at?: string | null`, `last_validated_version?: number | null` and a non-null
`owner_id: string` (uuid) — `frontend/src/api/generated/schema.d.ts`:3381-3399 — and
`backend/src/app/platform/datasets.py`:391-395 populates all four. `DatasetStatus` has **five**
members: `draft | validating | validated | failed | archived` (`schema.d.ts`:3482).

**One invariant the view gets for free.** `packages/model-schema/src/model_schema/datasets.py`:219-221
raises when `(last_validated_at is None) != (last_validated_version is None)` — "one fact
(FR-DATA-50)". So the view never has to render a date without its version or a version without
its date; the pair is structurally co-present or co-absent. This is why Task 2 needs no
defensive branch for the half-populated case, and it is a **citation, not an assumption** — the
branch would be dead code, and dead code in a governed view is a claim that a state exists.

---

## Findings

### F1 — nothing can turn `owner_id` into a person, and that is a spec gap

`owner_id` is a **uuid**, required and non-null. FR-DATA-51 says the column displays it, and
justifies itself on the ground that RBAC and approval trails "need a named subject — 'who owns
this data' is a question a workspace cannot answer". A uuid does not name a subject either.

**Nothing in the platform can resolve it.** I enumerated every path in the published contract:
there is **no `/api/v1/users`** and no principal-lookup route of any kind. The only identity
endpoint is `/api/v1/me`, whose `Me` schema (`schema.d.ts`:5233) carries `principal_id` and
`display?: string | null` — **the caller's own name and nobody else's**.

**And there is no convention to follow.** No `frontend/src/api/me.ts` exists; `frontend/src/stores/`
is still empty (recorded in `01` §5.3's 2026-08-19 note, still true); and no view in the SPA
renders a principal, actor or owner id anywhere.

**Ruled by the lead, and it is the right reading of §0:** name resolution is a capability not
yet specified, so it is a spec change first, never code smuggled in behind a table cell.
Building a partial resolution here — even the tempting "resolve *my own* id via `/me`" — would
be exactly that: a capability invented at a call site, with the platform's first identity
rendering decided by a slice that was scoped to render three columns. **The column renders the
uuid; the gap is filed as OQ-OVR-15.** Decision 1 covers only the presentation of the uuid.

### F2 — `failed` renders in the tone reserved for `draft`

`DatasetDetailView.vue`:34-38 holds a `STATUS_TONE` map with **four** of `DatasetStatus`'s
**five** members — `draft`, `validating`, `validated`, `archived`. `failed` is absent, and the
call site (`:216-218`) falls back to `'bg-slate-100'`, the exact tone `draft` is mapped to. A
version whose validation **failed** renders in the same calm neutral as one nobody has touched.

**Stated at its true strength:** this is not a WCAG violation. The badge renders `{{ row.status }}`
as text, so the word "failed" is on screen and colour is not the only channel — I read the
template before claiming otherwise. It is a *tone* defect: the visual channel says "nothing has
happened here" about the one state that means something went wrong. It is the same shape as the
`psiBand` defect `01` §5.3's 2026-08-19 note records — a dangerous state rendering as a calm one
— which is the precedent for fixing rather than tolerating it.

It is pre-existing and **W6b-3 inherits it by copying**: the list needs the same map for the
same enum. **Decision 2.**

### F3 — the second `STATUS_TONE` is a name collision, not a duplicate

`RuleSetView.vue`:56-60 also declares `const STATUS_TONE`, with `draft | review | approved`.
That is the **rule-set lifecycle**, a different enum sharing a constant name. Consolidating the
two would merge two vocabularies into one map and let a rule-set status pick up a dataset tone.
**No action.** Recorded because "there are two `STATUS_TONE` maps, extract them" is the obvious
wrong move and the next reader will hit the same grep.

### F4 — the "states which" rule has no enforcement anywhere

FR-DATA-50's "where the two refer to different versions the list states which" is a **view**
obligation. The model-schema validator enforces co-presence, not disclosure; no test, contract
or check anywhere asserts that a rendered date names its version. The requirement's worked
example is the point: a Dataset whose v12 is a fresh `draft` above a `validated` v11 must not
read as never validated, and must not read as though v12 were the validated one.

Nothing to fix — the rule was never delivered, because its owner is this slice. It is a finding
because it is the one clause in FR-DATA-50 a reviewer looking at three new columns would not
think to check.

### F5 — the §0 divergence is wider than the ruling described: two rows, not one

The lead flagged `01`:826 as the stale side of a spec/code disagreement. Verified, and the
verification found more:

- **`01`:826** — `GET /api/v1/datasets` is described as returning "`latest_version`,
  `latest_version_status` and `last_validated_at` (FR-DATA-50)". It omits
  **`last_validated_version`**, which `api/datasets.py`:339 passes, `platform/datasets.py`:394
  populates, the published contract declares (`schema.d.ts`:3383), and FR-DATA-50's own dated
  amendment explicitly announces as the third field. The row is stale in one field.
- **`01`:827** — `GET /api/v1/datasets/{slug}` is described as "Dataset detail incl.
  `latest_version`". The detail route (`api/datasets.py`:431-443) passes **both**
  `latest_version=` and `last_validated=`, so it serves the same four derived fields the list
  does. **This row is stale in three fields**, not one. The lead asked me to "check `:827`
  too"; this is the answer, and it is why the amendment is two rows.

**Which side is wrong is not in doubt** (§0 requires this be asked, not assumed): FR-DATA-50's
amendment, the code, and the published contract all agree on four fields; only the §5.1 route
rows disagree, and they were written before W32-3 landed. **The spec is stale and is amended**
— as a dated amendment on the two rows, never a silent rewrite. Task 4.

### F6 — two other `to_schema` callers return the derived fields as null, latently

`to_schema` takes `latest_version` and `last_validated` as optional keywords, so population is
per-caller. Five callers pass them; **two do not**: `create_dataset` (`api/datasets.py`:296) and
`put_dictionary` (`:502`).

- `create_dataset` is **correct** — a dataset with no versions genuinely has all four null.
- `put_dictionary` is **not**. `PUT /datasets/{slug}/dictionary` returns a `Dataset` whose
  derived fields are null regardless of how many versions exist, so the same shape from two
  routes disagrees about whether the dataset has ever been validated.

**Latent, not live, and stated that way.** `DatasetDetailView` assigns that response straight
into its `dataset` ref (`:71`), but reads none of the four fields from it — I checked every
`dataset.` access in the template. So nothing renders wrongly today. It becomes live the moment
any view reads a derived field off a dictionary-save response.

**Out of scope, and now formally reassigned**: it is a backend fix in a frontend slice, and this
plan's constraint is no backend change. Verdict per §13: **delivered but incorrect on one
route**. The lead confirmed it and took it off this slice; the reassignment, the rule it breaks
(already written down at `api/datasets.py`:436-437) and the unresolved tracking reference are
in §Interactions 4.

---

## Decisions for arbitration

### Decision 1 — how the uuid is presented — **DECIDED, against this plan's recommendation**

This plan first recommended rendering the first 8 characters with the full value in a `title`
attribute. **The lead ruled against it, and the reasoning is correct enough to record in full
rather than summarise**, because the mistake is one any later slice rendering an id will be
tempted into.

**The ruling: the full `owner_id` is the cell's text.** Any narrowing is presentational —
`max-width` plus `text-overflow: ellipsis` — never `String.slice`. A `title` may be added as a
mouse convenience but **must never be the only home of the value**.

Two reasons, both of which defeat the original recommendation:

- **`title` alone fails WCAG 2.2 SC 1.4.13** (Content on Hover or Focus), which requires such
  content to be dismissable, hoverable and persistent. A browser-native tooltip is none of
  those, and it is unreachable by keyboard and by touch entirely. `NFR-OVR-10` binds this SPA
  to **AA**, and 1.4.13 is AA. Putting the only copy of a value in a `title` is not a
  convenience with a fallback — it is the value being absent for a class of users.
- **Slicing destroys the one property a raw id has.** An opaque identifier's entire utility is
  exact copy and exact search. `3f2b9c14…` cannot be pasted into anything. The original
  recommendation optimised for the column looking tidy, and traded away the only thing the
  column was for — which is the sharper version of the mistake, since the tidiness was the
  *stated* justification.

CSS truncation keeps both: the full string is in the DOM, selectable, copyable, findable by
the browser's own find, and exposed to assistive technology; only its painted width is
constrained, and it degrades to the full value when the viewport allows.

**What this does not do** is pretend to name anybody. The column is visibly a machine
identifier — the accurate state of the platform's identity story, and what motivates
OQ-OVR-15.

### Decision 2 — where the status badge lives, and whether F2 is fixed here

| | Option | What it costs |
|---|---|---|
| **(a)** | Copy `STATUS_TONE` into `DatasetListView` | Ships F2's defect a second time. A shape defined twice diverges (§2). |
| **(b)** | **Extract `StatusBadge.vue`** taking a `DatasetStatus`, used by both views, `failed` given its own tone | One small component, one map, F2 fixed at source. Touches `DatasetDetailView`, which this slice does not otherwise need. |

**DECIDED: (b).** The map is not incidental duplication — it is *the* rendering of a contract
enum, and the enum has five members the one existing copy does not cover. Extracting it makes
the tone map `Record<DatasetStatus, string>` rather than `Record<string, string>`, which turns
a missing member from a silent grey fallback into a compile error. Same move as W6b-9's
required `currency` prop, and the reason (b) earns its extra file rather than being tidiness.

The lead's ruling adds that this **is not scope creep**: adding a badge without extracting
would author a second copy of a shape `model-schema` declares, which §2 forbids outright. The
extraction is the only conforming way to build the column at all.

Three conditions on it, all in Task 1:

- keyed `Record<DatasetStatus, string>` **off the generated enum**, so the compiler enumerates
  the members rather than a human doing it;
- `failed` given its own tone, in the same commit;
- the compile-error property **proven by mutation** — delete a member, show the type error,
  restore — not merely asserted. A type-level guard nobody has watched fail is a guard nobody
  has tested (§13).

**Blast radius is one call site**, `DatasetDetailView.vue`:214-218, whose existing tests assert
on rendered status *text*. F2's fix is a tone change, so no existing assertion changes meaning.

### Decision 3 — how the badge/date pair states which version it means (F4)

FR-DATA-50 requires disclosure only "where the two refer to different versions". Two readings:

- **Always name the version** — "v11 · 3 Feb" in every row.
- **Name it only on disagreement** — "3 Feb" when the last-validated version *is* the latest,
  "v11 · 3 Feb" when it is not.

**DECIDED: name it only on disagreement**, which is the requirement's own predicate — "**Where
the two refer to different versions** the list states which". Always naming it is not more
honest: it puts a version number in every row to disambiguate a case that is not present, and
the requirement's concern is that "the pair cannot be read as one fact" *when they are two
facts*. Where `last_validated_version === latest_version` they are one fact and the extra token
is noise.

**Both branches are tested.** A conditional exercised in one direction is a conditional whose
other direction is untested, and the untested direction here is the one the requirement was
written for. Agreement renders no version; disagreement names it.

The comparison is safe: both fields are on the same object, and §2's validator guarantees
`last_validated_version` is present whenever the date is.

---

## Interactions this slice touches but does not resolve

1. **OQ-OVR-14's currency defect does not reach this view.** `DatasetListView` renders
   `dataset.currency` from the Dataset object itself (`:135-137`), not a prop — correct here,
   and the positive control for OQ-OVR-14's claim that the value exists and is simply not
   threaded to `ProfileView`/`VersionDetailView`. Neither fixed nor worsened.
2. **No chart is added**, so NFR-OVR-10's tabular-equivalent half is not engaged. The list is
   already a `<table>` with `scope="col"` headers.
3. **Ownership change stays unbuilt**, with the §13 verdict in §1.
4. **F6's `put_dictionary` gap is reassigned to the backend — touched, not resolved.** The lead
   confirmed the finding and took it off this slice: `api/datasets.py`:502 returns
   `to_schema(row)` bare, so all four derived fields come back null however many versions
   exist. It breaks a rule **the codebase had already written down** two routes away, at
   `api/datasets.py`:436-437 — "a detail page that showed nothing where the list showed a date
   would be its own defect (FR-DATA-50)" — which is the detail route explaining why it passes
   both aggregates. `put_dictionary` is the third route and does not. Roughly four lines plus a
   test, in the backend, by a backend owner. My reading that `create_dataset` doing the same is
   *correct* (a dataset with no versions genuinely has all four null) was confirmed.

   **The tracking reference is unresolved and is deliberately not written here.** It was given
   as `#71`; that number cannot be a new filing, because issues and pull requests share one
   number sequence in this repository and pull requests already reach #199 — `gh issue view 71`
   resolves to the merged W5 pull request "feat(w5): the GLM spine". *Limit of my evidence:*
   `gh issue list` is refused by this token ("Resource not accessible by personal access
   token"), so I cannot enumerate issues to recover the correct number, and the lead can close
   this in one line. A wrong pointer in a governed document is worse than a described finding
   with none, so the finding is described in full above and the number is left for the lead.

---

## File Structure

```
frontend/src/
  components/
    StatusBadge.vue                        NEW  — DatasetStatus → badge, all five members
    __tests__/StatusBadge.test.ts          NEW
    __tests__/StatusBadge.test-d.ts        NEW  — the exhaustiveness proof (see Task 1)
  views/
    DatasetListView.vue                    three columns
    DatasetDetailView.vue                  STATUS_TONE deleted, StatusBadge used
    __tests__/DatasetListView.test.ts      extended
docs/
  specs/01-data-management.md              §5.1 rows :826 and :827 amended (F5)
  open-questions.md                        OQ-OVR-15 (+ 00-overview.md §10 mirror)
```

No `me.ts`, no store, no backend file — all three follow from the rulings above.

---

## Tasks

Each task is one commit. The gate runs at Task 5, not per task.

### Task 1 — `StatusBadge`, with `failed` given a tone (Decision 2)

Extract the badge into `StatusBadge.vue` typed on `DatasetStatus`; give `failed` a distinct
tone from the existing error surfaces; replace `DatasetDetailView`'s inline map and span.
Tests: one per enum member, and — the point of the extraction — a **type-level** proof in a
`.test-d.ts` that a status with no tone cannot compile. It must be `.test-d.ts`: vitest's
typecheck includes only `src/**/*.test-d.ts`, so this assertion is invisible to `pnpm test` and
lives or dies under `vue-tsc`. (Established the hard way in W6b-9.)

### Task 2 — the badge and last-validated columns (FR-DATA-50, Decision 3)

**This task first migrates `DatasetListView.test.ts` to `cellUnder`, including the four
assertions already there**, and does so *before* adding a column. `:44-47` asserts with a bare
`screen.getByText("v2")`. That is safe only while exactly one version-shaped string exists in a
row, and this slice is precisely what ends that: the disagreement branch of Decision 3 renders
a *second* version number in the same row. A bare `getByText` then either matches the wrong
cell or throws on multiple matches, and in neither case can it say which column it read.

This is the hazard `cellUnder` was built for in W6b-9 and filed as OQ-OVR-13 — a positional
`columns`/`rows` correspondence that a call site can silently get wrong. The migration comes
first so that the four existing assertions are proven to still pass *before* the new columns
change what is in the row; migrating afterwards would mean rewriting assertions and adding
columns in one step, with nothing establishing which change moved them.

Then both columns, with the disagreement rule. Tests, each phrased as the claim it defends:

- names the version when the last validated one is not the latest — FR-DATA-50's own
  v12-draft-above-validated-v11 example as the fixture;
- does not name it when they agree;
- renders a never-validated Dataset as `—` in the date column while still showing its badge —
  the two columns are independently absent;
- shows a badge for all five statuses.

### Task 3 — the owner column (FR-DATA-51, Decision 1)

The **full** `owner_id` as the cell's text, monospace, narrowed by `max-width` +
`text-overflow: ellipsis`. No `String.slice`. No `/me` call, no resolution, no store.

Tests, each defending the ruling's reasoning rather than the ruling's wording:

- the cell's text **is** the whole uuid — the assertion reads the exact value, so a later
  "tidy" truncation fails here rather than shipping;
- two datasets with different owners render differently (the guard against a hardcoded
  placeholder passing every single-row test);
- if a `title` is added at all, a test asserts the value is present **without** it, so the
  tooltip can never quietly become the only home (SC 1.4.13).

### Task 4 — the §5.1 amendment (F5) and OQ-OVR-15, both mirrors

**One commit, because it is one finding**: the two `01` §5.1 rows gain a dated amendment naming
the fields they omit — `:826` one field, `:827` three — written as an amendment, never a silent
rewrite (§0). Then OQ-OVR-15 in `docs/open-questions.md` **and** `00-overview.md` §10: how does
the SPA render a principal it did not authenticate as — an owner display on `Dataset`, a
`/api/v1/users` lookup, or a principal-name batch endpoint? Carries F1's evidence (no users
route, `Me` is caller-only, no store, first identity rendering in the SPA) and F6's finding, so
the maintainer re-derives neither.

Two traps this task must not step in, both already paid for once:

- The Status cell must lead with a bare vocabulary word — `**Open** — …`, never `**Open**, …`.
  Check 15 takes `split()[0]` and a comma sticks to it.
- The OQ is mirrored in two files, and amending one diverges them. Both, in this commit.

Run `python3 scripts/audit-docs.py` here.

### Task 5 — the gate, both halves, and the close

`ruff` · `mypy` · `lint-imports` · `pytest` · `audit-docs` · `req-coverage` ·
`generate-contracts --check`; then `pnpm install` · `generate:api` · `lint` · `type-check` ·
`test` · `build`. **Each exit code read separately** — a `&&` chain has reported a green gate
here while the frontend was red.

Then §13 enforcement on deliberately broken input, each reverted from a saved copy rather than
`git checkout --`. At minimum: a status member losing its tone (must fail `type-check`, not
`test`); the disagreement rule inverted; the date rendered without its version. Then PR, CI
read per-workflow, **merge verified by `state`/`mergeCommit` rather than exit code**, branch
cleanup, and a report to the lead.

---

## What would make this plan wrong

1. **If the maintainer reads FR-DATA-51's "displays" as requiring a name, not an id.** Then the
   uuid column is not a step toward the requirement but a failure to meet it, and the slice is
   blocked on the backend work OQ-OVR-15 proposes rather than shipping. The lead has ruled the
   other way; OQ-OVR-15 is where the maintainer can overturn it.
2. ~~**If `failed` is unreachable at the *latest* version.**~~ **Struck 2026-08-25, settled by
   the lead and verified here.** `VALID_DATASET_TRANSITIONS` (`model-schema/datasets.py`:77-81)
   maps `VALIDATING → {VALIDATED, FAILED, DRAFT}`, so a newest version that failed validation
   projects `latest_version_status: "failed"` through the list's `DISTINCT ON`. F2 stands at
   full strength and Decision 2 does not fall back to consolidation alone: a **failed** dataset
   currently renders in draft's tone, in the view someone reads to decide whether data is fit
   to model on.
3. **If `01` §5.3's Contents cell is later declared exhaustive.** FR-OVR-21 lets a cell declare
   its own kind. This plan reads it as prose because it is not among the seven and declares
   nothing; a later declaration could add scope.
4. ~~**If F5's two rows are owned by a docs slice already in flight.**~~ **Struck 2026-08-25:**
   the lead confirms no other session is building, so nothing else is in flight on `01` §5.1.
   This was the one falsifier I could not check myself — a conflict is visible from the team's
   position, not from inside a worktree.

**Falsifiers 1 and 3 stand deliberately.** Both are the maintainer's to overturn rather than
the lead's, and both are pointed at OQ-OVR-15, which is where an overturn would land. A
falsifier a peer *could* strike is worth striking; one only the maintainer can settle is worth
leaving visible.
