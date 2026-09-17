---
id: RL-859
family: ruling
title: the remainder splits, and the split is the answer
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-algorithm-pin-maturity.md
---

# The `rating_algorithm` remainder: what is RL-856 conformance and what is a new decision (2026-08-29)

**What this is.** A scope question put by the lead against
[`RL-00870-r8-is-ratified-as-applied-and-rl-856-is-not-fully-discharged-rating-algorithm-is-rate-table-s-stranded-list-mate.md`](RL-00870-r8-is-ratified-as-applied-and-rl-856-is-not-fully-discharged-rating-algorithm-is-rate-table-s-stranded-list-mate.md) RL-870 —
*is the `rating_algorithm` remainder inside RL-856's existing scope, or does it need its own
ruling?* It carries **RL-859**, a **correction to RL-870's own instruction**, and the
discharge of register row **F32**, which names this role as the owner of a correction to
RL-882.

**Numbering continues at 28.** Nothing here reuses a number ([`CLAUDE.md`](../../CLAUDE.md) §5).
**Mints no `FR-`/`NFR-`/`OQ-` id and no error code, and edits no specification and no frozen
plan.** Read against `origin/main` at `24b537d`, with `HEAD` identical.

**The three facts the question was put with were re-verified here rather than adopted**, because
`main` moved three times between the question and this record (#405, #406, #407):
`backend/src/app/platform/rating_versions.py:271` returns `ResolvedArtifact(status="approved", …)`;
`RatingAlgorithmRow` (`backend/src/app/db/models.py:1920`) contains zero occurrences of `status`;
and `compile_bundle`'s `all_refs`
(`packages/pricing-core/src/pricing_core/rating/compile.py:439-444`) lists rate tables, models,
reference tables and custom objectives, omitting `algorithm_ref`. All three hold.

---

## RL-859 — the remainder splits, and the split is the answer

**Ruled: it is two things, one inside RL-856 and one not. Only the second needed a ruling, and
ruling it on the merits changes what should be built.**

### Half A — the hardcode is RL-856 conformance, not an extension of it

RL-856's acceptance test reads, verbatim: *"**The ruling is overridden** if a build reports
`"approved"` for an artifact whose row has no status column."* That sentence quantifies over
artifacts. It never said "rate tables", and an acceptance test is precisely the instrument that
fixes a ruling's reach — that is what it is for.

So `rating_algorithm` was **inside RL-856 from the day it was filed**. Nothing new was decided
when RL-870 named it, and nothing new is decided now: the executor implements it as conformance
with an already-merged ruling, and no fresh decision record gates it.

**A correction to my own RL-870 while I am here:** it called this *"extending RL-856 rather
than reopening it"*. For this half that is wrong in a small way worth fixing, because it invites
exactly the question the lead asked — it was not an extension at all, it was a conformance finding
against a ruling whose acceptance test already covered the case.

### Half B — whether the algorithm is checked at all is a separate question, and a spec-versus-code one

This is not RL-856's subject. RL-856 decided *what a resolver branch reports*; whether
`compile_bundle` reads that report for the algorithm pin is a different question, with a different
requirement behind it (FR-240 clause (2) and FR-20, not FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236), a different
workstream (WK-669's, tracked as F-W9-3 at [`../findings/register.md`](../findings/register.md)`:25`), and
consequences for a pin kind that has nothing to do with rate tables.

**RL-870 asserted it rather than deciding it.** Its grounds were a sequencing argument — *"fixing
either alone is worse than fixing neither"* — which is a true observation about ordering and not a
decision on the merits. So this half did need its own ruling, and the lead was right to ask.

**Ruled, and this is a `CLAUDE.md` §0 question: the code is the wrong side.** FR-237 makes the
Rating Algorithm version a pin; FR-240 clause (2) requires *"all references resolvable and at a
sufficient maturity (FR-20)"*; and `compile_bundle`'s own docstring already claims *"the pins
resolve to `approved` or better (FR-20)"*. Four of five pin kinds are checked. The docstring is
right about the intent and the code is short one kind.

### The shape — and it is **not** the one RL-870 wrote

**RL-870's literal instruction was to bring the algorithm "into the same maturity loop as the
other four pin kinds". Taken literally that is a defect, and it is corrected here.**
`version.algorithm_ref` is already resolved at `compile.py:430`, and its payload is already written
into `payloads` at `:438`. Adding it to `all_refs` would call `resolver.resolve()` on it a **second
time** — a redundant database round trip on the compile path — and write its payload twice. That
instruction was written from the requirement's shape rather than from the function's, which is the
error `docs/plans/README.md` convention 1 exists to catch.

**The ruled shape instead:** check the algorithm's maturity **at the point it is already resolved**,
immediately after `compile.py:430-431`, keyed on the ref's own type against the same
`_MATURITY_CHECK_EXEMPT` set (`:299`) the loop uses at `:447`. One resolve, one check, no second
traversal.

And **`rating_algorithm` joins `_MATURITY_CHECK_EXEMPT`** — but note *why*, because the ordering
matters and the alternative was tempting: it must join **together with** the check above, never
before it. A member of an exemption set that nothing reads is a declared-and-inert control, which
is the defect `06` FR-367 names in terms — *"adding a member now that nothing checks would
recreate the exact defect §4.1 records"* — and this repository's closure records already list two
instances of it.

**So the two changes that look as though they cancel do not.** Adding a check and immediately
exempting the only type it covers leaves today's behaviour identical, and that is the point: it
converts a silence into a declared exemption with a tripwire, the same conversion RL-856 made for
`rate_table`. The payoff is deferred and real — when a `status` column arrives on
`rating_algorithms`, the tripwire fires, the exemption is removed, and **the enforcement is already
there to start working**. Without the check, removing the exemption would do nothing and the gap
would persist silently past the moment it began to matter.

### What the executor builds, after Task 1.4

1. `rating_versions.py:271` returns the `"no_maturity_concept"` sentinel instead of `"approved"`.
2. `rating_algorithm` joins `_MATURITY_CHECK_EXEMPT` (`compile.py:299`), with its own docstring
   line recording that `06` makes **no** governance claim about a Rating Algorithm.
3. A maturity check on `resolved_algorithm` immediately after `compile.py:430-431`, keyed on the
   ref's type against that set — **not** an addition to `all_refs`.
4. A tripwire asserting `RatingAlgorithmRow` has no `status` column, mirroring
   `test_rate_table_version_row_has_no_status_column`.

All four land together, for RL-870's sequencing reason, which stands even though its shape did
not.

**No `OQ-`, and this is the substantive difference from `rate_table`.** `06` mentions Rating
Algorithm six times — a role-assignment scope (§2, FR-345), a `risk_tier` carrier (FR-365),
§4.4's dossier section list, and OQ-636 — and never as approval-bearing; it is absent from §2's
Governed Artifact enumeration (re-checked at `24b537d`) and from §3.3's evidence table. There is no
`06`-versus-`03` contradiction here, so nothing is open and the exemption is simply true rather
than provisional. `OQ-620` covers Rate Table Version only and should not be widened to cover
this.

**Acceptance test — the violation that must become expressible.** Today no test can say *"a Rating
Version compiled against an algorithm nobody approved"*, because nothing reads the algorithm's
maturity at all. After this the expressible violation is a resolver reporting a non-mature
algorithm status and `compile_bundle` accepting it — writable the moment the check exists, and
red-on-arrival the day the exemption is removed without a real status to read. **This ruling is
overridden** if a build resolves `version.algorithm_ref` twice, or adds `rating_algorithm` to
`_MATURITY_CHECK_EXEMPT` without the check that reads it.

---

## Correction to RL-882, discharging register row F32

**F32 is right and my RL-882 was wrong.** F32 ([`../findings/register.md`](../findings/register.md)`:38`)
records that RL-882's acceptance-test item 1 claimed RL-876's `load_bundle` purity property
*"currently lives in a ruling and in no acceptance block anywhere"* and *"becomes expressible for
the first time"* in Slice 2. Verified independently rather than adopted:
[`../plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](../plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)`:1078-1080` is an
**Acceptance** block line, filed earlier the same day, reading *"`load_bundle` is pure with respect
to the cache (RL-876): consults no cache, registers itself in no global, starts no background
task. `lint-imports` staying green is the mechanical half"* — and naming a mechanical half implies
a behavioural half already owed. `packages/pricing-core/tests/test_rating_runtime.py:259`
(`test_load_bundle_is_pure_with_respect_to_any_cache`) then shipped with Task 1.3 in PR #406.

**Both halves of the claim were false**: the property was already in an acceptance block, and it was
discharged in Slice 1 rather than becoming expressible in Slice 2. The diagnosis that generalises:
I searched my own rulings and the frozen scoping plan for the property and did not search the
**leaf** plan's Acceptance block — which is where an executor's obligations actually live, and which
`docs/plans/README.md` convention 5 already warns is the half that gets implemented while the
narrative is the half that gets read. The convention was written about a plan author applying a
ruling; it applies just as well to a ruling author checking whether one is already applied.

**Two consequences, one of which matters for Task 2.1.** RL-882's other acceptance item — the
degraded read — is untouched; **only item 1 is withdrawn**. And Task 2.1 must not re-implement the
purity test as new work: it is in the tree and passing.

**Recorded here rather than by editing RL-882**, because `docs/plans/README.md` permits no such
edit — *"Do not edit a filed plan to agree with today's repository"*, its one exception being
address repair. F32's remedy line asks for the premise to be corrected; a dated sibling is the only
form that request can take, and it is the treatment RL-887 gave a wrong claim of mine before.

---
