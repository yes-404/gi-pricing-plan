# WK-668 spike resolution — zen-engine 0.53.0, S1/S2 re-verification

Re-run of the S1 and S2 verification suites against the installed engine, per
`docs/plans/PL-00817-wk-668-implementation-plan-spike-s1-s2-resolution-and-adr-706-confirmation.md` T1-T4. Version pinned: `zen-engine` 0.53.0
(cp312 manylinux wheel), fetched without pip per the `library-spike` procedure. The wheel
has no runtime dependencies; the importable package is `zen`.

## T1 — installation

- Wheel: `zen_engine-0.53.0-cp312-cp312-manylinux_2_28_x86_64.whl`, pinned to 0.53.0
  (the S1 spike's version; no delta).
- Import verified: `import zen` succeeds; `ZenEngine`, `evaluate_expression`,
  `compile_expression`, `validate_expression` present.

## T2 — S1 verification (FR-273/274/275/276)

All checks run through `zen.evaluate_expression` / `zen.compile_expression` on the
installed engine. 21 checks, 0 failed.

### Exactness — confirms FR-273's premise (engine arithmetic is exact)

| Check | Measured | Result |
|---|---|---|
| `0.1 + 0.2 == 0.3` | `True` | PASS |
| `1.005 * 100 == 100.5` | `100.5` | PASS |
| `2.675 * 100 == 267.5` | `267.5` | PASS |

### Binding — confirms FR-273 (no decimal type at the boundary)

| Check | Measured | Result |
|---|---|---|
| Decimal passed as a context value | `TypeError: argument 'ctx': unsupported type Decimal` | PASS |
| `Decimal("1.005")` as an expression | `RuntimeError: parserError` (no such function) | PASS |
| `1/3` returns a Python float | `0.33333333333333337` (float) | PASS |
| `36120 + 7` returns a Python float | `36127.0` (float) | PASS |

### Division — confirms FR-274 (division by zero returns null, raises only on use)

| Check | Measured | Result |
|---|---|---|
| `1/0` | `None` | PASS |
| `0/0` | `None` | PASS |
| `premium/0` | `None` | PASS |
| `(1/0) + 5` (used null) | `RuntimeError: vmError — Opcode Add: Unsupported type` | PASS |

### Vocabulary — confirms FR-276 (validated against the engine)

| Check | Measured | Result |
|---|---|---|
| `log(x)` | `RuntimeError: parserError` | PASS (fails to parse) |
| `sqrt(x)` | `RuntimeError: parserError` | PASS (fails to parse) |
| `min(a, b)` two-argument | `RuntimeError: compilerError — Invalid function call min` | PASS (rejected) |
| `max(a, b)` two-argument | `RuntimeError: compilerError — Invalid function call max` | PASS (rejected) |
| `abs(-3)` | `3.0` | PASS (accepted) |
| `round(1.5)` | `2.0` | PASS (accepted) |
| `floor(1.7)` | `1.0` | PASS (accepted) |
| `ceil(1.2)` | `2.0` | PASS (accepted) |
| `sum([1, 2, 3])` | `6.0` | PASS (accepted) |

### Scale cap — confirms FR-275 (decimal scale capped at 28)

| Check | Measured | Result |
|---|---|---|
| `(1/3) * 3 == 1` | `False` | PASS (repeated division loses exactness inside the engine) |

**FR-273/274/275/276: all confirmed by the re-run.**

## T4 — S2 latency verification (NFR-502/501)

Measurement: a 500-tree x 60-feature XGBoost booster (3.4.1) scoring a single row,
1000 iterations, `perf_counter`, p99 at the tail. The booster's `nthread` parameter was
switched between 1 and all-cores (-1).

### NFR-501 — `nthread=1` per request — CONFIRMED

| Case | p99 | max | median |
|---|---|---|---|
| nthread=1 (incl. DMatrix) | **1.626 ms** | 6.143 ms | 0.421 ms |
| all-cores (incl. DMatrix) | 4.737 ms | 26.692 ms | 0.425 ms |
| predict-only (nthread=1) | 0.308 ms | 0.572 ms | 0.075 ms |

- nthread=1 p99 is **0.34x** of all-cores at the tail (single-threading beats all-cores).
- p99 1.626 ms is **3.3 %** of the 50 ms budget (NFR-501 / OQ-615) — PASS.
- Matches the original S2 order (1.09 ms p99); the machine this run measured is slightly
  slower on DMatrix construction.

### NFR-502 — no `response_model` on the hot path — rule confirmed, premise not reproduced

The scoring endpoint is Phase 2 and not yet built, so no code applies `response_model` to
it today; the rule is confirmed as stated for the Phase 2 slice. The requirement's
justification — "Pydantic validation costs roughly 1 ms per request" — is **not reproduced**
on this machine: a realistic `ScoringResult` shape (premium, 20 rate steps, 60 factors,
metadata) validates and serialises at **p99 0.070 ms** (0.14 % of the 50 ms budget).
The design rule (validate inbound, never outbound; encode with `ORJSONResponse`) stands
regardless — outbound validation is pure overhead — but the 1 ms figure the requirement
cites is higher than this machine measures, and the decision-maker should weigh that in T3.

## Version and method

- Engine: `zen-engine` 0.53.0 (cp312, manylinux_2_28 x86_64), wheel fetched from PyPI,
  extracted to a local libs dir, imported via `PYTHONPATH`.
- Booster: xgboost 3.4.1, 2000 synthetic rows x 60 features, `reg:squarederror`,
  `tree_method=hist`, 500 rounds, trained with `nthread=1`.
- Timing: `time.perf_counter`, 1000 iterations, p99 = the 990th sorted value.
- Tree: the `w8-spike-resolution` branch off origin/main at `737823f`.
