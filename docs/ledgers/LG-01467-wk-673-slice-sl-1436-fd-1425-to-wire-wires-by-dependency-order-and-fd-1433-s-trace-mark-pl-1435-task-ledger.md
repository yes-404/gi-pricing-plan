---
id: LG-1467
family: ledger
title: WK-673 slice SL-1436 — FD-1425's wiring limb, to_wire wires by dependency order, and FD-1433's trace mark (PL-1435), task ledger
status: closed
created: 2026-10-06            # original date 2026-10-05, set at the working id; minted 2026-10-06
owner: executor
tree: 23af6997161789887d26f2868a6022a0738e44e6
phase: P2
work: WK-673
slice: SL-1436
plans: [PL-1435]
corrected_by: []
relates: [RL-1423, RL-1434, RL-1263, FD-1425, FD-1433, FR-212, FR-259, WK-673]
---

# WK-673 slice SL-1436 — the wiring limb of FD-1425 and FD-1433's trace mark

Executed from `PL-1435` by `executor-sl1436` (sonnet). Branch `sl-1436-fd-1425-to-wire-dependency-order`. Stamps are
BST (`TZ=Europe/London date`). The dispatch record is `gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1436-2026-10-05.md`
(FINAL; a local file, not in the repository). **FD-1425 stays OPEN in every record until this slice merges.**

## Tasks

### Task 0 — preconditions and the RL vs PL comparison

**Base.** Worktree from `origin/main` `23af6997161789887d26f2868a6022a0738e44e6` (#1226). `uv sync --all-packages` ran.
Test database `gipricing_sl-1436_d9698591` (`createdb -T gipricing`, `alembic upgrade head`); `alembic current` and
`alembic heads` both print `e5b7d9f1a3c6`. PL-1435 and SL-1436 are `active`.

**RL-1434 vs PL-1435:** D1 none (the anchors `RL-916.)* |` and the FR-212 row's closing text each `grep -cF` = 1 in `03`).
D2: T-M1 names WK-1178 where the slice is WK-673; applied as written, per the maintainer's (by delegation) entry
"2026-10-05 22:52:50 BST", which leaves it. D3: the `models.py` comment is Delta 7's; RL-1434 is silent, no conflict.

**RL-1423 vs PL-1435 (T1):** RL-1423's T1 replacement carries the working id "FD 9572" (28 occurrences in the RL);
RL-1423 lines 243-244 say the mint replaces it with the minted `FD-` id. The lead ruled (A): apply `FD-1425`, citing the
maintainer's (by delegation) entry "2026-10-05 19:33:23 BST" (Option A, SL-1427's T2) and RL-1423 lines 243-244.

### Task 1 and Task 2b — the reds, at base commit `23af6997` (tests only, no code change)

Commit `835e0e3d`. `_SCORE_FIXTURE_HASH` was printed twice before it was pasted: both runs
`sha256:86abdb81dc16d2075956aa11e05f2e9c87fe191d4a3397574e5a82520039073d`.

`uv run pytest packages/pricing-core/tests/test_rating_wire_order.py -q` at the base: **8 failed, 6 passed.**

| Test | At base | Cause shown |
|---|---|---|
| `…_topological_twin[ctx0]` | FAIL | `RuntimeError` NodeError on `s_b`, "base + 50" |
| `…_topological_twin[ctx1]` | FAIL | `assert 57 == 350` |
| `…_clamp_listed_before_its_producer_still_binds` | FAIL | `assert 1507 == 5250` |
| `…_no_side_branch_carries_a_stale_copy_into_the_sink` | FAIL | `assert 777 == 5250` (the plan's expected cause) |
| `…_r5_reorder_pair_prices_alike[False]` | FAIL | `assert 777 == 5250` |
| `…_r5_reorder_pair_prices_alike[True]` | PASS | a pin: the instalment step listed early already gave 5250 |
| `…_no_ladder_side_branch…[True-decline]`, `[True-error]`, `[True-terminal_expression]` | FAIL | `assert 300 == 5000` (side branch listed before the clamp) |
| `…_no_ladder_side_branch…[False-*]` (three) | PASS | pins: branch listed after the clamp |
| `…_wires_exactly_as_listed`, `…_bundle_hash_is_unchanged` | PASS | pins (proven able to fail in Task 2 Step 5) |

The no-ladder cases the plan expected might pass: three of the six are real reds (300 against 5000), a case the
auditor's measurement could not reach. No case was weakened. The `(c)` tests of the original Task 1 are PL-1426's and
were not added (Delta 1). The test module drops the `polars`/`score_batch` imports the withdrawn tests used.

### Task 2d — FD-1433: a trace that did not reproduce is marked where it is read (commit `6f4b6f2f`)

Lands **before** the `to_wire` chain change (FD-1433's ordering, GO condition (4)). Base run, alone, the test database
above: `test_a_reproduction_that_differs_from_the_served_quote_is_marked` FAILS with `assert None == 'complete'`.

Applied: T-M1 byte for byte at the end of FR-259's third clarification (`03` row, inserted after `RL-916.)*`), with
`<Task 2d date>` = 2026-10-05; `TraceView.status: Literal["complete", "mismatch"]`, required, set in `_view` from the
row (`cast`, because the model validates the two values at runtime and `mypy --strict` types the column as `str`);
`_filtered` unchanged; the `ScoringTraceRow.blob_sha256` comment corrected (a `mismatch` row whose bundle no longer
resolved has no body); `docs/contracts/openapi/generated.json` regenerated (`TraceView` gains `status`, nothing else;
`generate-contracts.py --check`: "45 generated contracts match the models"). No `model-schema` file, no migration.

Head: `test_traces_api.py` 8 passed, `test_traces.py` 39 passed, no assert edited. Broken `_view` (`status="complete"`
for every row): the new test FAILS at the `quote-differs` assert (the `mismatch` item, `'complete'` against
`'mismatch'`); reverted. `mypy` and `ruff` clean.

### Task 2c, Step 1 — the golden replay, recorded at the base (tests-only tree `835e0e3d`, `runtime.py` unchanged)

Script `replay.py` (sha256 prefix `b43d213cdd4bae7c`; scratch directory, with `base.jsonl`). It records, per case and
context, `score_one` with `trace=False` and `trace=True` (`trace` and `timing_ms` blanked) and the raw engine `result`,
each as canonical JSON, plus every `content_hash`. Cases: fremtpl2-demo@1 (21 contexts), bench-rating-gbm and
bench-rating-no-gbm (200 each, booster 300 rows / 20 rounds), bench-trace-size n = 5, 20, 50, 100, 187 (50 each),
bench-score-batch and bench-compiled-for (20 each), score-fixture and score-fixture-glm (243 each).
`base.jsonl`: 3603 lines, sha256 `19b819f761760779a4e4d9c15304255cd78a10a47fc58d1c82dd27c325d2cc70`.
`score` classes at base: quoted 809, clamp 91, declined 53, error 244. **Unproven class:** `score-fixture-glm` errors
on every context with `MODEL_CALL_FAILED` (a GLM pin has no factors in the bundle, by design at the base), so that
case proves only that the error is unchanged.

### The production-handler census (before the chain commit; the maintainer's (by delegation) ruling (A))

Pattern, verbatim, run at the worktree root on the tree above:

`grep -rnE "customHandler|custom_handler|ZenEngine\(|zen\.ZenEngine|create_decision|\"customNode\"|def handler\(" packages/*/src backend/src --include=*.py`

and `grep -rnE "^import zen|^from zen|import zen" packages/*/src backend/src --include=*.py`. Code hits (prose hits in
docstrings omitted): exactly **one** engine is built, `runtime.py:697` (`zen.ZenEngine({"customHandler": handler})`,
in `load_bundle`), and exactly **one** handler exists, `handler` at `runtime.py:556` inside `_model_call_handler`
(`customNode` is emitted only at `runtime.py:409`). Its three returns: the two failure returns (`:561`, `:594`) go
through `_model_call_failure` (`:138`: `{**context, <zeros>, MODEL_CALL_ERROR_KEY}`), and the one success return
(`:610`) is `{**context, <produced>}`: **all three pass the context through; none drops it.** The other importer,
`compile.py:25`, uses only `zen.compile_expression` (`:320`), a validator, no engine. The only context-dropping handler
in the repository was the test stand-in at `test_rating_runtime.py:345-346`, fixed by the one-line edit below.

**The one test line (ruling (A)).** `test_rating_runtime.py:346` now returns `{"output": {**request.input,
"risk_premium_minor": 5000}}`; the assert at `:351` is untouched; `git diff -U0` of the file shows that line alone.
Before it, `test_to_wire_translates_a_constraint_step` failed with `NodeError` on `s_office` (the stand-in dropped
`expense_factor`); after it the file passes (11 passed).

**Hand-off to A-1, A-2 and A-3 (WK-1178; PL 9599, PL 9597, PL 9595; `_model_call_handler`).** After this slice merges, the
handler returns `{**context, **produced}` on success and `{**context, <zeros>, MODEL_CALL_ERROR_KEY}` on failure. A
branch any of them adds (a GLM branch, a peril-structure branch) returns through that same success expression or through
`_model_call_failure`, never `{"output": {produced names only}}`: on the ordered chain the next step would lose the
context. The one that merges second rebases (merges main) and re-runs `test_rating_wire_order.py` and Task 2c's replay.

### Task 2 / 2b — the chain commit, with T1

T1 is applied to the FR-212 row of `03` in the same commit as the code (`CLAUDE.md` §2), `FD-1425` substituted for the
RL-1423 working id "FD 9572" as ruled (the 19:33:23 BST entry; RL-1423 lines 243-244). After it: `grep -cF` of the
substituted text prints **1**, and `grep -cF 'FD 9572'` over `docs/specs/03-rating-engine.md` prints **0**. At head with
the chain: `test_rating_wire_order.py` 14 passed (the eight base reds all green); pin proofs, each reverted after: a FIFO
in place of the heap fails `test_a_topologically_listed_algorithm_wires_exactly_as_listed` with
`assert ['s_a', 's_d', 's_b'] == ['s_a', 's_b', 's_d']`; the last hex digit of `_SCORE_FIXTURE_HASH` changed fails
`test_the_bundle_hash_is_unchanged` naming both values. `test_rating_score.py` 40 passed, `test_rating_ladder_exact.py`
26 passed, `test_rating_runtime.py` 11 passed (after the one-line stand-in fix above), no assert edited.

### Task 2c, Steps 2 and 4 — the head replay: a DIFFERENCE, so a STOP (RL-1423 conditions A and B)

At head `47e09550`, `replay.py` (sha256 prefix `b43d213cdd4bae7c`), the already-compiled path and the fresh path agree
with each other (both output files sha256 `8c1cec7b09f15a050130a479c66fd4152bf4f22841fdba66084ecefdd3c3ac4c`) and
every `content_hash` equals the base's. Per case, `equal N of N` over (hash line, then `score`, `score_trace`, `raw` per
context): fremtpl2-demo@1 64/64; bench-rating-no-gbm 601/601; bench-score-batch 61/61; bench-compiled-for 61/61;
score-fixture 730/730 (quoted 98, clamp 91, declined 53, error 1); score-fixture-glm 730/730 (all 243 error, unproven
beyond "the error is unchanged"); **bench-rating-gbm 401/601 and bench-trace-size n = 5, 20, 50, 100, 187 each 101/151.**

**All 450 differing lines are `raw` lines of the `model_call` cases** (200 + 5 x 50); **no `score` or `score_trace`
line differs anywhere**, so every served `ScoringResult` is identical, and every `content_hash` is identical. The
difference is the raw engine dict's echo of the quote's own float inputs `f0`..`f7`: the head value is the base
value cut to 15 significant digits (`0.08487199515892163` becomes `0.0848719951589216`; maximum relative difference
measured `1.17e-15`; no other key differs). The cause is read from the diff, not proven: on the chain the context
travels through the `model_call` handler's `request.input` and back, which the engine re-serialises.

**This is a difference outside the FD-1425 fixtures, so it is a STOP for the maintainer (by delegation)** (RL-1423
Condition B; Task 2c Step 4). Nothing was edited, no comparator was loosened. Reported to the lead.

**Timing and the sweep-pause (stated honestly).** The head replay ran once, as one process (`OMP_NUM_THREADS=1 nice -n 19`,
no pytest, no database), started just after the chain commit `47e09550` (commit stamp 22:48:35 UTC = 23:48:35 BST) and
finished 22:49:58 UTC (23:49:58 BST): `head-compiled.jsonl` written 22:49:19 UTC, `head-fresh.jsonl` 22:49:58 UTC (file
mtimes). The base recording had run earlier, finishing 22:42:19 UTC. **The head replay overlapped S7's held gate-1:** I did
not read the slots immediately before starting it, and the maintainer's (by delegation) ruling that Task 2c's replay is a
batch which waits for S7's release reached me after it had run. S7's gate may therefore have been contended during that
window of about 80 seconds. The replay is a run, not a re-run: it is not repeated, and its result above stands. A re-run, if
the maintainer rules one, waits for the release of gate-1.

### The two conditions on ruling (A) — run after S7's gate end (00:15:47 BST; both slots read free before each run)

**(1) The cause, one single-file experiment** (`echo_experiment.py`, scratch directory; one process, `OMP_NUM_THREADS=1 nice -n 19`):
the same float, bench-rating-gbm context 0's `f0`, through (i) an expression node only, and (ii) a `customNode` whose handler
returns `request.input` UNCHANGED. Echoes, verbatim:

```
input         : 0.08487199515892163
(i)  expression: 0.08487199515892163
(ii) handler in : 0.08487199515892163
(ii) handler out: 0.0848719951589216
```

The expression path keeps all 17 digits. The handler **receives** the exact value and the value it **returns** unchanged comes back
cut to 15 significant digits: **(ii) alone truncates**, on the handler's return path into the engine. So (A) stands.

**(2) The downstream-reader check.** Predicate: every committed algorithm step with `"type": "model_call"`
(`grep -rnE "\"type\": *\"model_call\"|type: *model_call|'type': *'model_call'" examples scripts packages backend docs/contracts
--include=*.py --include=*.json --include=*.yaml --include=*.yml -l`, plus `git ls-files | grep -E "\.(json|ya?ml)$" | xargs grep -lE
"\"model_call\""`; and `grep -rnE "RatingModelCallStep\(" --include=*.py packages backend examples scripts`, non-`src/` hits none), then
the steps after it that read a float. Hits: `scripts/bench-rating.py` (`s_risk`, steps listed after it), `packages/pricing-core/tests/
test_rating_score.py:66` (`s_risk`), `test_rating_runtime.py:121`; copies of one shape at `test_rating_compile.py:38, :86`,
`test_rating_compile_bundle.py:49`, `backend/tests/test_rating_algorithms.py:40, :88`, `model-schema/tests/test_rating_algorithm.py:53`,
`test_rating_version.py:105`, which are compiled or saved, never scored through the handler. `examples/` has no `model_call` step
(`grep -rln "model_call" examples` prints nothing). In every scored case the steps after `s_risk` read only `risk_premium_minor`
(an `int`), `driver_age` (an `int`), and `expense_factor` (a rate-table float produced BEFORE the model call, `1.1` and `1.25`,
`test_rating_runtime.py:94-95`: both exact in 15 significant digits) — and, in `bench-rating.py`, `v000`.. (produced after). **No
committed step reads a float input after a `model_call`:** `f0`..`f7` are consumed only by `s_risk` itself.

**Limit (C), for this ledger and the PR body.** An algorithm that, after a `model_call`, reads a float (an input, or a value
produced before the call) carrying more than 15 significant digits would see it cut to 15 digits at the 1e-15 level; none is
committed. The LOW finding is filed as FD 9480 (working id), draft #1229, by auditor-floatecho. Its disposition: (1) accept and disclose, and (2) a characterisation test carried by a later slice.

### The gate (2026-10-06, gate-1, one hold, head `e0e2ff2085c370c5b4e011acd84cfd1f632c8cf5`, tree `24595ee9483b0ef2cec32962972752116a7100a8`)

Granted by the lead for that head. `alembic current` == `alembic heads` == `e5b7d9f1a3c6` at the start. The Python half is
`dev-commands`' gate body verbatim, the frontend half follows inside the same `flock` hold (`flock -n -E 99 /tmp/slots/gate-1 env
GIP_GATE_SLOT=/tmp/slots/gate-1 timeout 3500 bash <script>`). The harness moved the foreground call to the background at its 600 s
cap; the wait was on the flock's pid (cwd read as this worktree). Python half 00:20:12 to 00:47:44 BST (start `load average:
2.05, 2.30, 1.93`, free 18048 MB; end 1.53, 1.51, 1.62, free 19609 MB); frontend half 00:47:44 to 00:48:45 BST (end 4.04, 2.15, 1.84).

| stage | result |
|---|---|
| ruff, mypy, import_linter, req_coverage, contracts | pass (exit 0) |
| audit_docs | FAIL (exit 1): only `check 31: gap in the full allocation between 1442 and 9482` (the ledger, then still unminted under working id 9482, now LG-1467) |
| pytest | FAIL (exit 1): `13 failed, 4957 passed, 4 skipped, 86 warnings in 1636.90s (0:27:16)` |
| pnpm install --frozen-lockfile, generate:api, lint, type-check, test, build | all rc 0 |

The 13 failed tests, each failing through audit-docs's check 31 or the `docs/INDEX.md` contiguity gap at 9482:
`test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`,
`test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`,
`test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`,
`::test_the_committed_digest_currently_matches_the_committed_spec`,
`test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`,
`test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`,
`test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`, `::test_check_29_note_carries_the_residue_line`,
`::test_phase1b_residue_count_matches_check_29s_own_count`, `test_register_owed.py::test_check_29_wiring_is_undisturbed`,
`test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`,
`::test_journey_citations_are_audited_in_ci`. The set was not compared with a recorded known set by the executor; the lead compares it.

### The trial merges (F-A: restored; a commit of this ledger had dropped the section)

At the gate, `git merge-tree --write-tree <other head> a67f46ce465f9a17b4fea1f224714058ec0f3373` (this slice's head after the INDEX
regeneration), each **exit 1**:
- against S7 (`origin/sl-1391-fr-231-exposure-weights-portfolio-frame`, `21096c36998c7f91f8eb6ce1463ed026851e6258`): the only
  `CONFLICT` is `docs/INDEX.md` (generated); `docs/specs/03-rating-engine.md` and `docs/contracts/openapi/generated.json`
  auto-merge clean.
- against SL-1430 (`origin/sl-1430-fd-1421-rating-version-algorithm-and-pins`, `260ead6640ed3a784426f38b0771206ec30ea8a1`): the
  same single conflict, `docs/INDEX.md`; `03` and `generated.json` auto-merge clean.

The slice auditor's re-run at this slice's head `669d55260931d0412e8d175627d789ce025d3d95` (as the lead relayed it): against
`origin/main` `8f5a8987c3467fa9961f02b2cfd5ceeb2d31411d` rc 0; against S7 `21096c36` rc 1, INDEX-only; against SL-1430 `260ead66` rc 1,
INDEX-only.

My own fresh run, 2026-10-06, `git merge-tree --write-tree 89fcb092811e3964d9e2af8d262019a396c21994
669d55260931d0412e8d175627d789ce025d3d95` (S7's new head against this slice's head): **exit 1**, the only `CONFLICT` is
`docs/INDEX.md` (generated); `03` and `generated.json` auto-merge clean.

`docs/INDEX.md` is registry-exempt and regenerated (`python3 scripts/doc-index.py`) by whichever slice merges second, by a MERGE of
main, never a rebase (the 22:52:50 BST exception's condition); `generated.json` is regenerated, never hand-merged.

### Acceptance 11 — the replay script inline, the basis for the difference, and the deviation (F-B)

The script, `replay.py`, sha256 `b43d213cdd4bae7c3b6d100933ba85875421ae15925a5eccde56832ecf71cfea` (recomputed 2026-10-06; the earlier entries gave its 16-hex prefix `b43d213cdd4bae7c`):

```python
"""PL-1435 Task 2c: golden replay, DP-R1 Condition B. Modes: record (base) / replay (head).

record DIR : build every case, write cases.json (version, payloads, contexts), one bundle file
             per case, and base.jsonl (one canonical line per case/context/path).
replay DIR : rebuild the lines from (a) the stored bundles loaded again, (b) a fresh
             compile_bundle from the stored version + payloads; compare each to base.jsonl.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import random
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path("/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1436")
sys.path.insert(0, str(ROOT / "packages/pricing-core/tests"))
sys.path.insert(0, str(ROOT / "scripts"))

from model_schema.rating import RatingVersion  # noqa: E402
from model_schema.refs import ArtifactRef  # noqa: E402
from model_schema.scoring import QuoteContext, QuoteContextOptions  # noqa: E402
from pricing_core.rating.compile import Bundle, ResolvedArtifact, compile_bundle  # noqa: E402
from pricing_core.rating.runtime import load_bundle  # noqa: E402
from pricing_core.rating.score import score_one  # noqa: E402


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


class DictResolver:
    def __init__(self, payloads: dict[str, dict[str, Any]]) -> None:
        self.payloads = payloads

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self.payloads[str(ref)])


def _plain_version(slug: str, algo_slug: str) -> RatingVersion:
    from uuid import uuid4

    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": slug, "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()), "model_ref": "model:none@1",
        "created_at": "2026-08-29T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-08-29T12:00:00Z",
        "algorithm_ref": f"rating_algorithm:{algo_slug}@1",
        "pins": {"rate_tables": [], "models": [], "reference_tables": [],
                 "custom_objectives": []},
        "model_reference_mode": "exact"})


def _bench_ctxs(n: int, seed: int, features: list[str]) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        d: dict[str, Any] = {"driver_age": rng.randint(17, 99),
                             "channel": rng.choice(["direct", "broker"])}
        d.update({f: rng.uniform(0.0, 1.0) for f in features})
        out.append(d)
    return out


def _int_ctxs(n: int, seed: int, hi: int, first: list[int] | None = None) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    vals = list(first or []) + [rng.randint(0, hi) for _ in range(n)]
    return [{"premium_in": v} for v in vals]


def _fixture_ctxs(n: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        decl = rng.random()
        out.append({
            "driver_age": rng.randint(17, 99), "channel": rng.choice(["direct", "broker"]),
            "min_premium_minor": rng.choice([0, 0, 5000, 100_000]),
            "sanity_cap_minor": rng.choice([999_999_999, 999_999_999, 1, 3000]) if decl < .3
            else 999_999_999,
            "sanity_floor_minor": rng.choice([0, 0, 999_999_999]) if decl > .7 else 0,
        })
    return out


async def build_cases() -> list[dict[str, Any]]:
    import test_rating_score as T  # noqa: N812

    br = _load("_bench_rating", ROOT / "scripts/bench-rating.py")
    ts = _load("_bench_trace_size", ROOT / "scripts/bench-trace-size.py")
    sb = _load("_bench_score_batch", ROOT / "scripts/bench-score-batch.py")
    cf = _load("_bench_compiled_for", ROOT / "scripts/bench-compiled-for.py")
    demo = _load("_demo_model", ROOT / "examples/fremtpl2/model.py")
    cases: list[dict[str, Any]] = []

    def add(name: str, version: RatingVersion, payloads: dict[str, Any],
            ctxs: list[dict[str, Any]], ref: str) -> None:
        cases.append({"name": name, "version": version, "payloads": payloads,
                      "contexts": ctxs, "ref": ref})

    # 1 demo
    algo = demo._demo_algorithm()
    add("fremtpl2-demo@1", _plain_version("fremtpl2-demo", algo["slug"]),
        {f"rating_algorithm:{algo['slug']}@1": algo},
        _int_ctxs(20, 1, 1_000_000, [demo.DEMO_PREMIUM_IN]), "rating_version:fremtpl2-demo@1")
    # 2, 3 bench-rating
    rounds, rows = ts.TRAIN_ROUNDS, ts.TRAIN_ROWS
    feats = br.FEATURE_ORDER
    for gbm in (True, False):
        r = br._FakeResolver(with_gbm=gbm, n_expr=br.N_EXPR_STEPS, rounds=rounds, rows=rows)
        v = br._version(with_gbm=gbm)
        add(f"bench-rating-{'gbm' if gbm else 'no-gbm'}", v, r._payloads,
            _bench_ctxs(200, 2, feats), f"rating_version:{v.slug}@1")
    # 4 trace-size
    for n in ts.N_EXPR_VALUES:
        r = br._FakeResolver(with_gbm=True, n_expr=n, rounds=rounds, rows=rows)
        v = br._version(with_gbm=True)
        add(f"bench-trace-size-n{n}", v, r._payloads, _bench_ctxs(50, 3, feats),
            f"rating_version:{v.slug}@1")
    # 5, 6
    for nm, mod in (("bench-score-batch", sb), ("bench-compiled-for", cf)):
        a = mod._algorithm_payload()
        add(nm, _plain_version(nm, a["slug"]), {f"rating_algorithm:{a['slug']}@1": a},
            _int_ctxs(20, 4, 100_000), f"rating_version:{nm}@1")
    # 7 score fixture
    extra = [
        {"driver_age": 34, "channel": "direct", "min_premium_minor": 0,
         "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0},
        {"driver_age": 34, "channel": "direct", "min_premium_minor": 0,
         "sanity_cap_minor": 1, "sanity_floor_minor": 999_999_999},
        {"channel": "direct", "min_premium_minor": 0,
         "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0},
    ]
    for glm in (False, True):
        r = T._FakeResolver(glm=glm)
        v = T._version(glm=glm)
        add(f"score-fixture{'-glm' if glm else ''}", v, r._payloads,
            extra + _fixture_ctxs(240, 5), "rating_version:score-fixture@1")
    return cases


def _qctx(inputs: dict[str, Any], ref: str) -> QuoteContext:
    return QuoteContext.model_validate({
        "purpose": "new_business", "quoted_at": datetime(2026, 8, 29, 12, 0, 0),
        "effective_date": date(2026, 9, 1), "inputs": inputs,
        "options": QuoteContextOptions(rating_version_ref=ArtifactRef.model_validate(ref))})


def _classify(res: Any) -> str:
    if isinstance(res, str):
        return "error"
    if res.outcome != "quoted":
        return "declined"
    rungs = {r.rung: r.value_minor for r in res.premium_ladder}
    if "constraints" in rungs and "office_premium" in rungs and \
            rungs["constraints"] != rungs["office_premium"]:
        return "clamp"
    return "quoted"


async def lines_for(case: dict[str, Any], compiled: Any, content_hash: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = [(f"{case['name']}|hash", "", content_hash)]
    for i, inputs in enumerate(case["contexts"]):
        ctx = _qctx(inputs, case["ref"])
        for path, trace in (("score", False), ("score_trace", True)):
            try:
                res = await score_one(compiled, ctx, trace=trace)
                d = res.model_copy(update={"trace": None, "timing_ms": {}}).model_dump(mode="json")
                out.append((f"{case['name']}|{i}|{path}", _classify(res), canon(d)))
            except Exception as exc:  # noqa: BLE001
                out.append((f"{case['name']}|{i}|{path}", "error", f"{type(exc).__name__}: {exc}"))
        engine_ctx = {"effective_date": "2026-09-01", "purpose": "new_business", **inputs}
        try:
            raw = await compiled.decision.async_evaluate(engine_ctx)
            out.append((f"{case['name']}|{i}|raw", "", canon(raw["result"])))
        except Exception as exc:  # noqa: BLE001
            out.append((f"{case['name']}|{i}|raw", "", f"{type(exc).__name__}: {exc}"))
    return out


def write(path: Path, lines: list[tuple[str, str, str]]) -> str:
    text = "".join(canon(list(t)) + "\n" for t in lines)
    path.write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


async def record(d: Path) -> None:
    cases = await build_cases()
    meta = []
    lines: list[tuple[str, str, str]] = []
    for c in cases:
        bundle = await compile_bundle(c["version"], DictResolver(c["payloads"]))
        (d / f"bundle-{c['name']}.json").write_text(bundle.model_dump_json())
        lines += await lines_for(c, load_bundle(bundle), bundle.content_hash)
        meta.append({"name": c["name"], "version": c["version"].model_dump(mode="json"),
                     "payloads": c["payloads"], "contexts": c["contexts"], "ref": c["ref"]})
    (d / "cases.json").write_text(canon(meta))
    print("base.jsonl sha256", write(d / "base.jsonl", lines), "lines", len(lines))


async def replay(d: Path) -> None:
    meta = json.loads((d / "cases.json").read_text())
    base = [json.loads(x) for x in (d / "base.jsonl").read_text().splitlines()]
    for mode in ("compiled", "fresh"):
        lines: list[tuple[str, str, str]] = []
        for c in meta:
            c = {**c, "version": RatingVersion.model_validate(c["version"])}
            if mode == "compiled":
                bundle = Bundle.model_validate_json((d / f"bundle-{c['name']}.json").read_text())
            else:
                bundle = await compile_bundle(c["version"], DictResolver(c["payloads"]))
            lines += await lines_for(c, load_bundle(bundle), bundle.content_hash)
        digest = write(d / f"head-{mode}.jsonl", lines)
        per: dict[str, list[int]] = {}
        diffs = []
        for b, h in zip(base, lines, strict=True):
            case = b[0].split("|")[0]
            tot = per.setdefault(case, [0, 0])
            tot[0] += 1
            if b == list(h):
                tot[1] += 1
            else:
                diffs.append((b, h))
        print(f"== {mode} head sha256 {digest}")
        for case, (n, eq) in per.items():
            classes: dict[str, int] = {}
            for b in base:
                if b[0].startswith(case + "|") and b[0].endswith("|score"):
                    classes[b[1]] = classes.get(b[1], 0) + 1
            print(f"{case}: equal {eq} of {n}; score classes {classes}")
        print("DIFFS", len(diffs))
        for b, h in diffs[:3]:
            print("BASE", b, "\nHEAD", list(h))


if __name__ == "__main__":
    mode, dirname = sys.argv[1], Path(sys.argv[2])
    asyncio.run(record(dirname) if mode == "record" else replay(dirname))
```

**Deviation from "equal N of N".** Acceptance 11 asks for `equal N of N` on every algorithm. It is not met: `bench-rating-gbm` is
equal 401 of 601 and each `bench-trace-size` n = 5, 20, 50, 100, 187 is equal 101 of 151 (450 differing lines, all `raw` lines of
the `model_call` cases, none in `score` or `score_trace`). The basis for accepting it is the maintainer's (by delegation) ruling (A),
the entry headed "2026-10-05 23:51:14 BST — RL-1423 Condition B STOP (SL-1436 replay): (A) ACCEPTED ON CONDITIONS (the cause PROVEN
first); a LOW FD; the overlap disclosure accepted" in `to-lead.md`, whose decision, verbatim: "DECISION: (A), ACCEPT, as the
consequence of the context passing through the handler (RL-1423 N2), ON TWO CONDITIONS before SL-1436's mint:" — the two conditions are
the cause experiment and the downstream-reader check above, both run.

## PRs

#1228, draft, opened 2026-10-06 from branch `sl-1436-fd-1425-to-wire-dependency-order` (gate head `e0e2ff20`; the
ledger commits after it are docs only). Not merged; the merge is the lead's.

## Closing note (2026-10-06, the mint; `document-ids.md` §1.6's closing acts, performed by the executor per `executor.md`)

Minted as `LG-1467` (working id 9482); status `closed`; the roadmap `SL-1436` row `closed`. Basis: the slice audit
(`gi-pricing-plan.local/handover/audit-sl1436-2026-10-06.md`, local, not in the repository, head audited `669d5526`,
range `origin/main...669d5526`) and Acceptance 11's three-file test, run at the merge head `8a6fb56b9b04fe69ba9ce95b81dc38ecf18ac9a6`
(`origin/main` `a9ef6777` merged in; `git merge-tree --write-tree` rc 1, conflict in `docs/INDEX.md` only, regenerated):

```text
OMP_NUM_THREADS=1 nice -n 10 uv run pytest packages/pricing-core/tests/test_testing.py packages/pricing-core/tests/test_replay.py packages/pricing-core/tests/test_testing_determinism.py -q
49 passed in 43.30s
```

Both slots (`/tmp/slots/gate-1`, `gate-2`) read free by the probe immediately before the run; no assert edited.

The audit's findings, by id, quoted from its proposed-findings list:

- **F-A** — "Commit 318a16ce rewrote the end of LG 9482 and deleted \"The trial merges before the gate\" section." **Restored at `a0ad36be`** (section "The trial merges", above).
- **F-B** — "Acceptance 11 is not met as written (LOW, documentary)." The replay script is inline above with its sha256 `b43d213cdd4bae7c3b6d100933ba85875421ae15925a5eccde56832ecf71cfea`; the 450 differing lines are accepted by the 23:51:14 ruling (A); the three-file test's totals are the 49 passed above.
- **F-C** — "the LOW finding the ruling asks an auditor to file" (the zen custom-node return path cuts floats to 15 significant digits) became **FD 9480, PR #1229**.
- **F-D** — "Ledger front matter `tree:` is the base 23af6997, not the head" (informational); and "the ledger itself says the executor did not compare the 13 failures with a known set": **compared by the lead — identical, by test name, to the known check-31 set recorded at LG-1444 :289-293.**

## The minted-head gate (2026-10-06, head `b0aca122c7903cb24081c84cad98cdebb8888543`)

**Why it ran.** The mint-head gate waiver's condition (a) failed: `e0e2ff20..b0aca122` brings 22 non-docs paths (S7's code, #1121's `uv.lock`, #1232) through `origin/main`, so the earlier gate at `e0e2ff20` does not cover this head. The lead's "GATE SLOT GRANTED gate-1" for this head was given first (S-13). Before the run: `uv sync --all-packages`; the worktree's test database `gipricing_sl-1436_d9698591` dropped and recreated from the template, then `alembic upgrade head` (S-14).

**Run.** The verbatim gate body of `.claude/skills/dev-commands`, run in the foreground under its slot wrapper (the lead granted gate-1; the wrapper takes the first free slot and I did not record which it took), `timeout 3600`, scratch and `TMPDIR` under `/home`. Started 2026-10-06T02:27:17Z, ended 02:56:48Z (UTC); wrapper exit 0.

| stage | result |
|---|---|
| ruff | pass (exit 0) |
| mypy | pass (exit 0) |
| import_linter | pass (exit 0) |
| audit_docs | pass (exit 0); the 13 earlier check-31 reds are gone |
| req_coverage | pass (exit 0) |
| contracts | pass (exit 0) |
| pytest | pass (exit 0): `5064 passed, 4 skipped, 87 warnings in 1750.18s (0:29:10)` |

Frontend half: `pnpm --dir frontend` install `--frozen-lockfile`, `generate:api`, lint, type-check, test and build, each rc 0 (the build prints only the chunk-size warning). The worktree was clean after the run. The earlier run's 13 failures were the known check-31 set; this run has none.
