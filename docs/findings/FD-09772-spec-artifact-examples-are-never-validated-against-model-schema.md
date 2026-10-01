---
id: FD-9772
family: finding
title: Spec artifact examples are never validated against model-schema
status: active
created: 2026-10-01
owner: auditor
tree: 08990db3ee7bcf950ea7cbfd8edd5e5f7d129d4f
corrected_by: []
relates: [WK-1178, FR-212, FR-214, FD-9773]
---

# FD-9772 — the spec's artifact examples are never validated against `model-schema`

**Filed under working id 9772.** The id is minted by the lead at the merge turn. The `tree:` is the tree of
`origin/main` at `c535b19d`; every count and path below was read at that tree. Ordered by the maintainer in
`to-lead.md` (`/home/puzhenhao1989/gi-pricing-plan.local/channel/to-lead.md:15492`), the entry headed
"2026-10-01 09:49:51 BST — PL 9776 @3e32c74c acknowledged; 03's example fails model_validate several ways: the corrected
example must pass FULL validation; the class (unvalidated spec examples) becomes a separate finding".

## Finding

**Severity: to be set by the maintainer; owner WK-1178 (backlog).** No check in the gate validates a JSON artifact example
in `docs/specs/` against the `model-schema` class it illustrates. `scripts/audit-docs.py` reads the specs for ids,
sections and links, and `backend/tests/test_contracts.py` compares the generated contracts with the hand-authored ones;
neither parses an example block and calls `model_validate` on it. So an example can contradict the shape it shows, and the
suite stays green.

**The instance that exposed it.** `docs/specs/03-rating-engine.md` §4.1, the example `RatingAlgorithm` (fence opens at
`03:233`, body `03:234-275`), fails `RatingAlgorithm.model_validate`. Validation stops at the first error, so each
error was reached by removing the one before it (`ra_probe.py`, below):

1. as written: `declared output 'premium_ladder' has no output step (FR-214)` (the example declares three outputs and has
   one output step, for `payable_premium_minor`);
2. with `outputs` cut to the one that has an output step: `step 's_out' consumes undefined value
   'payable_premium_pre_round' (FR-212)`;
3. with `s_out` consuming `office_premium_minor`: `value 'office_premium_minor' is produced by 2 steps that do not form a
   single re-production chain (FR-212)`.

That is the three defects the order names (FR-214 once, FR-212 twice). The five steps that under-declare their reads are
`FD 9773` (working id), not claimed here.

## Evidence

**A counted sweep, run at `origin/main` `c535b19d` (tree `08990db3`), not inferred.**

- Script: `/home/puzhenhao1989/.claude/jobs/6fa41099/tmp/spec_example_sweep.py`. Command, from the repo root of a checkout
  of that tree with `uv sync --all-packages` done: `.venv/bin/python
  /home/puzhenhao1989/.claude/jobs/6fa41099/tmp/spec_example_sweep.py`. The per-error probe is `ra_probe.py` in the same
  directory, same invocation.
- **Corpus and predicate.** Every fenced block in `docs/specs/*.md`, taken as a line starting with three backticks and an
  optional word, to the next such line. The predicate for a "block" is that, not a prose mention.
- **Classification rule.** The script imports every pydantic `BaseModel` defined in the `model_schema` package. A parsed
  block is classified to class C iff its top-level keys are a subset of C's field names or aliases, and C is the unique
  such class with the fewest fields. No match, or a tie, is **unclassified**: it is listed and never counted as passing.
- **Validation.** `C.model_validate(json.loads(block))`; pass or fail with the first error. A failure whose errors are
  all type-parse errors on placeholder values (`uuid-…`) is reported apart as *placeholder-only*, not as a shape defect.

| Population | Count |
|---|---|
| Fenced blocks in `docs/specs/*.md` | 74 (60 `json`, 4 bare, 9 `python`, 1 `ebnf`) |
| Not JSON by fence language (`python`, `ebnf`) | 10 |
| JSON-or-bare blocks that do not parse as JSON | 24 (the 4 bare blocks, which are prose, diagrams and an HTTP request, and 20 `json` blocks that carry `…` or `//` comments) |
| JSON blocks parsed | 40 (all objects) |
| of which unclassified | 18 |
| of which classified and validated | 22 |
| validated: pass | 10 |
| validated: fail, with a structural error | 10 |
| validated: fail, placeholder values only | 2 |

So of the 60 `json` blocks, 22 were validated and 38 were not. Of the 22, 10 failed on shape.

**Failing, with a structural error (file:fence-line, class, first error):**

- `00-overview.md:291` `envelope.ArtifactEnvelope`: 9 errors, 2 structural; first structural `slug` fails
  `^[a-z0-9][a-z0-9-]{1,62}$`.
- `01-data-management.md:224` `datasets.Dataset`: 5 errors, 3 structural; first `id` missing.
- `02-modelling.md:481` `modelling.Grouping`: 4 errors, 1 structural; `evidence.target_level_stats.0.relativity` is
  `extra_forbidden`.
- `02-modelling.md:627` `modelling.GlmSpec`: 3 structural; first `model_family_slug` missing.
- `02-modelling.md:662` `modelling.GlmCvSpec`: `method` is not one of `random`, `temporal`, `grouped_by_key`.
- `02-modelling.md:833` `modelling.EbmSpec`: 3 structural; first `model_family_slug` missing.
- `03-rating-engine.md:233` `rating.RatingAlgorithm`: `declared output 'premium_ladder' has no output step (FR-214)`
  (the only error reported; the others are behind it, above).
- `03-rating-engine.md:717` `scoring.ScoreComparison`: 22 structural; first `base.outcome` missing.
- `06-governance.md:504` `audit.AuditEvent`: 5 errors, 2 structural; first structural `prev_event_hash` fails
  `^sha256:[a-f0-9]{64}$`.
- `07-platform.md:233` `jobs.Job`: 8 structural; first `id` missing.

**Failing on placeholder values only:** `01-data-management.md:804` `datasets.DatasetLineage`; `02-modelling.md:1773`
`metrics.CustomMetric`. Both fail `uuid_parsing` and nothing else.

**Passing (10):** `00:338` `ProblemDetail`; `02:691` `TweediePowerSpec`; `02:1358` `EbmFitResult`; `02:1404`
`GbmFitResult`; `03:395` `GoldenQuoteNotChecked`; `03:416` `QuoteContext`; `03:658` `RegressionRun`; `03:706`
`ScoreCompareRequest`; `03:746` `SubGraph`; `07:279` `SettingResolution`.

**Unclassified (18; not counted as passing):** `01:324`, `01:341`, `01:545`, `01:750`, `02:384`, `02:1028`, `02:1074`,
`02:1455`, `03:286`, `04:254` (tie among four rating operation classes), `05:158`, `05:216`, `05:260`, `06:190`,
`06:344`, `06:442`, `07:247`, `07:263`. Each has no `model_schema` class whose fields contain all its keys; whether that is
an example that has drifted from a shape, or a shape `model-schema` does not yet define, the sweep does not say.

**Not parsed (24):** `00:14`, `00:79`, `00:242`, `00:329` (bare diagrams); `01:256`, `01:603`, `02:424`, `02:557`,
`02:711`, `02:1198`, `02:1520`, `02:1601`, `02:1674`, `03:347`, `03:428`, `03:465`, `03:489`, `03:518`, `04:135`,
`04:174`, `04:213`, `05:190`, `05:238`, `07:192`. Run the script for the first parse error of each.

**Blind spots, stated so the counts are not read wider than they are.**

- **Partial examples marked `…`** and blocks with `//` comments do not parse, so they are in the 24, not in the passes. A
  tolerant parser would reach some of them and was not written.
- **The classification is by keys alone.** A fragment whose keys happen to fit a small class passes as that class: `02:691`
  (`{"p_grid": …}`) passing as `TweediePowerSpec` shows a fragment match, not a full artifact. A wrong class for a real
  artifact would show as a failure, not a pass, so the passes are the weaker half of the table.
- **Errors after the first are hidden by model validators.** A pydantic model-level validator does not run when a field
  error exists, so a failing block can hide further errors; the `RatingAlgorithm` case shows three behind one.
- **Placeholder-only failures are a judgement.** A value `uuid-…` is not a shape defect; a real defect hidden behind such
  a value would still print as structural, so the split cannot hide one, but it cannot show a wrong uuid either.
- **Prose fragments and inline code** (a shape named in a table cell or sentence) are not fenced blocks and are not
  swept. **YAML:** no fenced block in `docs/specs/*.md` uses a `yaml` fence (the fence-language count above), so none was
  swept; a YAML example in another directory would not be reached.
- **Python blocks** (9) are not artifact examples; they were not swept. They carry signatures that a different check
  (the code-signature comparison, `spec-reconciler`) addresses.

## Why it matters

`CLAUDE.md` §2 makes `model-schema` the one source of a shape and says "a shape defined twice will diverge". A spec example
is a second definition of the shape: an implementer reads it, and so does a reviewer. Ten of the 22 examples that could be
validated disagree with the class, and 38 of 60 JSON blocks have never been tried. The corrected §4.1 in `PL 9776`
(working id) must pass `RatingAlgorithm.model_validate` in full; without a check, the next edit to that block can break it
again with nothing red.

## Disposition

**Severity: to be set by the maintainer.** Owner **WK-1178** (backlog).

**Proposed check.** A docs check in `scripts/audit-docs.py` that, for each fenced JSON block in `docs/specs/*.md`:

1. parses it, and treats a block marked as partial (a fence tag or an adjacent marker the check defines) as exempt, listed
   rather than silent;
2. classifies it to a `model-schema` class by a declared marker on the fence (preferred, because the key-subset rule above
   misclassifies fragments) rather than by inference;
3. runs `Class.model_validate`; and
4. fails the gate on any unclassified, unparsed and unmarked block, so the exemption set is explicit and shrinks.

The check must be **proven on deliberately broken input** (`CLAUDE.md` §13): the §4.1 example as written today is the
first such input, and it must print a failure. The 12 failures and 18 unclassified blocks above are the backlog it would
open with; fixing them is a spec change per `.claude/skills/spec-change`, owner WK-1178, one block at a time. The check
needs `model_schema` importable from the docs gate, which the docs half does not do today; that is a design point for the
plan, not decided here.

**Recorded here.** Proposed by the auditor, 2026-10-01; the lead gives the verdict. Event that next confirms or discharges
it: the maintainer sets severity, and the WK-1178 plan for the docs check is filed.

Filed 2026-10-01 as working id 9772.
