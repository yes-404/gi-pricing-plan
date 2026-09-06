---
id: FD-1006
family: finding
title: `audit-docs.py` check 28 has no plan-kind test for a ruling record
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F68.md
---

# F68 — `audit-docs.py` check 28 has no plan-kind test for a ruling record

Evidence essay for the register row self-named `(F68)` in `docs/findings/register.md`. The
finding: `check_plan_acceptance_standard` (check 28) classifies every file in `docs/plans/`
as "the plan" `writing-plans` produces unless its name ends in one of four excluded
suffixes — none of which covers a ruling record, a real, precedented, still-current kind of
file filed in that same directory. Every existing instance is shielded from the defect only
by predating the check's own cutoff date, which is exactly the "boundary metric reads zero
by construction" shape: the check has never actually been exercised against a ruling
record, not because it handles the case, but because no ruling record had been filed since
the cutoff until tonight.

## How it surfaced

The lead filed `docs/rulings/RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md` — a
ruling record in the shape of the existing precedent `2026-08-30-nt-0017-maintainer-
decisions.md` — and check 28 failed it, requiring an "Acceptance Standard" section the file
had no reason to carry. The lead did not patch the check (a shared gate, and RFC-937's own
migration rewrites this area), and instead added a genuine `## Acceptance Standard` section
to the record, stating there why it exists and that the classification defect is filed
separately. That file did not exist in this session's pinned tree (`89dd2b1`) at the time of
this filing, so its content is not independently re-verified here; the classification defect
itself is verified directly against the shipped check, independent of that file.

## The code, read directly (`scripts/audit-docs.py` at `89dd2b1`)

```python
_PLAN_KIND_EXCLUDED_SUFFIXES = ("-ledger.md", "-final-review.md", "-verified.md", "-handover.md")
...
PLAN_ACCEPTANCE_STANDARD_CUTOFF = date(2026, 8, 31)
...
def check_plan_acceptance_standard() -> None:
    """28. A filed plan (the `writing-plans` file kind) states an explicit acceptance standard.
    ...
    Scope is the plan *kind* only — the file `writing-plans` produces, discriminated by the
    four documented suffixes in `docs/plans/README.md`, never by guessing at content. Widen
    it past that and it reds on every future ledger, ruling record or handover file, which
    the "no warn phase" design above cannot excuse (RL-906 §2's own warning about a check
    that guesses).
    """
    for f in sorted(plans_dir.glob("*.md")):
        name = f.name
        if name == "README.md":
            continue
        if name.endswith(_PLAN_KIND_EXCLUDED_SUFFIXES):
            continue
        ...  # every other dated file is treated as "the plan" and must carry an
             # "Acceptance Standard" heading with content if filed >= the cutoff
```

The docstring's own stated intent — scope discriminated by "the four documented suffixes in
`docs/plans/README.md`," explicitly **naming "ruling record" as one of the things widening
past plan-kind would wrongly catch`** — is contradicted by the code's own mechanism: the
`for` loop's only exclusions are the four suffixes above, so anything else, ruling records
included, falls through to the branch that requires an Acceptance Standard heading.

## `docs/plans/README.md`'s own four kinds — verified, no fifth exists

```
## The four kinds of file

| Suffix | Written by | Holds |
|---|---|---|
| *(none)* | `writing-plans` | The plan — goal, architecture, tasks, bite-sized steps |
| `-ledger` | `subagent-driven-development` | What execution actually did, task by task |
| `-final-review`, `-verified` | a review pass | Findings against a finished branch, and their verdicts |
| `-handover` | a session ending mid-work | State a successor session needs to resume |
```

A ruling record has no suffix of its own in this table — by the table's own scheme it falls
under `*(none)*`, i.e. "the plan," the exact misclassification the docstring says the check
must not make.

## The precedent is shielded by date, not by correctness

`docs/rulings/RL-00914-rfc-898-the-maintainer-s-three-policy-decisions-recorded-2026-08-30.md` exists at `89dd2b1`, is a ruling
record in every respect that matters here (three maintainer policy decisions, recorded;
title "# RFC-898 — the maintainer's three policy decisions, recorded (2026-08-30)"), carries
no suffix from the excluded list, and is filed 2026-08-30 — one day **before**
`PLAN_ACCEPTANCE_STANDARD_CUTOFF` (2026-08-31). It is therefore counted in check 28's
`legacy` bucket and never reaches the Acceptance Standard test at all, regardless of whether
it has one (it does not). RFC-937 §5.2 independently corroborates that this is not an
isolated file: its own migration table counts **27 rulings files** currently living under
`docs/plans/` bound for a new `rulings/` family — 27 instances of exactly this shape, every
one of them pre-cutoff and therefore untested by check 28 for the same reason.

## A positive content-based test was considered and does not cleanly generalise

Some existing multi-ruling records in `docs/plans/` (per RFC-937 D9, "legacy multi-ruling
records") carry `^#+ Ruling [0-9]+` headings, which `git grep -n '^#+ Ruling [0-9]+'
89dd2b1 -- docs/plans` matches, and which could look like a ready-made positive signal for
"this file is a ruling record, not a plan." It is not general enough: the precedent file
`2026-08-30-nt-0017-maintainer-decisions.md` uses no such heading — its own sections are
"1. The decisions," "2. What these decisions do not settle," "3. Sequencing that follows
from Q3" — so a check keyed on `## Ruling N` would still misclassify it. There is currently
no single textual marker common to every ruling-shaped file in `docs/plans/`; a reliable
positive test would require first establishing a naming or front-matter convention for the
kind, which is a larger change than patching this one check and is what RFC-937 already does
by giving rulings their own `RL-` family and directory rather than a suffix inside
`docs/plans/`.

## Reproduction — the mutation that must become detectable

```bash
$ cat > /tmp/ruling-repro.md <<'EOF'
# A ruling-shaped record with no acceptance standard
EOF
$ mv /tmp/ruling-repro.md docs/plans/2026-09-02-ruling-repro.md
$ python3 scripts/audit-docs.py   # fails check 28: "no \"Acceptance Standard\" heading"
```

Today: a ruling record filed in `docs/plans/` on or after 2026-08-31, with no suffix from
the excluded list and no Acceptance Standard section, fails check 28. It should not — the
check's own stated scope is plan-kind only, and this is not a plan. Filed for the record
without applying it to the tree (no such file is added by this finding).

## Scope of this finding

- **Not fix-before-close.** Nothing live is failing today; the one real instance
  encountered was worked around in the record itself rather than by patching the shared
  gate.
- **Superseded, not merely fixed, by RFC-937's own migration.** Per RFC-937 §8 Sequencing,
  it is **S2 — the migration PR**, not S1, that rewrites `audit-docs.py`'s "parsers and
  roots" (S1 is "instruments, no moves" — new tooling only, no behaviour change to existing
  checks). Post-S2, rulings live in their own `docs/rulings/` family entirely outside
  `docs/plans/`, which removes the misclassification by construction rather than by adding a
  fifth suffix to a blocklist that would itself be thrown away at the same step.
- **The live window is real.** Between now and S2 landing, any further ruling record filed
  in `docs/plans/` on or after 2026-08-31 needs the same manual Acceptance Standard
  workaround the lead applied, or it fails the gate incorrectly.
