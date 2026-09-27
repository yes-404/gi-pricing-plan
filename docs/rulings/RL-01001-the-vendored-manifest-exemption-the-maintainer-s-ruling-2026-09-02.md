---
id: RL-1001
family: ruling
title: The vendored-manifest exemption — the maintainer's ruling, 2026-09-02
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-vendored-exemption-ruling.md
---

# The vendored-manifest exemption — the maintainer's ruling, 2026-09-02

**Raised** 2026-09-02 by the lead, from the gap-2 derivation. **Ruled the same day by the
maintainer.** Work item **W37-5c**, scope item 3. Phase 2.

**Filed late, and the lateness is the reason this record exists.** The ruling was given to the
lead in conversation and acted on immediately — `F83` was filed nineteen minutes later asserting
it, and `#634` built to it — but **it was never landed as a dated artifact.** `CLAUDE.md` §12:
*every decision lands as a dated artifact — a ruling record, an audit record, a plan — never in
chat.* Found by W37-5c's close audit, which observed that `F83` cites a ruling nothing in the
repository quotes, and that
[`../plans/PL-00957-w37-5c-the-slice-decision-and-gap-2-ruled.md`](../plans/PL-00957-w37-5c-the-slice-decision-and-gap-2-ruled.md) still describes the
question as open and has never been amended. **The gap was in the record, not in the decision.**

## The ruling, verbatim

> **Vendored manifests: exemption, as recommended.** Sidecar recorded as the option not taken
> and filed as a register finding so the 63 unstamped files have custody (`RFC-778`), not just a
> list. Two conditions on the exemption: every entry cites the reason and the ruling that permits
> it, and the exempt-by-path set is itself checked.

## What it settles

**An exemption, not a sidecar.** The sidecar design is recorded in `F83` as *the option not
taken*, so it is recoverable if those files ever need machine-readable ownership.

**Custody rather than an allowlist.** `RFC-778` — a deferred item with no owner is not deferred,
it is lost. The finding is the custody; the exemption is the disposition.

**Two conditions, both enforceable, both owed by W37-5c**: every entry cites its reason and the
ruling permitting it, and **the exempt set is itself checked**. The second inherits RL-985's
property — the check **names** the unstamped-and-not-exempt files and never compares two totals,
because two errors that cancel pass a total-only check.

## Two things the ruling's own text no longer matches, recorded rather than silently normalised

**The population is 65, not the 63 the ruling names.** Corrected at `24193dd` with a dated
correction on `F83` and an in-place annotation on the register row. **The quotation above is left
as spoken.** Two tracked files meeting the ruling's own criterion had never been counted:
`docs/process/delivery-process.core.json` and `docs/research/file-census-5ef559d.csv`. **Condition 2
is what found them**, on its first run against the real corpus — the exempt set could not grow
silently, and it did not.

**The exemption does not by itself let a run proceed.** `#634` implements it in **check 35** in
`scripts/audit-docs.py`. The same three manifests are also reached by
`_discover_vendored_skill_manifests` in `scripts/doc-id.py`, which raises `HeaderError` on
`.claude/skills/create-adaptable-composable/SKILL.md:6` and **aborts `migrate()` before its
stamp loop** — verified by execution at `d8d6e3f`. **Two instruments reach one population and
only one consults the register.** Filed as `F88`; noted here because a reader arriving at this
ruling could otherwise conclude the three files are settled for the migration, and they are not.

## Acceptance Standard

**This record is accepted when the ruling it quotes is citable from `F83` and from the
slice decision without either asserting an unquoted authority.** It changes no code and no
disposition; it lands the artifact a decision already acted on should have had.

### Acceptance — the violation that must become detectable

**The violation:** an entry in the exempt set carrying no reason or no ruling, or an unstampable
in-scope file absent from that set. Both are live and both red today —
`_check_unstampable_register` reports the symmetric difference and names every file on each side,
proven at `#634` on seven mutations including the compensating-error case where a dropped entry
and a bogus one leave the totals equal.

*Violation: an `UNSTAMPABLE_EXEMPTIONS` entry constructed without both fields.*

*Violation: a file that cannot carry a header, inside the stamp set, absent from the register.*

*Violation: a decision on this record's subject taken and acted on without a dated artifact —
which is what this record exists to close, nineteen minutes late.*
