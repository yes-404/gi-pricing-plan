---
name: mint-and-finish
description: The executor procedure for a minter or finisher seat — minting a batch of working ids (FD/RL/PL/SL/OQ/LG) into one batch PR, re-minting when the lead's allocation shifts, merging origin/main into a PR at its merge turn (docs/INDEX.md regenerated, docs/findings/register.md rebuilt, docs/roadmap.md duplicate check), the post-mint sweep, the evidence an ACK request needs under lead.md rule 4 (1E, E2, the code-PR rule, the precondition) and the traps around it (cancelled CI, conflicting PRs with no CI, DB-backed modules that ERROR, gh pr edit --body-file), and the closing acts (R1/R2 sibling closes, FD closes, the slice mint's LG/SL closes under the docs-only waiver). Use when a brief headed "Brief — executor (minter|finisher)" sends you to mint, re-mint, merge main or prepare a PR for its ACK.
---

# Mint and finish

"Minter" and "finisher" are **seat names, not roles**: every seat spawns from
`.claude/roles/executor.md` and works under a task brief (the maintainer's entry
"2026-10-08 12:56:01 BST — "finisher" and "minter" are SEAT NAMES, not roles …" in
`~/gi-pricing-plan.local/channel/to-lead.md`, item 3). The brief gives the values — PR, head,
branch, worktree, the lead's id allocation. This skill gives the procedure, so a brief
points here rather than re-pasting a checklist; a brief that re-pastes one drifts (the T1
cancelled-CI slip of 2026-10-08 came from a brief).

**What this skill does not restate.** The merge rules — 1E, E2, the code-PR carry-over rule,
the subset's DB-backed modules and the precondition — are `.claude/roles/lead.md` rule 4 and
`docs/process/delivery-process.md` §8 (5a–5h), on RFC-1506 P6. Read them there; this skill
adds only the steps and the traps measured on the way (RFC-756: a restated rule goes stale).
Git mechanics are [`git-hygiene`](../git-hygiene/SKILL.md); commands and gate slots are
[`dev-commands`](../dev-commands/SKILL.md).

## 0. Before anything

- **`ls-remote` the head and STOP if it differs from the brief's.** Why: a brief's head is
  the one the lead verified; a different one means someone pushed, and every later proof
  would be about the wrong object.
- **Never `cd`** — `git -C`, absolute paths, `uv run --directory`, `/usr/bin/git -C` if the
  guard refuses. Why: a `cd` moves the working directory for you and for every agent spawned after you
  (executor.md). The retry-cap hook runs by absolute path since PL 9617, so a `cd` no longer
  locks the session; the rule stands.
- **Every check behind the slot probe that exits**, never beside someone else's held gate:
  ```bash
  mkdir -p /tmp/slots; for s in /tmp/slots/gate-1 /tmp/slots/gate-2; do flock -n -E 75 "$s" true || { echo "SLOT HELD: $s"; exit 75; }; done && <check>
  ```
  Why: a gate carries NFR timing tests; a batch of checks beside it makes spurious reds
  (the sweep-pause rule, every role file that runs commands).
- **Scratch under `mktemp -d -p /home/puzhenhao1989/.cache`**, never `/tmp`. Why: a shared
  job tmp dir has been overwritten by a peer.

## 1. Mint a batch

1. **Step 1 — enumerate and verify.** For each source PR: its head (40 chars), every working
   id it ADDS (record files, SL rows, OQ rows, requirement ids), and every citation between
   records and its direction. Compare with the brief's table; **any difference is a STOP**
   before minting. Why: the allocation is ordered on those directions.
2. **Cited before citing.** The record a later one cites gets the lower id and comes first
   (5a). Why: check 32 reds a citation of an id that does not yet resolve on the tree.
3. **The lead is the only allocator, in MERGE order.** Never take an id from
   `doc-id.py next`. Why: it reads `origin/main` and cannot see a reservation or a batch
   still in flight — three roles once read the same next id.
4. **Re-mint HIGHEST FIRST** when the lead shifts the allocation (T2 2026-10-08: every id
   +1 after SL-1448's LG took 1487). Rename the top id first, then down. Why: renaming the
   lowest first collides with the next record's current id. One commit; then `git grep -c`
   of each OLD id = 0 outside verbatim quotes, and each new id resolves once.
5. **`created:` is the mint date, the original kept in a comment**, plus a disclosure line
   under the H1. Both forms on main: FD-1478 `created: 2026-10-08  # original date
   2026-09-30, set at the draft; minted 2026-10-08` with *"Disclosure: drafted under working
   id 9888; minted as FD-1478 on 2026-10-08, in the T1 batch mint PR."*; RL-1497 *"(Minted
   2026-10-08 as RL-1497 from working id 9718, in the T8 batch mint PR; …)"*. Why: the id
   sequence must read as creation order, and the draft date must not be lost.
6. **The barred word, in the batch copy.** Count it in each source PR's added lines; write
   "the maintainer (by delegation)"; inside a verbatim channel quote elide it as
   "[the maintainer's (by delegation)]" with a bracketed note; a quoted commit subject is
   cited by sha and date with a bracketed paraphrase. After = 0 over added lines, commit
   messages and the PR body. Why: lead.md's barred-word rule binds every hunk a PR edits;
   these elisions are the one non-id change R2 tolerates, LABELLED "barred-word elision"
   (the maintainer's entry "2026-10-06 01:19:14 BST — B1 (8 PRs) noted; …").
7. **Quoted channel headers keep their working ids** — a quote is a quote. Why: a re-pointed
   quote no longer matches its source, and a reader cannot find it.
8. **Forward-cites stay space-form working ids** ("PL 9578") and are LISTED in the PR body
   (5a). Why: a hyphen form of an unminted id reds check 32, and the list is what the
   later batch re-points from.
9. **Keep a batch docs-only.** A code file citing a working id (a test comment, a
   `runtime.py` docstring) is a listed follow-up, not a re-point here. Why: one non-docs
   path voids E2/1E and the docs-only waiver, and costs a full CI wait.
10. **INDEX is regenerated** (`python3 scripts/doc-index.py`), register rows in id order.
    A draft branch commits no INDEX hunk (5d). Check 31 names a gap below your ids until the
    batches before you merge — EXPECTED; record its line verbatim.
11. **R2's normalised diffs**, per source PR: its diff vs the batch copy, normalised for id
    re-points and INDEX/register regeneration, must be EMPTY (or only labelled elisions).
    The PR body carries the table: working id → minted id, source PR, normalised-diff result
    (R1, 5a). A non-empty one is listed with its lines; that sibling stays open.
12. **A new batch PR opens as a DRAFT** with `--body-file`; later body edits by REST (§4).

## 2. Merge main at the merge turn

Merge `origin/main`, **never rebase** (5e). Why: a rebase voids every SHA a record or ledger
already cites. Read `git merge-tree --write-tree` **rc first** — a conflict exits 1 and its
first line is still a tree id.

- **`docs/INDEX.md` → REGENERATE** with `doc-index.py`, never hand-merged. Why: INDEX is
  generated; a hand merge produces an index of neither side.
- **`docs/findings/register.md` → REBUILD** from main's file plus the batch's N rows. Then
  `grep '^|' docs/findings/register.md | sort | uniq -d` is empty and the table-line count =
  main's + N. Why: a naive keep-both on a stacked register duplicated rows in T1 on
  2026-10-08 — both sides carry the shared rows, so marker-stripping keeps them twice.
- **`docs/roadmap.md` → keep both sides**, then `grep '^|' docs/roadmap.md | sort | uniq -d`
  compared with main's own output — no NEW duplicate. Why: main already carries identical
  lines (5 at `42e56bd3`, by that command), so "empty" is the wrong bar.
- **Any other conflict → STOP.** Why: it is a content conflict, the lead's to route.
- Re-run audit-docs, `doc-index.py --check`, `register-lint.py` at the merged head.
- Do **not** run `doc-id.py migrate --verify` when preparing an open PR: it is heavy, and
  CI's docs job runs it. Read CI's stage log, not only its status (a stage pass has wrapped
  a recorded nonzero exit under RL-1045 §1). `delivery-process.md` §11a's run binds whoever
  opens a PR that adds a file under `docs/`.

## 3. The sweep (lead.md rule 4)

After the mint commit, sweep each minted working id **in space form** ("FD 9888") over the
living docs, open PRs and open `draft/` branches. Re-point live hits in this PR, or list each
with its follow-up PR; frozen records stay as written. Why: the hyphen form never appears for
an unminted id, so a hyphen sweep finds nothing and reports clean.

## 4. The evidence for an ACK request

Which evidence each case needs is lead.md rule 4 (1E, E2 (a)–(d), the code-PR rule (i),
(ii'), (iii'), (iv), the precondition). The traps it does not spell out:

- **A CONFLICTING PR gets NO CI runs** — zero check-suites (#1240 @a8b63dbf, 2026-10-08).
  Merge main first; the run the ACK names is the one at the merged head. Why: `pull_request` runs are
  built on the PR's merge ref, which GitHub cannot create while the PR conflicts.
- **A push CANCELS the branch's in-flight CI** (per-branch concurrency group, `git-hygiene`
  "Pushes share a CI concurrency group"). Cancelled ≠ green. Never push while a run the ACK
  needs is in flight; merge main and run local checks first, push after it completes. Why:
  T1's python run 37766410964 was cancelled this way and the ACK waited ~22 min for a new one.
- **Push ONCE at the finish, then no pushes while its CI runs.** Why: same mechanism.
- **The DB-backed modules ERROR, not skip, without `GIP_TEST_DATABASE_URL`** —
  `_per_worktree_test_database_url` in `backend/tests/conftest_db.py` raises `RuntimeError`
  when the per-worktree DB does not exist. So where rule 4 says they are SKIPPED, exclude
  them **by path** from the pytest command; where it says they run, use a per-worktree DB
  ([`python-test`](../python-test/SKILL.md) "A green `pytest -q` with no database is a
  partial run"). Why: an unset DSN turns the subset into a wall of errors, not a skip count.
- **Read pytest totals from the job log** (`gh api repos/{owner}/{repo}/actions/runs/<id>/jobs`,
  then `…/jobs/<id>/logs`), never the step status, and list FAILED lines by name. Why: the
  python stage has passed while pytest failed.
- **`gh pr edit --body-file` silently no-ops** — PATCH via REST
  (`gh api -X PATCH repos/{owner}/{repo}/pulls/<n> -F body=@<file>`) and re-read the body
  (`git-hygiene` "`gh pr edit --body-file` silently leaves the old body in place").
- **Report** the head (40 chars), name-status of the delta, merge-tree rc + tree, each check
  with its rc, pytest rc + totals + wall time, barred-word counts (added lines, messages,
  body), and 0 `claude.ai/code` links; for a SLICE PR also the `-U0` of its `LG-` and `SL-`
  row `status: closed` lines (§5).

## 5. Closing acts

- **R1/R2 sibling closes** are the lead's, after the verified merge read-back, with the
  comment "minted in #N as <id> (squash <sha>)" (R2, the maintainer's entry
  "2026-10-06 01:18:08 BST — Backlog triage: R1 and R2 RULED"; 5c). A seat never closes a PR.
- **An FD close rides a batch**: the essay's `status:` line and its register row only —
  the frozen body is never edited. The close itself is the auditor's act (FD-1420's close
  rode B3 as commit affaee48).
- **The slice mint** (executor.md, "As the mint step …"): LG id minted; LG `status: closed`;
  the roadmap SL row `status: closed` with a dated line; notes APPENDED to the ledger, never
  an earlier entry rewritten; INDEX regenerated; audit-docs green. Under the docs-only waiver
  (the maintainer's entry "2026-10-06 02:28:42 BST — The minted-head gate …: WAIVED for a
  DOCS-ONLY mint delta, on conditions …") show (a) `git diff --name-status <gated
  head>..<mint head>` is docs/ only; (b) full green CI at the mint head, totals from the log;
  (c) the gated head's local gate with only the known check-31 set. Which FD the slice
  discharges is stated in the PR body; the FD close is the auditor's, after the merge.
- **The slice PR sets its `LG-` and its `SL-` row `closed`** (auditor.md :37–45, RFC-1506 L1
  (a')); **the ACK request shows both `-U0` lines.** Why: #1247 (SL-1472) and #1245 (SL-1477)
  merged on 2026-10-08 with both still `active`; the closes rode a later batch
  (draft/close-sl1472-sl1477), and the maintainer's ACKs check it from then on
  (to-lead.md "2026-10-08 … The missed slice closing acts …").

- **Every L1 (a') slice whose plan is still draft sets the plan's status line to active in the slice PR's FIRST commit and closes its own LG and SL at the head** (to-lead "2026-10-09 13:29:49 BST — RULINGS …" item 3).

## 6. Never

- `cd`; `git stash`; checkout outside your worktree; rebase; force-push.
- Merge, close a PR, or comment on GitHub — the seats' acts end at the push and the report.
- A full test suite; `migrate --verify` at preparation (§2).
- A background process inside a held slot — the rule and its `fuser` check are
  [`dev-commands`](../dev-commands/SKILL.md)'s. Why: it inherits the lock fd and holds the
  slot after the run (about 17 min of gate-1 on 2026-10-08).
- A `claude.ai/code` session link in a commit, PR body or comment; Co-Authored-By only.

## Verified

2026-10-10 against the PL 9617 slice branch (based on main `fe0b0627`): the `Never cd` reason clause only, after the hook moved to an absolute path. Previously 2026-10-08 against main `42e56bd3` (RFC-1506 merged, #1240). Procedure taken from that
day's executed briefs (T1 #1242, T2 #1239, T8 #1244, B3 #1246, SL-1448 #1236, #1240) and
the lead's recorded slips: the T1 register duplicate rows, the T1 cancelled python run
37766410964, #1240's zero check-suites while conflicting. The DB-module ERROR was re-read in
`backend/tests/conftest_db.py` at `42e56bd3`; the two disclosure-line forms were read in
FD-1478 and RL-1497 on main.
