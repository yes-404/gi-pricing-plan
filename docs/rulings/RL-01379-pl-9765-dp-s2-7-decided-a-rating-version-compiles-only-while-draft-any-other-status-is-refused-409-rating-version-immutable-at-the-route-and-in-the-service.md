---
id: RL-1379
family: ruling
title: PL 9765 DP-S2-7 decided — a Rating Version compiles only while draft; any other status is refused 409 RATING_VERSION_IMMUTABLE, at the route and in the service
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-03              # the mint date (check 31); ruled 2026-10-01
owner: decision-maker
tree: 9cbc384fc042faeb6359b35aea9d01c1a730c197
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-4, FR-238, FR-239, FR-240, FR-257, FR-267, RL-915, RL-921, RL-922, LG-1204]
---

# RL-1379 — PL 9765 DP-S2-7 decided: a Rating Version compiles only while `draft`; any other status is refused 409 `RATING_VERSION_IMMUTABLE`, at the route and in the service

## How this was ruled

**Ruled 2026-10-01 10:42 BST at effort `medium`** by the decision-maker session `dm-s2c7`,
spawned from `.claude/roles/decision-maker.md`. The session printed `CLAUDE_EFFORT=medium`.
The commission is the maintainer's `to-lead.md` entry headed `2026-10-01 10:34:45 BST — FD 9754
(#1064, a non-draft rating version can be recompiled and its bundle rewritten): MEDIUM, owner
WK-674 S2, and **S2 does not merge without the guard**; the option choice goes to a DM now`,
which names "opus, medium". **Disclosed, not resolved:** the maintainer's entry headed
`2026-09-30 00:42:01 BST — #933 READ BACK; DECISION: the DM PREPARES the blocked rulings on
medium now, and RULES only on effort high` exists. This session read it as scoped to #933's
blocked rulings, because the later commission names medium for this one. Whether it binds
here is the lead's to confirm.

**Answered 2026-10-03 17:28:31 BST, by the maintainer, in `to-lead.md`, the entry
headed `2026-10-03 17:28:31 BST — dm-1377 GO already given
(messages crossed); RL 9751 Q1 answered: it stands at medium; GO the item-5 mint batch (RL 9751 +
#974 + FD 9772)`. It says the 30 Sep 00:42:01 rule ("the DM prepares … on medium, and rules only on
effort high") was scoped to #933's blocked rulings and does not bind this ruling, that the
commission named medium explicitly and the standing default is medium unless the lead raises it,
and that this ruling stands as ruled at medium. Nothing in the ruling's content changes.

**What was read, and at which trees.** Code and specs at `origin/main` `92b4e4ac` (tree
`9cbc384f`). `#1056`, the only commit between `1dd5e264` and `92b4e4ac`, changed docs only
(`git diff --name-only 1dd5e264 92b4e4ac`: `INDEX.md`, one FD, `register.md`, one PL,
`roadmap.md`, one RL), so FD 9754's code citations at `1dd5e264` hold here. FD 9754 (working
id) read in full at #1064 head `61a21edb`. PL 9765 (working id) read at #1062 head `d844dc09`,
then its DP-S2-7 row (`:852`), Acceptance 19 (`:644-656`) and Task 5A (`:1272-1280`) at head
`185e6759`.

## The question (DP-S2-7)

What happens when a compile is requested for a Rating Version whose status is not `draft`?

**The real statuses.** `RatingVersionStatus` (`packages/model-schema/src/model_schema/rating.py:32-44`)
is `draft`, `review`, `approved`, `live`, `retired`. The database column is `String(16)` with
no CHECK constraint (`backend/migrations/versions/06e5a5425a8b_rating_versions.py:35`); the
vocabulary is the enum's (`backend/src/app/db/models.py`, `RatingVersionRow.status`,
`info={"status_vocabulary": RatingVersionStatus}`). **There is no `archived` status** for a
Rating Version; PL 9765's Acceptance 19 example names one, and the cases below use the five
real ones. **No code at `92b4e4ac` writes `live` or `retired` to a row**
(`git grep -n "RatingVersionStatus.LIVE\|RatingVersionStatus.RETIRED" -- backend/src` prints
only the `_APPROVED_OR_AFTER` tuple, `rating_versions.py:75-79`), and PL 9765 at `185e6759`
adds no such write: a Deployment binds an `approved` version and leaves the row's status as it
is (FR-238, FR-267).

## Verified first, at tree `9cbc384f` (`origin/main` `92b4e4ac`)

| Claim | Where (body read) |
|---|---|
| The route needs only `Perm.RATING_COMPILE`, reads no row and submits a `rating.compile` Job | `backend/src/app/api/models.py:1232-1262` |
| The handler loads the row through `load_rating_version`, which checks only the workspace | `backend/src/app/worker/rating_handlers.py:35-90`; `backend/src/app/platform/rating_versions.py:126-138` |
| `compile_rating_version` reads no status; its last statement rewrites `row.bundle` | `rating_versions.py:395-543`, the write at `:538-542` |
| The only other writer of `row.bundle` is `record_bundle_blob`, called by the handler after the compile | `rating_versions.py:170-199`, the write at `:199` |
| The only draft test in the module is `submit_for_review`'s, raising `VALIDATION_FAILED` 409 | `rating_versions.py:278-284` |
| **`apply_approval_decision` does not re-check the bundle hash.** It locks the row, maps the decision to a target status and moves `review` to it. Nothing compares `row.bundle.content_hash` with the hash the submit gate pinned | `rating_versions.py:312-376` |
| The database does not stop it. `approval_guard` fires `BEFORE INSERT OR UPDATE OF status, workspace_id, slug, version` and refuses only a write of `approved` outside the decision path; `bundle` is not a trigger column | `backend/migrations/versions/a9f3c6d21b87_approval_guard.py:57-82`, `:104-112` |
| `content_hash` is `bundle_hash(graph, pins)`. It excludes `compiled_at` and the resolved payloads | `packages/pricing-core/src/pricing_core/rating/compile.py:520-533`, `:641-642`; `03:1067-1071` |
| A handler's `PlatformError` ends the Job `failed` with `JobError(code=exc.code, message=exc.detail or exc.title, retryable=False)` | `backend/src/app/worker/tasks.py:197-231`; `JobError` at `packages/model-schema/src/model_schema/jobs.py:168-181` |
| A 202 route may load the row synchronously before it submits a Job, so a refusal reaches the caller as a problem response | `start_regression_run`, `api/models.py:1282-1284` |
| The score path resolves a ref to `row.bundle`'s `content_hash` and `blob_sha256` on every call | `backend/src/app/api/score.py:191-207` |

**Three corrections to FD 9754, for its author.** This ruling does not edit the finding.
(i) R1 is `03-rating-engine.md:41`, not `00-overview.md:41`. (ii) The FD's open question
"whether `content_hash` covers `compiled_at`" is answered: it does not. So a recompile changes
the hash only if the graph or a pin ref changed. But a recompile always rewrites the summary,
and it can write a new blob under the same hash. (iii) "Refusing a *live* version needs the
Deployment record" does not hold. Every Deployment binds an `approved` version (FR-267), and
nothing writes `live` to the row, so a deployed version's row is `approved`. A status test
refuses it with no Deployment lookup. The FD's gap 3 ("whether `decide` re-checks them") is
now measured: **it does not** (row above).

## What the specification says, to the clause

- **FR-4** (`00-overview.md:209`), no dated amendment: *"Every Artifact is immutable once it
  leaves `draft`. Corrections create a new version with `parent_id` set; nothing is edited in
  place or hard-deleted."*
- **R1** (`03:41-43`): *"A `live` Rating Version is immutable and fully pinned. Every model,
  rate table, and reference table version it uses is fixed at bundle time."*
- **FR-238** (`03:135`), no amendment: the lifecycle; *"Only `approved` versions can be
  deployed; `live` is a property of a Deployment"*.
- **FR-239** (`03:136`), no amendment: *"A Rating Version compiles to a self-contained
  **Bundle** with a content hash. … is what gets cached and distributed."* It does not say when
  a compile may run.
- **FR-240** (`03:137`), one dated amendment (2026-09-30, `RL-1329`, `LADDER_CLAMP_UNPLACEABLE`
  at save and compile). It says what a compile validates and not when it may run.
- **FR-257** (`03:174`), clarified 2026-09-28: a version cannot reach `approved` without a
  passing Regression Suite; *"It applies forward, at submit."* The submit gate pins the
  evidence to the compiled bundle's hash (`rating_versions.py:583-650`).
- **FR-267** (`03:195`): a Deployment records *"the bundle hash"*. **FR-268** (`03:196`):
  *"a scoring call sees either the old or the new bundle, never a mix"*.
- `03` §5.1's compile row (`03:793`): *"**202** Compile + validate the bundle (FR-240)"*.
  `grep -n -i recompil docs/specs/*.md` prints nothing.

**No clause says when a compile may run.** FR-4 forbids the effect: a non-draft artifact's
compiled output is edited in place. Nothing names the cause. This is a gap in the
specification, and the code took the permissive default. **Neither side was wrong in the §0
sense. The spec was silent, and the code's default breaks a requirement the spec does state.**

## Prior art: what each decided, and that none decided this

| Record | What it decided (quoted) | This question? |
|---|---|---|
| **F50** (`docs/findings/register.md:91`) | That the `bundle_slot.py:28-31` docstring's argument *"is wrong as stated"*: `row.bundle` *"is mutable"*, the route *"carries no already-compiled refusal"*, and *"the repository already treats 'changed hash under an unchanged ref' as a normal, audited event"*. Resolved by a docstring correction. | **No.** It records the code's behaviour to fix a comment. It never asks whether FR-4 permits the behaviour. |
| **RL-921 §3** | *"Serving from `hash_for(ref)` without any read is refused"*. The memo *"is safe **today** only because `hash_for` is read solely in the degradation branch"*. *"The docstring's staleness argument … is a defect in the reasoning, not in the behaviour"*. | **No.** It rules on the memo's safety and takes the recompile as given. |
| **RL-922 §7** | Its owner table: *"**F50** — the `bundle_slot.py:28-31` docstring correction"*, owned by *"WK-671 Slice 3, Task 3B"* (the row's cells, joined here). | **No.** It routes a docstring fix. |
| **RL-915 §4** | *"Whether a rating version should retain *several* compiled bundles … This ruling gives it one … If a later workstream needs history, that is an additive change … and it would then need the 'which one is live' policy that §2 refuses to have invented silently."* | **No.** It defers the question. This ruling does not take up that policy (option 2 is refused below). One citation there does not resolve: §4 says *"FR-239's 'compiled once'"*, and FR-239 at this tree has no such words. |
| **LG-1204:380** (minted, frozen) | *"An RV in review cannot be recompiled."* | **No, and it is false of the code.** Compile reads no status (above). Cited here and not edited, per the commission. Under this ruling the sentence becomes true when WK-674 S2 merges. It is still not true at the ledger's own tree. |

## Ruled

**Option (1). A compile runs only while the Rating Version is `draft`.** A compile requested
for a version in any other status (`review`, `approved`, `live`, `retired`, and any status
added later) is refused with **`RATING_VERSION_IMMUTABLE`, HTTP 409**. The row's `bundle`
(summary and blob key) is left unchanged, no blob is written, and no compile audit event is
recorded. A version that has left `draft` gets a new compiled output only as a **new
version**. For `review` that means returning to `draft` through the decision path first
(`06` FR-355; `_target_status`, `rating_versions.py:378-386`). For `approved` and after it
means a new version of the slug (`create_rating_version`, `rating_versions.py:202-`).

### The maintainer's lean, tested

*"(1); 'approved' means the bytes can't move, and a recompile is a new version."* **It holds,
and the evidence makes it stronger in two ways.**

1. **It must cover `review`, not only `approved`.** The submit gate pins the Regression Suite
   evidence to the bundle hash. `apply_approval_decision` does not re-check that hash (verified
   above). So a compile during review would let a version reach `approved` on evidence taken
   from a different bundle. That breaks FR-257's *"cannot reach `approved` without a passing
   Regression Suite"*, and nothing would see it. A test of `status in {approved, live,
   retired}` would leave that hole. **The test is `status != draft`**, which is FR-4's own
   boundary.
2. **"Live" needs no Deployment lookup.** It is covered by the row's `approved` status (above).
   So the guard does not depend on S2's Deployment table, and it is correct before S2 too.

**"A recompile is a new version": true, with one gap that this ruling does not close.** FR-4's
correction mechanism is "a new version with `parent_id` set". A Rating Version has **no
`parent_id`**: `RatingVersionRow` (`db/models.py`, the class at `:1945-`) and the model-schema
`RatingVersion` carry none. `create_rating_version` numbers the next version of the slug
(`:218-229`). So a recompile-as-new-version works today, but its lineage is by slug and version
number only. That is a separate gap against FR-4. This ruling reports it to the lead as an
observation and does not rule it.

### Why not the other options

- **(2) Allow, and bind the bundle immutably.** This needs a bundle history and the "which one
  is live" policy that RL-915 §4 refused to invent silently. It still needs `decide` to
  re-check the hash, or FR-257 breaks as in point 1. No requirement names a use case for
  recompiling an approved version. Refused: it is larger, and it invents policy with no
  requirement behind it.
- **(3) Document it as intended.** This needs an FR-4 carve-out that calls `row.bundle` derived
  metadata. That contradicts R1's *"fully pinned … fixed at bundle time"*. It also leaves
  FR-267's recorded hash able to disagree with what the score path resolves (`score.py:196-207`
  reads the row, not the Deployment). Refused.
- **(4) Allow an identical recompile as a no-op** (an option from the evidence). "Identical"
  would have to mean the same blob bytes, because `content_hash` excludes payloads. A non-draft
  compile that changes nothing has no purpose, so this adds a comparison for no use. Refused.
- **(5) A database trigger refusing an update of `bundle` when `OLD.status <> 'draft'`** (an
  option from the evidence: the `approval_guard` precedent). Not required in S2. The two
  writers of `bundle` are both on the compile path (`:199`, `:538`), and the service guard
  covers both. A trigger would add a migration to a slice that has its own. This is recorded
  as available defence in depth, and it is not ruled out for later.

## What it obliges

WK-674 S2 builds these in Task 5A.

**One guard, in the service, used by both callers.** It is not a second copy at the route.

1. **`rating_versions.py`: a function `require_compilable(row: RatingVersionRow) -> None`.**
   If `RatingVersionStatus(row.status) is not RatingVersionStatus.DRAFT`, it raises exactly:

   ```python
   raise PlatformError(
       "RATING_VERSION_IMMUTABLE",
       "Rating version is immutable",
       409,
       f"Rating version {row.slug}@{row.version} is {row.status}; only a draft rating "
       "version can be compiled (03 FR-239, 00 FR-4). Create a new version to compile again.",
   )
   ```

2. **`compile_rating_version` loads its row `FOR UPDATE`** and calls `require_compilable`
   before resolving any pin. The lock follows `apply_approval_decision`'s precedent
   (`:329-338`, `.with_for_update()`). **`submit_for_review` loads its row `FOR UPDATE`
   too**, so a compile and a submit of the same version serialise. Without both locks, a
   compile that read `draft` can commit a new bundle after a concurrent submit has pinned
   evidence to the old one. The handler's own `load_rating_version` call at
   `rating_handlers.py` (`prior_hash`) stays, and it reads the same row within one session.
3. **The route** (`api/models.py:1232`) loads the row in its unit of work and calls
   `require_compilable` before `job_service.submit`, as `start_regression_run` does at
   `:1282-1284`. Its `responses=problems(401, 403, 404, 422)` gains **409**. The OpenAPI
   contract is regenerated (`scripts/generate-contracts.py`), never hand-edited.
4. **`backend/src/app/errors.py`**: `"RATING_VERSION_IMMUTABLE"` is added to
   `RATING_ERROR_CODES` with a one-line comment naming `<RL id>` and FR-239. It goes in the
   **same commit** as T3 below. FR-22's two-way check fails if either lands alone.
5. **`backend/src/app/platform/bundle_slot.py`**: the corrected paragraph (lines 28-46 at
   `92b4e4ac`) says *"nothing refuses a recompile"*. After this change that is false for a
   non-draft version and still true for a draft one. The paragraph gains a dated correcting
   sentence. Its text is code, not spec, and is given here so that no executor writes it:

   ```text
   **Corrected <fix date> (<RL id>):** a compile is now refused unless the version is
   `draft`, so a non-draft ref's hash no longer moves; a draft ref's still does, and draft
   versions are scoreable (`03` §5.1, `/score/compare`), so the degradation-only rule above
   stands.
   ```

   This file is outside Task 5A's listed write set. The lead's dated delta adds it.

### What the caller sees

- **A non-draft version at request time:** a synchronous **409**
  `application/problem+json` with `code` `RATING_VERSION_IMMUTABLE` and the detail above.
  **No Job is created**, and the row is unchanged.
- **The status changed after the 202** (the version was submitted, approved or otherwise moved
  between the route's check and the worker's run): the Job ends **`failed`** with
  `error.code` `RATING_VERSION_IMMUTABLE`, `retryable: false`, and `error.message` the detail
  (`tasks.py:197-231`). A Job carries no HTTP status. The 409 belongs to the route, and the
  code is the contract (FR-403). The row's `bundle` is unchanged, no blob is written (the
  `put` follows the compile), and the transaction rolls back.
- **A `draft` version:** unchanged. A draft version may be compiled any number of times. That
  includes a draft returned from review.

## Acceptance — the violation that must become detectable

This completes PL 9765 Acceptance 19 and Task 5A.

**File: `backend/tests/test_rating_version_compile.py`**, where the compile tests are. Each
red case is **run red before the change**, with its predicted cause recorded in the ledger,
and run green after. A reasoned red does not satisfy this (the maintainer: *"shown red
first"*).

- **C1. The route refuses each non-draft status (red).** Parametrise over `review`,
  `approved` (through `mark_approved`, `backend/tests/approved_rows.py:91-102`; RatingVersionRow
  is in `_EVIDENCE` at `:42`), `live` and `retired`. A direct status write is used for these;
  `approval_guard` polices only `approved`. Add a fifth case, **`approved` with a Deployment
  recorded through S2's own create path**. Each starts from a compiled version: `bundle` holds
  `content_hash` and `blob_sha256`. `POST /api/v1/rating-versions/{id}/compile` returns
  **409** with `code` `RATING_VERSION_IMMUTABLE`. Also assert: **no `rating.compile` Job row
  was created** for the version, **`row.bundle` equals its value before the request** (the
  whole dict), and **no `rating_version.compiled` audit event was added** (`rating_handlers.py:106`). Predicted red: 202 and a Job.
- **C2. The service refuses a status that changed after submission (red).** Submit the compile
  while the version is `draft`, then `mark_approved` it, then execute the Job. The Job is
  `failed` with `error.code == "RATING_VERSION_IMMUTABLE"` and `retryable is False`, and
  `row.bundle` is unchanged. Predicted red: the Job succeeds and rewrites `bundle`.
- **C3. Control: a draft version still compiles twice (green throughout).** Two compiles of
  one draft version both succeed. Run before and after the change. It shows the guard does not
  over-refuse.
- **C4. Control: review → draft → compile (green after the change).** A version that a
  `changes_requested` decision returns to `draft` compiles again and returns 202. It shows the
  recourse in T2's text works.

**Not test-required:** the two `FOR UPDATE` locks (item 2). A test would need two concurrent
sessions against the shared test database. The executor shows the lock by citing the
`with_for_update()` lines in the ledger, and the auditor reads them. The ledger records this
as "delivered, not concurrency-tested", which is the §13 verdict this ruling expects. **An
existing test that compiles a non-draft Rating Version and expects success is a stop, not an
edit.** Report it to the lead. None was found:
`git grep -l -E "/compile|compile_rating_version\(" -- backend/tests` gives four files, and
the only `mark_approved` in `test_rating_version_compile.py` (`:594`) approves a model, not a
version.

## Interplay

- **WK-674 S2's own flow does not compile.** PL 9765 at `185e6759` names no compile route or
  `compile_rating_version` call (`grep -n -i -E "recompil|rating\.compile|compile_rating|/compile|compiles?\b"`
  prints nothing). Its Deployment records `bundle_hash` (`:892`, `:1014`). Under this ruling a
  version's `content_hash` and blob key cannot change after it leaves `draft`. So the hash a
  Deployment records stays equal to the row's for the version's lifetime, and FR-268's
  *"never a mix"* cannot be broken by a recompile.
- **#974 (RL-1380; DP-S2-1 (a)).** The trace links to the live Deployment when the
  explicit ref *equals* the Deployment's Rating Version (type, slug, version). That compares
  refs, not bundles. **This ruling is what makes ref equality imply bundle equality** for every
  version that can be live. Without it, a quote served by a recompiled bundle would be linked
  to a Deployment whose recorded hash names a different bundle. An explicit ref to a `draft`
  version is never live, so its trace stays null under DP-S2-1 (a). No conflict.
- **The score path's memo (F50, RL-921 §3).** A draft ref can still move, and draft versions
  are scoreable (`03:799`), so RL-921 §3's degradation-only rule for `hash_for` is unchanged.
  This ruling does **not** license a memo-first happy path. It updates only the docstring
  sentence that becomes inaccurate (item 5).
- **`content_hash` is not byte identity.** It covers the graph and pin refs and excludes
  resolved payloads (`compile.py:520-533`), while `blob_sha256` is the bytes. This ruling does
  not depend on which one FR-267's "bundle hash" means. Both are frozen once the version
  leaves `draft`. Reported to the lead as an observation, not ruled.

## Spec texts this ruling carries

Placement was read at `origin/main` `92b4e4ac`. Each find string was counted with `grep -cF`
over its file, and each prints 1. The placeholders are `<fix date>`, the date of WK-674 S2's
Task 5A commit written `YYYY-MM-DD`, and `<RL id>`, this ruling's minted id written `RL-NNNN`.
Nothing else in a text is a placeholder. All four texts land in **Task 5A's commit**, with the
code and the tests (`CLAUDE.md` §2's one-commit rule; FR-22's agreement check needs T3 and
`errors.py` together).

**T1 — `00` FR-4.** File `docs/specs/00-overview.md`, the FR-4 row (`:209`). Find
`nothing is edited in place or hard-deleted. |` and replace it with:

```text
nothing is edited in place or hard-deleted. *(Amended <fix date>, <RL id>: an Artifact's compiled output is part of the Artifact for this rule, not derived metadata outside it. A Rating Version's Bundle summary and blob key are written only while the version is `draft` (`03` FR-239); a version that has left `draft` gets a new compiled output only as a new version.)* |
```

**T2 — `03` FR-239.** File `docs/specs/03-rating-engine.md`, the FR-239 row (`:136`). Find
`is what gets cached and distributed. |` and replace it with:

```text
is what gets cached and distributed. *(Amended <fix date>, <RL id>, on FD 9754: a compile runs only while the Rating Version is `draft`. A compile requested for a version in any other status — `review`, `approved`, `live`, `retired` — is refused with `RATING_VERSION_IMMUTABLE` (409), synchronously by the route when the status is already non-draft and by the `rating.compile` Job, which ends `failed` with that code, when the status changed after submission; the version's Bundle summary and blob key are unchanged. A version in `review` is recompiled only after the decision path returns it to `draft` (`06` FR-355), which resubmits it through FR-257's gate; an `approved` or later version is never recompiled, and a new compiled output is a new version (`00` FR-4).)* |
```

**T3 — `03` §5.1, the owned codes.** Same file, the end of the owned-codes paragraph (`:845`).
Find ``orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*.``
and replace it with:

```text
orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*,
`RATING_VERSION_IMMUTABLE`
*(added <fix date>, <RL id>, WK-674 Slice 2 — **409**. FR-239: a compile of a Rating Version whose status is not `draft`. `POST /api/v1/rating-versions/{id}/compile` refuses it synchronously and creates no Job; a `rating.compile` Job whose version left `draft` after submission ends `failed` with this code. `app.platform.rating_versions.require_compilable` is the only raiser)*.
```

**T4 — `03` §5.1, the compile endpoint row.** Same file (`:793`). Find
`| **202** Compile + validate the bundle (FR-240) |` and replace it with:

```text
| **202** Compile + validate the bundle (FR-240); **409** `RATING_VERSION_IMMUTABLE` unless the version is `draft` (FR-239) |
```

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop.

## Disposition

- **DP-S2-7: decided, option (1)**, as above. PL 9765 is not edited by this ruling. Its
  Acceptance 19 and Task 5A are completed by the lead's dated delta, which names cases C1–C4,
  the write set (`rating_versions.py`, `api/models.py`, `errors.py`, `bundle_slot.py`, the
  regenerated contract, the two spec files, the test file) and T1–T4.
- **FD 9754 discharge:** this ruling, together with S2's Task 5A commit merged with C1 and C2
  shown red first.
- **To the lead, not ruled here:** (a) the absent `parent_id` on Rating Versions against FR-4's
  correction mechanism; (b) whether FR-267's "bundle hash" means `content_hash` or
  `blob_sha256`; (c) FD 9754's three corrections above (R1's file, `compiled_at`, and that
  "live" needs no Deployment lookup); (d) the effort question under *How this was ruled*.

## Verification

- `CLAUDE_EFFORT=medium` printed by this session.
- `git rev-parse origin/main` → `92b4e4ac155536f80a5be183ad21be88cc92868f`, tree
  `9cbc384fc042faeb6359b35aea9d01c1a730c197`, read 2026-10-01 10:40:52 and 10:42:41 BST.
- PR heads: #1064 `61a21edbee9baa51a77121296e48f9fc7f75c288`; #1062
  `185e6759c73f83a3f076c4673a94955d66e4602a` (DP-S2-7 present at `:852`), first read at
  `d844dc097744e28eab5ecaf5cb862452e18d7763` (no DP-S2-7).
- Placement counts, each `1`: `grep -cF "nothing is edited in place or hard-deleted. |" docs/specs/00-overview.md`;
  `grep -cF "is what gets cached and distributed. |" docs/specs/03-rating-engine.md`;
  `grep -cF "| **202** Compile + validate the bundle (FR-240) |" docs/specs/03-rating-engine.md`;
  ``grep -cF 'orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*.' docs/specs/03-rating-engine.md``.
- `RATING_VERSION_IMMUTABLE` is new: `grep -rn RATING_VERSION_IMMUTABLE docs/specs backend/src`
  prints nothing at `92b4e4ac`. The precedent is `01`'s `DATASET_VERSION_IMMUTABLE`
  (`01-data-management.md:929`; raised 409 at `backend/src/app/platform/datasets.py:535-540`).
  `VALIDATION_FAILED` was considered and refused. It is generic (`errors.py:383-385`), so a
  caller could not tell "this version is frozen, make a new one" from any other validation
  failure, and FR-403 makes the code the contract.
- Writers of `row.bundle`: `git grep -n -E "\.bundle\s*=" -- backend/src` → `rating_versions.py:199`
  and `:538` only.

*Drafted as working id 9751; minted 2026-10-03 as RL-1379 (the item-5 batch, with RL 9986 -> RL-1380 and FD 9772 -> FD-1381).*
