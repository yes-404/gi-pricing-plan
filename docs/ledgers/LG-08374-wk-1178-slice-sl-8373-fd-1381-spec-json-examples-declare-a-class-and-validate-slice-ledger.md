---
id: LG-8374
family: ledger
title: WK-1178 slice SL 8373 — FD-1381's check, every JSON example in docs/specs declares a class or illustrative and is validated (slice ledger)
status: active
created: 2026-11-07
owner: executor
tree: d0b1f999f6b27f639e1a90af75ae79552d0aadad
phase: P2
work: WK-1178
slice: SL-8373
plans: [PL-2053]
corrected_by: []
relates: [FD-1381, PL-2053, RL-2054]
---

# LG-8374 — WK-1178 slice SL 8373: the spec-example check

**GO:** to-lead "2026-11-07 18:29:31 GMT" (Maintainer): "SL 8373 SEAT: YES, exec-sl8373 on brief af5502c1265c, ... S1 + S2 now ...; S3 (the audit-docs.py check) and S4 (the marks) only after LAST-2 is merged on main and into the branch, else push after S2 and stop; S5's gate at SL 8381's head (16:46:26) ...; no PR, mint or gate in this seat; DB-free; audit-docs under gate-2's flock".
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

Row SL 8373 of PL-2053 (Steps S1 to S5; acceptance A5 to A14). Base `origin/main` 3c3ee5cb. Seat exec-sl8373 (Sonnet 5.5, medium). Branch `sl-8373-spec-examples`, worktree `.claude/worktrees/sl-8373`. This ledger covers S1 and S2 so far.

### Task list

- **S1** (A6): the rule first. `.claude/skills/spec-change/SKILL.md` rule and `Verified` line, `.claude/skills/docs-audit/SKILL.md` check 40 row, the numbered line 40 in the docstring of `scripts/audit-docs.py`. Commit d0b1f999.
- **S2** (A7): `tests/test_spec_examples.py` and `tests/fixtures/spec-examples/ra-c535b19d.json` (the first `json` block after `### 4.1 ` at `c535b19d`, extracted by awk, parses as JSON). Plus the stub of S3's text (`SpecFence`, `spec_fences`, empty `check_spec_examples`) above `def main` in `scripts/audit-docs.py`, so a red is never an import error.

### Gate

Not run (S5, at SL 8381's head).

### Audit

(none yet)

### Build log

**Deviation, 2026-11-07:** the brief limits S1/S2's `scripts/audit-docs.py` edit to S1's docstring line; the plan's S2 text requires the stub above `def main` (the plan says LAST-2 has no hunk there). The stub is what makes T4 to T6 red by cause. Reported to the lead.
**2026-11-07:** S2's stub in audit-docs.py precedes LAST-2's merge; lead 31's ruling, from-lead 2026-11-07. Touch no other line of audit-docs.py; a conflict there at the LAST-2 merge is a STOP, reported verbatim.
**Deviation, 2026-11-07:** the plan's test and parser code was reformatted for `ruff check .` (E501, PT018, I001) and `mypy --strict` (annotations, `assert spec.loader is not None`); behaviour unchanged.

**S2 red** (log `~/gi-pricing-plan.local/scratch/sl-8373-spec-examples/s2-red.log`, tree d0b1f999f6b27f639e1a90af75ae79552d0aadad plus the S2 working-tree files, DB-free, run-small):

```
head=d0b1f999f6b27f639e1a90af75ae79552d0aadad (+uncommitted S2 stub, tests, fixture)
FAILED tests/test_spec_examples.py::test_check_40_refuses[json-{}-no schema= or illustrative marker]
FAILED tests/test_spec_examples.py::test_check_40_refuses[-{}-declares no language]
FAILED tests/test_spec_examples.py::test_check_40_refuses[json schema=Dataset-{-does not parse]
3 failed, 4 passed, 1 skipped in 0.95s
rc=1
```

The cause is the empty check recording no failure (`assert []`), not an import or fixture error. The skip is the empty `MARKED` parametrisation (no block is marked yet). The fixture test passes already (it needs no check); its mutation proof (T8) is S4's. `ruff check .` rc 0, `mypy` "Success: no issues found in 254 source files" at this tree.

**Check 32 read (2026-11-07, plain audit-docs, gate-2 flock):** the ~884 lines plain `audit-docs.py` prints are the DISCLOSED section ("DISCLOSED (849, at or under the W37-11 residue ceiling)"), not failures. At base 3c3ee5cb a detached comparison printed "All checks passed." with the same disclosed lines (244 check-32, 497 check-36, 71 check-30, 27 check-35); at b5c21895 FAILED (2) were check 31 (allocation gap) and check 32 (SL 8373 does not resolve in the INDEX), both this slice's own working ids. Plain is the gate's mode; used from here on. Logs: `scratch/sl-8373-spec-examples/audit-plain*.log`.

**Merge of LAST-2:** `git merge --no-ff origin/main` (c602a539, #1454): auto-merged `scripts/audit-docs.py`, conflict only in `docs/INDEX.md` (taken theirs, regenerated, `doc-index.py --check` rc 0). Merge commit b3079458.

**S3** (A7, A9): the check body from the plan, called after `check_register_grammar()` at the tail of `main()`; lines wrapped for E501. Tree b3079458+S3. `run-small` on `tests/test_spec_examples.py`: "7 passed, 1 skipped in 0.96s", rc=0 (T4 to T6 green). `ruff check .` rc 0; `mypy` "Success: no issues found in 256 source files". Plain audit-docs now FAILED (69): check 31, check 32 (own ids) and 67 check-40 lines on the real specs, as the plan requires before S4 ("check 40: 63 json blocks: 0 schema, 0 illustrative, 63 unmarked"; 4 bare fences: 00:14, 00:79, 00:269, 00:365).

**S4** (A5, A7 to A10, A12; one commit): `scripts/audit-docs.py` untouched. Marks by `~/gi-pricing-plan.local/scratch/sl-8373-spec-examples/mark.py` from the ruling's end state (RL-2054): 32 `schema=` and 31 `illustrative` blocks (63, parts sum), 4 bare fences retagged `text` (`00:14`, `00:79`, `00:269`, `00:365` at this tree); only fence lines changed (`git diff -U0 -- docs/specs` shows 67 changed lines, all fence lines: 63 + 4). Classes by `classify.py` (tries every `BaseModel` in `model_schema.__all__`): `03:551` is `GoldenQuoteNotChecked` (the block is the not-checked form its prose names; `RateTableCell` also passes and is not the shape). Illustrative: 20 that do not parse, 6 with no class (`01:794`, `05:158`, `05:216`, `05:260`, `06:190`, `07:272`), rows 5, 15, 17, 18 of RL-2054 (`01:582`, `03:951`, `04:254`, `06:346`) and row 19's second block (`06:483`). `ILLUSTRATIVE_CEILING = 31`. `backend/tests/test_objective_submission.py` regex widened to `` r"```json[^\n]*\n(.*?)\n```" `` (one line; asserts untouched).

Plain audit-docs at this tree (log `audit-s4.log`): `check 40: 63 json blocks: 32 schema, 31 illustrative, 0 unmarked` (A9); FAILED lists only check 31 and check 32 on SL 8373 / LG 8374 (own working ids). Green (run-small, DB-free): `tests/test_spec_examples.py tests/test_audit_docs_check_prefixes.py packages/pricing-core/tests/test_rating_declared_reads.py` "59 passed in 13.39s" rc=0 (A11, A13). The `-k` test of A4 cannot go through run-small (it accepts file names only; the file holds DB tests): its body was run as a script, `/tmp/t4.py`, DB-free: old regex `` ```json\n(.*?)\n``` `` finds no block (the refusal a fence token causes), new regex `ok 7 entries`. The node id itself is owed to CI or the gate.

**Mutation proofs (A7, A10), each reverted and proved reverted by `cmp` against the pre-mutation copy:**

```
--- T7 drop _validate assert  head=3c980951c34ea3d6745030b6f41d632bef82fc6c+S4
E       AttributeError: 'NoneType' object has no attribute 'model_validate'
FAILED tests/test_spec_examples.py::test_an_unknown_class_is_refused - Attrib...
1 failed, 38 passed in 1.00s
rc=1
reverted7
--- T8 _validate returns before model_validate  head=3c980951c34ea3d6745030b6f41d632bef82fc6c+S4
E       Failed: DID NOT RAISE ValueError
FAILED tests/test_spec_examples.py::test_the_example_the_finding_named_fails
1 failed, 38 passed in 0.96s
rc=1
reverted8
--- T9 _SPEC_FENCE_RE loses \s{0,3}  head=3c980951c34ea3d6745030b6f41d632bef82fc6c+S4
E       assert 63 == 62
FAILED tests/test_spec_examples.py::test_the_census_is_a_second_reading_of_the_same_lines
1 failed, 37 passed in 1.01s
rc=1
reverted9
--- T10 ceiling less 1  head=3c980951c34ea3d6745030b6f41d632bef82fc6c+S4
E       assert 31 <= 30
FAILED tests/test_spec_examples.py::test_the_exemption_set_only_shrinks - ass...
1 failed, 38 passed in 0.97s
rc=1
reverted10
```
T9's red is "63 == 62": the census regex (`^\s*`) finds 63, the parser cut to column 0 finds 62 (the shape of `03:1006`). T4 to T6's red is in S2/S3 above. Mutations ran at head 3c980951 plus the S4 working tree.

**Import closure (item 29)**, changed sources: `scripts/audit-docs.py` (imported by path, no module name), `backend/tests/test_objective_submission.py`, `docs/specs/*`. Tests reading `docs/specs` (item 39 predicate `grep -lE 'docs/specs|"docs" */ *"specs"' backend/tests tests`) and the eight docs-audit files: run at S5 with the re-merged head.

## PRs

(none; no PR in this seat)
