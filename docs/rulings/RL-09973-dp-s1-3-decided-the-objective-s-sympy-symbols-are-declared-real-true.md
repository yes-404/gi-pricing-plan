---
id: RL-9973
family: ruling
title: DP-S1-3 decided — the objective's SymPy symbols are declared real=True
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 095dd400918348b32ee6eab1db7915faaa9dfe35
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1268, RL-1289]
---

# RL-9973 — DP-S1-3 decided: the objective's SymPy symbols are `real=True`

## How this was ruled

**Ruled at effort `medium`**, under the maintainer's pre-decision by delegation of
2026-09-30 08:48:15 BST (`to-lead.md`, entry headed "PRE-DECISION: the DM may rule
SL-1271's three DPs at MEDIUM effort, under the 08:00 basis, with an executable-evidence
condition"). It applies the 08:00 CHECKPOINT DECISION's basis. For this DP, the condition
reads: "`Abs` differentiated with and without `real=True`, showing the real-valued form
that the `02` §4.6 derivation requires".

**Working id 9973.** The id is minted at the merge turn, which the lead schedules.

## Verified first, at 095dd400918348b32ee6eab1db7915faaa9dfe35

- **The decision point.** DP-S1-3 of SL-1271's leaf plan (#954, working id 9960; read at `4d2e78e8` and re-checked at `6853c1b3`, `:277`) asks:
  "What SymPy assumptions do the objective symbols (`y`, `f`, `w`, parameters) carry?"
  - (a) `real=True`;
  - (b) none.
  - Recommendation: (a). The kind is "decision point: it fixes the canonical derived text".
- **What §4.6 needs.** FR-145 (`docs/specs/02-modelling.md:209`) admits `abs`. §4.6 says
  the `derived` block "is what a reviewer reads" and is "the **canonical** one SymPy
  produces" (`:1029-1030`). The §4.6 domains are real: `y_domain`, the raw score `f`, and
  the weight `w`.
- **The version.** `sympy==1.14.0` (`RL-1289`).

## Proof — executable, red on (b), green on (a)

**Where it ran.**
- Scratch venv: `uv venv -p 3.12` with `uv pip install sympy==1.14.0 pytest`, at
  `/home/puzhenhao1989/.claude/jobs/0081b83b/dm-sympy-cert/venv`. That gives
  sympy 1.14.0, mpmath 1.3.0 and Python 3.12.13. None of it is in the repository or its
  lock.
- Test file: `test_dp_s1_3_real_symbols.py` (sha256 prefix `76e173338d383f50`), not
  committed. Its deciding part:

```python
OPTIONS = {"a_real": {"real": True}, "b_none": {}}
# symbols y, f, w, w_under, w_over built with **OPTIONS[opt]; where(c,a,b) -> Piecewise((a,c),(b,True))

@pytest.mark.parametrize("opt", OPTIONS)
def test_abs_derivative_is_real_valued(opt):
    g = diff(sympify("w * abs(y - exp(f))"), f)
    assert not g.has(re, im, Derivative)
    assert simplify(g - (-w * exp(f) * sign(y - exp(f)))) == 0

@pytest.mark.parametrize("opt", OPTIONS)
def test_section_4_6_example_still_reproduced(opt):   # 02 §4.6's loss, gradient and hessian verbatim
    assert simplify(piecewise_fold(diff(LOSS, f) - GRAD)) == 0
    assert simplify(piecewise_fold(diff(LOSS, f, 2) - HESS)) == 0
```

**Commands and results** (2026-09-30 08:54:46 BST):

```text
$ $V/bin/python -m pytest -q -s -p no:cacheprovider test_dp_s1_3_real_symbols.py
a_real d/df w*|y-exp(f)| = -w*exp(f)*sign(y - exp(f))
b_none d/df w*|y-exp(f)| = w*((-exp(re(f))*sin(im(f)) + im(y))*(-exp(re(f))*sin(im(f))*Derivative(re(f), f) - exp(re(f))*cos(im(f))*Derivative(im(f), f)) + … 
FAILED test_dp_s1_3_real_symbols.py::test_abs_derivative_is_real_valued[b_none] - AssertionError: b_none: complex form w*((-exp(re(f))*sin(im(f)) + im(y))*(-...
1 failed, 3 passed in 0.80s                                   rc=1
$ $V/bin/python -m pytest -q -p no:cacheprovider test_dp_s1_3_real_symbols.py -k a_real
2 passed, 2 deselected in 0.62s                               rc=0
$ $V/bin/python -c "…diff(Abs(g), g) for a plain and a real symbol g"
plain: (re(g)*Derivative(re(g), g) + im(g)*Derivative(im(g), g))*sign(g)/g
real: sign(g)
```

**How to read it.**
- Without the assumption, the derivative of `abs` is complex-valued. It contains `re`, `im`
  and unevaluated `Derivative` terms, and that text would be the canonical `derived` text a
  reviewer reads and Slice 2 records.
- With `real=True` it is `-w*exp(f)*sign(y - exp(f))`, the real form §4.6 needs.
- §4.6's own example (a `where()` objective with no `abs`) is reproduced exactly under
  both options. The assumption therefore changes no existing derived text.

## Ruled

**(a). Every objective symbol — the bound symbols `y`, `f`, `w` and every declared
parameter — is created as `sympy.Symbol(name, real=True)`.** No other assumption is added.
`positive=True` for `w`, for example, is not ruled: it would change simplification output
beyond what this DP asked, and the domain bounds are the certificate's to check (§4.7).

**Why (a).**
- §4.6's domains are real. The canonical derived text must be readable by a reviewer.
- Without the assumption, one admitted function, `abs`, yields a complex expression. That
  expression is not the maths of the objective and would be recorded as its derivation.
- The proof shows the assumption does not disturb §4.6's example.

**Narrowness: narrow.**
- It fixes how Slice 1's SymPy translator builds symbols, inside `02` §4.6's derivation.
- No FR text, published contract or existing behaviour changes. No SymPy translator exists
  today, and §4.6's example output is unchanged (proof above).

## What it obliges

- **WK-690 Slice 1 (SL-1271's leaf plan, #954: Task 5 Step 4):**
  - builds every objective symbol with `real=True`;
  - carries the test below;
  - states the assumption in the `02` §4.6 amendment it already makes (the leaf plan's
    `:1218` note at `4d2e78e8`, "The symbols are real (DP-S1-3)"), citing this record.
- **Slice 2** inherits it for the recorded `derived` text. This commit edits no spec, plan
  or roadmap text.

## Acceptance — the violation that must become detectable

- *Violation: a symbol the objective translator produces has `is_real` not `True`.*
- *Violation: the derivative of an objective containing `abs` contains `re`, `im` or an
  unevaluated `Derivative`.* It must be red with the assumption removed.
- *Violation: §4.6's example gradient or hessian is no longer reproduced.*
