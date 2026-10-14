---
id: FD-1723
family: finding
title: Both requirement-coverage scripts read one marker form with one regex, so 48 of 3,483 requirement markers are invisible to them
status: active
created: 2026-10-14
owner: auditor
tree: 4420f91fa4112a1fcabcae23d3d50a1ad4fcbb59
corrected_by: []
relates: [WK-1178, WK-674, FR-272, FR-217, FR-242, NFR-498, P2]
---

# FD-1723 — the requirement-marker parser sees one form of three

*(Minted 2026-10-14 as FD-1723 from working id 8029, in the D17 batch mint PR.)*

*(Filed under working id 8029, reserved by the lead in `eta.md`, line stamped "2026-10-14 11:14:02 BST"; a minter
folds it into the docs batch. Every count below was taken at `origin/main`
`4420f91fa4112a1fcabcae23d3d50a1ad4fcbb59` on 2026-10-14 from a clean `git worktree` of that commit, never from the
root checkout. The raising evidence is item (3) of the maintainer's (by delegation) entry "2026-10-14 11:13:20 BST — Marker
batch OK; FR-7/14/15 → FD 8027 PARTIAL limbs …" in `channel/to-lead.md`; its counts were re-measured, not copied.)*

## Finding

**Proposed severity: MEDIUM, owner WK-1178, fixed in P2** (the auditor proposes; the lead and the maintainer
(by delegation) rule). The entry above says the severity is the auditor's and "MEDIUM at least".

*(Ruled 2026-10-14: the maintainer (by delegation), "2026-10-14 11:20:00 BST" in `to-lead.md`, CONFIRMED MEDIUM and the HIGH re-rate trigger as written, owner WK-1178, fixed in P2. The proposal above is kept as written. The ruling ADDED one red to the fix, in Disposition step 2a.)*

`scripts/req-coverage.py` and `scripts/scope-audit.py` each carry their own copy of one regex, and the regex
reads one spelling of a marker: the single-argument decorator. Two other spellings that `pytest` accepts, and that
the repository's tests already use, are invisible to both scripts. A marker the scripts cannot see is not
evidence to them, and the scripts say so by silence.

## Evidence

**The two predicates, verbatim.**

- `scripts/req-coverage.py:58`: `for rid in re.findall(r'@pytest\.mark\.req\("([^"]+)"\)', source):`
- `scripts/scope-audit.py:65`: `_MARKER = re.compile(r'@pytest\.mark\.req\("([^"]+)"\)')`, used at `:108`
  inside `evidence()` (`:101-109`).

Both read the same roots, `[tool.pytest.ini_options] testpaths` of `pyproject.toml` (`packages/model-schema/tests`,
`packages/pricing-core/tests`, `backend/tests`, `tests`, `examples/fremtpl2`), by `rglob("test_*.py")`. The `req`
marker is registered at `pyproject.toml` `markers = [...]` with the text `"req: the requirement ID this test satisfies,
e.g. @pytest.mark.req('FR-10')"`, and `addopts` carries `--strict-markers`, so `pytest` accepts any arity and any
placement of it. The `python-test` skill shows only the single form.

**The census.** An `ast` walk over the same 302 `test_*.py` files finds every call of `pytest.mark.req(...)`
(`ast.Call` whose func is the attribute `req` of the attribute `mark`) and classifies it by its parent node. The
script is `/tmp/census.py` of the auditor's session, written for this finding; the run was one `flock -w 3600
/tmp/slots/gate-2 bash -c 'OMP_NUM_THREADS=1 nice python3 -I /tmp/census.py <worktree>'`.

| Form (AST parent, arity) | Markers | Seen by the regex? |
|---|---|---|
| function decorator, one id: `@pytest.mark.req("X")` | 3420 | yes |
| class decorator, one id | 15 | yes (the regex is text, so it sees a class decorator too) |
| function decorator, **several ids**: `@pytest.mark.req("A", "B")` | **38** | **no** |
| `pytestmark = pytest.mark.req("X")` (module level) | **9** | **no** |
| `pytestmark = [pytest.mark.req("X")]` (a list) | **1** (`backend/tests/test_sub_graphs_api.py`) | **no** |
| any other placement (`marks=` of a `pytest.param`, an argument of another call, a non-string argument) | 0 | n/a |

Total 3483 markers, **48 invisible = 38 + 10**, which confirms the maintainer's counts exactly. A second predicate agrees
on the 38: `git grep -nE 'req\("[^"]+", *"' -- backend packages` prints 38 lines (the same pattern over `tests` and
`examples` too prints 43, the five extra being `self.req("C6", …)` calls in `examples/fremtpl2/journey.py`, an HTTP helper and not a marker, which is why the AST, not the grep, is the census).
The 10: `git grep -nE 'pytestmark *= *.*mark\.req\(' -- backend packages tests examples` prints 10.

The 38 multi-argument markers sit in seven files: `backend/tests/test_deployments.py` (13),
`backend/tests/test_migration_deployments.py` (7), `packages/pricing-core/tests/test_rating_peril_scoring.py` (12),
`backend/tests/test_rating_peril_scoring_api.py` (5), `test_rating_glm_model_call.py` (4), `test_rating_inline.py` (2)
and `test_rating_mounted_model_call.py` (2). The ten `pytestmark` markers are in ten files (FR-212, FR-217 ×4,
FR-242 ×2, FR-396 ×2, NFR-498; the FR-217 list form is `test_sub_graphs_api.py`).

**What the undercount does, measured.** Comparing, per requirement id and test file, the regex's evidence to the AST's
(`/tmp/c2.py`, same worktree, same gate-2 form):

- Requirements specified (`_REQ_DEFINED`, `req-coverage.py:27`, over `docs/specs/*.md`): 544.
- Ids marked: **371 by the regex, 372 by the AST** (68.20 % against 68.38 %). **One id is marked only through an
  invisible form: FR-272**, by a multi-argument decorator in `backend/tests/test_deployments.py`. Both scripts report
  it as unmarked.
- (id, test file) pairs: **1046 by the regex, 1087 by the AST**. 28 ids have an understated file count: FR-4, FR-20, FR-88,
  FR-188, FR-191, FR-193, FR-212, FR-217 (9 against 15), FR-222, FR-237, FR-238, FR-240, FR-242, FR-255, FR-267, FR-272
  (0 against 1), FR-345, FR-351, FR-355, FR-356, FR-364, FR-386, FR-389, FR-396, FR-417, NFR-491, NFR-498, NFR-499.
- Ids the AST finds that no spec defines: none. The invisible markers carry no typo today.

**The effect on the gate.**

- `req-coverage.py` is a step of `.github/workflows/python.yml` (`:319-322`, "Requirement coverage",
  `continue-on-error: true`, with the verdict step deciding the job). It has **no threshold**: its only failing exit is
  a marker whose id is not in the specification (`:81-84`), or an empty denominator (`:69-73`). So no count the
  undercount produces passes or fails the CI job wrongly by itself.
- **That failing exit is the guard against a typo or a renumbering, and it is blind to the 48.** The `python-test`
  skill says the script "fails when a test claims a requirement that does not exist". The regex run on
  `@pytest.mark.req("X")` returns `['X']`; on `@pytest.mark.req("A", "X")` and on
  `pytestmark = pytest.mark.req("X")` it returns `[]`. A misspelled id in the two invisible forms passes the
  guard silently. None exists today (above); the guard cannot say so on its own.
- `scope-audit.py` is not in CI (`git grep -nE 'req-coverage|scope-audit' -- .github` finds only comments for it) but it
  is the **tool of `close-workstream`'s step 1**, and it **exits 1** when any in-scope requirement lacks evidence
  (`:440-449`, the `if missing:` block). FR-272 is in module RATE's scope, so a RATE scope audit prints "NO EVIDENCE" for it and exits 1 while a
  test marks it. FR-272 is the one id this flips today.
- The multi-argument form is in use in seven test files (above), the deploy and peril-scoring tests among them; nothing in the
  `python-test` skill or the scripts tells an author the form is not read.

**The D list.** `~/gi-pricing-plan.local/handover/sweep-unowned-D-2026-10-14.txt` (56 rows, the coverage sweep's class-D
list) was searched for the 28 ids above, as `|ID|` cells: **none is in it**. The undercount therefore does not
move a D row today. FR-7, FR-14 and FR-15 (the maintainer's item 2) are in the list and are marked by single-argument
decorators, so they are visible and unaffected. The list is re-checked, as ruled, after the fix.

## Why MEDIUM, and not LOW or HIGH

*Not LOW:* the failure is of the "a check that cannot see" class, and the check is the one the §13 and §14 verdicts
cite. It makes the closure and phase records that quote `req-coverage` numbers understate evidence, and it disables the
typo guard for 48 markers, which is the guard's whole purpose. One requirement is wrongly "unevidenced" today and a close
scoped to RATE would fail on it.

*Not HIGH:* the error runs toward "unevidenced", the safe side; no price, no approval evidence and no governed record is
wrong because of it; the CI job has no threshold to flip; and the count difference is one id in 544. The re-rate trigger,
to HIGH: an invisible marker with a wrong id found to be in a merged test, or a closure or phase record found to cite a
"NO EVIDENCE" verdict that an invisible marker contradicts.

The maintainer's entry also says "MEDIUM at least"; this proposal accepts that floor and gives its reason.

## Disposition

**Owner WK-1178, fixed in P2** (D17 of the maintainer's entry). Remedy, as ruled, nothing added:

1. **One shared AST parser** for requirement markers, imported by **both** scripts, so the duplicated regex cannot make
   them go blind together again. It reads a `pytest.mark.req(...)` call with any number of string arguments, in a
   decorator of a function or a class, as `pytestmark` single or a list or tuple, and fails loudly on a non-string
   argument or an unparseable file rather than skipping it.
2. **Red first**: a planted fixture tree holding each form (single, multi-argument, class decorator, `pytestmark`
   single, `pytestmark` list), whose expected (id, file) set is asserted; red on `main` by cause, because the regex
   returns the single forms only.
2a. **Added red (ruling of 2026-10-14 11:20:00 BST):** the same fixture tree also plants `req("FR-272", <an FR id that does not exist>)` as a multi-argument marker and `pytestmark = pytest.mark.req(<an NFR id that does not exist>)` as a module-level marker, and asserts that the unknown-id exit fires for both. Today it cannot: the one failing exit of `req-coverage` is blind to the 48 invisible markers, so a typo inside either form passes silently. Red on `main` by that cause. The ruling also lists `scope-audit`'s false close-audit FAIL on FR-272 as a consequence, which re-runs green after the fix.
3. **Before and after counts at the tree where it lands**, from both scripts. The "before" at `4420f91f` is:
   `req-coverage` 371 marked of 544 (68.20 %), 1046 (id, file) pairs; AST 372 (68.38 %), 1087 pairs, and FR-272 the one
   id that moves from unmarked to marked.
4. **The D list re-checked against the corrected evidence before FD-1721 is final** (done once above at `4420f91f`:
   no overlap; redone after the fix).

Also in scope of the fix, and named here so it is not forgotten: the `python-test` skill's marker section shows the one
form, and should state the accepted forms and that the parser reads them. Needs a resolution before any P3 start
(`CLAUDE.md` §14). Event that next confirms or discharges it: the fix's merge with the red shown on the base tree by its
causes.

*(Ruled 2026-10-14: the maintainer (by delegation), "2026-10-14 11:28:56 BST" in `to-lead.md`: "Cause noted: scope-audit counts any marker as evidenced (CR-754:111-112), and 9 of the 11 ids appear in no closure record. That goes to the §14 review as a process finding with FD 8029.")*
