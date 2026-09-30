---
id: FD-9972
family: finding
title: Working ids collided twice because two allocators picked them and the free-check reads only pushed origin refs
status: active
created: 2026-09-30
owner: auditor
tree: 8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862
corrected_by: []
relates: [WK-1178]
---

# FD-9972 — Working ids collided twice: two allocators, and a free-check blind to unpushed work

**Working id 9972**, reserved to the auditor by the lead (the lead's reservation table, `eta.md`), filed as a working id and
minted at the records PR. It is cited by number, not as a token, until then.

## Finding

**Severity: LOW; owner WK-1178.** Both collisions were caught **before a mint**, and `doc-id.py` assigns the final id at the
mint, so the cost was rework and confusion, not a duplicate governed id. The maintainer's order: "FILE THE FD NOW: owner
WK-1178, LOW (caught before a mint; doc-id assigns the final ids)". A working id is picked by hand, from a free-check that
cannot see everything that holds one, by more than one allocator. That is a process gap, and it has now failed twice in one
day.

- **Instance 1: 9991, 2026-09-30 about 11:30 BST.** A finding drafted under working id 9991 (the perils finding, now
  under 9995) collided with a ledger that already held it: the commit is `939799b3`, dated 2026-09-30 11:31:20 BST
  (10:31:20Z), subject "docs(findings): the perils finding (working id 9995) — renumbered from 9991, which executor-690s1's ledger holds;
  owner basis confirmed". The other holder, the ledger numbered 9991 (WK-690 Slice 1's
  ledger, executor-690s1), is on the executor's branch: `git log --all --grep='the ledger numbered 9991'` finds its commits, and the earliest
  whose subject names the id is dated 2026-09-30 11:37 BST, **after** the collision was caught, so the reservation had no
  pushed trace that the free-check could have read when the finding took the number; it existed on the executor's branch
  and in a brief.
- **Instance 2: 9970, 2026-09-30 about 17:05 to 17:12 BST.** The auditor (this finding's author) picked working id 9970
  for the open question that FD 9969 raises, on a branch not yet pushed (its head commit is `e86c6e42`, dated 17:07:35 BST),
  because the lead's brief for FD 9969 said "an OQ working id (check it free)". The lead had, meanwhile, assigned 9970 to
  auditor-933 for a different finding. The lead's free-check (a `git grep` over `origin` refs, and `eta.md`) could not see the
  unpushed commit. **Resolution: the OQ kept 9970 and auditor-933's finding moved to 9971** (`eta.md`, the lead's reservation
  table: "9971 | FD | auditor-933 | /score 200 response untyped", and the row "9970 | OQ | auditor-close1255 (via FD 9969) …
  self-picked ~17:05 (collision instance 2)"). The rule that authors do not pick did not yet exist; it was made after this
  (below).
- **Instance 3, a near-collision: 9970 again, 2026-09-30 about 17:12 BST.** auditor-933 filed the `/score` finding under
  working id 9970 (commit `cfe3359d`, 2026-09-30T16:12:07Z = 17:12 BST, branch `fd-9970-score-200-untyped`, subject "docs(findings):
  the working-id-9970 finding — the /score 200 response has no schema in the generated OpenAPI (working id)"), because the lead's correction to
  9971 was a chat message that crossed with its work; the finding is being re-numbered to 9971 (the lead's report, not yet
  seen on a pushed ref). Its free-check looked only for its own family's file, so it could not see the open question already
  pushed under 9970 in the same number space. **Two more causes** follow from it: a **correction travels by chat**, and a
  free-check matches **one family** only.

## Evidence

**1. The maintainer's entries, verbatim, with their headers** (`~/gi-pricing-plan.local/channel/to-lead.md`, outside the
repository).

> ## 2026-09-30 11:30:55 BST — the working-id collision (9991): interim OK, plus a WK-1178 item for a mechanical fix
> - The eta.md reservation list is **accepted as the interim.**
> - **A WK-1178 backlog item (planner logs it; not an FD unless it recurs):** make working-id allocation read **one shared append-only reservation ledger** (for example `~/gi-pricing-plan.local/working-ids.md`: id, holder, purpose, date). The allocation script, and any role's picker, **refuses an id already in the ledger or on any origin ref or PR title**. A reservation that exists only in a brief is the invisible case; a check should make it impossible, not a habit.

(The entry has a third bullet, unrelated status noting; it is omitted here.)

> ## 2026-09-30 17:09:40 BST — working-id collision: FILE THE FD NOW (my 11:30:55 trigger "unless it recurs" has fired)
> - **File an FD, owner WK-1178, severity LOW** (both collisions were caught before a mint, and `doc-id` minting assigns the final ids). It records:
>   - both instances with their dates;
>   - the cause as you stated it: two allocators, and a free-check that greps pushed origin branches only, blind to unpushed branches;
>   - the fix direction: the reservation ledger (a single record of reserved working ids that every allocator writes before use).
>   The backlog item points at the FD instead of duplicating it.
> - **Your interim is accepted as the rule until the ledger lands:** the lead is the only allocator of working ids of every family (FD, RL, PL, OQ, and all secondary ids); authors ask and do not pick. Put this rule in the dispatch brief of every spawned author, not only in chat.

The 17:08:59 BST entry ("… the 9970 id collision", item (3)) had noted the second instance and its resolution.

**2. The cause: two allocators, and a check blind to what is not on an origin ref.** Before the 17:09:40 rule, ids were
picked by the lead **and by authors** (the lead's brief told the author to "check it free"). The check that both used reads
pushed `origin` refs and `eta.md`. It cannot see: (a) a commit on a local branch that has not been pushed; (b) an edit in a
worktree that is not committed; (c) a reservation that lives in a brief or another role's ledger only (instance 1).

**3. The blind spots, measured** (scratch worktree from `origin/main` `8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862`, removed
afterwards; the plant an FD numbered 9990 was a scratch string never pushed and never used as an id). Predicate, verbatim, a
family-prefixed token: `(^|[^0-9A-Za-z.])(FD|OQ|RL|PL|SL|LG|CR|WK|RFC|ADR|NT|RS|F)-0*9990([^0-9]|$)`, `git grep -c -E … <ref> --
docs`, summed per ref set.

| Check | Over | Planted an FD numbered 9990 on an unpushed local commit | An uncommitted an OQ numbered 9990 edit in a worktree |
|---|---|---|---|
| A: the lead's free-check | the 66 `origin` refs | **0 hits, reads free** | not seen |
| B: A plus every local branch | `refs/heads` | **1 hit, reads taken** | not seen |
| C: B plus every worktree's files on disk | `git worktree list`, then a file scan | taken | **found (1)** |

So a check over `origin` refs cannot tell that an id is held by unpushed work; adding local refs and worktrees does. It
still cannot see a reservation that exists only in a brief or another role's private ledger, which is instance 1.

**4. The first free-check pattern was too loose.** The lead's first pattern, `(-|0)NNNN\b`, matches a bare number after a
hyphen or a zero. Measured for 9972 at the tree above: `git grep -c -E '(-|0)9972\b' <ref> -- docs` summed over the 66
`origin` refs gives **53 hits**, all one occurrence counted once per ref that contains it: `docs/findings/FD-01294-*.md:27`,
which mentions the branch name `` `dm-rl-9972-dp-s1-2` `` (a branch, not an id). The family-prefixed pattern of
evidence 3, run for 9972, gives **0 hits** on the same refs. (Numbers such as `0.99972` would match the loose pattern too.)
A free-check must be prefixed by an id family.

## Disposition

**Proposed by the auditor; the verdict is the lead's and the maintainer's.** Owner **WK-1178**, on the maintainer's order.

- **Interim rule, in force until the ledger lands (the maintainer's 17:09:40 BST entry):** the lead is the only allocator of
  working ids of every family (FD, RL, PL, OQ and every secondary id); authors ask and do not pick; the rule goes in the
  dispatch brief of every spawned author.
- **Fix direction (the maintainer's 11:30:55 BST entry):** one shared, append-only reservation ledger, for example
  `~/gi-pricing-plan.local/working-ids.md` with id, holder, purpose and date, **written before use** by every allocator; the
  allocation script and any role's picker **refuse an id already in the ledger or on any origin ref or PR title**. Two additions
  from the measurements above, for the WK-1178 item to weigh: the refusal check should also read local refs and worktrees
  (evidence 3), and it must use a family-prefixed pattern (evidence 4).
- **Carrying slice: the slice with working id 9836** (roadmap, draft, PR #982, head `7b43d278`, a WK-1178 backlog item with no leaf plan yet). It
  proposes the ledger and an allocator in `scripts/doc-id.py` that refuses an id held in the ledger, on any `origin` ref or in
  an open PR title. **Coverage of the three causes, read from its text:** (1) *two allocators*: covered in aim ("working ids
  are picked by hand", make an invisible reservation impossible) but only if every picker goes through the script; the slice
  does not say that hand-picking is retired. (2) *a free-check blind to unpushed work*: **gap**: it names `origin` refs and PR
  titles only, which is instance 2's blind spot (evidence 3 checks A and B), so local refs and worktree files must be added.
  (3) *a single-family pattern, and corrections by chat*: **gap**: the slice names no matching pattern (evidence 4 needs the
  family-prefixed one, across all families), and says nothing of a re-assignment: it must be an appended ledger row that
  supersedes the earlier holder, not a chat message (instance 3). It also leaves open whether the ledger is in the repository
  or local; only a local ledger can see an unpushed reservation (instance 1), and only a repository one can be read by CI.
  The slice's remark "not an FD unless it recurs" is discharged: it has now recurred.
- **Acceptance, red first, on broken input** (so the fix is not a green stamp): with an id present only in the ledger, only on an
  unpushed local commit, and only in an uncommitted worktree edit, the picker refuses each in turn; with the ledger check removed,
  each is accepted and the test fails; a bare number such as `0.99972` does not refuse an id.
- **The backlog item points at this finding instead of duplicating it** (the maintainer's 17:09:40 BST entry).

**Event that next confirms or discharges it:** WK-1178 lands the ledger and the refusing picker, red first as above.

Ownership shape: workstream

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The owner and the severity are the
maintainer's, per the entries quoted under evidence 1.
