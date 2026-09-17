---
id: FD-1055
family: finding
title: a filed ruling that omits the `## Ruling N` heading migrates as `PL-`, `owner: planner`, and nothing catches it
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-03
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F96.md
---

# F96 — a filed ruling that omits the `## Ruling N` heading migrates as `PL-`, `owner: planner`, and nothing catches it

**Filed 2026-09-03 at `origin/main`, on the lead's direction, under the W37-6 §1 delegated
authority, while fixing the same defect in the decision-maker's own two rulings this window.**
Id allocated by the decision-maker and verified free before use. Work item **W37-6**, phase 2.

## The mechanism

`_discover_multi_ruling_files` (`scripts/doc-id.py:1235-1279`) claims a `docs/plans/*.md` file
as one or more `RL-` drafts **only** if it contains at least one heading matching
`_RULING_HEADING_RE` (`:1146`): `^##\s+Ruling\s+(\d+)\s*(?:—\s*(.+))?$` — an H2, the literal
word "Ruling", a bare integer, an optional em-dash title. A file with zero such headings is
invisible to this function and falls through to `_discover_plain_plans`
(`:1878-1906`), which claims every remaining `docs/plans/*.md` file unconditionally: `kind:`
from filename suffix (`else leaf`), `owner:` from `_PLAN_KIND_OWNER["leaf"] = "planner"`
(`:1179-1206`). **A decision-maker's own ruling, filed as a standalone dated record in the
established sibling-record pattern, is stamped `PL- kind: leaf, owner: planner` if it does not
happen to carry that one specific heading form** — regardless of its title, its content, or
how plainly it identifies itself as a ruling.

**No guard catches this today.** `_check_multi_ruling_files_not_silently_unrecognised`
(`:3017-3074`), the census built to name files `_discover_multi_ruling_files` might be
under-matching, keys on `_CENSUS_ANY_RULING_HEADING_RE` (`:3013`):
`^#{1,6}[ \t]+Ruling[ \t]+\S.*$` — any heading level, but still requiring the word "Ruling" to
be the **first** word after the heading marker. A file titled, say, `# W37-6 — RL-1047:
...` does not match this either: "Ruling" is not the first word. The census's own docstring
independently anticipates part of this class — *"RL-996: a standalone ruling file (the h1
case) is `RL-`, not `PL- kind: leaf`"* — but names it as **not yet implemented** ("today it
demonstrably is not one … and no widening has landed") and scopes the described case to a
file whose first heading literally opens with "Ruling", which is narrower than what this
finding measures.

## The population, measured directly

**Two live instances this window, both self-inflicted and both fixed in the same PRs that
introduce this finding**: `docs/rulings/RL-01047-a-document-whose-entire-content-is-a-maintainer-decision-migrates-as-rl-owner-maintainer-no-kind-field.md` (Ruling
98, merged `d1cabe1`) and `docs/rulings/RL-01048-three-docs-audit-files-no-rfc-937-clause-maps-get-destinations-not-a-halt.md`
(RL-1048). Both were verified, not assumed, by running `_discover_multi_ruling_files` and
`_discover_plain_plans` against a temporary copy of each file before and after adding the
heading: zero `RL-` drafts and the file claimed by `_discover_plain_plans` before; one `RL-`
draft (`owner: decision-maker`, the correct default per RL-984) and zero `PL-` drafts
after.

**One pre-existing instance, unrelated to this window's own filings, found while measuring
the above and not yet fixed**: `docs/rulings/RL-01001-the-vendored-manifest-exemption-the-maintainer-s-ruling-2026-09-02.md`
(self-titled *"the maintainer's ruling, 2026-09-02"*, headings `## The ruling, verbatim`,
`## What it settles`, ...) carries no `## Ruling N` heading and no heading whose first word is
"Ruling" either — the identical shape, filed a day earlier by a different session. Not fixed
here: it is outside the two files this window's coordinator named, and its correct heading
text (and thus its correct `RL-` title) is a call for whoever owns that record, not one this
finding makes unilaterally.

**Both readings the two live instances give the same answer**, which is the population's own
strongest evidence: a decision-maker filing a ruling under the sibling-record convention this
window, twice, independently, both times without the one heading form the pipeline actually
keys on — and the file this finding's own author had freshly re-read every clause of RFC-937
§4 step 2 to write was one of the two.

## Why this is a finding, not just two fixes

**The convention is load-bearing and currently enforced by nothing.** Whether a document is a
decision-maker's `RL-` ruling or a planner's `PL-` plan is not a matter of judgment migrate()
applies — it is entirely a function of one regex matching one heading form. A ruling that
reads, verbatim, as a ruling — cites cells, prices alternatives, carries an Acceptance
Standard — is silently reclassified as a plan, with an owner attribution that is wrong by
construction, if the author (human or agent) writes `## Ruled` or `## 2. Ruled` instead of
`## Ruling <n> — …`. Nothing reds. Nothing warns. The `none` count does not move — the file is
claimed, just claimed wrong. This is the same asymmetry `RFC-789` records and F84 already
named for boundary metrics: **a guard that aborts announces itself; a population no census
covers does not**, and this convention has no census over it that a file failing to match the
narrow pattern, while plainly being a ruling by every other signal, is caught by.

## Falsifiable

Discharged when one of two remedies lands, named here rather than chosen, per delegation §1's
own framing (rule the classification, let the build choose the mechanism):

- **A guard** analogous to `_check_multi_ruling_files_not_silently_unrecognised`, but keyed on
  a broader, independent signal that a `docs/plans/*.md` file is ruling-shaped by content
  (an `## Acceptance Standard` section using the load-bearing phrase `ruling-acceptance-item-
  census.py` already matches on, combined with citation-and-pricing language, or a filename
  containing `-ruling` / `ruling-` outside the already-covered date-prefixed multi-ruling
  shape) — proven on deliberately broken input: a file shaped like a ruling but carrying no
  `## Ruling N` heading must be named, not silently claimed as `PL-`.
- **Or**, if that is judged too heuristic to be safe, a **written, checked convention**: every
  dated sibling ruling record must carry the heading, enforced the same way check 28 already
  enforces an `## Acceptance Standard` section on every plan filed after a flag day.

Either way: discharged when a file shaped exactly like `w37-vendored-exemption-ruling.md` —
self-titled a ruling, no `## Ruling N` heading — reds a real check rather than passing
`migrate()` silently as `PL- kind: leaf, owner: planner`.
