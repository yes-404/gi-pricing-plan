---
id: PL-1348
family: plan
kind: leaf
title: WK-674 Slice 3L — The premium ladder, exact unrounded rungs, true operations, one rounding (FR-247, FR-248, NFR-496, FD-1336, FD-1330; RL-1329 in full): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-01
owner: planner
tree: 248dbf11aa0a044ff4eaadcaa32aa82960aa6740
phase: P2
work: WK-674
slice: SL-1345
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1342, RL-1329, RL-1346, RL-1343, FD-1336, FD-1330, OQ-1316, RL-1263, PL-1325, PL-1327]
---

# PL-1348 — WK-674 Slice 3L — The premium ladder: exact unrounded rungs, true operations, one rounding: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` and `python-test` (every task), `fastapi-service` (Task 4), `test-driven-development` (every red-first step) and `dev-commands` (the gate and the gate slot), and reads [`README.md`](README.md)'s five unchecked conventions before its first step. The executor is spawned from `.claude/roles/executor.md`, whose Model / effort line it quotes verbatim.

## Goal

Make the Premium Ladder tell the truth and prove it on every quote: each rung carries the
engine's exact unrounded value and the operation it really applied, the replay rounds once and
equals the payable to the penny, a clamp is recorded on the `constraints` rung, and a ladder
that does not reconcile is refused, in every Environment, never sampled.

**Architecture.** This is the ladder half of WK-674 Slice 3, carved out of `SL-1257` by the
maintainer's entry headed
`2026-09-30 23:57:25 BST — DECISION on the S3 halt: (A) carve the ladder half into its own slice; lane B takes WK-1250 S1 now`
(`~/gi-pricing-plan.local/channel/to-lead.md`, a local file outside the repository). It builds
`RL-1329` in full: the engine's `string()` reads in generated ZEN (`runtime.py`), a builder that
records exact values and recovered operations (`score.py`, with the rung mapping moved to a new
`rating/ladder.py`), the contract shapes (`model_schema`), the R0–R4 predicate in
`reconcile_ladder`, `_build_outputs` serving declared outputs exact and rounded once, and the
compile-time refusal of an unplaceable clamp. On top of it, the DP-S3-1 ruling turns a false
verdict into a refusal with `LADDER_RECONCILIATION_FAILED`. **The work already built for it is on a
salvage branch** from the halted WK-674 S3 dispatch; Task 0 says how it is taken and verified.

**Tech Stack:** Python 3.12, Pydantic v2, `decimal` (a context of at least 100 digits),
`zen-engine` 0.53.0 (`packages/pricing-core/pyproject.toml:64`), FastAPI, `prometheus_client`
(the existing `backend/src/app/observability/metrics.py`), pytest. No new dependency: no
`uv.lock` or `pyproject.toml` change.

**Spec:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — **FR-240** (`03:137`, with
  `RL-1329`'s dated clause), **FR-247** (`03:154`), **FR-248** (`03:155`, with `RL-1329`'s dated
  clause), **FR-261** (`03:178`), **FR-273** (`03:222`), §4.4 (the ladder example and its dated
  note), §5.1 (the owned-code list), §10 (`OQ-1316`, `03:1194`), **NFR-496** (`03:1165`). Line
  numbers are at the tree above.
- The rulings this slice executes: **`RL-1329`** (DP-S3-5), **in full**, and the DP-S3-1 ruling
  **`RL-1346`** (minted in mint batch 13a from working id 9983, PR #1026, whose text this plan
  was written from at `2b98b5aacb4ce37cc98deb7fe2d53fd7ff799008`; its presence on `main` is an
  activation need). **`RL-1343`** (OQ-1334) binds what this slice must **not** change.
- The findings it discharges: **`FD-1336`** (all three limbs and F4, with the NFR-496
  prod-sampling limb) and **`FD-1330`**.

**What this plan implements.** The ladder half of **`PL-1342`** (WK-674 Slice 3's leaf plan,
frozen, `draft`), by quotation. `PL-1342` is **not superseded and not edited**: its environment
half stays on `SL-1257`, behind WK-674 Slice 2. The ladder half is `PL-1342`'s Acceptance 1 (the
FR-248 and NFR-496 clauses only), Acceptance 10 (as `RL-1329` supersedes it in part), Acceptance
11 and 12, and the WK-674 S3 dispatch record's delta D1 (Acceptance 13, `RL-1329` in full) and
delta D2 (DP-S3-6).

## Status

Filed 2026-10-01 against the tree above, under **working id 9993**, reserved by the lead (the
only allocator, `FD-1338`). The id is minted at this PR's merge turn.

**Minted 2026-10-01 as PL-1348** (`python3 scripts/doc-id.py next --ref f689c7828cb05eb2298f3fec505a4638c4437a11`
printed `1346`, as the lead ran it, and the lead allocated `1348` in mint batch 13a, after `RL-1346`
(working id 9983) and `RL-1347` (working id 9984)). It was filed under working id 9993,
and this body keeps that id where it describes the filing. The two in-batch rulings are re-pointed
to their minted ids.

**`draft`.** It turns `active` only when every activation need below is met, each shown by its
command at a named `origin/main` SHA in the dispatch record.

### Activation needs — each checked by a command, in this order

**`PL-1342:70-81` is where WK-674 Slice 3 went wrong: its activation needs were never checked,
and the slice was dispatched with two of them unmet** (the maintainer's 23:57:25 BST entry,
"My miss, again"). So each need here is a command, and the dispatch record pastes each command
with its output and the `origin/main` SHA it ran at. **A need with no pasted output is unmet.**
The lead's GO check starts here, before anything else (the same entry: "My GO checks from now on
start by reading the plan's and slice's `status:` on main and every activation need, before
anything else").

Run from any checkout, after `git fetch -q origin`; `M=$(git rev-parse origin/main)` is the SHA
recorded.

1. **`SL-1345` is on `main`** (PR #1027 merged):
   ```bash
   git show "$M":docs/roadmap.md | awk '/^#### SL-1345 /{f=1} f && /^status:/{print; exit}'
   ```
   Expected: one line beginning `status: draft` (before activation) or `status: active` (after the
   flip). No output means #1027 has not merged: **unmet**.
2. **This plan is minted on `main`** (its mint batch merged):
   ```bash
   git grep -l -E '^slice: SL-1345$' "$M" -- docs/plans/
   ```
   Expected: exactly one path, and `basename <that path> | cut -c4-8` prints a number below
   `09000`: `01348` for this plan once minted. The working-id file printed `09993`: that, or no
   path, is **unmet**.
3. **DP-S3-1 is ruled and minted as `RL-1346`** (filed under working id 9983, PR #1026):
   ```bash
   git grep -l -E '^title: .*DP-S3-1 decided' "$M" -- docs/rulings/
   ```
   Expected: exactly one path, and `basename <that path> | cut -c4-8` prints a number below
   `09000`: `01346` when mint batch 13a is on `main`. A file printing `09983` is the working-id
   draft, not a mint: **unmet**. Then the dispatch record diffs the minted ruling against the
   text this plan was written from, and quotes the diff:
   ```bash
   git diff 2b98b5aacb4ce37cc98deb7fe2d53fd7ff799008:docs/rulings/RL-09983-dp-s3-1-decided-a-ladder-that-does-not-reconcile-refuses-the-quote-on-every-scoring-path-and-is-logged-and-counted.md "$M":<the path the command above printed>
   ```
   `git grep` prints each path as `<sha>:<path>`: strip everything up to and including the first
   `:` of the printed path before passing it to `git diff`.
   **Where the minted ruling and Task 4 differ, the minted ruling wins**, and the dispatch record
   names each difference (the rule `RL-1329` set for D1, applied again).
4. **The records this slice builds from are on `main`:**
   ```bash
   git ls-tree --name-only "$M" docs/rulings/ docs/findings/ | grep -c -E '/(RL-01329|RL-01343|FD-01336|FD-01330)-'
   ```
   Expected: `4`. Met at the tree above.
5. **No decision point of this plan is open.** DP-S3-1 is need 3; DP-S3-5 and DP-S3-6 are
   resolved (the table below). DP-S3-2 and DP-S3-3 are **not this slice's** (below). Nothing else
   to run.
6. **The status flip has merged, and the lead has given the go.** The flip (this plan and
   `SL-1345` to `active`) is its own PR, after needs 1–5 are pasted:
   ```bash
   P=$(git grep -l -E '^slice: SL-1345$' "$M" -- docs/plans/ | sed 's/^[^:]*://'); git show "$M":"$P" | grep -m1 '^status:'
   git show "$M":docs/roadmap.md | awk '/^#### SL-1345 /{f=1} f && /^status:/{print; exit}'
   ```
   Expected: both lines begin `status: active`. Then the lead's go, dated, in the dispatch record,
   with the maintainer's GO-check line (the template widening the 23:57:25 BST entry accepted:
   "every activation need of the plan is quoted and shown met, and the plan and slice read
   `active` on main", together with the DP-resolver line).

**Not an activation need:** WK-674 Slice 2. The ladder half "depends on nothing in Slice 2"
(`SL-1345`'s row in PR #1027). The scoring path's `Caller.environment` already exists
(`backend/src/app/api/deps.py:69`), which is all the DP-S3-1 ruling's log line and counter label
read.

### Build-start conditions (Task 0, after activation; not activation needs)

- **A free lane under `RL-1263`** (at most two build slices, different Works). The maintainer's
  entry item 4: "The ladder slice takes the first free lane after activation (likely lane A, when
  WK-690 S2 merges; different Works, per RL-1263)".
- **The salvage branch is on origin.** Read at planning time (2026-10-01):
  `git ls-remote origin refs/heads/sl-1257-ladder-exact` printed
  `ceb23a001ccfa02ab37065dff65e303e5180d533	refs/heads/sl-1257-ladder-exact`. The lead confirms
  the name and the line (the entry's item 6). A different SHA is a stop: report it.
- **The `compile.py` order** (the entry's item 3): WK-1250 Slice 1 (`PL-1325`, `SL-1339`) goes
  first on `compile.py` and `ALGORITHM_CHECKS`. **Task 5 of this slice does not start while
  WK-1250 Slice 1 is open**, unless the dispatch record shows, from both slices' actual diffs,
  that both are append-only on `ALGORITHM_CHECKS` with no existing line edited by both; then the
  second to merge merges `main` in and re-runs its full gate. The check that WK-1250 Slice 1 has
  merged: `git merge-base --is-ancestor <its squash SHA, named in the dispatch record> HEAD`
  exits 0. Tasks 1–4 and 6 do not touch `compile.py`, and may run while WK-1250 Slice 1 is open,
  subject to the write-set check below.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the
failing run is quoted in the ledger with its failing assert line **and the cause the step
predicts**; a failure for any other cause is a plan defect. "Red on broken input" means the guard
is green, then deliberately disabled, the test is shown red with the predicted cause, and the guard
is restored. **A test taken from the salvage branch is red first on the base the same way**: the
test files alone applied to the base, the failure quoted (Task 0 says how).

1. **Spec, first, through `spec-change`** (`PL-1342` Acceptance 1, the FR-248 and NFR-496 part,
   quoted from `PL-1342:106-115`):
   > **FR-248 (`03:155`) and NFR-496 (`03:1157`) each gain a dated clause**, citing the
   > maintainer's entry headed `2026-09-30 15:17:54 BST — audit round-up: decisions`: the
   > reconciliation runs on every scored quote in every Environment and is never sampled,
   > superseding their "sampled in `prod`"; the trace-sampling rate governs trace persistence
   > only. NFR-499 (`03:1160`) is not touched: its "sampled traces" are trace persistence, not the
   > reconciliation.

   NFR-496 is at `03:1165` at the tree above (`PL-1342` read `:1157` at `11c76b6c`); the executor
   re-reads both lines. `RL-1329`'s FR-240 and FR-248 clauses, its §5.1 code and its §4.4 note are
   already on `main` and are **not reworded**. **The DP-S3-1 ruling's own FR-248 clause** lands
   in that ruling's commit on the same table row, so "whichever lands second keeps both clauses
   when it merges (a one-row textual conflict)" (`RL-1346`, "Spec changes in this commit"). **The
   OQ-1316 note, byte-identical on both mirrors**, appended to the question cell of OQ-1316's row
   in `docs/open-questions.md` (`:138`) and in `03` §10 (`:1194`); the row's status stays open.
   The text is the FINAL WK-674 S3 dispatch record's (condition 1), verbatim:
   > *(Cross-reference added 2026-09-30, on the maintainer's instruction: if this question is decided (a), rounding recorded as its own rung, `RL-1329`'s R0 ("`round` appears only on the last rung") must be amended by that ruling; `RL-1329` says so itself.)*

   (Planner-9947's D1 carried a different wording for the same note. The FINAL dispatch record,
   which the maintainer checked, is later, and its condition 1 carries the text, so it is the one
   used.) Commands:
   `python3 scripts/audit-docs.py` exits 0 apart from check 31's expected working-id gap on any
   commit that carries one; and
   `grep -c -F "<the note above, verbatim>" docs/open-questions.md docs/specs/03-rating-engine.md`
   prints `1` for each file.
2. **The contract** (`RL-1329` §3; Acceptance 13 (f), item 5, below). `PositionalDecimalStr` in
   `model_schema/money.py`, red first on `Decimal("0.0000001")`, `Decimal("1.2E-28")` and
   `Decimal("1E+1")` (serialised `"0.0000001"`, `"0.00000000000000000000000000012"`, `"10"`);
   `LadderOperationKind`, `LadderOperation` and `LadderRung` per `RL-1329` §3, the new fields
   optional in both schemas; `Trace.ladder_check_version` (`PL-1342:282-295`, quoted in
   Acceptance 4); the hand-authored `docs/contracts/schemas/scoring.schema.json` in step;
   `03` §4.4's example replaced in the same commit. `uv run python scripts/generate-contracts.py
   --check` exits 0, and the contract guard (`backend/tests/test_contracts.py`) passes, quoted.
3. **`RL-1329` in full.** Every item of `RL-1329`'s section "Acceptance — the violation that must
   become detectable" (items 1–13) is an acceptance item of this slice, red first on the base, each
   in a named test the ledger quotes with its failing assert line. **The record's text is the
   authority**; D1's restatement follows, quoted from the `+` lines of
   `~/gi-pricing-plan.local/handover/s3-delta-source/pl9947-delta-5c17a4dc.patch` (planner-9947's
   commit `5c17a4dc56c61693a5b2cdd0461e62c4954767d2`, reverted from `PL-1342` and preserved
   there; a local file outside the repository), with the five places where D1 and `RL-1329`
   differ resolved for `RL-1329` as the maintainer accepted
   (`s3-delta-source/planner-9947-report.md`, "Where RL-1329 differs from the brief"). **Where
   this restatement and `RL-1329` differ, `RL-1329` wins.**
   - **(a) The golden-rung stop predicate** (`RL-1329` Acceptance 8, second count, as amended at
     the mint on the maintainer's entry "2026-09-30 17:14:16 BST"). For rung `i` of a golden quote,
     `new_i` is this slice's ruled value and `base_i` the baseline value; "the baseline is
     `origin/main`'s builder run on the same golden contexts at S3's base tree". **The slice stops
     if:**
     - on a `multiply` rung: **`|base_i − new_i| > 5 × 10⁻⁵ · |base_{i−1}| + (e_apply + e_ruled)`**
       minor units, where `base_{i−1}` is the previous rung in the baseline ladder;
     - on an `add` or a `round` rung, and on the first rung: **`|base_i − new_i| > e_apply +
       e_ruled`**, where on the first rung `e_apply` is the error of today's single rounding;
     - on a `constraints` rung where a clamp binds: **`new_i` is not exactly the bound**;
     - on a rung that is **`none` in the baseline ladder**: **`|base_i − new_i| > e_apply +
       e_ruled`**, with no 5 × 10⁻⁵ term (delta D2, DP-S3-6, decided by the maintainer in the
       entry "2026-09-30 22:45:30 BST": on `main` a rung is `none` only when it is not
       `multiply` and `round(raw) == prev`, so the difference is only the two roundings).

     `e` is "0.5 for a `half_*` mode, and 1 for `ceiling`, `floor` and `down`"; `e_apply` is that
     of the rounding today's builder applied, `e_ruled` that of the rung's declared `RoundSpec`.
     **"The comparison is evaluated in integers and `Decimal`, never in float."** The rung kind is
     the **baseline** ladder's recorded kind. **Any exceedance is reported to the maintainer,
     "with no looser fallback"**, and the slice stops. Command: the false-positive control's test
     (Task 6) prints the exceedance count and the maximum tightness
     `(|diff| − (e_apply + e_ruled)) / (5 × 10⁻⁵ · |base_{i−1}|)` per rung kind, the count of
     baseline `none` rungs, and exits non-zero on any exceedance. **Red on broken input:** with one
     baseline rung of one golden quote shifted to its bound + 1 minor unit, the test is shown red
     naming that rung.
   - **(b) The report line.** "if [`5 × 10⁻⁵ · |base_{i−1}| / |new_i|`] exceeds 2 × 10⁻⁴ on a
     golden quote (a factor below about 0.25), S3 reports it to the maintainer before it
     continues." The same test prints this ratio's maximum and the count above 2 × 10⁻⁴; a count
     above 0 halts the task until the maintainer's reply is quoted in the ledger.
   - **(c) The golden payable stop** (`RL-1329` Acceptance 8, first count, and §4): "golden quotes
     whose payable changes": **a count above 0 stops the slice**, reported to the lead. The
     executor never edits a golden fixture and never edits a stored suite version; a re-baseline,
     if the lead routes one, is a **new** suite version whose `change_note` cites `RL-1329`, and
     "any golden re-baseline is dated and needs the maintainer's ACK".
   - **(d) Directed-mode tightness**, conditional as `RL-1329` states it: **"If S3's golden set
     contains a directed-mode rung, S3's first run records its tightness as the first
     measurement."** The ledger records, from the first run, either the directed-mode rungs' count
     and maximum tightness per mode, or the count `0` with the predicate that found none (every
     golden rung's declared and applied mode, verbatim).
   - **(e) Post-clamp served outputs, exact and rounded once, both cases** (`RL-1329` §4 C2 and
     Acceptance 13). Each declared output is served as "the engine's exact `string()` value of the
     output step's source … rounded once with that step's own `RoundSpec`", never the float and
     never a second rounding.
     - **clamped:** on `FD-1330`'s min-premium quote, `/score` serves `office_premium_minor` =
       **5000**, the `constraints` rung's `value_minor` and the bound, not the office rung's 1436.
       `RL-1329` says this case "is green today and must stay green", so **its red first is
       against a planted mutation**: a `_build_outputs` that serves the rung's `value_minor` gives
       1436, and the test is shown red on it; the mutation and its red run are in the ledger;
     - **unclamped:** the served output equals its ladder rung's `value_minor` exactly. Red first
       on the base by the exact value: `RL-1329` Acceptance 1's `outputs["office_premium_minor"]`
       = **67358** (today 67357), and `FD-1336`'s served-outputs case, a scratch algorithm declaring
       `instalment_loading_minor`: **69402** after, **69399** today, with every `multiply`-kind rung
       output covered and `ipt_and_fees_minor` and `constraints_minor` kept as green controls;
     - a test asserts the served value is built from the exact string read, not from the float.
   - **(f) The rest of `RL-1329`'s acceptance, by item:** 1 the realistic-scale red case through
     `score_one` with `trace=True` (61234.5 → 70726), and the auditor's case (60000.4 → 69402) at
     unit level; 2 the scale sweep through a real ZEN evaluation, 1e3–1e7, 0–6 optional rungs,
     float32 risk, ≥ 200 quotes per cell, **at least two recorded seeds**, one mixed-operation run,
     100 % reconciled, **and the same sweep red over `origin/main`'s builder**; 3 the six
     planted-defect controls; 4 the near-tie prices 1235, not 1234, and a test fails if
     `_build_ladder` receives only floats (`FD-1336` limb 3's one input-level test, scoped to
     `_build_ladder`, not the module, because `score.py` uses `float` legitimately for the
     elapsed-time parse; "the builder refuses a float money operand with a named error, and the
     test plants one and expects the refusal"); 5 the contract (Acceptance 2); 6 the three §5
     shapes (a first rung that is not `risk_premium`, a payable-only ladder, a ladder with rungs
     but no payable rung); 7 the re-derivation test's `round` branch
     (`packages/pricing-core/tests/test_rating_score.py:224-225`) replaced by R4 (`FD-1336` F4:
     **"the NFR-496 test's round weakness, fixed here, red first"**, red at a realistic scale on the
     base); 8 the false-positive control's three stop counts, of which (a)–(c) above are two, the
     third being "quotes on which a clamp's comparison and disposition disagree" (a count above 0
     stops the slice for the lead); 9 `scripts/bench-rating.py` before and after, in the ledger, no
     budget changed, in a solo window (`RL-1263` item 3); 10 the binding clamp (`FD-1330`),
     including a `max` clamp and a step declaring both bounds, the replacement of
     `test_a_clamp_overrides_the_ladder_and_is_recorded_on_the_constraints_rung`
     (`test_rating_score.py:262`), and the placement refusal (Acceptance 6); 11 the
     engine-precision guard on `zen-engine` 0.53.0 (the eighth product
     `2095.3120014523377649903134154`); 12 the release note (Acceptance 9); 13 is (e) above.
   - **(g) `FD-1330`'s factor.** `FD-1330`'s acceptance says "`multiply` factor **1.1000**";
     `RL-1329` records it unquantised ("×1.1", "never quantised to 4 dp"). **`RL-1329` governs**:
     the test asserts `Decimal(factor) == Decimal("1.1")` and that the recorded string carries no
     4 dp padding.
4. **`PL-1342` Acceptance 10, where `RL-1329` leaves it standing** ("Everything else in Acceptance
   10 stands", `RL-1329`, "What this record supersedes"). The four superseded sub-bullets
   (`PL-1342:229-251`) are **not** acceptance items; `RL-1329` §5 replaces them. The standing
   parts, quoted from `PL-1342`:
   - the corrected premise (`PL-1342:217-228`), re-derived at the executor's base;
   - the false-positive control (`PL-1342:252-258`): "**every existing scoring fixture and every
     committed regression suite still reconciles under the real check.** … A fixture that fails
     is either a real defect, reported as a finding, or a check defect; it is never 'fixed' by
     editing the fixture." (Acceptance 6's clamp-fixture edit is the maintainer's named exception,
     below, and is not a fixture "fixed" to pass the reconciliation.) Every caller changes:
     `score.py`'s `reconcile_ladder` call (`:769` at the tree above), the FR-261 property
     (`properties.py:41` import, `:303` call), the export (`pricing_core/__init__.py:13`, `:31`),
     and the docstrings. **The FR-261 property takes the scoring-time verdict with its independent
     inputs; it never rebuilds the anchors from the ladder it checks** (`RL-1329`, "What it
     obliges");
   - the call-site red case (`PL-1342:263-272`): "`score_one` **with `trace=True`** on a
     one-penny-off ladder produces `ladder_reconciled` **False** (or DP-S3-1's refusal)" — by the
     DP-S3-1 ruling it is the refusal (Acceptance 5);
   - the property red case (`PL-1342:273-274`): "the FR-261 property over a planted off-by-one
     ladder fails (predicted red at the tree above: it passes, via the same vacuous check)";
   - the raise-site census (`PL-1342:275-281`), with the message carrying rung names and the
     difference as a decimal string in minor units (`RL-1329`);
   - `ladder_check_version` (`PL-1342:282-295`): "`Trace` gains **`ladder_check_version`** … absent
     or `1` means 'first rung and int-ness only, before this slice — **not** a reconciliation'; `2`
     means FR-248's full check. A dated `03` §4.5 note says so." Red first: a new trace carries
     `ladder_check_version = 2`. Value `2` means `RL-1329`'s predicate over `RL-1329`'s shape;
   - **never sampled** (`PL-1342:296-306`), with `RL-1329`'s restated rationale ("exact decimal
     arithmetic, in a context of at least 100 digits, over a handful of rungs"): "with
     `rating.trace_sample_rate` set to `0`, `score_one` on a one-penny-off ladder still yields
     not-reconciled (or DP-S3-1's refusal)"; the docstrings that say otherwise are corrected in the
     same commit (`pricing_core/money.py:63`, "asserted continuously in non-prod and sampled in
     prod", and `pricing_core/rating/score.py:62-103`).
5. **What a failure does: the DP-S3-1 ruling, `RL-1346`** (working id 9983, read at `2b98b5aa`; the minted
   text wins, activation need 3). Its Acceptance 1–9, each red first on the slice's base before
   the refusal is added, on ladders built by this slice's builder, "planted" meaning a test-only
   mutation of the builder's output recorded in the ledger with its red run:
   1. through `score_one`, `trace=True` **and** `trace=False`, a ladder with one rung planted one
      minor unit off raises `CodedError` with code `LADDER_RECONCILIATION_FAILED`;
   2. an authored R0 case (a clamp whose `condition` and `clamp_bounds` disagree on a binding
      quote) is refused through `score_one`;
   3. `POST /api/v1/score` answers 500 with an RFC 9457 body whose `code` is
      `LADDER_RECONCILIATION_FAILED`; the body and the log line carry no sentinel planted in a quote
      input; this case's `scoring_traces` behaviour is unchanged from `36b2a121` and is not asserted
      (FR-259's error floor on `/score` is an open question, `RL-1346` "Observed, not ruled");
      `gip_ladder_reconciliation_failed_total` rises by 1 for that Environment;
   4. with `rating.trace_sample_rate` set to 0, case 3 is refused the same way;
   5. `POST /api/v1/score/compare`, the failing version on either side, answers 500 naming that side;
   6. `score_batch` over case 1's quote and a good quote writes one `"error"` row with that
      `error_code` and one scored row; the Job's per-type counts show one; no sentinel;
   7. a Regression Suite whose `LadderReconciles` property meets case 1's quote records it as a
      counterexample;
   8. the raise site is in `packages/pricing-core/tests/test_quote_input_raise_sites.py`, and a
      message that carries an input value fails it (red on broken input); the worker census
      (`backend/tests/test_worker_raise_sites.py`) stays green;
   9. controls: a correct ladder is served (200) with `ladder_reconciled: true` and
      `ladder_check_version: 2` on its trace; an empty ladder is not refused; `RL-1329`'s
      false-positive control over every fixture and committed suite has **no** refusals (a count
      above 0 stops the slice for the lead).
6. **The placement refusal, and the two test fixtures it refuses** (`RL-1329` §2 step 5, W-c, S1;
   Acceptance 3 (f) item 10). `_check_clamp_placement` is appended to `compile.py` and registered
   in `ALGORITHM_CHECKS`; `LADDER_CLAMP_UNPLACEABLE` is appended to `RATING_ERROR_CODES`
   (`backend/src/app/errors.py:297`); the three `RL-1329` algorithms are refused at save and by
   `compile_bundle`, red first (today all three save and compile); #967's closure test (ii) passes.
   **The clamp-fixture stop, resolved by the maintainer** (the 23:57:25 BST entry, item 5, "a
   test-only fixture edit is ALLOWED"):
   - The two refused fixtures are the functions named **`valid_algorithm`**, at
     `packages/pricing-core/tests/test_rating_compile.py:15` and
     `backend/tests/test_rating_algorithms.py:17`. (The halted slice's ledger and the entry call
     them `::_algorithm`; no function of that name exists in either file at the tree above,
     `grep -n 'def _algorithm' <both files>` prints nothing. The function meant is the one whose
     clamp the check refuses.) Each has one clamp, `s_minprem`, that consumes and produces
     `office_premium_minor`, and one output step, `payable_premium_minor`, reading
     `office_premium_minor`: a clamp on the source of a rung **after** `constraints`, with no rung
     before it, so the check refuses it.
   - Each gets a **placeable** clamp, the score fixture's shape
     (`packages/pricing-core/tests/test_rating_score.py:46-100`): the clamped name is the source of
     the last rung present before `constraints`, and the payable reads a later name. For example,
     an `s_out_office` output step (`office_premium_minor`, consuming `office_premium_minor`,
     `half_even`, `dp` 0) and an expression step that the payable output consumes instead of
     `office_premium_minor`. The executor chooses the least edit that makes
     `_check_clamp_placement(RatingAlgorithm.model_validate(valid_algorithm()))` return `[]` and
     keeps every other test in both files green, and corrects each docstring's step count.
   - **Each is listed in the ledger with its full `before` and `after` text.**
   - **`_check_clamp_placement` is unchanged by the fixture edit** (`git diff` of `compile.py`
     between the commit before the fixture edit and after it is empty).
   - **A test keeps the old shape refused**: the pre-edit `valid_algorithm` body, kept verbatim
     as a named constant in the test module, is refused with `LADDER_CLAMP_UNPLACEABLE`, at save
     (`backend/tests/test_rating_algorithms.py`) and by `validate_algorithm`
     (`test_rating_compile.py`).
   - **The recount is recorded with its command**: every committed algorithm with a clamp,
     enumerated by
     `git grep -l -E "on_violation[\"']?[:=] *[\"']clamp[\"']" -- ':!docs/**'` and
     `git grep -l -i -E 'clamp_bounds|"clamp"' -- ':!docs/**'`, each hit of either classified
     (test fixture, seed, example, script), each non-test algorithm run through
     `validate_algorithm`; and every row of the `rating_algorithms` table
     (`backend/src/app/db/models.py:1999`, its `content` column) in each database the executor's
     worktree reaches, loaded with `RatingAlgorithm.model_validate` and run through
     `_check_clamp_placement`, with the script and its output in the ledger. **Expected: 0 seeds,
     examples, scripts or stored algorithms refused.** A count above 0 stops the slice for the lead
     (`RL-1329` §2 step 5). A database that is not reachable is recorded as not measured, and the
     lead decides.
7. **R2: a declared non-rung `money_minor` output is served exact, rounded once, as an integer**
   (`RL-1329` §4, S6, and Acceptance 13; its own line, the dispatch record's D1 note). Red first on
   the base: an algorithm declaring a non-rung output `fee_minor` of type `money_minor`, whose
   output step's source evaluates in the engine to the near-tie `1234.50000000000000012345`
   (`RL-1329` part 1), `half_even`, `dp` 0: `score_one(...).outputs["fee_minor"]` is the `int`
   `1235`, and the JSON body of `POST /api/v1/score` carries `"fee_minor": 1235`, an integer.
   Predicted red on the base: the value is the `float` from `result`, `1234.5`, so the `isinstance(
   …, int)` assert fails. **And `RL-1343` holds** (its "What WK-674 Slice 3's dispatch record must
   carry", items 2 and 3, which bind this slice because it carries the `_build_outputs` change):
   a declared non-rung output of type `decimal`, `bool`, `string` or `date` is served exactly as
   on the base, value and JSON type; `_build_outputs` never puts the `string()` read or a `Decimal`
   into `ScoringResult.outputs` for these types. A test pins a `decimal` output's served value and
   JSON type (a number) against the base's, green on the base and after.
8. **The decimal-output guard** (the maintainer's entry "2026-09-30 22:43:26 BST", item 2: "until
   it merges, **no committed algorithm outside tests may declare a `decimal` output**"). The ledger
   states that none of this slice's committed algorithms, seeds or examples declares one, with
   `git grep -n -E "type[\"']?[:=] *[\"']decimal[\"']" -- ':!**/tests/**' ':!docs/**' ':!frontend/**'`
   and its output, each hit classified. At the tree above it prints one line,
   `scripts/bench-rating.py:213`, an **input-contract** row, not an output.
9. **The release note** (`RL-1329` Acceptance 12, W2 condition 2; the FINAL dispatch record,
   condition 7). One paragraph in the **squash-commit body and in the ledger**, stating: declared
   non-payable rung outputs change on most quotes, as a correction of `FD-1336`'s drift, by up to
   about 10⁻⁴ of the value (57–64 % of quotes, maximum 12521 minor units at the 1e7 scale, across
   the four seeded sweeps at `fa9a73c2`; the maintainer's acceptance line in force, `RL-1329` §4);
   payables change only at a near-tie, by at most 1 minor unit (0 of 42 000); **and** a declared
   non-rung `money_minor` output on `/score` changes from a JSON number with a fraction to an
   integer, by less than one rounding unit (R2). **It does not mention `decimal` outputs**
   (`RL-1343` item 3).
10. **The gate, in a gate slot, with every evidence field** (the FINAL dispatch record, condition
    8; `PL-1342` Acceptance 11). For every suite-level run and the full gate, the ledger records:
    a clean checkout of the named SHA with `git status --porcelain` empty; `ruff check --no-cache`,
    and `mypy` on a fresh cache or with `--no-incremental`; **the dev-commands slot wrapper
    verbatim** (`.claude/skills/dev-commands/SKILL.md:122-171`) plus `LOKY_MAX_CPU_COUNT=4`, in the
    foreground with a `timeout`; `uptime` **and** `free -h` at start and end; the other slot's
    holder as gate or not-gate, via `flock -n`; wall and pytest time against the 1469.6 s solo
    baseline (step-down line about 2204 s). Only named single test files or node ids are exempt. The
    full two-half gate (`CLAUDE.md` §11) exits 0, with every rc, the `N passed` line and `HEAD`
    quoted against main's. After merging a `main` that adds a migration, `alembic upgrade head`
    runs on the per-worktree test database first. Docs checks run on a clean detached checkout.
11. **Merge** (`PL-1342` Acceptance 12, `PL-1342:317-319`): "the maintainer's MERGE-ACK, naming the
    PR's full head SHA, recorded in the lead's channel file, never posted on the PR; and the slice's
    clean audit filed." **At the merge**, the lead records, dated, that the `FD-1336` hold on the
    WK-673 and WK-675 rung-reader slices lifts (the FINAL dispatch record, condition 6), and that
    `FD-1336` and `FD-1330` are discharged by the merge (their "Event that discharges it"). The
    WK-1178 slice that delivers `RL-1343` is then the next on the first free lane (the 22:43:26 BST
    entry, item 1; `RL-1343` §5).

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path — never float** (`CLAUDE.md`
  §7). The reconciliation compares integers at the payable and the displays (R2, R4) and exact
  decimals on the chain (R1, R3); every value crossing the binding for ladder or payable
  arithmetic is the engine's `string()`, never the float (FR-273's string limb) (`RL-1329`'s
  restatement of `PL-1342`'s line).
- **`pricing-core` gains no FastAPI, SQLAlchemy or Redis import** (`CLAUDE.md` §2).
  `rating/ladder.py` imports only `model_schema` (`RL-1329` §2 step 5, S2).
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2): the ladder shapes
  are declared once, in `model_schema/scoring.py`, and the hand-authored `scoring.schema.json` is
  held to them by the contract guard.
- **No golden fixture and no stored suite version is edited** (`RL-1329` §4). The only fixture
  edit this slice may make is Acceptance 6's two `valid_algorithm` fixtures, by the maintainer's
  item 5.
- **Frozen records are not edited**: nothing already on `main` in `docs/plans/`, `docs/rulings/`
  or `docs/findings/`, and above all `PL-1342` (`document-ids.md` §1.5).
- **Build ahead of the phase is forbidden** (`CLAUDE.md` §9): no alert routing (WK-688, the DP-S3-1
  ruling §5), no Environment-setting layer, no rate limit (the environment half, `SL-1257`).

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.4 | FR-240 | `RL-1329`'s dated clause: a clamp the ladder cannot place is refused at save and at compile, `LADDER_CLAMP_UNPLACEABLE` (Acceptance 6) |
| `03` §3.6 | FR-247 | The `constraints` rung records a binding clamp as `clamp` (`FD-1330`; Acceptance 3 (f) item 10, (g)) |
| `03` §3.6 | FR-248 | As amended by `RL-1329` (Acceptance 3); on every scored quote, never sampled (Acceptance 1, 4); a failure refused (Acceptance 5) |
| `03` §3.8 | FR-261 | The "ladder reconciles" property takes the scoring-time verdict with its independent inputs (Acceptance 4, 5 item 7) |
| `03` §3.11 | FR-273 | The string limb: ladder, payable and declared `money_minor` outputs read through `string()` (`FD-1336` limb 3; Acceptance 3 (e), (f) item 4; Acceptance 7) |
| `03` §9 | NFR-496 | The prod-sampling limb decoupled (every quote, every Environment) with a dated clause (Acceptance 1, 4); the NFR-496 test's `round` weakness, `FD-1336` F4 (Acceptance 3 (f) item 7) |

**Carried obligations placed here:** `RL-1329` in full, with D1 and D2; `FD-1336` limbs 1–3 and F4,
with the NFR-496 prod-sampling limb; `FD-1330`; R2; the release note; the OQ-1316 note; the DP-S3-1
ruling; `RL-1343`'s "dispatch record must carry" items 2 and 3; the decimal-output guard.

**Not in this slice** (they stay on `SL-1257`, `PL-1342`): FR-430, FR-431, FR-446, FR-447 and
NFR-499; `PL-1342` Acceptance 1's `07` edits, and Acceptance 2–9 (the settings source, the
migration, one key per Environment, the Environment-setting layer, Environment-only keys, the
override startup check, the rate limit, the monitoring limb). `SL-1257`'s later dispatch record
states which of `PL-1342`'s acceptance items this slice delivered (the 23:57:25 BST entry, item 2);
the Hand-off lists them.

### Decision points

Each is assigned to the half that needs it.

The maintainer's entry item 1: "**The planner assigns DP-S3-1 and DP-S3-2 to whichever half needs
them;** any the ladder slice depends on must be minted before its activation."

| DP | Question (source) | Half | Why | State |
|---|---|---|---|---|
| DP-S3-1 | What does a failed ladder reconciliation do at scoring? (`PL-1342:405`) | **This slice** | It decides the failure of `RL-1329`'s predicate, which only this slice builds; `RL-1329` defers to it three times ("What a failure does is DP-S3-1's", `:378`, `:452`, `:699`) | Ruled (a), refuse: `RL-1346` (from working id 9983, PR #1026, read at `2b98b5aa`), minted in batch 13a. Activation need 3 checks it on `main` |
| DP-S3-2 | The rate-limit counter's key and limit (`PL-1342:406`) | **`SL-1257`** (environment half) | It governs NFR-499's per-client rate limit and FR-430's per-Environment limits; nothing in this slice reads it. Its ruling's write-set additions (`auth/service.py`, `api/deps.py`, the `metrics.py` rate-limit counter, the `main.py` lifespan Redis client; the S3 dispatch record's Deltas 2 and 3) are the environment half's | Ruled: `RL-1347` (from working id 9984, PR #1024), minted in batch 13a. Not this slice's activation need |
| DP-S3-3 | FR-430's monitoring configuration (`PL-1342:407`) | `SL-1257` | The monitoring limb is the environment half's | Resolved (a), by the maintainer as scope |
| DP-S3-5 | How does the ladder record each rung? (D1's row) | This slice | The builder | Resolved: `RL-1329` |
| DP-S3-6 | The stop bound on a rung that is `none` in the baseline (D1's row) | This slice | Acceptance 3 (a) | Resolved: delta D2, the maintainer's entry "2026-09-30 22:45:30 BST" |

### Premises re-derived at the tree above (`248dbf11`)

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | The check is vacuous at its call site | `pricing_core/money.py:55` (`reconcile_ladder(risk_premium_minor: int, steps: list[tuple[str, int]])`); `rating/score.py:769` calls it; `properties.py:303` | reproduces `FD-1336` limb 1 |
| b | `LADDER_RECONCILIATION_FAILED` is registered and raised nowhere | `backend/src/app/errors.py:339`, inside `RATING_ERROR_CODES` (`:297`) | the DP-S3-1 ruling adds the raise site |
| c | The builder reads floats and quantises factors | `score.py:566` (`_round_minor(raw: float, …)`), `:582` (`_build_ladder`), `:657` (`_build_outputs`) | reproduces limbs 2 and 3 |
| d | The re-derivation test assigns the `round` rung | `test_rating_score.py:224-225` (`elif op.kind == "round": value = rung.value_minor`) | reproduces F4 |
| e | The clamp test fixes the misattribution | `test_rating_score.py:262` | replaced (Acceptance 3 (f) item 10) |
| f | `ALGORITHM_CHECKS` exists and `validate_algorithm` runs it | `compile.py:247-250` (`_check_result_types`, `_check_input_bound_scale`), `:277` | `RL-1329`'s ordering condition met |
| g | The two `valid_algorithm` fixtures clamp the payable's source | `test_rating_compile.py:15-60`, `test_rating_algorithms.py:17-60` (`s_minprem`, payable reads `office_premium_minor`) | Acceptance 6 |
| h | The docstrings that claim sampling or construction | `money.py:63`; `score.py:62-103` ("by construction", `:102`; "shallow", `:103`) | corrected (Acceptance 4) |
| i | The spec rows | FR-248 `03:155` ("asserted at scoring time in `dev`/`uat` and sampled in `prod`"), NFR-496 `03:1165` ("asserted continuously in non-prod and sampled in prod"), OQ-1316 `03:1194` and `open-questions.md:138` | Acceptance 1 |
| j | The trace-sampling key exists | `backend/src/app/platform/settings.py:196` (`rating.trace_sample_rate`) | the rate-0 cases need no new key |
| k | The route's per-quote mapping | `backend/src/app/api/score.py:93` (`_PER_QUOTE_CODES`), `:255` (`_as_platform_error`), `:319` (`_maybe_sample_trace`), `:324` (`_naming_side`) | the DP-S3-1 ruling's 500 mapping |
| l | No decimal output outside tests | Acceptance 8's grep: one input-contract hit | the guard holds |

The executor re-reads each at its own base (after WK-690 S2 or WK-1250 S1 may have merged) and
stops on any that no longer holds.

### Write set, and its contention (`RL-1263`)

The salvage branch's paths (`git diff --stat origin/main...origin/sl-1257-ladder-exact`, read
2026-10-01, merge base `36b2a121`), plus the DP-S3-1 ruling's, plus Task 1's:

| Path | This slice | Existing definitions edited |
|---|---|---|
| `docs/specs/03-rating-engine.md` §3.6 (FR-248), §9 (NFR-496), §4.4 (example), §4.5 (note), §10 (OQ-1316 row) | Acceptance 1, 2, 4 | those rows and the example |
| `docs/open-questions.md` (OQ-1316 row) | the note | one row |
| `packages/model-schema/src/model_schema/money.py` | `PositionalDecimalStr` added | none |
| `packages/model-schema/src/model_schema/scoring.py` | `LadderOperationKind`, `LadderOperation`, `LadderRung`, `Trace.ladder_check_version` | those four |
| `docs/contracts/schemas/scoring.schema.json` (hand-authored) | the same fields; the invariant text | the ladder definitions |
| `docs/contracts/` generated outputs, `docs/INDEX.md` | regenerated | registry-exempt (`RL-1263:104-116`) |
| `packages/pricing-core/src/pricing_core/money.py` | `reconcile_ladder` (R0–R4) and its docstring | `reconcile_ladder` |
| `packages/pricing-core/src/pricing_core/__init__.py` | the export | `__all__` |
| `packages/pricing-core/src/pricing_core/rating/ladder.py` | **new**: the rung mapping | — |
| `packages/pricing-core/src/pricing_core/rating/score.py` | the builder, `_build_outputs`, `build_scoring_result`'s raise, the docstrings | those |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `to_wire`'s `string()` read; `_constraint_node`'s `__before`, `__min`, `__max` | those two |
| `packages/pricing-core/src/pricing_core/rating/properties.py` | the FR-261 property | its `LadderReconciles` evaluation |
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `_check_clamp_placement` appended; one `ALGORITHM_CHECKS` entry; imports | the tuple and the import block (Task 5) |
| `backend/src/app/errors.py` | `LADDER_CLAMP_UNPLACEABLE` appended to `RATING_ERROR_CODES` | that frozenset |
| `backend/src/app/api/score.py` | the explicit 500 mapping on `/score` and `/score/compare`, the `ERROR` log line, the OpenAPI `responses`, `_PER_QUOTE_CODES`'s comment | those |
| `backend/src/app/observability/metrics.py` | `gip_ladder_reconciliation_failed_total` | none (an addition) |
| tests: `packages/model-schema/tests/test_money.py`, `test_scoring_ladder.py`; `packages/pricing-core/tests/test_rating_score.py`, `test_testing.py`, `test_rating_ladder_exact.py` (new), `test_rating_ladder_sweep.py` (new), `baseline_ladder.py` (new), `test_quote_input_raise_sites.py`; `test_rating_compile.py` and `backend/tests/test_rating_algorithms.py` (the `valid_algorithm` fixtures, and appended tests); backend route, batch and property tests; `backend/tests/test_contracts.py` only if the guard needs a comparison | as named | `test_rating_score.py`'s two tests; the two `valid_algorithm` fixtures |

**Against WK-690 Slice 2** (`PL-1327:90-127`; lane A, PR #1025): it writes `pricing_core/modelling/`,
`model_schema/objectives.py`, `model_schema/__init__.py`, the hand-authored
`objective-certificate.schema.json`, `scripts/bench-model.py`, `02`, and
`backend/tests/test_contracts.py` "if the guard needs a new comparison". **Possible shared file:
`backend/tests/test_contracts.py`**, only if both add a comparison: each appends its own function,
no existing function is edited by both, and the second to merge re-gates. `model_schema/__init__.py`
is shared only if this slice exports a new name; the salvage does not edit it, and **if the executor
adds an export, that row serialises**. **The two timing measurements never share a window**
(`RL-1263` item 3): this slice's `bench-rating.py` run and WK-690 S2's Task 6 NFR-476 run.

**Against WK-1250 Slice 1** (`PL-1325:141-188`; lane B, dispatching now). It edits `compile.py`'s
`_producer_types` and `_check_result_types` (kept registered in `ALGORITHM_CHECKS`) and its
`__all__`; it appends tests to `test_rating_compile.py` and `backend/tests/test_rating_algorithms.py`;
it edits `03` §2, a new §4 subsection and §5.1; and its set excludes "`compile_bundle`, `score.py`,
`TraceStep`, `runtime.py`, any `approvals.py`, `errors.py`" (`PL-1325:186-187`). So:
- **`compile.py`**: shared. This slice appends one function and edits the `ALGORITHM_CHECKS` tuple
  and the import block. **Serialised by the maintainer's order** (Build-start conditions): Task 5
  starts after WK-1250 Slice 1 merges, unless the dispatch record shows both diffs append-only on
  `ALGORITHM_CHECKS` with no existing line edited by both.
- **`test_rating_compile.py`, `backend/tests/test_rating_algorithms.py`**: this slice edits the
  existing `valid_algorithm` fixture in each; WK-1250 Slice 1 appends tests, which may call
  `valid_algorithm`. No definition is edited by both, but the fixture edit changes what those tests
  receive. Task 5 runs after WK-1250 Slice 1 merges, so its appended tests are in this slice's gate;
  under the append-only exception, the second to merge re-gates.
- **`03`**: sections are disjoint (this slice: FR-248's row, NFR-496's row, §4.4, §4.5's note, §10's
  OQ-1316 row; WK-1250 Slice 1: §2, a new §4 subsection, §5.1). §4.4 and §4.5 are existing
  subsections inside §4, where WK-1250 Slice 1 adds a new one, so that pair is checked on the actual
  diffs at dispatch. This slice does not edit §5.1 (`RL-1329`'s code and the DP-S3-1 ruling's §5.1
  entry land in those rulings' own commits).
- `model_schema/__init__.py`, as above.

**`SL-1340` (WK-1250 Slice 2, draft) also edits `compile.py`**; its dispatch record re-checks
`compile.py` and `ALGORITHM_CHECKS` against this slice (the WK-674 S3 dispatch record, condition 3,
names WK-1250 Slice 1 and Slice 2 as editing `compile.py`).

**Against the environment half (`SL-1257`)**: not concurrent (it waits on WK-674 Slice 2). Its
later dispatch record re-checks `backend/src/app/api/score.py` and `observability/metrics.py`,
which both halves edit (the DP-S3-1 ruling here; the DP-S3-2 ruling there).

---

## Tasks

### Task 0: Preconditions, and the start from the salvage branch

**Files:**
- Create: the slice ledger `docs/ledgers/LG-<working id>-….md`, the id allocated by the lead at
  dispatch (`FD-1338`; LG 9981 records the halt and is **not** this slice's).

- [ ] `pwd` is the executor's worktree; `git -C "$PWD" branch --show-current` is the slice branch,
  created from `origin/main`; `uv sync --all-packages`. Never `cd`.
- [ ] Quote the dispatch record in the ledger's Task 0, including each activation need's command and
  output, and D1's `+` lines in full.
- [ ] Re-derive premises a–l at the base; quote each. Stop on any that no longer holds.
- [ ] `gh pr list --state open`; read anything ruling on the ladder, `compile.py`, `ALGORITHM_CHECKS`,
  `score.py` or the served outputs; name the SHA read. Run the write-set check against the slices in
  flight.
- [ ] **Take the salvage work.** The four code commits, in order, each onto the slice branch:
  `2fd447f8` (the contract), `12a728b8` (the builder and predicate), `14a1701a` (the acceptance
  tests), `ceb23a00` (the placement refusal, **Task 5's; held while the `compile.py` order
  applies**). The two ledger commits (`c019bc6a`, `caf07f71`) and every hunk under `docs/ledgers/`
  are **not** taken. For each commit:
  ```bash
  git cherry-pick -n <sha>
  git rm -q -f --ignore-unmatch -- 'docs/ledgers/LG-09981-*'
  git diff --cached --stat
  git commit -m "$(git log -1 --format=%B <sha>)" -m "(from salvage <sha>)"
  ```
  Only `ceb23a00` touches `docs/ledgers/` among the four; on the slice branch the halt's ledger file (working id 9981) does
  not exist, so its hunk arrives as a modify/delete conflict, and the `git rm` line resolves it by
  leaving the file out. `git diff --cached --name-only` then lists no `docs/ledgers/` path.
  Where a pick conflicts because `main` moved, the resolution is recorded in the ledger by file.
- [ ] **Verify the start** (the maintainer's item 6: "re-gated from a clean checkout"). For the code
  paths `S` of the four commits (every path in `git diff --name-only 36b2a121 ceb23a00` except
  `docs/ledgers/`, `docs/INDEX.md` and `docs/contracts/schemas/generated/`), the patch-ids agree:
  ```bash
  git diff 36b2a121662b9d69a309fee0e8023fbfff3a71ea ceb23a001ccfa02ab37065dff65e303e5180d533 -- $S | git patch-id --stable
  git diff <the slice base> HEAD -- $S | git patch-id --stable
  ```
  Equal ids mean the taken work is the salvage work. Unequal ids are expected only where a
  conflict was resolved; the ledger names each file that differs and why. **When `ceb23a00` is
  held** (the `compile.py` order), take the first three commits, and derive `S` and the first
  `git diff` to `14a1701a` (`git diff --name-only 36b2a121 14a1701a`, the same exclusions, and
  `git diff 36b2a121 14a1701a -- $S`), excluding the `ceb23a00` hunk. Verify again at Task 5,
  with `S` running through `ceb23a00`. Then regenerate the
  generated contracts and `docs/INDEX.md` (`generate-contracts.py`, `doc-index.py`), never
  hand-merged.
- [ ] **Show each salvage test red on the base** (the Acceptance Standard's rule for taken tests):
  in a detached checkout of the base, apply the test files only
  (`git diff <base> HEAD -- '*/tests/*' | git apply`), run each named test file, and quote the
  failures with their causes. A file that fails at import on the base (a name the slice adds) is
  quoted once, with the missing name, which is its predicted cause. A test that passes on the base
  is not red first; it is a control, and the ledger says which.

### Task 1: Spec — FR-248 and NFR-496 "never sampled", and the OQ-1316 note

**Files:** Modify `docs/specs/03-rating-engine.md` (`:155`, `:1165`, `:1194`),
`docs/open-questions.md` (`:138`).

- [ ] Through `spec-change`: FR-248's and NFR-496's dated clauses (Acceptance 1, quoted text),
  citing the maintainer's entry headed `2026-09-30 15:17:54 BST — audit round-up: decisions`; do
  not reword `RL-1329`'s clauses.
- [ ] The OQ-1316 note, the FINAL dispatch record's text verbatim, appended to the question cell of
  each mirror row; the row's status unchanged.
- [ ] Run `python3 scripts/audit-docs.py` (exit 0), and the two `grep -c -F` commands (`1` each).
  Commit: `docs(specs): FR-248 and NFR-496 never sampled; OQ-1316 cross-reference to RL-1329 R0 (SL-1345)`.

### Task 2: The contract (salvage `2fd447f8`)

**Interfaces:**
- Produces: `model_schema.money.PositionalDecimalStr`; `LadderOperationKind` with `multiply`,
  `divide`, `add`, `clamp`, `round`, `none`; `LadderOperation` fields `factor`, `divisor`,
  `amount_unrounded_minor`, `bound`, `bound_unrounded_minor`, `applied`, `mode`, `dp`, legacy
  `amount_minor`; `LadderRung` fields `unrounded_minor`, `rounding`; `Trace.ladder_check_version`.

- [ ] Red first (quoted from Task 0): `packages/model-schema/tests/test_money.py`'s
  `PositionalDecimalStr` cases (predicted cause: no such name, then `"1E-7"` from `DecimalStr`);
  `test_scoring_ladder.py`'s shape cases; a stored pre-ruling ladder still validates.
- [ ] Confirm the picked commit carries `03` §4.4's example replaced and `ladder_check_version`
  (`git grep -n ladder_check_version -- packages/model-schema docs/contracts/schemas/scoring.schema.json`
  prints the model field and the schema property). The dated `03` §4.5 note on
  `ladder_check_version` (Acceptance 4) is added here if the salvage lacks it.
- [ ] `uv run python scripts/generate-contracts.py --check` exits 0; the contract guard
  (`uv run pytest backend/tests/test_contracts.py -q`) passes, quoted. Commit (the picked commit,
  amended only by the §4.5 note if added).

### Task 3: The builder, the reads, the predicate and the served outputs (salvage `12a728b8`, `14a1701a`)

**Interfaces:**
- Produces: `pricing_core.rating.ladder` (`RUNG_ORDER`, `output_steps_by_name`,
  `rung_output_name`, as the salvage names them); `reconcile_ladder` with `RL-1329` §5's inputs (its
  Python signature is the slice's to choose, `RL-1329` §5); `_build_outputs` per `RL-1329` §4.

- [ ] Red first (quoted from Task 0): Acceptance 3 (e), (f) items 1, 3, 4, 6, 7, 10 (the clamp half)
  and 11; Acceptance 4's call-site, property and rate-0 cases; Acceptance 7 (R2 and the `RL-1343`
  control). The ledger maps each to its test node id.
- [ ] **Acceptance 3 (e)'s clamped case, red on a planted mutation**: replace `_build_outputs`'s
  served value with the rung's `value_minor`, run the test, quote the red (1436 against 5000),
  restore, quote the green.
- [ ] **Acceptance 7, if the salvage lacks it**: add the near-tie `fee_minor` test and the `decimal`
  control. Predicted red on the base: `1234.5` is a `float`. The `decimal` control is green on the
  base and after; with `_build_outputs` changed to serve the `string()` read for a `decimal`
  output, it is red (a JSON string), then restored.
- [ ] Every caller of `reconcile_ladder`: `score.py`, `properties.py`, `pricing_core/__init__.py`;
  the docstrings of premise h and `model_schema/scoring.py`'s `LadderOperation` and module
  docstrings. `git grep -n -E 'sampled in prod|by construction|shallow' -- packages/pricing-core/src`
  prints nothing that describes the ladder check.
- [ ] Named test files green (exempt from the slot): `test_rating_score.py`,
  `test_rating_ladder_exact.py`, `test_testing.py`. Commit.

### Task 4: A ladder that does not reconcile is refused (the DP-S3-1 ruling)

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/score.py` (`build_scoring_result`),
`backend/src/app/api/score.py`, `backend/src/app/observability/metrics.py`,
`packages/pricing-core/tests/test_quote_input_raise_sites.py`; tests beside the route, batch and
property tests they mirror (mirror the neighbouring test; do not reinvent the module's fixtures).

**Interfaces:**
- Produces: one raise site, `_raise_named("LADDER_RECONCILIATION_FAILED", …)` in
  `build_scoring_result`, after the verdict and before any `Trace` or `ScoringResult` is built;
  message `LADDER_RECONCILIATION_FAILED: <clause>: <rungs>: <difference>` with no quote input;
  `gip_ladder_reconciliation_failed_total{environment}`.

- [ ] Red first: Acceptance 5 items 1–6 and 8 on Task 3's head, where the verdict is computed but
  nothing is refused. Predicted causes: item 1, a result is returned; item 2, the quote is served;
  items 3 and 4, status 200; item 5, status 200; item 6, two scored rows; item 8, the census does
  not list the new site. **Item 7 is red first on the slice base**, not on Task 3's head: on the
  base the vacuous check lets the property hold; on Task 3's head the real predicate already fails
  it. Its red run is quoted from Task 0.
- [ ] Implement the ruling's §2–§5 as written: `reconcile_ladder` stays a bool predicate; the
  backend maps the code to 500 explicitly, beside `_as_platform_error`'s case, not through
  `_PER_QUOTE_CODES`; `/score/compare` names the side through `_naming_side`; one `ERROR` log line
  on `/score` only; the counter on `/score` only; the OpenAPI `responses` gain 500 on both routes;
  regenerate the contract.
- [ ] Green, and Acceptance 5 item 9's controls. Commit.

### Task 5: The placement refusal and the two fixtures (salvage `ceb23a00`)

**Starts only when the `compile.py` order allows it** (Build-start conditions). Quote the
`merge-base --is-ancestor` exit code, or the dispatch record's append-only finding, before the first
step.

- [ ] Take `ceb23a00` (Task 0's procedure, including its patch-id check with `S` running through
  `ceb23a00`) onto the current branch, after merging `main` in if
  WK-1250 Slice 1 has landed. Re-read `compile.py`'s `ALGORITHM_CHECKS` and import block at that
  tree.
- [ ] Red first: the three `RL-1329` algorithms saved and compiled on the base (they are accepted);
  #967's closure test (ii) with the check unregistered.
- [ ] Green: the check registered; the three refused at save and by `compile_bundle`.
- [ ] **The fixture stop** (Acceptance 6): run `test_rating_compile.py` and
  `backend/tests/test_rating_algorithms.py`; quote the refused `valid_algorithm` failures (9
  `test_rating_compile.py` tests at the halt). Edit each `valid_algorithm` to a placeable clamp; list
  before and after in the ledger; add the kept-refused test of the old shape; show
  `git diff <pre-edit commit> HEAD -- packages/pricing-core/src/pricing_core/rating/compile.py`
  empty.
- [ ] The recount (Acceptance 6's two commands) with its output. Commit.

### Task 6: The sweep and the false-positive control (`RL-1329` Acceptance 2 and 8; D2)

- [ ] Acceptance 3 (f) item 2's sweep on this slice's builder, at least two recorded seeds, and the
  same sweep red over `origin/main`'s builder (`baseline_ladder.py`); quote both.
- [ ] The false-positive control over every scoring fixture and every committed Regression Suite's
  golden quotes, printing Acceptance 3 (a)–(d)'s counts and the disposition-disagreement count, and
  the count of refusals (Acceptance 5 item 9). The predicate for "every committed suite" is
  quoted in the ledger with its command and the list of suites it found.
- [ ] Red on broken input for (a). Any count above 0 stops the task: for (a) and (b) report to the
  maintainer, for the others to the lead. Commit.
- [ ] `scripts/bench-rating.py` before (on the base) and after, in a solo window the lead grants;
  quote both; no budget changed.

### Task 7: The gate, the ledger, the release note

- [ ] The decimal-output guard (Acceptance 8), quoted.
- [ ] The full two-half gate through the slot wrapper with every field of Acceptance 10; quote every
  rc, `N passed`, `HEAD` and main's.
- [ ] Docs checks on a clean detached checkout of the head: `python3 scripts/audit-docs.py`,
  `python3 scripts/doc-index.py --check`, `python3 scripts/doc-id.py check`, rcs quoted.
- [ ] The release-note paragraph (Acceptance 9) in the ledger, and drafted for the squash body.
- [ ] Open the PR; hand it to the auditor; Acceptance 11 at merge.

## Hand-off

- **To `SL-1257`'s later dispatch record** (the 23:57:25 BST entry, item 2): this slice delivers
  `PL-1342` Acceptance 1's FR-248 and NFR-496 clauses, Acceptance 10 in full (as `RL-1329`
  supersedes it in part, with DP-S3-1's refusal), and the dispatch record's D1 (Acceptance 13) and
  D2. `SL-1257` keeps Acceptance 1's `07` edits and Acceptance 2–9, with DP-S3-2 and DP-S3-3. If that
  makes `PL-1342` materially wrong, a planner files a superseding plan then.
- **To WK-1178:** the `RL-1343` slice follows this slice's merge on the first free lane, and
  serialises with it on `score.py` (`_build_outputs`).
- **To WK-673 and WK-675:** the `FD-1336` hold on rung-reader slices lifts at this merge (the lead's
  dated line).

## Self-review

- **Scope against the decision** (the 23:57:25 BST entry, item 1): `RL-1329` in full with D1 and D2
  (Acceptance 3); `FD-1336` all limbs plus NFR-496 (Acceptance 1, 3 (f) items 1–4 and 7, 4); `FD-1330`
  (3 (e), (f) item 10, (g)); R2 as an integer, red first (Acceptance 7); the release note
  (Acceptance 9); the OQ-1316 note on both mirrors (Acceptance 1). DP-S3-1 assigned here and made
  activation need 3; DP-S3-2 assigned to `SL-1257`.
- **The brief's premises checked at `248dbf11`:** one was wrong. The two refused fixtures are named
  `valid_algorithm`, not `_algorithm` (Acceptance 6). The OQ-1316 note has two wordings in the
  sources; the FINAL dispatch record's is used and the other named (Acceptance 1). NFR-496 is at
  `03:1165`, not `PL-1342`'s `:1157` (a different tree).
- **Rulings applied at every site class** (README convention 5): the DP-S3-1 ruling appears in the
  narrative, the DP table, activation need 3, Acceptance 4 and 5, the write set, and Task 4; `RL-1343`
  in the Spec list, Acceptance 7 and 9, and the Hand-off; the maintainer's item 5 in Acceptance 6,
  Global Constraints and Task 5; the `compile.py` order in Build-start, the write set and Task 5.
- **Frozen records:** `PL-1342`, `RL-1329`, `FD-1336`, `FD-1330`, `RL-1343` are quoted, not edited.
  The DP-S3-1 ruling was read as a draft at `2b98b5aa` and minted as `RL-1346`; its minted text governs.
- **Open:** none of this plan's own. `RL-1346` on `main` is activation need 3.
