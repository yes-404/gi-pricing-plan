---
id: PL-2040
family: plan
kind: map
title: WK-1178 — FD-2032's fix, a bulk operation is refused where the column's value type gives its result no meaning, SL-2041 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8388, minted 2026-11-06
owner: planner
tree: cda3c0dc326d4313add551693e3180d3b1e05a11
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1927, FD-2032, SL-2041, LG-2042, FR-233, FR-228, FR-234]
---

# PL-2040 — WK-1178: FD-2032's fix. A bulk operation is refused by value type (SL-2041, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"): a new `PL-` that `relates:` WK-1178's plan,
> `PL-1927`, and leaves it unedited. It holds one slice row, SL-2041. The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/spec-change` and
> `.claude/skills/python-test`. FD-2032, PL-2040, SL-2041 and LG-2042 were drafted under working
> ids 8387, 8388, 8389 and 8390, reserved by the lead, and minted on 2026-11-06 (`mint-repoint.py`).
> Nothing from 8391 is this plan's.

**Architecture:** one declared matrix in `pricing_core/rate_tables/operations.py`, read first in
each of the four operations. The refusal is a code-named `ValueError`, which the existing
`_map_operation_error` turns into a 422. No route, contract or frontend change.

**Tech Stack:** Python 3.12, `pricing-core`, FastAPI, pytest.

**Spec:** `docs/specs/03-rating-engine.md` §3.3 FR-233; `docs/specs/04-optimisation.md` §4.4.

## Goal

`uplift_table` and `uplift_by_filter` are refused on a `count` column, `rebase_to_level` runs only
on a `relativity` column, and the spec says so at FR-233.

## Authority

- **The finding.** FD-2032, HIGH, owner WK-1178. Filed by the maintainer's entry
  "2026-11-05 17:20:30 GMT", raised by "2026-11-05 17:29:19 GMT" (`to-lead.md`). HIGH is for the
  type of error, not a live incident (same entry).
- **The ruling, every clause of 17:29:19 taken as a closed decision here:** "uplift and uplift by
  filter refused on `count`; rebase runs only on `relativity`. It sets no rate, rounds nothing,
  moves no price on a correct table, so it doesn't wait for §14 or the user's rounding decision."
  "ROUTE: FR-233 dated clause first, then the refusal at the op, spec and code one change." "OWN
  SLICE, OWN LG, STACKED ON R2 … it takes R2's gate if built before that gate starts, no extra
  gate; if not, it gates after R2. R2 is never delayed for it."
- **The matrix.** `~/gi-pricing-plan.local/scratch/dm-fd8383/oq-draft.md` (sha256 prefix
  `99d83663edf8`) `:196-200`, accepted by the same entry, reproduced below. The FR-233 wording
  starts from the draft's proposal (`:204`).
- **The seating.** `brief-plan-fd8387-2026-11-05.md` (sha256 prefix `e68b153f96c5`).
- **The calendar.** Code freeze Thu 12 Nov 2026 (the entry "2026-11-05 09:58:58 GMT"; weekdays read
  with `date -d`).

### The matrix (16 cells: 5 refused, 11 allowed)

| | `relativity` | `percentage` | `money_minor` | `count` |
|---|---|---|---|---|
| `uplift_table` | allow | allow | allow | **refuse** |
| `uplift_by_filter` | allow | allow | allow | **refuse** |
| `rebase_to_level` | allow | **refuse** | **refuse** | **refuse** |
| `floor_and_cap` | allow | allow | allow | allow |

## Evidence

Read at `cda3c0dc326d4313add551693e3180d3b1e05a11` (R2's head, `sl-8345-r2-cell-hard-error`,
**a local branch with no `origin` ref at this date**), not run. Measurements are the DM's:
`measure_types.out` and `measure_engine.out` in the same scratch directory.

- **No type is consulted.** `_dispatch_operation` (`backend/src/app/platform/rate_tables.py:1513`)
  and the four operations (`packages/pricing-core/src/pricing_core/rate_tables/operations.py` :751,
  :776, :814, :842) never read `table.value.type`. Measured: M2 turns a fee of `2500` into `1`, and
  M5 moves a quote at F from 18500 to 15001 with a golden quote at C still passing.
- **The refusal has a route already.** `bulk_operation` (`rate_tables.py:1575-1585`) catches
  `ValueError` and calls `_map_operation_error` (`:129`), which answers 422 with the part before the
  first `": "` as the code, when that part is upper-case with an underscore (`:136`). `PlatformError`
  refuses an unregistered code (`backend/src/app/errors.py:467`), so the code is registered in the
  block at `errors.py:364-375`. `_VALIDATION_CODES` (`rate_tables.py:117`) is not touched.
- **The name.** `BULK_OPERATION_NOT_APPLICABLE`. The draft's `BULK_OPERATION_VALUE_TYPE_REFUSED` is
  not used: `git show cda3c0dc:backend/src/app/errors.py | grep -c '_REFUSED"'` prints 0, and the same
  command with `'_NOT_APPLICABLE"'` prints 2 (`METRIC_NOT_APPLICABLE`, `OBJECTIVE_NOT_APPLICABLE`),
  the catalogue's form for "this does not apply to that". The operations' own neighbours,
  `REBASE_NO_MATCH`, `REBASE_AMBIGUOUS`, `REBASE_ZERO_REFERENCE` and `FLOOR_ABOVE_CAP`, name one
  operation each; this code covers three. `git grep -c BULK_OPERATION_NOT_APPLICABLE cda3c0dc` finds
  nothing.
- **Contract and frontend reach: none.** `docs/contracts/` names no bulk-operation code: `git grep -n
  -E 'REBASE_NO_MATCH|FLOOR_ABOVE_CAP' cda3c0dc -- docs/contracts frontend/src` prints nothing. The
  route already declares 422 (`api/rate_tables.py:183-189`, `problems(401, 403, 404, 409, 422)`), so
  `generate-contracts.py --check` stays rc 0. `BulkOperationDialog.vue:52-54` shows
  `error.problem.detail ?? error.problem.title` for any `ProblemError`, so the refusal reads in the
  dialog with no change. `QuoteError` (`QuoteSandboxView.vue`) is the quote sandbox; a rate-table
  operation does not reach it. The dialog keeps offering all four operations on every table; hiding
  one by type is not in the ruling.
- **FR-303 is unaffected.** `04` §4.4 says FR-286's `segment_factor` and `global_levers` materialise
  through these operations. That is a later phase, it uses uplift, and uplift on `count` has no
  meaning there either.

### THE CHECK (result: **no hit**)

The ruling asks: no existing path, seed, test fixture, demo or journey rebases a non-relativity
column or uplifts a `count` column. A hit is a STOP to the lead. Run at
`cda3c0dc326d4313add551693e3180d3b1e05a11` and at `origin/main` `bdad132291fdc05fe233d3ddc946e413dcbd2e1f`,
identical result.

**Step 1, every caller, the whole tree outside `docs/`** (29 files at both trees):

```bash
CALL='rebase_to_level|uplift_table|uplift_by_filter|bulk-operation|bulk_operation|bulkOperat|BulkOperat'
git grep -l -E "$CALL" <tree> -- ':!docs'
```

**Step 2, a non-relativity declaration in any caller file:**

```bash
TYPE='RateTableValueType\.(MONEY_MINOR|PERCENTAGE|COUNT)|RateTableValueType\(|in RateTableValueType|\(RateTableValueType\)|["'"'"']?type["'"'"']?\s*[:=]\s*(["'"'"'])(money_minor|percentage|count)["'"'"']'
git grep -l -E "$CALL" <tree> -- ':!docs' | sed "s/^<tree>://" | xargs git grep -n -E "$TYPE" <tree> --
```

It prints one line, `packages/model-schema/src/model_schema/rating.py:1178`, the enum's own
definition. The instrument was shown red: given the four planted lines `"type": "count",`,
`type='percentage'`, `type=RateTableValueType.MONEY_MINOR` and `"type": "relativity",`, it matched 3.

**Step 3, a differently built check, because a value column's `type` often sits on its own line:**
an AST walk of every `.py` file outside `docs/`, taking each dict with `name`, `type` and `unit` keys
and each `RateTableValue(...)` call.

```python
import ast, subprocess, sys
R, T = sys.argv[1], sys.argv[2]
files = subprocess.run(["git", "-C", R, "ls-tree", "-r", "--name-only", T],
                       capture_output=True, text=True).stdout.split()
total, hits = 0, []
for f in (p for p in files if p.endswith(".py") and not p.startswith("docs/")):
    src = subprocess.run(["git", "-C", R, "show", f"{T}:{f}"], capture_output=True, text=True).stdout
    try:
        tree = ast.parse(src)
    except SyntaxError:
        continue
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            d = {k.value: v for k, v in zip(n.keys, n.values) if isinstance(k, ast.Constant)}
            if {"name", "type", "unit"} <= set(d):
                total += 1
                x = d["type"]
                if not (isinstance(x, ast.Constant) and x.value == "relativity"):
                    hits.append((f, n.lineno, ast.unparse(x)))
        if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == "RateTableValue":
            total += 1
            x = {k.arg: k.value for k in n.keywords}.get("type")
            ok = (isinstance(x, ast.Constant) and x.value == "relativity") or (
                isinstance(x, ast.Attribute) and x.attr == "RELATIVITY")
            if not ok:
                hits.append((f, n.lineno, ast.unparse(x) if x else "?"))
print("declarations", total)
for h in hits:
    print(h)
```

It prints `declarations 36` and two hits, both `packages/model-schema/tests/test_rate_tables.py`:
`:85` (`value_type`, the loop proving the four types construct) and `:97` (`'invalid'`, the refusal
of a bad type). Neither runs an operation, and that test file does not import `pricing_core`
(`git grep -n pricing_core cda3c0dc -- packages/model-schema/tests/test_rate_tables.py` prints
nothing). All 18 `examples/fremtpl2/rating/*.rate-table.*.json` read `relativity` (a `json.load` of
`["value"]["type"]`, `uniq -c`).

**The one journey bulk call** (`examples/fremtpl2/journey.py:415-423`, step A4) is `uplift_table` on
a table `seed_from_model` made, which is `relativity`. `WF-699` A4 says "the expense table"; whichever of
`relativity`, `percentage` or `money_minor` such a table declares, uplift stays allowed.

**Limits.** This reads code, not stored rows: no DB was read (the seat's ban). It says nothing about
a table written by hand into a live database. A version stored before the clause keeps its cells.

**A fact the check surfaced, for the lead and the maintainer.** No shipped route can create a
non-relativity table. `RateTableRow(` is built outside tests only at `rate_tables.py:204`, in
`seed_from_model`, and `RateTableVersionRow(` only at `:1450`, in `_persist_new_version`.
`seed_from_model` always declares `RateTableValueType.RELATIVITY` (`operations.py:247-253`). Edit,
import and bulk operation copy the baseline's definition, and `03` §5.1 lists no create route for a
hand-authored table, though FR-228 declares four value types. So all 5 refused cells, and M2 and M5,
are reachable today only by a row written directly. **The ruling is not reopened by this**: the
refusal is still right for the day such a table can be authored. It does mean the route-level test
inserts its table directly (T2), and it is a limit the FD essay should state.

## Decision points

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-1 | Who files FD-2032's essay and register row? No ref holds them: `git for-each-ref` shows no branch with the id, and the closing act needs a record to close. | (a) **The slice's auditor** writes essay and register row in the single commit that also carries the closing act and the LG Audit section, from the DM's draft and the two entries. (b) The lead's batch 12 files them first, and the slice closes them after re-merging. | **(a).** `FD-` is the auditor's family, the record and its closure then land in one PR, and the slice waits on no batch. (b) stands if batch 12 is already staged. |
| DP-2 | Does the slice get a DB window, for the route reds? | (a) **One window**, granted by the lead, on the terms in "DB window" below. (b) The route tests are first run by the gate, so no route red exists before green. | **(a).** The ruling says "through the route", and A3 needs the route's red. (b) would lose the red. |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run on the slice's tree. Items 1 and 2 apply
to this plan. A1 to A14 apply to the slice. `<R2>` is the R2 head the slice stands on: until R2
merges, read `origin/main...HEAD` as `<R2>...HEAD`.

1. **This delta passes the docs checks on its own branch.** At the branch head, `python3
   scripts/audit-docs.py` fails only on its working ids, expected until the mint. After the mint,
   `python3 scripts/audit-docs.py` and `python3 scripts/doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

The slice, SL-2041:

- **A1. The write set.** `git diff --name-only <R2>...HEAD` lists only
  `packages/pricing-core/src/pricing_core/rate_tables/operations.py`,
  `backend/src/app/errors.py`, `packages/pricing-core/tests/test_rate_table_bulk_ops.py`,
  `backend/tests/test_api_rate_tables.py`, `docs/specs/03-rating-engine.md`,
  `docs/specs/04-optimisation.md`, LG-2042, this plan, `docs/INDEX.md`, `docs/roadmap.md` (the SL
  row), FD-2032's essay and `docs/findings/register.md`, plus the 63 docs-only paths of
  `2f108b1e..bdad1322` that T0's merge brings, listed by name in the LG. Nothing under `frontend/`,
  `docs/contracts/` or `deploy/`, no migration, and `backend/src/app/api/` and
  `backend/src/app/platform/` unchanged.
- **A2. Spec first.** `git log --reverse --format=%s <R2>..HEAD` shows the commit that adds the
  FR-233 clause before, or as, the commit that adds the refusal. `git grep -n
  BULK_OPERATION_NOT_APPLICABLE -- docs/specs` shows FR-233, the `03` §5.1 owned-code list and `04`
  §4.4.
- **A3. Red first on the 5 refused cells, at both levels, by cause.** LG-2042 quotes, for each of
  the 5 cells in T1 and in T2, the red at the tests-only commit: T1 `DID NOT RAISE`; T2 an assertion
  whose actual status is 201. A fixture, import or `NameError` is not the red. T2's reds name the DB
  window.
- **A4. Red on the 11 allowed cells, by a planted break.** They are green at base by design, and
  the LG says so. Each is shown red by plant P (the matrix emptied), at both levels; the LG quotes
  the summary line and the rc, then `git diff` empty after reverting. P is never committed.
- **A5. Green on all 16 at both levels.** The refused: T1 raises, and T2 answers 422 with `code ==
  "BULK_OPERATION_NOT_APPLICABLE"`, a detail naming the operation, the value type and
  `rate_table:<slug>@<version>`, and `_version_count(slug)` unchanged. The allowed: exact cells,
  `created_by_operation.kind` equal to the operation, and one version more.
- **A6. The refusal comes first.** T3: a refused `rebase_to_level` with an unknown `base_level` key
  is the refusal, not `FILTER_UNKNOWN_KEY`; a refused operation on a `parquet` version is the
  refusal, not `PARQUET_CELLS_UNAVAILABLE`.
- **A7. No price moves on a correct table.** `git diff <R2>...HEAD --
  packages/pricing-core/tests/test_rate_table_bulk_ops.py backend/tests/test_api_rate_tables.py`
  removes no line, so every existing bulk test passes unedited; `_format_value`, `_transform_rows`
  and `_new_version` are outside the diff of `operations.py`; `git diff <R2>...HEAD --stat --
  packages/pricing-core/src/pricing_core/rating examples` is empty.
- **A8. The dated sentence.** FR-233's clause carries "moves premiums unless the base rate offsets
  it", and the slice adds no behaviour for it.
- **A9. Ancestor check.** At the executor's FINAL and at the audit: `git merge-base --is-ancestor
  <this plan's latest draft head> <slice head>; echo $?` prints 0, and the same for `<R2>`, each
  quoted with the heads named (the entry "2026-11-05 16:57:37 GMT").
- **A10. The small runs,** through `run-small.sh`, each log `head=` first and `rc=` last (the common
  seat brief, item 37): `packages/pricing-core/tests/test_rate_table_bulk_ops.py` +
  `packages/pricing-core/tests/test_rate_table_operations.py`;
  `backend/tests/test_error_sinks.py` + `backend/tests/test_worker_raise_sites.py` +
  `packages/pricing-core/tests/test_quote_input_raise_sites.py`. `uv run ruff check .` rc 0, and
  `ruff format --check` on the changed `.py` files (item 16).
- **A11. The GREEN set** is derived by import closure (item 29), commands and list in the LG, for
  `operations.py`. `errors.py`'s closure is the whole backend, so the LG says so, and the gate's full
  suite is the decisive green for it.
- **A12. The gate, both halves,** at a head that contains SL-2041, every rc quoted: R2's gate if SL
  8389's FINAL is accepted before that gate starts, else a gate after R2, in the next free slot. No
  gate of its own otherwise. `generate-contracts.py --check` rc 0 (no contract diff),
  `req-coverage.py` rc 0, `audit-docs.py` rc 0 after the mint. The END read lists any window beside
  it.
- **A13. FD-2032's closing act, in the FD-1842 form, in the slice's own PR, by the slice's auditor,
  in one commit.** Essay `status: closed` with a `***Resolved <date>***` paragraph (closing act of
  the mint of SL-2041; WK-1178, LG-2042, PL-2040; "this PR, its number and squash written at the
  merge's date-of-record"; the delivered remedy; the reds in LG-2042), and register row resolved. The
  PR number, full squash sha and `mergedAt` are written at the next docs batch, as FD-1842's were.
  `docs/INDEX.md` regenerated after it (item 17).
- **A14. The LG Audit section.** LG-2042's `### Audit` is the auditor's: scope from FR-233 and this
  plan first, every matrix cell a row with its evidence, verdicts proposed, and the lead's adoption
  line before the record is filed. It rides the same commit as A13.

## Global Constraints

- **The ruling is closed.** No rate set, nothing rounded, no stored cell changed. `floor_and_cap`
  stays allowed on all four types.
- **Spec and code are one change** (`CLAUDE.md` §2), FR-233 first. FR-233's id does not move; the
  change is a dated clause.
- **`pricing-core` stays free of FastAPI** (`CLAUDE.md` §2): it raises a code-named `ValueError`, as
  its neighbours do.
- **No shape is hand-written twice.** `RateTableValueType` is imported, never restated as strings in
  code. The tests' matrix is a separate literal on purpose: it is what the code is checked against.
- **R2 is never delayed for this slice.** Any wait is SL-2041's.
- **No test is removed or weakened** (the common seat brief, item 13). `git stash` is banned; plant P
  is an edit and a `git checkout -- <file>`.
- **Money and decimals:** parameters stay decimal strings; tests compare `Decimal`, never float.

## Tasks

### SL-2041 — FD-2032's fix: a bulk operation is refused by value type

**The row.** Order 1 in this delta, stacked on R2 (SL-2038).

- **Scope:** T0 to T5 below.
- **Requirements:** FR-233 (`03` §3.3, amended); FR-228 (`03` §3.3, read: the four value types);
  FR-234 (`03` §3.3, read: the result validation that still runs).
- **Register:** FD-2032 (HIGH, owner WK-1178) closes in the slice's PR (A13).
- **Depends on:** DP-1 and DP-2 ruled; the maintainer's GO on this row.
- **Size:** 1 slice, about **4.5 h**: T0–T1 0.75 h, T2–T3 1.5 h, the window 0.5 h, T4–T5 and the LG
  0.75 h, the audit 1 h. A gate is outside the figure: R2's, or one after it. One `sonnet`
  executor (the executor charter's model line governs) and one auditor.
- **Schedule:** started Thu 5 Nov 2026 or Fri 6, merged before the Thu 12 Nov 2026 code freeze. If R2's
  gate starts first, the slice gates after R2.

**T0 — the branch.**

- [ ] `git -C /home/puzhenhao1989/gi-pricing-plan worktree add .claude/worktrees/sl-8389 -b
  sl-8389-bulk-value-type cda3c0dc326d4313add551693e3180d3b1e05a11`. The R2 branch is local, so the
  commit is named. If R2 has moved, use its current head and name it in the LG.
- [ ] Bring this plan in: `git -C <wt> fetch origin draft/pl-fd8387-2026-11-05` then `git -C <wt>
  merge --no-ff FETCH_HEAD`. It brings `2f108b1e..bdad1322`, 63 paths, all under `docs/`
  (`git diff --name-only 2f108b1e bdad1322 | grep -v '^docs/'` prints nothing).
  `git merge-tree --write-tree cda3c0dc draft/pl-fd8387-2026-11-05` reports one conflict, `docs/INDEX.md`:
  take theirs and regenerate (the common seat brief, item 5). Any other conflict is a STOP.
- [ ] `uv sync --directory <wt> --all-packages --frozen`.

**T1 — the failing function-level matrix** (`packages/pricing-core/tests/test_rate_table_bulk_ops.py`,
appended; DB-free). The tests match on the code's literal text and never import the constant, so the
red is `DID NOT RAISE`, not an `ImportError`. `Callable`, `RateTableValueType` and the four operations
are already imported (`:15-50`).

```python
_OPERATIONS: dict[str, Callable[[RateTableVersion], RateTableVersion]] = {
    "uplift_table": lambda t: uplift_table(t, percentage=Decimal("0.10")),
    "uplift_by_filter": lambda t: uplift_by_filter(
        t, percentage=Decimal("0.10"), filter={"driver_age_band": ["17-20"]}
    ),
    "rebase_to_level": lambda t: rebase_to_level(t, base_level={"driver_age_band": ["17-20"]}),
    "floor_and_cap": lambda t: floor_and_cap(t, floor=Decimal("3"), cap=Decimal("6")),
}

#: FR-233's matrix, written out here on purpose: the code is checked against this literal.
_REFUSED_CELLS = {
    ("uplift_table", "count"),
    ("uplift_by_filter", "count"),
    ("rebase_to_level", "percentage"),
    ("rebase_to_level", "money_minor"),
    ("rebase_to_level", "count"),
}
_ALL_CELLS = [
    (kind, value_type.value) for kind in _OPERATIONS for value_type in RateTableValueType
]

#: Cells 2, 4 and 8, after each operation.
_EXPECTED = {
    "uplift_table": ["2.2", "4.4", "8.8"],
    "uplift_by_filter": ["2.2", "4", "8"],
    "rebase_to_level": ["1", "2", "4"],
    "floor_and_cap": ["3", "4", "6"],
}


def _typed(value_type: str) -> RateTableVersion:
    return _version(
        rows=[
            {"driver_age_band": "17-20", "relativity": "2"},
            {"driver_age_band": "21-24", "relativity": "4"},
            {"driver_age_band": "25-29", "relativity": "8"},
        ],
        value=RateTableValue(
            name="relativity", type=RateTableValueType(value_type), unit="u", min=None, max=None
        ),
    )


class TestBulkOperationValueType:
    @pytest.mark.req("FR-233")
    @pytest.mark.parametrize(("kind", "value_type"), _ALL_CELLS)
    def test_the_matrix(self, kind: str, value_type: str) -> None:
        table = _typed(value_type)
        operate = _OPERATIONS[kind]
        if (kind, value_type) in _REFUSED_CELLS:
            with pytest.raises(ValueError, match=r"^BULK_OPERATION_NOT_APPLICABLE: ") as refused:
                operate(table)
            text = str(refused.value)
            assert kind in text
            assert value_type in text
            assert f"rate_table:{_SLUG}@{table.version}" in text
        else:
            result = operate(table)
            assert [Decimal(c["relativity"]) for c in _cells(result)] == [
                Decimal(v) for v in _EXPECTED[kind]
            ]
            assert result.version == table.version + 1
            assert result.created_by_operation is not None
            assert result.created_by_operation.kind == kind
```

- [ ] Commit T1 and T2 together as the tests-only commit, `test(pricing-core): …`, once T2 is
  written.
- [ ] Red: `run-small.sh` on this file. Expected: 5 failed by `DID NOT RAISE`, 11 passed, the rest
  of the file passed. The LG quotes the 5 lines and states that the 11 are green at base by design.

**T2 — the failing route-level matrix** (`backend/tests/test_api_rate_tables.py`, appended;
**needs a DB**, the `api_client` fixture). No route creates a non-relativity table (Evidence), so the
fixture inserts the rows, as `:605-640` and `:1368-1391` do. `RateTableCellRow` is added to the file's
`app.db.models` import.

```python
_ROUTE_BODIES: dict[str, dict[str, object]] = {
    "uplift_table": {"percentage": "0.10"},
    "uplift_by_filter": {"percentage": "0.10", "filter": {"driver_age_band": ["17-20"]}},
    "rebase_to_level": {"base_level": {"driver_age_band": ["17-20"]}},
    "floor_and_cap": {"floor": "3", "cap": "6"},
}
_ROUTE_REFUSED = {
    ("uplift_table", "count"),
    ("uplift_by_filter", "count"),
    ("rebase_to_level", "percentage"),
    ("rebase_to_level", "money_minor"),
    ("rebase_to_level", "count"),
}
_ROUTE_EXPECTED = {
    "uplift_table": ["2.2", "4.4", "8.8"],
    "uplift_by_filter": ["2.2", "4", "8"],
    "rebase_to_level": ["1", "2", "4"],
    "floor_and_cap": ["3", "4", "6"],
}


def _insert_typed_table(workspace_id: UUID, slug: str, value_type: str) -> None:
    """A table of the given value type. Written directly: no route creates one that is not
    `relativity` (`seed_from_model` is the only writer of a new table)."""
    table_id, version_id = uuid4(), uuid4()
    _insert_rows(
        [
            RateTableRow(
                id=table_id, workspace_id=workspace_id, slug=slug, current_version=1,
                created_by=uuid4(),
            ),
            RateTableVersionRow(
                id=version_id, workspace_id=workspace_id, rate_table_id=table_id,
                version_number=1, storage="rows",
                definition={
                    "slug": slug, "version": 1, "rateable": True, "storage": "rows",
                    "keys": [{"name": "driver_age_band", "type": "string", "banding_ref": None}],
                    "value": {
                        "name": "v", "type": value_type, "unit": "u", "min": None, "max": None,
                    },
                    "default_row": None,
                },
                change_note="direct insert", created_by=uuid4(),
            ),
            *[
                RateTableCellRow(version_id=version_id, key=[band], value=value)
                for band, value in (("17-20", "2"), ("21-24", "4"), ("25-29", "8"))
            ],
        ]
    )


@pytest.mark.req("FR-233")
@pytest.mark.parametrize("value_type", ["relativity", "percentage", "money_minor", "count"])
@pytest.mark.parametrize("kind", list(_ROUTE_BODIES))
def test_bulk_operation_value_type_matrix_at_the_route(
    api_client: TestClient, workspace_id, actuary, kind: str, value_type: str
) -> None:
    """FR-233's matrix through `POST .../bulk-operation`: a refused cell is a 422 and no
    version; an allowed cell is the same 201 as before the clause."""
    slug = _table_slug()
    _insert_typed_table(workspace_id, slug, value_type)

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body(kind, _ROUTE_BODIES[kind]),
        headers=actuary,
    )

    if (kind, value_type) in _ROUTE_REFUSED:
        assert response.status_code == 422, response.text
        body = response.json()
        assert body["code"] == "BULK_OPERATION_NOT_APPLICABLE"
        assert kind in body["detail"]
        assert value_type in body["detail"]
        assert f"rate_table:{slug}@1" in body["detail"]
        assert _version_count(slug) == 1
    else:
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["created_by_operation"]["kind"] == kind
        assert {row["driver_age_band"]: Decimal(row["v"]) for row in body["rows"]} == dict(
            zip(("17-20", "21-24", "25-29"), map(Decimal, _ROUTE_EXPECTED[kind]), strict=True)
        )
        assert _version_count(slug) == 2
```

`Decimal` is added to the file's imports (`:2027` imports it locally). The test compares by key,
because `_load_cells` (`rate_tables.py:1189`) reads with no `ORDER BY`.

**T3 — the spec, then the refusal.**

- [ ] `docs/specs/03-rating-engine.md` §3.3, append to FR-233's row (the clause's date is the commit's
  date; working ids are re-pointed at the mint):

  > *(Amended 2026-11-05, WK-1178, SL-2041, FD-2032 (HIGH), on the maintainer's entries "2026-11-05
  > 17:20:30 GMT" and "2026-11-05 17:29:19 GMT" and plan PL-2040: **a bulk operation is refused when
  > the column's declared value type gives its result no meaning.** `rebase_to_level` runs only on a
  > `relativity` column. `uplift_table` and `uplift_by_filter` are refused on a `count` column.
  > `floor_and_cap` runs on all four types. The refusal is **422** `BULK_OPERATION_NOT_APPLICABLE`,
  > naming the operation, the value type and the table, and no version is created. A version stored
  > before this clause keeps its cells (`00` FR-4). **A rebase on a `relativity` column moves premiums
  > unless the base rate offsets it:** the operation rescales the levels and changes no base rate, so
  > it is not premium-neutral by itself. **Revisit trigger:** a percentage rebase in real use lifts
  > that one cell.)*

- [ ] `docs/specs/03-rating-engine.md` §5.1: in the owned-code list after `REBASE_ZERO_REFERENCE`
  (`:1148`), add `BULK_OPERATION_NOT_APPLICABLE` with *(registered 2026-11-05, WK-1178, SL-2041, FD
  8387: **422** from `POST /api/v1/rate-tables/{slug}@{version}/bulk-operation` (FR-233); the detail
  names the operation, the value type and the table)*. After the note at `:1220-1227`, add one dated
  line: the bulk operations' named refusals gained this code; the note's "All ten" is its date's
  count.
- [ ] `docs/specs/04-optimisation.md` §4.4, after the `rebase_to_level` bullet: "*(Amended 2026-11-05,
  SL-2041, FD-2032: `03` FR-233 refuses `rebase_to_level` on any column but `relativity`, and both
  uplifts on `count`, with `BULK_OPERATION_NOT_APPLICABLE`.)*"
- [ ] `backend/src/app/errors.py`, in the W10-3C block, after `"REBASE_ZERO_REFERENCE",`:

```python
        # FR-233 as amended (SL-2041, FD-2032): the column's value type gives the operation no
        # meaning.
        "BULK_OPERATION_NOT_APPLICABLE",
```

- [ ] `operations.py`, after `REBASE_ZERO_REFERENCE = …` (`:78`):

```python
BULK_OPERATION_NOT_APPLICABLE = "BULK_OPERATION_NOT_APPLICABLE"
```

and after `_check_filter_key` (`:731-737`):

```python
_ALL_VALUE_TYPES = frozenset(RateTableValueType)

#: FR-233: the value types each bulk operation has a meaning on. Absence refuses, so a value
#: type added later is refused until someone says otherwise.
_OPERATION_VALUE_TYPES: Mapping[str, frozenset[RateTableValueType]] = {
    "uplift_table": _ALL_VALUE_TYPES - {RateTableValueType.COUNT},
    "uplift_by_filter": _ALL_VALUE_TYPES - {RateTableValueType.COUNT},
    "floor_and_cap": _ALL_VALUE_TYPES,
    "rebase_to_level": frozenset({RateTableValueType.RELATIVITY}),
}


def _check_value_type(table: RateTableVersion, kind: str) -> None:
    """FR-233: refuse before anything else reads the table."""
    if table.value.type not in _OPERATION_VALUE_TYPES[kind]:
        raise ValueError(
            f"{BULK_OPERATION_NOT_APPLICABLE}: {kind} has no meaning on a "
            f"{table.value.type.value} column of rate_table:{table.slug}@{table.version}"
        )
```

- [ ] Call it as the **first statement** of each operation: `_check_value_type(table, "uplift_table")`
  in `uplift_table` (`:751`), `"uplift_by_filter"` in `uplift_by_filter` (`:776`), `"floor_and_cap"`
  in `floor_and_cap` (`:814`, ahead of its `floor > cap` check), and `"rebase_to_level"` in
  `rebase_to_level` (`:842`). `rebase_to_level`'s docstring gains one line: it runs only on a `relativity` column, and it moves premiums unless the base rate offsets it.
  `Mapping` is already imported (`:19`).
- [ ] Add T3's ordering tests to `TestBulkOperationValueType`:

```python
    @pytest.mark.req("FR-233")
    def test_the_refusal_comes_before_the_filter_check(self) -> None:
        with pytest.raises(ValueError, match=r"^BULK_OPERATION_NOT_APPLICABLE: "):
            rebase_to_level(_typed("money_minor"), base_level={"no_such_key": ["x"]})

    @pytest.mark.req("FR-233")
    def test_the_refusal_comes_before_the_parquet_check(self) -> None:
        table = _version(
            storage=RateTableStorageMode.PARQUET,
            value=RateTableValue(
                name="relativity", type=RateTableValueType.COUNT, unit="u", min=None, max=None
            ),
        )
        with pytest.raises(ValueError, match=r"^BULK_OPERATION_NOT_APPLICABLE: "):
            uplift_table(table, percentage=Decimal("0.10"))
```

- [ ] Green: `run-small.sh` on the file: all 16 pass, and every existing test unedited (A7).
- [ ] Commit, `fix(pricing-core): …`, spec and code together (`CLAUDE.md` §2; A2).

**T4 — the route, in the DB window** (DP-2). Three runs of `-k
bulk_operation_value_type_matrix_at_the_route` on `backend/tests/test_api_rate_tables.py`:

1. **Red**, at the tests-only commit: 5 failed with actual 201, 11 passed.
2. **Green**, at the fix: 16 passed.
3. **Plant P**: set every value of `_OPERATION_VALUE_TYPES` to `frozenset()`, run, expect the 11
   allowed red and the 5 refused green, then `git -C <wt> checkout -- <operations.py>` and quote `git
   diff` empty. P also runs in T1's file, DB-free, before the window.

Moving between commits is `git -C <wt> checkout --detach <sha>` and back, only in the slice's own
worktree, and never while a gate runs from that tree.

**DB window (need stated, 2026-11-05 14:40:19 GMT terms).** About 20 minutes, one window, granted by
the lead beside a gate's pytest stage only, or in a gap. Every term (a)–(j) of "2026-11-05 14:40:19
GMT" and its additions of "2026-11-05 15:49:09 GMT" goes in the window's brief: (a) a `-T` copy named
for the window, both URLs on it, createdb with mkdb's retry, template guard at both ends; (b) END reads
the window's own DB gone and the gate's still there; (c) redis db 11–13, `-n <db>` on every command,
dbsize 0 at both ends, db 0 = 56 quoted at both ends; (d) bucket `gip-test-blobs-sl8389`,
`GIP_GATE_SLOT=/tmp/slots/window-sl8389`, `gip:switch` channels read at START, any fixture ignoring the
slot a stop; (e) no compose, no service restart, no fixed port; (f) `run-heavy`, nice 10, the cap's
one, the memory guard; (g) the gate's pytest expected to outlast the window by 30 minutes, by its own
progress line, quoted; (h) START and END name the gate and its stage; (i) the attribution read; (j) no
`test_deployment_switch*.py`. No migration and no switch test is in this selection.

**T5 — the record.**

- [ ] LG-2042 under `docs/ledgers/`, in `docs/_templates/LG.md`'s form: Scope quotes this row; Task
  list; Gate; Build log with A3's and A4's lines, every log `head=` first and `rc=` last; `### Audit`
  left to the auditor (A14). Red and green lines go in the LG before the audit.
- [ ] A9's check, A10's runs, A11's derivation.
- [ ] FINAL to the lead. The mint, the PR and the ACK follow R2's merge; the slice's PR opens only once
  R2 is on main, after a merge of `origin/main`, never a rebase.

**CI that fires.** Matched against each workflow's `paths`: `python.yml` (`packages/**`, `backend/**`),
`docs.yml`, and `history-policy`. `frontend.yml` does not: its `packages/` glob is
`packages/pricing-core/src/pricing_core/modelling/**`, and nothing under `frontend/` or
`docs/contracts/openapi/` changes.

### Seen, not in this slice

- **`default_row`.** `_new_version` (`:671`) leaves a table's default row at its old value after an
  operation, though `04` §4.4 says uplift "applies to every cell of the table". The DM's read, not
  measured, not filed; a type refusal does not touch it.
- **`floor_and_cap` on `count`.** A `floor` of `2.5` writes a non-integral count. The matrix allows
  the operation; the parameter is not checked against the type. Not ruled, not changed here.
- **A hand-authored table.** No route creates one (Evidence).

## Hand-off (not this plan's writes)

- DP-1, DP-2 and the GO on the row are the maintainer's (by delegation) to rule.
- The SL-2041 roadmap row and the mint are the lead's; LG-2042 is the executor's; FD-2032's essay
  (DP-1 (a)), its closing act and the LG Audit section are the auditor's.
- `PL-1927` is not edited.

## Self-review

1. **Every cite was read** at `cda3c0dc`; the two channel entries were read whole; the check was run
   at both trees and its predicate is quoted verbatim.
2. **Every requirement is named by id**: FR-233, FR-228 and FR-234; no range.
3. **All 16 cells have a test at both levels**, and T1's and T2's literals agree with the matrix above.
4. **The red is by cause**: `DID NOT RAISE` and 201 for the refused cells; plant P for the allowed,
   which are green at base by design and are said to be.
5. **Names are consistent** across tasks: `BULK_OPERATION_NOT_APPLICABLE`, `_OPERATION_VALUE_TYPES`,
   `_check_value_type`, `_insert_typed_table`.
6. **No placeholders.**
