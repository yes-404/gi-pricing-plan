---
id: LG-9981
family: ledger
title: WK-674 Slice 3 (SL-1257) — environment isolation, and the exact premium ladder (RL-1329)
status: active
created: 2026-09-30
owner: executor
tree: 36b2a121662b9d69a309fee0e8023fbfff3a71ea
phase: P2
work: WK-674
plans: [PL-1342]
corrected_by: []
relates: [RL-1329, RL-1311, RL-1343, RL-1344, FD-1336, FD-1330, OQ-1316, RL-1263]
---

# LG-9981 — WK-674 Slice 3 (SL-1257)

Executed from `PL-1342` under the dispatch record below. Branch `sl-1257-ladder-exact`, from
`origin/main` `36b2a121662b9d69a309fee0e8023fbfff3a71ea`, lane B, executor-674s3. The id is a
working id (the lead allocates every id); it is minted at the merge turn.

## Tasks

### Task 0 — preconditions

The dispatch record, quoted verbatim
(`~/gi-pricing-plan.local/handover/DISPATCH-WK-674-S3-2026-09-30.md`, outside the repository,
FINAL 23:32:11 BST, lane B grant 2026-09-30 23:33:40 BST).

````text
# Dispatch record — WK-674 Slice 3 (SL-1257), from PL-1342 (working id 9947) — FINAL

**Status: FINAL 2026-09-30 23:32:11 BST, DISPATCHED 2026-09-30 23:33:40 BST** (lane B GO by the lead). The maintainer checked this FINAL record and cleared GO (entry "2026-09-30 23:32:44 BST" in to-lead.md). Drafted 23:01:33 BST, with the maintainer's three additions, and finalised after mint batch 12 merged. The grant time is filled in at GO. The executor's ledger Task 0 quotes the FINAL record verbatim. Plans are frozen by family, a draft included (`document-ids.md` §1.5; RL-1329:34-35, :902-904). **This record is where the plan's changes live.** The plan is not edited.

- **Plan:** PL-1342 (minted in batch 12 from PL 9947 at 06e3e896; the body is byte-identical apart from id, H1 and the disclosure). `corrected_by: []`: the maintainer withdrew that condition, because check 34 needs the correcting record's `corrects:` and RL-1329 is frozen. Its mint disclosure names N5 (the ladder replay) as superseded by RL-1329, and points here.
- **Rulings:** RL-1329 (DP-S3-5, ruled **in full**); RL-1311 and the earlier S3 rulings the plan cites; RL-1343 (OQ-1334: decimal outputs; delivery after S3); RL-1344 (PL-1254 DP-2; not S3's, listed for the compile.py order).
- **Findings delivered:** FD-1336 (HIGH: reconcile_ladder vacuous, 4-dp drift; limbs 1–3 and F4); FD-1330 (the clamp attributed to `constraints`); the FR-447 limb the plan already carries.
- **Lane:** B, under RL-1263 (≤2 build slices, different Works). Lane A holds WK-690 S2 (GO 22:59:52 BST).

## Activation facts (filled in at GO)
1. Mint batch 12 merged: #1022 squash-merged 2026-09-30 23:30:04 BST, origin/main `36b2a121662b9d69a309fee0e8023fbfff3a71ea` (parent 71b67220, tree c436851f), on the maintainer's MERGE-ACK #1022. PL-1342, RL-1343 and RL-1344 are on main. RL-1343 on main meets S3's OQ-1334 merge gate.
2. RL-1329 is on main (#1013). SL-1315 (#967's code slice) merged at 3a5f7cd5, which meets RL-1329 E1's build order.
3. **Lane B grant: 2026-09-30 23:33:40 BST**, by the lead, at main 36b2a121, with this record's write-set check. Lane A: WK-690 S2's full gate is running (head 125a403b).

## Delta D1 — the RL-1329 alignment (the operative text; the maintainer's option (A), entry "2026-09-30 22:45:30 BST — PL 9947: option (A); DP-S3-6 decided…"; mint terms in "2026-09-30 22:47:48 BST")
The operative delta is the **added text of commit `5c17a4dc56c61693a5b2cdd0461e62c4954767d2`** (planner-9947). It was reverted from the plan and preserved verbatim at `~/gi-pricing-plan.local/handover/s3-delta-source/pl9947-delta-5c17a4dc.patch`: its `+` lines, 279 insertions. The ledger's Task 0 **quotes those lines in full**. Where D1 and RL-1329 differ, **RL-1329 wins**. planner-9947 found five such places, all accepted by the maintainer (`s3-delta-source/planner-9947-report.md`):
1. The directed-mode clause is conditional: "If S3's golden set contains a directed-mode rung…".
2. The clamped served-output case already passes on origin/main, so it is shown red **against a planted `_build_outputs` mutation**. Record the mutation and its red run in the ledger. The unclamped case is red on main (office 67358 vs 67357; FD-1336's instalment case 69402 vs 69399).
3. The stop predicate is stated for `multiply` rungs. D2 covers `none` rungs.
4. Any exceedance of the exact bound is reported to the maintainer and stops the slice, "with no looser fallback".
5. RL-1329's unquantised "×1.1" governs over FD-1330's "1.1000".

**S3's acceptance is RL-1329 IN FULL** (the maintainer's entry "2026-09-30 22:22:45 BST — the new lead's read-back is ACCEPTED, with one addition to (c)…"). D1's Acceptance 13 lists it item by item, including:
- the exact stop predicate |base_i−new_i| > 5e-5·|base_{i−1}| + (e_apply+e_ruled) for `multiply` rungs; for add, round and the first rung, > e_apply+e_ruled; clamp exact; Decimal and integers only;
- a report to the maintainer before continuing if any golden rung's 5e-5·|base_{i−1}|/|new_i| > 2e-4;
- the golden payable stop;
- directed-mode tightness recorded on the first run (conditional, as in 1 above);
- post-clamp served outputs, exact and rounded once, red first for BOTH cases (as in 2 above).
- **NFR-496, by name:** F4 is "the NFR-496 test's round weakness, fixed here, red first" (FD-1336 F4).
- **R2, its own acceptance line:** a non-rung declared `money_minor` output is served exact, rounded once with its output step's RoundSpec, **as an integer** (it was a float), red first. It changes a JSON type, so it is named in the release-note line (condition 7).

## Delta D2 — DP-S3-6, decided by the maintainer (entry "2026-09-30 22:45:30 BST"; read it verbatim)
A baseline `none` rung stops if **|base_i − new_i| > e_apply + e_ruled**. There is no 5e-5 term: on main, `score.py:640-648`, a rung is `none` only when it isn't `multiply` and round(raw) == prev, so the difference is only the two roundings. Decimal and integers only. Any exceedance stops the slice and is reported, with no fallback. If the decision-maker sees a flaw, it says so before this GO.

## Conditions
1. **Write set:** PL-1342's own write set, plus D1's write-set table (RL-1329's paths), plus:
   - `compile.py`: the LADDER_CLAMP_UNPLACEABLE compile-time refusal of an unplaceable clamp in `compile_bundle` (FR-240's dated clause), and `_check_clamp_placement` appended to `ALGORITHM_CHECKS` (`compile.py:247` at 8cef871d);
   - `backend/src/app/errors.py`: the new code;
   - the new `pricing_core/rating/ladder.py`, with score.py's mapping moved into it;
   - **the OQ-1316 cross-reference note, byte-identical on BOTH mirrors** (`docs/open-questions.md:138` and `docs/specs/03-rating-engine.md:1194`, both re-verified by the lead at 36b2a121; Task 0 re-verifies them at the executor's base). The text:
     > *(Cross-reference added 2026-09-30, on the maintainer's instruction: if this question is decided (a), rounding recorded as its own rung, `RL-1329`'s R0 ("`round` appears only on the last rung") must be amended by that ruling; `RL-1329` says so itself.)*
     The source is the maintainer's entry "2026-09-30 19:06:06 BST — RL 9973: fold the OQ-1316 cross-reference into WK-674 S3…", with RL-1329:953-956. No record on main assigns it (planner-9947's premise 2); this record does.
2. **RL-1263 write-set check against lane A (WK-690 S2, PL-1327:90-127):**
   - **`backend/tests/test_contracts.py`**: shared only if both slices add a comparison. Both would be appends of new tests; no existing test is edited by both. The second to merge merges main in and re-runs its full gate.
   - **Generated `docs/contracts/` outputs and `docs/INDEX.md`**: registry-exempt (RL-1263:104-116). The later slice regenerates.
   - **No other shared path.** WK-690 S2 writes `modelling/`, `model_schema/objectives.py`, `__init__.py` re-exports, `02`, and `bench-model.py`; S3 writes `rating/`, `03`, and errors.py. `model_schema/__init__.py`: **S3 WILL add model-schema shapes** (the clamp kind plus `bound_unrounded_minor`; the positional decimal), so this case **applies** (the maintainer's check): append-only, no existing line edited by both, and the second to merge re-gates.
   - **The two timing measurements never share a window** (RL-1263 item 3): S3's `bench-rating.py` run (D1, Acceptance 13 (f) item 9) and WK-690 S2's Task 6 NFR-476 run. Each asks the lead for a solo window.
3. **Serialisation on compile.py and ALGORITHM_CHECKS:** #967's slice is merged (met). WK-1250 S1 (PL-1325) and S2 edit the same file, so they **do not run concurrently with S3**. WK-1250 S1 dispatches after S3 merges (the maintainer, 22:33:30 BST, Decision 4). errors.py is also shared with future RATING/GOVERNANCE code additions; there is no concurrent holder today.
4. **Merge gates:**
   - **S3 does not merge until OQ-1334 is ruled (a), or (d) is ruled as the interim** (roadmap row "Before WK-674 Slice 3 merges"). RL-1343 rules (a), so this is met once batch 12 is on main.
   - **S3 keeps non-rung decimal outputs unchanged** (RL-1343). Their JSON-string delivery is WK-1178's fix slice, which goes IMMEDIATELY after S3 merges.
5. **The decimal-output interim guard** (the maintainer's entry "2026-09-30 22:43:26 BST — RL 9974 … consequences; FD-1333 re-opened to MEDIUM"): until WK-1178's fix merges, **no committed non-test algorithm declares a `decimal` output**. S3 touches goldens and fixtures, so the executor states in the ledger that none of S3's committed algorithms, seeds or examples declares one, with the grep and its output.
6. **The FD-1336 hold release:** on S3's merge, the hold on WK-673/675 rung-reader slices lifts. The lead records the lift, dated (the maintainer's check of this draft, received by the lead by 23:03 BST per `date`).
7. **W2 condition 2:** the release-note line goes in **S3's squash body and the ledger** (the maintainer at the #1013 ACK). It covers RL-1329's visible rung-output change **and R2's JSON type change** (non-rung `money_minor` outputs: float → integer).
8. **Gate evidence, for EVERY suite-level run and the full gate.** Record in the ledger:
   - a clean checkout of the named SHA, with `git status --porcelain` empty;
   - `ruff check --no-cache`, and mypy on a fresh cache or with `--no-incremental`;
   - the dev-commands slot wrapper verbatim (`.claude/skills/dev-commands/SKILL.md:122-171`), plus `LOKY_MAX_CPU_COUNT=4`, in the foreground with a `timeout` (executor.md S-11: never relaunch at the 600s auto-background);
   - `uptime` AND `free -h` at start and end;
   - the other holder as gate or not-gate, via `flock -n`;
   - wall and pytest time against the 1469.6s solo baseline (step-down line ≈ 2204s).
   A concurrent gate pair with WK-690 S2 is an RL-1263 pair candidate. A missing field disqualifies it.
9. **After merging a main that adds a migration,** run `alembic upgrade head` on the per-worktree test DB first.
10. **Red first:** every acceptance item. FD-1336's reproductions are quoted as pre-fix evidence.
11. **Gate:** the full two-half gate before pushing. Docs checks run on a clean detached checkout.
12. **Ledger:** LG working id **9981**, reserved by the lead at 23:31 BST and checked free (the lead is the ONLY allocator, FD-1338). Ask for any other id. Task 0 quotes this FINAL record, including D1's lines in full.
13. **Frozen records:** nothing in `docs/plans/`, and no frozen record body, is edited.
14. **Executor:** a fresh `executor-674s3`, from `.claude/roles/executor.md` with its Model / effort line verbatim (sonnet, medium). Its worktree is new, from origin/main `36b2a121` or later. It never `cd`s.
15. **Lane A at the time of writing:** WK-690 S2's full gate is running (head 125a403b). S3's first suite-level run takes a gate slot only when one is free. Contention fields per condition 8.
````

Delta D1, the `+` lines of commit `5c17a4dc56c61693a5b2cdd0461e62c4954767d2` (279 insertions),
quoted in full from `~/gi-pricing-plan.local/handover/s3-delta-source/pl9947-delta-5c17a4dc.patch`.
Where D1 and `RL-1329` differ, `RL-1329` wins.

````text
+++ b/docs/plans/PL-09947-wk-674-slice-3-environment-isolation-leaf-plan.md
+relates: [PL-1237, PL-1306, PL-1303, RL-1184, RL-1301, RL-1232, RL-1236, RL-1263, RL-1311, RL-1329, FD-1336, FD-1330, OQ-1316, OQ-1334, PL-1325, PL-1327]
+- The second ruling this slice executes: **`RL-1329`** (DP-S3-5 decided; drafted under working
+  id 9963, minted in mint batch 9, #1013), and the three records it binds this slice to:
+  **`FD-1336`** (drafted as working id 9949: the vacuous check, the 4 dp drift, float money in
+  the builder; HIGH, owner this slice), **`FD-1330`** (drafted as working id 9967: the clamp
+  attributed to `office_premium`; MEDIUM, owner this slice) and **`OQ-1334`** (the merge gate,
+  below). Each is read at `origin/main` `8cef871d4ec30869dc3ef20559f3cac64e239a5c`; the section
+  *RL-1329 alignment* below carries every citation made at that tree. `03` FR-240 (`03:137`),
+  FR-247 (`03:154`), FR-273 (`03:222`) and §4.4 (`03:414`) are read there too.
+3. **DP-S3-1 and DP-S3-2 below resolved** (DP-S3-3 and DP-S3-5 are resolved).
+**Merge needs, beyond Acceptance 12** (a merge gate, not an activation need):
+- **S3 does not merge until OQ-1334 is ruled (a), or (d) is ruled as the interim.** Source:
+  `docs/roadmap.md`'s gate row "Before WK-674 Slice 3 merges" (`roadmap.md:1561` at
+  `8cef871d`) and its dated note (`:1570`): "Slice 3's dispatch record carries that Slice 3 does
+  not merge until OQ-1334 is ruled (a), or (d) is ruled as the interim." The row gates the
+  merge, not the start: declared `decimal` outputs are out of this slice's scope (`RL-1329` §4).
+
+   **`RL-1329`'s spec work** (verified at `8cef871d`): its own commits already added FR-240's
+   dated clause (`03:137`), FR-248's dated clause (`03:155`), `LADDER_CLAMP_UNPLACEABLE` to §5.1's
+   owned codes (`03:783`) and §4.4's dated note; the executor verifies each and does not reword
+   it. This slice adds, in its spec commit:
+   - **§4.4's example replaced** (`03:414`), in the same commit as the contract change of
+     Task 6, "as the dated note added there" by `RL-1329` says — so this edit moves to Task 6's
+     contract commit, not Task 1's;
+   - **the OQ-1316 cross-reference note, byte-identical on both mirrors**: appended to the
+     question cell of OQ-1316's row in `docs/open-questions.md` (`:138` at `8cef871d`) and to its
+     row in `03` §10 (`03:1194` at `8cef871d`; the lead's brief said `~:1190`, re-verified), the
+     text exactly:
+     `*Cross-reference (added YYYY-MM-DD by WK-674 Slice 3, RL-1329): if this question is decided (a), an intermediate rounding recorded as its own ladder rung, RL-1329 §5 R0's "round appears only on the last rung" must be amended by that ruling.*`
+     with `YYYY-MM-DD` the commit's date. Its content is `RL-1329`'s observation (`:953-956`
+     at `8cef871d`, "This ruling interacts with OQ-1316"); the note carries it to the question
+     it bears on. The row's status stays open. Command: `python3 scripts/audit-docs.py` exits
+     0, and `grep -c -F "<the note, verbatim>" docs/open-questions.md
+     docs/specs/03-rating-engine.md` prints `1` for each file.
+    > *Superseded in part, 2026-09-30, by `RL-1329` ("What this record supersedes in the S3
+    > plan", read at `8cef871d`).* Four sub-bullets below — **the signature changes**, **the
+    > risk premium's source and check**, **the four operation kinds** and **the comparison** —
+    > are replaced by `RL-1329` §5 (*Inputs*, R0–R4) and §3 (six kinds), and are marked
+    > *superseded* where they stand. The **never sampled** sub-bullet's conclusion stands; its
+    > rationale "it is integer arithmetic over a handful of rungs" becomes "exact decimal
+    > arithmetic, in a context of at least 100 digits, over a handful of rungs". Everything
+    > else in this item stands, as `RL-1329` says: the corrected premise; the false-positive
+    > control (extended by item 13's stop counts); the call-site red case with `trace=True` and
+    > the untraced failure's signal; the property red case; the raise-site census (the message
+    > carries rung names and the difference, now a decimal string in minor units); and
+    > `ladder_check_version`, whose value `2` means `RL-1329`'s predicate over `RL-1329`'s
+    > shape (`RL-1329` §3). Item 13 is the acceptance for the superseded parts.
+    - *(Superseded by `RL-1329` §5 Inputs — see the note above.)* **The signature changes** (auditor-close1255 M1). `reconcile_ladder` receives the
+      - *(Superseded by `RL-1329` §5 R1 and R2.)* **the risk premium's source and check.** The first rung carries **no** recorded
+      - *(Superseded by `RL-1329` §3 and §5 R3–R4: six kinds, replayed on unrounded values.)* **the four operation kinds** (`LadderOperationKind`,
+      - *(Superseded by `RL-1329` §5 R2–R4.)* **the comparison:** every replayed value equals that rung's recorded `value_minor`,
+      it is ~~integer arithmetic~~ exact decimal arithmetic, in a context of at least 100
+      digits, over a handful of rungs (`RL-1329`'s restated rationale) — and `rating.trace_sample_rate` governs
+13. **`RL-1329` in full** — S3's acceptance, by the maintainer's decision relayed by the lead on
+    2026-09-30 (~22:3x BST). **Every item of `RL-1329`'s section "Acceptance — the violation that
+    must become detectable" (items 1–13) is an acceptance item of this slice, red first on
+    `origin/main`** as that section requires ("S3 carries each item red first, shown failing on
+    `origin/main`"), each in a named test the ledger quotes with its failing assert line. The
+    record's text is the authority; the clauses below restate the ones that carry a number or a
+    stop, **quoted from `RL-1329` at `8cef871d`**, and where this restatement and the record
+    differ, the record wins.
+    - **(a) The golden-rung stop predicate** (`RL-1329` Acceptance 8, second count, "ruled on the
+      third re-audit, R1 … the **exact** form below is in force", as amended at the mint on the
+      maintainer's entry "2026-09-30 17:14:16 BST"). For rung `i` of a golden quote, `new_i` is
+      this slice's ruled value and `base_i` the baseline value; "the baseline is `origin/main`'s
+      builder run on the same golden contexts at S3's base tree". **The slice stops if:**
+      - on a `multiply` rung: **`|base_i − new_i| > 5 × 10⁻⁵ · |base_{i−1}| + (e_apply + e_ruled)`**
+        minor units, where `base_{i−1}` is the previous rung in the baseline ladder;
+      - on an `add` or a `round` rung, and on the first rung: **`|base_i − new_i| > e_apply +
+        e_ruled`**, where on the first rung `e_apply` is the error of today's single rounding;
+      - on a `constraints` rung where a clamp binds: **`new_i` is not exactly the bound**.
+
+      `e` is "0.5 for a `half_*` mode, and 1 for `ceiling`, `floor` and `down`"; `e_apply` is that
+      of the rounding today's builder applied (the step's mode passed to `apply_factor`, or to
+      `_round_minor`), `e_ruled` that of the rung's declared `RoundSpec`. **"The comparison is
+      evaluated in integers and `Decimal`, never in float."** The rung kind is the **baseline**
+      ladder's recorded kind, because the bound is derived from the baseline's own mechanism
+      (`RL-1329`: "Today's rung is `apply_factor(base_{i−1}, q_i)`"). **Any exceedance is
+      reported to the maintainer, "with no looser fallback"**, and the slice stops. Command: the
+      false-positive control's test (Task 6), which prints the exceedance count and the maximum
+      tightness `(|diff| − (e_apply + e_ruled)) / (5 × 10⁻⁵ · |base_{i−1}|)` per rung kind, and
+      exits non-zero on any exceedance. **Red on broken input:** with one baseline rung of one
+      golden quote shifted to its bound + 1 minor unit, the test is shown red naming that rung.
+    - **(b) The report line.** "if [`5 × 10⁻⁵ · |base_{i−1}| / |new_i|`] exceeds 2 × 10⁻⁴ on a
+      golden quote (a factor below about 0.25), S3 reports it to the maintainer before it
+      continues." The same test prints this ratio's maximum and the count above 2 × 10⁻⁴; a
+      count above 0 halts the task until the maintainer's reply is quoted in the ledger.
+    - **(c) The golden payable stop** (`RL-1329` Acceptance 8, first count, and §4): "golden
+      quotes whose payable changes" — **a count above 0 stops the slice**, reported to the lead.
+      The executor never edits a fixture and never edits a stored suite version; a re-baseline,
+      if the lead routes one, is a **new** suite version whose `change_note` cites `RL-1329`, and
+      "any golden re-baseline is dated and needs the maintainer's ACK".
+    - **(d) Directed-mode tightness** (the 17:14:16 BST entry, as `RL-1329` quotes it): **"If
+      S3's golden set contains a directed-mode rung, S3's first run records its tightness as the
+      first measurement."** The bound is "validated on half_even only; directed modes are
+      covered by derivation, not measurement". The ledger records, from the first run, either
+      the directed-mode rungs' count and maximum tightness per mode, or the count `0` with the
+      predicate that found none (every golden rung's declared and applied mode, verbatim).
+    - **(e) Post-clamp served outputs, exact and rounded once, both cases** (`RL-1329` §4 C2 and
+      Acceptance 13; the maintainer's entry "2026-09-30 16:41:11 BST — RL 9963 C2: declared
+      outputs keep the POST-clamp served value; the acceptance is NOT widened"). Each declared
+      output is served as "the engine's exact `string()` value of the output step's source …
+      rounded once with that step's own `RoundSpec`", never the float and never a second rounding.
+      - **clamped:** on FD-1330's min-premium quote, `/score` serves `office_premium_minor` =
+        **5000**, the `constraints` rung's `value_minor` and the bound, not the office rung's
+        1436. `RL-1329` says this case "is green today and must stay green", so **its red
+        first is against a planted mutation**: a `_build_outputs` that serves the rung's
+        `value_minor` gives 1436, and the test is shown red on it;
+      - **unclamped:** the served output equals its ladder rung's `value_minor` exactly. Its red
+        first on `origin/main` is the exact value: `RL-1329` Acceptance 1's
+        `outputs["office_premium_minor"]` = **67358** (today 67357), and `FD-1336`'s
+        served-outputs case, a scratch algorithm declaring `instalment_loading_minor`: **69402**
+        after, **69399** today, with every `multiply`-kind rung output covered and
+        `ipt_and_fees_minor` and `constraints_minor` kept as green controls (`FD-1336`
+        *Disposition*, "Served outputs");
+      - a test asserts the served value is built from the exact string read, not from the float,
+        and a declared non-rung `money_minor` output is served as an integer from the exact
+        string, red first because today it is the float from `result` (`RL-1329` S6).
+    - **(f) The rest of `RL-1329`'s acceptance, by item:** 1 the realistic-scale red case
+      through `score_one` with `trace=True` (61234.5 → 70726), and the auditor's case (60000.4 →
+      69402) at unit level; 2 the scale sweep through a real ZEN evaluation, 1e3–1e7, 0–6
+      optional rungs, float32 risk, ≥ 200 quotes per cell, **at least two recorded seeds**, one
+      mixed-operation run, 100 % reconciled, **and the same sweep red over `origin/main`'s
+      builder**; 3 the six planted-defect controls; 4 the near-tie prices 1235, not 1234, and a
+      test fails if `_build_ladder` receives only floats (this is also `FD-1336` limb 3's one
+      input-level test, scoped to `_build_ladder`, not the module, because `score.py` uses
+      `float` legitimately for the elapsed-time parse); 5 the contract, with
+      `PositionalDecimalStr` red first on `Decimal("0.0000001")`, `Decimal("1.2E-28")` and
+      `Decimal("1E+1")`; 6 the three §5 shapes; 7 the re-derivation test's `round` branch
+      (`test_rating_score.py:224-225` at `8cef871d`) replaced by R4 (`FD-1336`'s F4); 8 the
+      false-positive control's three stop counts, of which (a)–(c) above are two, the third
+      being "quotes on which a clamp's comparison and disposition disagree" (a count above 0
+      stops the slice for the lead); 9 `scripts/bench-rating.py` before and after, in the
+      ledger, no budget changed; 10 the binding clamp (`FD-1330`), including a `max` clamp and a
+      step declaring both bounds, the replacement of
+      `test_a_clamp_overrides_the_ladder_and_is_recorded_on_the_constraints_rung`
+      (`test_rating_score.py:262` at `8cef871d`), and the placement refusal with
+      `LADDER_CLAMP_UNPLACEABLE` on its three algorithms, both at save and by `compile_bundle`,
+      with `_check_clamp_placement` registered in `ALGORITHM_CHECKS` so #967's closure test (ii)
+      passes, and the count of committed fixture algorithms and reachable stored bundles it
+      refuses (above 0 stops the slice); 11 the engine-precision guard on `zen-engine` 0.53.0;
+      12 the release-note line in the squash-commit body and the ledger; 13 is (e) above.
+    - **(g) `FD-1330`'s factor.** `FD-1330`'s acceptance says the office rung keeps "`multiply`
+      factor **1.1000**"; `RL-1329` records the factor unquantised ("×1.1", "never quantised to
+      4 dp"). **`RL-1329` governs**: the test asserts `Decimal(factor) == Decimal("1.1")` and
+      that the recorded string carries no 4 dp padding.
+- **Money is integer minor units, or `Decimal` in the rating path — never float** (`CLAUDE.md`
+  §7). ~~the reconciliation compares integers.~~ *(Superseded 2026-09-30 by `RL-1329`:)* the
+  reconciliation compares integers at the payable and the displays (R2, R4), and exact decimals
+  on the chain (R1, R3); every value crossing the binding for ladder or payable arithmetic is the
+  engine's `string()`, never the float (FR-273's string limb).
+| `03` §3.4 | FR-240 | `RL-1329`'s dated clause: a clamp the ladder cannot place is refused at save and at compile, `LADDER_CLAMP_UNPLACEABLE` (Acceptance 13 (f), item 10) |
+| `03` §3.6 | FR-247 | The `constraints` rung records a binding clamp as `clamp` (`FD-1330`; Acceptance 13 (f), item 10) |
+| `03` §3.6 | FR-248 | As amended by `RL-1329`: exact unrounded values, true operations, one rounding (Acceptance 13) |
+| `03` §3.8 | FR-261 | The "ladder reconciles" property takes the scoring-time verdict with its independent inputs, never rebuilding the anchors from the ladder it checks (`RL-1329` "What it obliges") |
+| `03` §3.11 | FR-273 | The string limb: ladder, payable and declared `money_minor` outputs read through `string()`, never the float (`FD-1336` limb 3; Acceptance 13 (e), (f) item 4) |
+**Also placed here (2026-09-30, `RL-1329` alignment):** `RL-1329` in full (Acceptance 13, Task
+6); `FD-1336` limb 1 — `reconcile_ladder` runs on every scored quote in every Environment, never
+sampled, with the NFR-496 prod-sampling limb decoupled, and the write-set additions its
+*Disposition* names (`pricing_core/__init__`, `rating/properties.py`, the census tests; all
+already in the table below) — and limbs 2 and 3 and F4 (Acceptance 13 (f), items 1–4 and 7);
+`FD-1330`, the clamp attributed to `constraints` (Acceptance 13 (f), item 10, and (g)); the
+OQ-1316 cross-reference note (Acceptance 1); and OQ-1334's merge gate (Status).
+### Write set added by `RL-1329`, and its contention (at `8cef871d`)
+
+`RL-1329` ("What it obliges", "S3's write set gains") adds the rows below; each cell was read at
+`origin/main` `8cef871d4ec30869dc3ef20559f3cac64e239a5c`. **#967's code slice has merged**
+(`3a5f7cd5`, #1012): `ALGORITHM_CHECKS` exists (`compile.py:247`), `validate_algorithm` runs it
+(`:253`, `:277`), and `RATING_ERROR_CODES` is `errors.py:297`. So `RL-1329`'s ordering
+condition ("S3's `compile.py` edit starts only after #967's code slice has merged", and the same
+for `errors.py`) is **met at this tree**; the executor re-verifies it in Task 0.
+
+| Path | This slice | Existing definitions edited |
+|---|---|---|
+| `packages/pricing-core/src/pricing_core/rating/compile.py` | **appends** `_check_clamp_placement(algo: RatingAlgorithm) -> list[ValidationIssue]` and **one entry** to `ALGORITHM_CHECKS` (`:247`); one import from `rating/ladder.py` | the `ALGORITHM_CHECKS` tuple (one entry), the import block. The check reads only `on_violation`, `consumes`, `produces` of a `constraint` step and the output steps' `output_name` and `consumes` (#967's closure 3c (i)) |
+| `packages/pricing-core/src/pricing_core/rating/ladder.py` | **new**: `_RUNG_ORDER`, `_output_steps_by_name` and the `<rung>_minor` naming, moved out of `score.py`; imports only `model_schema` | — (new file) |
+| `packages/pricing-core/src/pricing_core/rating/score.py` | the mapping moved out (`_RUNG_ORDER` `:226`, `_output_steps_by_name` `:576`); `_build_ladder` (`:582`), `_round_minor` (`:566`), `_build_outputs` (`:657`), the `reconcile_ladder` call (`:769`), and the "Ladder construction" docstring (`:62-103`) | all of these (existing definitions) |
+| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `to_wire` (`:344`)'s generated `string()` read; `_constraint_node` (`:264`)'s `__before`, `__min`, `__max` reads | `to_wire`, `_constraint_node` |
+| `packages/model-schema/src/model_schema/money.py` | **new** `PositionalDecimalStr`, beside `DecimalStr` (`:85`); `DecimalStr` and `Relativity` (`:94`) untouched | none (an addition) |
+| `packages/model-schema/src/model_schema/scoring.py` | `LadderOperationKind` (`:63`), `LadderOperation` (`:108`), `LadderRung` (`:127`) per `RL-1329` §3, beside the plan's `Trace.ladder_check_version` | those three, plus `Trace` (already in the table above) |
+| `docs/contracts/schemas/scoring.schema.json` (hand-authored) | `RL-1329` §3's fields, and the invariant text (`:60`) | the ladder definitions (already a row above) |
+| `backend/tests/test_contracts.py` | the contract guard run; a comparison added only if the guard needs one | only if a comparison is added |
+| `backend/src/app/errors.py` | **one member** `LADDER_CLAMP_UNPLACEABLE` appended to `RATING_ERROR_CODES` (`:297`) | that frozenset (one member) |
+| `packages/pricing-core/tests/test_rating_score.py` | the re-derivation test's `round` branch (`:224-225`) replaced by R4; `test_a_clamp_overrides_the_ladder_and_is_recorded_on_the_constraints_rung` (`:262`) replaced; new tests | those two tests |
+| `packages/pricing-core/tests/test_rating_compile.py`, `backend/tests/test_rating_algorithms.py` | the placement refusal's tests, **appended** | none |
+| `docs/specs/03-rating-engine.md` §4.4 (`:414`) | the example replaced (Task 6's contract commit) | §4.4 |
+| `docs/specs/03-rating-engine.md` §10 (`:1194`) and `docs/open-questions.md` (`:138`) | the OQ-1316 note appended to one row in each | OQ-1316's two mirror rows |
+
+**Against WK-690 Slice 2** (`PL-1327:90-129`, its write set, measured by it at `11c76b6c`).
+It writes `pricing_core/modelling/` (`objectives.py`, the new `expression_objective.py`,
+`errors.py`), `model_schema/objectives.py`, `model_schema/__init__.py`, the hand-authored
+`docs/contracts/schemas/objective-certificate.schema.json`, `scripts/bench-model.py`,
+`docs/specs/02-modelling.md`, and `backend/tests/test_contracts.py` "if the guard needs a new
+comparison". **The one possible shared existing file is `backend/tests/test_contracts.py`**,
+and only if both slices add a comparison there; each would add its own function, and no
+existing function is edited by both, which the dispatch record must name with that check
+(`RL-1263`'s exception). `model_schema/__init__.py` is shared only if this slice exports
+`PositionalDecimalStr`; the plan does not need it to (the ladder fields import it from
+`model_schema.money`), and **if the executor adds an export, that row serialises**. The generated
+contracts and `docs/INDEX.md` are exempt. **Also:** WK-690 S2's Task 6 is an NFR-476 timing
+measurement that "runs alone" (`RL-1263` item 3), and this slice's `bench-rating.py` run
+(Acceptance 13 (f), item 9) is a measurement too, so **the two measurements never share a
+window**, and neither runs beside the other slice's build.
+
+**Against WK-1250 Slice 1** (`PL-1325:141-175`, its contention table; `:176-186`, the existing
+definitions it edits). It edits `compile.py`'s `_producer_types` and `_check_result_types`
+(kept registered in `ALGORITHM_CHECKS`, with its signature, `PL-1325:132`, `:660-664`) and adds
+public entry points to `compile.py`'s `__all__`; it also edits `rating_algorithms.py`'s
+`_parse_algorithm`, `model_schema/rating.py`'s `_graph_invariants`, `model_schema/__init__.py`,
+`03` §2, §4 (a new subsection) and §5.1, and `scripts/generate-contracts.py`. Its set
+excludes "`compile_bundle`, `score.py`, `TraceStep`, `runtime.py`, any `approvals.py`,
+`errors.py`" (`PL-1325:186-187`). **Shared file: `compile.py`.** No function is edited by
+both: this slice appends one new function and edits the `ALGORITHM_CHECKS` tuple and the
+import block; WK-1250 S1 edits `_producer_types`, `_check_result_types` and `__all__`, and
+does not plan to edit the tuple. **The tuple and the import block are the lines at risk**: if
+WK-1250 S1's diff touches either, the two serialise. **Shared file: `03`.** Sections are
+disjoint (this slice: §3.6's FR-248 clause, §9's NFR-496 clause, §4.4, §4.5's note, §10's
+OQ-1316 row; WK-1250 S1: §2, §4's new subsection, §5.1). §4.4 and §4.5 are existing
+subsections inside §4, where WK-1250 S1 adds a new one, so that pair is checked on the actual
+diffs at dispatch. `model_schema/__init__.py` as above. `test_rating_compile.py` and
+`test_rating_algorithms.py`: appended tests on both sides, no existing test edited.
+**Verdict for the lead:** this slice can build beside WK-690 S2, provided the dispatch
+record names `test_contracts.py` with the no-shared-definition check and keeps the two
+measurements apart. Beside WK-1250 S1, the only shared definitions possible are the
+`ALGORITHM_CHECKS` tuple and `compile.py`'s import block. The dispatch record names them and
+checks both diffs. If either slice's actual diff edits a definition the other edits, they
+serialise (`RL-1263`: "any other shared path serialises unless the lead's dispatch record names
+the path and the check").
+
+| DP-S3-5 | **How does the premium ladder record each rung so that it shows the true operations and still reconciles to the penny?** (Raised by auditor-close1255's N5, folded into `FD-1336` as limb 2; routed by the maintainer to a fresh high-effort decision-maker.) *Row added 2026-09-30: the plan at `06e3e896` did not carry it as a row.* | as posed in `RL-1329` §1: (a) build each rung from the previous rounded rung; (b) a final residual `adjust`; the maintainer's steer (exact unrounded values, true factors, one rounding) | — (the planner's input predates the row) | decision point | yes — Task 6 | **Resolved by `RL-1329`** (minted from working id 9963): neither (a) nor (b); the steer adopted with three departures (the string read, the 10⁻²⁶ per-rung tolerance, `divide`) and the `clamp` kind. Its acceptance is this slice's Acceptance 13 |
+| DP-S3-6 | **Which stop bound applies to a rung that is `none` in the baseline ladder** (the `office_premium` checkpoint when unchanged, `constraints` when no clamp binds)? `RL-1329` Acceptance 8 names bounds for `multiply`, `add`, `round`, the first rung and a binding clamp, and is silent on `none` | (a) the bound of the nearest earlier rung that is not `none`, because a `none` rung copies its predecessor's value in both ladders (`RL-1329` §2 step 3; `score.py`'s checkpoint convention), so its difference is its predecessor's; (b) exact equality with the predecessor's difference, `abs(base_i − new_i) == abs(base_{i−1} − new_{i−1})`, which is what (a) implies and is stricter | **(b)**: it follows from the construction without a new constant, and a violation would mean the rung is not a copy, which R1 should already refuse | decision point | no — resolved at Task 6 step "the false-positive control"; **default (b)** until ruled, and the ledger records the count of baseline `none` rungs | *open* — for the decision-maker at medium effort |
+- [ ] Re-verify the `RL-1329` write-set rows at the executor's tree: `ALGORITHM_CHECKS` exists
+  in `compile.py` and `validate_algorithm` runs it (the ordering condition), `RATING_ERROR_CODES`
+  in `errors.py`, and every line cited "at `8cef871d`". Record OQ-1334's state (the merge gate).
+- [ ] Acceptance 1's edits through `spec-change`, including the OQ-1316 note on both mirrors
+  (its `grep -c -F` prints `1` per file) and not §4.4's example (Task 6);
+  `python3 scripts/audit-docs.py`; commit.
+- [ ] **`RL-1329`, red first on `origin/main`** (Acceptance 13), in this order, each commit
+  green on its own:
+  1. **The contract:** `PositionalDecimalStr` in `model_schema/money.py` (red first on the
+     three values of Acceptance 13 (f), item 5); `RL-1329` §3's fields on `LadderOperation` and
+     `LadderRung`, the hand-authored `scoring.schema.json` in step, `generate-contracts.py
+     --check` and the contract guard quoted; **§4.4's example replaced in this commit**; commit.
+  2. **The mapping moved:** `pricing_core/rating/ladder.py` created with `_RUNG_ORDER`,
+     `_output_steps_by_name` and the naming; `score.py` imports it; no behaviour change (the
+     existing suite green, quoted); commit.
+  3. **The reads:** `to_wire`'s `string()` read and `_constraint_node`'s `__before`, `__min`,
+     `__max` reads (`runtime.py`); commit with the tests of Acceptance 13 (f), items 4 and 11.
+  4. **The builder, `_build_outputs` and the predicate:** `RL-1329` §2, §4 and §5 in
+     `score.py`, `reconcile_ladder` and every caller (`score.py:769`, `properties.py:303`,
+     `pricing_core/__init__.py:31` at `8cef871d`); the FR-261 property takes the scoring-time
+     verdict with its independent inputs; red first for Acceptance 13 (e) and (f), items 1–3,
+     6, 7 and 10; the docstrings (`score.py:62-103`, `model_schema/scoring.py`'s
+     `LadderOperation` and module docstrings); commit.
+  5. **The placement refusal:** `_check_clamp_placement` appended to `compile.py`,
+     one entry in `ALGORITHM_CHECKS`, `LADDER_CLAMP_UNPLACEABLE` appended to
+     `RATING_ERROR_CODES`; red first on the three algorithms, at save and at `compile_bundle`;
+     the refused-fixture count; commit.
+  6. **The sweep and the false-positive control:** Acceptance 13 (f), item 2's sweep (≥ 2 seeds,
+     and red over `origin/main`'s builder); the three stop counts with (a)–(d), DP-S3-6's rule
+     applied to baseline `none` rungs; any count above 0 stops the task for the lead or, for (a)
+     and (b), the maintainer; commit.
+  7. **The bench** (`scripts/bench-rating.py` before and after, in a solo window, `RL-1263`
+     item 3) and the release-note line drafted for the squash body and the ledger (Acceptance 13
+     (f), items 9 and 12).
+- **`RL-1329` alignment (2026-09-30, at `8cef871d`)**, on the lead's brief: Acceptance 13 is
+  `RL-1329` in full, with its stop predicate, report line, golden payable stop, directed-mode
+  clause and served-output cases quoted from the record; Acceptance 10's superseded parts are
+  marked as `RL-1329`'s supersede table names them; the Global Constraints money line restated;
+  `FD-1336` (limbs 1–3, F4 and served outputs) and `FD-1330` placed; the OQ-1316 note
+  (Acceptance 1); OQ-1334's merge gate (Status); the added write set with its contention against
+  WK-690 S2 (`PL-1327`) and WK-1250 S1 (`PL-1325`); DP-S3-5 recorded as resolved; DP-S3-6
+  raised (the baseline `none` rung, on which `RL-1329` is silent). Three places where the
+  record and the brief's paraphrase differed, `RL-1329` followed: the directed-mode clause is
+  conditional ("If S3's golden set contains a directed-mode rung"); the clamped served-output
+  case is green on `origin/main` and red first only against a planted mutation; and `FD-1330`'s
+  "1.1000" is `RL-1329`'s unquantised "×1.1".
+- **Open:** DP-S3-1 and DP-S3-2, each for the decision-maker at medium effort; DP-S3-6,
+  non-blocking with a default.
````

Premise check at `36b2a121` (executor-674s3):

- Base verified: `git log -1` prints `36b2a121662b9d69a309fee0e8023fbfff3a71ea`.
- `uv sync --all-packages` succeeded in the new worktree.
- OQ-1316 mirrors: `docs/open-questions.md:138` and `docs/specs/03-rating-engine.md:1194` both
  exist, both status `open`, neither carries the cross-reference note yet
  (`grep -c "Cross-reference added 2026-09-30"` prints 0 for each).
- `gh pr list --state open`: no open PR touches `packages/`, `backend/`, `docs/specs/03-*` or
  `docs/open-questions.md` (the docs-only PRs #1023, #987, #986 touch plans, roadmap, findings).

## PRs

(none yet; the lead opens or approves the PR at the gate.)
