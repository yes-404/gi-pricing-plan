---
id: RL-9986
family: ruling
title: DP-S2-1 decided — an explicit-ref trace links to the environment's live Deployment only when it serves that version, else null
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1263]
---

# RL-9986 — DP-S2-1 decided: (a)

## How this was ruled

- **Effort.** Ruled at effort `medium`, on the lead's routing of 2026-09-30. The plan itself
  routes this point "to the decision-maker at medium effort: it concerns monitoring's input
  (`05`), not governance evidence". The session's `$CLAUDE_EFFORT` read `medium`.
- **Working id 9986.** It was checked free on every `origin/*` branch, in every open PR's
  title and body, and in the channel files. It is minted at the merge turn.
- **Sources.**
  - The decision point is DP-S2-1 of the WK-674 Slice 2 leaf plan, #973 (working id 9920,
    branch `wk674-s2-leaf-plan`, head `22cb24b3`), in its DP table (`:329`).
  - DP-S2-2 and DP-S2-3 are ruled separately, at high effort, in #971 (RL working id 9906,
    head `5fb440fb`), which introduces the deployment request row.
  - Neither record is minted, so both are cited in prose.

## Verified first, at 9f63d0feee524815e7e0c68c99a53ac3f80e6c37

The plan's premises (a) to (r) were re-derived at the same tree. The rows below are the ones
this point turns on, each read in its owning module.

| Premise | Where | Present? | What the source says |
|---|---|---|---|
| No Deployment object exists (plan's (a)) | `git grep -n 'class .*Deployment' 9f63d0fe -- backend/src` | **absent** | Prints nothing; greenfield |
| A trace's environment is a plain string (plan's (k)) | `backend/src/app/db/models.py:2140-2160`, `:2199` | present | "`environment` is a plain string, not a Deployment FK … `Deployment` does not exist before WK-674" |
| `00` makes every trace a child of a Deployment | `docs/specs/00-overview.md:263` | present | `Deployment ──< ScoringTrace (sampled) ──< MonitoringAggregate` |
| Only `/score` persists a sampled trace | `backend/src/app/api/score.py:288-323` calls `_maybe_sample_trace` (`:379`); `score_compare` (`:336-378`) does not call it | present | Compare and batch traces are not written through this path |
| A persisted real-time trace always has an environment | `score.py:407-418` | present | With no `caller.environment`, it raises rather than write (RL-916 part 3) |
| The trace row cannot be updated by the application | `backend/migrations/versions/835988d1de4c_scoring_traces_row_plus_blob_body.py:78` | present | `REVOKE UPDATE ON scoring_traces FROM {APP_ROLE}` |
| The explicit ref is the only scoring path today (plan's (j)) | `score.py:128-151` (`_required_ref`) | present | No ref gives 409 `NO_LIVE_RATING_VERSION` (RL-880) |
| Governance evidence does not read traces | `docs/specs/06-governance.md` (grep `trace`); `git grep -n scoring_traces 9f63d0fe -- backend/src` | **absent** | `06`'s only trace mentions are `rating:read` (`:265`), an audit `trace_id` (`:479`) and prose (`:47`). `scoring_traces` is read only by `api/traces.py` (`GET /traces`) and written by `platform/traces.py` |
| `uat_deployment` is a Deployment fact | `07-platform.md:140` (FR-429); `approvals.py:107`; #971 item 2 | present | "a prior successful deployment to `uat`". #971 pins it on the deployment request as "the id of the successful predecessor Deployment … or a skip record". It is never a trace |
| Traces feed monitoring | `03` FR-259 (`03:176`); `05-monitoring.md:376`; `00:263` | present | Sampled production traces go to `05`'s aggregates, keyed through the Deployment |

**Confirmed: DP-S2-1 does not touch governance evidence.** Evidence for a deployment is a
Deployment or a skip record on the deployment request (#971). No governance code or `06`
clause reads a trace's Deployment link. The link is monitoring's input only.

## Ruled

**(a).** When `/score` persists a sampled trace for a quote scored with an **explicit**
`rating_version_ref`, the trace's Deployment reference is the caller environment's live
Deployment **if that Deployment serves exactly the Rating Version the ref names**. Otherwise
it is null. A default-live quote (no ref) always carries the Deployment that served it.

**Mechanics** (Task 6):
- **Resolved together with the bundle.** The Deployment is resolved **once**, when the ref
  and bundle are resolved, before scoring. That value, the Deployment id or null, is passed
  to the trace write. It is never re-read at write time. So a switchover between scoring and
  sampling cannot attach the quote to a Deployment that did not serve it (`03` FR-268, `03:196`:
  "either the old or the new bundle, never a mix").
- **Written once.** It is written with the pending row, never back-filled: `UPDATE` is
  revoked on `scoring_traces`.
- **The comparison is exact.** The environment's live Deployment's Rating Version, pinned
  through its approved deployment request (#971 item 1), must equal the explicit ref as an
  `ArtifactRef`: type, slug and version. A different version of the same slug gives null.
- **The environment string is unchanged.** It is still written as today (RL-888, RL-916),
  so `GET /traces`'s production filter and existing readers keep their behaviour. The
  Deployment reference is additive.
- **Rows before Slice 2 get null**, as forced: no Deployment existed to serve them. The
  plan's Acceptance 3 tests this on pre-existing rows.

**Why (a).**
- It records the truth in both cases. A quote served by the live version is attributable to
  its Deployment, and `05`'s aggregates then include it.
- A what-if quote against another version is not attached to a Deployment that did not
  serve it, so it cannot distort that Deployment's A/E (`05` FR-317).
- **(b)** would detach live-version quotes that callers pin explicitly, and so under-count
  the live Deployment's monitoring for no gain in truth.
- **(c)** would break every caller that pins a version today, because RL-880 made the
  explicit ref the only path until this slice. It would also change the score route's
  contract, which is wider than this point.

**Compatibility with #971.**
- (a) needs only "an environment's live Deployment, and the Rating Version it serves". #971's
  Deployment row references an approved deployment request that pins the Rating Version and
  the target Environment's identity, not its name. So the comparison reads the Rating
  Version through that request.
- (a) is also robust to an Environment rename (`07` FR-428). The live lookup is by the
  caller's environment identity at resolution time, and the trace keeps the string it
  already keeps.
- None of #971's options changes (a).

**Departure from the recommendation: none.**

**Narrowness: narrow.**
- It fixes one nullable column's value rule inside Slice 2's own Task 6.
- No FR text beyond what the plan's Task 1 already writes for the trace link, no contract
  change to `/score`, and no governance effect (above).

## What it obliges

- **WK-674 Slice 2, Task 6.** Write `deployment_id` as ruled, resolved with the bundle.
- **Acceptance 7.** Its explicit-ref case carries these tests, each red first:
  - an explicit ref equal to the environment's live Rating Version → the live Deployment's id;
  - an explicit ref naming a non-live version, or another version of the same slug → null;
  - an environment with no live Deployment → null.
- **Acceptance 3** keeps null for pre-existing rows.

This commit edits no spec, plan or roadmap text.

## Acceptance — the violation that must become detectable

- *Violation: a trace of a what-if quote (explicit ref ≠ live version) carries the live
  Deployment's id.*
- *Violation: a trace of an explicit-ref quote whose ref equals the live version carries
  null.*
- *Violation: a trace's Deployment is re-resolved at write time.* A test switches the live
  Deployment between scoring and the trace write, and the trace must still carry the
  Deployment resolved with the bundle.
- *Violation: a pre-Slice-2 row gains a non-null Deployment reference.*
