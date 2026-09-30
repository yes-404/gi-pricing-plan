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

**Severity: LOW; owner WK-1178.** Both collisions (and a third near-collision, below) were caught **before a mint**, and `doc-id.py` assigns the final id at the
mint, so the cost was rework and confusion, not a duplicate governed id. The maintainer's order: "FILE THE FD NOW: owner
WK-1178, LOW (caught before a mint; doc-id assigns the final ids)". A working id is picked by hand, from a free-check that
cannot see everything that holds one, by more than one allocator. That is a process gap, and it has now failed twice in one
day, and a third time was caught.

- **Instance 1: 9991, 2026-09-30 about 11:30 BST, a near-simultaneous race.** A finding drafted under working id 9991 (the
  perils finding, now under 9995) collided with a ledger numbered 9991 (WK-690 Slice 1's ledger, executor-690s1). Times, from
  commits and the remote-ref reflog of this clone (`git log -S` and `git reflog show --date=iso origin/sl-1271-arity-refusal`):
  the ledger was created in commit `463abf2c` (message "pin sympy==1.14.0 …", which does not name it; `git log -S` finds the
  ledger's first appearance there) at 11:28:52 BST, amended 11:29:47, and **pushed at 11:29:49 BST** (10:29:49Z); the
  perils finding's commit `97f5a4ae` is dated 11:29:20 BST, **29 seconds before that push**; the maintainer's entry is
  11:30:55; the renumber `939799b3` is dated 11:31:20 BST (subject "… renumbered from 9991, which executor-690s1's ledger
  holds; owner basis confirmed"). So a free-check at pick time could not have seen the reservation: it was a local commit,
  and it reached `origin` 29 seconds after the finding took the number. (An earlier draft of this essay dated the ledger by
  the first commit **message** naming it, 11:37 BST; that instrument reads messages and misses a ledger created in a commit
  about something else. As a cross-check only, `git log --all --grep='L[G]-9991' --oneline` returns 5 commits, the earliest dated 11:37 BST (10:37:11Z), after
  the collision, which is why it misses the race.)
- **Instance 2: 9970, 2026-09-30 about 17:05 to 17:12 BST.** The auditor (this finding's author) picked working id 9970
  for the open question that FD 9969 raises (the lead's eta row records "self-picked ~17:05"), because the lead's brief for FD 9969
  said "an OQ working id (check it free)". The lead had, meanwhile, assigned 9970 to auditor-933 for a different finding.
  The auditor's commit `e86c6e42` is dated 17:07:35 BST and was **pushed at 17:07:36 BST** (remote-ref reflog of
  `origin/fd-9969-decimal-output-float`, 16:07:36Z). **What is established and what is not:** at pick time (about 17:05) the
  pick was unpushed. The lead reports (the lead's own statement, not a recorded measurement) that a re-check of 9970 (a loose-pattern
  `git grep` over `refs/remotes/origin` after `git fetch`) read it free, that the time of that check was **not recorded to the
  second**, and that it ran shortly before the FD 9969 report reached the lead (about 17:08 BST); the lead later verified that this
  pattern does match the content of `e86c6e42` (OQ 9970 twelve times in five files), so **the pattern was not the cause**.
  Either the check preceded the push by seconds (a race, as in instance 1) or the fetch did not see it; **neither is established
  to the second**. That is itself a gap: a check with no timestamp cannot be placed against a push. **Resolution: the OQ kept
  9970 and auditor-933's finding moved to 9971** (`eta.md`, the lead's reservation table: "9971 | FD | auditor-933 | /score 200
  response untyped", and the row "9970 | OQ | auditor-close1255 (via FD 9969) … self-picked ~17:05 (collision instance 2)"). The
  rule that authors do not pick did not yet exist; it was made after this (below).
- **Instance 3, a near-collision: 9970 again, 2026-09-30 about 17:12 BST.** auditor-933 filed the `/score` finding under
  working id 9970 (commit `cfe3359d`, committed 17:12:07 BST and pushed 17:12:10 BST, branch `fd-9970-score-200-untyped`, whose
  subject, not quoted here, names working id 9970 and says the `/score` 200 response has no schema in the generated OpenAPI),
  because the lead's correction to 9971 was a chat message that crossed with its work; the finding was re-numbered to
  9971 in commit `4f38b04c`, committed 17:14:43 BST and pushed **17:15:10 BST** (remote-ref reflog of that branch). **This is not the unpushed blind spot:** 9970 had been on `origin`
  since 17:07:36, so a check over `origin` refs **would have caught it**. Its causes are that a **correction travels by chat**
  and that its free-check looked only for its own family's file, so it did not see the open question under the same number in
  another family.

## Evidence

**1. The maintainer's entries, verbatim, with their headers** (`~/gi-pricing-plan.local/channel/to-lead.md`, outside the
repository). The 11:30:55 entry also has a third bullet of status notes, omitted here, one clause of which (the perils finding "renumbered to 9995") corroborates instance 1.

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
pushed `origin` refs and `eta.md`. It cannot see: (a) a commit on a local branch that has not been pushed (instance 1 at pick time; instance 2 unless the check followed the push); a push that lands seconds after the pick (a race, instances 1 and 2), for which a check with no recorded time cannot be placed; (b) an edit in a
worktree that is not committed; (c) a reservation that lives in a brief or another role's ledger only (instance 1).

**3. The blind spots, measured** (scratch worktree from `origin/main` `8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862`, removed
afterwards, measured at the refs of that time (the baseline for 9990 was 0, before this essay existed; the essay now mentions 9990, so a re-run must use an id absent from it); the planted FD numbered 9990 was a scratch string never pushed and never used as an id). Predicate, verbatim, a
family-prefixed token: `(^|[^0-9A-Za-z.])(FD|OQ|RL|PL|SL|LG|CR|WK|RFC|ADR|NT|RS|F)-0*9990([^0-9]|$)`, `git grep -c -E … <ref> --
docs`, summed per ref set.

| Check | Over | An FD numbered 9990 planted on an unpushed local commit | An OQ numbered 9990 in an uncommitted worktree edit |
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
evidence 3, run for 9972, gives **0 hits** on the same refs. (Numbers such as `0.09972` would match the loose pattern too.)
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
  titles only (and the ledger itself, which could carry an unpushed reservation **if every allocator writes the ledger before use**), which is the blind spot of evidence 3's checks A and B (instance 1 at pick time; instance 2 unless the check followed the push), so local refs and worktree files must be added.
  (3) *a single-family pattern, and corrections by chat*: **gap**: the slice names no matching pattern (evidence 4 needs the
  family-prefixed one, across all families), and says nothing of a re-assignment: it must be an appended ledger row that
  supersedes the earlier holder, not a chat message (instance 3). It also leaves open whether the ledger is in the repository
  or local; only a local ledger can see an unpushed reservation (instance 1), and only a repository one can be read by CI.
  The slice's remark "not an FD unless it recurs" is stale: the maintainer's 17:09:40 BST entry (evidence 1) supersedes it by filing this FD, and the slice text should point here.
- **Acceptance, red first, on broken input** (so the fix is not a green stamp): with an id present only in the ledger, only on an
  unpushed local commit, and only in an uncommitted worktree edit, the picker refuses each in turn; with the ledger check removed,
  each is accepted and the test fails; a bare number such as `0.99972` does not refuse an id.
- **The backlog item is to point at this finding instead of duplicating it** (the maintainer's 17:09:40 BST entry); the slice's row (PR #982) still says "not an FD unless it recurs" and has not yet been changed.

**Event that next confirms or discharges it:** WK-1178 lands the ledger and the refusing picker, red first as above.

Ownership shape: workstream

## Decision

The decision is the lead's and the maintainer's, recorded in this finding's row of `docs/findings/register.md`, not here (a frozen essay goes stale).
