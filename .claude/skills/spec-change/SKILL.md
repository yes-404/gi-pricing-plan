---
name: spec-change
description: Add or modify a requirement, section, or open question in the docs/specs/ specification suite of this GI pricing platform. Use whenever adding an FR-/NFR- requirement, editing a module spec (00-overview through 07-platform), raising or resolving an OQ- open question, or changing a spec's data contracts, interfaces, or tech dependencies. Enforces the append-only requirement-ID rule, the ten-section standard, and both-direction cross-referencing.
---

# Changing a spec

The specification suite is the product of Phase 0 (`CLAUDE.md` §0). Specs are versioned
prose with **permanent identifiers** — the failure mode is not a typo, it is a broken
traceability chain that nobody notices for months.

## Before editing

1. Read `docs/specs/00-overview.md` §2 (glossary) and §7 (module map) — terminology must
   match exactly. A new term goes in the glossary **before** first use anywhere.
2. Read the target spec end to end. Read any `docs/workflows/` file that references it.

## The rules that are easy to break

**Requirement IDs are append-only.** Never renumber. Never insert `42a`/`42b` — that is not
the convention and the audit will not see them. Find the current maximum and append:

```bash
grep -o 'FR-MODEL-[0-9]*' docs/specs/02-modelling.md | sort -t- -k3 -n | tail -1
```

To retire a requirement, mark it `SUPERSEDED BY <id>` in place. Do not delete it.

**A bolded ID *is* a definition.** The audit treats `**FR-PLAT-51**` as declaring that
requirement, so bolding an ID when merely *referring* to it elsewhere creates a phantom
second definition and fails the build. Reference IDs in backticks or plain text; reserve
bold for the row that defines them.

A new ID may sit anywhere in the document — position is free, the number is not. Placing
FR-MODEL-68 next to FR-MODEL-42 because they are topically related is correct.

**Every spec keeps all ten sections** (`CLAUDE.md` §5). If a change adds a tech dependency,
§8 of that spec **and** `docs/skills-map.md` must both change in the same commit.

**Open questions are mirrored in both directions.** An `OQ-` raised in a spec's §10 must
appear in `docs/open-questions.md` with options, trade-offs, a recommendation, an owner and
a status — and nothing may appear in that file that no spec raises. The audit enforces both
directions.

**Never silently pick a side on an open design choice.** Record options and a
recommendation; do not resolve it in prose (`CLAUDE.md` §10).

**A new `OQ-` also goes into `docs/roadmap.md` §10's decision-gate table, in the same
commit.** `audit-docs.py` does not check this — it verifies the spec ↔ register mirror and
stops there — so a question can be raised, mirrored, and still be invisible to the plan.
Four were: OQ-DATA-7, OQ-OVR-6, OQ-PLAT-6 and OQ-MODEL-8 were all raised inside Phase 1a,
all mirrored correctly, and none reached the gate table until 2026-08-15. The `docs-audit`
skill carries the script that catches it; run it whenever you add or decide a question.

**Deciding one is the same edit in three places**, and the register's own precedent shows
the shape: strike the question and prefix `**DECIDED <date>: …**`; leave the options column
as it was, because it records what was believed at the time; rewrite the recommendation
column as the decision, naming the requirements it became; set the status. Then the spec's
§10 row gets the same strike and a one-line pointer to those requirements, and the
obligation itself lands in §3 as an appended `FR-`. **A decision that appends no
requirement usually has not been applied** — it is still a recommendation.

## After editing

```bash
python3 scripts/audit-docs.py          # must print "All checks passed."
```

Then check the decision-gate invariant if you touched open questions — see the
`docs-audit` skill, which covers the checks the script does not.

## Writing style that matches the suite

Say who does what, with what data, and what changes. Numbered requirements, typed fields,
explicit status enums. Avoid "the system should handle…". Small illustrative snippets are
encouraged; full implementations are not.

## Verified

2026-08-15 — Confirmed while recording six maintainer decisions (OQ-MODEL-1, 2, 4, 5, 6, 7)
as FR-MODEL-75..82. The gate-table rule above was learnt from the failure, not from
foresight: the invariant was already broken on `main` when this work started.

2026-08-14 — Confirmed again while recording four maintainer decisions: bolding
`**FR-PLAT-51**` in an open-questions row created a duplicate-definition failure, caught by
the audit. Originally confirmed by applying Track A research findings across four specs: appended
FR-MODEL-68..71, FR-RATE-56..58 and NFR-RATE-13 (400 → 408 requirements) with
`scripts/audit-docs.py` passing before and after. The append-only rule was verified the
hard way: an initial attempt used `FR-MODEL-42a/42b/42c`, which the audit's
`(?:FR|NFR)-[A-Z]+-\d+` pattern silently does not match, so the requirements would not have
been registered at all.
