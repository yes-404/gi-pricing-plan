---
id: RL-890
family: ruling
title: D5: FR-258/259 are not silent about batch, and no open question is raised
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-3-4-rulings.md
---

## RL-890 — D5: FR-258/259 are not silent about batch, and no open question is raised

**The decision, restated.** The recovery document flags, and the readiness document carries as D5,
that *"FR-258/259 state no batch sampling default"* — recommending batch inherit the 1 % policy
*"or a 10M-row batch Job blows the annual storage budget in one run"* — and says it *"needs an
`OQ-` or a spec change from the decision-maker"*.

**Ruled: no `OQ-`, no gap. The suite answers it in three independent places, and the answer is not
the one the recommendation reaches for.** `OQ-RATE-8` is not taken.

### What the sweep found

1. **FR-259 scopes itself.** *"**In production**, traces are sampled (default 1 %, configurable,
   plus 100 % of declines and errors) and persisted for ≥ 13 months"* (`03:175`). The sampled
   stream is the production quoting path, not every code path that can produce a trace.
2. **Two more locations say *production* independently.** `03` §5.1's route is *"Sampled
   **production** traces (FR-259)"* (`:525`), and `05` §7 lists what it consumes from `03` as
   *"Sampled **production** traces, deployment events, premium ladders …"*.
3. **A dated amendment inside a requirement already divides the labour.** FR-317
   ([`../specs/05-monitoring.md`](../specs/05-monitoring.md)`:101`) carries: *"(Recorded 2026-08-26,
   OQ-627: A/E is computed from a full batch re-score of the exposure dataset (`03` FR-253),
   **not from traces**; trace sampling stays for quote-level metrics — conversion, declines,
   latency, constraint activation.)"* OQ-627 is **decided**, maintainer-accepted, and its
   reasoning is exactly D5's subject: full coverage comes from the batch re-score's own output; the
   trace stream is for the quote-level metrics where full coverage is unaffordable.
4. **NFR-500's budget is over quotes, not batch rows** — *"1 % sampling of 50 M annual
   **quotes**"* (`03:795`).

So the feared failure mode — a multi-million-row batch Job consuming the annual trace budget — is
of something the suite never asked for. **This is the same class as RL-856's finding and the
opposite result to D3's:** a claim of silence that a suite-wide grep dissolves, where the answer
was sitting in a sibling module's dated amendment that an id-based search never reaches.

### What follows for Slice 3 and Slice 4

- **Batch scoring contributes nothing to the sampled production trace stream, and `score_batch`
  takes no sampling policy.** Slice 3 builds none, and Slice 4's sampling applies to the real-time
  path only.
- **A batch run may still produce traces**, because FR-258 says *"Traces are the same structure
  in real-time and batch"* — but on request, per FR-258's own *"on request"*, and they are
  written with that Job's output under RL-888's row-plus-blob shape with the **Job** as their
  parent. They never enter `GET /api/v1/traces`, which `03` §5.1 scopes to production.

### Disposition

One spec change: FR-259 gains a dated clarification recording the scope its first two words
already carry and pointing at FR-317's amendment — because two independent readers, the recovery
document and the readiness document, both read the pair as silent, which is evidence the text
invites the misreading even though it does not contain it. No requirement's meaning changes.

**Acceptance test — the violation that must become expressible.** The violation is a batch run
whose traces land in the production stream: after Slice 3, `GET /api/v1/traces` must return nothing
attributable to a `score/batch` Job, and a batch run must not consume sample budget. Before this
ruling that could not even be asserted, because an implementer following the recovery document's
recommendation would have made batch traces *part* of that stream at 1 %. **The ruling is
overridden** if `score_batch` acquires a sampling rate parameter, or if a trace row written by a
batch Job is returned by the production traces route.

---

## Findings reported, not ruled

1. **The trace sampling rate is specified in three places and nothing reconciles them.**
   FR-448 (`07:174`) makes it a **workspace** setting; FR-431 (`07:142`) makes *"sampling
   rates"* part of **environment** configuration resolved by §3.8's precedence; and `05`'s Monitor
   shape carries `"trace_sample_rate": 0.01` inside a Monitor's own **population** block
   (`05:164`), which is a third declaration that a Monitor asserts rather than reads. A Monitor
   whose declared rate disagrees with the environment's actual rate computes A/E against a
   population that does not exist. Not WK-671's — the Monitor shape is `05`'s and the precedence is
   `07` §3.8's — and not urgent, since OQ-627 moved A/E off traces. Owner: the lead to place.
2. **`00` §4.1's ERD parents `ScoringTrace` on `Deployment`, which is the third WK-671 surface to hit
   the WK-674 dependency** after FR-250's default-live path (RL-880) and NFR-497's degraded
   read (RL-882). Three instances is a pattern rather than three coincidences, and it may be
   worth one register row naming the class instead of three naming the cases. A §14 plan-review
   question, which `CLAUDE.md` §12 puts outside this role.

---

## Sources — read at `d614f24`

- `docs/specs/03-rating-engine.md` — FR-254/255 `:165-166`, FR-258/259 `:174-175`, §4.5
  `Trace`, §4.6 `DislocationRun` `:447-472`, §5.1 `:525`, NFR-500 `:795`.
- `docs/specs/07-platform.md` — FR-410 `:99`, FR-418/419/420 `:112-114`, FR-431 `:142`,
  §3.8 FR-446/447/448 `:172-174`.
- `docs/specs/05-monitoring.md` — FR-317 `:101` including its 2026-08-26 amendment, the Monitor
  shape `:158-168`, §7's dependency table.
- `docs/specs/01-data-management.md` — FR-56 `:118`, `:352`, `:355`.
- `docs/specs/00-overview.md` — §4.1's ERD `:261`, NFR-459 `:523`.
- `docs/open-questions.md` — OQ-627 `:143`, decided 2026-08-26.
- `docs/plans/PL-00851-wk-671-five-decision-points-recovered.md` items 2, 4 and the flagged omission;
  `2026-08-29-w11-slices-2-4-planning-readiness.md` §9's queued table;
  `2026-08-29-w11-scoring.md` Slice 4.
- Code: `backend/src/app/platform/blobs.py:301-350`, `backend/src/app/platform/settings.py:194-201`
  and `:261-345`, `backend/src/app/platform/model_specs.py:53-140`; and the absence sweep
  `git grep -ln "ScoringTrace\|scoring_trace\|trace_sampling\|sample_reason" -- packages backend`,
  which returns nothing.
