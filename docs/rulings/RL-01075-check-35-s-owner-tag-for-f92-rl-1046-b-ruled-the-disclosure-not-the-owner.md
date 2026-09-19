---
id: RL-1075
family: ruling
title: check 35's owner tag for F92 — RL-1046 §B ruled the disclosure, not the owner
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-19
owner: decision-maker
tree: 7d5d6e0a3730bfd790dace3a95c63a0ea71ec031
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1070, RL-1046, CR-1064, FD-1029]
---

# RL-1075 — check 35's owner tag for F92: RL-1046 §B ruled the disclosure, not the owner

## Verified first, at 7d5d6e0a3730bfd790dace3a95c63a0ea71ec031

This rules `PL-1070`'s **DP-7-1**, the only blocking decision point holding that plan at
`status: draft` (`PL-1070-…-leaf-plan.md:51`, `:74-80`). Everything below was read at
`7d5d6e0` in worktree `agent-a7575676d7fdc9dcf`, `git status --short` empty, with
`/usr/bin/git show 7d5d6e0:<path>` and line numbers taken from `grep -n` on that ref's
content. Clock at ruling: 2026-09-19.

**The decision point as it was put** (`PL-1070-…-leaf-plan.md:330`, quoted, options
abbreviated):

> Check 35's printed owner tag for F92's deferred population. The lead ruled the owner of
> record is **W37-11** (`CR-1064:372`); the ruling the line itself cites, `RL-1046` §B, says
> **W37-10** … (a) print `owner: W37-11` and leave `RL-1046` §B cited as-is; (b) print
> `owner: W37-11 (deferred under RL-1046 §B, which named W37-10; owner of record
> reassigned)` and rename the helper to carry no slice tag — `_is_stamp_deferred_f92`;
> (c) leave `W37-10` and file the misalignment as a finding for W37-11 | **(b)**.

Six findings, each measured rather than recalled.

**1. What the code actually prints.** `scripts/audit-docs.py:2936`, inside `check_owner`
(`:2890`), run live at this tree:

```
check 35: 406 owner(s) checked in scope; 50 owner check(s) deferred (owner: W37-10,
RL-1046 §B — F92's stamp-deferred population); 66 exemption(s) in the F83 register
reconciled against 579 file(s) in RFC-937's stamp set; 93 unstamped file(s) in the
enforced checks-30-39 scope
```

The literal also carries into the helper `_is_stamp_deferred_w37_10` (`:2443`), its call
site (`:2911`), the comment block at `:2433` and `:2436`, and the docstring at `:2898-2899`.

**2. `CR-1064` is a filed proposal, not a governed ruling — it reports a decision, it does
not make one.** `CR-1064-…md:24-25` self-declares: *"Per `CLAUDE.md` §14 and §12 this is
**a proposal and nothing else**: it edits no plan, no roadmap row and no"* …; `:632` reads
`**Maintainer acceptance:** _pending_`. And `:372` *narrates* rather than rules: *"The lead
has ruled the reconciliation (00:55:09 BST relay: …)"* — a chat relay, which `CLAUDE.md` §12
says is not where a decision lands. **So `CR-1064:372` is not one of two disagreeing
governed records.** It is a review reporting an unfiled ruling.

**3. But the decision it reports *is* durably filed — in the findings register, and that
changed after `PL-1070`'s frozen base.** `docs/findings/register.md:133`, F92's own row,
carries at this tree:

> **Reconciled at checkpoint 3, 2026-09-18 (lead decision; deputy ruling `to-lead.md`
> 2026-09-18 00:55:09 BST acknowledges it):** … **Owner of record stays W37-11** — the
> 2026-09-03 maintainer-sourced reassignment (quoted above) stands and is not reopened. The
> live check-35 tag `W37-10` (`RL-1046` §B) is **not a fourth owner**: it is recorded here as
> the stamp-deferral population's own label, to be aligned by W37-7's and W37-8's leaf plans
> … **Count corrected: ~~53~~ (struck 2026-09-18) → 50**

**That clause is absent at `a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15`**, the commit
`PL-1070`'s `tree:` field names, and present at `7d5d6e0`. Measured by extracting F92's row
from both refs and diffing them: the row is the only changed F92 text, and the added text is
the reconciliation clause. It landed in `d63f765085fe6eb1c594177c5779ecfc3caf7ae8`
(`docs(closures): W37-6 checkpoint 3 — slice close record, register, roadmap row, ledger`,
2026-09-18T09:17:52+01:00), which `git merge-base --is-ancestor d63f765 7d5d6e0` confirms is
an ancestor of this tree. **`PL-1070` was drafted against a tree at which the register did
not yet answer DP-7-1. It does now.** The register is a governed record: `audit-docs.py`
check 35 and `register-owed.py` both read it.

The older limb of that cell — the 2026-09-03 reassignment from W37-6 to W37-11 — I verified
at its source rather than through the register's quotation of it. `git log -1 --format=%B
db19be8` (2026-09-03T00:04:54+01:00, PR #654) reads: *"The maintainer offered W37-11 or the
Work's closure record for F92's 53 deferred files; the lead names W37-11, because a closure
record should record that the standard was applied rather than be where it is finally
applied."* The register's quotation is faithful to it.

**4. `RL-1046` does not rule on F92 at all.** Two differently-built sweeps of the whole
267-line file agree on the negative. `grep -n 'F92\|\b53\b\|\b50\b\|SKILL\|agents\|stamp-defer\|deferred'`
returns only three hits, all in the unrelated live-agent-cap section at `:209`, `:212`,
`:217`. A second, looser sweep — `grep -ni 'defer\|front.matter\|harness\|merge into\|FD-1029\|F9[0-9]'`
— returns `:58` (a comment naming F96) and `:83` (§8.5's essay deferral), neither about this
population. The section list confirms §B is the only candidate section.

**What §B does rule** (`RL-1046-…md:99-113`) is which **`audit-docs.py` failure classes**
may be non-zero in the `§7(h1)` gate row: *"`(h1)` passes when every `audit-docs.py` failure
class on the migrated snapshot is zero except checks 29, 30 and 35, which the row prints **by
count, each labelled `owner: W37-10`**, and which do not set the exit code."* Its grounds
(`:113`) source that label to the map plan's slice scope via `PL-1036:143-151`, whose table
row reads: *"Widening `_ID_SCOPE_ROOTS` (row 1h) does put `.claude/roles`, `.claude/skills`
and `.claude/agents` in scope, and **92 files** there are unstamped on the migrated tree.
Those are **content** rows: the checks now *see* them, which is row (h)'s job; **making them
pass is W37-10's**."*

**5. So the two populations are different sets, and both are in check 35's one note.**
`RL-1046` §B's check-35 class is *files unstamped under the widened scope* — 92 at
`PL-1036`'s tree, printed at this tree as the note's final figure, **93 unstamped file(s)
in the enforced checks-30-39 scope**. F92's population is a different, narrower set defined
by a different predicate: `.claude/skills/*/SKILL.md` and `.claude/agents/*.md` whose front
matter is the harness's own schema *that a stamp must merge into* (`_is_stamp_deferred_w37_10`,
`:2443-2474`, anchored on both path and content) — **50** at this tree, matching F92's
corrected register count of 50 exactly. The `−3` against F92's original 53 are the vendored
manifests `create-adaptable-composable`, `planning-with-files` and `vue-best-practices`,
which raise `HeaderError` in `parse_header` and so are dropped by `check_owner`'s
`except _docid.HeaderError: continue` (`:2907-2908`) before the helper is ever called —
F88's gap, limb 1 of which is discharged (register `:129`, PR #649) in `doc-id.py`'s
discovery but not at this separate call site.

**The defect is therefore not a disagreement between records. It is a label that travelled
off the population it was ruled over onto a narrower one, carrying its citation with it** —
`RL-1046` §B is cited at `:2428-2436` and `:2899` as the authority for an owner it never
named. Two populations share one note; the label attached to the wrong one.

**6. The DP row's five test citations are four different meanings of one string.** Verified
individually at `7d5d6e0`:

| Citation | What `W37-10` means there | Disposition |
|---|---|---|
| `tests/test_audit_docs_ids.py:684` | *"Slice W37-10's to write"* — the `docs/` READMEs | correct; **must not change** |
| `tests/test_audit_docs_ids.py:1630`, and `:1638`, `:1639`, `:1656`, `:1665`, `:1681` | F92's deferred population and the helper name | **change** |
| `tests/test_register_lint.py:547` | *"Residue class 2: the phase-1b merge (RL-1046 check 29, owner W37-10)"* — check **29**, not 35 | correct; **must not change** |
| `tests/test_doc_id_verify.py:1881`, `:1894` | `RL-1043` §3 (cited there in its pre-migration form): row `(i)` is W37-10's | correct; **must not change** |
| `scripts/audit-docs.py:2481` | `readme_owner_allowlist`: *"`docs/ READMEs` is Slice W37-10's to write"* | correct; **must not change** |

## Ruled

**Option (b) in shape, amended in its literal. (a) and (c) are refused.**

**(i) The printed note.** `scripts/audit-docs.py:2934-2937` prints:

```
"deferred (F92's stamp-deferred population, owner W37-11 per "
"docs/findings/register.md; non-fatal here under RL-1046 §B, which ruled the "
"disclosure and not the owner); "
```

This names the owner of record from the record that holds it, keeps `RL-1046` §B cited for
the only thing `RL-1046` §B rules — that the class is disclosed by count and does not set
the exit code — and stops citing it for the owner. A reader following either citation lands
on a document that says what the sentence says it says, which is the test `RFC-777` sets.

**Why (b)'s own proposed string is amended rather than adopted.** (b) would have printed
*"deferred under RL-1046 §B, which named W37-10; owner of record reassigned"*. That asserts
a reassignment away from W37-10 that never happened: W37-10 was never F92's owner, as F92's
register row says in terms (*"not a fourth owner … the stamp-deferral population's own
label"*). The only reassignment of record is W37-6 → W37-11, 2026-09-03, `db19be8`. Writing
(b) verbatim would have put a false history into the instrument that exists to detect false
history. The recommendation's *reasoning* — that (a) leaves a self-contradicting sentence and
that the identifier must stop carrying a slice tag — is adopted in full; only its draft
wording is corrected.

**(ii) The helper renames to `_is_stamp_deferred_f92`**, at `:2443` and its call site
`:2911`. A finding id is permanent (`CLAUDE.md` §5); a slice id is not. The name keys on the
population's defining finding, so the next reassignment cannot reproduce this row.

**(iii) The comment block and docstrings.** `:2436` (*"deferred to W37-10 rather than
hand-stamped here (that would be W37-10's own work)"*) and `:2898-2899` (*"RL-1046 §B,
`owner: W37-10`"*) state the owner and are **wrong**; both take W37-11 with the register
cited. `:2433` is a **verbatim quotation of `RL-1046` §B** and its words are not altered —
the surrounding prose instead states that the quoted label ranges over §B's unstamped-scope
class (the note's `93 unstamped file(s)` figure), not over F92's 50.

**(iv) No frozen record is amended, superseded or worked around.** Because `RL-1046` §B
never ruled F92's owner, this ruling does not touch it. Options (a) and (b) both silently
assumed §B had to be contradicted; neither had to be. `RL-1046` §B's own acceptance clause —
*"a 29/30/35 count omitted rather than printed with its owner"* — is satisfied by the new
string, which still prints the count with an owner.

**(v) `PL-1070`'s Task 13 Step 1 is corrected by this ruling.** Its stated reasoning — *"A
partial rename leaves the corpus saying both things — which is the defect being fixed,
reproduced"* — **inverts here**. Four distinct meanings share the string `W37-10`; a
corpus-wide rename would corrupt three correct statements. Only the rows marked **change**
in the table above are touched. The executor runs Step 1's `grep` as an enumeration, then
classifies each hit against that table, and changes nothing the table marks correct.

**Why not (c).** (c) defers a one-line edit into W37-11 — the slice whose job is to *prove*
the corpus consistent — and would have it inherit, as its own finding, a defect in the
instrument it must use to do the proving. Refused for the reason the plan gives.

## What it obliges

- **W37-7's executor**, at `PL-1070` Task 13: applies (i)–(iii), classifies Step 1's hits by
  the table in §6 above, and adds the check named under Acceptance. The task is unblocked.
- **The lead**: adopts, amends or rejects this ruling; then writes `RL-1075` into DP-7-1's
  `Resolved by` cell and moves `PL-1070` to `status: active`. Both are the lead's edits, not
  this role's — `docs/process/document-ids.md:152`.
- **This ruling deliberately does not decide**: DP-7-2 through DP-7-5 (their `Resolved by`
  cells name Task reviews and the lead); F108's output-shape question at register `:148`;
  whether the `93 unstamped file(s)` class is fatal, which I did not measure and do not
  assert; and anything about `CR-1064`'s pending acceptance line, which is the maintainer's.
- **A disclosure this ruling found on its own path, sized but not ruled — it is the lead's.**
  Minting this record's id surfaced a live id collision, and I record it here rather than fix
  it because it is corpus-wide, already on `main`, and in no charter of mine.
  **`RFC-937` §1.1 rule 1: *"`n` is an integer from one sequence shared by every family …
  No number is used twice."*** `docs/REDIRECTS.csv` allocates **74** `FD-` ids to legacy
  *register rows* — rows whose `new_path` is `docs/findings/register.md`, so they never
  materialise as files and never reach `docs/INDEX.md`. Their numbers run from **1063 to
  1136** inclusive (written as bare numbers here: citing the unmaterialised ids in their
  `FD-` form would add check-32 unresolvable-id rows for ids that by definition cannot
  resolve, which is the defect being reported, not a way to report it).
  Predicate, runnable at this tree:

  ```
  grep ',docs/findings/register.md,' docs/REDIRECTS.csv | grep -oE 'FD-1[0-9]{3}' | sort -u -V
  ```

  **Five of that block are already live in `docs/INDEX.md` as different governed things** —
  `FD-1066`, `FD-1067`, `FD-1068`, `FD-1069`, `FD-1074` — found by testing each of the 74
  for a row in `INDEX.md`. The sharpest instance is `docs/REDIRECTS.csv:310`, whose
  `new_id` is `FD-1074` and whose `title:` field names a legacy overview requirement clause,
  while `FD-1074` in `INDEX.md` is *"No SL- row exists for any slice, and no PL- carries a
  slice: field"* — filed at this very tree. **A reader following that row's legacy citation
  lands on an unrelated finding.** (The legacy id and path literals in that row are not
  reproduced here: check 36 counts them wherever they appear, including in a quotation of the
  redirect table itself, and this record must not spend from that pooled count to make a
  point it can make by description.) The file-migration rows are *not* affected and are
  correct — `docs/REDIRECTS.csv:364`'s `new_id` `FD-1006` resolves to the matching file
  under `docs/findings/` and to the matching `INDEX.md` title; the defect is confined to the
  register-row block.

  **Why neither instrument catches it, pinned by symbol rather than by description:**
  `scripts/doc-id.py`'s `compute_next` is *"`max` across all four RFC-937 §1.7 sources, plus
  one"*, and those four are `scan_header_ids`, `scan_spec_bold_ids`, `scan_roadmap_row_ids`
  and `scan_index_ids`. **`docs/REDIRECTS.csv` is not one of them**, and the register-row ids
  appear in no other source, so allocation cannot see them. `doc-id.py check` likewise
  reports zero duplicates: its contiguity source is `docs/INDEX.md`, where these 74 ids are
  absent. **So every id minted from now to 1136 collides** — roughly 61 still queued.
  (`doc-id.py next` reads a committed ref via `compute_next_at_ref`, not the working tree,
  which is correct behaviour and not part of this defect.)

  **This record takes `1075`, which `doc-id.py next` gave it, knowing `docs/REDIRECTS.csv:312`
  assigns 1075 to `F20`'s register row.** That is the sixth instance, taken deliberately and
  disclosed rather than taken silently: the five precedents above are on `main`, every id
  below 1137 collides equally, and choosing one above the block by hand would be exactly the
  hand-minting the process forbids. **Renumbering this record is cheap while it is unmerged
  and I will do it on request** — which id policy applies is the lead's, not mine. Filing
  this as a finding with an owner is also the lead's; I have measured it, not disposed of it.

- **One observation, not a ruling, for the planner.** `PL-1070`'s front matter field is named
  `tree:` but holds `a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15`, which `git cat-file -t`
  reports as a **commit**, not a tree. The same is true of `CR-1064`'s `tree: 4d9fe1d…` and
  of this record's own `tree:` field, which follows the established convention rather than
  breaking it unilaterally. The convention is harmless but the field name is inaccurate
  corpus-wide; worth a `docs/process/document-ids.md` clarification in an instruments slice,
  and it is `RFC-937`'s to define, not this ruling's.

## Acceptance — the violation that must become detectable

**The violation: check 35's printed owner tag and F92's owner cell in
`docs/findings/register.md` say different things, and nothing reds.** That is the defect
class this ruling closes, and it is the class — not the instance — that must become
checkable. Changing an assertion to match the new string proves only that the string was
changed.

- **A test that derives both sides and compares them.** It reads the owner tag out of
  `check_owner`'s note and the Work-item cell out of F92's register row, and fails when they
  differ. *Violation: the register's F92 Work-item cell is set to any value other than the
  one the note prints — flip it to `W37-10` in a `tmp_path` copy of the register and the
  test must red.* Built on constructed input rather than by mutating the real tree (F89 limb
  1, declined rather than repeated), and pinned by symbol, never by a pasted literal: a
  pasted `"W37-11"` on both sides is a tautology that survives the register changing under
  it.

- **A test that the three correct `W37-10` statements survive.** *Violation: a corpus-wide
  rename of `W37-10`. Apply one to `tests/test_register_lint.py:547`'s check-29 comment or to
  `scripts/audit-docs.py:2481`'s `readme_owner_allowlist` docstring and the check must red* —
  this is the failure mode Task 13 Step 1's own wording would have produced, so it is the one
  worth arming.

- **Shown red before this ruling is applied, not after.** The executor demonstrates both
  reds on deliberately broken input in Task 13 Step 3 and pastes the failing output into the
  slice ledger. A check that has never printed a failure has not been tested (`CLAUDE.md`
  §13).
