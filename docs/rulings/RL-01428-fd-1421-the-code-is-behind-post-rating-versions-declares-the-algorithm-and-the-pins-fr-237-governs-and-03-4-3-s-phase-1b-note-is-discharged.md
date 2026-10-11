---
id: RL-1428
family: ruling
title: FD-1421 — the code is behind, not the spec — POST /rating-versions declares the algorithm and the pins, FR-237 governs, and 03 §4.3's Phase 1b note is discharged
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: decision-maker
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [WK-669, WK-1178, CR-838, CR-1212, PL-1371, SL-1300, FD-1297, FR-223, FR-237, FR-240, FR-440]
---

# RL-1428 — FD-1421: which side is wrong about Rating Version pins over HTTP

**Decided by the maintainer, by delegation**, in the entry headed
*"2026-10-05 13:12:56 BST — DECISIONS 15 and 16; CORRECTION to my 13:03:23 item 11; a priority rule for HIGH G2 blockers"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 15, relayed to this session by the
lead: *"RL 9695 (FD 9708): OPTION (a). POST /rating-versions takes algorithm_ref and pins,
checked at compile, in a WK-1178 slice. FD-1421: HIGH, owner WK-1178, deadline before the P2
exit demo (it blocks G2 over HTTP)."* The options below were drafted before that decision
and sent as a DP; the section headed "Ruled" records it.

## How this was ruled

**Written 2026-10-05, from 13:06 BST, at effort `medium`** (`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"`
printed `CLAUDE_EFFORT=medium`), by the decision-maker session `dm-9708`, on the lead's brief
`~/gi-pricing-plan.local/handover/brief-dm-9708-2026-10-05.md`. **Working id 9695 is the
lead's allocation.** Every fact below was read at `origin/main`
`caa4e411a9c07a389cf47092a923c7761b2b92dc`, re-checked at 13:12 BST. Unminted records
(FD-1421, FD 9995, RL 9758, PL 9713) are cited in working-id form and kept out of
`relates:` (check 32).

**The question** (FD-1421, draft PR #1130, head `11f87e26`, section *Disposition*): *"which
side is wrong. Either the spec's §5.1 row and WF-699 C1 describe Phase 2 and the code is
behind …, or §4.3's Phase 1b note stands and §5.1 and WF-699 C1 should say the route creates
the minimal version and pins are set by a route yet to be specified. A third option is a
separate pin-setting route on a `draft` version."* The maintainer, by delegation, filed it as spec-vs-code with
sides unruled, on G2's path (`~/gi-pricing-plan.local/channel/to-lead.md`, entry headed
*"2026-10-05 13:04:03 BST — DECISIONS: FR-1399 = (β); exit-demo C1 finding OK; …"*, item 13).

## Verified first, at `caa4e411`

| Fact | Where |
|---|---|
| FR-237, no dated amendment: *"A **Rating Version** pins: one Rating Algorithm version, an exact Rate Table Version per referenced table, an exact Model/Peril Structure version per `model_call`, an exact Reference Table Version per `lookup`, and the input contract. Nothing is unpinned."* | `docs/specs/03-rating-engine.md:134` |
| §5.1, the `POST /api/v1/rating-versions` row: *"Create a draft Rating Version with pins (FR-237)"* | `03:908` |
| WF-699 C1: *"`POST /rating-versions` — declares the algorithm version and every pin: rate tables, peril structure, reference tables."* C4–C5: the first compile fails `PIN_NOT_APPROVED`; the actuary waits for the model's approval and **recompiles** — the pins declared at C1 are not re-entered | `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:70`, `:73-74` |
| §4.3's note: *"(Scoped 2026-08-27, W7-3 — OD1.) Phase 1b builds the **minimal subset** of this shape … Compile, score, rate tables, the `pins`/`evidence`/`bundle` blocks, `model_reference_mode`, and deployment stay Phase 2 (FR-440). The `RatingVersion` model in `model-schema` carries only the Phase 1b subset; a Phase 2 build widens the shape with the full contract."* No later dated line | `03:430-436` |
| `07` FR-440 (appended 2026-08-27, W7-3 — OD1): the demo seed creates a **minimal Rating Version** …; *"The full `03` surface — compile, score, rate tables, deployment — stays Phase 2."* | `docs/specs/07-platform.md:156` |
| FR-237 is in WK-669's scope: the row lists it under its pre-migration id, which `REDIRECTS.csv` maps to FR-237 (with FR-238 to FR-242); WK-669 is `status: closed` | `docs/REDIRECTS.csv:1189`; `docs/roadmap.md:620-632` |
| WK-669's close records FR-237 **delivered**, *"marker-evidenced (22: 3 …)"*, via W9-3 (#293), which *"widened `RatingVersion` (spec-reconciled vs `03` §4.3)"* and added `POST /rating-versions/{id}/compile`. No create route is in its row | `docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md:33`, `:40` |
| `model_schema.RatingVersion` **is already widened**: its docstring *"W9-3 widens the Phase 1b subset with the full contract: `algorithm_ref`, the exact `pins` (FR-237), `model_reference_mode` …"*; `algorithm_ref: ArtifactRef \| None = None`, `pins: Pins \| None = None`. `Pins` holds `rate_tables`, `models`, `reference_tables`, `custom_objectives` | `packages/model-schema/src/model_schema/rating.py:65-78`, `:138-170` |
| `RatingVersionCreate` (`extra="forbid"`) has `slug`, `dataset_version_id`, `model_ref` only; the handler docstring says *"Create a draft rating version with pins to a model (FR-237)."* | `backend/src/app/api/models.py:271-276`, `:1160-1171` |
| The seed sets the pins on the ORM row after the service creates it, and they are empty: `row.algorithm_ref = f"rating_algorithm:{DEMO_ALGORITHM_SLUG}@1"`, `row.pins = dict(_EMPTY_PINS)` | `examples/fremtpl2/model.py:396-397` |
| FR-240: compilation validates *"all references resolvable and at a sufficient maturity (FR-20)"*; `RATING_VERSION_UNPINNED` is compile's refusal for a version with no `algorithm_ref`, no `pins`, or a step ref not pinned at its exact version | `03:137`; `03:967-970` |
| Phase P2 is `status: active` | `docs/roadmap.md:556` |
| G2: *"`WF-699` end to end on the freMTPL2 seed … a Rating Version compiled with pins … from one command to a served page, in Phase 1b's form."* Ruled 2026-10-05 13:05:42 BST (the maintainer, by delegation): one command runs WF-699 A–E and its deploy step **over HTTP** | `docs/roadmap.md:566`; `to-lead.md` entry of that header |

Not verified, stated as pointers: RL 9758 (#1061, open) rules *when* FR-223 is checked on
"version pin writes" — title read, not the diff. FD 9995 (#980, open, head `9074f155`) — the
compile resolver has no peril-structure branch — read through FD-1421's account of it.

## Which side is wrong

**The code is behind. The spec is not inconsistent in what it requires now.**

1. **§4.3's note and FR-440 are a deferral *to* Phase 2, not a carve-out *of* it.** Both
   say what Phase 1b builds and that the rest "stay[s] Phase 2". P2 is the active phase. Read
   in P2, the note requires the `pins` block, so it agrees with FR-237, §5.1 and WF-699 C1.
   There is no second clause to choose between.
2. **The note is stale, not governing.** Its sentence *"The `RatingVersion` model in
   `model-schema` carries only the Phase 1b subset"* is false at `caa4e411` (`rating.py:138-170`):
   W9-3 did the "Phase 2 build" for the stored shape and for compile, and CR-838 recorded FR-237
   delivered. Nobody added the dated line saying the note was discharged.
3. **What W9-3 left out is the HTTP write.** CR-838's evidence for FR-237 is markers on the
   pinned shape and on compile. No row in it names the create route, so the "delivered"
   verdict covered *a Rating Version that holds pins*, not *a client that can declare them*.
   The request DTO kept its Phase 1b fields, and its docstring kept the claim. The seed
   compensates by writing the ORM row directly.
4. **WF-699 C4–C5 confirms the design intent:** pins are declared once, at C1, and validated at
   compile (FR-240). A recompile after an approval re-reads the same declared pins. A create
   route that stores the declaration and leaves the checks to compile is the shape the
   journey already assumes.

So: FR-237, §5.1 and WF-699 C1 govern. The note gets a dated line saying it was discharged.
The code is behind, and the gap belongs to a closed Work (WK-669), so the fix goes to the
standing maintenance Work, WK-1178, as SL-1300 (FD-1297's FR-237 fix) did.

## DP-1 — how a client declares a Rating Version's algorithm and pins

### Options

| | (a) The create route takes them | (b) Pins stay off HTTP in P2 | (c) A separate pin route on a `draft` |
|---|---|---|---|
| **Rule** | `POST /rating-versions` accepts optional `algorithm_ref`, `pins` and `model_reference_mode`. The shape is checked at create (422). Resolvability and maturity stay with compile (FR-240). Absent fields leave today's behaviour: compile refuses `RATING_VERSION_UNPINNED` | The create route stays minimal. §5.1, FR-237 and WF-699 C1 get dated clarifications that the pins are set outside HTTP in P2. A route is specified in a later phase | Create stays minimal. A new `PUT /rating-versions/{id}/pins` sets `algorithm_ref`, `pins` and `model_reference_mode` on a `draft` only (`RATING_VERSION_IMMUTABLE`, 409, otherwise) |
| **Which side was wrong** | The code (and CR-838's "delivered" reading of FR-237) | Nobody: the spec is amended to match the code | Both in part: §5.1's row is right that a client pins; WF-699 C1 gets a second step |
| **Effect on G2** (ruled 13:05:42: WF-699 A–E over HTTP) | **Met.** C1 is one HTTP call, as written. The exit-demo script needs no ORM write | **Not met.** WF-699 C1 can only run as the seed's ORM write (`examples/fremtpl2/model.py:396-397`), which is not HTTP. G2 would need the 13:05:42 ruling amended to allow it, which is the maintainer's to decide | **Met** with two calls (create, then `PUT …/pins`). WF-699 C1 splits into C1a/C1b |
| **Cost** | One WK-1178 fix slice: the DTO built from `model_schema` types (`ArtifactRef`, `Pins`, `ModelReferenceMode` — no hand-written shape), the service and row writes, the contract and generated client regenerated, negative tests. The spec change is small (T1–T3) | Spec only (T4–T6). But it moves FR-237's HTTP limb out of P2, which is a scope move for the maintainer (G1/G2), and it leaves the platform with no client-visible way to pin | A new route, a new FR, an audit event for a pin change, immutability rules, WF-699 rewritten. It also creates the re-pin route that the DP-S2-3 decision of the maintainer, by delegation (PL 9713, entry headed *"2026-10-05 13:03:23 BST — #1066 (FD-1416 mint) at a202f030: NO ACK YET, one false cite in the body; then decisions 10 and 11"*, item 10: *"no re-pin (no route exists)"*) relied on being absent |
| **Risk** | A version can be created with refs that do not resolve. That is today's state for the seed, and compile refuses it with a coded error | The demo's "over HTTP" is weakened at the step where pricing correctness is set | A mutable draft pin set is a second write path. RL 9758's FR-223 check point would then need to cover two writers |

### Trade-offs

(a) is the smallest change that makes the spec, the journey and G2 agree, and it adds no
concept: the stored shape, compile's checks and the refusal codes already exist. Validation
stays in one place (compile), so it cannot diverge between create and compile. (c) adds
flexibility the journey does not use (C5 recompiles; it does not re-pin), at the cost of a
second writer and of reversing an assumption the maintainer, by delegation, has already ruled on. (b) is cheapest
in this PR and most expensive for G2. It is also the silent "make the spec match the code"
move that `CLAUDE.md` §0 warns against, because it would record that the spec was wrong when
the evidence (WF-699 C4–C5, the widened `model_schema`, CR-838) says the code fell short.

**Dependency, whichever option:** a `peril_structure` pin declared over HTTP still does not
compile until FD 9995 (#980) is fixed. WF-699 C1 names "peril structure", so G2's demo depends
on FD 9995 as well as on this ruling. The exit-demo leaf should name both.

## Ruled

**Decided by the maintainer, by delegation, 2026-10-05 13:12:56 BST (item 15).** The entry is
cited by its header, *"2026-10-05 13:12:56 BST — DECISIONS 15 and 16; CORRECTION to my 13:03:23 item 11; a priority rule for HIGH G2 blockers"*. FD-1421's severity is **HIGH**, its owner **WK-1178**, its deadline
**before the P2 exit demo**, by the same item. The same entry's priority rule applies: a HIGH
finding that blocks G2 takes the first build lane that frees once its plan is active.

| DP | Ruling |
|---|---|
| Which side | **The code is behind.** FR-237, `03` §5.1 and WF-699 C1 govern. `03` §4.3's Phase 1b note was discharged by W9-3, with no line recording it. FR-440 is a Phase 1b seed requirement and is not in conflict |
| DP-1 | **(a)**, as recommended, with T3 amended on item 25 of the 13:20:26 BST entry (FR-223's mode check at create where `algorithm_ref` resolves). `POST /api/v1/rating-versions` accepts optional `algorithm_ref`, `pins` and `model_reference_mode`, typed from `model_schema`. Their shape is checked at create (422 `VALIDATION_FAILED`); their resolvability and maturity are checked at compile (FR-240), as now |
| Owner | **WK-1178**, a fix slice with its own leaf plan. It merges before PL-1371 §3.8 row 7 (exit demo (b), the scripted `WF-699` journey) needs C1. In the same slice the seed declares the algorithm and the pins through the create service, so nothing in `examples/` writes a pin to the ORM row after creation |

## The exact texts

**T1 to T3 (option (a)) do not land in this PR.** They change behaviour, so each lands in one
commit with the code it describes (`CLAUDE.md` §2), applied by the WK-1178 slice, as
`RL-1407`'s texts were applied by SL-1409. `<date>` is that commit's date. Each find string
has exactly one hit at `caa4e411`.

### T1 — `03` §5.1, the create row (a). Find `` | Create a draft Rating Version with pins (FR-237) | `` and replace it with

```markdown
| Create a draft Rating Version with pins (FR-237). The body takes `slug`, `dataset_version_id`, `model_ref` and, optionally, `algorithm_ref` (a `rating_algorithm` ref), `pins` (§4.3's `Pins`) and `model_reference_mode`; a ref of the wrong type in any of them is **422** `VALIDATION_FAILED`. Resolvability and maturity are checked at compile (FR-240), and a version created without `algorithm_ref` or `pins` is refused there with `RATING_VERSION_UNPINNED`. *(Amended <date>, RL-1428), FD-1421.)* |
```

### T2 — `03` §4.3's note (a). Find `` > build widens the shape with the full contract. `` and insert after it

```markdown
>
> *(Discharged <date>, RL-1428), FD-1421.)* This note scoped Phase 1b only. W9-3
> (#293) widened `RatingVersion` with `algorithm_ref`, `pins` and `model_reference_mode`
> (CR-838), and `POST /api/v1/rating-versions` declares them (§5.1, FR-237). The note's
> statement that `model-schema` carries only the Phase 1b subset is no longer true and does
> not govern.
```

### T3 — `03` FR-237 (a). Find `` and the input contract. Nothing is unpinned. | `` and insert before its final `` |``

*Amended 2026-10-05, before the mint, on the maintainer's (by delegation) entry headed *"2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap findings"*, item 25
(PL-1429 DP-1): "Check MODEL_REFERENCE_MODE_INCONSISTENT at create when algorithm_ref
resolves; an unresolvable ref stays compile's." The text first filed here ended "The create
route stores them and does not resolve them."; it is replaced by the last two sentences
below.*

```markdown
 *(Amended <date>, RL-1428), FD-1421.)* The algorithm version and the pins are declared when the Rating Version is created (`POST /api/v1/rating-versions`, §5.1) and are checked at compile (FR-240). Where `algorithm_ref` resolves in the workspace, the create route also checks FR-223's model-reference-mode consistency and refuses a mismatch with **422** `MODEL_REFERENCE_MODE_INCONSISTENT`, as RL 9758 (working id) item 2 binds every route that writes a version's `algorithm_ref` or `model_reference_mode`. An `algorithm_ref` that does not resolve is stored and left to compile, which refuses it.
```

**Ordering with RL 9758** (the same item 25): the FD-1421 slice and the slice applying RL 9758
both need `MODEL_REFERENCE_MODE_INCONSISTENT` registered. **The first slice to merge registers
the code and lands RL 9758 T1; the second drops its copy and says so.** Both dispatch records
name this; the second slice rebases, and its ledger records the dropped copy.

WF-699 C1 needs no change under (a): it already says what the route does.

### T4 to T6 — withdrawn

They were option (b)'s texts, given for comparison only (`03` §5.1's row, WF-699 C1 and
FR-237, each saying no route declares the pins in Phase 2). Option (b) was not ruled, so they
are void. Their text is in this PR's first commit, `68096376`.

## Acceptance — the violation that must become detectable

This record builds nothing. The WK-1178 slice carries these, each shown red on deliberately
broken input:

- *Violation: a pin cannot be declared over HTTP.* A test creates a Rating Version through
  `POST /api/v1/rating-versions` with an `algorithm_ref` and a non-empty `pins`, then compiles
  it through `POST …/compile` to `compiled`. Broken by dropping the fields from the DTO: the
  create is 422.
- *Violation: a malformed pin is stored.* A body whose `algorithm_ref` is not a
  `rating_algorithm` ref, or whose `pins.rate_tables` holds a `model` ref, is 422
  `VALIDATION_FAILED` and writes no row.
- *Violation: the create route checks maturity in a second place.* A version that pins a model
  in `review` is created (201) and refused at compile with `PIN_NOT_APPROVED`, which is
  WF-699 C4. After that model is approved, a recompile succeeds without a new create (C5).
- *Violation: the DTO hand-writes a shape `model_schema` owns.* The request model's
  `algorithm_ref`, `pins` and `model_reference_mode` are the `model_schema` types, and
  `generate-contracts.py --check` is green.
- *Violation: a pin is written to a row after creation.* After the slice, the predicate
  `grep -rnE "\.(algorithm_ref|pins)\s*=[^=]"`, run over the corpus `examples/` and
  `backend/src/`, matches no line; the seed passes both to the create service instead. At
  `caa4e411` it matches **0** lines in `backend/src/` and **2** in `examples/`, both the seed's
  post-create write, `examples/fremtpl2/model.py:396-397` (counted with
  `git grep -nE '\.(algorithm_ref|pins)\s*=[^=]' caa4e411 -- backend/src` and `-- examples`).
  So it is meetable, and it shows the write once one exists. *(Replaced 2026-10-05, before
  the mint, on the same entry, item 26 (PL-1429 DP-2). The predicate first filed here,
  `grep -rn "algorithm_ref\s*=\|\.pins\s*=" --include=*.py examples/`, has an unanchored
  `algorithm_ref\s*=` that also matches a keyword argument or a `==`.)*
- *Violation: a mode mismatch is accepted at create.* A create whose resolvable
  `algorithm_ref` has a `model_call` step whose `mode` differs from the body's
  `model_reference_mode` is 422 `MODEL_REFERENCE_MODE_INCONSISTENT` and writes no row; the same
  body with an `algorithm_ref` that does not resolve is 201 and is refused at compile
  (item 25).

## What it obliges

- **The lead, at the mint:** mint this record before FD-1421's plan, which cites it (the
  order of the maintainer, by delegation, in the entry headed
  *"2026-10-05 13:13:32 BST — PL 9716 noted; batching UNRELATED findings ≤3 per mint PR: APPROVED (a widening of my 10:47:03 rule); cite fix"*,
  item 5), replacing working id 9695 everywhere this commit writes it. File
  the WK-1178 slice row. **PL-1371 is frozen, so its §3.8 row 7 is not edited:** record the
  slice and FD 9995 as prerequisites of C1 in a dispatch-record delta against PL-1371, and the
  exit-demo plan names both when it is filed. *(Amended 2026-10-05, before the mint, on the
  entry headed *"2026-10-05 13:15:53 BST — DECISIONS 17–21 (PL 9689 DP-S3-2/3/6; FD 9707 DP-1; RL 9695 follow-ups)"*,
  item 21(i). The text first filed here said to add both to PL-1371
  §3.8 row 7.)*
- **FD-1421's planner:** the leaf plan cites this record for which side is wrong and for DP-1,
  and carries T1 to T3 and the acceptance list above as its scope, rather than re-deciding
  them.
- **The WK-1178 slice:** apply T1 to T3 verbatim in the commit that builds them,
  with the acceptance tests above. Correct the handler docstring, which today claims pins it
  does not take.
- **A correcting record for CR-838:** CR-838 recorded FR-237 *delivered* on evidence that did
  not reach the create route. It is frozen, so its body is not edited. A correcting record
  states the false "delivered", cites FD-1421 and has `corrects: CR-838`; CR-838 gains only
  an append to its `corrected_by:` (`docs/process/document-ids.md` :135-136; check 34). Before
  it is drafted, the lead checks `document-ids.md` §1.6 for which family and role may correct
  a CR; if that is the maintainer's, the maintainer accepts it at its ACK. *(Amended
  2026-10-05, before the mint, on the same entry's item 21(ii). The text first filed here left
  whether a correcting record was needed to the lead's verdict.)*

## Spec changes in this commit

None. T1 to T3 are the WK-1178 slice's to apply. T4 to T6 are withdrawn.
