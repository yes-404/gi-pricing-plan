---
id: RL-876
family: ruling
title: the warm-worker refresh trigger is WK-674's, and Slice 1 owes it exactly two properties
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice1-rulings.md
---

## RL-876 — the warm-worker refresh trigger is WK-674's, and Slice 1 owes it exactly two properties

**The decision.** Recovery item 1 carries forward, from the unfiled WK-671 orientation report,
a refresh mechanism RL-867 never restated: each worker *"refreshed by a short background
poll against 'current hash for env X'"*, recommending *"poll over pub/sub … NFR-494's 30
s switchover budget has plenty of room for a ~1-2 s poll."* The recovery document asks a
decision-maker to *"confirm this mechanism (or rule a different one) when Task 1.3's refresh
behaviour is built."*

**Ruled: neither. The refresh trigger is not WK-671's to build, and Task 1.3 builds no refresh
behaviour.** The recommendation is declined as premature rather than wrong.

Rationale:

- **Nothing in Slice 1 or Slice 2 builds a cache tier for it to sit in.** A grep of the
  frozen plan for `redis`, `cache`, `warm`, `refresh`, `poll` and `slot` returns four hits
  in total, none of them a task: two in the tech-stack preamble (`:31`, `:33`), one that is
  Job-status polling for a 202 (`:292`), and Task 1.3's description of `CompiledBundle` as
  *"what a warm worker process holds after loading one"* (`:310`). `load_bundle` appears
  five times and is never described as called repeatedly or on a timer. Slice 2 has zero
  hits for all six terms. There is no in-process slot to refresh and no Redis tier to
  refresh it from.
- **The refresh trigger belongs to Deployment, and Deployment is WK-674.** A warm worker learns
  a new bundle exists *because a deployment switched* — `FR-268` (`:194`), `FR-267`,
  `03` §3.10, with `NFR-494`'s 30 s budget (`:782`) measured from the deploy command.
  DP1 already establishes Deployment and the Environment entity (`FR-428`) as WK-674's,
  three workstreams out. Ruling a refresh mechanism now is building ahead of the phase,
  which `CLAUDE.md` §9 forbids and §0's table routes to a spec change instead.
- **When it is ruled, "poll" starts behind, not ahead.** Two facts the orientation report
  did not have. First, the only mechanism `docs/specs/` actually specifies is a **push**:
  `FR-268` — *"Bundles are pre-warmed into cache before the switch"* — and `03` §6 step
  11, *"Backend Pre-warms the bundle, switches atomically, emits Audit Event +
  notification"* (`:706`). A sweep of all of `docs/specs/` for `poll`, `pub/sub`, `pubsub`,
  `subscribe`, `invalidate`, `refresh` and `warm` finds no refresh mechanism of any kind for
  the bundle cache. Second, `07` has already ruled against polling as a platform pattern,
  in a clause that names this exact situation: `FR-413`
  (`../specs/07-platform.md:102`) — *"**Event-triggered runs are not polled**: where a
  platform event should start a Job — a deployment creating its monitors (`WF-701`) — the
  transaction recording the event submits the Job in the same outbox write, so there is no
  sensor watching the database for something the platform already knows."* A deploy-time
  push is the platform's stated shape; a 1–2 s per-worker poll is the sensor it names. That
  is not a ruling against poll — `FR-413` scopes itself to Job submission, and a
  cross-process cache handoff is a different problem — but it means WK-674 starts from push and
  argues its way to poll, rather than the reverse.

**Disposition — no spec change; two properties Slice 1 must have so WK-674 has a choice left.**
Both are already implied by RL-867 and are stated here so Task 1.3 cannot quietly close
the option:

1. **`CompiledBundle` exposes the `content_hash` of the `Bundle` it was loaded from.** Every
   candidate switch mechanism — push, poll, or pub/sub — compares a held hash against a
   current one. A `CompiledBundle` that has forgotten its provenance cannot participate in
   any of them, and `FR-268`'s *"either the old or the new bundle, never a mix"* becomes
   unverifiable at runtime.
2. **`load_bundle` is pure with respect to the cache**: it consults no cache, registers
   itself in no global, and starts no background task. It takes a `Bundle` and returns a
   `CompiledBundle`. This is not merely tidy — `.importlinter:16-34` forbids `pricing_core`
   from importing `redis` at all, so any cache tier must live above it in `backend/`, and a
   `load_bundle` that owned a slot would put the seam on the wrong side of `ADR-703`.

---
