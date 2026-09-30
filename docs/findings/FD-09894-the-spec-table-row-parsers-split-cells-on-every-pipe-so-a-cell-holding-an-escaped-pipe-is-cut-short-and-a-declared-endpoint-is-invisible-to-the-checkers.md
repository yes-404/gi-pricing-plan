---
id: FD-9894
family: finding
title: The spec table-row parsers split cells on every pipe, so a cell holding an escaped pipe is cut short and a declared endpoint is invisible to the checkers
status: active
created: 2026-09-30
owner: auditor
tree: daa7f5f8d6f0ff80dee7dfccf8ca18309d626816
corrected_by: []
relates: [WK-1178]
---

# FD-9894 — The spec table-row parsers split cells on every pipe, so a cell holding an escaped pipe is cut short and a declared endpoint is invisible to the checkers

## Finding

**Severity: low**, because it silently under-reads the checkers' input. Three copies of one
regular expression capture a §5.1 row's path cell with `([^|]+)`: `_ENDPOINT` in
`scripts/scope-audit.py:68`, `_ENDPOINT_ROW` in `scripts/audit-docs.py:299`, and
`_SPEC_ENDPOINT` in `backend/src/app/demo/guide.py:64`. Markdown spells a pipe inside a cell as a
backslash and a pipe, and the regex stops at the backslash-pipe's pipe character, so a path cell
that holds one is cut off mid-path, the following backtick is never closed, and
`_PATH_IN_CELL` finds **no path**. The declared route is then invisible. **Three §5.1 rows are
affected today**: `docs/specs/01-data-management.md:873`
(`/api/v1/dataset-versions/{id}/lineage?direction=up` then a backslash-pipe then `down`), and
`docs/specs/06-governance.md:539` (`/api/v1/dossiers/{id}?format=html`, then `pdf`, then
`bundle`, each separated by a backslash-pipe) and `:543`
(`/api/v1/artifacts/{ref}/dependencies?direction=up` then a backslash-pipe then `down`). It was
found by auditor-926-927 in #977's audit; this record reproduces it independently.

**The maintainer's decision** (`~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 11:42:08
BST — two decisions: the escaped-pipe checker blindness → a LOW FD; box load → heavy audit runs
take a gate slot"): a LOW FD, owner #977's WK-1178 slice, silence being the reason to record it
(`CLAUDE.md` §13, a check that has never printed a failure). The fix is one shared parser, or
pipe-free cells, never a third parser.

## Evidence

Measured at `origin/main` `daa7f5f8d6f0ff80dee7dfccf8ca18309d626816`.

**1. The reproduction** (`python3 repro.py` from the repository root; the script below loads
`scripts/scope-audit.py` by path and reads the DATA and GOV declared pairs, then re-reads them
with the escaped pipe in the path cells respelled pipe-free):

```python
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location("sa", "scripts/scope-audit.py")
sa = importlib.util.module_from_spec(spec)
sys.modules["sa"] = sa
spec.loader.exec_module(sa)
print("DATA:", len(sa.declared_endpoints("DATA")), "pairs")
line = next(l for l in open("docs/specs/01-data-management.md", encoding="utf-8").read().split("\n")
            if "/lineage?direction=" in l and l.startswith("| `GET`"))
m = sa._ENDPOINT.match(line)
print("captured path cell:", repr(m.group(2)))
print("paths found in it:", [p for p in sa._PATH_IN_CELL.findall(m.group(2)) if p.startswith("/")])
orig = pathlib.Path.read_text
def respelled(self, *a, **k):
    t = orig(self, *a, **k)
    return t.replace("\\|", "-or-") if self.name.startswith(("01-data", "06-gov")) else t
pathlib.Path.read_text = respelled
print("DATA respelled:", len(sa.declared_endpoints("DATA")), "pairs")
print("GOV respelled:", len(sa.declared_endpoints("GOV")), "pairs")
pathlib.Path.read_text = orig
print("GOV as it stands:", len(sa.declared_endpoints("GOV")), "pairs")
```

Output: `DATA: 39 pairs`; the captured cell is `' `/api/v1/dataset-versions/{id}/lineage?direction=up\\'` (it ends at the backslash), and
`paths found in it: []`; `DATA respelled: 40 pairs`; `GOV respelled: 25 pairs`; `GOV as it stands:
23 pairs`. **`declared_endpoints("DATA")` gives 39 pairs where 40 are expected, and GOV gives 23
where 25 are.**

**2. What the checker reports, and what it cannot see.** `python3 scripts/scope-audit.py DATA
--endpoints` prints `declared : 39` and `published : 39  (100%)` and *"every declared endpoint is
published in the contract"*. That is true of the 39 it sees. The spec declares 40 (39 method rows
in `01` §5.1, one of them two-method: `01:880`, `GET`/`PUT` on the rule-set route), and the
lineage route **is live**: the generated contract carries it at
`/api/v1/dataset-versions/{version_id}/lineage` (`docs/contracts/openapi/generated.json:17717`).
So **nothing reads wrong today**: the figure would be 40 of 40. The blind spot is that a removed,
renamed or unpublished lineage route would go undetected, and that #977's planned pin, which
reuses the same row shape, would report the live route as rowless unless the shared regex or the
row is fixed (auditor-926-927, who supplied the row count and this consequence; the first version
of this record said the route was unbuilt, and that was wrong). For GOV the script prints
`declared : 23`, `published : 13  (57%)`; the two hidden rows (`:539`, `:543`) would make the
declared count 25. Whether those two routes are published was not checked here.

**3. A second, loud consequence in another tool.** `scripts/doc-index.py:1061`, the register
reader, splits every row on every pipe and drops any row that does not give exactly five cells
(`:1062-1063`). Two register rows hold an escaped pipe (`docs/findings/register.md:197` and
`:213`), so **`python3 scripts/doc-index.py --phase P2` raises**: `ValueError:
findings/register.md: parsed 183 of 185 data row(s) — coverage mismatch (RL-982 acceptance item
2)` (`:1157-1161`). That one is loud, not silent; the default `--check` path does not call it.

## Class sweep

**Sweep (a): every table row in `docs/` containing an escaped pipe.** Predicate, verbatim:

```
git grep -n -F '\|' -- docs ':!docs/INDEX.md' | grep -E '^[^:]+:[0-9]+:\s*\|'
```

**241 table rows** (377 lines in all contain the sequence; the other 136 are prose or code).
By file, the top: RFC-937 14, RS-1002 12, `open-questions.md` 12, `document-ids.md` 11, PL-960 11,
`docs/README.md` 11, then 23 further files with 9 or fewer. **`docs/specs/` holds 28**, listed in
full:

- `00-overview.md`: 214, 551, 555
- `01-data-management.md`: 866, 873, 1226
- `02-modelling.md`: 118, 206, 282, 364, 370, 1784, 3217, 3239
- `03-rating-engine.md`: 63, 96, 97, 98, 100, 101, 109, 123
- `06-governance.md`: 92, 146, 539, 543
- `07-platform.md`: 88, 509

Of the 28, **five are §5.1 method/path rows** (`01:866`, `01:873`, `02:1784`, `06:539`,
`06:543`), and **none is in a §5.3 section** (measured by nearest heading). In `01:866` and
`02:1784` the escaped pipe is in a later cell, so the path cell is intact; **only `01:873`,
`06:539` and `06:543` hold it in the path cell**. `docs/roadmap.md` holds none.

**Sweep (b): every script that captures or splits table cells on a pipe.** Predicates, verbatim:

```
git grep -n -E '\[\^\|\]' -- scripts tests packages backend .claude
git grep -n -E 'split\(("|.)\|("|.)\)' -- scripts tests packages backend
```

Each hit, and whether the escaped pipe affects it today:

- **`scripts/scope-audit.py:68` `_ENDPOINT`, `scripts/audit-docs.py:299` `_ENDPOINT_ROW`,
  `backend/src/app/demo/guide.py:64` `_SPEC_ENDPOINT`: affected** (the three copies above). The
  copies are deliberate: `audit-docs.py:295-298` says "deliberately the same shape
  `scope-audit.py` uses, because ... a second parser would eventually disagree", and
  `guide.py:60-63` says it is duplicated because the backend may not import `scripts/`. They are
  now three, and they share the blindness. `audit-docs.py` check 21 reads the declared paths
  through `_ENDPOINT_ROW` (`:4027`), so a journey citing the lineage, dossier or dependencies
  route would be reported as undeclared (a false red); not measured, by code reading. The demo
  guide's route list is built from `_SPEC_ENDPOINT` and so omits the three routes; not measured.
- **`scripts/doc-index.py:1061` (the register): affected**, two rows excluded (evidence 3).
- **`scripts/audit-docs.py:353` and `:394` (`open-questions.md`): not affected today, fragile.**
  Twelve rows there hold an escaped pipe, none in the last two cells, which is all the code reads
  (`cells[-2]`, `cells[-1]`); an escaped pipe in either would shift the read.
- **`scripts/audit-docs.py:4118` `_route_rows` (§5.3 view tables): not affected today** (no
  escaped-pipe row in a §5.3 section).
- **`scripts/audit-docs.py:578` (`docs/rfcs/README.md`), `scripts/_docid.py:1611` (the residue
  record), `backend/src/app/demo/guide.py:87` `_cells` (roadmap and §5.3 tables),
  `tests/test_findings_ids.py:157` (first cell only): not affected today**, none of their inputs
  holds an escaped pipe in a cell they read.
- **`scripts/register-lint.py:165-170` `_split_row`: correct.** It swaps the escaped pipe for a
  placeholder before splitting and restores it after. It is the working model of the fix, and the
  reason the register itself is read correctly by `register-lint` and wrongly by `doc-index`.
- **Regexes with `[^|]*` that do not read the cell after it**: `scripts/doc-index.py:458-461`
  and `scripts/graphify-docs-extract.py:41` skip the rest of the id cell and take the remainder as
  text: **not affected**.

**Limits:** the sweep finds the two textual forms above. A parser that splits with a different
idiom (`re.split`, `csv`) or a regex that names the pipe by another spelling is not seen. It is a
listing at one tree.

## Disposition

**Deferred with an owner: #977's slice (DP-S2-4, RL working id 9907), a WK-1178 slice.** Event
that discharges it: that slice's merge. **Acceptance, red first:** **one shared table-row
parser**, not per-script regexes and never a fourth (the model is `register-lint.py`'s
`_split_row`), read by `scope-audit.py`, `audit-docs.py`, `doc-index.py` and, through whatever
seam the application allows, `demo/guide.py`; **or** pipe-free cells in the three §5.1 rows. The
red-first case is **01:873: `declared_endpoints("DATA")` goes from 39 pairs to 40**, with GOV
23 to 25 as a second case, and `doc-index.py --phase P2` no longer raising.

*Drafted under working id 9894.*
