---
id: FD-1159
family: finding
title: Map-plan item 11's ten broken-input proofs for checks 30–39 do not exist in its stated form — four checks have no fixture, and two prove only a disclosed failure
status: active
created: 2026-09-27
owner: auditor
tree: 47065da50c34f0bf613f7dd972675c96d12f78ed
corrected_by: []
relates: [PL-939, PL-1144]
---

# FD-1159 — Map-plan item 11's ten broken-input proofs for checks 30–39 do not exist in its stated form — four checks have no fixture, and two prove only a disclosed failure

Filed by the auditor at 2026-09-27 15:04:42 BST, under the lead's adoption of 2026-09-27 14:58:11 BST.
The lead adopted the auditor's source contradiction and the verdicts on each check. It is
filed in one commit with FD-1154 to FD-1162, before the W37 closure record cites any of them.

## Finding

`PL-939`'s Acceptance Standard item 11 reads: *"Each of checks 30–39 has been shown to exit 1
on a deliberately broken fixture under `tests/fixtures/docs-ids/`, one fixture per check, and
the ten proofs are listed in the closure record with the fixture path and the failure
message."* `PL-1144` expected to take the ten proofs from the earlier closure records of this
Work. **They are not there.** No closure record, ledger or plan names a `w37-4-checks` fixture
or a `test_check_3x` test. The earlier records hold only incidental mentions.

At `47065da5`, the proofs that exist are:

- **Checks 30, 31, 33, 34, 35 and 37** each have a broken fixture under
  `tests/fixtures/docs-ids/w37-4-checks/` and a test that asserts the check's failure message.
- **Check 39** is proven on the shared corpus `tests/fixtures/docs-ids/w37-3-corpus/`, and on a
  stale index built in `tmp_path`. It has no fixture of its own.
- **Checks 32 and 36** are proven only on files built in `tmp_path`. Their failures are keyed to
  the sentinel path, and the residue ceiling **discloses** them (classes `h1-check32` and
  `h1-check36`). So under `main()` neither broken input exits 1.
- **Check 38** is warn-only by design, so no input can make it fail. Its proof is that it never
  fails.
- **No proof observes an exit code.** Every test asserts on the `failures` list. Exit 1 is
  inferred from `main()`'s rule.

RFC-937 §5.7 (`:418`) specifies *"checks 30–39 on `tests/fixtures/docs-ids/`, five broken
fixtures"*, while the map plan's item 11 says ten. The two sources disagree on the count.

## Evidence

A read-only evidence run in a detached worktree at `47065da50c34f0bf613f7dd972675c96d12f78ed`,
2026-09-27 14:50:32–14:52:22 BST. The 16 pytest nodes in `tests/test_audit_docs_ids.py` for
checks 30–39 all passed (`16 passed`). Each check's fixture and verbatim message will be listed
in the W37 closure record's item-11 table. The auditor confirmed the fixture set with
`ls tests/fixtures/docs-ids/w37-4-checks/`: `check30-*` (six entries), `check31`,
`check33-bad-status.md`, `check33-supersedes`, `check34-dangling-corrected-by`,
`check35-bad-owner.md`, `check35-readme-allowlist` and `check37`. There is no entry for 32, 36,
38 or 39. `git grep -l -E 'w37-4-checks|test_check_3[0-9]' -- docs` finds no closure record.

## Disposition

**Per check, as adopted by the lead on 2026-09-27 at 14:58:11 BST:**

- 30, 31, 33, 34, 35 and 37: evidenced.
- 39: evidenced, on the shared corpus.
- 38: not executable as written. The never-fails proof stands under `PL-939`'s G3.
- 32 and 36: **delivered but untested** in item 11's form.

**The gap is deferred with an owner — the lead.** Event: the create-read-retire audit's first
slice. A fix would add committed fixtures for 32 and 36 whose failures are keyed to their own
path, so that they count, plus one test that runs `audit-docs.py` and reads its exit code.
