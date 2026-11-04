---
id: RS-1899
family: research
kind: audit
title: SL-1569 (WK-1178, PL-1568) delta audit of the oracle fix and the re-merges, bf845e11 to aaebd5df
status: draft
created: 2026-10-25   # drafted 2026-10-25 under working id 8236; minted 2026-10-25 as RS-1899
owner: auditor
tree: 908c4215d71989df7ce8284d41ed9bf8392763af
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1569, PL-1568, LG-1896, RS-1897, RS-1898]
---

# RS-1899 — SL-1569 delta audit, `bf845e11..aaebd5df`

*(Working id 8236, written by `aud-1569d`, 2026-10-25, from `brief-aud-1569d-2026-10-25.md` (lead 28). Check 31/32 on this id is expected until the mint. The ledger is cited by its working id `LG-1896`. Read by `git` and plain reads only; no test, no DB, no gate was run by this seat. Tree audited: `aaebd5df` (tree `908c4215d71989df7ce8284d41ed9bf8392763af`), the gate head that stands under 1(f).)*

## Question

RS-1898 audited `bf845e11`. The slice has since gained a fix for the one real red of its gate and several merges. Does the delta `git log bf845e11..aaebd5df` change the slice only as the 2026-10-25 15:23:06 GMT ruling allows, and did the merges bring nothing but main's content?

## Method

Scope first, from the ruling (`to-lead.md`, "2026-10-25 15:23:06 GMT — Maintainer: SL-1569 RED ruled (a)"): each of three asserts becomes **(i)** `served` is a `str` with exactly 9 digits after the point **and (ii)** `float(served) == pytest.approx(expected, abs=5e-10)`; item 13 and the out-of-write-set touch are granted for `backend/tests/test_rating_glm_model_call.py` and `backend/tests/test_rating_peril_scoring_api.py`; `FR-116` markers kept. Evidence second.

## The window (`git log --format='%h %p %s' bf845e11..aaebd5df`, 13 commits)

The brief expected three slice-own commits and two merges. The window holds more, all of them docs-only except the oracle commit:

| Commit | Kind | Paths |
|---|---|---|
| `2a1588c9` | slice-own | `LG-1896` only |
| `3eb04166` | merge (main `ff976406`) | see merge table |
| `37e7726a` | slice-own | RS-1897 + RS-1898 folded at working ids |
| `66d5a35d` | slice-own | `docs/INDEX.md` |
| `aab18283`, `2ec62327` | slice-own | `LG-1896` only |
| `c62e4e48` | merge (main `034781b3`) | see merge table |
| `5dc23c98` | slice-own, **code** | the two test files |
| `1f41acc6` | slice-own | `LG-1896` only |
| `93bf1321` | slice-own, comment-only | the two test files |
| `efb4cf27` | merge (main `01a28e6d`, #1370) | see merge table |
| `aaebd5df` | merge (main `4e7ca81d`, INDEX-only) | see merge table |

(`git diff --name-only <c>^ <c>` for the five docs commits; `git diff c62e4e48 93bf1321 --stat` = the two test files + `LG-1896`, 3 files.) **No `packages/*/src` or `backend/src` file changed in any slice-own commit of the window.**

## Merges: every path they brought equals main

Predicate, per merge `m`: incoming paths = `git diff --name-only $(git merge-base m^1 m^2) m^2` minus `docs/INDEX.md`; for every incoming path the slice did not itself change, `git diff --quiet m^2 m -- <path>` rc 0. For paths both sides changed, the merge's diff against `m^2` has the same +/- line multiset as the slice's own diff, and its diff against `m^1` has the same multiset as main's incoming diff (a clean 3-way result).

| Merge | Main parent | Incoming non-INDEX paths | Non-overlap paths differing from main parent | Overlap (both sides changed) | Overlap result |
|---|---|---|---|---|---|
| `3eb04166` | `ff976406` | 2 | 0 | none | n/a |
| `c62e4e48` | `034781b3` | 49 | 0 | `docs/contracts/openapi/generated.json`, `docs/roadmap.md`, `docs/specs/03-rating-engine.md` | clean 3-way, all 3 |
| `efb4cf27` | `01a28e6d` | 11 | 0 | `docs/roadmap.md` | clean 3-way |
| `aaebd5df` | `4e7ca81d` | 12 | 0 | none | n/a |

`docs/INDEX.md` differs from main's in each merge, as it must (the slice's own rows); it is regenerated in step 6 and not read here.

## Slice-own code: the oracle fix (`5dc23c98`, `93bf1321`)

`git diff c62e4e48 93bf1321 -- backend/tests`, 19 + 5 lines. Helper at `test_rating_glm_model_call.py:41-45`:

```
RISK_OUT_DP = 9  # the output step's declared rounding dp, read by `_algorithm` and the oracle alike

def assert_served_at_declared_scale(served: object, expected: float) -> None:
    assert isinstance(served, str)
    assert re.fullmatch(rf"-?\d+\.\d{{{RISK_OUT_DP}}}", served), served
    assert float(served) == pytest.approx(expected, abs=0.5 * 10**-RISK_OUT_DP)
```

| Ruling clause | At `aaebd5df` | Met |
|---|---|---|
| (i) `str` | `assert isinstance(served, str)` | yes |
| (i) exactly 9 digits after the point | `re.fullmatch(rf"-?\d+\.\d{{9}}", served)` (a full match, so no extra digits and no exponent form) | yes |
| (ii) `abs=5e-10` | `abs=0.5 * 10**-RISK_OUT_DP` = 0.5 × 10⁻⁹ = 5e-10, the half-quantum | yes |
| dp read once, no second copy | `RISK_OUT_DP = 9` is one module constant; `_algorithm`'s output step now reads `"dp": RISK_OUT_DP` (was literal `9`); the helper reads it; the peril test imports the helper | yes |
| three asserts changed | `glm_model_call` `:137` and `:202`, `peril_scoring_api` `:217`: each `float(...) == approx(expected, rel=1e-9)` → `assert_served_at_declared_scale(response.json()["outputs"]["risk_out"], expected)`, with the comment "oracle at the declared scale (dp 9, half_even): str with 9 dp + abs=half-quantum — to-lead 2026-10-25 15:23:06 GMT" | yes |
| no assert weakened elsewhere | `git diff 4e7ca81d aaebd5df` on the two files, `-` lines filtered of the replaced forms: only the three `rel=1e-9` asserts and the literal `"dp": 9` are removed. The one `approx` left in the two files is the helper's. The new form is stricter on type and scale than the old one and no looser in value (abs 5e-10 against rel 1e-9 at the value 0.3166 is 3.2e-10; the old form was the one that failed) | yes |
| `FR-116` markers kept | `pytest.mark.req` count 4 in each file on main (`4e7ca81d`) and at `aaebd5df`; the diff touches no marker line | yes |
| write set | the two files + `LG-1896`; granted by the 15:23:06 line | yes |

Compared to the maintainer's own check, "Maintainer: SL-1569 oracle fix @93bf1321 VERIFIED in the 15:23:06 form" (`to-lead.md` 15:26:31 GMT): this audit read the same diff and agrees item by item. `LG-1896` (+15 lines at `1f41acc6`) quotes the ruling verbatim, the RED line (`14 failed, 6838 passed` at `c62e4e48`, the one real red `test_a_model_offset_glm_scores_with_its_source_model`, `assert 0.316648016 == 0.3166480164244357 ± 3.2e-10`), the three changed asserts before → after, and marks GREEN as owed to the re-gate.

## The gate at `aaebd5df`

`~/gi-pricing-plan.local/scratch/sl1569-gate/gate.log` line 1: `START head: aaebd5dff63f3e89d9f7d4c52eb7d1f942d204d2 tree: 908c4215d71989df7ce8284d41ed9bf8392763af`. `pytest.log` last line: `13 failed, 6853 passed, 13 skipped, 149 warnings in 3469.09s (0:57:49)`; `pytest.rc` = `1`.

`grep -E '^FAILED .*(test_rating_glm_model_call|test_rating_peril_scoring_api)' pytest.log` → no line, grep rc 1. The 13 `FAILED` lines by file (`grep -E '^FAILED' pytest.log | sed 's/ - .*//' | cut -d: -f1 | sort | uniq -c`): `test_audit_docs_finding_citations` 1, `test_audit_docs_ids` 2, `test_audit_docs_process_core_digest` 2, `test_audit_docs_w37_11_ceiling` 1, `test_doc_index` 1, `test_register_lint` 3, `test_register_owed` 1, `test_repository_invariants` 2 = 13: exactly the 8-file docs-audit set of the common brief's item 31. The two oracle files therefore passed, including the formerly red offset test.

## Whole-window completeness (lead's addition, same method)

The one command that lists the slice-own non-docs paths of the window (first-parent, non-merge commits only; without `--first-parent` the list also holds main's own commits that the merges brought, which are not the slice's):

```
git -C <wt> log --first-parent --no-merges --format= --name-only bf845e11..aaebd5df | sort -u | grep -v '^docs/'
```

Output (tree `aaebd5df`), complete:

```
backend/tests/test_rating_glm_model_call.py
backend/tests/test_rating_peril_scoring_api.py
```

One verdict per path, per slice-own commit (`git show --format= --name-only <c>`):

| Commit | Path | Verdict |
|---|---|---|
| `2a1588c9` | `LG-1896` | docs; the B1′/B2′ remedy, see below |
| `37e7726a` | `RS-1897`, `RS-1898` (added) | docs; fold of the two prior audit records at working ids |
| `66d5a35d` | `docs/INDEX.md` | generated |
| `aab18283`, `2ec62327` | `LG-1896` | docs; Task 6 diagnostic-window readings (the ledger's own text) |
| `5dc23c98` | `backend/tests/test_rating_glm_model_call.py`, `backend/tests/test_rating_peril_scoring_api.py` | non-docs; the three oracle re-expressions, covered by the 15:23:06 ruling (read in full above) |
| `1f41acc6` | `LG-1896` | docs; the RED, the ruling and the three changed asserts |
| `93bf1321` | the same two test files + `LG-1896` | comment-only (the ruling quoted at each assert) + ledger |

No slice-own non-docs change exists outside the three oracle commits' two files, so there is no uncovered non-docs change and no B-item on this axis. The three oracle re-expressions are exactly: `test_rating_glm_model_call.py` `test_a_rating_version_pinning_a_fitted_glm_compiles_and_scores` (:137 before the helper's comment lines), `test_a_model_offset_glm_scores_with_its_source_model` (:202), and `test_rating_peril_scoring_api.py` `test_a_rating_version_pinning_an_approved_peril_structure_compiles_and_scores` (:217); the only other change is the literal `"dp": 9` → `"dp": RISK_OUT_DP` in `_algorithm`. The merges' non-docs paths (main's code) are in the merge table: each equals its main parent.

## Status of RS-1898's B1′ and B2′

Both were discharged by `2a1588c9` (RS-1898 line 99: "B1′/B2′ discharged 2a1588c9, verified by the lead directly, to-lead 2026-10-23 11:38:45 BST"); this audit re-read them in `LG-1896` at `aaebd5df`.

- **B1′** — "`r/b1-green.log` line 1 is not a head sha, and the census test has no committed-head run … Remedy: one `run-small` run of `test_quote_input_raise_sites.py` + `test_rating_decimal_outputs.py` at the final head, sha on line 1, quoted in the LG (or leave it to the gate … and say so in the LG)." **LANDED** (`2a1588c9`) at `LG-1896:105`: the old `b1-green.log` line is marked "superseded: line 1 was not a head sha"; "B1′ (committed head `bf845e11`): `test_quote_input_raise_sites.py` alone via `run-small.sh` … `19 passed in 6.84s`, `rc=0` … (`b1-green-committed.log`, line 1 = `bf845e116c30…`)". Note: the run is of the census file alone, not the two files the remedy names; the remedy's alternative (the gate includes the file) also applies, and the census entry is still present at `aaebd5df` (`packages/pricing-core/tests/test_quote_input_raise_sites.py:86`, `("rating/score.py", "_build_outputs"): 1`) with the file passing in the gate (not among the 13 `FAILED` lines).
- **B2′** — "`LG-1896:85` (Task 4 RED `02d4bc6d` / GREEN `4ba9d138`, the direct-call harness) has no log and is not marked superseded. Remedy: mark it 'superseded (no log)' at the line, or re-derive it …". **LANDED** (`2a1588c9`) at `LG-1896:85`: "B2′: this RED/GREEN pair is superseded (no log): the direct-call harness was not kept … The committed-head evidence is `scripts/generate-contracts.py --check` `58 generated contracts match the models`, rc 0, at `bf67458e` (`r/b4-contracts.log`) and `test_contracts.py` in the backend window log …; the gate decides it". Neither is SUPERSEDED as a finding or NOT LANDED. The gate's `contracts.rc` is the decisive run and is read from the stand-under-1(f) entry (rc 0), not re-run here.

## Findings

- **No B-item.**
- **N1 (note, no action).** `pytest.log` does not open with `head=<sha>` (common brief item 37): its first line is a progress row. The head is on `gate.log` line 1 and in the `GLM_PREDICT_TIMING … head=aaebd5df…` lines inside `pytest.log` (lines 20 and 22), so the log is attributable; the form rule is not met to the letter.
- **N2 (note).** The window is wider than the first brief listed (see the table); every extra slice-own commit is LG, RS or INDEX only.
- **Owed, not run by this seat:** `ruff format --check` on the two files (the ledger and the maintainer both say rc 1 pre-exists on main's hand-aligned versions; this audit did not reproduce it), `audit-docs`, and the mint-time re-run of the 8 docs-audit tests on the minted head (item 31's conditions), which are the lead's and the executor's.

## Proposed verdict

**CLEAN.** The oracle fix implements the 15:23:06 ruling to the letter, weakens nothing, keeps the markers, and the gate's pytest shows no failure in those files; all four merges brought only main's content. The slice's gate failures are exactly the item-31 class. Proposal only; the verdict is the lead's.
