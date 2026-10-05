---
id: RL-9634
family: ruling
title: Working ids are lead-reserved, written in the space form, kept out of titles, slugs and headers, and re-pointed at mint; created is the mint date
status: active                 # active → superseded | retired (§1.2a) — PROPOSED until the ACK of the maintainer (by delegation)
created: 2026-10-05            # drafted 2026-10-05; set to the mint date at mint (clause 2)
owner: decision-maker
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RFC-9635, WK-1178]
---

# RL-9634 — Working ids, and `created:` as the mint date

*Working id 9634; its RFC has working id 9635. Drafted 2026-10-05 by the decision-maker on
the lead's instruction. The family is `process/`'s (`document-ids.md` §1.6, row "Reference —
`process/`"), so the maintainer accepts this ruling. It stays **PROPOSED** until the ACK of
the maintainer (by delegation). It mints after #1147 (RFC 9653 + RL 9654). **Nothing below is
applied in this PR**: every amendment is a T-text.*

*The decided points are the maintainer's (by delegation) own words, quoted by entry header
from `~/gi-pricing-plan.local/channel/to-lead.md` (a local file, not in the repository). The
decision-maker drafted options and a recommendation for the four points those entries left
open (OP-A to OP-D below). The maintainer (by delegation) ruled all four in the entry
`2026-10-05 14:33:33 BST — RFC 9635 + RL 9634 (#1153 @b14d674f, the working-id rules): OP-A..OP-D
RULED now, two narrowed`, quoted in full under "OP-A to OP-D — ruled", and the clauses and
T-texts below carry those rulings (folded 2026-10-05 15:55 BST at origin/main `cdaaa573`).*

## Verified first, at 83ea509023d6d705d6f78fe74b7124fdf1375739

Every example below was read at origin/main `83ea5090` on 2026-10-05, between 14:20 and 14:40
BST. The evidence table is in RFC 9635's Problem section. This section adds only what the
ruling itself relies on.

- **The maintainer's (by delegation) entries, read in full:** `2026-10-05 14:15:12 BST — ID AUDIT (…): the
  sequence is sound; 4 defects to fix, 3 rule gaps`; `2026-10-05 14:19:21 BST — CORRECTION to
  my 14:15:12 order 3: …`; `2026-10-05 14:26:28 BST — ID AUDIT: consolidated instruction and
  next steps (…)`; `2026-10-05 13:50:07 BST — Snapshot-table working ids: AGREED as they are,
  with one label; the PL 9688 correction is noted`.
- **`document-ids.md` at this tree** has no text on working ids. A case-insensitive grep for
  `working id|working-id|9xxx` over the file returns no line. It does not define `created:`
  beyond the specimen `created: 2026-09-02` (§1.5) and check 31's "`created`
  non-decreasing with the number" (§1.11).
- **The practice for a draft's own id**, read from #1147 at `cd08475b`: the RFC draft with
  working id 9653 carries that number in the hyphen form in its filename (padded), its `id:`
  and its H1, and its `relates:` names its same-PR sibling, working id 9654, in the hyphen
  form too. In prose it writes "Working id 9653" and "Its ruling is RL 9654". (The hyphen
  forms are not reproduced here: in this file they are citations, and check 32 cannot
  resolve an id that is not yet in `INDEX.md`.)
  So the hyphen form appears in the draft's **own** id slots and in the `relates:` of its
  same-PR sibling, and nowhere else. This draft follows the same practice. That is why
  check 31 is expected to red on it until it mints.
- **The mint-commit clocks** (`git show -s --format='%aI %cI'`; author and committer dates
  agree on all five): `d2ac260d` 2026-10-01T00:57:18+01:00 (`RL-1346`, `RL-1347`);
  `c535b19d` 2026-10-01T09:36:36+01:00 (`RL-1362`); `95bcf1a9` 2026-10-03T18:31:02+01:00
  (`RL-1379`); `36a9f483` 2026-10-05T11:45:05+01:00 (`LG-1412`); `072c56e1`
  2026-10-05T12:10:45+01:00 (`FD-1413`).
- **Re-verified at origin/main `cdaaa57345cb765f96034ce1ec2733c338f1c3cd`** (2026-10-05, about
  15:55 BST), when the OP rulings were folded in. Every line cited below at `83ea5090` still
  sits at the same number. One fact has moved: #1150 merged as `bc92bb7e`, and it re-pointed D1
  (`03-rating-engine.md:136` now reads "on FD-1393") and D2 (`roadmap.md:1434` now reads
  "FD-1415" and "FD-1414"). So the pre-existing hits that the lint's warning period was to let
  clear are now cleared. The insertion anchors that the T-texts give are counted at this tree
  under each T-text.

## Ruled

### Clause 1 — Working ids (decided by the maintainer (by delegation); written down here)

The maintainer's (by delegation) 14:26:28 entry, item 5(a): *"working ids: 4-digit 9xxx, written "FD 9707"
(space form, never hyphen), reserved only by the lead in eta.md, never in a title, filename
slug or header, re-pointed in living files at mint (step 3)"*. Its sub-rules:

- **(i) Format.** Four digits, 9000–9999, prefixed by the family in the **space form**
  (`FD 9707`). A working id is never written in the hyphen form, because that form is a
  minted id's (§1.7) and check 32 resolves it. One exception, OP-A as ruled (narrowed): the
  draft's own id slots inside its own files. Every text that survives a squash into main's
  history or is read outside the file uses the space form: the PR title (the squash
  subject), commit subjects and the PR body. A branch name may use either form, because it
  is deleted at merge.
- **(ii) Allocation.** The lead is the sole allocator and reserves each working id in the
  reservation table of `~/gi-pricing-plan.local/handover/eta.md`. `doc-id.py next` reads
  origin/main, so it cannot see a reservation. The 14:26:28 entry, item 4: *"eta.md: mark
  each reservation row "→ MINTED <id> (mint <sha>)" IN the same turn as its read-back, so the
  table never drifts again."*
- **(iii) Never in a title, filename slug or header.** A record's `title:`, its filename
  slug, its H1 and every other header field cite only **minted** ids (OP-A's own-id slots excepted). A record that must
  name an unminted record waits for that record to mint (the maintainer's (by delegation) 13:15:19 rule, "a
  citing record mints after the cited", as restated in the 13:50:07 entry). Otherwise it
  names the record in its body only. `RL-1362` and `RL-1379` are the historical cases: both
  titles and both slugs carry a working id. #1147 records them as known historical defects
  that stand as merged, and this ruling does not reopen them.
- **(iv) Re-pointed at mint, in living files.** The 14:26:28 entry, item 3: *"after the mint
  commit, `git grep -nE '\b(<FAMILY>) <working id>\b' origin/main -- docs/` over LIVING
  files (specs, roadmap, open-questions, register, INDEX, READMEs) and over open PRs;
  re-point every live hit in the same mint PR, or list it in the PR body with the follow-up
  PR. Frozen records are left as written."* `docs/INDEX.md` is generated. It is re-pointed by
  re-running `doc-index.py`, never by hand.
- **(v) Frozen records and quotations stay as written.** A frozen record keeps the working
  ids it was merged with (§1.2's mutability column; RL 9654 under #1147). A quotation
  reproduces its source, so a quoted entry header that names a working id keeps it. The
  minted id may go **beside** the quotation, never into it. (This is the maintainer's (by delegation) 14:15:12
  order 1: "keep the quote and add the minted id beside it instead".)
- **(vi) Snapshot tables.** The 13:50:07 entry: *"a working id written BESIDE its PR number in
  a contention snapshot table resolves permanently through the PR … One condition: each such
  table is labelled as a snapshot, "open PRs at <tree sha>, <date>; working ids as then", so
  nobody reads a row as current or as a dependency. A working id WITHOUT its PR number
  anywhere in a frozen record still needs a re-point or must mint first."*
- **(vii) Live working ids in living files are labelled.** Before mint, a living file that
  must cite an unminted record writes "`PL 9776` (working id)". This is the form at
  `open-questions.md:141` and `03-rating-engine.md:1369` at this tree. The label tells a reader
  that the citation is provisional. The sweep in (iv) replaces the label together with the
  id.

### Clause 2 — `created:` is the mint date (decided by the maintainer (by delegation); the clock is OP-B)

The 14:26:28 entry, item 5(b): *"`created:` = the mint date (resolve the RL-1346/1347 and
LG-1412 mismatches by noting them, with no edits)"*. The 14:15:12 entry asks the rule to
"say what a mismatch means".

- **The mint date** is the calendar date, on the clock fixed by OP-B, of the commit that
  adds the file to origin/main under its minted id.
- **The filing date is kept in a YAML comment** on the same line, in the precedent form.
  `RL-1379` reads `created: 2026-10-03              # the mint date (check 31); ruled
  2026-10-01`. `FD-1413` reads `created: 2026-10-05            # the mint date (check 31);
  filed 2026-10-01`. `RL-1379` (`95bcf1a9`, 3 Oct) is the earlier precedent. `FD-1413` is the
  one the lead named.
- **What a mismatch means.** For a record minted **before** this ruling mints, a `created:`
  that is not its mint date is a **pre-rule value**. Read it together with the body's mint
  line, which is authoritative for the mint date. It is not a defect to correct. For a
  record minted **after** this ruling, a mismatch is a defect. The auditor files it as a
  finding against the minting PR, and it is corrected only through `corrected_by:`, since
  the record is frozen. No body or header is edited.
- **The three known mismatches are noted here and not edited** (all verified at `83ea5090`):
  - `RL-1346`: `created: 2026-09-30`; body :31 "**Minted 2026-10-01 as RL-1346**"; added by
    `d2ac260d` at 2026-10-01T00:57:18+01:00, which is 2026-09-30 in UTC.
  - `RL-1347`: `created: 2026-09-30`; body :30 "**Minted 2026-10-01 as RL-1347**"; same commit
    and instant.
  - `LG-1412`: `created: 2026-10-04`; body :21 "reserved by the lead 2026-10-04 17:15:20 BST
    … it was minted as `LG-1412` on 2026-10-05"; added by `36a9f483` at
    2026-10-05T11:45:05+01:00. This is a reservation date, not a clock artefact.

  **Under OP-B as ruled (a), the Europe/London date, all three disagree with their mint
  date.** Under OP-B (b) (UTC), `RL-1346` and `RL-1347` would have agreed. That is why the
  clock had to be fixed. The 14:33:33 entry states the consequence: they *"are mismatches under
  this rule (their stamp is a UTC reading), as is LG-1412. All three are noted, not edited
  (frozen)."*
  The files themselves cannot say which reading their authors meant, and this ruling does
  not guess.

### Clause 3 — The lint (ruled by OP-C; not built here)

The 14:26:28 entry, item 5(c): *"an optional lint for a space-form working id in a living
file after its id has minted (check 32 cannot see it)"*. The decision-maker proposed the lint.
The maintainer (by delegation) ruled its predicate, its warning period and its IETF handling
under OP-C (14:33:33 entry), so the lint is no longer optional. **T3** states it. Its host
(check 32) is the decision-maker's proposal; the 14:33:33 entry does not name a host.

- **Host: check 32** (`check_citations` in `scripts/audit-docs.py`). The violation is a
  citation that does not resolve to a minted id, which is check 32's subject. Check 38 (the
  loop signal, warn-only) is the alternative. It is rejected because a stale working id is
  wrong, not merely a signal. As ruled under OP-C, the lint is **warn-only for 2 weeks from
  this ruling's merge, then fatal**. The 14:33:33 entry: *"the date goes in the RL, not "2
  weeks""*. The merge date is not known until this ruling mints, so the date is written here
  at the mint: **warn-only until <the mint date + 14 days>, written at mint**. The
  pre-existing hits that the warning period was first meant to clear (D1 and D2) were
  re-pointed by #1150 (`bc92bb7e`).
- **Scope: living files only.** Under §1.2's mutability column, that means specs, the
  roadmap, `open-questions.md`, `findings/register.md` and READMEs. Frozen and append-only
  families are never scanned (clause 1 (v)), and `INDEX.md` is regenerated, not linted.
- **False-positive cases**, measured at `83ea5090` (RFC 9635: 13 hits, 3 true):
  1. **Quotations** of an entry header or a record. The lint skips text inside double
     quotes, inside `*"…"*`, and inside `>` blockquotes. 4 of the 13 hits.
  2. **Snapshot tables** labelled per clause 1 (vi). The lint skips a table whose preceding
     line carries "open PRs at <sha>". 0 of the 13 (none in the scanned living files).
  3. **Live working ids**, not yet minted. OP-C (a) makes these exact. 3 of the 13 hits.
  4. **IETF RFC numbers.** `RFC 9457` (HTTP problem details) is cited at `00-overview.md:346`,
     `07-platform.md:181` and `roadmap.md:774`. In the space form, the `RFC` prefix collides
     with IETF numbering, which already reaches 9xxx. This RFC's own working id, 9635, is also
     an IETF number. Under OP-C (a), only an RFC working id that has actually minted can fire,
     so a collision needs an IETF citation that matches an RFC working id the lead
     allocated. As ruled, that case is handled by **an allowlist entry with a reason**: the
     14:33:33 entry, *"IETF "RFC 9457" is flagged only if 9457 was one of ours, and then an
     allowlist entry with a reason handles it"*. At `cdaaa573` the only 9xxx IETF RFC that the
     living files cite is 9457 (`git grep -h -o -E '\bRFC [0-9]{4}\b' cdaaa573 -- docs/specs
     docs/roadmap.md docs/open-questions.md docs/findings/register.md '*README.md'` prints
     `RFC 9457` six times and `RFC 6648` twice), and the lead's reservation table in
     `eta.md` (local) holds no 9457.

### OP-A to OP-D — ruled

The decision-maker drafted the options and recommendations below. The maintainer (by
delegation) ruled them in this entry in `~/gi-pricing-plan.local/channel/to-lead.md`, quoted in
full:

> ## 2026-10-05 14:33:33 BST — RFC 9635 + RL 9634 (#1153 @b14d674f, the working-id rules): OP-A..OP-D RULED now, two narrowed
>
> OP-A: (a), NARROWED. A draft's OWN id slots inside its own files (`id:`, the filename, the H1, a same-PR sibling's relates:/deliverable:) keep the hyphen form, because check 31 needs it to parse. But every text that survives a squash into main's history or is read outside the file uses the SPACE form: the PR TITLE (the squash subject), commit subjects and the PR body. That is the D4 class. Branch names: either form, since they are deleted at merge.
> OP-B: (a), the mint date on the Europe/London clock, the project's clock for every stamp. Consequence, stated in the RL: RL-1346 and RL-1347 (`created: 2026-09-30`, merged 2026-10-01T00:57+01:00) are mismatches under this rule (their stamp is a UTC reading), as is LG-1412. All three are noted, not edited (frozen).
> OP-C: (a), a `working_id:` header field set at mint, a dated addition to document-ids.md's closed field set (§1.5 :119-142) in the same RL. The lint flags a space-form id in a living file ONLY when that number is some record's `working_id`, so IETF "RFC 9457" is flagged only if 9457 was one of ours, and then an allowlist entry with a reason handles it. Warn-only for 2 weeks from the RL's merge, then fatal; the date goes in the RL, not "2 weeks".
> OP-D: (a). At `doc-id next` ≥ 8000 the lead raises an RFC to move the working-id range. Today next is 1417.
> Clause (vii) (a live working id in a living file carries "(working id)"): OK.
> It mints after #1147, as planned.

Clause 1 (vii) stands as written ("OK"). Each point's options follow, with the ruling after
the recommendation. The entry's `§1.5 :119-142` reads, at `cdaaa573`, as §1.5's YAML field
block (the fence opens at :119, the last field, `was:`, is :138, and the fence closes at :140).


**OP-A. Does "never in a header" bar a draft's own working id from its own header?**
- (a) **No.** The draft's **own** id slots carry it in the hyphen form until mint: `id:`,
  the filename prefix, the H1, and a sibling's header citations of it (`relates:`,
  `deliverable:`) when the sibling is filed in the same PR. The mint renames all of them. This is the practice, verified on #1147. Its cost: check 31 reds
  until mint (expected and known), and check 32 resolves only after `doc-index.py` runs on
  the branch.
- (b) **Yes.** The draft would carry no id until mint. Check 30 requires `id:` and check 31
  parses it from the filename, so a draft could not be filed as a governed file. Activation
  needs that cite a pre-mint ruling would lose their anchor.
- **Recommendation: (a).** The maintainer's (by delegation) words target citations: the defects named are titles
  and slugs that cite **another** record's working id. (a) writes down what every pre-mint
  draft already does. (b) breaks drafting.
- **Ruled: (a), NARROWED.** The hyphen form stays only in the draft's own id slots inside its
  own files. The PR title, commit subjects and the PR body use the space form. A branch name
  may use either. Carried into clause 1 (i) and T1.

**OP-B. Which clock is the mint date read on?**
- (a) **The UK civil date** (Europe/London, BST or GMT) of the commit that adds the file to
  origin/main. The channel, the handover and the body mint lines ("Minted 2026-10-01") all
  use this clock.
- (b) **The UTC date** of the same commit. This is machine-neutral, but it disagrees with
  every body line for a mint between 00:00 and 01:00 BST, as `d2ac260d` shows.
- **Recommendation: (a)**, read with `git show -s --format=%cI <commit>` and converted to
  Europe/London. On a squash merge, the committer date is the merge instant (the five commits
  above show identical `%aI` and `%cI`).
- **Ruled: (a)**, the Europe/London clock, *"the project's clock for every stamp"*. Its
  consequence is in clause 2: `RL-1346`, `RL-1347` and `LG-1412` are noted as mismatches and
  not edited.

**OP-C. How does the lint know a working id has minted?**
- (a) **A new header field, `working_id:`**, written once at mint (for example
  `working_id: 9635`). It is added to §1.5's closed field set and joins the fields that are
  never edited after freeze. The lint reads it from `INDEX.md`'s source headers. This is
  exact, and the mapping lives in the repository rather than only in bodies and the local
  `eta.md`.
- (b) **Parse body lines** such as "Drafted as working id 9751; minted …" and "filed under
  working id 9789". This needs no new field, but the phrasings vary ("filed under working id",
  "**Working id**", "Drafted as working id" in the records RFC 9635 quotes), so it is a proxy predicate that misses whatever it does not match.
- (c) **No mint knowledge.** Fail every unlabelled space-form id in a living file, minted or
  not. This is simple. It misses a stale id that still carries the "(working id)" label, and
  it fires on the IETF case.
- **Recommendation: (a)**, if T3 is adopted at all. (b) is the proxy predicate the evidence
  rules out. (a) also gives the post-mint sweep (clause 1 (iv)) a repository-side source.
  If T3 is declined, OP-C lapses with it.
- **Ruled: (a).** `working_id:` is a dated addition to §1.5's closed field set, made by this
  ruling (T2). The lint flags a space-form id in a living file only when that number is some
  record's `working_id`. An IETF collision is handled by an allowlist entry with a reason.
  The lint is warn-only until the date that this ruling states at mint (2 weeks from its
  merge), then fatal. The ruling sets the lint's behaviour, so T3 is adopted. Carried into
  clause 3, T2 and T3.

**OP-D. What happens when the minted sequence nears 9000?** At this tree the maximum
minted id is 1416 (`FD-1416`). There is no near risk, but a 4-digit range has a ceiling.
- (a) **State a trigger now.** When `doc-id.py next` prints 8000 or more, the lead raises an
  RFC that moves working ids to a disjoint range. This costs one sentence.
- (b) **Say nothing.**
- **Recommendation: (a).** A collision would make one number both a working id and a minted
  id, and check 32 could then resolve a stale citation to the wrong record. The trigger is
  in T1.
- **Ruled: (a).** T1's last sentence carries the trigger.

### T-texts (to be applied to `docs/process/document-ids.md` by the applying PR; not applied here)

**T1, a new paragraph at the end of §1.7 "Citation and allocation":** inserted immediately
before the line `## 1.8 Widening` (`grep -cF` = 1 in `document-ids.md` at `cdaaa573`).

> **Working ids.** *(Added <date of the applying commit>, RL-<this ruling's minted id>, the
> maintainer's acceptance by delegation.)* Until a record mints, it is cited by a **working id**: four
> digits from 9000 to 9999 after its family, in the space form (`FD <9xxx>`), never in the
> hyphen form, which belongs to a minted id. The lead is the sole allocator: each working id
> is reserved in the lead's reservation table (`handover/eta.md`, local), and the row is
> marked with the minted id and mint commit in the same turn as the mint's read-back.
> `doc-id.py next` reads origin/main and cannot see a reservation. A draft's own id slots
> (`id:`, the filename prefix, the H1, and a same-PR sibling's header citations of it) carry its working
> id in the hyphen form, renamed at mint. Nothing else does: every text that survives a squash
> into main's history or is read outside the file (the PR title, commit subjects and the PR
> body) uses the space form, and a branch name may use either form. A working id never appears in a
> title, a filename slug or any other header field: a record that must name an unminted one
> mints after it or names it in the body only. In a living file, an unminted record is cited
> "`<PREFIX> <9xxx>` (working id)". At mint, every living file and every open PR is swept with
> `git grep -nE '\b(<PREFIX>) <9xxx>\b' origin/main -- docs/`, and each live hit is re-pointed
> in the mint PR or listed in its body with the follow-up PR. `INDEX.md` is regenerated, not
> edited. Frozen records stay as merged, and a quotation stays as quoted: the minted id goes
> beside it, never into it. A working id written beside its PR number in a contention
> snapshot table is permitted when the table is labelled "open PRs at <tree sha>, <date>;
> working ids as then". When `doc-id.py next` first prints 8000 or more, the lead raises an
> RFC that moves working ids to a disjoint range.

**T2, two parts, both in §1.5 (OP-C's "dated addition to document-ids.md's closed field set
… in the same RL" is T2b).**

**T2a, a sentence after §1.5's field block,** inserted immediately before the paragraph that
begins ``A vendored skill (`planning-with-files` `` (`grep -cF` = 1 at `cdaaa573`):

> **`created:` is the mint date**: the Europe/London calendar date of the commit that adds
> the file to origin/main under its minted id. The date the record was filed or ruled is
> kept in a YAML comment on the same line (`created: <mint date>   # the mint date
> (check 31); filed <date>`). *(Added <date>, RL-<this ruling's minted id>.)* For a record
> minted before that ruling,
> a `created:` that differs from its mint date is a pre-rule value, and the body's mint line
> is authoritative. For a later record, the difference is a finding, corrected through
> `corrected_by:`.

**T2b, one line in §1.5's field block,** inserted immediately after the line
`relates: [RFC-<n>, RL-<n>]    # ids only — never paths` (`grep -cF` = 1 at `cdaaa573`):

> `working_id: <9xxx>           # set once at mint, the record's working id; never edited (added <date>, RL-<this ruling's minted id>)`

It is not added to the fields permitted to change after freeze (`superseded_by:`, `status:`,
`corrected_by:`): it is written at mint, before the file freezes, and never changes.

**T3, the lint (adopted by OP-C as ruled; a WK-1178 backlog item, owner the lead).** A new
sub-rule of check 32 in §1.11's row 32. It is inserted between the cell's last words and the
row's closing ` |`. The find string is this one, with `grep -cF` = 1 at `cdaaa573`:
`every row id's anchor exists in its file |`

> "; **no space-form working id whose number is some record's `working_id:` remains in a
> living file outside a quotation, a labelled snapshot table or an allowlist entry that
> carries a reason** (warn-only until <the mint date of RL-<this ruling's minted id> + 14
> days>, a date written into this ruling at its mint; fatal from then)"

The allowlist entry with a reason is the ruled handling for an IETF collision, such as `RFC
9457` if 9457 were ever one of our working ids.

## What it obliges

- **The lead**: apply T1, T2a and T2b in one docs PR after this ruling's ACK, in the
  non-minting queue, and cut T3 into WK-1178's backlog (owner the lead). The warn-only date
  in T3 is written into this ruling at its mint (2 weeks from the merge). Brief every mint with clause 1
  (iv)'s sweep, which is already standing from the 14:26:28 entry, item 3.
- **The auditor**: from this ruling's mint onward, check `created:` against the mint commit
  (OP-B's clock) at every slice and record audit, and file a mismatch as a finding.
- **Not decided here**: T3's host, which is the decision-maker's proposal (check 32) and is
  not named in the 14:33:33 entry; any edit to `RL-1346`, `RL-1347`, `LG-1412`, `RL-1362` or `RL-1379` (none is made or
  proposed: they are frozen and noted). The spec-change skill states no id rules at this
  tree, so it is not amended.

## Acceptance — the violation that must become detectable

The violation: **a working id left in a living file after its record has minted**, and
**a `created:` that is not the mint date on a record minted after this ruling**.

- *Violation: a living file cites `FD <9xxx>` for a record whose `working_id:` is that
  number.* This is detectable only once T3 and OP-C (a) are built. Until then the mint sweep
  (clause 1 (iv)) is a procedure, not a check. Before the lint is called done, show it red
  on a deliberately broken input: D1's line (`03-rating-engine.md:136`) with "on FD-1393"
  put back to "on FD 9754" in a scratch copy. #1150 (`bc92bb7e`) re-pointed the real line,
  so at `cdaaa573` it no longer reds. This PR builds nothing, so nothing is shown red here.
- *Violation: a record minted after this ruling has `created:` ≠ the Europe/London date of
  its adding commit.* No check exists. It is an auditor check per "What it obliges". Check 31
  cannot see it: the three noted records pass check 31 at this tree.
- **Scope note:** clause 1 (ii), the lead's reservation table, is a local file outside the
  repository. No repository check can attach to it, and none is forced.
