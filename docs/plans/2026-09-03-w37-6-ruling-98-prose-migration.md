# W37-6 — Ruling 98: how the maintainer's prose decisions under `docs/plans/` migrate under NT-0019 (2026-09-03)

**Filed** 2026-09-03 by the decision-maker, under restored §1 authority. **What this is.**
The question put to the decision-maker: *"How do the maintainer's prose rulings filed under
`docs/plans/` migrate under NT-0019?"* — with a named starting set the delegating instruction
itself said to verify rather than assume complete.

**Authority.** The original W37-6 window (`2026-09-03T00:07:32Z`–`08:07:32Z`) expired and its
halt protocol ran and merged before this task reached the decision-maker
(`178541a8201be765dd262c895c61658b0d2b0581`, PR #663); the decision-maker verified this against
the tree itself and declined to file. **The maintainer renewed the delegation on the same
terms for eight hours from PR #663's merge**, recorded as a dated append at §6 of
`docs/plans/2026-09-03-w37-6-time-boxed-delegation.md`, merged `e56d038` (PR #664, "renew the
W37-6 delegation, and rule condition 2 and the tagged evidence ref"). **Self-verified**: `git
show e56d038:docs/plans/2026-09-03-w37-6-time-boxed-delegation.md` read directly from the
committed blob, not from a relay — §6.2 states *"So the renewed window expires
`2026-09-03T16:43:13Z`"*; this ruling is filed at `2026-09-03T09:04:39Z` (`date -u`), inside
that window. §1's two conditions on every ruling (delegation record, lines 27–31) — cite the
cell, not a paraphrase; price the option not taken — are both discharged below, revised twice
against the coordinator's review before filing (§5).

**Filed under** delegation §1, which delegates *"NT-0019 §1/§4 amendments needed to reach a
completing, green run — owner values, scope markers, stamp-set membership, exemption
dispositions, and template body shapes (`docs/_templates/`)"* (lines 19–21). This ruling is a
**scope marker / classification disposition**: which family and `owner:` a class of
already-existing documents takes when `doc-id.py migrate` runs.

**When the predicate in §2.1 is evaluated**, stated once here because §1 and §2.2 both depend
on it: **at migration time, against whichever tree `migrate` actually runs on — never frozen
at the tree this ruling happens to have been read against.** §1's membership table is a
reading taken at `e56d038`; it is illustrative of the predicate's result on that tree, not a
second, independent list. Where a later tree's content and this table's row disagree, the
predicate in §2.1 governs and the table is what has gone stale, not the rule — this is why
§2.2's exclusion is written as conditional on a named tree rather than as a permanent property
of the file.

## Authority

- The decision is the maintainer's under `CLAUDE.md` §12, delegated to the decision-maker for
  this window by delegation §1.
- The halt condition (delegation record, line 33 — *"two options with no cell to read from is
  a halt, not a coin-flip"*) — **not triggered**. Every element below reads from a named,
  quoted cell; where a reading had no cell, a competing reading with one existed, so it is
  priced out rather than halted on (§4).

## Ruling 98 — a document whose entire content is a maintainer decision migrates as `RL-`, `owner: maintainer`, no `kind:` field

**Structural note, added after filing.** This heading exists so `scripts/doc-id.py`'s
`_discover_multi_ruling_files` (`_RULING_HEADING_RE`, matching `^## Ruling \d+`) discovers
this record as one `RL-` draft rather than falling through to `_discover_plain_plans`'s
`PL- kind: leaf, owner: planner` catch-all — the exact misattribution this ruling's own §2.1
exists to prevent, which its own file was silently exposed to before this line existed.
Verified directly, not assumed: `_discover_multi_ruling_files` run against a copy of this file
with the heading present returns one `RL-` draft, `owner: decision-maker` (Ruling 95's default
— correct here, since this record is the decision-maker's own ruling, not a maintainer-
authored one under §2.1's `owner: maintainer` carve-out), covering the whole file; without the
heading it returns none, and `_discover_plain_plans` claims the file instead. Everything above
and below this line is one ruling; the heading marks where the splitter's own preamble-folding
rule needs an anchor, not a second document.

## 1. The set, verified structurally, not by filename keyword

The delegating instruction named four documents and warned that neither its list nor a
parallel agent's was certified complete. Two independent sweeps were run and are reconciled
here rather than either taken on faith:

- **A code-derived sweep** (relayed by the coordinator, independently verified against
  `scripts/doc-id.py` below): filtered `docs/plans/*.md` filenames on
  `handover|withheld|withholding|delegat|maintainer-decision`, then read each hit. Nine files.
- **A text sweep run here**: every `docs/plans/2026-*.md` file with no `^## Ruling [0-9]+`
  heading (125 of 164, reproduced independently — matches the coordinator's own count) whose
  first six lines mention "maintainer" case-insensitively. Twenty-three files.

**Verified directly in the source, not taken from the relay**: `scripts/doc-id.py:1179-1183`
(`_PLAN_SUFFIX_KIND`, the four suffix-to-kind pairs from NT-0019 §5.2), `:1186-1189`
(`_plan_kind_for_slug`, returning `"leaf"` when no suffix matches), `:1205-1206`
(`_PLAN_KIND_OWNER = {"map": "planner", "leaf": "planner", "review": "auditor", "handover":
"executor"}`), and `:1878-1906` (`_discover_plain_plans`, which stamps every non-multi-ruling
`docs/plans/*.md` file `prefix="PL"` unconditionally, `kind`/`owner` from the suffix table
alone, with **no content check at discovery time**). This is a real, currently-shipped default,
not a hypothetical one: absent this ruling, every one of the documents below is stamped
`owner: planner` at the next `migrate` run, because nothing in the discovery path reads a
document's own attribution.

**Reconciling the two sweeps, file by file** (title/attribution checked against each file
directly, not assumed from either sweep's label):

| File | In code sweep | In text sweep | Its own attribution | Verdict |
|---|---|---|---|---|
| `2026-09-03-w37-6-time-boxed-delegation.md` | yes | yes | "Issued...by the maintainer" (line 3); now also contains `### 6.3`/`### 6.4`, "the maintainer's judgement" (§2 below) | **RL-, owner: maintainer** |
| `2026-09-02-w37-6-go-ahead-withheld.md` | yes | yes | "Decided by: the maintainer" (line 3) | **RL-, owner: maintainer** |
| `2026-09-02-w37-6-second-withholding-and-standing-rules.md` | yes | yes | title: "...the maintainer's, 2026-09-02" | **RL-, owner: maintainer** |
| `2026-09-01-maintainer-delegation-and-nt-0019-precedence.md` | yes | yes | "Four decisions the maintainer made...no ruling number is minted here — they are not the decision-maker's to rule" | **RL-, owner: maintainer** |
| `2026-08-30-nt-0017-maintainer-decisions.md` | yes | yes | "The maintainer's answers to NT-0017 §5's three open questions, quoted and dated...not the decision-maker's to rule" | **RL-, owner: maintainer** |
| `2026-08-30-w11-reopen-direction.md` | yes | yes | "The maintainer's instruction to reopen...quoted verbatim and dated" | **RL-, owner: maintainer** |
| `2026-09-02-w37-vendored-exemption-ruling.md` | **no** — filename matches none of the code sweep's keywords | yes | "Raised...by the lead...**Ruled the same day by the maintainer**" | **RL-, owner: maintainer** — a real gap in the code-sweep's filename filter, independently confirmed structurally (no `id:`, no `## Ruling N`, opens on a bold attribution line) |
| `2026-09-03-w37-6-maintainer-decisions.md` | yes | yes | "**This document decides nothing. Every Decision line below is blank and is the maintainer's**" (line 10); `> **Decision:**` / `> **Date:**` blank at lines 141/143 and 184/186, verified unfilled **at `e56d038`** | **Excluded at `e56d038` — see §2.2. Conditional, not permanent**: named "maintainer decisions," structurally matches, but its content does not, because its Decision lines are blank *as at this tree*. The actual answers were filed as Rulings 96/97 in a sibling document; if this vessel is ever itself the one edited to carry a filled-in decision, it re-enters §2.1's predicate at that tree, not this one |
| `2026-09-03-w37-6-window-handover.md` | yes | no | "Written...**by the lead**" | **Not this predicate — `PL- kind: handover, owner: executor`** |
| `2026-08-20-w5-worker-handover.md` | yes | no | (a different work item's handover, same shape) | **Not this predicate — `PL- kind: handover, owner: executor`** |

**The two handovers are excluded by two independent routes, and both are recorded because a
reader who checks only one will not know the other agrees**: NT-0019's own prose (§1.13,
`:238`, *"handover → `PL- kind: handover`"*) and the shipped code's suffix table
(`_PLAN_SUFFIX_KIND`, `scripts/doc-id.py:1181`, `("-handover", "handover")`, resolved to
`owner: executor` at `:1206`) reach the identical answer without reading each other.

**The remaining sixteen of the text sweep's twenty-three** — the two slice-decision records
(`2026-09-02-w37-5b-slice-decision.md`, `...-5c-...`, "Decided by: the lead, under the
maintainer's...delegation" — the lead's decision, not the maintainer's own, and the RL role
row at `:149` names only "decision-maker" or "the maintainer" as owner, never "the lead"), the
two go-ahead ask documents (awaiting the maintainer's line, not yet decided), the outstanding-
obligations list, the two RFC drafts (self-declared `RFC-`, a different family), the process-
conformance audit (auditor-authored), the closure proposal, the landing package, the
chart/table retrofit plan (executor-authored), and three ledgers (mentioning "maintainer" only
in a provenance line) — **do not satisfy the predicate** and are not ruled here; each fails on
its own stated authorship, not on a shape check.

**Ruled population: seven, at `e56d038`.** The sweeps' union, corrected for the one member
whose label matches the predicate's name but whose content does not at that tree
(`w37-6-maintainer-decisions.md`), is what §2 below rules on. **This count is a reading, not
the rule** — stated in full at the top of this section: the predicate governs at whatever tree
`migrate` runs on, and this table is not re-verified automatically if that tree moves.

**One further exemplar, disclosed and not ruled on**: `2026-08-30-nt-0012-0013-0014-adoption.md`
opens the same way ("**Filed 2026-08-30 against `origin/main` @ `2e4684b`.**") but states of
itself *"a working record, revised in place with dated entries, not frozen"* — a living
container mixing a plan, the maintainer's instructions, and rulings made under it, rather than
one frozen decision. It is the same class of problem as §2.3 below (an embedded, unsplit
ruling inside a larger record), not an instance of this ruling's clean seven; naming it here so
a later split of that file is not treated as a fresh question.

**Limits carried forward, not dropped**: neither sweep is certified exhaustive. The code sweep
filtered on filename keywords first; the text sweep required "maintainer" in the first six
lines, which would miss a maintainer decision phrased without that word. Both sweeps agree on
every file they both examined, and the one file only the text sweep caught
(`vendored-exemption-ruling.md`) is independently confirmed by direct reading, not by a third
sweep — that convergence is evidence of coverage, not proof of it.

## 2. Ruled

### 2.1 A document whose entire content is a decision the maintainer made and dated, filed without a `## Ruling N` heading, migrates as `RL-`, `owner: maintainer`, no `kind:` field

**(a) The migration's mechanical split rule does not reach these documents.** §4 step 2:
*"Multi-ruling files → one per `## Ruling N`..."* (`docs/notes/0019-one-id-per-document.md:277`).
None of the seven carry that heading (verified per-file, §1 above); they are plan-shaped
(numbered `## 1.`, `## 2.` …), so step 2 does not fire and they fall to the residual rule.

**(b) The residual, suffix-only rule — real, shipped, and currently wrong for these seven.**
§5.2: *"...the rest → `plans/` with `kind:` from suffix (...); else `leaf`"*
(`docs/notes/0019-one-id-per-document.md:319`), implemented verbatim at
`scripts/doc-id.py:1179-1206` (verified above). None of the seven filenames match a named
suffix, so `_plan_kind_for_slug` returns `"leaf"` and `_PLAN_KIND_OWNER["leaf"]` is `"planner"`
— the shipped default today. **This is not a hypothetical reading; it is the status quo the
ruling overrides**, and it is worth stating what that costs left alone: a maintainer's own
"not yet," a maintainer's second withholding and standing rules, a maintainer's delegation
carrying two more embedded rulings (§2.3) — each attributed in the stamped header to the
planner, who wrote none of them.

**(c) A second, content-based cell governs and is not suffix-derived.** §1.13: *"...maintainer
decisions and phase pre-decisions → `RL-` with `owner: maintainer`..."*
(`docs/notes/0019-one-id-per-document.md:238`). This sentence's `handover` and
`slice-map/map-plan` clauses restate the suffix table verbatim (confirming (b)'s two clean
cases); the "maintainer decisions" clause names no suffix — it is a content rule sitting
alongside the suffix default, not inside it. Each of the seven is, on its own first line, a
document whose author names the maintainer as decider.

**(d) The role table's `RL` row independently reaches the same `owner: maintainer`.** §1.6, row
**RL**: *"decision-maker; **the maintainer may author one on scope or process**"*
(`docs/notes/0019-one-id-per-document.md:149`, Owner column). All seven are decisions on scope
(a go-ahead, a slice, a delegation's reach) or process (standing rules on method, a
delegation's terms) — matching the carve-out this row names, independently of (c).

**(e) `RL` carries no `kind:` field at all.** `docs/_templates/RL.md:8`: *"`kind:` and `plans:`
do not apply to this family and must not appear here."* Confirmed by the family table
(`docs/notes/0019-one-id-per-document.md:38`, `RL`'s `kind:` column `—`, against `PL`'s
`map`·`leaf`·`review`·`handover` at `:36`). The template's own field
(`docs/_templates/RL.md:27`) is `owner: decision-maker # the maintainer may also author one on
scope or process` — the exact carve-out (d) cites, with no `kind:` line to fill.

**(f) Nothing in NT-0019 supports "disclosed rather than migrated."** §4 step 1:
*"Assign one sequence to every row and document in `created`-date order"*
(`docs/notes/0019-one-id-per-document.md:276`) — unconditional, no carve-out for
maintainer-decision documents. **Step 6's "nothing exempt" is not this proposition's cell and
is withdrawn as support** (correction adopted from review): that clause reads *"Rewrite every
citation across the whole tree — `git ls-files`, nothing exempt"* (`:281`) — its "nothing
exempt" scopes to the **citation rewrite**, a later, narrower step, not to whether a document
is assigned an id at all. Step 1 alone rejects reading C, and does so on its own text without
needing step 6's help. (Step 6 remains true and relevant to what leaving these documents
unmigrated would cost — dangling citations from the go-ahead re-ask and the D1/D2 rulings file
— but it is evidence of cost, not of the rule.)

### 2.2 `2026-09-03-w37-6-maintainer-decisions.md` — excluded at `e56d038`, conditionally, not permanently

This file is the case the predicate's name alone would have swept in wrongly, **as read at one
named tree**. It is titled "maintainer decisions," is attributed nowhere else, and
structurally matches every marker the other six share. **But its own first paragraph says the
opposite of what its title implies, at `e56d038`**: *"This document decides nothing. Every
Decision line below is blank and is the maintainer's"* (line 10), and both
`> **Decision:**` blocks are unfilled **at `e56d038`** (lines 141/143, 184/186). The actual
decisions D1 and D2 it asked for were filed as Rulings 96 and 97 in
`docs/plans/2026-09-03-w37-6-d1-d2-rulings.md` — a **separate** document, per the frozen-file
convention (correct by append or new record, never in place).

**The exclusion is a state, not a property of the file, and it is written that way on
purpose.** *"Its `Decision:` lines are blank"* is true as at `e56d038`; it is not a fact about
the file that survives every future reading of it. The file exists precisely so the maintainer
can fill those lines in, and the moment one is, the document becomes exactly what §2.1's
predicate describes — a document whose content is the maintainer's own dated decision — and it
re-enters the ruled population at whatever tree that happens on. **This ruling does not rule
that outcome out; it rules that it has not happened yet, at the one tree checked.** So: **at
`e56d038`, this file keeps the shipped default** — `PL- kind: leaf, owner: planner` —
correctly, not by exception: it is a planner-assembled batch awaiting the maintainer, which is
exactly what a `PL-` `leaf` is for (§1.6, `:145`, "planner, via `writing-plans`"). **At the
tree `migrate` actually runs on, re-check this file's `Decision:` lines before relying on this
row** — do not carry `e56d038`'s reading forward as though it were the rule. Naming the file
"maintainer decisions" does not make it one, and blank `Decision:` lines today do not make it
permanently not one either; the predicate in §2.1 tests content at the tree in question, never
a title and never a past reading of that content.

### 2.3 The delegation record's own `### 6.3`/`### 6.4` — confirmed as the same document, not split

`docs/plans/2026-09-03-w37-6-time-boxed-delegation.md` was appended, after this ruling was
first drafted, with `## 6. Renewal and two rulings — dated append, 2026-09-03`, containing
`### 6.3 Ruling — gate condition 2 is accepted as met, with its disclosure` and `### 6.4 Ruling
— a tagged evidence ref does not count as an open branch` (verified directly at `e56d038`,
§ "Authority" above). **Confirmed: this is the behaviour intended, and it is a case §1's
seven-file enumeration did not have in front of it when first drafted.**

**Why it does not split.** §4 step 2's splitter matches `^## Ruling [0-9]+` exactly
(`docs/notes/0019-one-id-per-document.md:277`, and the parser it is coded against,
`_RULING_HEADING_RE`, matches only that top-level, numbered form). `### 6.3` and `### 6.4` are
third-level headings reading "Ruling — <title>," not second-level "## Ruling N" — the pattern
does not match on either axis (depth or numbered form), so `_discover_multi_ruling_files`
correctly does not touch this file and it stays one draft for `_discover_plain_plans`.

**Why that is the right outcome and not a gap.** §1.13's own clause for this exact situation is
adjacent to the one this ruling already cites: *"corrections and ruling addenda →
`corrected_by:` + a correcting `RL-`/`RFC-`"* (`docs/notes/0019-one-id-per-document.md:238`,
same sentence as the maintainer-decisions clause). §6.3 and §6.4 are additions to an
**unfrozen, pre-migration** file — the append itself says so (§6 preamble, "dated append,"
distinguished from a rewrite precisely because the header must stay legible as history). At
the real migration run, once this file is frozen as one `RL-` document under §2.1's ruling,
any *further* addition would have to arrive as a **new**, separate `RL-` correcting record
with `corrects:` naming this one and this one's `corrected_by:` appended — never as a further
in-place `### 6.n`. §6.3/§6.4 predate that freeze (they were appended to the still-`docs/plans/`
file, before `migrate` ever runs), so they migrate as part of the one document `migrate` finds,
which is what "the split rule does not reach `### `-depth headings" in fact produces. **No
amendment to step 2 is needed or ruled here** — the file's own structure and the standard's own
split predicate agree without help.

**This is the strongest concrete instance of what §2.1(b) costs left uncorrected.** The
document now carries the maintainer's original delegation *and* two more of the maintainer's
own rulings — §6.4 is itself "the maintainer authoring one on scope" in `:149`'s own words, a
second, dated corroboration of that cell distinct from the rule's own text. Absent this ruling,
all of it — three maintainer decisions in one file — is stamped `owner: planner` by the shipped
default (§1(b)).

## 3. What it obliges

- At the real `doc-id.py migrate` run, `_discover_plain_plans` needs a predicate check ahead of
  its suffix fallback for this content type — "the document's own attribution names the
  maintainer as decider" — before defaulting to `leaf`/`planner`. This ruling does not choose
  the implementation (a coded predicate versus a short exception list maintained beside
  `document-ids.md`); it rules the target output — `RL-`, `owner: maintainer`, no `kind:` —
  that either implementation must produce for the seven named in §1, and for
  `2026-08-30-nt-0012-0013-0014-adoption.md` once it is separately dispositioned (§1, not ruled
  here).
- `2026-09-03-w37-6-maintainer-decisions.md` is explicitly **not** obliged by this ruling to
  change **at `e56d038`**; it keeps the shipped default there. It **is** obliged to be
  re-checked against §2.1's predicate at the tree `migrate` actually runs on — the exclusion
  in §2.2 is this ruling's finding about one tree, not a standing carve-out for the file.
- The two handovers are confirmed, not changed.
- This ruling amends nothing in `CLAUDE.md`, NT-0019 §1, or any template — it applies an
  already-declared predicate (§1.13) and an already-declared field prohibition (`RL.md:8`) to a
  verified population.

## 4. The options not taken, priced

| Reading | What it produces for the seven | Cell it reads from | Cost of taking it instead |
|---|---|---|---|
| **A — the shipped default, `PL- kind: leaf, owner: planner`** | Wrong family and wrong owner for all seven: `owner: planner` on documents none of which attribute their decision to the planner. | `docs/notes/0019-one-id-per-document.md:319` + `scripts/doc-id.py:1179-1206` (a real cell, not a straw option — it is what runs today absent this ruling) | Misattributes the maintainer's own "not yet," second withholding, delegation (twice more via §6.3/§6.4), NT-0017 answers, and W11 reopen direction to the planner in the stamped header — the exact false-authorship defect Ruling 86 already struck for `RL`'s old hardcoded-owner heuristic in the opposite direction (`scripts/doc-id.py:1195-1201`'s own comment). |
| **B — `RL-`, `kind: delegation`, `owner: maintainer`** (as originally proposed) | Family and owner correct; `kind: delegation` is invalid — `RL.md:8` forbids any `kind:` on this family, and the family table (`:38`) lists no kind vocabulary. | `:238` + `:149` for family/owner; **no cell** for `kind: delegation` | Would fail `audit-docs.py` check 30 (unknown field) the first time stamped. Adopted **with `kind: delegation` struck**, which is what §2.1 rules. |
| **C — disclosed, not migrated** | Leaves the seven permanently outside the id scheme. | **No cell** — §4 step 1 is unconditional; the only named exemption (vendored skills, `:129`) does not reach `docs/plans/`. `:281` ("nothing exempt") was cited for this in the first draft and is withdrawn as support on review (§2.1(f)) — it scopes to the citation rewrite, not to assignment; §1 step 1 rejects C on its own and needs no help from it. | Breaks the citation rewrite for every inbound citation once the corpus moves regardless of which cell is cited for the rejection — the conclusion is unaffected by the correction, only its stated reason. |

**Per-reading rejection, at the verified seven-member population** (plus the two handovers and
the one excluded name-only match, shown for completeness):

| Reading | Rejects, of 7 (the ruled population) | Row 8 (`...maintainer-decisions.md`, **at `e56d038`** — re-evaluate at the migration tree) | Rows 9–10 (the two handovers) |
|---|---|---|---|
| A (shipped default) | 7 of 7 | Correctly produces `leaf`/`planner` at `e56d038` — not a rejection, this is the right answer for this file **on this tree**; the shipped default would also be right the moment it becomes wrong for the other seven, i.e. it degrades silently the day row 8's content changes and nobody re-runs the check | 2 of 2 rejected (wrong kind and owner) |
| B, uncorrected | 7 of 7 (invalid `kind:` field on every one) | N/A — B does not reach this row | 2 of 2 rejected if extended there |
| B, corrected (§2.1's ruling) | 0 of 7 | correctly not extended to it, at `e56d038`; correctly extends to it automatically at whatever tree its `Decision:` lines are filled, because §2.1 is a predicate over content, not a list | correctly not extended to it |
| C (disclosed) | 7 of 7 | 1 of 1 (would also leave this one stranded, though it has no decision to strand yet) | 2 of 2 |

Reading B, corrected, is what §2.1 rules. Readings A and C are priced out on cells that exist
and say otherwise (A) or say nothing supports the exemption (C, on step 1 alone after the
correction) — neither reaches the "no cell to read from" halt, because in both cases a cell
governs and points the other way.

## 5. Revision history — what changed under review, and why

Filed once as an unauthoritative draft while §1 authority had lapsed (§ "Authority" above), then
revised twice against the coordinator's review before this filing:

1. **Citation correction**: `:281` ("nothing exempt") was cited as rejecting reading C; its own
   scope is the citation rewrite, not document assignment. Struck as support; C's rejection now
   rests on `:276` alone (§2.1(f), §4).
2. **Population correction**: the original draft ruled on three named files. Reconciled against
   an independently-derived, code-based sweep (nine files) and a text sweep run here
   (twenty-three files); the seven-file population in §1 is the union, corrected for one file
   whose name matches the predicate and whose content does not (§2.2) — the "member that
   breaks the rule's implicit type," found by reading the file rather than trusting its title.
3. **Embedded-append case**: confirmed against `### 6.3`/`### 6.4`, appended to the delegation
   record after the first draft and read directly at `e56d038` (§2.3).
4. **Dated-absence correction**: §2.2's exclusion of `w37-6-maintainer-decisions.md` originally
   read as a property of the file ("keeps the shipped default," stated without a tree). It is
   in fact a property of one tree — its `Decision:` lines are blank *at `e56d038`*, not
   permanently — and the file is the one member of the seven-plus-one this ruling names whose
   membership is expected to change, since it exists so the maintainer can fill those lines in.
   §1's introduction now states once that §2.1's predicate is evaluated at migration time
   against whatever tree `migrate` runs on, never frozen at the tree a ruling happened to read;
   §1's table, §2.2, §3 and §4's rejection table are re-worded to name `e56d038` explicitly
   rather than let a true-then statement be read as an always. The exclusion itself is
   unchanged and was not re-litigated — only how it is stated.

## Acceptance Standard

The violation this record must make detectable: **a document whose content is the maintainer's
own decision, filed in `docs/plans/` without a `## Ruling N` heading, migrating with a family,
owner, or field the standard's own cells do not support — or a document whose title matches
that description while its content does not, migrated as though it did.**

### Acceptance — the violation that must become detectable

1. *Violation: any of the seven files in §1 stamped `family: plan` at migration.* The
   predicate in §2.1 must route each to `family: ruling`, `owner: maintainer`.
2. *Violation: a `kind:` field of any value present on any of the seven's stamped header.*
   `RL.md:8` forbids the field on this family outright; `audit-docs.py` check 30 (unknown
   field) must red on one if a header carries it.
3. *Violation: the two handovers reclassified by this ruling.* They stay
   `PL- kind: handover, owner: executor`, untouched.
4. *Violation: `2026-09-03-w37-6-maintainer-decisions.md` stamped `owner: maintainer` while its
   `Decision:` lines are still blank at the tree migration runs against — **or** stamped
   `owner: planner` after a dated correction has filled them in, on the strength of `e56d038`'s
   reading rather than a fresh check.* §2.2 rules the disposition follows the file's content at
   the migration tree, not this ruling's own reading of it in the past; either direction of
   staleness is the violation.
5. *Violation: this predicate applied by hardcoding seven filenames and nothing else, silently
   missing `2026-08-30-nt-0012-0013-0014-adoption.md`'s own embedded rulings or any later
   maintainer-decision document at the real migration tree.* §2.1's rule is stated as a
   predicate for this reason.
6. *Violation: `### 6.3`/`### 6.4` split out of the delegation record into separate documents
   at migration, or the delegation record stamped anything other than one `RL-` document.*
   §2.3 rules they stay embedded in the one document.
7. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
