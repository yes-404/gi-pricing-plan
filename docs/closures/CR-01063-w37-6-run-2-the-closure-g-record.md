---
id: CR-1063
family: closure
kind: work
title: Work-item record — W37-6 run 2 (the closure/(g) record)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-17
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
---

# Work-item record — W37-6 run 2 (the closure/(g) record)

## Scope

Drafted by the executor under the lead's delegation (`~/gi-pricing-plan.local/channel/to-lead.md`
2026-09-17 21:04:32 BST, after-merge item 5: "closure/(g) record PR drafted (draft) for my
review"), opened as a **draft** pull request for the deputy's review per that same instruction.
**Not a close** — `CLAUDE.md` §13 closes a Slice on a clean audit and the lead's merge, and this
record is the evidence-and-incident write-up the lead asked for, not the merge itself. Every
number below is pasted from a command run in this worktree, from `git log -1 --format=%B
71f5a2208c7a92bad486ae128775a4a42c7ebc63` (the squash commit's own message), or from a named
`handover/` log or `channel/` entry — never retyped from memory. Where no source could be found,
the item says "not found: …" rather than supplying a number.

**Measurement tree: `71f5a2208c7a92bad486ae128775a4a42c7ebc63`** (`main` after PR #782's
squash-merge; sole parent `0651c1e265648cbd3918adfc729ad965b83b1e0b`, committer date
`2026-09-17T21:03:42+01:00`, `git log -1 --format=%cI 71f5a22`).

## Evidence

### 1. The 13:43:54Z incident, with attribution

**Writer.** The squash commit's own reproduction section (`git log -1 --format=%B 71f5a22`)
names it: *"the previous lead's T′ run (session `3c99cadf`, `13:43:28Z`, `153ed40`'s tool over
`w37-6-fbb5555-unmigrated`, which then carried a synced `.venv/`)"*. The deputy's channel entry
(`to-deputy.md:10632`) states the attribution was closed the same way: *"Writer attribution
closed for the closure record (previous lead's T′, 13:43:28Z, from its own log)."* The tool
worktree at that session's launch was `w37-6-final-m1` (`to-deputy.md:9807`: *"Tool worktree at
launch: `w37-6-final-m1` HEAD `153ed40`"*), and its target was the unmigrated worktree
`w37-6-fbb5555-unmigrated` — the same two paths the task brief's command form names
(`python3 …/w37-6-final-m1/scripts/doc-id.py migrate --repo-root …/w37-6-fbb5555-unmigrated`);
no single logged command line combining both paths at that exact timestamp was found in the
channel transcripts searched, so the command form is reconstructed from these two independently
verified facts (tool location + repo-root target) rather than quoted from one command line —
disclosed rather than presented as a direct quotation.

**The log.** `~/.claude/jobs/137a6dcd/tmp/migrate-T-prime.log` lines 432–434, read directly:

```
wrote .venv/lib/python3.12/site-packages/certifi/cacert.pem
wrote .venv/lib/python3.12/site-packages/hypothesis/internal/conjecture/data.py
wrote .venv/lib/python3.12/site-packages/hypothesis/strategies/_internal/numbers.py
```

**The corruption**, from the deputy's ruling (`to-lead.md:5116`, `to-deputy.md:10611`): *"cause:
certifi 2026.7.22 `cacert.pem` block 12 (Buypass Class 2 Root CA) line 410 `…/ehb8t/WK-658+xUbP…`
where pristine reads `…/ehb8t/W2+xUbP…` — the migration's `W2` → `WK-658` token rewrite; one inode
(410131, 40 hardlinks: uv cache + 14 worktree venvs) written in place at 2026-09-17 13:43:54Z.
Blast radius 3 files (certifi cacert.pem; hypothesis `data.py` and `numbers.py`, whose only
change is the migration's `notes/` → `rfcs/` rewrite inside a URL)."*

**Commit identity.** Commit 1's tree is `6d058ba642481404815ab573e848a8cf34e671ee`; commit 2's
tree is `390ff37358efdc2071eeae6ce8b114141eb7c9be`. The squash commit's own tree equals commit
2's: `git rev-parse 71f5a22^{tree}` → `390ff37358efdc2071eeae6ce8b114141eb7c9be` (verified
directly in this worktree).

**The token classes**, both from the squash commit's message and confirmed directly against a
pristine `hypothesis` wheel install (`/tmp/gi-pricing-plan-clone-fbb5555/.venv/lib/python3.12/
site-packages/hypothesis/strategies/_internal/numbers.py`, `grep -n fastmath`, lines 181, 353,
372, 380 all read `https://simonbyrne.github.io/notes/fastmath/`): (1) the `W2` → `WK-658`
token rewrite inside `certifi/cacert.pem`; (2) the migration's directory-move rewrite of the
same docstring URL inside `hypothesis/internal/conjecture/data.py` and
`hypothesis/strategies/_internal/numbers.py` — `https://simonbyrne.github.io/notes/fastmath/`
→ `https://simonbyrne.github.io/rfcs/fastmath/` (`notes/` → `rfcs/`, the migration's own
directory rename applied to a third-party library's docstring text by the same writer).

**Inode identity**, from `handover/team2-venv-restore-1789672411.log` (read directly):

```
== certifi/cacert.pem
  before: 1d46bbcdcb06ff0de3f53fdfd8bb80379213ea1b32735ce32f965a60ff049c2b inode=410131 links=40
  pristine: 9cc2a774b5198dcff14d9be1e66091f538975d867ce029a96bce15a55dfd730f
  after:  9cc2a774b5198dcff14d9be1e66091f538975d867ce029a96bce15a55dfd730f inode=410131 links=40 equal-to-pristine: yes
```
(the two hypothesis files carry the same "equal-to-pristine: yes" line for inodes 788763/789268,
39 links each — a smaller hardlink fan-out than the certifi inode, both restored the same way.)

**Symptom**, from the squash commit's own text: *"Found by the gate on 323b523: 12 of 13 steps
exit 0; pytest `1 failed, 3433 passed, 3 skipped, 1 xfailed`, collected 3438 == ran 3438; the one:
`backend/tests/test_blobs.py::test_presigned_single_part_upload_is_usable —
ssl.SSLError: [X509] PEM lib (_ssl.c:4106)`, raised in `httpx/_config.py:40` while
`httpx.AsyncClient()` builds its SSL context from certifi's bundle. Environmental, proven both
ways: identical on M's own checkout in a fresh venv (`1 failed in 2.35s`), CI python green on the
same SHA."*

**Restore**, from `team2-venv-restore-1789672411.log`'s own summary line: *"single test in
`w37-6-M-unmigrated` (0651c1e) at 19:13:31Z: 1 passed, 1 warning in 1.17s"* and *"single test in
`w37-6-run2-fold` (323b523) at 19:13:37Z: 1 passed, 1 warning in 1.19s."*

**Fix in #782**, from the squash commit's message ("Sweep enumeration" section): the sweep had
enumerated `root.rglob("*")` minus `.git` and `sweep_exclusion_reason` — a filesystem walk that
reads a checkout's synced `.venv` — feeding `migrate()`, `_rewrite_citations`,
`_normalize_padded_citations`, `_repoint_all_relative_links`, `_read_tree_text`. Fixed by
`_enumerate_tree(root)`: a `git rev-parse --is-inside-work-tree` probe; inside a work tree,
`git ls-files -z --cached --others --exclude-standard` (the same predicate
`_docverify._LS_FILES_ARGS` already uses); the `rglob` walk kept only outside one. **Two proofs**,
named in the commit message, module `297 → 299` (`299 passed in 74.10s`):
`test_sweep_never_reaches_a_gitignored_path` (a planted `.venv/lib/site-packages/vendored.md`
citing a real migrate token — byte-identical after migrate, no `.venv/` entry in
`files_written`) and `test_sweep_still_reaches_an_untracked_unignored_path` (the positive
control — a `stray/untracked.md` with the same token, rewritten, present in `files_written`).

**Standing-rule proofs.** T⁵ — a second real run of the fixed tool on a pristine `--detach`
worktree at `M` (no venv present) — from `handover/t5-4faf31d-1789672943.log` (read directly):

```
T5 START 2026-09-17T19:22:24Z tool=4faf31d root=/home/puzhenhao1989/.claude/worktrees/w37-6-repro-t5
…
doc-id.py migrate: 1133 id(s) assigned
MIGRATE_EXIT=0
T5_TREE=6d058ba642481404815ab573e848a8cf34e671ee
T5 == 6d058ba6 EXPECTED: YES
T5 END 2026-09-17T19:29:55Z
T5_EXIT=0
```

`6d058ba642481404815ab573e848a8cf34e671ee` is commit 1's own tree (branch SHA `0c41a0b`), so T⁵
reproduces commit 1 exactly on a second, independent run. **Verify at M**, from
`handover/verify5-4faf31d-1789672947.log` (read directly):

```
summary: 15 DISCLOSE, 1 FAIL, 8 PASS over 24 row(s)
FAIL: (g)
UNCHANGED: 1 fatal row(s), matching the recorded set of 1 in `_docverify.EXPECTED_VERDICTS` — the standing red, and this change moved no row.
INNER_EXIT=1
VERIFY2 END 2026-09-17T19:41:48Z
VERIFY2_EXIT=0 (inner=1; summary: 15 DISCLOSE, 1 FAIL, 8 PASS over 24 row(s); REGRESSION lines: 0)
```

### 2. The docs-CI exit-3 incident on 323b523, and its fix

**Incident.** Run `35261236904` on head `323b523` exited 3 at `doc-id migrate --verify`. On a
pull request the step's `--ref HEAD` resolved to GitHub's merge ref (`2ee3cdd`, "Merge 323b523…
into 0651c1e…") — the **already-migrated** tree — so the instrument migrated a migrated tree.
Pasted from the squash commit's message:

```
SET CHANGE (9): 9 fatal row(s) against a recorded 1. This change MOVED A ROW; the standing red is not the whole story.
  REGRESSION (newly failing): (a) PASS -> FAIL
  REGRESSION (newly failing): (d1) PASS -> FAIL
  RECLASSIFIED: (d4) DISCLOSE -> FAIL
  REGRESSION (newly failing): (d5) PASS -> FAIL
  RECLASSIFIED: (d8) DISCLOSE -> FAIL
  RECLASSIFIED: (d9) DISCLOSE -> FAIL
  RECLASSIFIED: (d10) DISCLOSE -> FAIL
  REGRESSION (newly failing): (f) PASS -> FAIL
  PROGRESS (newly passing): (h1) DISCLOSE -> PASS
summary: 10 DISCLOSE, 9 FAIL, 5 PASS over 24 row(s)
FAIL: (a), (d1), (d4), (d5), (d8), (d9), (d10), (f), (g)
```

Nothing about the real corpus had changed — the local verify at M from the un-migrated worktree
(the run the record defines) read `15/1/8, FAIL (g), REGRESSION 0` throughout.

**Fix** (deputy ruling, option (i), `.github/workflows/docs.yml`): the step now resolves its own
ref — on a migrated checkout (`audit-docs.py`'s `migrated_tree()` sentinel: `docs/INDEX.md` and
`docs/REDIRECTS.csv` both present) `--ref` becomes `docs/process/delivery-process.core.json`'s
`meta.verified_against_tree`, the pre-migration base the tool itself recorded from the run;
otherwise `--ref HEAD` unchanged. `RL-1045` §1's exit-1 reading is unchanged; the step echoes
which branch it took.

**Local CI-form proof before the push**, `handover/verify-ci-form-323b523-1789671513.log` (read
directly, migrated checkout, workdir outside any git tree, base read from the file):

```
VERIFYCI START 2026-09-17T18:58:33Z fold=323b523 status=0
migrated sentinel present: INDEX.md yes, REDIRECTS.csv yes; BASE (meta.verified_against_tree) = 0651c1e265648cbd3918adfc729ad965b83b1e0b
…
summary: 15 DISCLOSE, 1 FAIL, 8 PASS over 24 row(s)
FAIL: (g)
UNCHANGED: 1 fatal row(s), matching the recorded set of 1 in `_docverify.EXPECTED_VERDICTS` — the standing red, and this change moved no row.
INNER_EXIT=1
VERIFYCI END 2026-09-17T19:16:51Z
VERIFYCI_EXIT=0 (inner=1; summary: 15 DISCLOSE, 1 FAIL, 8 PASS over 24 row(s); REGRESSION lines: 0)
```

**CI proof, two trees.** Pre-merge, on `f777159` (the PR branch head that became the squash),
the lead's own channel entry (`to-lead.md:5154`) names all four workflows by run id: *"CI on
f777159 by head SHA: history-policy 35266452693, frontend 35266452586, python 35266452782,
docs 35266452720 — all `completed/success`; the docs run's verify stage resolved `migrated
checkout … --ref 0651c1e…`, printed `summary: 15 DISCLOSE, 1 FAIL, 8 PASS` / `FAIL: (g)`, stage
table 4/4 pass."*

Post-merge, on `main` at `71f5a22` itself — verified directly in this worktree, `gh run list
--branch main --limit 8 --json databaseId,name,status,conclusion,headSha,createdAt`:

```
history-policy  35268549712  completed  success  71f5a2208c7a92bad486ae128775a4a42c7ebc63  2026-09-17T20:03:46Z
frontend        35268549550  completed  success  71f5a2208c7a92bad486ae128775a4a42c7ebc63  2026-09-17T20:03:46Z
python          35268549539  completed  success  71f5a2208c7a92bad486ae128775a4a42c7ebc63  2026-09-17T20:03:46Z
docs            35268549620  completed  success  71f5a2208c7a92bad486ae128775a4a42c7ebc63  2026-09-17T20:03:46Z
```

All four `completed/success` on the measurement tree itself (`71f5a22`, not `f777159`), created
`2026-09-17T20:03:46Z` — 17 seconds after the merge commit's own committer date
`2026-09-17T21:03:42+01:00` (`20:03:42Z`). The docs run's verify stage resolves the same way as
on `f777159` (migrated checkout, `--ref` := `core.json`'s `meta.verified_against_tree` =
`0651c1e`), so `15/1/8, FAIL (g), REGRESSION 0` is the standing CI reading on `main` itself, not
only on the branch that became it.

### 3. The three W37-11 census per-file rows' shrink to 0 — proposed record change, not applied here

The W37-11 record's three per-file rows carry the key

```
docs/audit/file-census-5ef559d.csv
```

— the row key as read at the control tree `0651c1e`, not a live path: the file itself now lives
under `docs/research/file-census-5ef559d.csv` per RFC-937 §5.2, `docs/REDIRECTS.csv`'s own row
(grepped directly):

```
,,docs/audit/file-census-5ef559d.csv,docs/research/file-census-5ef559d.csv,,
```

and the record's key has not been re-derived to match. Those rows carried ceilings of **h1-check36
17, d9 14, d10 2** before this run. Measured 0 for all three, from
`handover/verify2-e30a082-1789664602.log` (the 18:03:25 → 18:21:12 BST run) and
`handover/verify3-2307087-1789666744.log` (the 18:39:07 → 18:57:10 BST run), both read directly
(the record's own key, unchanged, is what the tool prints):

```
PROGRESSED (W37-11 record can shrink): 'docs/audit/file-census-5ef559d.csv' (h1-check36) — ceiling 17 now measures 0
PROGRESSED (W37-11 record can shrink): 'docs/audit/file-census-5ef559d.csv' (d9) — ceiling 14 now measures 0
PROGRESSED (W37-11 record can shrink): 'docs/audit/file-census-5ef559d.csv' (d10) — ceiling 2 now measures 0
```

The 18:57 run's log carries the identical three lines, confirmed by the deputy's own
`to-deputy.md` entry at that timestamp, quoted verbatim as an exhibit (the same record key,
unchanged by the migration):

```
PROGRESSED x3: docs/audit/file-census-5ef559d.csv h1-check36 17 -> 0 . d9 14 -> 0 . d10 2 -> 0 ... Identical to the 18:21 run.
```

**Reason**, quoted from `git show 0846ad6` (commit `0846ad6af93959696db68cf5356dae8b619fcedf`,
reachable at `origin/w37-6-h1-check36`, not on `main` — its content is carried here rather than
merged, per the deputy's 18:59:00 BST ruling below):

> "retired 2026-09-17: the file is a GOVERNANCE_RECORD_EXCLUSIONS member (class F loop 2), so
> its hits now key to the sentinel row by `_h1_residue_by_file`'s construction; measured 0 in
> handover/verify2-e30a082-1789664602.log (PROGRESSED lines)"

**Mechanism**, from the deputy's ruling (`to-deputy.md:10411`, amended 18:29:10 BST):
`_docverify.tracked_files` (`:428`) is `git ls-files` minus every `sweep_exclusion_reason` hit by
design, and `_h1_residue_by_file` (`:3048`) keys a hit to its file only if the path is in that
set, else the sentinel — so once the census file became a `GOVERNANCE_RECORD_EXCLUSIONS` member
(class F loop 2, the migration's own carve-out for a commit-bound governance record), its hits
key to the sentinel row instead of the per-file row: sentinel `904 → 1088` (+184), per-file rows
`17 → 0`, `14 → 0`, `2 → 0` (17 + 14 + 2 = 33; the remaining 151 of the 184 come from other
sweep-excluded files already pooling to the sentinel, not from these three rows alone).

**Why proposed, not applied.** The verify inside the migration PR reads the W37-11 record from
the **control** ref (`scripts/_docverify.py:4333`, `load_w37_11_record(snap.control)`), never the
live branch — so a record edit made *inside* the PR branch can never be seen by that PR's own
verify (`to-deputy.md:10469`, `to-lead.md:5066`). The reason-cell commit (`0846ad6`, following
`baad1f9`) was built and accepted in substance (`to-lead.md:5047`, 18:41:59 BST ACCEPTED) but
then **dropped from commit 2** at the deputy's 18:59:00 BST ruling (`to-deputy.md:10469`): *"a
docs-only record PR from `fbb5555` with ONLY the sentinel h1-check36 row 904 → 1088 + the
18:29:10 reason — the three census rows STAY 17/14/2 (this PR's own verify runs main's tool,
which still rewrites the census; zeroing them would regress it; they PROGRESS to 0 after the
migration and are shrunk in the closure record)."* That is this section: the sentinel transfer
(`904 → 1088`) landed inside commit 2 itself (see §4 below, row `h1-check36`'s per-file bucket),
and the three per-file rows' actual zeroing is left for a follow-up record edit against `main`,
proposed here with its measurement and reason rather than applied in this PR.

**The pinned-base consequence, disclosed.** On `main`, `.github/workflows/docs.yml:117` resolves
`--ref` to `docs/process/delivery-process.core.json`'s `meta.verified_against_tree` (read
directly, `core.json:7`: `"verified_against_tree": "0651c1e265648cbd3918adfc729ad965b83b1e0b"`),
and `scripts/_docverify.py:4333` loads the W37-11 record from `snap.control` — the snapshot built
at that same pinned ref, not the live checkout. So the standing CI verify reads the W37-11 record
**at the pinned base, forever**: any record edit landed on `main` after tonight — the three census
rows' zeroing proposed in this section, or any future shrink — is invisible to it, and the
`PROGRESSED` lines above will print on every CI run until W37-11 decides where the standing
check reads the record from post-migration (the control tree, for the run's own hermeticity, versus
the live tree, for a standing check that should see later record edits). **Owner: lead, W37-11.**
This record's "proposed, not applied" reading above is unaffected by this: an applied edit would
have been unobservable to CI anyway, for exactly this reason.

### 4. The squash commit's own "Disclosed to W37-11" section, quoted in full

From `git log -1 --format=%B 71f5a2208c7a92bad486ae128775a4a42c7ebc63`:

> ## Disclosed to W37-11 (not fixed here)
> - `_discover_ruling_headings` globs only docs/plans/ — 3 of 114 RL- headings measured
>   (executor B, class D).
> - check 35: two sub-clauses both fire on one non-markdown file after F87's widening —
>   output-shape question, owner lead.
> - F88: three vendored SKILL.md raise HeaderError and are invisible to check_owner
>   (pre-existing).
> - `_docverify._h1_residue_by_file` docstring says "the unfiltered tracked-file set" while
>   `tracked_files` is filtered by `sweep_exclusion_reason` (by design): per-file attribution
>   for sweep-excluded files (generated contracts, governance records) is a design item —
>   owner lead (deputy ruling 18:29:10 BST).

**The `(d → W37-11)` attribution item and the `_h1_residue_by_file` docstring/implementation
item are the same item, not two**: the deputy's ruling (`to-deputy.md:10411`) names it
`(d → W37-11)`, and the lead's own channel gloss (`to-lead.md:5028`) spells out why: *"(d →
W37-11): `_h1_residue_by_file`'s docstring claims 'the unfiltered tracked-file set' while
`tracked_files` is filtered — a docstring/implementation mismatch; per-file attribution for
sweep-excluded files (generated contracts, governance records) is a design item, owner lead, in
the commit-2 disclosures."* Verified directly against source in this worktree:
`_h1_residue_by_file`'s docstring (`scripts/_docverify.py:3054-3056`) reads *"the unfiltered
tracked-file set of the migrated snapshot"*, while `tracked_files`'s own docstring
(`scripts/_docverify.py:428-430`) reads *"`_LS_FILES_ARGS`'s population, minus every
`_docid.sweep_exclusion_reason` hit"* — the two disagree exactly as the disclosure states.

The check-35 two-clause item and the F88 HeaderError gap are each exactly the bullet quoted
above; no fuller description than the quoted sentence was found in the squash commit's message
or in the channel entries searched.

### 5. PL-960:909 idempotence item, with tonight's numbers

**The obligation**, `docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md:909` (read
directly; cited here as `PL-960:909`, unpadded — RFC-937 §1.1 rule 2, padding belongs only
inside a link target's filename): *"- [ ] Prove idempotence on the real tree: a second
`migrate` run produces zero diff."*

**Tonight's proof of determinism** (a second real run from the same starting point produces the
identical tree, not a re-run over already-migrated input): the squash commit's message names
T⁗ — *"this commit's own `scripts/doc-id.py migrate` run on a pristine worktree at M yields tree
`6d058ba642481404815ab573e848a8cf34e671ee` (T⁗; both the lead's and the deputy's write-trees
agreed before commit 1 was cut)"* — and T⁵, this record's §1 above, on the same pristine base
after the sweep-enumeration fix: `T5_TREE=6d058ba642481404815ab573e848a8cf34e671ee`. **T⁗ and T⁵
are the identical tree id** (`6d058ba6…`), two independent runs of the tool against `main` at
`M=0651c1e` agreeing byte-for-byte.

**What a second run over already-migrated input looks like** — the shape idempotence in the
literal §909 sense would need to rule out — is §2's docs-CI exit-3 incident: running
`migrate --verify` with `--ref HEAD` against a migrated checkout (a pull-request merge ref that
is already the migrated tree) produced the `SET CHANGE (9)` block quoted in full in §2, including
`PROGRESS (newly passing): (h1) DISCLOSE -> PASS` alongside eight new or reclassified `FAIL`
rows. That run is not evidence of non-idempotence in `migrate()` itself — it is a `--ref`
resolution defect (fixed in §2) that fed the verify instrument the wrong control tree — but it is
the only observation tonight of what happens when the tool's verify machinery is pointed at
migrated input a second time, and PL-960:909's literal "second `migrate` run … zero diff"
proof (running `migrate` itself, not `migrate --verify`, a second time over the migrated tree and
asserting an empty diff) was not separately run tonight. **Carried to W37-11** as the squash
commit's own line states: *"The idempotence item PL-960:909 carries to W37-11 with this
incident's numbers."* (the squash commit's own text pads the number; unpadded here per RFC-937
§1.1 rule 2 — the number, not the wording, is what carries.)

**The measured figure W37-11 starts from.** From the exit-3 incident's own CI run (`35261236904`,
step `doc-id migrate --verify`, on head `323b523`), `handover/team2-ci-docs-323b523.log` line
1239, timestamp `2026-09-17T18:52:07.2709322Z` (read directly):

```
REGRESSION (residue exceeds W37-11 ceiling): 'scripts/doc-id.py' (d10) — 41 hit(s) exceeds the W37-11 record's ceiling of 15 for 'd10'
```

The 41 are commit 2's own restored, `# rfc-937: legacy-form-spec`-marked literals (§ "The tool's
own self-migrated literals" in §7 below) counted as residue when the tool is applied to its own
output — that same defective `--ref HEAD` run migrating an already-migrated tree. This is
tonight's measured shape of the real-corpus idempotence gap the channel tracks under a
finding/finding-document pair — not a filed governed document; the second half does not resolve
in `docs/INDEX.md`, so the pair is quoted here as an exhibit rather than as a live citation
(`to-lead.md:4460`, `:5106`, `:5198`):

```
the F28/FD-1069 idempotence gap stays W37-11's
```

The figure above is what W37-11's own idempotence work starts from.

### 6. The (g) second half — what still fails, and why it stays the standing red

`scripts/_docverify.py:3788` — `EXPECTED_VERDICTS`: `"g": FAIL, # the token-boundary defect —
RL-1043 §2 row 1`. Row (g) has two components, g1 and g2 (`_docverify.py`'s own row-`g`
predicate text, read directly):

- **g1** — the token-boundary/provenance/bare-comma sub-checks. **All three read 0 tonight**,
  from `handover/verify5-4faf31d-1789672947.log`'s own `[FAIL] (g)` row (read directly):
  `migrated     g1 WK-shape mangled = 0 in 0 file(s), provenance mismatch(es) = 0,
  bare-comma-after-rewrite violation(s) = 0`. This is §1's incident's own standing-rule proof:
  g1 is clean.
- **g2** — the closed six-class classifier (`doc-id.classify_migration_diff`); everything it
  cannot place into classes 1–6 is `classified-by-none`. From the same log: `g2
  1-front-matter-stamp=0, 2-reference-token=589, 3-move=96, 4-split=1, 5-roadmap-restructure=1,
  6-generated-artifact=33, classified-by-none=251`, against a denominator of *"971 file(s)
  classified (485 unchanged, not a hunk); 412 compound citation(s) at risk in 164 file(s)."*
  The row's `note` breaks the 251 down by cause:

  | Cause | Count |
  |---|---:|
  | cause3-legacy-path-citation | 136 |
  | slash-compound-citation (unassigned — reported, not investigated) | 34 |
  | unmapped-work-slice-key (named elsewhere, reported here by shape) | 28 |
  | cause2a-range-citation | 16 |
  | other | 13 |
  | cause1-foreign-frontmatter | 11 |
  | new-frontmatter-stamp-no-move (unassigned — reported, not investigated) | 7 |
  | cause4-compound-token-adjacent-uppercase | 6 |
  | **Total** | **251** |

  (136+34+28+16+13+11+7+6 = 251, matching `classified-by-none` exactly.)

**Row (g) stays FAIL** because g2's `classified-by-none` population is 251, not 0, even though
g1 is fully clean tonight: the verdict is `FAIL` on `residue` alone
(`scripts/_docverify.py`'s row-`g` logic: `elif wk_mangled or provenance_mismatches or
bare_comma_violations or residue:` → `FAIL`), so a non-empty g2 residue fails the row regardless
of g1's state. This is `_docverify.EXPECTED_VERDICTS["g"] = FAIL` unchanged tonight —
`UNCHANGED: 1 fatal row(s)` in every verify log quoted in §§1–2 above — the same standing red
RL-1043 §2 row 1 named it as, now with g1 clean and g2's 251-file residue as the whole remaining
cause.

### 7. The disclosures list and the per-class dispositions table

**Disclosures list**: §4 above quotes the squash commit's "Disclosed to W37-11" section in full;
no further disclosure paragraph was found outside it, the docs-CI incident (§2), the census
shrink (§3), and the idempotence carry-forward (§5).

**Per-class dispositions table (classes A–G + siblings)**, from the squash commit's "Tests: the
103 CI failures on commit 1, by mechanism" section, quoted:

| Class | Disposition (quoted) |
|---|---|
| A (check-35 owner) | "F92's harness-schema agents/skills deferred by predicate `_is_stamp_deferred_w37_10` (path AND no `family:`; 50 = 46+7 − 3 vendored SKILL.md under F88's HeaderError gap; RL-1046 cited by file path); the 27 unstamped root files are the W37-11 record's own per-file rows (class h1-check35) … Loop 2 of 2." (the squash commit's own text pads the number; unpadded here per RFC-937 §1.1 rule 2) |
| B (check-28 plan acceptance standard) | "tests re-pointed to the hermetic one-plan `docs/` shape; RL-906's wording 'filename date' kept verbatim." |
| C (register-lint) | "residue class 2 by the register's own `Phase` column ('1b'; 11 defective of 20 at `0b8d200`, measured by `phase1b_residue(rows)` and cross-checked against check 29), never an id list; header cell at `_PHASE_FIELD_INDEX` must read 'Phase'. RL-910 §2 honoured by its reason. Loop 1." |
| D (ruling-acceptance census) | "heading predicate on the `RL-N —` form; the fixture's placeholder labels had collided with real RL-864/RL-865 and been rewritten correctly by the sweep. Loop 1." |
| E (doc_id_verify self-tests) | "id-pattern re-measured on the flattened form (226 members); `_NT0019_PATH` restored + marked. Loop 1." |
| F (bundled data) | "docs/REDIRECTS.csv carve-out verified structurally (manifest at its one location, every new_path exists); the file-census record is a GOVERNANCE_RECORD_EXCLUSIONS predicate entry at both locations (content never rewritten; the §5.2 move stands). Loop 2 of 2." |
| G singletons | "notes-path sweep exempts `_legacy_form_spec_spans` by predicate (two prose mentions reworded, no marker on prose); findings-heading check re-pointed to the FD- family with the non-vacuity assert kept (39 files); `_ROADMAP_WORK_ROW_RE` accepts canonical `WK-<n>` rows." |

Counts (quoted, same section): "103 CI failures on commit 1" (`all-103 on 0b8d200: 21 failed / 82
passed`), and the final measurement before merge: "`all-103 on 2995a1e: 103 collected, 1 failed /
102 passed — the census (class F), red until the re-cut; expected 0 after`" — i.e. every class
but F's own re-cut dependency cleared before commit 2 was finalised, and F itself cleared once
commit 1 was re-cut from T‴ (§ "Commit 1" of the squash message, `docs/research/file-census-…`
byte-identical to `fbb5555`'s audit copy).

**The tool's own self-migrated literals — the classification table**, from the squash commit's
message ("The tool's own self-migrated literals" / "Classification table (45 rows)" sections):
**45 rows**, disposed **restore (10)** — rows 10, 13, 14, 21, 34, 35, 36, 37, 38, 42, all
directly touching the register-rename bug the lead's proven-consequence section named, plus the
two `_discover_named_phase_records` targets and the `tie_break` sort key — and **prose (35)** —
"exception-reason strings never read by any comparison (only checked for non-blankness), CLI
`--help` text, stderr diagnostics, and refuse-path exception messages that never execute against
a well-formed corpus — plus two items I initially suspected might need restoring but ruled out on
inspection." The predicate for the split: "an `ast.walk` string-constant diff of `git show
fbb5555:scripts/doc-id.py` vs `git show 0de7d34:…` (1866 constants each, same AST shape,
positional pairing): 181 differ = 107 docstrings + 74 non-docstring", with the rule (from
`_legacy_form_spec_spans`'s docstring): *"a lookup literal matches the tree the instrument reads
at run time — doc-id.py the pre-migration input; audit-docs.py the migrated tree; _docverify.py
both."*

## Verdict

This record makes no close disposition — per `CLAUDE.md` §13 a Slice closes on a clean audit and
the lead's merge, neither of which this PR performs. Each item above is either (a) fully
evidenced and resolved on `main` at `71f5a22` (the 13:43:54Z incident, restored and proven by T⁵;
the docs-CI exit-3 incident, fixed and proven by CI on `f777159`; row (g)'s g1 half, clean), (b)
**deferred with an owner**, per the squash commit's own disclosures (§4, §6 — all four owned by
"lead"; F88 and the ruling-headings glob pre-existing, unowned in the quoted text), or (c)
**carried forward to W37-11 as a named item with its numbers** (the three census rows, §3; the
idempotence item, §5; #757's rebase, per the ledger entry filed alongside this record). No item
in this record is asserted "not started" or silently dropped.
