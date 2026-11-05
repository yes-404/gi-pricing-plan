---
id: RL-8375
family: ruling
title: FD-1381 TRACK A — the 22 spec examples that fail their class, each given a side (11 spec wrong, 9 fragment by design, 2 code wrong)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-11-05            # drafted under working id 8375
owner: decision-maker
tree: 850cf225797c8a63065130dc9012a2ef31b5ef55
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1381, FD-1281, FD-1374, RL-1522, RL-1301, RL-1311, RL-1263]
---

# RL-8375 — FD-1381: the 22 failing spec examples, each with a recorded side

## Authority and scope

- **The ruling asked for.** T1 and T2 of PL 8372 (working id; `draft/pl-1381-2026-11-05` @`f3094233`), accepted in
  `to-lead.md` "2026-11-05 16:11:50 GMT": DP-4 (b), *"every one of the 22 gets a recorded side"*. The discharge is
  `FD-1381`'s item 1: the spec example is never matched to the code silently, and where the code is wrong that is its own
  finding.
- **The tree.** `origin/main` `bdad132291fdc05fe233d3ddc946e413dcbd2e1f`, tree `850cf225`. **Every line number here holds
  at this commit only** (G7). `NN:line` is the opening fence line in `docs/specs/NN-*.md`.
- **Not ruled here.** No spec text, code or fence line changes in this record. T3 applies the fixes; S4 of SL 8373 applies
  the marks.

## T1: the re-derivation

The sweep was re-run at the base with the plan's predicate, a fence being `^\s{0,3}` followed by three backticks, so
list-indented fences are read. Scripts in `~/gi-pricing-plan.local/scratch/rl-1381/`: `t1.py` (sha256 prefix `6e3f01d1cf7e`,
the census and every error) and `fix_proof.py` (prefix `06a70a52cb72`, the fixes), each given this checkout as its argument and
run on `tools-main`'s venv at the same commit, read-only.

| Population | Plan's Evidence | Here |
|---|---|---|
| Fenced blocks in `docs/specs/*.md` | 76 | 76 |
| `json` blocks | 62 | 62 |
| Bare blocks | 4 | 4 |
| `python` + `ebnf` | 10 | 9 + 1 |
| `json` blocks that parse | 42 | 42 |
| `json` blocks that do not | 20 | 20 |

**No count moved from Evidence.** Every row's error list was re-read in full by `model_validate` and agrees with the plan's
table, with three corrections to what that table can show:

1. **Three blocks hide a model validator behind their field errors,** the blind spot `FD-1381` names. Each surfaced only
   once the field errors were cleared: `01:224` (`latest_version` needs `latest_version_status`, `datasets.py:224`),
   `02:544` (`default_target_level` must be a target level, `modelling.py:612`; the printed `"…": "…"` entry maps nothing to
   `G4`), `02:690` (a Poisson spec must declare an offset, `modelling.py:1222`, FR-111). The fixes below include them.
2. **`07:234`'s class is `JobError`, not `Job`.** The block is the `error` member of a failed Job, under the sentence
   "Failure shape:" (`07:232`). `Job` is the plan's reading from the section heading.
3. **`04:254` as printed fails all four rating operation classes** with a `kind` `literal_error` plus `extra_forbidden` on the
   parameters the other kinds use. It is a template of the union, row 17.

## Ruled

Every one of the 22 has the side, the fix and the mark in **The 22**, under these four rules:

- **`schema=<Class>` wherever a block can validate without losing what it exists to show.** A fragment gains the fields
  rather than a mark: an `illustrative` block is never read again, which is the class of defect `FD-1381` records.
- **`illustrative` on a row of the 22 needs one of two grounds.** Either it is an elision or a union template shown not to
  contradict the class (rows 15 and 17; **Proof** below), or it is a code-wrong row carried by a finding (rows 5 and 18).
  Nothing else; so no `illustrative` here turns the check green over an unrecorded disagreement.
- **A dated note is a record and is not edited.** Where a note says the example is flat, or is not rewritten, T3 leaves it and
  appends a dated line citing this ruling.
- **The keys and the side are this ruling's; the literal values are T3's** (uuids, hashes, timestamps). A block that does not
  pass after its fix is a STOP (G3), not a re-mark.

### The 22

Side counts: **spec wrong 11, fragment by design 9, code wrong 2.** Sum 22, equal to T1's count. A row with any code-wrong limb
counts as code wrong.

| # | Block | Class | Side | The spec says | The code says | Fix (T3) | Mark (S4) |
|---|---|---|---|---|---|---|---|
| 1 | `00:318` | `ArtifactEnvelope` | fragment by design | Each value is a type description: `"slug": "string, ^[a-z0-9]…"`, `"created_at": "timestamptz"` | `envelope.py:16`: typed fields, pattern on `slug`, datetimes | **Fields.** Literal values for every key. One sentence after the block keeps what the values said: the `slug` pattern, `status` being entity-specific, ISO 4217 and OQ-542 on `currency`, which fields are nullable | `schema=ArtifactEnvelope` |
| 2 | `01:224` | `Dataset` | fragment by design | Omits the envelope by §4's stated convention: "every entity also carries the `ArtifactEnvelope`" | `datasets.py`: `id`, `workspace_id`, `created_at` required; `latest_version` and `latest_version_status` are "one fact" (`:224`) | **Fields.** Add `id`, `workspace_id`, `created_at`, `latest_version_status`; literal uuids | `schema=Dataset` |
| 3 | `01:329` | `ValidationRule` | spec wrong | `"owner": "pricing-actuary@example.com"` | `validation.py:83`: no `owner`, `extra="forbid"`. `validation-rule.schema.json`'s description, reconciled 2026-08-23, already records `owner` as "carried by no field of the model". No FR names a rule owner | Remove `owner`; add `id` and `version` | `schema=ValidationRule` |
| 4 | `01:346` | `ValidationRuleSet` | spec wrong | `"rules": [{"rule_id": …, "rule_version": 2, "enabled": true, "severity_override": null}]` | `validation.py:157`: `entries: tuple[RuleSetEntry, ...]`, each embedding the whole `rule` (`:115`). `GET`/`PUT …/rule-set` return that class (`api/validation.py:422`, `:439`). The `PUT` body is `rules` of `rule_id`, `enabled`, `severity_override` (`RuleSetReplace`, `:124`), with no `rule_version` | Replace `rules` by `entries`, one entry embedding row 3's fixed rule; add `id`; literal uuids. Dated line under the 2026-08-15 note: the read shape is `entries`, the `PUT` body is `rules`, and neither has the printed `rule_version` | `schema=ValidationRuleSet` |
| 5 | `01:550` | `ValidationReport` | **code wrong** (wire) + spec wrong (limbs) | Prints `overall` and `counts`; the authored `validation-report.schema.json:7-8` requires both. Also `evidence_blob`, and `overall` as a four-way string | `validation.py:556`, `:567`: plain properties, so `GET /validation-reports/{report_id}` (`api/validation.py:146`) omits both, as does `generated.json`'s `ValidationReport`. `RuleResult` (`:510`) has no `evidence_blob`, nothing builds one, and FR-49 does not list one; the authored contract's nullable entry (`:59`) is the only other trace | Spec limbs only: add `id`, literal uuids, remove `evidence_blob`, `"overall": "pass_with_warnings"`. **Keep `overall` and `counts`.** Dated line naming the finding of **Code wrong** below | `illustrative` until that finding closes |
| 6 | `02:421` | `Factor` | fragment by design | Omits the envelope, §4's convention | `id` required | **Fields.** Add `id`; literal uuids | `schema=Factor` |
| 7 | `02:544` | `Grouping` | spec wrong | `target_level_stats` carries `"relativity": 0.78`; `mapping` holds `"…": "…"` | `modelling.py:563`: `tuple[OneWayRow, ...]`; `profiles.py:137` has no `relativity`. FR-107 asks for Level statistics and the change in fit, not a relativity | Remove `relativity`. Replace the `"…"` entry with a real entry mapping a source level to `G4`, so `default_target_level` is a target level. Literal uuids | `schema=Grouping` |
| 8 | `02:690` | `GlmSpec` | fragment by design | "`GlmSpec` adds:" (`02:688`), the arm's own fields only | `model_family_slug`, `dataset_version_id`, `response_column` required; a Poisson spec needs `offset` (`modelling.py:1222`) | **Fields.** Add those three and `"offset": {"kind": "log_column", "column": "exposure_years"}`, §4.4's own common-block value. Reword `02:688` to say the example also carries the required common fields | `schema=GlmSpec` |
| 9 | `02:725` | `GlmCvSpec` | spec wrong | `method` holds the three choices as one string | `Literal` of the three | `"method": "random"`; name the three values in one sentence after the block | `schema=GlmCvSpec` |
| 10 | `02:896` | `EbmSpec` | fragment by design | "`EbmSpec` adds" (`02:894`) | As row 8, less the offset | **Fields.** Add the three; reword `02:894` as row 8 | `schema=EbmSpec` |
| 11 | `02:1092` | `CustomObjective` | fragment by design | Omits the envelope, §4's convention | `id`, `version` required | **Fields.** Add `id`, `version` | `schema=CustomObjective` |
| 12 | `02:1138` | `ObjectiveCertificate` | spec wrong | Flat `checks`, `sampling`, `overall`, `library_versions`, plus `_note` | `objectives.py:941`: identity wrapping `result: CertificateResult`. The spec's own amendment of 2026-08-18 says so: "The JSON above shows them flat. The split is ADR-703" (`02:1199`) | Nest the four under `result`; add `id`, `certified_at`, `job_id`; literal uuid. `_note`'s sentence moves to prose after the block. Dated line under the amendment that the example is now nested | `schema=ObjectiveCertificate` |
| 13 | `02:1531` | `TransparencyArtifact` | spec wrong | `kinds` array; `relativity_table_blob` and `dependence_blob` as `"blob:sha256:…"` | `transparency.py:222`: `kinds` "Derived, never stored"; absent from both contracts; `02:1645` records the reasoning. Both blobs are `BlobRef` objects (`refs.py:182`), as ID-4 states. `terms_blob` is a `str`, and stays | Remove `kinds`; both blobs as `BlobRef` objects (`sha256` of 64 hex, `bytes`, `media_type`); add `id`, `created_at`; literal uuids | `schema=TransparencyArtifact` |
| 14 | `03:374` | `RateTableVersion` | spec wrong | `value` has no `unit`; carries `diff_vs_previous`, `diff_vs_seed` | FR-228 and `rating.py:1225` require `unit`. `rating.py:1590` has no diff field. A diff is served by `GET …/diff?against=&portfolio=` (`03:1104`), against a portfolio the caller names (FR-231), so an immutable version cannot hold one | Add `"unit": "factor"`, the seeded value's unit (`pricing_core/rate_tables/operations.py:248`); remove both diffs; one sentence pointing at the `/diff` route | `schema=RateTableVersion` |
| 15 | `03:954` | `ScoreComparison` | fragment by design | `{"...": "a traced ScoringResult"}` and `{"...": "TraceStep"}`: elisions of shapes defined elsewhere, to show the diff | `scoring.py:317`. With only the elisions filled, everything printed passes | **`illustrative`.** No text change. A filled block would be a false "traced" example or a long one, and would obscure what it shows | `illustrative` |
| 16 | `03:1024` | `Deployment` | spec wrong | `"bundle_hash": "sha256:9f2c…"`, truncated | `deployments.py:49`, 64 hex; every other value in the block is literal | A full 64-hex value | `schema=Deployment` |
| 17 | `04:254` | the four rating `*Operation` classes | fragment by design | `kind` lists all four and `parameters` all their keys: a template of the union, explained by the list after it | `rating.py:1464`, `:1468`, `:1472`, `:1476`, not in `model_schema.__all__`, so no marker can name them. Each kind with its FR-233 parameters, all else as printed, passes `BulkOperation` | **`illustrative`.** No text change | `illustrative` |
| 18 | `06:346` | `ApprovalPolicy` | **code wrong** (`FD-1281`) | `expedited` (FR-385) and `separation_of_duties` | `approvals.py:250`: neither; a flat `submitter_may_approve`. FR-385 is unbuilt, owner WK-677 | **No text change.** Not re-ruled: `FD-1281` is active and its Disposition settles the shape when that Work builds FR-385 or amends §4.2. No new finding | `illustrative` until `FD-1281` closes |
| 19 | `06:462` | `ApprovalRequest` | spec wrong | `expedited`, `evidence_bundle`, `checklist`, `flags` | `approvals.py:490`: none. `RL-1522` DP-4 (a) ruled them "not fields of the shape now"; FR-352's limbs and FR-385 stay owned by WK-677, a P3 Work | Remove the four; add `id`, `workspace_id`; literal uuids. Dated line under the note at `06:492`: the example now validates, and that note's "illustrates FR-352's full submission" no longer describes it. The same line names `checklist`'s item keys (`item`, `checked`, `by`, `auto_verified`) so the shape stays on record. FR-352 is not amended | `schema=ApprovalRequest` |
| 20 | `06:536` | `AuditEvent` | spec wrong | `"id": "01J…"`, truncated hashes | `audit.py:78`: `id` a UUID, as ID-1 says; both hashes 64 hex (`:86`, `:93`) | Literal uuids; full hashes | `schema=AuditEvent` |
| 21 | `07:234` | `JobError` (T1, item 2) | fragment by design | `{"error": {…}}`, the one member of a failed Job | `jobs.py:174`: the inner object passes as printed | **Fields, by narrowing.** Drop the wrapper; the block is the `JobError`. Reword `07:232` to say it is `Job.error` on a failed Job | `schema=JobError`, not `Job` |
| 22 | `07:248` | `Environment` | spec wrong | No `slug`; `settings`; truncated hash | `deployments.py:59`. The notes at `07:262` and `07:268` already record both, each saying "The example above is not rewritten" (`RL-1301` A.6; `RL-1311`) | Add `"slug": "prod"`; remove `settings`; a full hash. Dated line after those notes that the example is now rewritten | `schema=Environment` |

**Proof.** `fix_proof.py` applies each fix above to the spec's own block at the base, and each named row passes
`model_validate`, the model validators included: 27 `PASS` lines, among them all four kinds of row 17 and row 15 with its
elisions filled. The one `FAIL` line is `02:544` with its `mapping` left as printed, which is why row 7 replaces that entry.
Row 18 is not in the script, having no fix. Row 5's block passes with `overall` and `counts` removed, so its code-wrong limb is
the only thing keeping it `illustrative`. T3 re-runs the script at its own base, since slice C changes `model_schema/refs.py`.

**End state, for S4 and A9.** Of the 62: `schema=` 32 (the 12 that pass, `01:809` and `02:1861` after T3, and 18 of these 22);
`illustrative` 30 (the 6 with no class, the 20 that do not parse, and rows 5, 15, 17, 18). 32 + 30 = 62.

### Code wrong

- **Row 5: a new finding, for the lead to file; no id minted here.** `GET /api/v1/validation-reports/{report_id}` omits
  `overall` and `counts`, which `01` §4.6 and the authored contract state. **Why the code and not the spec.** The other three
  statements agree: the example, the authored contract's `required`, and `ReportSummary`, the sibling route, which does carry
  `overall` (`api/dataset_versions.py:188`). The model's own sibling calls this exact omission a defect: *"A plain `@property`
  is not serialised … A client deriving it from `entries` would be a second implementation of the rule"* (`validation.py:187`,
  `ValidationRuleSet.empty_layers`). Row 13's `kinds` looks the same and is not: it is in neither contract and has a recorded
  reason. For `overall`, `grep -rln 'ValidationReport.overall\|`overall`' docs/rulings docs/findings` at this tree prints
  three records, and each is about another `overall` (`RL-1900`, `RL-1172`, `FD-1512`). **Trap for whoever fixes it.** The
  stored body is `report.model_dump(mode="json")` (`platform/validation.py:114`), read back by `model_validate` (`:154`) under
  `extra="forbid"`, so a bare `@computed_field` writes keys the read then refuses. **It does not widen TRACK A.** Until it
  closes the block is `illustrative` and `ILLUSTRATIVE_CEILING` counts it.
- **Row 18: `FD-1281`, existing.** No new finding.

### Noticed, not ruled

Each is outside the 22 and changes nothing above.

- `02`'s note that `holdout_strength_ratio` makes the example invalid (noted 2026-08-24) is overtaken: `transparency.py:163`
  has the field.
- `03:374`'s `"min": 0.2` is a JSON float beside "never JSON floats (R2)"; it passes the class, so nothing here reads it as a
  failure.
- `rate-table.schema.json` still declares row 14's two diffs, and that file is F27's and "never compared". `validation-report.schema.json:59` still declares row 5's `evidence_blob`. T3 edits neither.

### Could not be ruled

Nothing. DP-4's fallback is not used.

## What it obliges

- **T3 (executor):** rows 1 to 14, 16 and 19 to 22, one commit per spec, each citing this ruling. Rows 15, 17 and 18 have no
  text change. A3 holds on this list: every fix is in a §4 section, and none is in `06` §4.1, the section SL 8361 shares.
- **S4 of SL 8373:** the Mark column. Row 21 is `schema=JobError`.
- **The lead:** row 5's finding, whose id T3's dated line and A2 then name.

## Acceptance — the violation that must become detectable

The violation: a block of the 22 goes green without its side, by an `illustrative` this ruling does not name or a fix that does
not pass. This ruling adds no script; these are the checks.

1. **Every row has a side (A1).** `grep -cE '^\| [0-9]+ \| `[0-9]{2}:[0-9]+` \|' <this file>` prints 22.
2. **Each fix passes, until check 40 lands.** `fix_proof.py` at T3's base prints no `FAIL` line but the one for `02:544` as printed.
   Once T3 has merged, the blocks themselves are the input, and `tests/test_spec_examples.py` of SL 8373 (A11) reads them.
3. **No other `illustrative` on this list.** After S4, of these 22 fences only rows 5, 15, 17 and 18 carry `illustrative`, and each
   of the others carries the class in its Mark column. Check 40's note line must then read 62 blocks, 32 `schema`, 30 `illustrative`,
   0 unmarked, unless a dated line moves a block.
