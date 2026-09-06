---
id: FD-1020
family: finding
title: 63 in-scope files cannot carry a header, and their custody is an exemption rather than a sidecar
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F83.md
---

# F83 — 63 in-scope files cannot carry a header, and their custody is an exemption rather than a sidecar

**Raised** 2026-09-02 by the lead, from the gap-2 derivation. **Ruled the same day by the
maintainer.** Work item **W37-5c**, scope item 3. Phase 2.

## The population, measured

**63 tracked files in RFC-937's stamp scope cannot hold a YAML front-matter header at all.**

| | Count | Why |
|---|---|---|
| `docs/contracts/**.json` | **59** | JSON has **no comment syntax**. Prepending `---` … `---` produces a file that is not JSON; `json.load`, the OpenAPI toolchain and `frontend/src/api/generated`'s generator all fail at parse |
| `docs/contracts/**.yaml` | **1** | Front matter ahead of `openapi: 3.1.0` breaks the document for the same reason in a different grammar |
| Unparseable vendored `SKILL.md` manifests | **3** | `CLAUDE.md` §12: **vendored files stay as upstream wrote them.** Two carry an upstream `author:` field the closed field set refuses; a third does not parse at all |
| **Total** | **63** | |

**The one `.md` file under `docs/contracts/` is deliberately not in this set** — it can carry a
header, so it is stamped like any other markdown document. The exemption is scoped to the files
that physically cannot, not to the directory.

## Why this is not a choice about effort

The maintainer's gap-2 ruling specified *"the generator emitting the header so regeneration
doesn't strip it"*, with a fallback: *"if that's a bigger change than a `generated: true`
exemption in check 35, say so and I'll take the exemption."*

**It is not a bigger change; it is a format impossibility for 60 of the 63.** No amount of
generator work makes a JSON file carry front matter. Reported on that basis, and the fallback
taken.

## The decision, and the option not taken

**Ruled: exemption.** A `generated: true` exemption in check 35 for the contracts, and an
exempt-by-path entry for the three manifests.

**A sidecar was the alternative and is recorded here because it was rejected on judgement rather
than on merit.** One manifest carrying header fields beside the files that cannot hold their own
would serve both populations with a single mechanism, and would keep all 63 files owned and
machine-readable. It was declined because it introduces a new convention, a parser change, and a
rule for keeping sidecar and file in step — inside a **precondition** slice, which is the kind of
scope growth that put W37-6 where it is. **If the unstamped population ever needs machine-readable
ownership, the sidecar is the design to reach for, and this is the record that it was considered.**

## Two conditions on the exemption — the maintainer's, and both are enforceable

1. **Every entry cites its reason and the ruling that permits it.** An exemption list whose
   entries carry no justification is indistinguishable from a list of things nobody got round to.
2. **The exempt-by-path set is itself checked: the count of unstamped in-scope files must equal
   the exempt list.** This is the condition that matters. Without it the list is a hole that grows
   silently — every future unstampable file lands in it and nothing reports the growth. With it,
   an addition is visible as an arithmetic failure the moment it happens.

**Condition 2 is RL-985's property applied to an exemption rather than to a census**, and it
inherits RL-985's reasoning: the check must **name** the files that are unstamped and not
exempt, never merely compare two totals. Two errors that cancel would pass a total-only check —
see `.claude/skills/docs-audit` §*"a total validates the total, and nothing else"*, added the same
day after exactly that failure.

## Custody, which is the point of filing this

**Per [`RFC-778`](../rfcs/RFC-00778-seven-deferred-items-with-no-durable-custody.md), a deferred item
with no owner is not deferred, it is lost.** This finding exists so the 63 unstamped files have a
**named home** rather than an entry in an allowlist nobody revisits. The exemption is the
disposition; this record is the custody.

## Falsifiable

Discharged when check 35 carries the exemption with per-entry reasons, **and** the equality check
of condition 2 is implemented and proven on deliberately broken input — an unstamped in-scope file
absent from the exempt list must red. Re-opened if the exempt list ever grows without a
corresponding finding, which is the event condition 2 exists to make impossible to miss.

## Dated correction — 2026-09-02, after filing: the population is 65, not 63

**Superseded by this section**, named rather than edited: this record's title, the sentence
*"63 tracked files in RFC-937's stamp scope cannot hold a YAML front-matter header at all"*
under **The population, measured**, that table's `Total` row, and the three later sentences
reading *"60 of the 63"*, *"all 63 files"* and *"the 63 unstamped files"*. The corresponding
claim cell and disposition in `docs/findings/register.md` carry the same figure and the same
correction, annotated in place per that file's own rule.

**Two tracked files in the ruled stamp set were never counted**, both satisfying this record's
own stated criterion — a format with no comment syntax cannot carry front matter:

| | Why it qualifies |
|---|---|
| `docs/process/delivery-process.core.json` | `CLAUDE.md` §15's machine-readable process extract. Front matter breaks `json.load` for exactly the reason the 59 contracts schemas do |
| `docs/research/file-census-5ef559d.csv` | CSV has no comment syntax either |

So 60 + 2 non-`.md` files, plus the 3 unparseable vendored manifests, is **65**.

**The defect was not arithmetic, and naming it correctly is the point of this correction.** The
lead measured `docs/contracts/` and the vendored manifests — the two populations already in mind
when the finding was written — and reported their union as *the unstampable files*, never
enumerating the stamp set the rule ranges over. The corpus was chosen to fit the answer rather
than derived from the predicate. This is the failure class `F85` describes, committed by the
author of `F85` four hours after the maintainer amended `CLAUDE.md` §13 to require that a count
carry **the predicate it counted with**.

**Measured, with its predicate.** At `7186dca`, `git ls-tree -r --name-only 7186dca -- docs/ |
grep -v '\.md$'` returns **62** — the 60 under `docs/contracts/` and exactly the two above,
nothing else. The figure is stable across `e63332c`, where the executor first measured it, and
`544b90c`: `#629` touched no file under `docs/`.

**Status of the two new entries.** They ship on the register flagged in their own `ruling` cell
as *found by this check, not in F83's ruled population, awaiting ratification*. An entry that
declares it has no ruling satisfies condition 1 honestly; one that borrowed a citation would not.
Deleting the two tuples reverses this if the maintainer rules the exemption narrower than its
criterion.

**This is condition 2 working on its first day.** The maintainer's second condition was that the
exempt-by-path set is itself checked, and the first thing that check did on the real corpus was
name two files nobody had counted. A list that could not grow silently did not.
