---
id: PL-8162
family: plan
kind: map
title: WK-1178 — FD-1723's residual "Fix in P2" limbs. The GLM families and the GLM direction diagnostic (FR-110, FR-89), the test-only limbs (FR-33, FR-80, FR-41, FR-123, FR-7, FR-14, FR-15) and the dated clauses (FR-6, FR-109) — a dated Work-plan delta
status: active                 # draft → active → superseded | retired (§1.2a) — activated 2026-10-22 by L1 in slice C's PR (SL-8164); all five DPs ruled in "2026-10-22 16:02:49 BST"
created: 2026-10-22            # filed under working id 8162
owner: planner
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1733, SL-1734, PL-1735, SL-1736, FD-1723, FR-6, FR-7, FR-14, FR-15, FR-33, FR-41, FR-80, FR-89, FR-109, FR-110, FR-123]
---

# PL-8162 — WK-1178: FD-1723's residual "Fix in P2" limbs (a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: one plan per Work, slices as rows, no per-slice leaf; a change
> is one dated delta, a new `PL-` that `relates:` the Work's plan). WK-1178 has no Work plan, so,
> as `PL-1733` did, this delta `relates:` the records it builds on: `PL-1733` and `SL-1734` (FD-1723's
> HIGH limbs, merged), and `PL-1735` and `SL-1736` (the P2 NFR sweep, which keeps NFR-467). It cuts
> **five slice rows**, A to E, below. REQUIRED SUB-SKILL: subagent-driven-development (recommended)
> or executing-plans, task by task; steps use checkbox (`- [ ]`) syntax. Each executor also binds:
> - `test-driven-development`: every red is seen red **by its cause** before the code that turns it
>   green; for a test-only limb, the named mutation is the red (see "Test-only limbs" below);
> - `python-test`: the `req` marker on every new test, and the negative tests;
> - `python-package`: `pricing-core` stays standalone (ADR-703);
> - `spec-change`: every task headed "spec" (spec first, `CLAUDE.md` §0);
> - `contract-schema` and `contract-guard`: slice A's model-schema change;
> - `vue-frontend`: slice A's builder input only (the generated client is never hand-written);
> - `dev-commands`: `uv sync --all-packages`, `scripts/run-small.sh` for one-file runs, the DB window
>   of the maintainer's standing pre-approval (a), and both gate halves;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. Each executor is
> spawned from `.claude/roles/executor.md`.

Filed under **working id 8162**, reserved by the lead for this seat (brief
`handover/brief-planner-1723-2026-10-22.md`, written 2026-10-22 15:51:11 BST by lead 26). **The
five slice rows have no working ids yet**: this draft names them slice A to slice E, and the lead
reserves an `SL-` working id for each it activates (see "Hand-off"). Written 2026-10-22 by the
planner (seat planner-1723). **Tree read:** `origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`
(#1358, committed 2026-10-21T22:37:56+01:00). Every `file:line` below is at that tree unless marked
otherwise; each executor re-reads its own at its base (Task 0 of its slice).

## Authority

Read in full in `~/gi-pricing-plan.local/channel/to-lead.md` on 2026-10-22 between 15:52 and 15:58 BST.

- **"2026-10-22 15:50:37 BST — Maintainer: the HIGH-finding triage: GO for the FD-close batch, GO
  for the FD-1723 PL delta planner; SL-1771 HOLD confirmed"**, item 2, verbatim:
  > **GO: a planner (opus) for the WK-1178 PL delta** on FD-1723's residual "Fix in P2" limbs:
  > - (a) FR-110/FR-89: red-first glum family-name translation, the declared θ and the GLM direction diagnostic;
  > - (b) FR-33/80/41/123: test-only;
  > - (c) FR-6/109/7/14/15: dated spec clauses.
  > **FR-110's `power(k)` option:** the planner lays out the options, trade-offs and one recommendation in the PL, and I rule at the PL's review. It does not wait on me to start.
- **"2026-10-14 11:28:56 BST — FD 8027 severity → HIGH (the max of its limbs), per-limb table
  kept; …"**, the lines this plan applies, verbatim:
  > - FR-110's glum spellings ("negative.binomial", "inverse.gaussian") giving a misdirecting GLM_FIT_FAILED are part of the fix.
  > - **NB theta: NOT defaulted silently.** The spec declares none, so the fix slice puts it as a DP (declared parameter with a stated default and its recording, or estimated) for a decision-maker. glum's 1.0 is never adopted by omission.
  > - **power(k): BUILD if glum supports a power link natively** (Task 0 verifies it in the pinned glum version and cites it); otherwise STRIKE it from FR-110 by a dated amendment with that reason. Not left in the spec unbuilt.
  >
  > **LOW limbs:** fixed in P2 where small (FR-33, 80, 123, NFR-467's measurement joins the P2 NFR sweep); else carried with owner at §14.
  > **Owners at §14:** FR-6 UI half, FR-109, FR-127 spliced/excess (refused loudly today, so deferral is safe).
- **"2026-10-14 13:55:54 BST — FD 8027 FR-7/14/15 limbs: severities ADOPTED; …; two test designs
  CORRECTED so they can fail"**, as FD-1723 quotes it (its italic note after the table, read in the
  FD at this tree): FR-7 MEDIUM, test from the spec and the declared lifecycles, not from the
  `audit.record(` call sites; FR-14 LOW, the inverse check (no frontend code reaches the API except
  through the client); FR-15 LOW, the timezone check over `Base.metadata.tables` plus the
  rating-version boundary test, red on a planted naive column.
- **"2026-10-22 15:43:10 BST — Maintainer: SPEED MEASURES …"**, items 1(a) and 3: per-worktree DB
  test windows are pre-approved on the template (at most 3 files per run, redis db 11–13, `dropdb`),
  and the build seat writes its red and green summary lines verbatim into the LG before any audit,
  the test set derived by import closure.
- **FD-1723** (`docs/findings/FD-01723-…`, read whole at this tree, its per-id table and every dated
  ruling under it). **The slice cut follows the triage outline** `handover/planner-fd-triage-2026-10-22.md`
  §5 (planner-fd, read-only at `f3462d8f`), verified here against the code. Where it differed from
  the primary source, the primary source governs, and the difference is stated where it applies
  (DP-C, DP-F14, the NB deviance).

## Two readings this plan does not settle (raised, not picked)

1. **Item (c) groups FR-7, FR-14 and FR-15 under "dated spec clauses"; FD-1723's adopted
   dispositions for those three are tests** (the 13:55:54 entry: *"Fix in P2, test only"* for FR-7
   and FR-15, *"Fix in P2 where small"* with a red-on-a-planted-call check for FR-14). A dated
   clause that narrows them to the clause already proved would contradict the later, limb-specific
   design the maintainer (by delegation) corrected *"so they can fail"*. This is **DP-C**; the plan cuts
   the tests (slices D and E) and recommends that reading.
2. **FR-14's adopted design rests on a premise this tree does not bear out.** The 13:55:54 entry
   calls *"every path the generated client calls is in the published document"* **true by
   construction**. At this tree the client is not generated: `frontend/src/api/client.ts:4-12` is a
   hand-written transport (*"It knows **no** data shapes"*), and every API module passes it a
   **hand-written path literal**, e.g. `frontend/src/api/datasets.ts:37`
   `` request<Dataset>(`/datasets/${encodeURIComponent(slug)}`) ``. Predicate:
   `git -C <wt> grep -c -E "request(<[^(]*>)?\(" -- 'frontend/src/api/*.ts'`, summed → **81** call
   lines at `f3462d8f` (a call split across lines before its `(` escapes it; slice E's test
   closes that hole). So the path check **can** fail today, and the adopted inverse check
   (no raw `fetch(` or `axios` outside the transport) passes by construction: the census
   `git -C <wt> grep -n -E "\bfetch\(|axios" -- frontend/src ':!frontend/src/api/generated'`
   outside `__tests__` finds the transport's own `fetch(` (`client.ts:68`) and nothing else. This is
   **DP-F14**.

## Goal

Every limb of FD-1723 that a ruling sends to "Fix in P2" under WK-1178 and that no merged slice or
open plan carries ends with one of: a fix proved red first, a test proved able to fail (by a named
mutation), or a dated spec clause. After the five slices merge, FD-1723's close condition (every
limb fixed, accepted with a dated clause, or carried with a named owner) depends only on the limbs
outside WK-1178: NFR-467 (SL-1736), and the §14 owners for FR-6's UI half, FR-109's
finer-level view and FR-127 `spliced`/`excess`.

| limb | FD severity | slice | deliverable |
|---|---|---|---|
| FR-110 | MEDIUM | A | glum family-name translation; a declared NB θ (DP-T); the NB deviance; the whole `family` literal fitted; `power(k)` per DP-K |
| FR-89 | MEDIUM | A | the GLM direction check, reported in `GlmDiagnostics` (DP-M) |
| FR-41 | MEDIUM | B | test only: the stored recipe replayed over the same source bytes gives the same table hashes |
| FR-33 | LOW | B | test only: a failed run releases its `Idempotency-Key` |
| FR-80 | LOW | B | test only: an Auditor reads an archived version over the API; a Model on it still resolves |
| FR-123 | LOW | B | test only: a constrained booster has no cross-group split and differs from the unconstrained one |
| FR-6 | MEDIUM | C | dated clause in `00` stating what is built; the shared object and the UI half carried to §14 |
| FR-109 | LOW | C | dated clause in `02`, accept with reason; the finer-level view carried to §14 |
| FR-7 | MEDIUM | D (DP-C) | test only: every declared governed transition emits its Audit Event in the same transaction |
| FR-14 | LOW | E (DP-C, DP-F14) | test only: every client path is an operation of the published document; no raw call |
| FR-15 | LOW | E (DP-C) | test only: every `DateTime` column is `timezone=True`; a rating version's interval is half-open |

Not here: FR-100, FR-127 GLM and FR-127 EBM (`SL-1734`, merged per the triage, `2bc4dc8c` #1331);
NFR-467 (`SL-1736`, `PL-1735`); FR-127 `spliced`/`excess` (the §14 owner).

## Evidence at `f3462d8f` (the owning code, read)

**FR-110.** `docs/specs/02-modelling.md:129`: seven families and the links `log`, `logit`,
`identity`, `inverse`, `power(k)`. The note at `:130-141` already records `power(k)` as *"declared and
unbuilt — `GlmSpec` has no spelling for it"*. `GlmSpec.family` is the seven-member literal and
`link` the four-member one (`packages/model-schema/src/model_schema/modelling.py:1117-1122`);
`family_params: dict[str, float]` is read only for `"power"` (`:1179`, `:1296`).
`fit_glm` passes `spec.family` to glum unchanged except for Tweedie
(`packages/pricing-core/src/pricing_core/modelling/glm.py:620-633`, then `:641` and `:646`), and
translates only `inverse` (`:614`). A glum `ValueError` becomes `GLM_FIT_FAILED` with a message
about the response's domain (`:680-707`): the misdirection the ruling names.

**glum, probed here** (the `tools-main` venv, glum **3.4.1**; `OMP_NUM_THREADS=1 nice -n 19`,
read-only, at 2026-10-22 ~15:55 BST). `glum._glm.get_family`: `negative.binomial`,
`inverse.gaussian`, `normal` and `gaussian` resolve; **`negative_binomial` and `inverse_gaussian`
raise** `The family must be an instance of class ExponentialDispersionModel or an element …`.
`NegativeBinomialDistribution().theta` is `1.0`, and its docstring defines the unit variance as
**`v(μ) = μ + θ·μ²`**: glum's θ is the NB2 dispersion, the **reciprocal** of the `theta` (size) that
R's `MASS::glm.nb` reports. `glum._link` exports `CloglogLink`, `IdentityLink`, `Link`, `LogLink`,
`LogitLink` and `TweedieLink`; there is **no `PowerLink`** and no `"power"` link string.
`TweedieLink(p)` is `μ^(1−p)` (`log` at `p = 1`); its setter raises
`ValueError("For `0<p<1`, no distribution exists.")` and **casts a float power to `np.float32`**
(`TweedieLink(1-(-1/3)).power` → `1.3333334`, type `numpy.float32`); an `int` power is kept exact.

**The NB deviance is the Poisson deviance.** `unit_deviance`
(`packages/pricing-core/src/pricing_core/modelling/diagnostics.py:142-190`) takes `family` and
`power` only, and its first branch is `if family in {"poisson", "negative_binomial"}:` (`:166`). So
once an NB GLM fits, every deviance-based number about it (the diagnostics' deviance, the CV
selection at `glm.py:346`, the backtest's family via `_family_of`, `diagnostics.py:736-756`) is the
Poisson deviance, θ ignored: silent wrong evidence, the FR-127 class. It is unreachable on `main`
only because NB cannot fit. **Slice A fixes it in the same commit as the translation**, never after.
Call-site census for Task A0:
`git -C <wt> grep -n -E "unit_deviance\(|[^_]deviance\(" -- packages/pricing-core/src backend/src`
→ **14** lines at `f3462d8f`.

**The builder offers NB.** `frontend/src/api/modelSpecs.ts:39-41` lists `FAMILIES` (NB included)
and `LINKS` (four), pinned to the generated types; `frontend/src/views/ModelSpecBuilderView.vue:143`
sends `family_params: { power }` for Tweedie only. Under DP-T (a) an NB spec from the builder is
refused at POST until the builder sends θ.

**FR-89.** `02-modelling.md:92`: the direction is *"checked (not enforced) for GLMs, where a
violation is reported as a diagnostic"*. `git -C <wt> grep -n -i monoton -- packages/pricing-core/src/pricing_core/modelling/glm.py`
→ none. The GBM check is `compute_gbm_diagnostics`'s sweep loop
(`diagnostics.py:1371-1431`): successive mean predictions in the sweep's axis order, `worst =
max(0, max(against))`, `holds = worst <= 1e-9`, into `MonotonicityCheck`
(`packages/model-schema/src/model_schema/diagnostics.py:493-509`). `GlmDiagnostics` (`:253-277`)
has no monotonicity field; `compute_diagnostics` builds it at
`packages/pricing-core/src/pricing_core/modelling/diagnostics.py:723-732`. FR-178 (`02:275`) is the
omission precedent: a skip that only the source states is the silence the omission records exist to
end.

**FR-41.** `ingest` applies the recipe during ingestion and stores the steps on the version
(`backend/src/app/data/ingestion.py:169-183`, `:236-240`); each table is stored by
`_store_table` as a blob ref (`:310-330`). No test re-ingests the same bytes with the stored recipe
and compares the stored tables (FD-1723's FR-41 row; `packages/pricing-core/tests/test_prepare.py:280`,
`:322` are in-memory).

**FR-33.** The only run row is written `status="succeeded"` (`ingestion.py:249-255`); `_find_run`
(`:289`) can therefore never hand back a failure. The existing tests (`backend/tests/test_ingestion.py:181`,
`:205`) cover reuse on success and a new version on changed data.

**FR-80.** `backend/tests/test_lineage.py:470-491` reads the archived **row** through a DB session
and asserts its status only; `:494-511` proves the refusal to fit.

**FR-123.** `packages/pricing-core/tests/test_gbm.py:642`, `:657`: an unknown feature is refused and a
declared group reaches both backends; no test shows a forbidden interaction forbidden.

**FR-7.** Declared lifecycles: `git -C <wt> grep -n -E "VALID_.*TRANSITIONS\s*[:=]" -- backend/src packages`
→ **8** maps at `f3462d8f` (approvals `:83`, datasets `:86`, jobs `:118`, metrics `:62`, modelling
`:2089`, objectives `:161`, perils `:120`, rating `:57`, each in `packages/model-schema/src/model_schema/`).
Which are **governed Artifacts** is `00` §2's to say (slice D, Task D0).

**FR-15.** The one marked test is `backend/tests/test_api_reference.py:120` (reference data only).
Rating-version effective dating is served at `backend/src/app/platform/rating_versions.py:146`.

**In flight at this tree** (`git diff --name-only $(git merge-base origin/main origin/<b>) origin/<b>`,
read 2026-10-22 ~15:56 BST): `sl-1260-wk674-s6` @`7b9f2684` writes `backend/src/app/db/models.py`,
`docs/contracts/openapi/generated.json` and four generated schemas, and `model_schema/__init__.py`;
`sl-1551-wk675-s8` @`04b632b5` writes `generated.json`, `model_schema/__init__.py` and
`frontend/src/api/dislocationRuns.ts`; `sl-1554-wk675-s9` @`beae0dff` adds
`frontend/src/api/subGraphs.ts`; `sl-1736-wk1178-nfr-sweep` @`40d4ac28` writes
`docs/specs/01-data-management.md` and `scripts/measure-*`; `sl-1711-wk674-wf701-demo` @`be830a88`
and `fix/fd-1838-switch-namespace` @`b95c9d3d` touch none of this plan's write sets. Every branch
writes `docs/roadmap.md`.

## Decision points

All five are for the maintainer (by delegation) at this plan's review; DP-K is named for the
maintainer's own ruling in the 15:50:37 entry. The plan is `draft` until each is ruled.

### DP-K — `power(k)` (FR-110): build, part-build, or strike

The rule already given (11:28:56): *"BUILD if glum supports a power link natively … otherwise
STRIKE it from FR-110 by a dated amendment with that reason."* The probe above is the Task 0 the
rule asks for, run now so the ruling can be made at review. Its answer is **partly**: glum has no
power link by name, but `TweedieLink(1−k)` computes `μ^k` for every `k` outside `(0, 1)`.

| option | what it is | for | against |
|---|---|---|---|
| **(i) Strike** (recommended) | A dated amendment to FR-110 strikes `power(k)`, with the probe as the reason; the `:130-141` note is closed by it. | Exactly the rule's "otherwise" limb. No shape change, no contract regeneration, no scoring change. The useful members of the family are already named: `identity` (k = 1), `inverse` (k = −1) and `log` (the k → 0 limit). | Drops a link the spec promised. A future need (e.g. `1/μ²`, the canonical inverse-Gaussian link) is a new requirement. |
| (ii) Part-build, integer `k` outside `(0, 1)` | `link: "power"` plus a declared integer `k`; fit with `TweedieLink(1 − k)`; `predict._inverse_link` (`predict.py:70-88`) gains `μ = η^(1/k)`; a dated clause narrows FR-110 to that range. | Native in glum for that range; an `int` power avoids the float32 cast, so the fitted `k` is the declared one. | A model-schema shape change (link literal plus a parameter), a contract and generated-type regeneration, the builder's `LINKS` list and a `k` input, and a new arm in the **scoring** path, for a link no Work, workflow or demo uses. Excludes the square-root link (k = ½), the one power link a pricing actuary is most likely to ask for. |
| (iii) Full build, any real `k` | as (ii), with a pricing-core `Link` subclass for `0 < k < 1` and float `k` | The whole of FR-110 as written. | **Not native**, so outside the rule as given. Pricing-core then owns link arithmetic glum does not test. For a float `k` passed through `TweedieLink`, glum fits `float32(1 − k)` while `spec_hash` and the scorer use the float64 `k`, so fit and score can disagree in the seventh significant figure. |

**Recommendation: (i) strike**, because the native support is partial (no `k` in `(0, 1)`) and
lossy for a float `k` (the float32 cast). The rule gives "native" as the condition for building, and
a native build that silently changes the declared exponent is the FR-127 class this finding exists
for. Under (i), slice A's Task A2 writes the strike. Under (ii), slice A grows the shape change, the
`_inverse_link` arm, the builder input and their reds (an integer-`k` fit whose scorer reproduces
glum's predictions to `1e-10`; a `k` in `(0, 1)` refused by name), and its size moves from 3 to 4.

### DP-T — the negative-binomial θ

| option | for | against |
|---|---|---|
| **(a) Declared and required** (recommended): `family_params["theta"] > 0` is required when `family == "negative_binomial"` and refused on any other family; FR-110 states the NB2 form `v(μ) = μ + θ·μ²` | Small: a validator, no shape change (`family_params` is already `dict[str, float]`), and θ is in `spec_hash` because the spec is. Naming the variance form blocks the silent inversion of a θ copied from R's `glm.nb`. | The actuary must choose θ (in practice from a Poisson fit's over-dispersion, or from R). |
| (b) Declared with a stated default, materialised into the stored spec | Lets the builder default the field | Any default for over-dispersion is a modelling judgement with no neutral value; the 11:28:56 entry allows it only *"with its recording"*, and glum's 1.0 is the value it forbids by omission. |
| (c) Estimated by profile likelihood over a declared grid, as FR-114 does for the Tweedie power | The statistically complete answer | A new spec block, a diagnostics shape and a contract change; larger than the limb, which is MEDIUM. It can be specified later as its own requirement. |

**Recommendation: (a).** A θ on a non-NB family is refused because a declared parameter that is
silently ignored is the FR-127 class (the existing `power` key on a non-Tweedie family is left as it
is; that is not this limb).

### DP-M — what the GLM direction check reports for a factor it cannot sweep

The check follows the GBM rule (`diagnostics.py:1420-1431`): mean prediction over the training rows
with the factor held at each value of its axis, successive differences against the declared
direction, `holds = worst <= 1e-9`, and the result in a new `GlmDiagnostics.monotonicity:
tuple[MonotonicityCheck, ...] = ()`. Three kinds of factor have no ordered axis to sweep: an operand
of an interaction (FR-178), an `expression` factor (FR-178's 2026-10-16 amendment), and a factor whose
levels have no order (a grouping, or an identity factor over a text column, whose sweep axis is
ranked by exposure, not by value).

- **(a) Skip with no record**, as the GBM block does for its monotonicity check. Against it: the GBM
  skip is visible through the partial-dependence omission beside it; a GLM has no such block, so the
  skip would be stated only in the source.
- **(b) Record the skip** (recommended): `GlmDiagnostics.monotonicity_omitted:
  tuple[MonotonicityOmission, ...] = ()`, each with a reason from a new
  `MonotonicityOmissionReason` (`operand_of_interaction`, `expression_factor`, `unordered_levels`),
  defined once in model-schema, FR-178's own pattern. A declared direction then always produces a
  check or an omission, never nothing.

### DP-C — FR-7, FR-14 and FR-15: tests (D, E) or dated clauses

- **(i) Tests, as FD-1723's adopted dispositions say** (recommended): slices D and E below. The
  13:55:54 entry corrected the two test designs *"so they can fail"*; a clause cannot fail.
- (ii) Dated clauses in `00` narrowing each requirement to the clause already proved. The
  requirement then promises less than it did, while the parts it stopped promising (every
  transition audited, UTC everywhere) still describe how the platform is meant to behave.

If (ii) is ruled, slices D and E are not cut, and slice C's Task C2 gains the three clauses.

### DP-F14 — what FR-14's test checks

- **(a) Both** (recommended): (1) every `request(` call in `frontend/src/api/*.ts` has a method and a
  templated path that is an operation of `docs/contracts/openapi/generated.json`, with every call the
  parser cannot read counted and failed, so a multi-line call cannot escape; red on a planted
  misspelt path. (2) The adopted inverse check: no `fetch(`, `axios` or `/api/v1` literal outside
  `client.ts` in `frontend/src` (tests and `api/generated` excluded); red on a planted raw `fetch(`.
- (b) The adopted inverse check alone. At this tree it passes with nothing to fix, while 81
  hand-written paths stay unchecked against the document.

Where: a Python test in `backend/tests/test_contracts.py` (beside the FR-14 marker at `:216`), so
`req-coverage.py` sees the marker. A vitest file would hold the check closer to the code, but
req-coverage does not read the frontend.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree. "Red" means seen red **by the stated cause** at the slice's base, recorded verbatim in the
slice's LG before the fix (the 15:43:10 entry, item 3). For a test-only limb, "red" means the test
fails on the slice head with the named mutation applied (and not committed), and passes without it.

1. **This delta passes the docs checks on its branch.** At the branch head,
   `python3 scripts/audit-docs.py` prints no line naming this file except the working-id lines of
   checks 31 and 32 for 8162, and check 28 does not name it. After minting,
   `python3 scripts/audit-docs.py`, `python3 scripts/doc-index.py --check` and
   `python3 scripts/register-lint.py` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.
3. **Spec first, in every slice that changes behaviour or a spec.**
   `git log --reverse --format='%h %s' origin/main..<slice head> -- docs/specs/` shows the slice's spec
   commit before or with its first code commit, never after (A: `02` FR-110, FR-89 and the §4/§5
   diagnostics contract; C: `00` FR-6 and `02` FR-109).
4. **A. NB and inverse Gaussian fit (red A-R1).** A parametrised test over every member of
   `GlmSpec.family`'s literal, each fitted on data simulated from that family with its usual link,
   recovers the simulated coefficients within a stated tolerance. At the base, `negative_binomial`
   and `inverse_gaussian` fail with `GlmFitError` code `GLM_FIT_FAILED` and glum's *"The family must be
   an instance of class ExponentialDispersionModel"* in the message.
5. **A. θ is declared, never defaulted (red A-R2, DP-T (a)).** A `GlmSpec` with
   `family="negative_binomial"` and no `family_params["theta"]`, or `theta <= 0`, raises at
   construction; a `theta` on `family="poisson"` raises. At the base each reports *DID NOT RAISE*. An
   NB fit with `theta=0.5` and one with `theta=2.0` on the same data give different coefficients (the
   declared θ reaches glum).
6. **A. The NB deviance uses θ (red A-R3).** `unit_deviance(y, mu, family="negative_binomial", theta=0.5)`
   equals the closed form `2[y·log(y/μ) − (y + 1/θ)·log((1 + θy)/(1 + θμ))]` (the `y = 0` limit
   taken) to `1e-12`, and differs from the Poisson unit deviance on the same arrays. At the base
   the call raises `TypeError` (no `theta` parameter), and with the keyword removed the value equals
   Poisson's. Every one of Task A0's enumerated deviance call sites passes θ for an NB spec (the LG
   tables each).
7. **A. `power(k)` per DP-K.** Under (i): `grep -n 'power(k)' docs/specs/02-modelling.md` shows only
   the struck text and the dated amendment, and `GlmSpec.link`'s literal is unchanged. Under (ii):
   the reds named in DP-K.
8. **A. The GLM direction is checked (red A-R4).** A GLM fitted with an `increasing` banded factor
   whose simulated effect decreases yields `diagnostics.glm.monotonicity` with one entry, `holds is
   False` and `worst_violation > 0`. The same fit with an increasing effect yields `holds is True`.
   At the base, `GlmDiagnostics` has no `monotonicity` attribute (`AttributeError`). Under DP-M (b), a
   declared direction on an interaction operand yields a `monotonicity_omitted` entry with reason
   `operand_of_interaction`, and no `monotonicity` entry.
9. **A. One contract, one way.** `uv run python scripts/generate-contracts.py --check` exits 0 on the
   slice head, and `git diff --name-only origin/main...<slice head> -- docs/contracts frontend/src/api/generated`
   lists only generated files changed by that script (no hand edit; `frontend/src/api/generated`
   never committed).
10. **A. The builder sends θ.** In a single-file vitest run of the builder view's test (the
    maintainer's 13:34:04 guard), choosing `negative_binomial` shows a θ input, and the posted spec
    carries `family_params.theta`. Red at the base: the posted NB spec has no `theta`.
11. **B. FR-41 replay.** A DB test ingests bytes `B` with recipe `R` into one Dataset, then ingests `B`
    with the version's stored `derived_from["recipe"]` into a second Dataset, and asserts each stored
    table's blob content hash is equal across the two versions. Mutation: drop one step from the
    replayed recipe; the test fails on the hash. If the unmutated test is red, the limb becomes a
    defect: STOP to the lead (a new FD, re-rated), never a weakened assert.
12. **B. FR-33 release.** Ingest `B` with key `K` and a recipe that fails, so the call is refused;
    ingest `B` again with `K` and a recipe that succeeds; a version is created and `reused is False`.
    Mutation: write an `IngestionRunRow` with `status="failed"` before the refusal and have
    `_find_run` return it; the test fails.
13. **B. FR-80 over the API.** An Auditor `GET` of an archived Dataset Version returns 200 with
    status `archived`; a `GET` of a Model fitted on that version returns 200 and still names the
    version, which itself resolves. Mutation: filter `archived` out of the version read; the test
    fails.
14. **B. FR-123 forbids.** On data with a real cross-group interaction, for each backend
    (XGBoost, LightGBM), the booster fitted with `interaction_constraints` has no root-to-leaf path
    splitting on features of two different groups, and its holdout predictions differ from the
    unconstrained booster's. Mutation: drop the constraint before the backend call; the path
    assert fails.
15. **C. The clauses.** `git diff origin/main...<slice C head> -- docs/specs/00-overview.md docs/specs/02-modelling.md`
    shows one dated clause under FR-6 and one under FR-109, each naming its §14 carry (FR-6: the
    shared `provenance` object and the UI display; FR-109: the finer-level diagnostics view), and
    no other row changed. FR-6's clause cites Task C0's census verbatim.
16. **D. FR-7 (DP-C (i)).** A parametrised DB test with one case per declared governed transition
    (Task D0's list from `00` §2 and the declared transition maps, never from `audit.record(` sites)
    performs the transition through its public service or route and asserts an Audit Event with
    the expected `action` committed in the same transaction (a rollback of the transition leaves
    neither). Mutation: delete one transition's `audit.record(` call; that case fails. The call-site
    census (`git -C <wt> grep -n -E "audit\.record\(" -- backend/src`; **81** lines at `f3462d8f`, 79 at
    `854fb7d5` in FD-1723) is printed in the LG, and any site matching no declared transition is listed. A case red without a mutation is a defect: STOP
    to the lead.
17. **E. FR-15.** A test over `Base.metadata.tables` asserts every `DateTime` column has
    `timezone=True`; mutation: a planted naive `DateTime` column on a test-only table bound to that
    metadata fails it. A DB test asserts a rating version with `[from, to)` serves at `from` and not
    at `to`; mutation: `<=` for `<` at the effective-to comparison fails it.
18. **E. FR-14 (DP-F14 (a)).** The `test_contracts.py` test passes on the slice head; mutation: one
    planted misspelt path in a copy of an API module fails check (1), and one planted `fetch(` fails
    check (2). The count of `request(` calls parsed equals the count of `request(` tokens found, or
    the test fails.
19. **Every slice: closure-derived GREEN.** Each LG quotes its changed-module list, the import closure
    and the derived test-file list (seat brief item 29), and its gate's summary line.

## Global Constraints

- **`pricing-core` owns the fit and the diagnostics** (ADR-703; `CLAUDE.md` §2): a notebook calling
  `fit_glm` or `compute_diagnostics` gets the translation, θ, the NB deviance and the direction check,
  as the fit Job does.
- **One contract, one way** (`CLAUDE.md` §2). `MonotonicityCheck` is reused, never redefined; any new
  shape (`MonotonicityOmission`, its reason enum) is defined once in model-schema. `docs/contracts/`
  changes only through `scripts/generate-contracts.py`; `frontend/src/api/generated/` is regenerated,
  never committed or hand-written.
- **glum's 1.0 is never adopted by omission** (11:28:56). No code path supplies a θ the spec did not
  declare.
- **No change to `spec_hash`'s inputs or to a stored spec's meaning.** A stored NB spec without θ
  could not have been fitted (its fit raised), so DP-T (a) refuses only specs that never produced a
  model. Slice A's Task A0 confirms this with a read-only count of stored NB models
  (`select count(*) …` in its DB window); a non-zero count is a STOP to the lead.
- **A test-only limb that goes red unmutated is a defect, not a test to adjust** (seat brief item 13):
  STOP to the lead, who routes a new FD.
- **Money is untouched**; no float reaches a price.
- **The barred word.** Write "the maintainer (by delegation)".

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | **C** — FR-6 and FR-109 dated clauses (docs only) | Tasks C0 to C2 | `00` §3: FR-6; `02` §3.3: FR-109 | this delta minted; slice C's SL id reserved; may ride a docs batch | 1 |
| 2 | **A** — the GLM families (FR-110) and the GLM direction diagnostic (FR-89) | Tasks A0 to A7 | `02` §3.4: FR-110; `02` §3.1: FR-89; `02` FR-172 and FR-178 (the omission pattern, read); FR-114 and FR-115 read only | this delta minted; DP-K, DP-T and DP-M ruled; serialise the contract regeneration with SL-1260 and SL-1551 (below) | 3 (4 under DP-K (ii)) |
| 3 | **B** — FR-41, FR-33, FR-80, FR-123 tests | Tasks B0 to B3 | `01` §3.2: FR-41; `01` §3.1: FR-33; `01` §3.7: FR-80; `02` §3.5: FR-123 | this delta minted; a DB window (pre-approval (a)) | 2 |
| 4 | **D** — FR-7 transition audit test | Tasks D0 to D2 | `00` §3: FR-7; `06` read for each Audit Event's `action` | DP-C (i); SL-1260 merged (it adds routing and shadow lifecycles, which D0 must enumerate); a DB window | 3 |
| 5 | **E** — FR-15 and FR-14 tests | Tasks E0 to E3 | `00` §3: FR-15; `00` §3: FR-14 | DP-C (i), DP-F14 ruled; SL-1260 merged (its new `models.py` columns are in E's metadata walk); SL-1554 and SL-1551 merged or rebased past (their new API modules are in E's path walk) | 2 |

**Order and parallelism.** C, A and B can run beside one another: their write sets are disjoint
except `docs/specs/02-modelling.md` between C and A (different rows; the second to merge re-merges
`main`, a mechanical conflict at most). D and E wait on SL-1260. **Clashes with in-flight work:**
A regenerates `docs/contracts/openapi/generated.json` and the generated diagnostics and model-spec
schemas, which SL-1260 and SL-1551 also regenerate; whichever merges second **re-runs
`generate-contracts.py` after re-merging `main`**, never hand-merges a generated file. A may touch
`model_schema/__init__.py` (DP-M (b) exports), which SL-1260 and SL-1551 also edit: a re-merge, export
lines only. No slice here touches `deployment_switch.py` (fix-1838), `scripts/demo.py` or the WF-701
journey (SL-1711), the designer views (SL-1554), `scripts/measure-*` or `01-data-management.md`'s
NFR rows (SL-1736). Every slice adds its own row under `### WK-1178` in `docs/roadmap.md`: line
conflicts only.

### Slice C — FR-6 and FR-109 dated clauses

- [ ] **C0. Census (read-only).** For FR-6, list every governed Artifact shape in model-schema and
  whether it carries the id of the Job that produced it (field name, `file:line`). Predicate: each
  class named as an Artifact in `00` §2, read in its owning module, not a grep for `job_id`. Record
  the table in the LG.
- [ ] **C1. FR-6 clause (`spec-change`).** A dated amendment under FR-6 (`00:219`): what is built (the
  per-artifact producing-Job id, C0's table, each artifact without one named as a gap); what is not
  (the shared `provenance` object `{entity_type, entity_id, version, produced_by_job_id}` and any UI
  that reads it); the latter **carried to the §14 review** for an owner, per 11:28:56 *"Owners at
  §14: FR-6 UI half"*. The `CR-819:128` mis-citation (trace id, not provenance) is noted as corrected
  by FD-1723, not edited.
- [ ] **C2. FR-109 clause (`spec-change`).** A dated amendment under FR-109 (`02:123`): accepted with
  reason. The chain is stored (`parent_grouping_id`) and read by nothing; an actuary can already hold
  both levels as two Groupings and rate on one; the finer-level diagnostics view is **carried to the
  §14 review** for an owner (11:28:56).
- [ ] **C3.** audit-docs under the gate-2 flock; the LG; the roadmap row's status line.

### Slice A — the GLM families and the GLM direction diagnostic

- [ ] **A0. Re-read and enumerate.** Re-read every `file:line` in "Evidence" at the base. Re-run the
  glum probe in the slice venv and record the version (the pin must still be 3.4.1, else STOP).
  Enumerate the deviance call sites (the 14-line predicate) and sort each into "takes a GLM spec's
  family" or not. Count stored NB models (read-only, in the DB window). Read `to-lead.md` from
  "2026-10-22 15:50:37 BST" onward for anything on FD-1723, FR-110, FR-89 or this plan; name each
  entry in the LG.
- [ ] **A1. The reds, at the base.** Write A-R1 (`packages/pricing-core/tests/test_glm.py`, the
  parametrised whole-literal fit), A-R2 (`packages/model-schema/tests/` beside the GlmSpec tests, plus
  the θ-reaches-glum fit in `test_glm.py`), A-R3 (the NB unit deviance, in the diagnostics test file
  Task A0 names) and A-R4 (the GLM direction check). Run each through `run-small.sh`; record each
  red line verbatim in the LG. A red by any other cause is a plan defect: STOP.
- [ ] **A2. Spec (`spec-change`), before the code.** Under FR-110: the family translation (the spec
  spellings are the platform's; glum's are a boundary detail), θ per DP-T with the NB2 variance
  stated, the NB deviance, and `power(k)` per DP-K. Under FR-89: the GLM check's rule (axis, mean
  scale, `1e-9`), where it is reported, and DP-M's omission reasons. The §4 diagnostics data
  contract gains the new field(s).
- [ ] **A3. model-schema.** The θ validator on `GlmSpec`; `GlmDiagnostics.monotonicity` (and, under
  DP-M (b), `monotonicity_omitted`, `MonotonicityOmission`, `MonotonicityOmissionReason`). Regenerate
  contracts; run `generate:api`; the contract-guard comparisons per `contract-guard`.
- [ ] **A4. pricing-core, fit.** In `glm.py`, one translation at the glum boundary, applied before
  both the CV path and the final fit: `negative_binomial` → `NegativeBinomialDistribution(theta=θ)`,
  `inverse_gaussian` → `"inverse.gaussian"`. The `GLM_FIT_FAILED` message stays for genuine domain
  errors.
- [ ] **A5. pricing-core, deviance and diagnostics.** `unit_deviance` and `deviance` take
  `theta: float | None = None` and raise `ValueError` for NB without it; NB gets its own branch.
  `_family_of` and every GLM call site from A0 pass θ. The GLM direction check in
  `compute_diagnostics`, reusing the GBM sweep's axis helpers (`_resolved_axis`, `_weighted_levels`)
  with the GLM scorer, never a second axis rule.
- [ ] **A6. The builder (`vue-frontend`).** `ModelSpecBuilderView.vue` shows a θ input for
  `negative_binomial` and sends `family_params.theta`; its test (single file, the 13:34:04 guard).
- [ ] **A7. Green and close.** The reds green; ruff, mypy and the closure-derived test set; both gate
  halves (the frontend half is required: A changes the contract and a view). LG with red and green
  lines first, then the audit.

**Interfaces (A).** Produces: `unit_deviance(y, mu, *, family: str, power: float = 1.5, theta: float | None = None) -> NDArray[float64]`
and `deviance(..., theta: float | None = None)`; `GlmDiagnostics.monotonicity: tuple[MonotonicityCheck, ...]`;
under DP-M (b) `GlmDiagnostics.monotonicity_omitted: tuple[MonotonicityOmission, ...]`.

**Write set (A).** `packages/model-schema/src/model_schema/modelling.py` (validator only),
`.../diagnostics.py`, possibly `.../__init__.py`; `packages/pricing-core/src/pricing_core/modelling/glm.py`,
`.../diagnostics.py`; their tests; `docs/contracts/**` (generated); `docs/specs/02-modelling.md`;
`frontend/src/views/ModelSpecBuilderView.vue` and its test; the LG; the roadmap row. Under DP-K (ii)
also `predict.py`, `frontend/src/api/modelSpecs.ts` and its type test.

### Slice B — test-only limbs FR-41, FR-33, FR-80, FR-123

- [ ] **B0. Re-read** the Evidence lines at the base; name the blob ref's content-hash field read by
  B1 (`_store_table`, `ingestion.py:310-330`); read `to-lead.md` from 15:50:37 as in A0.
- [ ] **B1. DB tests**, one DB window (pre-approval (a); at most 3 files per run):
  `backend/tests/test_ingestion.py` (FR-41 replay, FR-33 release) and `backend/tests/test_lineage.py`
  (FR-80 over the API, as an Auditor). Each with its mutation, applied, run, recorded, reverted.
- [ ] **B2. pricing-core test** `packages/pricing-core/tests/test_gbm.py` (FR-123, both backends),
  through `run-small.sh`, with its mutation.
- [ ] **B3. Close.** Any test red unmutated: STOP (Global Constraints). Otherwise the LG with every
  red and green line, the gate, the audit.

**Write set (B).** The three test files, the LG, the roadmap row. No source file. A source change
appears only through a STOP and a ruling.

### Slice D — FR-7 (only under DP-C (i))

- [ ] **D0. Enumerate from the spec.** Every governed Artifact in `00` §2, its declared lifecycle
  (the transition maps, and `06`'s event table for each `action`), after SL-1260's merge. The LG
  tables Artifact → transition → expected `action` → the service or route that performs it. Print
  the `audit.record(` census and list the sites matching no declared transition.
- [ ] **D1. The test**, a new `backend/tests/test_audit_transitions.py`, one case per row of D0's
  table, plus the rollback leg. Mutation per Acceptance 16. Split into at most 3 files per run in the
  DB window.
- [ ] **D2. Close** as B3.

### Slice E — FR-15 and FR-14 (only under DP-C (i))

- [ ] **E0. Re-read** at a base that includes SL-1260, SL-1554 and SL-1551 (or record which have not
  merged); confirm the OpenAPI document's path prefix and how path parameters are spelt there.
- [ ] **E1. FR-15**: the metadata test (no DB) and the rating-version boundary test (DB), each with its
  mutation.
- [ ] **E2. FR-14**: the `test_contracts.py` test per DP-F14, with both mutations. Any existing call
  that fails check (1) at the base is a finding, listed in the LG and routed by the lead, never
  allow-listed by the executor.
- [ ] **E3. Close** as B3.

## Hand-off (not this plan's writes)

- **Ids.** The lead reserves an `SL-` working id for each slice it activates (C, A and B now; D and E
  after DP-C), and an `LG-` id per slice. This draft writes no `docs/roadmap.md` row because it has no
  slice id to write; the minter or the planner adds the rows at mint (`document-ids.md` §1.6 SL row).
  No INDEX hunk on this branch (brief, 5d).
- **§14 items** (the planner's review, not this plan): FR-6's shared object and UI half; FR-109's
  finer-level view; FR-127 `spliced`/`excess`. Each is a carry with an owner named there.
- **A process observation, not a finding:** the GBM monotonicity check's skip for interaction
  operands and expression factors is visible only through the partial-dependence omission beside it.
  If DP-M (b) is ruled, the lead may route the question of a GBM `monotonicity_omitted` to the
  process backlog.

## Self-review

- Every limb in FD-1723's table is accounted for once: A (FR-110, FR-89), B (FR-41, FR-33, FR-80,
  FR-123), C (FR-6, FR-109), D (FR-7), E (FR-14, FR-15), outside (FR-100, FR-127 GLM, FR-127 EBM,
  FR-127 `spliced`/`excess`, NFR-467). Sixteen limbs, sixteen placements.
- Every behaviour change has a red at the base by its cause (A-R1 to A-R4, the builder red); every
  test-only limb has a mutation (Acceptance 11 to 14, 16 to 18).
- The 15:50:37 entry's (a), (b) and (c) are each met; where (c) and the FD's adopted dispositions
  differ, the difference is DP-C, not a silent pick. `power(k)` has options, trade-offs and one
  recommendation (DP-K).
- The 11:28:56 constraints are applied where they bite: θ never defaulted by omission (Global
  Constraints, DP-T), the glum spellings in A4, `power(k)`'s native test in DP-K's evidence.
- A finding the triage did not carry (the NB deviance is Poisson's) is fixed in the slice that makes
  it reachable, in the same commit as the translation.
- Requirements are listed by id, never by range (Acceptance 2).
