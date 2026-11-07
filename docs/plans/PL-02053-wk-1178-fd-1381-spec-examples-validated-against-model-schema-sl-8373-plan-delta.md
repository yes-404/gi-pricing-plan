---
id: PL-2053
family: plan
kind: map
title: WK-1178 — FD-1381, every JSON example in docs/specs carries a marker and every class-marked example passes model_validate, SL 8373 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-06             # original date 2026-11-05, filed under working id 8372; minted 2026-11-06
owner: planner
tree: 850cf225797c8a63065130dc9012a2ef31b5ef55
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1381, FD-1374, FD-1281, FD-1484, RL-1263, FR-212, FR-214, FR-152]
---

# PL-2053 — WK-1178: FD-1381. Spec examples are marked, and validated against `model-schema` (SL 8373, a dated Work-plan delta)

*Disclosure: drafted under working id 8372; minted as PL-2053 on 2026-11-06, in the TRACK A (SL 8373, T3) mint.*

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L1 (a'): a new `PL-` that
> edits no earlier plan. It holds one docs track, TRACK A, and one code slice, SL 8373. **It
> decides nothing, and no build seat starts until the maintainer accepts it** (to-lead
> "2026-11-05 15:55:35 GMT" item (4)). The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test` and
> `.claude/skills/spec-change`. PL-2053 is minted (was working id 8372); SL 8373 and LG 8374 are working ids, reserved by the lead.

## Authority

- **The finding.** `FD-1381`, MEDIUM, owner WK-1178, `docs/findings/FD-01381-…md`. *Discharge*,
  `:137-147`: (1) "Each of the 10 structural failures is resolved individually, recording which
  side was wrong"; (2) "The docs check lands", with a class marker or an "illustrative fragment"
  marker, "`model_validate` in full", "proven on deliberately broken input", failing "on any
  unmarked `json` block", "The rule goes into the docs-process text first, then the check";
  (3) "the end state has 0 unmarked blocks, counted by the check itself".
- **The placement.** Essay `:152-168`: (a) the adjudication and spec text are a docs track; (b) the
  check is a code slice under `RL-1263`; its ordering is "the planner's choice, stated in the
  plan" (`:167`). `:182-183` leaves `model_schema` in the docs gate as "a design point for the plan".
- **This seat.** To-lead "2026-11-05 15:55:35 GMT" item (4): the plan states its gate cost and any
  overlap with the chain's paths; "the Tue 10 18:00 re-decision becomes 'at the plan's acceptance,
  if earlier'". FD-1381 is a named freeze exception, register `:292` dated line of 2026-11-05.
  Dates of record: code freeze Thu 12 Nov, docs freeze Fri 13 Nov (to-lead "2026-11-05 09:58:58 GMT").

## Goal

No JSON example in `docs/specs/` can disagree with `model-schema` while the gate stays green. Every
block declares what it is, every declared class is validated in full, and every spec/code
disagreement the sweep exposes gets a recorded side (`CLAUDE.md` §0).

## Evidence at `bdad1322` (tree `850cf225`), run read-only

**The essay's script is gone.** `~/.claude/jobs/6fa41099/tmp/spec_example_sweep.py` does not exist
on this box. It was rebuilt from the essay's rule (`:51-57`) as
`~/gi-pricing-plan.local/scratch/plan-fd1381/spec_example_sweep.py`, sha256 prefix `022060c84edc`,
run with `tools-main`'s venv at the same commit. Two departures: *placeholder* means
`uuid_parsing` only, so `00:318` reads 5 structural errors where the essay read 2; and an indented
fence was added by hand, below. **Every line number here holds at this tree only.**

| Population, any fence up to three spaces in | Essay at `c535b19d` | Here |
|---|---|---|
| Fenced blocks in `docs/specs/*.md` | 74 | 76 |
| `json` blocks | 60 | **62** |
| Bare blocks | 4 | 4 |
| `python`, `ebnf` | 10 | 10 |

The extra block over the essay's predicate is `03:1006`: a list-indented fence, which a
start-of-line predicate never sees, so **the essay's rule undercounts by construction**. The new
check must read indented fences. `_FENCE_RE` (`scripts/_docid.py:502`) already allows them.

**The 62, by what each needs.** Parts sum: 12 + 22 + 2 + 6 + 20 = 62.

| Class of block | n | Blocks |
|---|---|---|
| Pass the class their heading names | 12 | `00:369` `02:754` `02:1422` `02:1468` `03:250` `03:554` `03:581` `03:886` `03:943` `03:985` `03:1006` (`SubGraphRef`) `07:290` |
| Placeholder only, class exists | 2 | `01:809` `DatasetLineage`, `02:1861` `CustomMetric` |
| No `model_schema` class | 6 | `01:755`, `05:158`, `05:216`, `05:260`, `06:190`, `07:272` |
| Do not parse (`…`, comments, `a \| b`) | 20 | `01:256` `01:608` `02:476` `02:620` `02:774` `02:1262` `02:1596` `02:1683` `02:1756` `03:505` `03:593` `03:630` `03:663` `03:729` `04:135` `04:174` `04:213` `05:190` `05:238` `07:193` |
| **Fail the class their heading names** | **22** | the table below |

**The 22.** `Row` is the essay's list: **E** a row of its 10, **N** new by the essay's own rule at
this tree, **U** unclassified by the essay's rule only because the keys left the class.

| Block | Class | Row | First errors, by `model_validate` |
|---|---|---|---|
| `00:318` | `ArtifactEnvelope` | E | 9 errors: `slug` pattern, `created_at` date form, uuids |
| `01:224` | `Dataset` | E | `id`, `workspace_id` missing; uuids |
| `01:329` | `ValidationRule` | U | `id`, `version` missing; `owner` extra_forbidden |
| `01:346` | `ValidationRuleSet` | U | `id` missing; `rules` extra_forbidden |
| `01:550` | `ValidationReport` | U | 10 errors: `id` missing, uuids |
| `02:421` | `Factor` | N | `id` missing; uuids |
| `02:544` | `Grouping` | E | `evidence.target_level_stats.0.relativity` extra_forbidden |
| `02:690` | `GlmSpec` | E | `model_family_slug`, `dataset_version_id`, `response_column` missing |
| `02:725` | `GlmCvSpec` | E | `method` holds the three choices as one string |
| `02:896` | `EbmSpec` | E | the same three missing |
| `02:1092` | `CustomObjective` | N | `id`, `version` missing |
| `02:1138` | `ObjectiveCertificate` | U | 9 errors: `result`, `certified_at` missing, `_note` |
| `02:1531` | `TransparencyArtifact` | U | 7 errors: `id`, `created_at` missing |
| `03:374` | `RateTableVersion` | U | `value.unit` missing; `diff_vs_previous`, `diff_vs_seed` extra_forbidden |
| `03:954` | `ScoreComparison` | E | 22 errors: `base.outcome` and more missing |
| `03:1024` | `Deployment` | N | `bundle_hash` pattern |
| `04:254` | the rating `*Operation` classes | U | a tie of four; `kind` literal, `parameters` extra_forbidden |
| `06:346` | `ApprovalPolicy` | U | `expedited`, `separation_of_duties` extra_forbidden |
| `06:462` | `ApprovalRequest` | U | 8 errors: `id`, `workspace_id` missing, uuids |
| `06:536` | `AuditEvent` | E | `prev_event_hash` pattern; uuids |
| `07:234` | `Job` | E | the block shows `error` alone; the rule now misfiles it as `ObjectivePreview` |
| `07:248` | `Environment` | U | `slug` missing; `settings` extra_forbidden |

**The essay's 10 at this tree.** Nine stand. **`03:233` is discharged**: `FD-1374` is `closed`, and
the block, now `03:250`, passes `RatingAlgorithm`, which
`packages/pricing-core/tests/test_rating_declared_reads.py:92-99` reads from the spec. With the
three **N** rows, the essay's own rule yields **12 structural failures**, not 10.

**`06:346` is already a ruled limb.** `FD-1281` is active, and register `:216` records both keys and
FR-385 as unbuilt. This plan does not re-rule it.

**What the docs job can import.** `.github/workflows/docs.yml` runs `python3 scripts/audit-docs.py`
after `setup-python` with no `uv sync`. `scripts/audit-docs.py` imports the standard library only,
and bare `python3` here has no pydantic. `python.yml` fires on `docs/**` and runs `uv run pytest -q`,
so a pytest file sees every spec-only PR. Every class named above is in `model_schema.__all__`, 409
names, so a marker can name a class without its module, **except the four rating `*Operation` classes
of `04:254`**, which are not exported: under G1 that block can only be `illustrative`, or a STOP.

**What reads a spec fence.** By `git grep` of three backticks over `scripts`, `backend`, `tests`,
`packages` and `frontend/src`, three sites read a spec's JSON block:

- `backend/tests/test_objective_submission.py:533`, `r"```json\n(.*?)\n```"`: **an exact match, which
  a fence token breaks.** Its block is `06:346`.
- `packages/pricing-core/tests/test_rating_declared_reads.py:96-97`, `startswith`: survives a token.
- `scripts/audit-docs.py:627`, check 22, `startswith`: survives a token.

**Blind spots.** A block outside `docs/specs/` is unread; `docs/workflows/` holds no `json` fence.
The class of each **U** row is read from its heading and key overlap, which is evidence for the
ruling, not the ruling. Hunks were read on local heads on 2026-11-05 before 16:10 UTC; a head moves.

### The chain's collisions

Measured per worktree: `git diff -U0 $(git merge-base HEAD origin/main) HEAD -- docs/specs`, each
new-side hunk compared with that branch's own fenced ranges and enclosing heading. **Zero hunks
touch a fence, on 8 branches with spec hunks.** The instrument is proved: over `c535b19d..bdad1322`
on `03`, the same predicate hits 8 blocks.

| Slice | Paths shared with this plan | Reading |
|---|---|---|
| LAST-2 + T, SL 8343 @`5748acc7` | `scripts/audit-docs.py`, nothing else | 9 hunks at `:293-:642` and `main()` `:4062-:4153`; none at the docstring, above `def main`, or the tail of `main()`, which is where check 40 goes. **`table_rows` is not touched here**, and `_docid.py` stays outside this write set. Merge after it, the chain's order. |
| SL 8361 @`3527bf87`, the column | `06` §4.1, which holds `06:190` | A row at `06:284`, not the fence. **The one section clash** (`RL-1263` `:89`); its `02` and `03` hunks are §5.1 rows, no fence. The mark on `06:190` merges after it. |
| M, SL 8359 @`913b4674` | `02` | §3.8 and §10 only; no §4 section. |
| R1 SL 8322, R2 SL 8345 | `03` | §3.3, §3.4, §3.7, §5.1 only; no §4 section. |
| C SL 8328, SL 8368 | `02` §5.1 | No §4 section. **C changes `model_schema/refs.py`**, so a ref in a block may read differently after it: T1 re-reads at its base. |
| A SL 8325 | `01`, `03`, `07` | §5.1, §3.3, §3.9 only. |
| D `sl-1689-d` | `07` §8 | No §4 section. |
| LAST-1, SL 8340 | `00` | FR-21's row, `00:234`; no fence. |
| G, F, H, P | none | No spec hunk. |

**So TRACK A's edits, all under §4, share a section with one slice: SL 8361, at `06` §4.1,** and no
block in that section is in TRACK A's text.

## Decision points

No DP is the planner's to rule. Each states a recommendation; **DP-4 and DP-5 are blocking**.

- **DP-1: where `model_validate` runs.** (a) **Two halves, one parser.** `audit-docs.py` check 40,
  stdlib, refuses an unmarked, unparsed or language-less block; `tests/test_spec_examples.py` loads
  that parser by path and validates. (b) `uv sync` in `docs.yml`, and audit-docs imports
  `model_schema`. (c) Pytest alone. **Recommendation (a).** (b) ends bare `python3
  scripts/audit-docs.py`, the command `CLAUDE.md` §0 binds to every spec change and every seat's
  route. (c) has no collision with LAST-2, but the command every spec edit runs would stay silent on
  an unmarked block. (a) departs from the essay's "in `scripts/audit-docs.py`" (`:170`), which `:182`
  leaves open.
- **DP-2: the marker.** (a) A fence token: ` ```json schema=RatingAlgorithm` or
  ` ```json illustrative`. (b) An adjacent `<!-- example: … -->` line. **Recommendation (a).** The
  token cannot drift from its block, shifts no line, and CommonMark reads the first word as the
  language. Its one cost is `test_objective_submission.py:533`.
- **DP-3: ordering (`:166-168`, the planner's choice, stated here for the maintainer's sight).**
  (a) **The marks ride SL 8373**, after TRACK A's text has merged, and the check is in gate mode from
  its first commit on `main`. (b) The marks land in TRACK A first. (c) Report-only first, then the
  switch. **Recommendation (a): one gate.** Under DP-2 (a), (b) puts a `backend/tests/` edit in a
  docs PR, so the docs-only gate no longer applies (common seat brief, item 30): a second code gate.
  (c) is one gate only as a last commit in one PR, where report-only never reaches `main` and buys
  nothing; merged apart it is two.
- **DP-4 (blocking): the ruling's scope.** (a) The 12 by the essay's rule; the 10 **U** rows are
  marked `illustrative` and carried by a new finding. (b) All 22. **Recommendation (b).** Marking a
  block `illustrative` while it contradicts an existing class would turn the check green over a live
  `CLAUDE.md` §0 disagreement: `01:329`, `01:346`, `03:374` and `07:248` each carry a key the class
  forbids. The essay's "10" is a product of a classifier its blind spots already doubt (`:110-112`).
  Cost: about 3 h more, docs, no gate. Fallback if TRACK A is late: (a) for what remains, each row
  named in the finding.
- **DP-5 (blocking): when, against the freeze.** (a) TRACK A seats at acceptance; SL 8373 queues
  behind M with the chain's additions, and gates before Wed 11 Nov 12:00 if the re-baseline at D's END
  shows the margin. Otherwise it stays the named exception and merges after the code freeze, as a
  tooling-only change. (b) All of it waits for the chain's end. (c) Both after the freeze.
  **Recommendation (a).** TRACK A holds no gate and shares one section with the chain, and the
  chain's order stands: D, F, run 3, A, C, H, R2, LAST-1, LAST-2 + T, G, M, then additions.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run. Items 1 and 2 apply to this plan.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py` prints no
   failing line except those for the working ids this file uses, and `python3 scripts/doc-index.py
   --check` agrees. After the mint both exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

TRACK A:

- **A1. Every row has a side.** The ruling holds one row per block of the 22 (or the 12, on DP-4),
  each naming the block, the class, and **spec wrong, code wrong, or fragment by design**. The count
  of rows equals T1's count. The rule of `FD-1381` `:139`: no example is matched to the code silently.
- **A2. Code wrong is its own finding.** Every code-wrong row names an `FD-`. No file outside
  `docs/` changes in this track: `git diff --name-only origin/main...HEAD` lists only `docs/`, quoted
  first in the log (common seat brief, item 30).
- **A3. No clash.** `git diff -U0 origin/main...HEAD -- docs/specs` hunks lie only in §4 sections, and
  none in a section a running build slice changes (`RL-1263` `:89`), re-measured on the day.
- **A4. The docs-only gate is green,** and `test_rating_declared_reads.py` plus
  `-k test_the_section_4_2_policies_array_validates_as_policy_entries` pass, since both read spec text.

SL 8373:

- **A5. The write set** is the Write set below, by `git diff --name-only origin/main...HEAD`.
- **A6. Rule first.** `git log --reverse` shows the skills' commit before the first commit touching
  `scripts/audit-docs.py` (`FD-1381` `:144-145`).
- **A7. Red by cause, in the LG before the green.** T4 to T6 fail first against the empty check; T7 to
  T10 are each shown red by the mutation Task S2 names, reverted and proved reverted. A fixture, import
  or `NameError` is not the red.
- **A8. Proven on broken input (`CLAUDE.md` §13).** T8: `c535b19d`'s §4.1 example, stored verbatim as a
  fixture and validated as `RatingAlgorithm`, fails, and the message holds `premium_ladder` and `FR-214`
  (`FD-1381` `:179`, which named that text; today's §4.1 passes, so the fixture is the input now).
- **A9. 0 unmarked, counted by the check.** `python3 scripts/audit-docs.py` prints
  `check 40: <n> json blocks: <s> schema, <i> illustrative, 0 unmarked` with `n = s + i`.
- **A10. The count cannot read clean by dropping blocks.** T9's second predicate, a plain line
  regex, equals the parser's `json` count and is above zero; the parser cut to column 0 goes red on
  `03:1006`, the shape the essay's own sweep missed.
- **A11. Every class-marked block passes.** `uv run pytest tests/test_spec_examples.py` passes, and
  the parametrised ids name each block as `<file>:<line>`.
- **A12. The exemption set only shrinks.** `ILLUSTRATIVE_CEILING` equals the count at the head; a new
  `illustrative` block fails until the constant is raised in a reviewed diff.
- **A13. The readers still read.** `test_rating_declared_reads.py`, the `-k` test of A4, and
  `tests/test_audit_docs_check_prefixes.py` pass; the last holds check 40's prefix.
- **A14. The gate.** One SOLO full gate on the re-merged head, every rc quoted. Audit-docs at the head
  against its base differs only by check 40's note line.

## Global Constraints

- **G1. No product behaviour.** Nothing under `backend/src/`, `packages/*/src/` or `frontend/`.
- **G2. `audit-docs.py` stays stdlib.** No import of `model_schema` or pydantic in `scripts/`.
- **G3. No side picked by the executor.** A block whose fix is not in the ruling is a STOP.
- **G4. A failing test is never weakened** (common seat brief, item 13). `06:346`'s test keeps its
  asserts; only its regex widens.
- **G5. Requirement and section ids are permanent** (`CLAUDE.md` §5).
- **G6. No range of ids in any file this plan writes.**
- **G7. Line numbers are re-derived at each base.** This plan's are `bdad1322`'s.

## Needs

- **Seats:** one decision-maker for T2; one executor for T3 and for SL 8373, model per the role file;
  one auditor. Audits take precedence when the cap binds (to-lead "2026-11-05 15:55:35 GMT").
- **Ids, not reserved:** one `RL-` for T2; one `FD-` per code-wrong row; on DP-4 (a), one `FD-` for the
  carry. PL-2053, SL 8373 and LG 8374 are held.
- **Gate cost:** **one SOLO full gate, about 2.5 h, for SL 8373**, no DB window of its own, no compose
  build, no timed path changed. **TRACK A: no gate slot**, the docs-only gate only, on the lead's
  light route. Hours, gate not counted: TRACK A about 10 h under DP-4 (b), about 7 h under (a); SL
  8373 about 7 h. Total about 17 h against the triage's 16, since the population grew from 10 to 22.
- **Docker, redis, DB of its own, NFR VM:** nothing.

## Tasks

### TRACK A: the adjudication and the spec text (docs)

**Task T1: re-derive at the base.** Run the sweep at TRACK A's base, reading indented fences. A count
that moved from Evidence is named in the ruling. Re-read every row's error by `model_validate`.

**Task T2: the ruling (decision-maker, not the planner).** One row per block, as A1. For **fragment
by design**, the fix is either the fields the class needs or `illustrative`, and the row says which.
`06:346` cites `FD-1281` and stays `illustrative` until that closes.

**Task T3: the spec text (executor).** Apply each spec-wrong and fragment row, one commit per spec,
each citing the ruling. Replace the placeholders in `01:809` and `02:1861` with literal uuids, so both
validate. Change no fence line: the marks are S4's. Stop on any block outside the ruling. Docs-only
gate, then a docs PR; run A4's two tests.

### SL 8373: the check (code). Its row: scope A5 to A14; lane WK-1178; after TRACK A's merge, LAST-2 and SL 8361

**Files:** see Write set. **Base:** a head holding TRACK A's merge.

- [ ] **Step S1: the rule, first commit.** Add to `.claude/skills/spec-change/SKILL.md`, under "The
  rules that are easy to break", and refresh its `Verified` line:

```markdown
**Every JSON example declares what it is, on its fence.** ` ```json schema=<Class>` names a class in
`model_schema.__all__`, and the block must pass `<Class>.model_validate` in full. ` ```json illustrative`
marks a fragment or a shape `model-schema` does not define; the block is listed, never validated.
An `illustrative` mark on a block that contradicts an existing class is a silent pick (`CLAUDE.md` §0).
Every fence in `docs/specs/` declares a language.
```

  Add check 40's row to the table in `.claude/skills/docs-audit/SKILL.md`, and the numbered line to
  the docstring of `scripts/audit-docs.py`.

- [ ] **Step S2: the failing tests, committed alone.** Create `tests/test_spec_examples.py`:

| Test | Planted input | Red, by cause |
|---|---|---|
| T4 | a `json` fence with no marker | the empty check records no failure |
| T5 | a bare fence | the same |
| T6 | `json schema=Dataset` over `{` | the same |
| T7 | `schema=NoSuchClass` | mutation: drop `_validate`'s assert; `None.model_validate` is not the refusal |
| T8 | `c535b19d`'s §4.1, verbatim, as `tests/fixtures/spec-examples/ra-c535b19d.json` | mutation: `_validate` returns before `model_validate`; DID NOT RAISE |
| T9 | every real spec | mutation: `_SPEC_FENCE_RE` loses `\s{0,3}`; 61 against 62 |
| T10 | every real spec | mutation: `ILLUSTRATIVE_CEILING` less 1 |

First add `SpecFence`, `spec_fences` and an empty `check_spec_examples` (S3's text, its body `pass`),
so a red is never an import error. T4 to T6 need the empty check; the mutations run after S3 and S4.

```python
"""`docs/specs/` JSON examples against `model-schema` (FD-1381). Correctness of the audit tool."""
import importlib.util, json, pathlib, re, sys

import model_schema
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ILLUSTRATIVE_CEILING = 0  # S4 sets this to the count at the head; it may only fall.
_JSON_FENCE = re.compile(r"^\s*```json\b")


def _audit():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location("audit_docs_for_examples", ROOT / "scripts/audit-docs.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _audit()
BLOCKS = [b for p in sorted((ROOT / "docs/specs").glob("*.md")) for b in AUDIT.spec_fences(p)]
MARKED = [b for b in BLOCKS if b.schema]


def _validate(schema: str, body: str) -> None:
    cls = getattr(model_schema, schema, None)
    assert cls is not None, f"{schema} is not in model_schema"
    cls.model_validate(json.loads(body))


@pytest.mark.parametrize("block", MARKED, ids=lambda b: f"{b.path.name}:{b.line}")
def test_a_class_marked_example_validates_in_full(block) -> None:
    _validate(block.schema, block.body)


@pytest.mark.parametrize(
    ("info", "body", "expected"),
    [
        ("json", "{}", "no schema= or illustrative marker"),
        ("", "{}", "declares no language"),
        ("json schema=Dataset", "{", "does not parse"),
    ],
)
def test_check_40_refuses(tmp_path, monkeypatch, info, body, expected) -> None:
    spec = tmp_path / "99-planted.md"
    spec.write_text(f"```{info}\n{body}\n```\n", encoding="utf-8")
    failures: list[str] = []
    monkeypatch.setattr(AUDIT, "fail", failures.append)
    AUDIT.check_spec_examples([spec])
    assert [m for m in failures if m.startswith("check 40: ") and expected in m]


def test_an_unknown_class_is_refused() -> None:
    with pytest.raises(AssertionError, match="NoSuchClass"):
        _validate("NoSuchClass", "{}")


def test_the_example_the_finding_named_fails() -> None:
    body = (ROOT / "tests/fixtures/spec-examples/ra-c535b19d.json").read_text("utf-8")
    with pytest.raises(ValueError, match=r"premium_ladder.*FR-214"):
        _validate("RatingAlgorithm", body)


def test_the_census_is_a_second_reading_of_the_same_lines() -> None:
    lines = [ln for p in (ROOT / "docs/specs").glob("*.md") for ln in p.read_text("utf-8").splitlines()]
    json_lines = sum(bool(_JSON_FENCE.match(ln)) for ln in lines)
    assert json_lines > 0
    assert json_lines == sum(b.language == "json" for b in BLOCKS)


def test_the_exemption_set_only_shrinks() -> None:
    assert sum(b.illustrative for b in BLOCKS) <= ILLUSTRATIVE_CEILING
```

  The fixture is `git show c535b19d:docs/specs/03-rating-engine.md`'s first `json` block after
  `### 4.1 `. Run: `run-small.sh` on this file. Paste each red into the LG.

- [ ] **Step S3: the check.** In `scripts/audit-docs.py`, directly above `def main`, and called at the
  tail of `main()` after `check_register_grammar()`. Not beside that function's own definition, where
  LAST-2 has a hunk:

```python
_SPEC_FENCE_RE: Final = re.compile(r"^\s{0,3}```(?P<info>.*)$")
_EXAMPLE_MARKER_RE: Final = re.compile(r"^json (?:schema=(?P<schema>[A-Z]\w*)|(?P<illustrative>illustrative))$")


@dataclass(frozen=True)
class SpecFence:
    """One fenced block of a spec. `tests/test_spec_examples.py` reads this parser by path (FD-1381)."""

    path: pathlib.Path
    line: int
    info: str
    body: str

    @property
    def language(self) -> str:
        return self.info.split(" ", 1)[0]

    @property
    def schema(self) -> str | None:
        marker = _EXAMPLE_MARKER_RE.match(self.info)
        return marker["schema"] if marker else None

    @property
    def illustrative(self) -> bool:
        marker = _EXAMPLE_MARKER_RE.match(self.info)
        return bool(marker and marker["illustrative"])


def spec_fences(path: pathlib.Path) -> list[SpecFence]:
    """Every fenced block, indented ones included: a list-indented fence is still a fence."""
    lines = path.read_text(encoding="utf-8").splitlines()
    fences: list[SpecFence] = []
    i = 0
    while i < len(lines):
        opening = _SPEC_FENCE_RE.match(lines[i])
        if opening is None:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and _SPEC_FENCE_RE.match(lines[j]) is None:
            j += 1
        fences.append(SpecFence(path, i + 1, opening["info"].strip(), "\n".join(lines[i + 1 : j])))
        i = j + 1
    return fences


def check_spec_examples(specs: list[pathlib.Path]) -> None:
    """Check 40: every fence declares a language; every json block is marked (FD-1381)."""
    total = schema = illustrative = unmarked = 0
    for spec in specs:
        for block in spec_fences(spec):
            where = f"{block.path.name}:{block.line}"
            if not block.language:
                fail(f"check 40: {where}: a fence declares no language")
                continue
            if block.language != "json":
                continue
            total += 1
            if block.schema:
                schema += 1
                try:
                    json.loads(block.body)
                except ValueError as exc:
                    fail(f"check 40: {where}: schema={block.schema} does not parse: {exc}")
            elif block.illustrative:
                illustrative += 1
            else:
                unmarked += 1
                fail(f"check 40: {where}: json block has no schema= or illustrative marker")
    notes.append(f"check 40: {total} json blocks: {schema} schema, {illustrative} illustrative, {unmarked} unmarked")
```

  `json.loads` needs no dedent, since JSON ignores the indent. `fail`, `notes` and `specs` are named at
  `scripts/audit-docs.py:255`, `:252` and `:3701`; `rel` is a local there, so the function uses
  `block.path.name`. T4 to T6 turn green; check 40 is now red on the real specs, as it must be. Commit.

- [ ] **Step S4: the marks and the one regex, one commit.** Widen
  `backend/tests/test_objective_submission.py:533` to `r"```json[^\n]*\n(.*?)\n```"`. Mark all 62 blocks
  from T1's table and the ruling: passing and fixed blocks `schema=<Class>`, the rest `illustrative`.
  Retag the 4 bare blocks (`00:14`, `00:79`, `00:269`, `00:360`) as `text`. Set `ILLUSTRATIVE_CEILING` to
  the count. Run: `python3 scripts/audit-docs.py` for A9; `run-small.sh` on the test file; then T7 to
  T10's mutations, each reverted. A block that fails is a STOP (G3), never a re-mark.

- [ ] **Step S5: the re-merge and the gate.** Re-merge `origin/main`, re-measure A3's overlap, run A13
  and the eight docs-audit files, then one SOLO gate (A14). Item 31's set gains this file by the lead's
  dated line (Hand-off).

### Write set

SL 8373: `scripts/audit-docs.py`; new `tests/test_spec_examples.py` and
`tests/fixtures/spec-examples/ra-c535b19d.json`; `backend/tests/test_objective_submission.py` (one line);
`docs/specs/00` to `07` (fence lines only); `.claude/skills/spec-change/SKILL.md`;
`.claude/skills/docs-audit/SKILL.md`; the LG; `docs/roadmap.md` (the SL row); this plan (`status:` only);
`docs/INDEX.md`. TRACK A: `docs/specs/` §4 sections, the `RL-`, any new `FD-` and `docs/findings/register.md`.

### Files shared

Named row by row under **The chain's collisions**. In short: `scripts/audit-docs.py` with LAST-2, no hunk
in common; `06` §4.1 with SL 8361, one fence line; `docs/INDEX.md` and `docs/roadmap.md` with every
slice, by re-merge.

## Hand-off (not this plan's writes)

- **The maintainer:** DP-1 to DP-5, and the acceptance.
- **The lead:** the ids in Needs; a dated line adding `tests/test_spec_examples.py` to the docs-only
  gate's list and item 31's set (common seat brief, items 30 and 31), or a docs batch that goes
  red on it is caught at CI, not locally.
- **The auditor:** the closing act on `FD-1381` and its register row, with a dated line that the essay's
  `:149` date has passed and its "10" reads 12 here, and that `03:233` closed under `FD-1374`.
- **A later Work:** when `model-schema` gains a monitoring, service-account or role shape, a block in
  the no-class row moves to `schema=` and `ILLUSTRATIVE_CEILING` falls.

## Self-review

1. **Spec coverage.** Discharge (1): T1, T2, T3. (2): S1 rule first, S3 and S2 the check, A8 the proof.
   (3): A9. Proposed check steps 1 to 4 (`:172-177`): S3; the class by marker, not inference. 2. **Every
   cite read** at `bdad1322`; the triage's `:166` is the essay's, and the essay's own line numbers were
   re-read here. 3. **Placeholder scan:** `<Class>` per block comes from T1 and the ruling, by design. 4. **Names:** `spec_fences`, `SpecFence`,
   `check_spec_examples`, `ILLUSTRATIVE_CEILING` agree between S2, S3 and S4. 5. **Sums:** 62 and 76
   above are recounted; 12 + 22 + 2 + 6 + 20 = 62. 6. **Calendar:** read from `date`: Wed 11, Thu 12,
   Fri 13 Nov. 7. **No range of requirement ids.** 8. **The plan decides nothing:** five DPs, open.

## Dated lines

- **2026-11-05 17:46:59 GMT — block count 62 → 63 (T3, `RL-2054` row 19; `to-lead.md` "2026-11-05 16:31:45 GMT" (2)).** Row 19's block at `06:462` splits into two `json` blocks, so the `json` blocks of `docs/specs/*.md` are 63, not 62. Every "62" above (the Evidence table, "The 62, by what each needs", S4's "all 62 blocks", T9's "61 against 62", the self-review sums) reads 63 from this line: the 12 + 22 + 2 + 6 + 20 = 62 sum gains the one block, and S4's end state is `schema=` 32 + `illustrative` 31 = 63 (`RL-2054` "End state"). T3 sets no mark: the marks are S4's.
- **2026-11-05 17:46:59 GMT — A14's "the re-merged head" is SL 8381's head (`to-lead.md` "2026-11-05 16:46:26 GMT", "2026-11-05 16:55:19 GMT").** Where A14 says "One SOLO full gate on the re-merged head", the head is SL 8381's, not SL 8373's branch tip alone.
- **2026-11-05 17:47:05 GMT — row 5 (`01:550`, `ValidationReport`) is code wrong, finding FD 8379 (working id; `RL-2054`, `to-lead.md` "2026-11-05 16:31:45 GMT" (1)).** MEDIUM, owner WK-1178. The block keeps `overall` and `counts` and is marked `illustrative` by S4, naming FD 8379, until the fix lands; `ILLUSTRATIVE_CEILING` counts it.

## Audit — TRACK A (PL-2053 T3 against RL-2054), aud-t3, 2026-11-05

Object: `origin/main...fd5e5d81` (detached worktree `aud-t3`, tree `5d24a34e`). Proposals only; the lead adopts.

| Check | Result |
|---|---|
| RL-2054 A1: 22 rows with a side | `grep -cE '^\| [0-9]+ \| `[0-9]{2}:[0-9]+` \|'` prints 22. Counts: 10 spec wrong, 9 fragment, 1 spec ahead, 2 code wrong (rows 5 and 18). They sum to 22 and agree with the title and INDEX row. |
| Rows 1-4, 6-14, 16, 19-22 applied as ruled | DELIVERED. Each ruled fix is in the diff, in a §4 section (A3). |
| Rows 15, 17, 18 no text change | CONFIRMED. No hunk in `03` near 954, none in `04`, none at `06:346`. |
| Row 5 | Spec limbs only; `overall` and `counts` kept; `evidence_blob` removed; dated "Clarified" line at `01` §4.6 names FD 8379 (working id) and WK-1178. PL-2053 has the matching dated line. |
| Row 19 | SPLIT. Block 1 validates as ApprovalRequest. Block 2 has the four keys as printed. The dated line names WK-677 and RL-1522 DP-4 (a) and says FR-352 is not amended. The older note is not edited. |
| Row 21 | `07:232` reworded; block narrowed to `JobError`. |
| Hidden validators `01:224`, `02:544`, `02:690` | DELIVERED: `latest_version_status`; a `5 → G4` mapping entry; `offset` log_column. All three blocks pass in full. |
| Dated notes not edited | `01` 2026-08-15 note, `02` 2026-08-18 and 2026-09-30 notes, `07` 2026-10-10 note: no deletions. Each has an appended dated line (rows 4, 12, 22). |
| PL-2053 dated lines | 62→63 (names RL-2054 row 19), A14 head = SL 8381's head, row 5 names FD 8379. |
| MARKS | No fence line in the diff carries `schema=` or `illustrative`. The lead's brief said otherwise and was wrong. The marks are S4's. |
| Fence census (own predicate `^\s{0,3}` + 3 backticks) | 154 fence lines = 77 blocks. json per file: 2, 8, 19, 15, 4, 5, 5, 5 = 63. |
| Own validation (`scratch/aud-t3/val.py`, tools-main venv, read-only) | 20 blocks PASS `model_validate`, validators included: 00:318, 01:224, 01:333, 01:351, 01:848, 02:421, 02:545, 02:691, 02:730, 02:903, 02:1102, 02:1150, 02:1556, 02:1887, 03:374, 03:1021, 06:462, 06:553, 07:234 (as JobError), 07:246. Row 5 (01:582) FAILs with exactly 2 errors, `overall` and `counts` extra_forbidden, as ruled. |
| audit-docs at the head | rc=1. FAILED (2), both check 31: allocation gaps 2010..8372 and 8373..8375. These are working-id gaps (8373 SL and 8374 LG reserved and unfiled; 8379 not filed). Classified expected before the mint (A1 of the plan's Acceptance Standard). Not run on base. Log: `scratch/aud-t3/audit-docs.log`. |
| doc-index --check | rc=0, byte-stable. Log: `scratch/aud-t3/doc-index.log`. |

Does any requirement's meaning change beyond the example? No. Two factual sentences are new: `01` §4.6 says the route does not yet serialise `overall` and `counts`, and `03` §4.2 says an immutable version cannot hold a diff. Both are ruled in RL-2054 rows 5 and 14. No FR is amended, and the OQ mirrors and skills-map are not touched (no dependency moved).
Does a changed example disagree with prose? None found. `02:1671` (§4.9's `kinds`) and `03:468` (`diff_vs_seed` as a function) still hold.

Four verdicts: no requirement is left without evidence by TRACK A. Row 19's FR-352 limbs are deferred, owner WK-677 (RL-1522). Row 5's wire defect is FD 8379, owner WK-1178. Row 18 is carried by FD-1281.

Nit (non-blocking): row 12's sentence moved out of `_note` sits after the 2026-09-30 amendment, not directly under the block.

Item 42 (the `SL-` row's status at `origin/main`, read 2026-11-06 at 0510d2c4e5e1): no `SL-` row exists for SL 8373 on main or on this head (`git grep -nE '(SL|LG)[- ]?(8373|8374)\b' -- docs/roadmap.md docs/ledgers` prints nothing); both ids are reserved and unfiled. There is no `active` row to close, and none is claimed closed. The marks are S4's.

No gate ran on this docs track. The audit above, the eight docs-audit files and the DB-free spec-readers are its evidence; the DB-backed modules are owed to CI.

**Lead's adoption (from-lead, 2026-11-05 18:02:39 GMT, verbatim):** "aud-t3 ADOPTED, released: TRACK A @fd5e5d81: nothing NOT MET; 20 blocks validate, row 5 fails only on overall + counts as ruled; 8 spec-reading files pass; 2 fail on the working-id gap, re-read at the mint (test_audit_docs_ids's message unread by the auditor: read at the mint); 3 DB-backed owed to CI. Drafts scratch/aud-t3/. Mint after #1434."

**Mint record (2026-11-06):** working ids 8372 and 8375 became PL-2053 and RL-2054, minted contiguously after LG-2052 on origin/main 0510d2c4e5e1. FD 8379 is not filed on this head and stays a working id in space form. SL 8373 and LG 8374 stay reserved. This PR's number, squash commit and merge date are written at the merge's date-of-record.

*(Dated note, 2026-11-07, docs batch 16, by the executor: the row at line 150, `A SL 8325`, names the slice minted as **SL-2075** (PL-2074, LG-2076, #1456). The plan is frozen at its date and line 150 is not edited.)*
