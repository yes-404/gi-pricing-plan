---
id: RL-9566
family: ruling
title: WK-673 Slices 4 to 6 — the dislocation run is one Job guarded at 4 h, the movers blob holds no portfolio column, FR-224's default threshold is 10 % at the 99th percentile, and rate_table_diffs fails closed
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1267, RL-1264, RL-917, CR-927, WK-1178, FR-263, FR-224, FR-257, FR-242, NFR-499, NFR-493]
---

# RL 9566 (working id) — WK-673 Slices 4 to 6: the decision points of PL 9591, PL 9590 and PL 9589

## How this was ruled

- **Filed under working id 9566, reserved by the lead** (`handover/eta.md`, row "RL 9566",
  5 Oct 17:16:13). In the texts below, `RL-<n>` is this ruling's minted id.
- **Two kinds of decision are recorded here, and each says whose it is.**
  - **The maintainer's, by delegation:** DP-S4-1, DP-S4-3, DP-S5-2's default figures,
    DP-S6-1 and the E1 owner. They are in `~/gi-pricing-plan.local/channel/to-lead.md`, the
    entry headed *"2026-10-05 17:14:54 BST — FD 9572 placement accepted; WK-673 S4/S5/S6,
    A-1, A-2 and CR-838 DECISIONS (1–8)"*, items 1, 2, 3, 4 and 7. Item 8 is folded into
    RL 9668, not this record. Items 5 and 6 and the FD 9572 paragraph are other slices'.
  - **The decision-maker's (this role's charter: technical decision points):** DP-S4-2,
    DP-S4-5, DP-S5-1, DP-S5-3, DP-S5-4 and DP-S5-5. The entry headed *"2026-10-05 17:07:00
    BST"* called DP-S4-2's and DP-S4-5's recommendations "fine to present" and asked for
    DP-S5-1, 3, 4 and 5 "with recommendations"; the 17:14:54 entry does not rule them. The
    lead's order of 2026-10-05 (after 17:16 BST) says "as you recommended". They are ruled
    here as recommended in the memo below.
- **The evidence** is the decision-maker's memo
  `~/gi-pricing-plan.local/handover/dp-memo-wk673-s4-s5-2026-10-05.md` (2026-10-05,
  17:11:04 BST), read at `137bc817`. Every cite it carries that this record uses was re-read
  at the tree above (`4d3be141`); none had moved.
- **The plans are read at their PR heads:** PL 9591 (#1176, `ac8221eca47df4f4af7d3c8cfde2be54187620b1`),
  PL 9590 (#1181, `7db4d646ab13d04e4ef985b7d6d710f894576ebb`), PL 9589 (#1184,
  `a34248f6c476dc5dd19c85d52c2e3e7fd8aa5e80`). This record edits none of them.
- **T7 was added before the mint** on the maintainer's (by delegation) entry headed
  *"2026-10-05 18:49:06 BST — PL 9595: no completeness limb accepted (none invented); the
  score-time-only gap goes to a READ-ONLY check; PL 9590's 4.6 note: a DM reads it, then (a)
  or (b)"*, item 2, verbatim: "PL 9590's 4.6 note: YES, have a DM read 03 4.6 against
  DP-S5-3 and DP-S5-4 and answer which applies. If a ruling changes a behaviour 4.6 states,
  then (a): RL 9566 gains the 4.6 T-text pre-mint (RL 9566 is unminted), applied by S5. If
  4.6 states nothing the rulings change, then (b): the write-set row and Task 1's mention
  are dropped from PL 9590 pre-mint." The decision-maker read `03` §4.6 (`:514`–`:578`) at
  `ecbd1954` and found (a): §4.6 states what a `DislocationRun` holds and how each figure
  is computed, and DP-S5-4 adds a figure it does not define, which T4 already cites as
  "(§4.6)"; DP-S5-3 removes attribution from one kind of run, where §4.6 states
  attribution's `method` as `shapley` or `order_dependent` with no third case.

## The decision entry, verbatim (items 1–4 and 7)

Fenced so that its ids are read as quotation; `audit-docs.py` check 32 skips fenced blocks.

```text
1. DP-S4-3: CORRECTION of my 17:07:00 premise. "No raw quote inputs stored outside sampled traces" was FALSE as written: NFR-499 names three stores (traces, Golden Quotes in regression_suite_versions JSONB, regression cases), and RL-917 says "any further store requires its own requirement". RULING: option (d). The movers blob holds only quote_id plus the computed figures, and the /movers route joins the portfolio columns from the Dataset Version at read time. No new store; a dated 03 T-text at :1124. A red test: the stored blob contains no portfolio column.
2. DP-S4-1: ONE Job in P2, as a dispatch-record delta against PL-1267 :525-526 (the drafted text). Because the ESTIMATE for a full-portfolio K=6 re-rate is ~8.5 h (from CR-927's measured 5,093,947 rows/h/worker × 678,013 rows; 43 h at the NFR-493 floor), the Job is GUARDED: before launch it estimates its run time (DP-S4-5's estimate route) and REFUSES a run estimated over 4 h on one worker, with a message naming K and the row count ("reduce K or sample"). Fan-out is carried to WK-1178 with the 4 h trigger as its activation, re-decided at the Friday checkpoint. G2's dislocation run uses a small K and is well inside. The Celery risk is FIXED in S4, not noted: task_acks_late on Redis with no visibility_timeout (celery_app.py:46) redelivers any task over 1 h, so S4 sets broker_transport_options visibility_timeout above the 4 h guard, with the proposed test.
3. DP-S5-2, the DEFAULT figures (mine): OPTION D, `{quantile: 0.99, max_abs_change_pct: 10}`. The tail is the customer protection, and at the 99th percentile a 10% bound admits surrogates from R² ≈ 0.994 (s = 0.5) / 0.983 (s = 0.3) under the memo's stated assumptions. A (1% at p99) is refused: it needs R² > 0.9998, a de facto ban on the mode FR-223 made legal. CONDITIONS: (i) the default is recorded WITH the memo's labelled assumptions (normal log-deviation; premium deviation = model deviation; s = 0.5 / 0.3; no measured data) so the first real run can falsify them; (ii) S5's first freMTPL2 run reports the observed quantiles (DP-S5-4's fixed set) into its ledger, and the default is re-read against them at the next checkpoint; (iii) it is a per-workspace policy setting, so a stricter book sets its own; the default only governs when unset.
4. E1 OWNER: its OWN small WK-673 slice beside S5 (it needs only diff_algorithms, the rate-table diff and _baseline, all on main; off the critical path). ACCEPTED; the planner cuts the row and leaf. "Unowned" is closed.
7. S6 DP-S6-1 (06 §4.2's rating_version default, 06:360-362, names rate_table_diffs, gipp_check_if_enabled and change_summary, but DEFAULT_POLICY, approvals.py:344-349, does not): OPTION (c). Verify change_summary and gipp now; fail closed on rate_table_diffs until it is produced, owner WK-673 (the rate-table diff is S7's domain), named in S6's dispatch record, so a workspace copying §4.2 is refused with a reason naming the missing evidence, never silently.
```

## Locators — read at `4d3be141`

- `backend/src/app/worker/celery_app.py:46`: `task_acks_late=True`; `grep -rn
  visibility_timeout backend/src` prints nothing. `backend/src/app/worker/tasks.py`, module
  docstring: "A second delivery for a Job that is no longer `queued` is a no-op, not a
  second run."
- `docs/closures/CR-00927-work-item-record-wk-671-scoring.md:355`: NFR-493, "5,093,947
  risks/hour/worker", measured on 300,000 rows (W11 Task 3D). `docs/specs/02-modelling.md:2941`:
  "678 013 rows — freMTPL2's row count".
- `docs/specs/03-rating-engine.md:919-920`: the two dislocation rows of §5.1, with no
  permission and no code.
- `03:1124`: `dislocation_frame`'s row is `quote_id` … `origin_rung`, "then every portfolio
  column, in the portfolio's order"; "Slice 4 writes them to `largest_movers_blob`".
  `03:715`: `quote_id` is "the drill-down key for movers".
- `03:1340`, NFR-499 with RL-917's clarification: "Any further store requires its own
  requirement." `backend/src/app/platform/blobs.py:496`, `QUOTE_INPUT_BLOB_COLUMNS`.
- `packages/model-schema/src/model_schema/permissions.py`, `BUILTIN_ROLES` and `_analyst()`:
  `Permission.RATING_COMPILE` is held by `analyst` and `pricing_actuary`; `DATASET_READ` and
  `RATING_READ` by all six built-in roles; `SCORE_BATCH` by none.
- `backend/src/app/api/models.py:1276`: `start_regression_run` requires
  `Perm.RATING_COMPILE`.
- `packages/model-schema/src/model_schema/approvals.py:344-349`: `DEFAULT_POLICY`'s
  `rating_version` entry, evidence `("structural_diff", "regression_run",
  "dislocation_run")`. `docs/specs/06-governance.md:360-362`: §4.2's `rating_version` entry,
  evidence also naming `rate_table_diffs`, `gipp_check_if_enabled`, `change_summary`.
- `packages/model-schema/src/model_schema/deployments.py:55`, `class Environment`: fields
  `slug`, `name`, `description`, `promotion_order`, `requires_prior_environment`,
  `retired_at`, `live_deployments`.
- `backend/src/app/platform/rating_versions.py:704`, `_baseline`: "The most recently
  approved other version of the algorithm".
- `06:557`: `GET`/`PUT` `/api/v1/approval-policy`, "the workspace policy (FR-354)".

## Ruled

1. **DP-S4-1 (the maintainer's): one Job, guarded.** The attribution runs inside one
   `dislocation.run` Job. Before launch the run is estimated (item 4's route and code path),
   and a run whose estimate exceeds **4 hours on one worker** is refused with 422
   `VALIDATION_FAILED`, naming K, the policy count and the estimate, and saying "reduce K or
   sample the portfolio". The estimate is the route's rating count (replay or re-rate, as
   `method` says) divided by the rate in "Details" below. A run on a sampled Dataset Version
   is exact Shapley over that Dataset Version, so `RL-1264` item 3 ("a sampled portfolio is
   never presented as exact Shapley") is kept. **Fan-out is carried to WK-1178**, activated
   by the 4 h trigger, and re-decided at the Friday checkpoint (the maintainer's). Recorded
   as the dispatch-record delta D1 against frozen `PL-1267`.
2. **The Celery redelivery risk is fixed in Slice 4.** `build_celery` sets
   `broker_transport_options={"visibility_timeout": 21600}` (6 h), above the 4 h guard with
   room for the subset compiles. Its test is in "Acceptance".
3. **DP-S4-2 (the decision-maker's): (b).** `POST /api/v1/dislocation-runs` and `POST
   …/estimate` require `rating:compile` and `dataset:read` on the portfolio Dataset Version;
   `GET /api/v1/dislocation-runs/{id}` requires `rating:read`. (a) refuses WF-699 D6's
   Analyst, whose role cannot hold `score:batch` (FR-347). (c) lets a read-only role spend
   worker-hours.
4. **DP-S4-5 (the decision-maker's): (a).** `POST /api/v1/dislocation-runs/estimate`, 200
   with a `DislocationEstimate`, no Job. Its fields are PL 9591's (`derived_changes`,
   `policies`, `estimated_ratings`, `method`) plus `estimated_worker_hours`, the figure item
   1's guard compares. `POST /api/v1/dislocation-runs` computes the same estimate in the same
   code path, so the two cannot disagree.
5. **DP-S4-3 (the maintainer's): option (d).** `largest_movers_blob` holds `dislocation_frame`'s
   own columns only (`quote_id` through `origin_rung`), never a portfolio column. `GET
   /api/v1/dislocation-runs/{id}/movers` joins the portfolio columns at read, on `quote_id`,
   from the run's portfolio Dataset Version, and requires `rating:read` and `dataset:read`
   on that Dataset Version. The blob is not a quote-input store: it is **not** added to
   `QUOTE_INPUT_BLOB_COLUMNS`, and NFR-499 gains no carve-out. This replaces PL 9591's
   options (a) and (b), which both registered the blob.
6. **DP-S5-1 (the decision-maker's): (a).** As PL 9590 states it. Premise h is corrected
   (text C1); the conclusion, no production marker on an Environment, stands.
7. **DP-S5-2: the shape is (a), amended; the default figures are the maintainer's, option
   D.** `approximation_deviation: {quantile, max_abs_change_pct}` on the `rating_version`
   `ApprovalPolicyEntry`, refused on any other artifact type. **The default is `{quantile:
   0.99, max_abs_change_pct: 10}`.** Option A (1 % at the 99th percentile) is refused: under
   the assumptions below it needs R² > 0.9998, a de facto ban on the mode FR-223 made
   legal.
   - **Amendment to PL 9590's (a), on the entry's condition (iii):** "the default only
     governs when unset". An entry that leaves the field unset (null) is governed by the
     default, **not** refused. A workspace that wants a stricter or looser gate sets its own
     value in its policy (`PUT /api/v1/approval-policy`, FR-354). Nothing can switch the gate
     off: there is no value that disables it, and omission gives the default. PL 9590's
     "`None` fails closed" exists so that omission cannot opt out, and that still holds.
   - **It is the workspace's ApprovalPolicy, not a Setting.** `RL-1264` DP-3 (b) holds: no
     environment-variable override, and `07` FR-446 does not reach it. "Per-workspace policy
     setting" in the entry means this.
   - **The assumptions, recorded beside the default (condition (i)).** These are not
     measured data. (1) The per-policy deviation, ln(approximation ÷ exact), is normal with
     mean 0; this is optimistic in the tail, where a surrogate's misfit concentrates. (2) The
     premium deviation equals the model deviation; clamps and rounding are ignored. (3) Its
     spread is s × √(1 − R²), where R² is the GLM approximation's fidelity on the log scale
     and s, the spread of ln(predicted pure premium) across policies, is 0.5 (central) or
     0.3 (narrow). Under them, 10 % at the 99th percentile admits surrogates from R² ≈ 0.994
     (s = 0.5) or 0.983 (s = 0.3).
   - **The re-read (condition (ii)).** Slice 5's first freMTPL2 run writes the observed
     `abs_change_pct_quantiles` (item 9's fixed set) into its ledger. The default is re-read
     against them at the next checkpoint (the maintainer's).
8. **DP-S5-3 (the decision-maker's): (a).** `DislocationSpec.baseline_mode_override:
   Literal["exact"] | None`, valid only when `baseline_ref == candidate_ref`. The baseline
   bundle is compiled ephemerally through `WorkspaceResolver` under `RL-1264` DP-1's
   conditions, and attribution is not run for such a spec. It is the mechanism `PL-1267`
   names (`:557`).
9. **DP-S5-4 (the decision-maker's): (a).** `DislocationRun.abs_change_pct_quantiles` for
   the fixed set `"0.5"`, `"0.9"`, `"0.95"`, `"0.99"`, `"0.999"`, `"1"`. A policy's
   `quantile` must be in the set, validated at `PUT /api/v1/approval-policy`. The ruled
   default's 0.99 is in it.
10. **DP-S5-5 (the decision-maker's): (a).** 422 `EVIDENCE_INCOMPLETE`, naming the model, at
    `POST /api/v1/dislocation-runs` with the override and again at submission, when a model
    referenced in `approximation` mode has no GLM approximation (`02` FR-133).
11. **DP-S6-1 (the maintainer's): (c).** `change_summary` is verified when the summary is
    non-blank; `gipp_check_if_enabled` is verified while no workspace can enable GIPP (`04`
    FR-294, Phase 4). `rate_table_diffs` **fails closed** until it is produced, refused with a
    reason naming the missing evidence kind, never silently. **Owner: WK-673** (the
    rate-table diff is Slice 7's domain), named in Slice 6's dispatch record.
12. **The E1 owner (the maintainer's).** WF-699 E1, `03` FR-242's drafted change summary, is
    its own small WK-673 slice beside Slice 5: SL 9565 and PL 9564 (working ids), cut by a
    planner. It needs only `diff_algorithms`, the rate-table diff and `_baseline`, all on
    main. PL 9629's need 5 then cites that slice, not Slice 5.

### Details taken from main or chosen here (technical, no scope)

- **The rate in item 1's estimate** is a named constant in the Slice 4 handler module,
  `DISLOCATION_RATINGS_PER_WORKER_HOUR = 5_093_947`, citing CR-927 `:355`. When Slice 3's
  ledger records a measured dislocation-path rate (`RL-1264` item 1), Slice 4 uses that
  figure instead and cites the ledger. The bound is `DISLOCATION_SINGLE_JOB_MAX_HOURS = 4`,
  citing this record. At the CR-927 rate the bound admits about 20.4 M ratings: K ≤ 4 by
  re-rate on 678,013 policies (10.8 M), and any K by replay (1.36 M).
- **The guard's code is `VALIDATION_FAILED`**, the code the same route already uses for a bad
  partition (PL 9591 P1). No new code.
- **6 h for `visibility_timeout`.** It bounds how long a message for a dead worker host waits
  before redelivery, for every task kind. A worker process that dies while its host lives is
  still requeued at once by `task_reject_on_worker_lost=True` (`celery_app.py`, the line
  after `:46`), and a redelivery to a Job that is not `queued` is a no-op (`tasks.py`). So the
  cost is a slower recovery from a lost host only.
- **Why the movers blob is unreadable through `/blobs`:** `blob_readable_by` serves only a
  digest a Dataset Version's table or a Job's `JobResult(kind="blob")` references in the
  caller's workspace (`blobs.py`, the function after `:496`). The movers digest is referenced
  by the run row only, so `/movers` is its one reader without registering it.

## The texts

Each text gives the file, the find string, who applies it and the exact bytes. Every find
string was counted at `4d3be141` and occurs **exactly once** in its file. The placeholders
are `RL-<n>` (this ruling's minted id) and `<Slice N date>` (the date of the commit that
applies the text). Nothing else is a placeholder. Each is applied by its slice in one commit
with the code (`CLAUDE.md` §2).

### PL 9591 (Slice 4)

**T1 — `03` §5.1, the dislocation rows (PL 9591 P1, adopted with DP-S4-1's guard and DP-S4-3
(d)).** Find each of the two lines below (each occurs once) and replace the pair with the
four rows that follow.

```text
| `POST` | `/api/v1/dislocation-runs` | **202** Baseline vs candidate over a portfolio (FR-263) |
| `GET` | `/api/v1/dislocation-runs/{id}` | Dislocation artifact |
```

```markdown
| `POST` | `/api/v1/dislocation-runs` | **202** Baseline vs candidate over a portfolio (FR-263), with attribution where the versions differ in more than one respect (FR-266); body a `DislocationSpec`; requires `rating:compile` and `dataset:read` on the portfolio Dataset Version; 202 with the `Job`; **422** `VALIDATION_FAILED` when the change groups do not partition the derived changes (FR-1399), naming each change, or when the run's estimate exceeds 4 hours on one worker, naming K, the policy count and the estimate; the Job ends `failed` with `BUNDLE_COMPILE_FAILED` (a subset, FR-1398) or `ATTRIBUTION_RECONCILIATION_FAILED` (FR-1397). *(Amended <Slice 4 date>, WK-673 Slice 4, RL-<n>.)* |
| `POST` | `/api/v1/dislocation-runs/estimate` | The rating count and single-worker hours a run with this `DislocationSpec` would take (`RL-1264`'s feasibility rule), before launch, computed by the code path the run uses; the same permissions and the same partition 422 as the run; **200** with a `DislocationEstimate`; no Job. *(Added <Slice 4 date>, WK-673 Slice 4, RL-<n>.)* |
| `GET` | `/api/v1/dislocation-runs/{id}` | Dislocation artifact (FR-265); requires `rating:read`; **404** `NOT_FOUND` for an unknown id or another workspace's. *(Amended <Slice 4 date>, WK-673 Slice 4, RL-<n>.)* |
| `GET` | `/api/v1/dislocation-runs/{id}/movers` | The run's movers (FR-263's drill-down), each stored row joined at read on `quote_id` to the portfolio columns of the run's portfolio Dataset Version; requires `rating:read` and `dataset:read` on that Dataset Version. The stored movers hold no portfolio column, so they are not a quote-input store (NFR-499). *(Added <Slice 4 date>, WK-673 Slice 4, RL-<n>.)* |
```

**T2 — `03:1124`, what the movers blob holds (DP-S4-3 (d)).** Find:

```text
Slice 4 writes them to `largest_movers_blob`.
```

Replace with:

```markdown
Slice 4 writes them to `largest_movers_blob` with the frame's own columns only, `quote_id` through `origin_rung`, and never a portfolio column; `GET /api/v1/dislocation-runs/{id}/movers` joins the portfolio columns at read, on `quote_id`, from the run's portfolio Dataset Version, so the blob is not a quote-input store (NFR-499). (Amended <Slice 4 date>, WK-673 Slice 4, RL-<n>.)
```

T2 sits inside an italic paragraph (`*…*`), so its dated note is not itself italicised.

**D1 — the dispatch-record delta against frozen `PL-1267` `:525-526` (DP-S4-1).** Recorded in
Slice 4's dispatch record, never in `PL-1267`:

```text
PL-1267 Slice 4, "the subset re-rates fanned out across workers" (:525-526), is narrowed by RL-<n> item 1: Slice 4 runs the attribution in one dislocation.run Job, refusing a run estimated over 4 hours on one worker. Fan-out across workers is carried to WK-1178, activated by that trigger and re-decided at the maintainer's Friday checkpoint.
```

### PL 9590 (Slice 5)

**T3 — `03` FR-257 (`:174`), appended at the row's end (DP-S5-1 (a); PL 9590 P1, adopted
unchanged).** Find (once): ``is refused with `EVIDENCE_INCOMPLETE`. It applies forward, at
submit. |``. Insert before its final ` |`:

```markdown
 *(Clarified <Slice 5 date>, WK-673 Slice 5, RL-<n>.)* "The current live version" is the Rating Version live in the Environment the `rating_version` approval policy entry names in `dislocation_baseline_environment` (default `prod`, `06` §4.2). With nothing live there, the baseline is the most recently approved other version of the same algorithm; with neither, the version is the algorithm's first, limb (2) records `first_version` on the evidence, and no run is required. The run must name this version at its current bundle hash as its candidate and the baseline as its baseline; a run on an earlier bundle hash is stale and refused with `EVIDENCE_INCOMPLETE`.
```

**T4 — `03` FR-224 (`:110`), appended at the row's end (DP-S5-2 to DP-S5-5; PL 9590 P2,
amended for the default and the unset rule).** Find (once): `a plainly poor surrogate is
refused before a portfolio run is spent on it. |`. Insert before its final ` |`:

```markdown
 *(Decided <Slice 5 date>, WK-673 Slice 5, `RL-1264` DP-3 (b), RL-<n>.)* The threshold is `approximation_deviation` on the `rating_version` `ApprovalPolicyEntry` (`06` §4.2), a `quantile` and a `max_abs_change_pct`, default `{"quantile": 0.99, "max_abs_change_pct": 10}`; an entry that leaves it unset is governed by the default, and no value switches the gate off. It is never read from Settings or an environment variable. The exact-mode baseline is a Dislocation Run whose spec names the version as both baseline and candidate with `baseline_mode_override: "exact"`; its baseline bundle is ephemeral (FR-1398). The observed figure is the run's `abs_change_pct_quantiles` at the declared quantile (§4.6). The pre-check refuses, before a run and again at submission, a version referencing in `approximation` mode a model whose transparency artifact has no GLM approximation (`02` FR-133, FR-136), naming the model.
```

**T5 — `06` §4.2, a dated note after the `skippable_predecessors` note (DP-S5-1, DP-S5-2;
PL 9590 P3, amended).** Find (once) the note's opening, ``> **`skippable_predecessors`,
dated 2026-10-03 (WK-674 Slice 2; `RL-1296`).**``; the new note goes after that note's last
line, separated by one blank line:

```markdown
> **`approximation_deviation` and `dislocation_baseline_environment`, dated <Slice 5 date> (WK-673 Slice 5; `RL-1264` DP-3 (b); RL-<n>).** The `rating_version` entry carries FR-224's threshold, `{"quantile": 0.99, "max_abs_change_pct": 10}` by default, and the Environment whose live version is FR-257's baseline, `"prod"` by default. Both are refused on any other artifact type. An entry that leaves the threshold unset is governed by the default; a workspace sets its own value in its policy, and no value switches the gate off. Neither is a Setting (`07` FR-446 does not reach them). The default was ruled with these stated assumptions, not measured data: the per-policy deviation ln(approximation ÷ exact) is normal with mean 0; the premium deviation equals the model deviation; its spread is s × √(1 − R²) with s = 0.5 or 0.3. Under them it admits GLM approximations from R² ≈ 0.994 (s = 0.5) or 0.983 (s = 0.3). It is re-read against Slice 5's first observed quantiles.
```

**T7 — `03` §4.6, inside the "Bands and movers" paragraph (`:572`) (DP-S5-3 (a), DP-S5-4
(a); PL 9590's write set and Task 1, the dated §4.6 note).** Counted at `ecbd1954`, not
`4d3be141`. Find (once): ``an empty band has `policies` 0. A **mover** is``. Replace it
with:

```markdown
an empty band has `policies` 0. *(Added <Slice 5 date>, WK-673 Slice 5, RL-<n>.)* `abs_change_pct_quantiles`, FR-224's observed figure, maps each of the fixed set `"0.5"`, `"0.9"`, `"0.95"`, `"0.99"`, `"0.999"` and `"1"` to a quantile of the banded set's absolute percentage changes: with the n values in ascending order, quantile q is the value at rank ⌈q × n⌉ (nearest rank, so `"1"` is the largest), chosen exactly on the integers and written as a decimal string rounded once to 6 places toward +∞, so that the rounding never brings a figure under FR-224's bound that its exact value exceeds. With n = 0 every value is `null`, and FR-224's gate refuses a run with no figure. A run whose spec has `baseline_mode_override: "exact"` names one Rating Version as both baseline and candidate, and has no `attribution` and no `attribution_summary`. A **mover** is
```

Trial apply on `03` at `ecbd1954`: the find string counts 1 before and 0 after; the new
text's ``FR-224's observed figure, maps each of the fixed set`` counts 0 before and 1 after.
The §4.6 example is not changed by this text. Why these choices (technical, the
decision-maker's): nearest rank picks one policy's actual change, so the figure is exact
without interpolation; rounding toward +∞ is the safe side for an upper bound; the banded
set is the one §4.6 already defines a per-policy percentage change over; and `attribution`
and `attribution_summary` are already optional in `dislocation-run.schema.json`.

**C1 — PL 9590 premise h, a correction for the planner to apply at the plan's next pre-mint
edit (a citation fix, no scope).** The "At `137bc817`" cell reads "`slug`, `name`,
`predecessor`, `retired_at`". At `4d3be141` (`deployments.py:55`) it should read:

```text
`Environment` (`model_schema/deployments.py:55`): `slug`, `name`, `description`, `promotion_order`, `requires_prior_environment`, `retired_at`, `live_deployments`; no production marker
```

and DP-S5-1 option (c), "the last Environment in the predecessor chain", reads "the
Environment with the highest `promotion_order`". The conclusion is unchanged.

### PL 9589 (Slice 6)

**T6 — `06` FR-364 (`:145`), appended at the row's end (DP-S6-1 (c); PL 9589 P1, amended
for the owner).** Find (once): ``which this requirement's 2026-08-29 invariant permits. |``.
Insert before its final ` |`:

```markdown
 **Amended <Slice 6 date> (WK-673 Slice 6, RL-<n>): the `rating_version` floor is wired.** Submission of a Rating Version checks the union of the floor and the matching policy entry, in that order, and fails closed on any kind it cannot verify, naming it. `change_summary` is verified when the submitted summary is non-blank, the test FR-352's guard in `approvals.submit` applies; `gipp_check_if_enabled` is verified while no workspace can enable the GIPP check (`04` FR-294, Phase 4), and the slice that builds FR-294 replaces that verifier. `rate_table_diffs` has no persisted artifact yet and is refused, naming the kind, when a policy names it; owner: WK-673, the slice named in Slice 6's dispatch record.
```

## What it obliges

- **This commit:** this record only. No spec, plan or code file is edited here.
- **Slice 4 (PL 9591)** applies T1 and T2 with the code, writes D1 into its dispatch record,
  sets `visibility_timeout` (item 2) and does not register the movers column in
  `QUOTE_INPUT_BLOB_COLUMNS`.
- **Slice 5 (PL 9590)** applies T3 to T5 and T7, and writes the observed quantiles of its first
  freMTPL2 run into its ledger (item 7). The planner applies C1 before the mint.
- **Slice 6 (PL 9589)** applies T6 and names the `rate_table_diffs` owner slice in its
  dispatch record.
- **WK-1178** gains the fan-out follow-up (item 1), to be cut when the trigger fires or the
  Friday checkpoint rules.
- **A planner** cuts SL 9565 and PL 9564 (item 12).

## Acceptance — the violation that must become detectable

Each test is shown failing on deliberately broken input.

- **The movers blob holds no portfolio column (DP-S4-3).** After a run on a portfolio with
  extra columns, the stored `largest_movers_blob`'s columns are exactly `dislocation_frame`'s
  own, `quote_id` through `origin_rung`. With the handler writing `select_movers`' frame
  unchanged, the test fails. `/movers` returns those rows joined to the portfolio columns,
  equal to `select_movers` on the full frame; a caller without `dataset:read` on the
  portfolio gets 403. `GET /api/v1/blobs/{sha256}` on the movers digest gets 404.
- **The guard (DP-S4-1).** A spec whose estimate exceeds `DISLOCATION_SINGLE_JOB_MAX_HOURS`
  gets 422 `VALIDATION_FAILED` naming K, the policy count and the estimate, and writes **no
  Job row**. The same spec at `/estimate` gets 200 with that estimate. With the guard
  removed, the test fails.
- **The redelivery fix.** `build_celery().conf.broker_transport_options["visibility_timeout"]`
  exceeds `DISLOCATION_SINGLE_JOB_MAX_HOURS × 3600`. Red at `4d3be141`: the key is absent.
  And a second delivery of a `dislocation.run` message for a `running` Job does nothing.
- **The threshold (DP-S5-2).** With the entry unset, a run whose observed 0.99 quantile is
  above 10 % is refused at submission and one at or below is accepted. A workspace entry of
  `{0.99, 5}` refuses the second run too. With the default read as "no gate", the test fails.
- **DP-S6-1.** A policy naming `rate_table_diffs` refuses submission with a reason naming
  that kind; one naming `change_summary` with a non-blank summary does not.

Drafted as working id 9566.
