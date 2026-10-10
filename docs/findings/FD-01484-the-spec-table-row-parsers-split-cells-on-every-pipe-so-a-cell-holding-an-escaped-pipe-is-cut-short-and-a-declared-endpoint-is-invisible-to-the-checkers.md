---
id: FD-1484
family: finding
title: The spec table-row parsers split cells on every pipe, so a cell holding an escaped pipe is cut short and a declared endpoint is invisible to the checkers
status: active
created: 2026-10-08            # original date 2026-09-30, set at the draft; minted 2026-10-08
owner: auditor
tree: daa7f5f8d6f0ff80dee7dfccf8ca18309d626816
corrected_by: []
relates: [WK-1178]
---

# FD-1484 — The spec table-row parsers split cells on every pipe, so a cell holding an escaped pipe is cut short and a declared endpoint is invisible to the checkers

*Disclosure: drafted under working id 9894; minted as FD-1484 on 2026-10-08, in the T1 batch mint PR.*

## Amendment before mint (2026-10-05)

Amended 2026-10-05 before mint, re-measured at `47d770e8` (`origin/main`): **the finding holds, undone.** The three `([^|]+)` parsers are unchanged (`_ENDPOINT` in `scripts/scope-audit.py:68`, `_ENDPOINT_ROW` in `scripts/audit-docs.py:299`, `_SPEC_ENDPOINT` in `backend/src/app/demo/guide.py:64`); no `table_rows.py` exists. The spec cites below moved: `06:539` is now `docs/specs/06-governance.md:583` (`/api/v1/dossiers/{id}?format=html\|pdf\|bundle`) and `06:543` is now `:587` (`/api/v1/artifacts/{ref}/dependencies?direction=up\|down`); `01:873` is unchanged; the purpose-cell rows are `01:866` and `02-modelling.md:1840` (formerly `02:1784`). The register now holds three rows with an escaped pipe, not two (`docs/findings/register.md:197`, `:213`, `:222`), and `python3 scripts/doc-index.py --phase P2` still raises `parsed 208 of 211 data row(s)`. The test lookbehind splits cited as `tests/test_audit_docs_ids.py:2413` and `:2462` are now the `re.split(r"(?<!\\)\|", line)` uses at `:2427` and `:2476`. The fix is the `table_rows.py` slice of RL-1483 (working id, unminted), owner the WK-1178 slice that carries it; PL-1276's sweep (#986) owns the earlier unowned recommendation `CR-823` item (c). Every other cite below is to tree `2e427bd1bf6535b6b1fda356527b342e99b2f4bd`'s merge base `daa7f5f8` and is read by symbol.

## Finding

**Severity: MEDIUM** (raised from low by the maintainer, `to-lead.md` "2026-09-30 11:46:58 BST —
#983 (escaped-pipe FD) raised to MEDIUM; the closure-evidence check": `scope-audit` is §13 close
evidence, so a false completeness figure can have let a closure report coverage the repository
does not have; see the closure-evidence sweep below). It silently under-reads the checkers'
input, and **it is a recurrence**: plan review 5 at WK-664's close recorded the same blind spot on
2026-08-27 with a recommendation and no owner (`docs/closures/CR-00823-plan-review-5-at-wk-664-s-close.md:67-72`,
item (c)). Three copies of one
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
take a gate slot"): ~~a LOW FD~~, owner #977's WK-1178 slice, silence being the reason to record it
(`CLAUDE.md` §13, a check that has never printed a failure). ~~The fix is one shared parser, or
pipe-free cells, never a third parser.~~

**Superseded, dated 2026-09-30** (struck above, not deleted): the severity by "2026-09-30 11:46:58
BST — #983 (escaped-pipe FD) raised to MEDIUM; the closure-evidence check", so this FD is
**MEDIUM**, not LOW; and the fix statement by "2026-09-30 11:49:44 BST — DECISION: the shared row
parser is route (a), a stdlib-only module file; this amends my 11:46:58 "model-schema
helper"", so the fix is **a stdlib-only `table_rows.py`, loaded by path by the scripts and imported
by the backend** (see Disposition), not "one shared parser, or pipe-free cells". Owner and the
§13 reason stand.

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
`declared : 23`, `published : 13  (57%)`. **The two hidden rows (`:539`, `:543`) are
unpublished, so GOV's real coverage is 13 of 25 (52%), not the printed 13 of 23 (57%).**
Measured two ways at `daa7f5f8`: (a) `grep -n '"/api/v1/dossiers\|"/api/v1/artifacts'
docs/contracts/openapi/generated.json` returns **no line**, while
`"/api/v1/dataset-versions/{version_id}/lineage"` is at `:17717`; (b) `scope-audit.py`'s own
`implemented_endpoints()`, run on the two declared sets (the script under the next item), gives
`GOV declared as printed: 23 published: 13`, `GOV declared with the two rows visible: 25
published: 13`, hidden GOV pairs `('GET', '/api/v1/artifacts/{}/dependencies')` and `('GET',
'/api/v1/dossiers/{})` **published: [False, False]**, and hidden DATA pair `('GET',
'/api/v1/dataset-versions/{}/lineage')` **published: [True]** (so DATA is 40 of 40).

```python
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location("sa", "scripts/scope-audit.py")
sa = importlib.util.module_from_spec(spec)
sys.modules["sa"] = sa
spec.loader.exec_module(sa)
impl = sa.implemented_endpoints()
orig = pathlib.Path.read_text
def respelled(self, *a, **k):
    t = orig(self, *a, **k)
    return t.replace("\\|", "-or-") if self.name.startswith(("01-data", "06-gov")) else t
gov_now = sa.declared_endpoints("GOV")
pathlib.Path.read_text = respelled
gov_true = sa.declared_endpoints("GOV")
data_true = sa.declared_endpoints("DATA")
pathlib.Path.read_text = orig
print("GOV declared as printed:", len(gov_now), "published:", len(gov_now & impl))
print("GOV declared with the two rows visible:", len(gov_true), "published:", len(gov_true & impl))
hidden = sorted(gov_true - gov_now)
print("hidden GOV pairs:", hidden)
print("hidden GOV pairs published:", [h in impl for h in hidden])
dh = sorted(data_true - sa.declared_endpoints("DATA"))
print("hidden DATA pairs:", dh, "published:", [h in impl for h in dh])
```

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
- **Idioms that already handle the escaped pipe correctly:** `tests/test_audit_docs_ids.py:2413`
  and `:2462` (`re.split(r"(?<!\\)\|", line)`, a lookbehind split, the second form of the fix
  besides `_split_row`'s placeholder swap). `scripts/doc-id.py:2921` and
  `tests/test_doc_id_migrate.py:4951` split only the first cell (`.split("|", 1)[0]`), so they
  are unaffected. "Never a fourth" refers to the **row-splitting logic**, not to these being
  counted as parsers to keep.
- **Regexes with `[^|]*` that do not read the cell after it**: `scripts/doc-index.py:458-461`
  and `scripts/graphify-docs-extract.py:41` skip the rest of the id cell and take the remainder as
  text: **not affected**.

**Limits:** the sweep finds the two textual forms above. A parser that splits with a different
idiom (`re.split`, `csv`) or a regex that names the pipe by another spelling is not seen. It is a
listing at one tree. **The row-split population is wider than this sweep's textual forms**:
#977's own finding, reported by the lead and **not re-run by this record's author**, counts about
**18 sites** that split a table row, **all of which migrate** to the shared parser (this record's
sweep found the endpoint regexes, the naive splitters and the two lookbehind splits, which are the
subset it could see with two predicates).

## Closure-evidence sweep

The maintainer's 11:46:58 entry asks for every closure record (`docs/closures/`) and slice ledger
(`docs/ledgers/`) that cites a DATA or GOV endpoint coverage figure from `scope-audit`, whether the
three affected routes were counted, and whether each is built. **Predicates, verbatim** (text
only; run from the repository root at `daa7f5f8`):

```
git grep -n -i -E "(declared|published)[ :]+[0-9]+|endpoints? (declared|published)|scope-audit.*--endpoints|--endpoints|[0-9]+ ?% ?published|published.*[0-9]+ ?%" -- docs/closures docs/ledgers
git grep -n -E "scope-audit(\.py)? (DATA|GOV)|(DATA|GOV) (endpoints|--endpoints)|(DATA|GOV)[^a-z].*(declared|published)|(declared|published).*(DATA|GOV)[^a-z]" -- docs/closures docs/ledgers
git grep -n -E "(28|33|34|39) ?(/|of) ?(28|33|34|39)( |\)|$|\*)|GOV.{0,40}[0-9]+ ?(/|of) ?[0-9]+|11 ?/ ?20|10 published" -- docs/closures docs/ledgers
```

The first gives 33 hits (MODEL and RATE figures included); the second and third narrow it to the
DATA and GOV ones below. **The affected routes were counted in none of them**: the parser cannot
see them, so every figure below excludes them by construction. Built status is read at
`origin/main` `daa7f5f8`: a route is built if the generated contract carries it
(`docs/contracts/openapi/generated.json`) and a router exists under `backend/src/app/api/`.

| Record, line | Created | Figure cited | Hidden routes it would cover | Built? |
|---|---|---|---|---|
| `CR-721` `:47` (WK-660 close) | 2026-08-15 | DATA `--endpoints` **28 / 28 (100 %)** | 01:873 lineage | **yes** (the first commit naming lineage in `api/dataset_versions.py` is `989308b3`, 2026-08-15, "close the Data Workbench"; in `generated.json:17717`) |
| `CR-719` `:54` (WK-663 close) | 2026-08-15 | DATA `28 / 28` then **33 / 33** | lineage | yes |
| `CR-723` `:25` (plan review 1) | 2026-08-15 | **33/33** endpoints | lineage | yes |
| `CR-722` `:34` (plan review 2) | 2026-08-15 | DATA **34 / 34** | lineage | yes |
| `CR-722` `:36` (plan review 2) | 2026-08-15 | GOV **11 / 20** | 06:539 dossiers, 06:543 dependencies | **no** (neither is in `generated.json`; no router; `gi-pricing.yaml:439` declares `/dossiers` as a hand-authored stub) |
| `CR-819` `:106` (WK-664 close) | 2026-08-27 | DATA **28/28 → 39/39** | lineage | yes |
| `CR-823` `:31` (plan review 5) | 2026-08-27 | DATA **39/39**, GOV **13/23** | lineage; dossiers, dependencies | lineage yes; the other two **no** |
| `CR-718` `:56-63` (demo entrance) | 2026-08-15 | the demo guide's **63 of 148** endpoints published (`guide.py`'s copy of the regex) | all three | lineage yes; the other two no |

**No slice ledger cites a DATA or GOV endpoint figure**: the second predicate finds only
catalogue and RATE lines in the ledgers (`LG-730:527`, `LG-1225:314`).

**GOV focus (the maintainer's and the lead's ask):** for each record that cites a GOV endpoint
figure, were FR-379's route (06:539) and FR-384's route (06:543) in its scope, built, or recorded
as deferred?

- `CR-722` `:36` (plan review 2, Phase 1a exit): GOV **11 / 20**. Not in scope: the review says
  the phase covers `DATA` and the `PLAT` and `GOV` **foundations** "which is what Phase 1a's rows
  claim and no more" (`:39-41`). Neither route is built; the cited passage does not name them.
- `CR-823` `:31` (plan review 5, WK-664 close): GOV **13 / 23** (really 13 of 25). **Recorded as
  deferred, by direct comparison:** `:120-123` says "**GOV 06 §5.1, FR-344 class:** attestations,
  dossiers, change control, audit/anchor. Declared with no route, all Phase 3 by the roadmap. This
  is spec-ahead-of-phase, not drift. No change." Dossiers (FR-379) and change control (FR-383 to
  FR-385, which includes FR-384 blast radius) are both named there. The same record names the
  parser blind spot at `:67-72` (item (c)) and counts "10 published versus 12 found by direct
  comparison" for GOV, so **the review knew of the two rows**.
- No closed **Work** record cites a GOV endpoint figure at all (the sweep finds only these two
  reviews). WK-664, whose close CR-823 reviewed, is the frontend of Phase 1b, and neither route
  is in its scope.

**Are the unbuilt hidden routes in any closed Work's scope?** **No.** The dossier route
(06:539) belongs to **WK-680** (P3, `active`, "Dossier generation, commentary blocks, PDF,
point-in-time regeneration", FR-376 to FR-381). The dependencies route (06:543, FR-384, blast
radius) was **held by no roadmap row at this tree** (already recorded at
`PL-1237` `:525`; `RS-708` `:303` puts FR-383 to FR-385 in Phase 3, not started); the
maintainer has since made **WK-680 its owner, provisionally** (§14 does not permit it to be
unowned; the lead's roadmap row, #985, cites `to-lead.md` "2026-09-30 11:52:53 BST — #983's
closure sweep: accepted (no §13 verdict owed); DECISIONS on the recurrence and FR-384"). **So no
closed Work's scope hid an unbuilt route**, and **no §13 verdict is owed** (the same entry:
"DATA closures under-count, but lineage is built; the GOV-hidden routes are unbuilt but in no
closed Work's scope"). The one route the false figures did hide from a closed Work's scope,
lineage, is built. What the sweep does show: the two GOV figures (`CR-722:36`, `CR-823:31`)
were understated by two declared routes, and `CR-823:67-72` had already named the cause ("fix
the parser or record the limitation in the close-workstream skill before the WK-664 close counts
GOV endpoints"); **`.claude/skills/close-workstream/SKILL.md` and
`.claude/skills/docs-audit/SKILL.md` record no such limitation** (searched for `pipe` and
`escaped`), and no owner was ever assigned. **This record is a recurrence of `CR-823` item (c)**
(plan review 5, 2026-08-27), **not a separate finding of a new defect**, per the maintainer's
11:52:53 BST entry (above): the recommendation predates the 2026-09-29 §14 amendment
(RFC-1248, RL-1249) that forbids an unowned accepted proposal. The class may have other members:
the maintainer sends a one-time sweep of accepted §14 plan-review proposals before 2026-09-29
that never became an owned record to WK-1170's Slice 1 audit (PL-1276's inputs, by the planner's
dated delta), where each unowned one gets an owner. MODEL, RATE and PLAT figures are unaffected: no
escaped pipe sits in one of their path cells.

## Disposition

**Deferred with an owner: #977's slice (DP-S2-4, RL working id 9907), a WK-1178 slice**;
dm-effort-high carries it in #977 (the 11:46:58 entry). Event that discharges it: that slice's
merge, except the secondary instance below.

**Acceptance, red first** (route decided by the maintainer, `to-lead.md` "2026-09-30 11:49:44
BST — DECISION: the shared row parser is route (a), a stdlib-only module file; this amends my
11:46:58 "model-schema helper""):

- **a stdlib-only `packages/model-schema/src/model_schema/table_rows.py`**, the one source of the
  row-splitting logic, modelled on `register-lint.py`'s `_split_row` (`:165-170`). **The scripts
  load it by path via `importlib`; the backend (`guide.py`) imports it normally; `docs.yml` is
  unchanged.** Route (b), installing pydantic in the docs gate, is rejected (an infrastructure
  change for no gain);
- **a test fails if `table_rows.py` imports anything outside the stdlib**: an AST walk of its
  imports against `sys.stdlib_module_names`, **red first on a planted `import pydantic`**, so a
  later edit cannot silently break the docs gate. The docs gate itself is proven by running
  `audit-docs.py` under a bare `python3` with no project packages;
- **every idiom migrates to it**: audit-docs `_ENDPOINT_ROW` (`:299`), scope-audit `_ENDPOINT`
  (`:68`), `backend/src/app/demo/guide.py:64`, and `tests/test_audit_docs_ids.py:2413` and `:2462`
  (the lookbehind splits), as do the register reader (`doc-index.py:1061`) and the other cell
  splitters that read a table. **"Never a fourth" means the row-splitting logic**, not a count of
  regexes;
- **the demo guide's "63 of 148"** (`CR-718:56-63`, produced by `guide.py`'s copy of the regex)
  **is corrected when `guide.py` moves to the shared parser**, its declared count rising by the
  three hidden routes;
- **red first:** `declared_endpoints("DATA")` **39 to 40**, GOV **23 to 25** (and GOV published
  stays 13, so 13 of 25), the demo guide's declared count up by the same three, and **the
  `doc-index.py --phase P2` raise** (evidence 3).

**Secondary instance, in this same FD: `doc-index.py --phase P2` raises** `ValueError:
findings/register.md: parsed 183 of 185 data row(s)` (evidence 3), because `register.md:197` and
`:213` hold an escaped pipe. It is loud, but **a P2 phase check that cannot run is a gap before
the P2 exit review**: its fix, making the phase report run, **red first on `:197` and `:213`,
lands before the P2 exit review**. **It is carried by #977's slice** (the lead's message of
2026-09-30, after the 11:52:53 entry), the same slice as the shared parser, so the raise goes away
with the migration of `doc-index.py:1061` and is proven by the red-first case above.

*Drafted under working id 9894.*

Re-anchored 2026-10-05 at main `caa4e411`: re-run of the reproduction above (the
`scope-audit.py` script, escaped pipe respelled) prints `DATA printed 39 true 40, published
printed 39 published true 40` and `GOV printed 23 true 25, published printed 13 published true
13`; the hidden GOV pairs `('GET', '/api/v1/artifacts/{}/dependencies')` and `('GET',
'/api/v1/dossiers/{}')` are published `[False, False]` and the hidden DATA pair
`('GET', '/api/v1/dataset-versions/{}/lineage')` `[True]`: **the finding reproduces undone**. The
three `([^|]+)` parsers are unchanged (`scripts/scope-audit.py:68`, `scripts/audit-docs.py:299`,
`backend/src/app/demo/guide.py:64`) and `scripts/table_rows.py` does not exist. Cites that moved
since `47d770e8`: `06:583` is now `docs/specs/06-governance.md:594` (the dossiers row) and `06:587`
is now `:598` (the dependencies row); the lineage route in
`docs/contracts/openapi/generated.json` is at `:19792` (was `:17717`); the register's three rows
with an escaped pipe are still `docs/findings/register.md:197`, `:213` and `:222` at `main`;
`python3 scripts/doc-index.py --phase P2` still raises `parsed 211 of 214 data row(s)` in this
tree, which carries this record's own row; `tests/test_audit_docs_ids.py:2427` and `:2476` are
unchanged. `RL-1483` is minted in the same batch (T1) as this record.
