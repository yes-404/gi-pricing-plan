---
id: FD-1393
family: finding
title: An approved or live rating version can be re-compiled, because compile reads no status, so its bundle ref and content hash change after approval (FR-4)
status: active
created: 2026-10-03
owner: auditor
tree: 8bd782acbbdde8e3b4195b5a0acb89183b5a0253
corrected_by: []
relates: [WK-674, WK-1178, FR-4, FR-238, FR-239, FR-267, RL-921, RL-922, RL-865]
---

# FD-1393 — An approved or live rating version can be re-compiled (FR-4)

## Finding

**Severity (proposed, the maintainer decides): MEDIUM now, HIGH from the first deployment.**
**Owner (proposed): WK-674 Slice 2.** **Prior art does not decide this question: it names the
behaviour and never asks whether FR-4 permits it** (see *Prior art*). **Working id 9754**,
minted at the records PR. Raised by dm-f35 in RL 9771 (#1060) as an observation, and confirmed
by auditor-1060.

**FR-4** (`00-overview.md:209`): *"Every Artifact is immutable once it leaves `draft`.
Corrections create a new version with `parent_id` set; nothing is edited in place or
hard-deleted."* A Rating Version is an Artifact with the lifecycle `draft → review → approved →
live → retired` (FR-238, `03:135`). **FR-239** (`03:136`) says it compiles to a Bundle with a
content hash; **FR-267** (`03:195`) says a Deployment records the bundle hash. No requirement
says when compilation is allowed.

**What happens today.** `POST /api/v1/rating-versions/{id}/compile`
(`backend/src/app/api/models.py:1233-1262`) needs only `Perm.RATING_COMPILE`. It submits a
`rating.compile` Job. `_rating_compile` (`backend/src/app/worker/rating_handlers.py:35-`) loads
the row with `load_rating_version`, which reads only the workspace
(`platform/rating_versions.py:126-138`). It then calls `compile_rating_version`
(`rating_versions.py:395-`), whose last statement rewrites the row's bundle summary,
`row.bundle = {"content_hash": ..., "bytes": ..., "compiled_at": ...}` (`:538-542`). The handler
then merges the new blob key into that dict (RL-915). **Nothing in the chain reads
`row.status`.** The only status check in the module is `submit_for_review`'s draft test
(`:278-283`). So an `approved`, `live` or `retired` version can be compiled again, and each
compile re-points the version's bundle and `content_hash`.

**`live` is a Deployment property, not a row status** (`model_schema/rating.py:32-38`: the version's own statuses `live` and `retired` are declared, and their transitions belong to WK-674). So a status test at compile covers `approved` (and `review`, `retired`) today; refusing a *live* version needs the Deployment record WK-674 S2 builds. That is a second reason the owner is S2.

**It does not always change the hash.** A compile resolves the pinned content as it is now. The
pins are rate tables, reference tables, a model, an algorithm and objectives
(`rating_versions.py:420-520`). Rate-table versions are immutable (FR-229). A reference-table
version has the lifecycle `draft` / `published` (`:495-505`). `compiled_at` is in the summary
(`:541`), and the Bundle may carry it. I did not measure whether `content_hash` covers
`compiled_at`. If it does, **every** recompile changes the hash. If it does not, the hash
changes only when a pinned artifact or the compiler changed. Either way the summary row is
rewritten in place.

**Why the audit event does not make it lawful.** `_rating_compile` captures `prior_hash`
before the call and audits `before`/`after` (`rating_handlers.py:47-52`, and the audit write after the blob put). That records the
change. FR-4 says the change must not happen. An audit event for an edit in place is not a new
version with `parent_id` set.

## Prior art: what it decides and what it does not

| Record | What it says | Does it decide that an approved or live version may be re-compiled? |
|---|---|---|
| Register row **F50** (`docs/findings/register.md`, row "`bundle_slot.py` immutability argument (F50)") | The `bundle_slot.py:28-31` docstring says "artifacts are immutable (FR-4) … The mapping cannot change under the memo." The row says that is wrong: `compile_rating_version` rewrites `row.bundle`, the route "carries no already-compiled refusal", so "a recompile of an already-compiled version re-points a pinned ref to a new hash", which "the repository already treats as a normal, audited event". Resolved 2026-08-30 by a docstring fix only (`6a44dd4`). | **No.** It treats the recompile as a fact about the code and corrects a comment. It never asks whether FR-4 allows it, and it names no status. |
| **RL-921 §3** (`docs/rulings/RL-00921-…`) | Same argument. The recompile is "a normal, audited event". The memo is safe only because it is read on the degradation branch. | **No.** The question was the memo's safety. FR-4 is cited only to say the docstring misused it. |
| **RL-922 §7** (`docs/rulings/RL-00922-…`) | Assigns the F50 docstring fix to WK-671 Slice 3 Task 3B. | **No.** It routes a docstring fix. |
| **RL-915 §4** (`docs/rulings/RL-00915-…`, "What this does not decide") | A recompiled version has several `rating.compile` job rows. It leaves open whether a version should keep several bundles. "If a later workstream needs history, that is an additive change… and it would then need the 'which one is live' policy that §2 refuses to have invented silently." | **No, and it points the other way.** It defers the question and names the missing policy. |
| **RL-865** (compile is 202 + Job) | The route's shape. | No. |
| `LG-1204` (WK-672 S2 ledger) line 380: "An RV in review cannot be recompiled." | A claim in a frozen ledger. | **No, and the code does not support it.** Compile reads no status, so a version in `review` can also be compiled again. What the ledger probably means is that the submit gate pins `bundle_hash` and refuses a bundle whose hash differs (`rating_versions.py:583-590`). That is a check at submit, not a refusal at compile. |
| **PL-1306** (WK-674 S2 leaf plan; the superseding plan 9765, now `PL-1392`, is a draft PR, not in `origin/main`) | A Deployment binds an `approved` version and records the bundle hash (`PL-1306` lines 424, 660, 772). The text names compile nowhere: `grep -n -i "recompil\|compile"` over it finds no refusal. | **No.** It records `bundle_hash` on the Deployment and does not say what stops the version's own `bundle` changing afterwards. |
| Spec `00`/`03` | Searched for "recompil" in `docs/specs/*.md`: no hit. FR-239/240 say what a compile validates, not when it may run. | **No.** |

**Verdict: nothing decides it.** F50 and RL-921 §3 are the two records that came closest. They
addressed whether a *memo* is safe given that a recompile can happen. They did not address
whether an *approved artifact* may change.

## Why this matters

1. **FR-4 and R1.** R1 (`00-overview.md:41`) says a `live` Rating Version is immutable and fully
   pinned. Recompiling it changes the stored bundle the version resolves to
   (`api/score.py:196-207` reads `content_hash` from `row.bundle`).
2. **FR-267.** A Deployment records the bundle hash at deploy time. After a recompile, the
   version's `row.bundle.content_hash` can differ from the Deployment's recorded hash. The
   scoring path then resolves a different bundle from the one that was approved and deployed.
   `trace_handlers.py:90` already treats "the version has moved on" as a condition (a)
   refusal, so the repository knows the state exists.
3. **Review and approval.** The submit gate pins `bundle_hash`, the suite hash and the
   regression run to the compiled bundle (`rating_versions.py:583-650`). A compile after
   submit moves `row.bundle.content_hash` away from the pins. I did not measure whether
   `decide` re-checks them. That is a gap in this finding, not a clean bill.
4. **Authorisation.** `Perm.RATING_COMPILE` is the only gate. It is the permission that also
   guards `POST …/regression-runs` (`api/models.py:1271`). A holder of it who is not a
   Deployer or an approver can change what an approved version resolves to.

## Evidence

**Code, at tree `8bd782ac…` (`origin/main` `1dd5e264`):** the chain above, by line.
`grep -n "status" backend/src/app/platform/rating_versions.py` gives status reads only at
`:278` (`submit_for_review`), `:346-360` (`decide`) and `:687` (a baseline query); none is on
the compile path (`:395-543`). `git grep -n "REVOKE\|trigger" -- backend/migrations/versions/06e5a5425a8b_rating_versions.py`
shows only `REVOKE DELETE ON rating_versions FROM PUBLIC` (`:61`). **There is no row trigger or
grant that stops an update of an approved row's `bundle`**, unlike the artifact-immutability
trigger work in `backend/tests/test_artifact_immutability.py`. So the database would not stop
it either.

**Red reproduction: reasoned from code, not run.** A run needs the shared test database, and
`conftest_db.py`'s teardown truncates every table in it (F45): another session's rows would be
lost. A red test would be: create a version, compile it, `mark_approved`
(`backend/tests/approved_rows.py`), compile it again through the route, and assert 409. Today
the second compile returns a Job that succeeds. Existing `test_rating_version_compile.py`
tests compile, then drive the Job; none compiles an approved version.

**Exposure, measured 2026-10-01, run before 10:31:26 BST (the clock at filing), read-only.**
`docker exec gi-pricing-postgres-1 psql -U gipricing …` over every `gipricing%` database, the
FD-1356 loop:

```sql
BEGIN READ ONLY; select count(*) filter (where status='approved'), count(*) filter (where status='live'), count(*) filter (where status in ('approved','live','retired')), count(*) filter (where status in ('approved','live','retired') and bundle is not null and bundle ? 'content_hash'), count(*) from rating_versions; ROLLBACK;
```

Result: `databases=81 with_table=78`, `TOTAL approved=0 live=0 approved_live_retired=0
of_which_compiled=0 all=0`. **No approved or live rating version exists in any local
database**, and `rating_versions` is empty in all 78. `deployments` does not exist (WK-674 S2
has not landed). **Limits:** local databases only; the 3 databases without the table are not
separated from errors; the set moves as worktree databases come and go; and an all-zero count
cannot show that the query works on non-empty data (`all=0` everywhere). The query and filter
text match `rating_versions` columns `status` and `bundle` (`db/models.py:1956-1974`), and the
loop matched 78 rows of five-column output, so it ran; I did not run it on a populated
database.

## Severity (proposed)

**MEDIUM now.** The code path is real and reachable by any `rating:compile` holder. Zero
approved or live rows exist, so nothing has been changed. There is no production.
**HIGH from the first Deployment**: the day WK-674 S2 lets a version go live, R1 and FR-267's
recorded hash are breakable by one API call. That is why the fix should land **with** S2, not
after it. The maintainer decides.

## Owner (proposed): WK-674 Slice 2

WK-674 S2 builds the Environment and Deployment record and "only `approved` deploys"
(`PL-1306`, FR-238/FR-267). It is the first workstream that makes `live` real and records a
bundle hash, so it is where the guard has to exist. WK-1178 (the overloaded queue,
`FD-1356`'s class) is the wrong owner: it holds approval-path bypasses, and this is a missing
guard on a different route. A status check at compile is a few lines. The decision about which
disposition is the real work.

## Disposition options (for a DM)

1. **Refuse compile when `status ≠ draft`** (409, e.g. `ARTIFACT_IMMUTABLE`). Matches FR-4
   literally and is the smallest change. A compile after submit goes back through `draft` by
   `decide`'s return-to-draft path (`rating_versions.py:350`). Cost: a `review` version that
   needs a recompile must be withdrawn first. Needs a spec line in `03` (FR-239 or a new FR),
   because no clause says when compile is allowed.
2. **Allow it, but bind the bundle to the version immutably.** Keep the recompile (for example,
   after a pinned reference table is republished) and make each compile a new bundle record,
   with the Deployment and the pins naming a specific bundle hash. This is what RL-915 §4
   names and defers: it "would then need the 'which one is live' policy". Larger. It needs a
   `bundles` history and a decision on what "live" resolves to.
3. **Document it as intended.** An FR-4 carve-out for `row.bundle` as derived metadata, not
   artifact content. That needs a dated spec amendment, and it still leaves the Deployment's
   recorded hash able to disagree with `row.bundle`. Weakest, because R1 says a live version is
   *fully pinned*.

**Recommendation: option 1, with the refusal in `compile_rating_version` (the service), not
only the route**, so `_rating_compile`'s handler cannot bypass it. Plus a dated spec line, and a
red test that compiles an `approved` version and expects 409. Option 2 is a later step if a
recompile of an approved version is a real use case; nothing in the specs says it is.

## Disposition

**Severity MEDIUM** (the maintainer, `to-lead.md` entry "2026-10-01 10:34:45 BST — FD 9754 (#1064, a non-draft rating version can be recompiled and its bundle rewritten): MEDIUM, owner WK-674 S2, and **S2 does not merge without the guard**; the option choice goes to a DM now"). Owner WK-674 Slice 2, which does not merge without the guard. **Discharged by `RL-1379`** (DP-S2-7, option 1) when WK-674 Slice 2 merges with the guard; the finding stays open until then.

## Corrections before the mint

Dated 2026-10-03 (18:34 BST), at the mint, from the auditor's audit of the ruling now minted as `RL-1379` (filed as working id 9751, #1068); the text above is as filed on 2026-10-01 and is not edited.

1. **R1's location is wrong in *Why this matters*, item 1.** The text cites "R1 (`00-overview.md:41`)". R1 is `03-rating-engine.md:41-43` ("R1 — A `live` Rating Version is immutable and fully pinned"); `00-overview.md:41` is an unrelated bullet and `00` has no R1.
2. **"Refusing a *live* version needs the Deployment record WK-674 S2 builds" is wrong** (the paragraph beginning "`live` is a Deployment property"). FR-238 (`03:135`) makes `live` a property of a Deployment, so a deployed version's own row stays `approved`; a `status != draft` test at compile refuses it with no Deployment lookup. That sentence's "second reason the owner is S2" does not stand; the first reason (S2 is the first slice that makes `live` real) does.
3. **Left as filed:** "I did not measure whether `content_hash` covers `compiled_at`" is an open question, not an error; `RL-1379` answers it (the hash excludes `compiled_at`).

Filed 2026-10-01 as working id 9754; minted 2026-10-03 as `FD-1393`.
