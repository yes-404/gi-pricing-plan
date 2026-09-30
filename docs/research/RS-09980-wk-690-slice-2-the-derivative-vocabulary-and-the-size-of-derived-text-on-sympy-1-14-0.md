---
id: RS-9980
family: research
kind: spike
title: WK-690 Slice 2 — the derivative vocabulary and the size of derived text on sympy 1.14.0 (DP-S2-7)
status: active
created: 2026-09-30
owner: executor
tree: 71b672205f7212008d0ff00b5cbc4810b56f12e6
phase: P2
work: WK-690
corrected_by: []
relates: [PL-1327, RL-1328, RL-1291]
---

# RS-9980 — The derivative vocabulary and the size of derived text

## Question

PL-1327 DP-S2-7: which function heads do first and second derivatives of the ten objective-profile functions carry, and how large (in `ast.expr` nodes and depth, RL-1291's predicate) is derived text against its loss? The answer sets `DERIVED_LIMITS`.

## Method

`library-spike` shape, on the locked `sympy==1.14.0` (`uv run`, real-valued symbols as RL-1293). Scratch scripts, not committed: `spike.py` (sha256 prefix `f13d2472095379f9`) and `printer.py` (prefix `10d6760957b39d2d`, the first form of the Task 2 printer). Each loss is differentiated twice in `f`, lifted with `piecewise_fold`, printed in the objective grammar with `sign`, `Heaviside` and `DiracDelta` rewritten (RL-1328 DP-S2-2), and measured by `measure_expression`. The constructed worst cases are a nested-`exp` loss and a nested-`where` loss, each built to fit the 200-node / depth-20 loss limits, and a 19-deep `log1p` chain.

## Findings

Heads, gradient / hessian: `abs` → `sign` / `DiracDelta`; `min`, `max`, `clip` → `Heaviside` / `DiracDelta` (plus `Heaviside` for a nonlinear argument); `where` → `Piecewise`; `exp`, `expm1` → `exp`; `log`, `sqrt`, `log1p` → no new head. `Heaviside(0) = 1/2`. This agrees with RL-1328's spike.

Size, nodes / depth:

| loss | loss | gradient | hessian |
|---|---|---|---|
| §4.6 example | 19 / 6 | 41 / 7 | 61 / 8 |
| `abs(y - f)` | 7 / 4 | 26 / 8 | 1 / 1 |
| `clip(f, 0, y)` | 7 / 3 | 25 / 7 | 1 / 1 |
| `max(y, f) * where(f < y, 2, 3)` | 14 / 4 | 37 / 8 | 1 / 1 |
| nested `exp` | 161 / 20 | 87 / 13 | 505 / 18 |
| nested `where` | 193 / 18 | 11 / 4 | 11 / 4 |
| 19-deep `log1p` chain | 39 / 20 | 474 / 22 | 9081 / 40 |

The maximum derived size is 9081 nodes at depth 40. `max(nodes_hess / nodes_loss)` is 232.8 and `max(depth_hess / depth_loss)` is 2.33. Without common-subexpression elimination the chain rule's repeated factors multiply. The Task 1 rule (maxima × 2, rounded up to 100 nodes and 10 depth) gives `ExpressionLimits(max_nodes=18200, max_depth=80)`. The result is conclusive, so the 2000 / 200 fallback of DP-S2-7 does not apply; it would refuse a 39-node loss.

Limit of the corpus: the test-suite losses named by the plan's grep are all small; the table's constructed cases carry the maxima.
