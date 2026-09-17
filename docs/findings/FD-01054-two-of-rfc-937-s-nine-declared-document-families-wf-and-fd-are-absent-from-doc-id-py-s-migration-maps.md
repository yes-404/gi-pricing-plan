---
id: FD-1054
family: finding
title: two of RFC-937's nine declared Document families, `WF` and `FD`, are absent from `doc-id.py`'s migration maps
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-03
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F95.md
---

# F95 — two of RFC-937's nine declared Document families, `WF` and `FD`, are absent from `doc-id.py`'s migration maps

**Filed 2026-09-03 at `735c828`, on the lead's direction, under the W37-6 §1 delegated
authority.** Id allocated by the decision-maker and verified free before use (`F95` unused
under `docs/audit/findings/`; next `## Ruling N` number, unrelated, is separately tracked).
Work item **W37-6**, phase 2.

## The population, counted directly against the table

**RFC-937 §1.2 declares nine Document-kind rows** (`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`,
lines 33–41): `WF` (Workflow, line 33), `ADR` (34), `RFC` (35), `PL` (36), `LG` (37), `RL`
(38), `RS` (39), `CR` (40), `FD` (41).

**`_DOCUMENT_FAMILY_DIR` (`scripts/doc-id.py:2628-2631`) implements seven**: `ADR, RFC, PL,
RL, CR, LG, RS`. **`WF` and `FD` are both absent.**

**`_MIGRATE_TEMPLATE_FILENAME` (`scripts/doc-id.py:870-872`) has the identical gap**: `ADR,
RFC, PL, RL, CR, REFERENCE, LG, RS` — eight entries (`REFERENCE` is there by design, per the
constant's own comment: it is stamped in place and never moved, so it is deliberately absent
from `_DOCUMENT_FAMILY_DIR` while present here). `WF` and `FD` are absent from both tables,
not just one — a document of either prefix cannot be placed **and** cannot be rendered.

**Both families already have a template.** `docs/_templates/WF.md` and `docs/_templates/FD.md`
both exist (`ls docs/_templates/`, 13 files, all named). The declaration and its template are
not the gap; the migration code that would read them is.

**Worth a sentence on its own, because a reader will ask how nine became seven without anyone
noticing: `WF` is not a row in an obscure corner of the table.** It is the *first* Document
row — the one carrying the bolded `**Document**` kind marker that opens the group — and it
was still missed, from the table itself, by two independent readings before this one (a
relayed count of eight, corrected once already). The omission is not a matter of a small
print row easy to miss.

## The two absences do not fail the same way, and only one is visible today

**`FD` shows up in the numbers `classify_docs_files` already reports.** A disposable snapshot
at `e56d038`, `migrate()` run to completion and then `doc-id.py check --classify` run against
the result (the auditor's instrument): total **457** matches `git ls-files docs/` exactly, but
**110** of those classify `"none"`. **45 of the 110 are under `docs/audit/`**, which `RFC-937
§4` step 4 (`:279`) requires dissolved — *"Move into the family directories; dissolve
`docs/audit/`…"* (the clause's own remainder, unrelated to this population, is not quoted
here so this record does not itself become a fifth reviewed member of
`tests/test_notes_move_citations.py`'s `_SPECIFICATIONS_OF_THE_OLD_PATH`) — and is not,
because among other gaps
nothing discovers `docs/audit/findings/F*.md` to route the essays into `docs/findings/`.
(The other 65 of the 110 — `docs/contracts/` and two whitelisting gaps in
`classify_docs_files` itself — are a separate, already-identified defect in the counting
function, not this one; noted here only so a reader summing `45 + 65 = 110` does not
conflate the two causes.)

**`WF` shows up in nothing, and that is the more dangerous shape.** `docs/workflows/` is
already `WF`'s declared home (§1.2, `:33`) both before and after migration — no move is
needed — and `_CLASSIFY_FAMILY_BY_DIR` already carries `"workflows": "workflow"`
(`scripts/doc-id.py:465`), so the five `wf-0N-*.md` files classify correctly today and would
continue to. **No `_discover_workflows` function exists** (checked against the full list of
fourteen `_discover_*` functions in `scripts/doc-id.py`; none reaches `docs/workflows/`), so
a real `migrate()` run leaves all five files completely untouched — no `id:` header, no
`WF-nnnn` number, no stamp of any kind — while reporting nothing wrong, because the file the
classifier already expected to see is still exactly where it expected it. **This is F84's own
shape** ("a guard that aborts is a gap that announces itself; a population no census covers is
a gap that does not," `RFC-789`'s asymmetry) **in the one family whose gap the visible `none`
count cannot catch**, because nothing about it looks unclassified.

## Why this is filed rather than folded into F84 or left for the citation-rewrite question

Distinct population (`docs/audit/findings/*` and `docs/workflows/*`, not F84's `audit/work/`
and `audit/phases/` READMEs), distinct root cause (two missing map entries in `doc-id.py`
proper, not a missing discovery function reading an existing, otherwise-handled directory
shape), and distinct visibility (one manifests in the acceptance-item-(a) count, one does
not). Checked first, per `RFC-756`/`RFC-779`: no existing register row or finding names
either gap — `git grep -i "classify_docs_files"` and a direct read of every open finding
citing `docs/audit/` or `docs/workflows/` in the register turned up none. **F88 limb 2** is
adjacent (the phase register's own discovery gap, one file, already open, owned by W37-6) but
is a third, independent cause and is not folded in here for the same reason.

## Status

**Both gaps are, as of this filing, being closed inside W37-6's own build** — `FD` and `WF`
added to `_DOCUMENT_FAMILY_DIR` and `_MIGRATE_TEMPLATE_FILENAME`, `_discover_findings` over
`docs/audit/findings/F*.md` with `owner: auditor` (§1.6) and `was:` per RFC-937's own worked
example (`:269`, `F27` → `FD-0nnnn-rating-shapes.md`, register row `was: F27`), and
`_check_every_document_draft_is_placeable` proven red on an `FD` draft before the fix lands.
`WF`'s own discovery is not yet named as owned; raised here so it is not lost once the more
visible `FD` half is fixed and the `none` count reads clean without it.

## The citation-form residue — ruled, not open

**Whether `F`-prefix citations rewrite to `FD-<nnnnn>` in this run is decided, and is not this
finding's to reopen.** The maintainer, 2026-09-03, on the deferral: *"I'll take the deferral
if the essays get their ids and paths now; a half-migrated family is what F84 was"* — met, and
then, on landing the rewrite itself with the run: *"I've already priced that and it doesn't
return to me."* **Ruled: the essays get `FD-<nnnnn>` ids and paths in this run; the bare
`F<n>` citation-form rewrite across prose is deferred to W37-11, with the resolver accepting
`F<n>` as an interim alias for the essay's `FD-` id until that rewrite lands.** Relayed to the decision-maker via the lead and recorded here as
the dated artifact `CLAUDE.md` §12 requires — no prior written record of this specific
instruction exists to cite instead. Not priced, not recommended on, and not reopened by this
filing.

## Falsifiable

Discharged when `_DOCUMENT_FAMILY_DIR` and `_MIGRATE_TEMPLATE_FILENAME` both carry `WF` and
`FD`, a `migrate()` run over the real corpus places every `docs/audit/findings/F*.md` and
every `docs/workflows/wf-0N-*.md` as a stamped draft of the correct family, and
`_check_every_document_draft_is_placeable` — run against a copy of the source with either key
removed — reds naming the missing key, proving the guard (not silence) is what would catch a
regression.
