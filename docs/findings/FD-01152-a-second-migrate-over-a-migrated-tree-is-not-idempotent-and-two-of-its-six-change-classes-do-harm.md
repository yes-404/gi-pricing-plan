---
id: FD-1152
family: finding
title: A second migrate over a migrated tree is not idempotent, and two of its six change classes do harm
status: active
created: 2026-09-27
owner: auditor
tree: 47065da50c34f0bf613f7dd972675c96d12f78ed
corrected_by: []
relates: [FD-1066, PL-1144, LG-1148, FD-1149]
---

# FD-1152 — A second migrate over a migrated tree is not idempotent, and two of its six change classes do harm

Filed by the auditor at 2026-09-27 14:24:50 BST, as part of the first commit of PL-1144's docs PR. This
is **C4** in PL-1144 Scope A, re-typed by the deputy at 2026-09-27 13:30:35 BST. The
type is *"disproven in W37-11, fix deferred"*. It continues register finding **F107**,
whose essay is `FD-1066`. That essay records that the idempotence proof (`PL-960:909`,
*"a second `migrate` run produces zero diff"*) had not been run. This record files the
run and its result.

**Why a new record, and not an edit to FD-1066.** An `FD-` essay is frozen
(`document-ids.md` §1.2, the Finding row: *"living row + frozen essay"*). Check 34 lets a
frozen file change only in `status:`, `superseded_by:` and an append to `corrected_by:`.
Each `corrected_by:` entry must be an `RL-` or `RFC-` that names the file in its own
`corrects:`. An `FD-` cannot correct an `FD-`. The result is a new fact about the
property, with its own evidence, so it is a new finding. F107's register row is the
living half, and it is amended in place to point here. `FD-1066` stays `active`, because
the property it concerns is still not delivered.

## Finding

A second `scripts/doc-id.py migrate` over a tree that is already migrated does **not**
produce zero diff. At `03f61d83` it changed 17 files, with 57 insertions and 51
deletions. The changes fall into six classes. Two of them damage the corpus, and they
are the reason this is more than a cosmetic re-sort. The deputy's severity note,
verbatim from the ruling of 2026-09-27 13:30:35 BST (LG-1148 Task 5 quotes the same
text):

> classes 3 and 4 make a second `migrate` over a migrated tree actively harmful (a
> legacy-spec constant rewritten, PowerShell `::` split), and the harm is latent because
> nothing in standing CI re-runs migrate on the live tree (`--verify` migrates the pinned
> pre-migration base into a snapshot). A reader of the register must not be able to take
> "idempotence disproven" for a cosmetic re-sort.

**The six change classes**, each described with one example. The examples are from
LG-1148 Task 5's word diff. A legacy form is described here and not spelled.

1. **Padded ids are unpadded in prose and code.** In `.github/ISSUE_TEMPLATE/bug.yml`, a
   five-digit, zero-led finding id becomes its unpadded form. In
   `.github/workflows/docs.yml`, a padded plan-id citation does the same.
2. **Plain citations are wrapped into links.** `docs/findings/register.md` gains four link
   wraps of a closure-record citation (`CR-1063`), and `docs/roadmap.md` gains one of
   `CR-1065`.
3. **A legacy-form spec constant is rewritten (harmful).** In `scripts/_docverify.py`, a
   string constant that names the RFC's original note under the retired notes directory
   is rewritten to point under `rfcs/`. The constant must keep its legacy form: it is the
   spec the verification reads (`doc-id-migration-run`, "Legacy-form-spec constants").
4. **Code is corrupted (harmful).** Beneath the vendored `planning-with-files` manifest,
   PowerShell's two-colon static-member operator is split into a colon, a space and a
   colon. In `check-complete.ps1`, `[Console]::Out.Write(` becomes
   `[Console]: :Out.Write(`. In `set-active-plan.ps1`, `[System.IO.File]::WriteAllText(`
   becomes `[System.IO.File]: :WriteAllText(`. Both scripts break. This is the same
   mechanism as FD-1149, recurring.
5. **`delivery-process.core.json`'s `meta.verified_against_tree` is overwritten,** from
   `0651c1e…` to `75779691…`, the snapshot's own commit. This one is inherent: a real run
   records its run ref by design (`PL-960`), so any second run changes it.
6. **`docs/REDIRECTS.csv` is regenerated.** Rows are re-sorted, and one row is added: the
   redirect for the file-census CSV from the retired audit directory to `docs/research/`.
   The row that the code PR's Task 3 added is kept and only moved.

## Evidence

**Method**, verbatim from LG-1148 Task 5 (*"plan Task 5 steps 1–2, verbatim in
effect"*):

> - `git archive 03f61d83437a9dd4138b7e7309b22c96148f3680 | tar -x -C <job dir>/t5-snap`.
>   That commit is this branch's head after Task 4, and its tree is already migrated.
> - Inside the snapshot: `git init -q -b snapshot`, `git add -A`, and one commit. The
>   snapshot holds 1709 files, `status --porcelain` read `0`, there is no `.venv`, and it
>   lies outside every worktree.
> - Then, with the branch's own tool and the `dev-commands` thread caps:
>   `python3 scripts/doc-id.py migrate --repo-root <job dir>/t5-snap`. It ran 13:28:26 →
>   13:28:32 BST, exited `rc 0`, printed `doc-id.py migrate: 0 id(s) assigned`, and wrote
>   17 files.

In the deputy's words, the method is *"archive → snapshot repo → one commit → migrate →
status"*.

**Reading.** `git -C <snapshot> status --porcelain | wc -l` gave **`17`**, not the
expected `0`. `git diff --stat` gave **17 files changed, 57 insertions(+), 51
deletions(-)** (LG-1148 Task 5).

**Trees and tool.** The auditor resolved each value at filing:

- The tree read is the commit `03f61d83437a9dd4138b7e7309b22c96148f3680`, with tree
  `9e42c114035869b9df747a9a3e3a680638fa92bb`. It is a pre-squash commit of #821,
  reachable via `refs/pull/821/head` (`git merge-base --is-ancestor` exit 0).
- The tool is that commit's own. `scripts/doc-id.py` is blob `c5a6b309e2a7…`,
  `scripts/_docid.py` is blob `1b92b515ad70…`, and `scripts/_docverify.py` is blob
  `7ad2a215f33c…`.
- The snapshot's own commit is `75779691…` (class 5).

**Local evidence, not governed and not in the repository:**
`~/gi-pricing-plan.local/handover/w37-11-t5-second-migrate-03f61d8/`. It holds
`t5-status.log` (17 lines), `t5-diffstat.log`, `t5-diff.patch` (476 lines) and
`t5-migrate.log` (423 lines). The auditor read the line counts and the diffstat's last
line at filing. The last line is `17 files changed, 57 insertions(+), 51 deletions(-)`,
which agrees with the ledger. These files are handover material and may not survive.
The governed record of the reading is LG-1148 Task 5.

## Consequence, and the guard that contains it

Before #821, the only protection against classes 3 and 4 on the live tree was that
nobody re-ran `migrate`. The deputy's condition 3 named the recommended fix as *"the
guard, not the four mechanisms"*. That fix is **landed in #821 (squash `47065da5`)**
(LG-1148, *"The migrate guard — C4's recommended fix, adopted by the lead"*):

- `_docid.is_migrated_tree(root)` is true when `docs/INDEX.md` and `docs/REDIRECTS.csv`
  are both present.
- `doc-id.py`'s `_cmd_migrate` checks it in the non-verify branch, before `migrate()`, and
  refuses with **exit 2** and a named reason.
- `tests/test_doc_id_migrate.py::test_cli_migrate_refuses_an_already_migrated_tree` is the
  broken-input test. It failed with `assert 0 == 2` before the guard, and again with the
  guard disabled (proof 7).
- On the real Task 5 snapshot, the guarded CLI printed the refusal, exited `rc=2`, and
  left `status --porcelain` at 17 lines.

The guard **prevents the harm and does not make `migrate` idempotent.** A second run is
now refused, not proven harmless. `--verify` is not affected, because it migrates the
pinned pre-migration base, where the predicate is false.

## Disposition

**Deferred with an owner — the lead.** This is the deputy's re-typing by delegation at
2026-09-27 13:30:35 BST: *"C4 re-typed by delegation: (i). Exit `status --porcelain` 0
is NOT MET at `03f61d83` (17 files, +57/−51); the §13 verdict is **deferred with an
owner** — the lead — event: the create-read-retire audit's first slice."* In one line,
C4 reads: **disproven; its harm is guarded in PL-1144's slice by #821 (squash
`47065da5`); true idempotence is deferred with the lead.** The event is the
create-read-retire audit's first slice. The deputy's condition 4 requires that the D7
line name C4 among the items the Work closes over, with this owner and event.

## Amended 2026-09-27 (the W37-11 slice close, `LG-1148`) — the starting figure `CR-1064:414` names

This amendment adds a figure. It supersedes nothing above. The auditor makes it in place,
dated, under `docs/findings/README.md` (*"An essay file is write-once, amended in place"*).
It discharges pass (a) finding F-5 of #822, as the lead ruled at 2026-09-27 15:35:39 BST.

`PL-1144` Acceptance Standard item 4 requires the C4 record to give the starting figure
*"verbatim from `CR-1064:414`"*. Neither this essay nor `CR-1164` gives it. The starting
figure in `CR-1064:414`'s Evidence cell reads, verbatim:

> `REGRESSION (residue exceeds W37-11 ceiling): 'scripts/doc-id.py' (d10) — 41 hit(s) exceeds the W37-11 record's ceiling of 15 for 'd10'`

The same cell names the local CI log it came from, by file and line. That citation is left
at `CR-1064:414` and is not repeated here. The log's name carries a head SHA of the
migration PR that its later force-push left reachable from no ref, and repeating it would
add an unreachable token to this essay.

**What the figure measures.** It is a residue count: 41 hits of class `d10` in
`scripts/doc-id.py`, against the ceiling of 15 that the W37-11 record held. It was read from
a CI docs log of the migration PR. The Finding above measures something else: the diff of a
second `migrate` over a migrated snapshot, which touched 17 files with 57 insertions and 51
deletions at `03f61d83`. The two figures are not the same quantity. So the starting figure
is recorded here as the one `CR-1064` named, and it is not a baseline for the 17-file
reading.
