---
id: RL-993
family: ruling
title: `WK-662` converts, as a `WK-` row with `status: retired`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-roadmap-transform-rulings.md
---

## RL-993 — `WK-662` converts, as a `WK-` row with `status: retired`

### 1. Verified first, at `f4cbbb7` — and the brief's premise corrected

**`WK-662`'s row is not under the archival heading.** Measured:

```
317  ### Original scope, for reference     ← Goal + Demo-able outcome prose only, 317–326
327  ### Workstreams                       ← sibling heading; WK-662's row is at 336, under this
```

Both are `###` siblings under `## Historical record` (269) — **whose own body says it is a
signpost, not a container**: *"This page is the forward-looking plan; the archive is at
`docs/findings/README.md`."* It is also the only unnumbered `##` in a file whose other eleven are
numbered. **So the nesting that would have to answer Q3 as posed is itself unreliable**, and
this is the third instance of that shape in this migration, after `plan-reviews.md`'s single
level-2 heading and `#### Phase 1b status` sitting inside `### Phase 1a`.

**The question does not need the nesting, because a dependency answers it.** Line 337:

```
| **WK-665** | freMTPL2 demo seed **and the demo entrance** | WK-660, WK-661, WK-662 | …
```

**`WK-665`'s `Depends on` cell names `WK-662`.** If `WK-662` does not convert, that dependency names a work
with no `WK-` id, and §1.7's resolver — which requires `WK-0*(\d+)` — cannot reach it. `WK-662` is
also referenced in the roadmap's own prose at 339 and in one filed plan.

**What `WK-662` is:** the pre-split frontend work, re-cut into `WK-663` and `WK-664`, both of which have
their own rows and are closed. The heading above its table says the original goal is *"now
superseded by the split above"*.

### 2. Ruled

**`WK-662` converts, as a `WK-` row with `status: retired`, its body naming `WK-663` and `WK-664` as the
works its scope was re-cut into.**

**`retired`, not `closed`.** §1.2a: `retired` is *"ended without completing — withdrawn, dropped,
rejected, deprecated, archived; **the reason is in the body**"*. `WK-662` ended without completing
*as `WK-662`*; its scope was delivered under two other ids. `closed` — *"completed its purpose"* — is
false of `WK-662` itself.

**`superseded` would be the exact word and is not available.** §1.2's `WK` status subset is
`draft → active → closed | retired`; `superseded` is not in it, and §1.2a is explicit that *"a
family uses a subset and never a synonym"*. So `retired` is the available term and the precision
lost goes into the body, where §1.2a says the reason belongs. **This is a real limitation of the
row vocabulary meeting a real case, and it is surfaced below rather than worked around.**

**Rejected: dropping `WK-662` as archival-only.** It is a live dependency target (§1). Dropping it
converts a resolvable reference into a dangling one inside the commit that cannot be re-run.

**Rejected: deciding it by how far the archival heading's scope reaches.** §1 shows that
question has no reliable answer in this document — and answering Q3 by it would have made the
outcome depend on a nesting the file does not honour.

### 3. What happens to what it does not choose

The archival framing is not discarded: *"now superseded by the split above"* is exactly the
reason §1.2a requires in the body, so the prose that would have justified dropping `WK-662` becomes
the justification for its `retired` status instead.

### 4. Acceptance — the violation that must become detectable

**The violation: a work id referenced by another row's dependency has no `WK-` row.**

- **Every work id named in any `Depends on` cell resolves to a `WK-` row after the migration.**
  *Violation: a dependency naming a work that does not exist.* `WK-662` is the positive control and
  the corpus supplies it — the check must fail today under the drop-it reading.
- **`WK-662`'s migrated row is `status: retired` and its body names `WK-663` and `WK-664`.** *Violation: a
  retired row with no reason* — which §1.2a requires and no check enforces.

---

## Surfaced for the maintainer's `RFC-` route — two vocabulary limits, batched

Neither blocks anything; both are cases where the corpus is wider than §1's words, found by
migrating rather than by reading. They join the `exit_criteria` / `exit criteria` divergence and
§8's *"eleven primary skills"* already on that route.

1. **`WK` has no `superseded`.** RL-993 uses `retired` for a work whose scope was re-cut into
   named successors, because the subset offers nothing better. Document families have
   `superseded` and `superseded_by:`; the two row families that can be re-cut — `WK` and `SL` —
   do not.
2. **`## Historical record` is a signpost at container level.** Not a standard defect, but the
   roadmap restructure will have to decide where its two lines go, and its own body says the
   archive is elsewhere.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **Which milestone section a multi-phase work sits under** | RL-992 fixes *"the phase the work was executed in"*; if any work was executed across two phases the rule needs a tie-break, and I did not measure whether one exists | **W37-6's executor**, as a measurement; a new finding only if a work spans phases |
| **Whether the restructure keeps, folds or replaces the source tables** | An editorial choice about the migrated document, not a standard question. RL-992 §3 item 3 constrains only that the diff must account for each | **The executor**, with the lead reviewing the shape |
| **The `#### Phase 1b status` inside `### Phase 1a` mis-nesting** | A structural defect in a governed document, same class as RL-978 §3 item 4 | **The lead**, as a finding — the roadmap's instance of a shape now seen three times |
| **Whether `owner:` follows §1.6 or the historical author** | Routed at RL-979 and still open | **The planner**, unchanged |

## Provenance

Routed by the lead on 2026-09-02 as one package, with rulings requested rather than options, an
explicit invitation to hand Q1 to the maintainer, and a condition that any answer to Q2 must say
what happens to the rows it does not choose. Q1 is ruled rather than handed over, on the ground
in RL-991 §2. Q3's premise was corrected by measurement before it was answered, and the
answer rests on a dependency reference rather than on the nesting the brief assumed.
