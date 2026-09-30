---
id: FD-9966
family: finding
title: FR-275's intermediate precision limb is not met at runtime, because the ZEN engine silently rounds its own intermediates at 28–29 significant digits
status: active
created: 2026-09-30
owner: auditor
tree: 25ca36df89b0ac6e97a14cb08ca2b07f54fef085
corrected_by: []
relates: [WK-1178]
---

# FD-9966 — FR-275's intermediate precision limb is not met at runtime, because the ZEN engine silently rounds its own intermediates at 28–29 significant digits

## Finding

**Severity: low.** FR-275 (`docs/specs/03-rating-engine.md:224`) says bundle compilation
*"checks that no rate table value, constant, or intermediate requires a decimal scale beyond
`rust_decimal`'s limit of 28, and fails with a named error rather than allowing a silent loss of
precision deep in a ladder"*. The **intermediate** limb is not met, and cannot be met by a
compile-time check as worded: an intermediate is a run-time value, and the ZEN engine rounds it
silently when it runs. A product whose exact value has more than 29 significant digits comes
back rounded to 29, with no error.

The compile-time check that exists covers the other two limbs of the sentence: `_check_scale_cap`
(`packages/pricing-core/src/pricing_core/rating/compile.py:199-222`) refuses a decimal *literal*
with more than 28 places (`EXPRESSION_SCALE_OVERFLOW`) and an input bound with a scale above 28.
It never sees an intermediate.

The effect is about 10⁻²⁸ relative, so the money impact is nil at any realistic quote size.
What is wrong is the requirement's wording, which promises a failure the platform cannot deliver.

## Evidence

Measured at `origin/main` `25ca36df89b0ac6e97a14cb08ca2b07f54fef085`, under the repository
`.venv`, whose `zen-engine` is **0.53.0**, the version locked by `packages/pricing-core/pyproject.toml:64`
(`"zen-engine==0.53.0"`) and `uv.lock`.

**The source of the finding.** The decision-maker's ruling for DP-S3-5 (working id 9963, local
commit `48621365`, not pushed at the time of filing) found it while building the exact-replay
ladder: *"The engine rounds its own intermediates at 28–29 significant digits. The eighth
product has 30 digits exactly, and the engine returned 29 digits"*, and *"The 'intermediate' limb
of FR-275 is not met at runtime … compilation cannot see runtime values. The effect is about 10⁻²⁸
relative, and this ruling tolerates it. The requirement's wording is a separate question."* This
record adds the wording question, and reproduces the measurement on its own.

**Reproduction.** A real ZEN graph: one `expressionNode` computing the product from two decimal
literals, then a second `expressionNode` reading it with the engine's `string()` so the exact
engine value is visible, compared with Python's `Decimal` at 100 digits of precision. The script
is scratch, outside the repository (sha256 prefix `f5509f17288b08cd`); its two probes are:

```
p = 12345678901234567890.123456789 * 1.000000000123456789    (product with 47 significant digits)
q = 12345678901234567890.123456789 * 1.5                      (product with exactly 30 significant digits)
```

Output, verbatim:

```text
zen-engine 0.53.0
exact product      : 12345678902758725765.294924676517146788750190521 (47 significant digits)
engine string(a*b) : 12345678902758725765.294924677 (29 significant digits)
absolute difference: 4.82853211249809479E-10 | relative: 3.911e-29
exact 30-digit     : 18518518351851851835.1851851835 (30 significant digits)
engine string(a*b) : 18518518351851851835.185185184 (29 significant digits)
```

So a 30-digit exact product `…835.1851851835` comes back as `…835.185185184`, and a 47-digit
product comes back at 29 digits. Neither raised. Each literal has at most 18 decimal places, so
`_check_scale_cap` (which refuses more than 28) passes both expressions.

**A literal that does exceed the scale is refused, loudly, by the engine.** `1.5 * 2.00000000000000000000000000001`
(a literal with 29 places) fails at evaluation with a `NodeError`, not silently. This is the
behaviour the compile check anticipates for literals. It is *not* what happens to a computed
intermediate.

**What was not measured.** The finding is about the engine's `string()` view of a value. This
record did not trace how much of the rounding survives in the engine's numeric result, or
through the binding in `score.py`. RL working id 9963's sweeps (42 000 quotes per run) are the
evidence for the size of the effect on ladders.

## Disposition

**Deferred with an owner: WK-1178.** Event that discharges it: FR-275's text corrected by a
dated amendment (`spec-change`, as `CLAUDE.md` §0 and §5 require), or a code guard the decision-maker
finds cheap enough to make the current wording true.

**Routing.** The maintainer's decision, by delegation, in the lead's channel file (the entry
headed *"2026-09-30 16:16:06 BST — DP-S3-5 ruled (RL 9963, local 48621365): accepted in
substance pending auditor-plans; routing of the 4 observed items"*, item (2)): a new finding,
LOW, owner WK-1178.

**Direction, from the same entry.** The likely resolution is **the spec overclaiming the
engine**. This is a `CLAUDE.md` §0 disagreement, where the spec is the side to correct: state the
engine's real intermediate precision, and cite RL working id 9963's tolerance, a **1e-26
relative per-rung tolerance** with an exact chained replay, unless the decision-maker finds a
cheap code guard.

**What a correct FR-275 says, for the amendment's author to decide.**
- The compile-time limbs stay: no rate table value, constant, literal or bound beyond scale 28,
  with a named error (`EXPRESSION_SCALE_OVERFLOW`).
- The intermediate limb is restated as the engine's real behaviour: intermediates are held to
  28–29 significant digits and are rounded silently beyond that, at about 10⁻²⁸ relative, and
  the platform's reconciliation tolerates 1e-26 relative per rung.
- The S1 sentence *"`(1/3) * 3 == 1` evaluates `false`"* is the same limitation seen from the
  other side, and can stay as its example.

*Drafted under working id 9966.*
