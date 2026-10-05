---
id: FD-9709
family: finding
title: The pseudo_huber template certifies `failed` on the platform default grid at delta 100 and above, because its loss cancels catastrophically and the derivative check's noise floor does not model that
status: active
created: 2026-10-05
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-690, LG-1412, FR-143, FR-146, FR-149, FR-151]
---

# FD 9709 (working id) — pseudo_huber certifies `failed` at large delta (WK-690)

## Finding

**Severity MEDIUM, owner WK-690, no deadline ruled.** The maintainer's (by delegation) entry "2026-10-05 13:10:43 BST — Early
severity signals for FD 9708 and FD 9709 (final at mint)" (`channel/to-lead.md`, local) says: "FD 9709 (#1129,
pseudo_huber certifies `failed` at δ ≥ 100 on the default grid): MEDIUM, owner WK-690, as proposed. A false
`failed` blocks a valid objective but misprices nothing. The draft states the δ at which it first fails,
measured, and the reproduce command." The entry is an early signal, final at the mint. The template catalogue is
`pricing-core`'s (`objectives.py`); the platform grid is `platform/objectives.py`.

**First failing δ, measured: 63** (an integer: `delta` is money in minor units and the schema refuses a
non-integer, `CLAUDE.md` §7). The failure is **not monotone in δ**. Every integer δ from 1 to 100, on the default
grid at the tree named under Evidence 3, gives `failed` at 63, 64, 73, 74, 78, 83, 84, 86, 87, 89, 93, 94, 97, 99
and 100, and not `failed` at the other 85 values; the gradient check is `pass` at δ = 1 and `warn` at every other
δ that does not fail. A bisect would have said 99 and was therefore wrong; the scan is what the table below
samples. Reproduce command: Evidence 3.

`LG-1412`'s note flags the symptom and names no check and no cause. Quoted from
`docs/ledgers/LG-01412-wk-690-slice-3-the-expression-kind-through-the-platform-behind-the-flag.md`,
§"FD 9780 — (f) the six templates that certify `violated`": *"Note: `pseudo_huber` with `delta`
100, 1000 and 100000 certified `failed` on the default grid (a draft, not `violated`), so
`delta=1` is used; a point for the FD batch."*

**It reproduces at `origin/main` `caa4e411`, and only on the platform's default grid.** The
certification is `pricing_core.modelling.objectives.certify_objective`, called with
`app.platform.objectives.default_sampling(objective)` (2000 points, `y ∈ [0, 1e6]`,
`f ∈ [-5, 15]`, `w ∈ [0.01, 10]`, seed 20260818), over `test_objectives.py`'s `_objective`
with `T.PSEUDO_HUBER` and `params={"delta": d}`. No database.

| delta | `overall` | `analytic_vs_numeric_gradient` | `analytic_vs_numeric_hessian` | `convexity` |
|---|---|---|---|---|
| 1 | `certified_with_findings` | pass (4.7e-08) | pass (2.9e-12) | violated (73.6%) |
| 100 | **`failed`** | **failed (1.78e-03)** | pass | violated |
| 1000 | **`failed`** | **failed (5.98e-02)** | pass | violated |
| 100000 | **`failed`** | **failed (1)** | pass | violated |

Every other check passes at all four values. On `test_objectives.py`'s own grid
(`_sampling`: `y ∈ [1, 1e6]`, `f ∈ [8, 14]`, 1000 points) the same four deltas certify
`certified_with_findings` (gradient pass, 3.4e-12 to 9.9e-09; hessian `warn` at delta 100,
1.6e-06). So **the failure is grid-dependent**, and the suite's grid does not see it.

## Why: a numerical-precision failure of the loss, not a wrong derivative

The failing check is `analytic_vs_numeric_gradient` (`objectives.py:1164-1169`): it differences
the **loss** (`_richardson(lambda fs: fns.loss(y, fs, w), f, _STEP)`) and compares the result
with the analytic gradient. The template's loss is `_pseudo_huber_loss` (`objectives.py:372-374`):
`delta**2 * (s - 1.0)`, `s = sqrt(1 + (r/delta)²)`. Where `|r| ≪ delta`, `s` rounds to
`1 + k·1e-16` and `s − 1` loses its digits (catastrophic cancellation); `delta²` then multiplies
the rounding error. At delta = 1e5 the loss carries an absolute error of order `delta²·eps ≈
2e-6` where the true loss is of order `r²/2`, tiny for small `y` near `mu`.

**The analytic derivative is right; the loss evaluation is the unstable part.** I
re-differenced the algebraically identical, cancellation-free form `r² / (s + 1)` on the same
grid and step and compared it with the same analytic gradient. At delta 100000 the worst three
points of the shipped loss are `y=0.04866, f=-3.191` (analytic −3.098e-04, numeric +1.85e-03,
relative error 6.97), `y=0.07504, f=-3.456` (2.35) and `y=0.5115, f=-4.884` (1.49); the stable
form agrees at those points to 3.7e-12, 3.5e-12 and 1.6e-11. Over the whole grid the stable
form's maximum is 2.2e-04 at delta 100000, a `warn` band (`_TOLERANCE_PASS` 1e-6 to
`_TOLERANCE_WARN` 1e-3, `objectives.py:103-104`), against the shipped 1. The numeric value
`+1.85e-03` is the same at all three bad points: a noise floor, not a slope.

**Why `_agreement` does not absorb it.** `_agreement` (`objectives.py:1079-1109`) subtracts a
noise of `8·eps·|loss|/h`, the `magnitude` argument being the loss itself. That models the
cancellation of the *finite difference*. It does not model the error in the loss *evaluation*,
which for this formula is `delta²·eps`, independent of `|loss|` and, at small `|r|`, far larger
than `eps·|loss|`. FR-149's tolerance is step-aware, not formula-aware, and this formula is
where the difference shows. A smaller residue remains with the stable form (delta 100,
`y ≈ 9e5`, `f ≈ -4.6`: 1.5e-04, a `warn`); it is not analysed here.

## What `failed` means, and what it does downstream

`02-modelling.md` §4.7 (`:1114-1117`): *"`overall` ∈ `certified` | `certified_with_findings` |
`failed`. A `failed` certificate blocks submission entirely."* The dated amendments fix the
meaning: a `violated` check yields `certified_with_findings` and **never** `failed` (Amendment to
FR-152, 2026-08-25, `:236-238`); `CheckStatus` is `pass | warn | violated | failed` and
`overall` is derived by `CertificateResult.outcome_of`, any `failed` ⇒ `failed`
(`:1147-1152`). So `failed` is **not** "the certification could not complete": all nine checks
ran. One of them, derivative agreement (FR-151), exceeded `_TOLERANCE_WARN`.

Downstream, `backend/src/app/platform/objectives.py`:

```
655:    failed = result.overall is CertificateOutcome.FAILED
656:    row.status = (ObjectiveStatus.DRAFT if failed else ObjectiveStatus.CERTIFIED).value
657:    row.certificate_id = None if failed else certificate.id
```

and `submit_for_review` (`:707-714`):

```
    if current is ObjectiveStatus.DRAFT:
        raise PlatformError(
            "OBJECTIVE_NOT_CERTIFIED", "This objective has no passing certificate", 409, …
```

So a `pseudo_huber` objective at delta ≥ 100 certified on the default grid **cannot be submitted
or approved**: it stays `draft`, the certificate is recorded with `certificate_id` cleared, and
submit is 409 `OBJECTIVE_NOT_CERTIFIED`. The platform blocks correctly in the sense that its
gate does what FR-146 says; what is wrong is that the block rests on a correct analytic
derivative over a loss formula that rounds. Deltas of this size are the realistic range for a
severity in minor units (`test_objectives.py` `_PARAMS` uses `delta=100_000`), so the template
is unusable in the range it exists for, on the default grid.

## Requirement

- **FR-143** (`02-modelling.md:207`): templates carry analytic gradients and hessians
  "implemented and unit-tested in `pricing-core`". The derivatives are correct; the loss is not
  numerically sound over the platform's certified domain, and `test_every_template_certifies`
  uses a grid on which it passes. This is a quality finding, so MEDIUM, not a clause breach.
- **FR-149** (`:213`): tolerances are step-aware; the loss-evaluation error term is the
  missing one (the noise model was corrected once already, `:1176-1183`).
- **FR-146 / FR-151**: the gate works as written; here it blocks a correct objective.

## Proposed remedy (a proposal, not a decision)

1. Evaluate `_pseudo_huber_loss` as `r² / (s + 1)`; re-run this table; expect `warn` or `pass`.
2. Add `pseudo_huber` at delta 100 000 on `default_sampling`'s grid to the certification tests,
   red first; the suite's own grid is why the defect was invisible.
3. For the decision-maker: should `_agreement` add a loss-evaluation error term so any template
   with a cancelling form is judged on what the method can resolve? Not decided here.

## Evidence

1. Run at `caa4e411a9c07a389cf47092a923c7761b2b92dc` after `uv sync --all-packages`: a short
   script calling `certify_objective(_objective(T.PSEUDO_HUBER, params={"delta": d}),
   sampling=default_sampling(o))` for d in 1, 100, 1000, 100000; the table is its output. The
   same with `_sampling(T.PSEUDO_HUBER)` gives the second set of figures.
2. The stable-form comparison: `r²/(s+1)` Richardson-differenced on the same grid
   (`h = 1e-4`) against `_pseudo_huber_grad`; figures above.
3. **First failing δ and the reproduce command.** Saved as `repro.py` anywhere, run from the repository root
   (`uv run python repro.py`; about 5 s per δ on one thread, so pin `OMP_NUM_THREADS=1` on a shared box). It
   prints, for each integer δ asked, whether `overall` is `failed` and the gradient check's status. The scan of
   1..100 is `for d in range(1, 101): print(d, *run(d)[:2])`. Run at `origin/main`
   `809a3794af6d3a6ba688663b0d9b59f951190680` (the sources of `objectives.py` and `platform/objectives.py` are
   unchanged since `caa4e411`, `git diff --stat caa4e411 origin/main` on both is empty), 2026-10-05.

   ```python
   from uuid import uuid4

   from app.platform.objectives import default_sampling
   from model_schema import (TEMPLATE_APPLICABILITY, CertificateOutcome, CustomObjective,
                             HessianStrategy, ObjectiveTemplate)
   from pricing_core.modelling import certify_objective

   T = ObjectiveTemplate.PSEUDO_HUBER


   def run(delta):
       o = CustomObjective(id=uuid4(), slug="repro-pseudo-huber", version=1, template=T,
                           params={"delta": delta}, applicability=TEMPLATE_APPLICABILITY[T],
                           hessian_strategy=HessianStrategy.CLIP_TO_MIN)
       r = certify_objective(o, sampling=default_sampling(o))
       g = next(c for c in r.checks if c.name == "analytic_vs_numeric_gradient")
       return r.overall is CertificateOutcome.FAILED, g.status.value, g.detail
   ```

4. Code: `objectives.py:372-374`, `:1079-1109`, `:1153-1200`, `:103-104`;
   `platform/objectives.py:588-619` (`default_sampling`), `:655-657`, `:707-714`.

## Disposition

Open. Filed by the auditor, 2026-10-05, on the lead's relay of `LG-1412`'s note; severity and
owner are proposals. The verdict is the lead's; the severity is the maintainer's (by delegation) at the mint.
