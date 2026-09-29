---
id: FD-1208
family: finding
title: PL-1205 Task 0's precondition for PR 868 self-matches the plan's own squash commit body
status: active
created: 2026-09-28
owner: auditor
tree: ce27e5604c8e932437819dcbc6e4872270cdd4f4
corrected_by: []
relates: [PL-1205, PL-1189, WK-1178]
---

# FD-1208 — PL-1205 Task 0's precondition for PR 868 self-matches the plan's own squash commit body

**Severity: low.** The auditor filed this finding on 2026-09-28, on the lead's instruction. The
planner-side executor (executor-s2) reported it at about 20:24 BST during the hold. It is a
defect in a **frozen plan's** check, so the finding proposes; whether `PL-1205` gets a dated
correction is the deputy's.

## Finding

`PL-1205` Task 0b requires that #868 (the WK-1178 blob-route PR) is on `origin/main` before
Task 5, and gives the check as `git log --grep '(#868)' -1 origin/main`. Task 0's first
precondition uses the same form for Slice 2: `git log --grep 'PL-1189' -1 origin/main`.

`git log --grep` searches the **whole commit message**, subject and body. The squash commit that
merged `PL-1205` itself (`ce27e560`, #866) has a body that names both strings. So both checks
return `ce27e560`, the plan's own squash, whether or not the thing they test is on main. The
#868 check **passes while #868 is not on `main`**, so its "if it is absent, stop and report"
branch cannot fire.

## Evidence

Run on 2026-09-28 at 20:39:59 BST, with `origin/main` at
`ce27e5604c8e932437819dcbc6e4872270cdd4f4`:

```text
$ git log --grep '(#868)' -1 --format='%h %s' origin/main
ce27e560 docs(plans): PL-1205 — WK-672 Slice 3 leaf plan: property assertions and regression runs (#866)     (rc 0)
$ git log --grep 'PL-1189' -1 --format='%h %s' origin/main
ce27e560 docs(plans): PL-1205 — WK-672 Slice 3 leaf plan: property assertions and regression runs (#866)     (rc 0)
$ git show -s --format=%B ce27e560 | grep -n -F -e 'PL-1189' -e '(#868)'
3:WK-672 Slice 3 leaf plan, minted PL-1205 and activated in one step (the route PL-1189 used): ...
5:- Scope: ... Task 5 is gated on the WK-1178 blob-route PR (#868) being on main.
```

The sound forms, at the same tree:

```text
$ git log --format=%s origin/main | grep -F '(#868)'                    (no output, rc 1)
$ git log --format=%s origin/main | grep -F '(#867)'
feat(rating): WK-672 Slice 2 — Golden Quotes and promotion re-scoring, PL-1189, LG-1204 (#867)   (rc 0)
$ git grep -c QUOTE_INPUT_BLOB_COLUMNS origin/main -- backend/src/app/api/blobs.py     (no output, rc 1)
```

So at this tree #868 is **not** on `main`, and the plan's check says it is. The `PL-1189` check
gives the right answer only by luck: #867 is on main, but the check would also pass if it were
not.

## Proposed correction

Match the commit **subject**, and add a symbol check that the fix's mechanism exists:

- `git log --format=%s origin/main | grep -F '(#868)'` must print a line, and
- `git grep -n QUOTE_INPUT_BLOB_COLUMNS origin/main -- backend/src/app/api/blobs.py` must
  find the symbol (`PL-1205` Task 0b step 2 relies on it).

The same subject-form rule applies to the `PL-1189` check in Task 0.

## Disposition

**Carry forward, unowned — until the deputy decides** whether `PL-1205` gets a dated correction. Event: the
deputy's ruling on that correction, or the merge of #868 with Task 5 Step 0 run in the
subject-plus-symbol form (which discharges the practical risk for Slice 3).
