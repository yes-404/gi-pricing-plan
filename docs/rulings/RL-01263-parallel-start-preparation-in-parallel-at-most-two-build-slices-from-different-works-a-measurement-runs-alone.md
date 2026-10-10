---
id: RL-1263
family: ruling
title: Parallel start — preparation runs in parallel; at most two build slices from different Works; a measurement runs alone (process, on the maintainer's behalf)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: maintainer               # a process ruling, authored on the maintainer's behalf (§1.6 RL row)
tree: 19c395acad594d1b193da197461bec85201d2248
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: [RL-1445]
corrects: CR-1212
relates: [RL-871, CR-1212]
---

# RL-1263 — Parallel start: preparation runs in parallel; at most two build slices from different Works; a measurement runs alone

*Minted from working id 9760 at #928's merge turn, `RL-1263`, 2026-09-30 00:40:47 BST, by `doc-id.py next --ref origin/main` at aa14e90d. Where the maintainer's entry titles quoted below named the working id, the minted id is inserted in square brackets.*

## Verified first, at 19c395acad594d1b193da197461bec85201d2248

- **`docs/process/delivery-process.md` §8**, on main, before this ruling: "Sequential processing
  of a layer's **children** (Project→Phase→Work→Slice: no two Slices run at once, at any
  layer)". The interest it protects is "resource contention, not plan stability". An exception
  argued on plan-independence "argues past it". A contended NFR measurement "fails in the
  direction that gets booked as a pass".
- **RL-871** (`docs/rulings/RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md`)
  refused an exception to §8 argued on plan-independence. This ruling does not rest on that
  argument (see "Ground").
- **CR-1212** (`docs/closures/CR-01212-…md:333`), Proposal 2's maintainer acceptance: "WK-674,
  then WK-673, then WK-675; WK-690 independent; then WK-1170, then WK-1169;
  `delivery-process.md` §8 stands."
- **The resource budget changed on 2026-09-29.**
  - The VM was resized to e2-standard-8 (8 vCPU, 31 GiB).
  - Gate concurrency is enforced at 2 slots by the repository-root `conftest.py`
    (`_SLOT_COUNT`) and the `dev-commands` gate wrapper. The move from 3 slots to 2 is PR #925,
    open at this tree.
  - At 22:43 BST the maintainer's session measured 12 claude processes using 2.9 GiB in total,
    25 GiB free, and a load average of about 2 with one gate running.

## Ruled

**The user (the maintainer), 2026-09-29, about 22:45 BST:** "go ahead with the parallel start",
following "plz verify the plan and start works on outstanding works in parallel".

**The maintainer's decision, by delegation, quoted whole** from the entry "2026-09-29 22:46:27
BST — CORRECTION TO "PARALLEL START AUTHORISED" (22:45:35): it is done through a dated §8
amendment, not by breaching §8" in `~/gi-pricing-plan.local/channel/to-lead.md`:

> 1. **Preparation runs in parallel on every open Work, now:** map and leaf plans, rebases,
>    audits, DM rulings and records PRs. These are docs-only and hold no gate beyond the 2-slot cap.
> 2. **Build slices:** **at most 2 at once, from different Works**. Each holds one of the 2 gate
>    slots (#925). A third waits for a slot.
> 3. **An NFR-measurement slice, or any measurement step, runs alone.** Nothing else holds a gate
>    while it runs, per §8's correctness clause. Hold the other slot empty.
> 4. **Two concurrent slices must not edit the same files.** Known shared files (from my readiness
>    check at 19c395ac):
>    - `packages/model-schema/src/model_schema/approvals.py` (EVIDENCE_FLOOR/DEFAULT_POLICY):
>      WK-674, WK-673, and WK-1250 if its DP-1 is (a);
>    - `docs/specs/03-rating-engine.md`: WK-674 §3.10, WK-673 §3.11 and FR-266, WK-1250
>      FR-217/218, WK-690 FR-244, WK-675 §5.1;
>    - scoring `score.py` and `TraceStep`, and `compile_bundle`: WK-1250, WK-673 and WK-675 S7b.
>    Serialise the slices that touch the same file. `docs/INDEX.md` conflicts are regeneration only.
> 5. **The Work order in CR-1212 is relaxed to real dependencies only.** The planner re-derives
>    each "after WK-674" as either a dependency (a named slice or artifact) or bare sequencing;
>    bare sequencing is lifted. Known real dependencies:
>    - WK-675 S5 needs WK-673's F-W10-2 slice; WK-675 S8 needs WK-673 S4; WK-675 S9 needs WK-1250;
>    - WK-1250 S2's trace limb needs the FD-1246 ruling;
>    - the exit demo needs WK-673 and WK-674;
>    - WK-1169 comes after WK-1170.

**The merged wording**, from the maintainer's entry "2026-09-29 22:47:23 BST — DECISIONS ON YOUR
PARALLEL-START BUNDLE (A–D)", D1:

> - preparation (plans, rulings, rebases, mints, audits) **is not a slice** and runs alongside;
> - at most 2 code slices, from different Works, each holding a gate slot, with no shared files;
> - **any slice that takes an NFR measurement runs exclusive**: no other gate, suite or load test
>   while it measures. WK-674 S5 is named.
> - It amends CR-1212's "§8 stands", and cites RL-871 as the ruling it narrows, with the reason:
>   the maintainer's decision on the user's order. What changed is the resource budget (the
>   8-core box plus the 2-slot flock gate), not a plan-independence argument.

**What "no shared files" means**, from the maintainer's entry "2026-09-29 22:57:52 BST —
DECISION: [RL-1263, then working id 9760]'s "no shared files" means OPTION (c); lane B opens with WK-690", item 2,
quoted whole:

> Two concurrent build slices may not both change the same **existing** function, class, method, spec section, or policy table. Examples: `approvals.py` EVIDENCE_FLOOR/DEFAULT_POLICY; one `03-rating-engine.md` section; `score.py`, `TraceStep`, `compile_bundle`.
> **Registry files are exempt, and only these**, each for **append-only** edits:
> - `backend/src/app/db/models.py`: a new class appended; no edit to an existing class;
> - `backend/src/app/main.py`: a router registration or lifespan hook added; no other change;
> - `backend/alembic/versions/`: a new revision file;
> - generated files (`docs/contracts/**` generated outputs, `docs/INDEX.md`), regenerated and never hand-merged.
> **At the second merge**, the later slice must:
> - merge main in;
> - re-point its Alembic `down_revision` to the new head, so there is **exactly one head**;
> - regenerate generated files;
> - **re-run its full gate** on the merged tree.
> **Any other shared path serialises** unless the lead's dispatch record names the path and the check showing that no existing definition is edited by both. A file joins the registry list only by a dated amendment.

The entry's reason: "a list can be checked, while "registry-style" is a judgement that drifts.
The list stays closed until it is amended."

**Registry list, as corrected** by the maintainer's dated line, by delegation
(`~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-29 23:20:11 BST — DATED CORRECTION to the 22:57:52 option-(c) registry list (two paths)"), verified at main 25b0ead2. The quote above
stands as given; these two corrections apply to it:
1. "`backend/alembic/versions/`" reads **`backend/migrations/versions/`** (`backend/alembic`
   does not exist). auditor-plans2 found it.
2. "generated files (`docs/contracts/**` generated outputs, `docs/INDEX.md`)" reads **generated
   files, exactly: `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/`,
   `docs/INDEX.md`**. These are `scripts/generate-contracts.py`'s outputs (:32–33) plus the
   index. The hand-authored contracts (`docs/contracts/openapi/gi-pricing.yaml`,
   `docs/contracts/schemas/*.json`, `docs/contracts/schemas/common/`) are **not** exempt, and
   concurrent edits to them serialise.

**RL-871 §7's three conditions, adopted as the amendment's form.** *Confirmed with amendments
by the maintainer, by delegation: `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-29
23:11:20 BST — CONFIRMATION WITH AMENDMENT: [RL-1263, then working id 9760] finding 2 (RL-871 §7 conditions and the
override trigger)", checked against RL-871 :153–191.* RL-871 (`docs/rulings/RL-00871-…md` §7)
recommends that when the resource budget changes, §8 be amended, not excepted, and in resource
terms. Two children may build concurrently only when all three hold:

- **(i) Two independent executors exist.** Confirmed as met: each lane is a separately spawned
  executor, in its own worktree, holding its own gate slot.
- **(ii) Neither child's in-flight work includes an NFR measurement or a benchmark.** Confirmed;
  this is item 3 above: a measurement step runs alone.
- **(iii) Coordination state is published.** As amended:
  - **The enforcing mechanism** is the gate wrapper's flock slots (`/tmp/slots/gate-1..2`),
    which cap concurrent gates at 2 by construction.
  - **The coordinating record** is the lead's slot grant (slice, head SHA, BST time), written
    to `eta.md` "In flight" before each gate.
  - The runtime state file's `in_flight_expensive_verifications` announcement is also made but
    **not relied on**: #909 (its finding, working id 9640) records that writer as stale and wrong. It
    becomes the record by a dated note when #909's fix lands.

**RL-871's override trigger, made an obligation** (as amended). RL-871 names "a measurement shows
this machine carries two concurrent gate runs without contention". The 22:43 BST reading above
had one gate running, so it is not that measurement.
- **What is recorded:** for the **first three** concurrent gate pairs, the lead records each
  gate's wall-clock time, the load average and `free -h`, at start and at end.
- **The baseline** is the higher of #925's solo full Python gate (about 19 min, 22:37:32 →
  22:56:35 BST, at e937d766) and the next solo run.
- **Step-down:** if any gate exceeds 1.5× the baseline, or fails in a way that does not
  reproduce solo, the lanes step down to one build slice **at once**. The lead tells the
  maintainer and logs it in the slice's `LG-` ledger. Only the maintainer's dated line
  re-opens two lanes, after a re-measure.
- **When all three pairs pass,** RL-871's "without contention" is recorded as **met**, citing
  the three `LG-` entries.

## Ground

**This ruling rests on §8's own clause for revisiting it, not on plan-independence.** §8 cites
the reproduced design proposal's rationale: "this bounds context/resource usage per session ...
revisit only if resource budget materially changes". The budget has materially changed (see
"Verified first"). RL-871's refusal stands for what it refused: plan-independence is still not
an exception. What it is narrowed by is the enforced 2-slot gate cap. §8's correctness control
is kept whole: a measurement step runs alone.

## What it obliges

1. **`docs/process/delivery-process.md` §8** gains the dated amendment line the maintainer's
   22:46:27 entry gives, verbatim, in the same commit as this ruling.
2. **`docs/process/delivery-process.core.json`** (the derived extract, `meta.authoritative:
   false`):
   - `hierarchy.children_execution` and the `parallelism` block record the amended rule;
   - `meta.derived_from_digest` is re-derived against the amended markdown (checks 26 and 27).
     `meta.verified_against_tree` is **not** changed: `.github/workflows/docs.yml`'s
     `doc-id migrate --verify` stage reads it as the recorded pre-migration base (`0651c1e2` on
     main), not as the tree the digest was reconciled at. *(Corrected before merge, 2026-09-30:
     this item first said both fields are re-derived, which reddened the docs CI at 43710ff2.
     auditor-928 found it.)*
3. **CR-1212's "§8 stands"** (`:333`, `:474`) is amended by this ruling. CR-1212 is frozen; this
   ruling is the amending record, and CR-1212 gains `corrected_by: [RL-<minted id>]` at this
   ruling's mint turn (document-ids §1.5 permits `corrected_by:` on a frozen file).
4. **The lead**, which dispatches every slice:
   - runs at most 2 build slices at once, from different Works;
   - checks each pair for shared files before dispatch, and serialises any that share one;
   - keeps the second slot empty while any measurement step runs, WK-674 S5 among them.
5. **The planner** re-derives each "after WK-674" in the open map plans as a real dependency
   or as bare sequencing, and bare sequencing is lifted.

## Acceptance — the violation that must become detectable

- A third concurrent build slice, two concurrent slices from the same Work, or a measurement
  step with the other gate slot held. Each is visible in the runtime state file
  (`in_flight_expensive_verifications`) and in the gate slot locks (`/tmp/slots/gate-{1,2}`).
- Two concurrent slices whose plans name the same source file. The lead's dispatch record names
  the file check.
