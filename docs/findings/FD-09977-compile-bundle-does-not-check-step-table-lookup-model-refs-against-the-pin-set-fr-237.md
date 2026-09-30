---
id: FD-9977
family: finding
title: compile_bundle does not check step table, lookup and model refs against the pin set (FR-237)
status: active
created: 2026-09-30
owner: auditor
tree: eeda8f4ba20d247ac18d6a35d7f81589c8527ed2
corrected_by: []
relates: [WK-1250, WK-1178, FR-237, FD-1241]
---

# FD-9977 — `compile_bundle` does not check step table, lookup and model refs against the pin set

## Finding

**Severity: high**, in force on the maintainer's decision (see *Severity*). **Proposed by the auditor;
the disposition is the lead's.** FD-9977 is a working id, minted at the records PR.

FR-237 (`03-rating-engine.md:134`) says a Rating Version pins "an exact Rate Table Version per
referenced table, an exact Model/Peril Structure version per `model_call`, an exact Reference Table
Version per `lookup`, and the input contract. **Nothing is unpinned.**" At `origin/main`
`eeda8f4ba20d247ac18d6a35d7f81589c8527ed2`, `compile_bundle`
(`packages/pricing-core/src/pricing_core/rating/compile.py:425`) never compares the refs the
algorithm's steps name (`RatingTableStep.rate_table_ref`, `RatingLookupStep.reference_table_ref`,
`RatingModelCallStep.model_ref` / `peril_structure_ref`) with the version's pin set. It resolves and
maturity-checks whatever the **pins** list, and builds the wire graph from the payloads that produced.
A step whose ref is absent from the pins, or present at **another version**, compiles without a word.

Three defects, one missing check:
1. **No pin-membership check at compile** (the class). A table, lookup or model step can name an
   artifact that no pin covers, or that a pin covers at another version.
2. **A silent wrong price.** When the step's output is consumed by a null-tolerant expression, the run
   does not stop: it is **quoted, with no decline reason and no warning, at a wrong premium** (−9.1%
   and −23.1% in the two independent reproductions below; a wrong-version pin prices 1370 where the
   right answer is 2740). Table steps are exposed as well as lookups.
3. **The model path fails uncoded.** At score, `payloads[ref_str]` raises a bare `KeyError`
   (`runtime.py:463` in the model-call handler, `:533` in the booster loader), where every refusal in
   this engine is meant to be a `CodedError`.

Raised by the high-effort decision-maker while ruling #938 (working id 9851), and reproduced by
auditor-922 and, independently, by auditor-933. **The auditor who filed this did not run the price
reproductions itself: tables 1 to 3 below are the two auditors' own results, relayed by the lead and
reproduced here as they reported them.** The code read and the data read are the filer's own.

## Evidence

### 1. The code, read at `eeda8f4b`

- **`compile.py:425-492`.** `compile_bundle` requires `algorithm_ref` and `pins` (`:434-443`),
  resolves the algorithm, runs `validate_algorithm(algorithm)` (`:461`, defined at `:261`, which takes
  **the algorithm only**) and `check_model_reference_mode(version, algorithm)` (`:464`;
  `model_schema/rating.py:171`, which compares each step's `mode` with the version's
  `model_reference_mode` and nothing else). It then builds `all_refs` from **the pins alone**
  (`:467-472`: `rate_tables`, `models`, `reference_tables`, `custom_objectives`), resolves each, and
  stores `payloads[str(ref)]`. No line reads a step's ref and looks it up in `pins`.
- **`runtime.py:190-262`, `_decision_table_node`.** For a `table` step it reads `payloads.get(ref)` and,
  when absent, builds a `decisionTableNode` with no inputs and no rules; its docstring calls that "a
  not-yet-hydrated graph is not this function's failure to report", a rule written for a
  structural-only `to_wire` call that a compiled bundle then inherits. A `lookup` step does the same
  with `_reference_rows(payloads.get(ref))` (`runtime.py:233-243`; `_reference_rows(None)` returns `[]`).
  An empty decision table produces **no output key at all**; the next step reads the key as null.
- **`runtime.py:463` and `:533`.** `payload = payloads[ref_str]` and
  `payloads[ref_str].get("fit_result", {})` raise `KeyError` for a `model_call` whose ref is not a
  pinned payload.
- **The test that covers FR-237.** `test_rating_compile_bundle.py:146`
  (`test_an_unpinned_version_is_refused`) sets `algorithm_ref` to `None`: a **missing algorithm ref**,
  not a step ref outside the pin set. No test in `packages/pricing-core/tests` or `backend/tests`
  covers an unpinned or wrong-version step ref (auditor-922's search, 2 irrelevant hits).
- **`_check_vocabulary` (`compile.py:233`)** accepts whatever ZEN compiles. `03` does not specify the
  `??` operator, only FR-244's `coalesce(a, b)` (`03:146`). Recorded as an observation only (see *Related,
  not part of this fix*).

### 2. Reproduction by auditor-922 (at `eeda8f4b`, reported verbatim)

Fixture base `test_rating_score.py`, row `driver_age` 34, `distribution_channel` direct; refs
`rate_table:motor-expense@1` and `model:motor-freq@1`; a v2 table with direct 2.0 and broker 3.0.

**Table 1 — table and model steps** (these fail loudly; no premium is produced):

| Case | Pins | Compile | Score |
|---|---|---|---|
| Control: step and pins at v1 | table@1, model@1 | OK | quoted, `payable_premium_minor` = **1507** (ladder 1305, 1436, 1436, 1507, 1507) |
| Wrong-version table: step @1, pin @2 | table@2 only | OK | `CodedError RATE_TABLE_MISS`, no premium |
| Wrong-version model: step @1, pin @2 | model@2 only | OK | `KeyError 'model:motor-freq@1'`, no premium |
| Unpinned table (`on_miss` error or default) | no table | OK | `CodedError RATE_TABLE_MISS` |
| Both table v1 and v2 pinned | table@1 and table@2 | OK | quoted, 1507 (the v1 pin is used; the extra v2 pin is ignored) |

**Table 2 — lookup through tolerant consumers** (`s_expense` replaced by a lookup,
`reference_table:expense@1`, direct → "1.1", broker → "1.25", `on_miss="default"`; same row; always
quoted, no decline reasons, no warning):

| Case | `s_office` expression | Ref pins | Compile | Score |
|---|---|---|---|---|
| Control: numeric lookup pinned | `risk_premium_minor * number(expense_factor)` | expense@1 | OK | **1507** (ladder 1305, 1436, 1436, 1507, 1507) |
| Same, lookup unpinned | same | none | OK | `RuntimeError NodeError` on `s_office`, no price |
| (a) `??`, pinned | `risk_premium_minor * number(expense_factor ?? "1.0")` | expense@1 | OK | 1507 |
| **(a) `??`, lookup UNPINNED** | same | none | OK | **quoted 1370** (ladder 1305, 1305, 1305, 1370, 1370): **−137 minor, −9.1%, silent** |
| **(a) `??`, WRONG VERSION: step @1, pin @2 only** | same | expense@2 | OK | **1370**; the correct v2 price (factor 2.0) is **2740** |
| Wrong-version control: step @2, pin @2 | `number(x)` | expense@2 | OK | 2740 (ladder 1305, 2610, 2610, 2740, 2740) |
| Wrong version, no `??`: step @1, pin @2 | `number(x)` | expense@2 | OK | `RuntimeError` on `s_office`, no price |
| Wrong version, no `??`: step @2, pin @1 | `number(x)` | expense@1 | OK | `RuntimeError` on `s_office`, no price |

**Table step through a tolerant consumer (auditor-922, additions of the same day).** Table step,
`on_miss="default"`, `s_office` = `risk_premium_minor * (expense_factor ?? 1.0)`, rate table **unpinned**:
compile OK; **quoted, 1370 against 1507 pinned** with the same expression, silently. With `on_miss="error"` the
step raises `CodedError RATE_TABLE_MISS`; without `??` it raises `RuntimeError NodeError` on `s_office`. A
`model_call` unpinned or at the wrong version raises the bare `KeyError` for **any** consumer, so no silent price.

**Other consumers of the missing value:**
- **(b) constraint step.** `clamp_bounds.min = number(expense_factor ?? "0") * 1000`: pinned 1507;
  unpinned with the `??` in `s_office` gives 1370. The constraint tolerates the missing value; it is
  not an independent mechanism.
- **(b2) decline condition** `office_premium_minor <= sanity_cap_minor and expense_factor != "0"`:
  pinned 1507; unpinned with the `??` gives **1370, quoted, no decline**, because `null != "0"` is true.
- **(c) sub-graph port.** Not evaluable today (`score.py:399-401`: the engine never evaluates `sub_graphs`).
- **Wire level.** An unpinned lookup with `on_miss="default"` gives a decision table with **0 rules** and
  an output with **no key at all**, with no error; pinned gives 1 rule and `{'area_code': 'LDN'}`.

*Caveats reported by auditor-922:* its first pinned-lookup control also raised `REFERENCE_LOOKUP_MISS`
because a lookup emits a string and its expression multiplied it (an invalid control, replaced by
`number(expense_factor)`); one earlier table row was mislabelled (the algorithm was not edited) and
duplicates the wrong-version row.

### 3. Independent reproduction by auditor-933 (reported by the lead)

Its own algorithm: `base_minor` 100000, a G7 factor (v1 1.30, v2 1.80); the lookup expression is
`base_minor * number(veh_loading ?? "1.0")`; the table expression is `base_minor * (veh_factor ?? 1.0)`.

| Case | Lookup | Table |
|---|---|---|
| (a) step @1, pin @1 (control) | 130000 | 130000 |
| (b) step @1, unpinned | **100000**: quoted, `decline_reasons: []`, **−23.1%** | 100000 |
| (c) step @1, only @2 pinned | **100000**, −44.4% against 180000 | 100000 |
| (d) step @2, pin @2 (control) | 180000 | 180000 |

**Recorded from it:**
- **Table steps are affected, not only lookups.**
- **The trace is silent:** `matched: null`, `violation: null`. Nothing in the result tells a reader the
  ref was missing.
- With `on_miss="error"` the step fails at score, not at compile.
- **`03`'s own worked example (`03:258-272`) has this shape:** a `table` step (`s_expense`,
  `rate_table:motor-expense@3`, `on_miss: "default"`) whose output `expense_factor` is consumed in
  `s_office`'s expression. The example's expression multiplies `expense_factor` directly, which fails
  loudly (Table 2, "no `??`"); with a null-tolerant consumer it prices, as above.

### 4. The coded error the fix uses

`RATING_VERSION_UNPINNED` is already registered (`backend/src/app/errors.py:298`, in
`RATING_ERROR_CODES`, "Bundle compilation (W9-3)") and is owned by `03` §5.1 (`03:772-776`, a list of code names
with no definition beside them).
`compile_bundle` already raises it for a version with no `algorithm_ref` or no `pins`
(`compile.py:434-443`, message "… (FR-237)"). It fits an unpinned step ref, and one pinned at the wrong
version, without a new code. `PIN_NOT_APPROVED` (`errors.py:304`) is the wrong code: it means a pin exists
but its artifact is not approved. **No new code is needed;** if the maintainer wants the wrong-version case
named apart (for example `PIN_VERSION_MISMATCH`), that is a new code and a `03` §5.1 owned-code row, and it
is the maintainer's call. **The maintainer's condition (about 10:24 BST): reusing this code is allowed only if its spec catalogue meaning covers "a step ref not pinned at its exact version"; otherwise the slice amends the catalogue row, spec first, in the same commit.** Which case applies: **an amendment is needed.** The catalogue is `03` §5.1's paragraph headed "**Error codes owned by this module:**" (`03:772-776`); it is a bare list of names. Verbatim, the row for this code is only
`` `RATING_VERSION_UNPINNED`, `INPUT_CONTRACT_VIOLATION`, `` inside that list, with no definition. Nothing else in the specification defines it (`git grep -n "RATING_VERSION_UNPINNED" -- docs` finds the list entry and `CR-837`'s line "added to the §5.1 error codes"); the only written condition that raises it is in the code, `compile.py:434-443` (a version with no `algorithm_ref` or no `pins`). So the catalogue **does not cover the step case as written** — it covers nothing as written. Its name and FR-237's "Nothing is unpinned" (`03:134`) make it a natural home, but that is inference, not text. The fix slice therefore adds a one-line meaning to that paragraph in the same commit, spec first: for example "`RATING_VERSION_UNPINNED`: a Rating Version lacks its algorithm or pins, or a step's table, lookup or model ref is not in its pins at the exact version (FR-237)". The runtime `KeyError`s at `runtime.py:463` and `:533` become coded in the same slice. The score-time `KeyError` (defect 3) becomes unreachable through a compiled bundle once compile
refuses the version (a bundle cannot then exist with a step ref outside its payloads), and stays coded as a backstop.

### 5. Read-only data check (the filer's own)

**Question.** Does any stored Rating Version name a table, lookup or model step ref that is not in its own
pin set?

**Run**: 2026-09-30, from the auditor's worktree at `eeda8f4b`, all `SELECT`, in
`BEGIN TRANSACTION READ ONLY` with `PGOPTIONS='-c default_transaction_read_only=on'` through
`docker exec gi-pricing-postgres-1 psql`. Predicate (`scan_rv_pins.py` with `rvlogic.classify`): for each
row of `rating_versions` joined to its `rating_algorithms` row on
`algorithm_ref = 'rating_algorithm:' || slug || '@' || version`, collect every `rate_table_ref`,
`reference_table_ref`, `model_ref` and `peril_structure_ref` of the algorithm's steps and test each, as an
exact string, against the union of the version's `pins.rate_tables`, `pins.models`,
`pins.reference_tables` and `pins.custom_objectives`; an absent ref counts as unpinned, and one whose
`type:slug` matches a pin at another version also counts as wrong-version.

| Corpus | Count |
|---|---|
| Databases with both tables | **73** of 78 (`pg_database` with `datallowconn`) |
| Rating versions | **491**, of which **22** have a non-null `pins` (469 have none: drafts and demo rows that `compile_bundle` refuses as unpinned already); 7 name an algorithm that is not stored |
| Step refs (table, lookup, model) on those versions' algorithms | **0** (the pinned versions point at algorithms with only input, expression and output steps) |
| Unpinned step refs / wrong-version step refs | **0 / 0** |
| Algorithms carrying a table, lookup or model step | **3** (`motor-gb@1` twice and `motor-gb@2`, all in `gipricing_wt-ci-structure`, a test-scratch database); **no rating version points at any of them** |
| `gipricing` (the dev database) | 0 rating versions |

auditor-922's independent read agrees (73 non-template databases, 22 rating versions with pins checked, 0
unpinned; it did not scan `sub_graphs` steps or compare `custom_objectives`). **Nothing stored is
affected, and nothing stored could be, because no stored version names a step ref at all.** The defect is
latent in the data and live in the code. `rvlogic.py` carries a four-case self-test (pinned control; all
unpinned; wrong version on the table; model unpinned only) that exits 0. 

**Sweeps of fixtures, examples and MinIO (auditor-922, at `eeda8f4b`, reported; not re-run by the filer).**
- **`pricing-core` rating tests:** 118 passed; 76 `compile_bundle` calls logged; **0** step refs outside the pins.
- **Backend fixtures (rerun, superseding the first attempt's tenant error).** auditor-922 used a per-worktree scratch
  database with `alembic upgrade head` (the tenant-marker migration `d7e2a9b5c418` applied; the first database lacked it,
  which caused the `TenantMismatchError`). Set: `test_rating_version_compile`, `test_rating_versions`,
  `test_api_approvals`, `test_regression_runs`, `test_demo_rating_evidence`, `test_worker_raise_sites`,
  `test_error_sinks`, `test_api_blobs`: 181 passed. A scratch instrumentation of `compile_bundle` logged **70 compile
  calls** (`test_rating_versions` 48, `test_rating_version_compile` 11, `test_regression_runs` 9,
  `test_demo_rating_evidence` 2), **0 with a step ref outside the pins**. **Limit:** the 70 count only tests that reach
  `compile_bundle`, and auditor-922 did not check how many of them use a table, lookup or `model_call` step, so a 0
  there is bounded by that.
- **Examples and scripts:** the demo seed (`examples/fremtpl2/model.py:375-415`, `_demo_algorithm`) is input, then
  expression `premium_in * 2`, then output, with `_EMPTY_PINS` and **no step refs at all** (read, not executed);
  `scripts/bench-rating.py`'s pins match its step refs (read, not run).
- **PostgreSQL:** 22 rating versions with pins, 0 unpinned (agrees with the filer's read above).
- **MinIO:** 5 buckets; 6519 bundle JSONs (`gip-bench-compiled-for` 2, `gip-bench-score-batch` 2,
  `gip-test-blobs` 6515), **0** with a graph step ref outside its pins or `resolved_payloads`; **the 3986 blobs that first looked
  "algorithm-shaped" are score traces, not algorithms** (classified by auditor-922, read-only, reported, not re-run by the
  filer): class A, 2279 blobs with keys `bundle_hash, ladder_reconciled, quote_id, rating_version_ref, steps`, steps of type
  `constraint` and `lookup`, `quote_id` "quote-batch"; class B, 1707 blobs with the same keys, steps of type `lookup` only,
  `quote_id` "quote-realtime"; 2279 + 1707 = **3986**. Neither class has a `rate_table_ref`, `reference_table_ref`,
  `model_ref`, `peril_structure_ref`, `pins`, `graph`, `resolved_payloads` or `algorithm_ref` key; each step records
  consumed, produced and matched values, and the `bundle_hash` values are synthetic (ending in zeros). They cannot be
  compiled into a bundle or priced, so **they cannot be an affected artifact**. Cross-check: canonical-JSON matching against
  bundle-embedded algorithms and the pinned `rating_algorithms` of the 73 databases gave 0 of 3986 matches. The earlier
  "algorithm-shaped" label came from a predicate that was too loose (a `steps` list holding a table, lookup or
  `model_call` step). (This is a different question from the filer's text scan in the parser finding; the two share no result.)
- **MinIO, whole bucket now** (auditor-922, later run): `gip-test-blobs` holds 14 602 objects = 2069 non-JSON + 6540
  bundles + 3986 traces + 2007 other JSON; the growth over the earlier 14 577 is auditor-922's own backend test runs. Of the
  6540 bundles, the 6519 checked earlier had 0 step refs outside their pins; **the 21 new ones were not re-checked**, and the
  **2007 other-JSON and 2069 non-JSON objects were not classified or scanned** (this is stated, not counted as zero).

Tally: `pricing-core` 76 compile calls, backend 70, PostgreSQL 22 rating versions (491 versions, 73 databases in the
filer's read), MinIO 6519 bundles: **0 unpinned in every one.** The 3986 blobs are traces (0 affected, by class). Gaps stated, not
counted as zero: 21 newer bundles, and the 2007 other-JSON and 2069 non-JSON objects in `gip-test-blobs`. Owner of any
further amendment: the auditor.

## Severity

**High**, in force. The maintainer's entry of 2026-09-30 10:10:11 BST set it **medium, provisional**,
because no wrong price had been shown for table and model steps, and named the trigger: it rises to high
if the lookup path prices. auditor-922 then reproduced a silent wrong price on the lookup path, and
**auditor-933's independent reproduction confirmed it** (Table 3, both lookup and table steps). The
maintainer's entries of 10:12:52 BST ("DECISION (maintainer by delegation): the unpinned-step FD is HIGH on independent
reproduction; the owner changes; the queue is unchanged") and 10:15:07 BST ("the unpinned-step FD is HIGH (independent repro
confirmed) …") in `~/gi-pricing-plan.local/channel/to-lead.md` put it at **high**, and in force. A silent wrong price is the platform's most
serious class; it is held below critical because nothing stored is affected and there is no production
deployment yet (WK-674 builds one).

## Disposition

**Proposed by the auditor; the verdict is the lead's.** The maintainer's decision, recorded here rather
than restated as a ruling:

- **Owner: a dedicated WK-1178 fix slice**, replacing WK-1250 Slice 2 (the maintainer's first decision
  of 10:10:11 BST named Slice 2; the high severity moved it).
- **Scope:** `compile_bundle` refuses any table, lookup or `model_call` ref not pinned at the **exact
  version**, with a `CodedError` (`RATING_VERSION_UNPINNED`, evidence item 4), **with the code's catalogue meaning amended in the same commit (spec first)**. The model-path `KeyError`
  becomes coded by the same refusal.
- **Acceptance:** red first, per kind (table, lookup, model_call), **both unpinned and wrong-version**,
  **including the null-tolerant case that priced 1370, written with the `??` consumer**; `coalesce(` is refused at compile at this tree (`EXPRESSION_INVALID_VOCABULARY`), so it is not an acceptance case (see below).
  The controls stay green at **1507** and **2740**.
- **Order:** it merges before the WK-1250 Slice 1 dispatch (`compile.py` has a single writer), in the next
  free RL-1263 slot. It does not pre-empt WK-674 Slice 2 or WK-690 Slice 1: there is no production, and 0
  stored rating versions are affected so far.
- **The relation to #938's G1.** This fix **generalises the check #938 (working id 9851, the WK-1250
  rulings) gives WK-1250 Slice 2 as G1**: the compile-time refusal of a `SubGraphRef` that is not in
  `Pins.sub_graphs`, with fragment refs resolving only against the rating version's pins. G1 shrinks to
  `SubGraphRef` and reuses this fix's function. The planner records the delta to PL-1254 and PL-1278, citing
  this finding and G1; the WK-1250 Slice 2 dispatch record lists this finding among its acceptance sources.

### Related, not part of this fix
- **`??` is a separate §0 question, and `coalesce(` does not parse.** `03` specifies `coalesce(a, b)` (FR-244, `03:146`), not
  `??`. At this tree **`coalesce(` is refused at compile** (`EXPRESSION_INVALID_VOCABULARY`; ZEN answers
  `RuntimeError {"type":"parserError","source":"Incomplete parser output"}` for `coalesce(a, 1.0)`, and evaluates `a ?? 1.0`; found by
  auditor-924d, and re-run by the filer at the ZEN level), so **only `??` prices**. FR-244 lists a form the engine does not
  parse: a separate §0 matter, not this fix's. `_check_vocabulary` (`compile.py:233`) accepts only what ZEN compiles, which
  is why `coalesce(` is refused and `??` is accepted. The maintainer's 10:15:07 BST entry sends the `??` question to the DM
  as a §0 code/spec disagreement and notes that the class is wider than `??`; that entry's reading of `coalesce(` is being
  corrected. WK-690 Slice 1 must not change `??` semantics while that is open. The finding does not depend on the ruling,
  because the fix refuses an unpinned or wrong-version ref at compile whatever the consumer, `??` or any other form. FR-244
  listing `coalesce(a, b)` while the engine cannot parse it is the second §0 direction the DM may take (a spec correction,
  or a grammar change), and is not this fix's.
- **The model-call `KeyError` and the sentinel path.** The handler at `runtime.py:463` runs inside ZEN, which swallows a
  handler's exception (`runtime.py:85-91`, `_model_call_failure`'s docstring: the raised type, message and code are
  discarded and surface as the generic `NodeError`). So "coded" for the model path means the `MODEL_CALL_FAILED` sentinel
  path, not a raised `CodedError`. Any coded outcome, such as `MODEL_CALL_FAILED` through the sentinel, meets the requirement; the leaf plan decides the
  mechanism as a decision point (planner-1250's read).

**Event that next confirms or discharges it:** the WK-1178 fix slice merges with the exact-version
pin-membership refusal for table, lookup and `model_call` refs and its red-first tests (unpinned and
wrong-version, per kind, through the `??` consumer), the 1507 and 2740 controls stay green, and a step ref
pinned at another version is refused with `RATING_VERSION_UNPINNED`.

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The owner and
the high severity are the maintainer's, per the entries cited under *Severity* and *Disposition*.

Ownership shape: event
