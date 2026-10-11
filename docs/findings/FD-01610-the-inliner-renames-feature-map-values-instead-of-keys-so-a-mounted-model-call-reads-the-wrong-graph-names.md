---
id: FD-1610
family: finding
title: The fragment inliner renames feature_map VALUES (model features) instead of KEYS (graph names), so a mounted model_call can read the wrong graph names
status: active
created: 2026-10-11
owner: auditor
tree: 99f22479
corrected_by: []
relates: [WK-1178, FD-1374, RL-1571, SL-1541, FR-222, FR-239, FR-246]
---

# FD-1610 — the inliner renames `feature_map` VALUES, not KEYS

**Minted 2026-10-11 from a working id, in the D10 batch.** Drafted in the D10 docs batch, at the maintainer's ruling (`to-lead.md`, "2026-10-10 23:46:57 BST —
RULING (mispricing): the inliner renames feature_map KEYS, never values — option (A), fixed INSIDE SL-1541; 03
:943 corrected by dated line; an FD at D10; the exposure query owed before SL-1541's ACK", item 5) and its
severity text per "2026-10-11 10:35:30 BST — READ-IN OK …", item 3. Every line number is at `origin/main`
`99f22479`, read for this record (not the lead's relay).

## Finding

`feature_map` on a `model_call` step maps **graph name → model feature slug**. FR-222 (`03` :110) refuses "a
`feature_map` value that is neither one of that Model's required inputs … nor the column its spec declares as
the offset", so the VALUES are model features and the KEYS are graph names. The runtime reads it the same way:
`runtime.py:754-758` builds `{feature_slug: context[graph_name] for graph_name, feature_slug in
step.feature_map.items() if graph_name in context}`.

The fragment inliner (`packages/pricing-core/src/pricing_core/rating/inline.py`) reads it the other way round:

- `:118` collects `step.feature_map.values()` as the fragment's names (the names to namespace).
- `:152-154` renames `{feature: mapping.get(name, name) for feature, name in step.feature_map.items()}`, that
  is, the VALUES.

So at a mount, a KEY naming a mapped input port, or an internal fragment name, is not renamed to the parent
name or to `<mount_point>__<name>`; a VALUE (a model feature slug) that happens to equal a fragment name is.
`03` :943 (`RL-1571`) states the same inversion: names are renamed "in every field that holds one (… the
values of `clamp_bounds` and `feature_map`)". The spec line and the inliner share the error, against FR-222 and
the runtime.

## Evidence

The code and spec lines above, read at `99f22479`, and the entries cited in the header. The severity reasoning follows.

## Why it is HIGH, and why it is latent

**Severity HIGH, proposed by the auditor** (the maintainer expects HIGH): a wrong `feature_map` key feeds the
model a wrong or absent feature, which is a wrong premium and not an error.

**Latent, no live exposure.** Mounting merged in `#1263`; the exposure query owed before SL-1541's ACK
(to-lead 23:46:57 item 4) was reported at 0 (to-lead 10:35:30 item 3). SL-1541 carries the fix and discharges
this finding.

**How it surfaced, and what that says about the silent case** (the maintainer's text, to-lead 10:35:30 item 3).
On `main` the defect surfaced as a **compile refusal** via FD-1374's reads guard
(`compile.py:_check_declared_reads`, code `RATING_STEP_UNDECLARED_READ`, `referenced_names` including the
`feature_map` keys at `references.py`) wherever a mounted `model_call` key was unread: the unrenamed key is not
in the renamed `consumes`. So a **silent** mispricing needs a key that guard does not catch. I did not construct
such a case; the claim here is the bound, not a demonstrated mispricing. The base red in SL-1541 was that
refusal rather than a premium inequality (10:35:30 item 3).

## Remedy (ruled)

Option (A) of the 23:46:57 ruling: the inliner renames `feature_map` KEYS by token and never touches values;
`:118` collects KEYS; `03` :943 gains a dated correcting line (the old words struck, not deleted). Fixed
**inside SL-1541** (write set += `inline.py`, `test_rating_inline.py`), red-first on base. Option (B), a
pre-inlining check, was rejected: it would pass a bundle the runtime misprices.

## Second limb — recorded, not decided (23:46:57 item 5)

The runtime's silent drop, `if graph_name in context` (`runtime.py:757`): a `model_call` whose key is not in
the scoring context scores with that feature **absent**, with no error. That is the hazard class of this
finding. Should a `model_call` with an unmapped key refuse at scoring? A runtime change must not reprice an
existing bundle, so each option carries the FR-239 check.

FR-239 (`03` :138, amended 2026-10-04, RL-1379) bars recompiling a non-`draft` Rating Version, so a stored
`approved` or `live` bundle can never be re-compiled under a new rule: any rule that is to reach it must be
enforced in the **runtime** or accepted as not reaching it.

| Option | What it does | FR-239 check |
|---|---|---|
| (a) Leave the drop | Status quo; SL-1541's post-inlining compile check is the only guard. | Reprices nothing. A stored bundle with an unmapped key keeps scoring with the feature absent. |
| (b) Refuse at scoring, any unmapped key | `graph_name not in context` raises a coded, input-free scoring error. | Changes a stored bundle's result from a price to a refusal. Needs the exposure query first: every stored Rating Version whose `model_call` keys exceed what its context can hold. 0 hits means no stored bundle changes. |
| (c) Refuse at scoring only when the key feeds a required model input | As (b), narrowed to the coverage the compile check already enforces. | Same query, a smaller set; a stored bundle is affected only if it already violated the compile rule. |
| (d) Record, do not refuse | Add the dropped keys to the trace. | Reprices nothing; the price is unchanged and the omission becomes visible. |

The choice is the maintainer's through the lead; this record does not pick one.

## Disposition

**Owner: WK-1178**, discharged by SL-1541. Decision: `fix before close with an owner: SL-1541`. Second limb:
open, event that next confirms or discharges it: the lead's ruling on options (a) to (d). Filed by the auditor,
2026-10-11; the lead gives the verdict.
