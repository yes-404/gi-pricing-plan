# The `rating_algorithm` remainder: what is Ruling 22 conformance and what is a new decision (2026-08-29)

**What this is.** A scope question put by the lead against
[`2026-08-29-w11-ruling-vs-plan-scope.md`](2026-08-29-w11-ruling-vs-plan-scope.md) Ruling 27 —
*is the `rating_algorithm` remainder inside Ruling 22's existing scope, or does it need its own
ruling?* It carries **Ruling 28**, a **correction to Ruling 27's own instruction**, and the
discharge of register row **F32**, which names this role as the owner of a correction to
Ruling 16.

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

## Ruling 28 — the remainder splits, and the split is the answer

**Ruled: it is two things, one inside Ruling 22 and one not. Only the second needed a ruling, and
ruling it on the merits changes what should be built.**

### Half A — the hardcode is Ruling 22 conformance, not an extension of it

Ruling 22's acceptance test reads, verbatim: *"**The ruling is overridden** if a build reports
`"approved"` for an artifact whose row has no status column."* That sentence quantifies over
artifacts. It never said "rate tables", and an acceptance test is precisely the instrument that
fixes a ruling's reach — that is what it is for.

So `rating_algorithm` was **inside Ruling 22 from the day it was filed**. Nothing new was decided
when Ruling 27 named it, and nothing new is decided now: the executor implements it as conformance
with an already-merged ruling, and no fresh decision record gates it.

**A correction to my own Ruling 27 while I am here:** it called this *"extending Ruling 22 rather
than reopening it"*. For this half that is wrong in a small way worth fixing, because it invites
exactly the question the lead asked — it was not an extension at all, it was a conformance finding
against a ruling whose acceptance test already covered the case.

### Half B — whether the algorithm is checked at all is a separate question, and a spec-versus-code one

This is not Ruling 22's subject. Ruling 22 decided *what a resolver branch reports*; whether
`compile_bundle` reads that report for the algorithm pin is a different question, with a different
requirement behind it (FR-RATE-25 clause (2) and FR-OVR-14, not FR-RATE-14..21), a different
workstream (W9's, tracked as F-W9-3 at [`../audit/register.md`](../audit/register.md)`:25`), and
consequences for a pin kind that has nothing to do with rate tables.

**Ruling 27 asserted it rather than deciding it.** Its grounds were a sequencing argument — *"fixing
either alone is worse than fixing neither"* — which is a true observation about ordering and not a
decision on the merits. So this half did need its own ruling, and the lead was right to ask.

**Ruled, and this is a `CLAUDE.md` §0 question: the code is the wrong side.** FR-RATE-22 makes the
Rating Algorithm version a pin; FR-RATE-25 clause (2) requires *"all references resolvable and at a
sufficient maturity (FR-OVR-14)"*; and `compile_bundle`'s own docstring already claims *"the pins
resolve to `approved` or better (FR-OVR-14)"*. Four of five pin kinds are checked. The docstring is
right about the intent and the code is short one kind.

### The shape — and it is **not** the one Ruling 27 wrote

**Ruling 27's literal instruction was to bring the algorithm "into the same maturity loop as the
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
is the defect `06` FR-GOV-39 names in terms — *"adding a member now that nothing checks would
recreate the exact defect §4.1 records"* — and this repository's closure records already list two
instances of it.

**So the two changes that look as though they cancel do not.** Adding a check and immediately
exempting the only type it covers leaves today's behaviour identical, and that is the point: it
converts a silence into a declared exemption with a tripwire, the same conversion Ruling 22 made for
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

All four land together, for Ruling 27's sequencing reason, which stands even though its shape did
not.

**No `OQ-`, and this is the substantive difference from `rate_table`.** `06` mentions Rating
Algorithm six times — a role-assignment scope (§2, FR-GOV-4), a `risk_tier` carrier (FR-GOV-43),
§4.4's dossier section list, and OQ-GOV-4 — and never as approval-bearing; it is absent from §2's
Governed Artifact enumeration (re-checked at `24b537d`) and from §3.3's evidence table. There is no
`06`-versus-`03` contradiction here, so nothing is open and the exemption is simply true rather
than provisional. `OQ-RATE-7` covers Rate Table Version only and should not be widened to cover
this.

**Acceptance test — the violation that must become expressible.** Today no test can say *"a Rating
Version compiled against an algorithm nobody approved"*, because nothing reads the algorithm's
maturity at all. After this the expressible violation is a resolver reporting a non-mature
algorithm status and `compile_bundle` accepting it — writable the moment the check exists, and
red-on-arrival the day the exemption is removed without a real status to read. **This ruling is
overridden** if a build resolves `version.algorithm_ref` twice, or adds `rating_algorithm` to
`_MATURITY_CHECK_EXEMPT` without the check that reads it.

---

## Correction to Ruling 16, discharging register row F32

**F32 is right and my Ruling 16 was wrong.** F32 ([`../audit/register.md`](../audit/register.md)`:38`)
records that Ruling 16's acceptance-test item 1 claimed Ruling 10's `load_bundle` purity property
*"currently lives in a ruling and in no acceptance block anywhere"* and *"becomes expressible for
the first time"* in Slice 2. Verified independently rather than adopted:
[`2026-08-29-w11-1-evaluator-core.md`](2026-08-29-w11-1-evaluator-core.md)`:1078-1080` is an
**Acceptance** block line, filed earlier the same day, reading *"`load_bundle` is pure with respect
to the cache (Ruling 10): consults no cache, registers itself in no global, starts no background
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

**Two consequences, one of which matters for Task 2.1.** Ruling 16's other acceptance item — the
degraded read — is untouched; **only item 1 is withdrawn**. And Task 2.1 must not re-implement the
purity test as new work: it is in the tree and passing.

**Recorded here rather than by editing Ruling 16**, because `docs/plans/README.md` permits no such
edit — *"Do not edit a filed plan to agree with today's repository"*, its one exception being
address repair. F32's remedy line asks for the premise to be corrected; a dated sibling is the only
form that request can take, and it is the treatment Ruling 21 gave a wrong claim of mine before.

---

## Ruling 29 — owners for the seven unowned register findings, and one new row

**Authority, stated rather than assumed.** This discharges a maintainer delegation recorded at
M2 in the lead's rulings file, 2026-08-29 20:30Z, quoting the maintainer verbatim: *"for unowned
findings assign to decision maker to decide"*. **It reached me as the lead's record of the
maintainer's words, not from the maintainer directly**, so it is cited as what it is. It
supersedes M1's carve-out reserving owner assignment to the maintainer. It does **not** touch
`CLAUDE.md` §12's reserved list — the four §13 verdicts and the merge stay the lead's — and
nothing below claims otherwise.

**Decided, not written into the register.** Each owner below is a decision; transcribing it into
`docs/audit/register.md`'s Decision cell is a mechanical edit, and that file is an audit artifact
`CLAUDE.md` §12 has the lead file after an auditor proposes. This is the **fourth** instance of
the charter-grant finding first filed as Ruling 12 (`docs/contracts/`, `docs/roadmap.md`,
`docs/process/delivery-process.md`, now `docs/audit/register.md`) and it is getting expensive to
meet case by case. The wording for each cell is given below so the transcription is a copy, not a
re-derivation.

| Row | Owner | What that owner must do |
|---|---|---|
| **F-W9-3** *(cheap half)* | **W11**, in Ruling 28's follow-up PR | Point `FR-RATE-25`-marked tests at the mechanisms that already run — clauses (1), (2)'s maturity half, (3). That PR is already in `compile_bundle` and its tests |
| **F-W9-3** *(expensive half)* | **The §14 review at W11's close** | Place clauses (4), (5) and (6)'s transitive half on a workstream **or** accept them as not-built with a reason. Validation code for these exists nowhere |
| **F26** `.claude/` CI gap | **W11** | Land the `paths:` filter and the content check **before** the charter amendments R6 is holding for the §14 review, which land into exactly that unwatched directory |
| **F27(c)** + **F29** + **the new row below** | **The §14 review at W11's close**, as **one** gate-coverage item | Decide whether it becomes a workstream row or a maintainer task. One mechanism answers all three |
| **F30** `balance-watch` | **W11** | Delete the `ceiling_meter` import, `CEILING_METER_DIR` and the `live_limit_events` block, and say in `SKILL.md` that the maintainer's manual 5-hour relay replaced them; **and, unconditionally, make the arm banner state whether limit-event detection is active** |
| **F31** roster constant | **The §14 review**, as a fourth charter amendment beside R6's three | Drop `watcher.md`'s derived-roster-state clause. Nothing in the repository needs removing — `update-roster.sh` was always handover-local, so "do not carry it forward" is discharged by not carrying it |
| **F32** Ruling 16's premise | **This role — discharged in this record** | Done above. The register row can be marked resolved with a pointer here |

### Three of these are not pass-throughs, and here is why each is where it is

**F-W9-3 splits because its two halves have different costs and different homes.** The cheap half
is evidence for mechanisms that already run, and Ruling 28's follow-up is touching that exact file
and those exact tests — attaching it there costs almost nothing and is visible to the same
auditor. It does **not** reopen W9: `CLAUDE.md` §13 reserves that to the maintainer, and this is a
missing marker, not a defect in what W9 delivered. The register row is marked resolved with a
pointer rather than W9's close being touched.

**F27(c), F29 and the mypy gap are one finding wearing three coats.** All three are the same
categorical hole the Slice 1 record's third finding already named — *the gate checks documents
against documents and code against code, and nothing checks a document against the artifact it
specifies*. Placing them as three items invites three partial fixes; placing them as one names the
mechanism. **One constraint on that mechanism, derived from Ruling 21 and binding on whoever
builds it:** the error-code check must **compare, not forbid**. An unregistered spec-declared code
is the *designed* state until something raises it — `PlatformError.__init__` says so in its own
message — so a check demanding registration would fire 32 times on day one and be turned off. The
direction that is always an error is the other one: a code in `errors.py` that no spec owns.

**F30's banner fix is unconditional and that is the point.** Whether the meter is superseded is a
real question with a likely answer (the maintainer's manual relay is the live mechanism). But the
row's sharpest observation is independent of it: *a guard that degrades silently is the defect
regardless of which branch is right*. So the banner change lands either way, and the delete lands
if the supersession holds.

### The mypy-coverage gap earns its own row, and it is wider than reported

**Ruled: its own row, not an extension of F26.** F26 is a **path-filter** gap — a PR touching
`.claude/roles/**` gets zero CI of any kind. The mypy gap is a **checker-coverage** gap — CI runs,
and mypy does not look. The two overlap on one directory out of five and their remedies are
disjoint: F26's fix is a workflow filter plus a content check, this one's is `files` plus the
consequences of widening it. Folding them together would produce a row whose fix is two unrelated
changes, and the named half gets fixed.

**Verified, and the report understates it.** `pyproject.toml`'s `[tool.mypy]` sets
`files = ["packages/model-schema/src", "packages/pricing-core/src", "backend/src"]` — three `src`
trees. Uncovered: `.claude/skills/` and tests as reported, **and `scripts/`**, which holds
`audit-docs.py`, `req-coverage.py`, `generate-contracts.py` and `scope-audit.py` — the gate's own
tooling, unchecked by the strictest tool the gate runs. That is the sharpest instance in the set:
the programs that decide whether everything else is correct are the ones nothing type-checks.

**Owner when filed: the §14 review, inside the single gate-coverage item above.** Sizing it is
planning work — `--strict` over test files is not a one-line change — and it is the same family as
F27(c) and F29.

**Filing it is not mine.** A new register row is a finding, which `CLAUDE.md` §12 has an auditor
propose and the lead file; the delegation I am acting under covers owners for rows that exist. So
the row is proposed here with its evidence and its owner already decided, and the lead files it.

**Acceptance test — the violation that must become expressible.** Before this, "a register row
has no owner" was a state the register could sit in indefinitely, and six rows did. After it, the
expressible violation is a row in `docs/audit/register.md` whose Decision cell names no owner —
checkable by reading one column, and `CLAUDE.md` §13's "silence is not a verdict" applied to the
register rather than to a requirement. **This ruling is overridden** if a row is filed with
"unowned" or "owner TBD" in that cell.

---

## Sources — read at `24b537d`

- `packages/pricing-core/src/pricing_core/rating/compile.py:299`, `:428-450`;
  `backend/src/app/platform/rating_versions.py:261-271`;
  `backend/src/app/db/models.py:1920`;
  `packages/pricing-core/tests/test_rating_runtime.py:259`.
- `docs/specs/06-governance.md` §2 `:63-64`, FR-GOV-4 `:81`, FR-GOV-39 `:148`, FR-GOV-43 `:146`,
  §3.3, §4.4; `docs/specs/03-rating-engine.md` FR-RATE-22 `:133`, FR-RATE-25 `:136`;
  `docs/specs/00-overview.md` FR-OVR-14 `:223`.
- `docs/audit/register.md` F-W9-3 `:25`, F32 `:38`.
- [`2026-08-29-w11-1-2-rate-table-maturity-ruling.md`](2026-08-29-w11-1-2-rate-table-maturity-ruling.md)
  Ruling 22, read for its acceptance test;
  [`2026-08-29-w11-ruling-vs-plan-scope.md`](2026-08-29-w11-ruling-vs-plan-scope.md) Ruling 27;
  [`2026-08-29-w11-slices-2-4-rulings.md`](2026-08-29-w11-slices-2-4-rulings.md) Ruling 16;
  [`2026-08-29-w11-1-evaluator-core.md`](2026-08-29-w11-1-evaluator-core.md)`:1074-1082`;
  [`README.md`](README.md) conventions 1 and 5.
