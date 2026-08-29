# When a merged ruling and a frozen plan's scope line collide, and R8 as applied in PR #400 (2026-08-29)

**What this is.** Two questions, raised by the lead against its own R8 (a lead ruling held
outside the repository, in a handover file, dated 2026-08-29 18:36Z). **Ruling 26** answers the
general question — which artifact governs, and who decides. **Ruling 27** ratifies or overturns
R8 as it was actually applied in PR #400, merged `39cb58e`.

**Numbering continues at 26.** Rulings 1–5, 6–13, 14–15, 16–21, 22 and 23–25 are the six earlier
records'; nothing here reuses a number ([`CLAUDE.md`](../../CLAUDE.md) §5).

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code, and edits no specification.** Read against
`origin/main` at `39cb58e`, with `HEAD` identical.

**One thing this record deliberately does not do.** It does not amend
[`../process/delivery-process.md`](../process/delivery-process.md). The gap Ruling 26 finds is a
process obligation, and this role holds no grant over that file — the third instance of the
charter finding first filed as Ruling 12. It is proposed here and left for the planner to draft
and the maintainer to accept.

---

## Ruling 26 — the general question: precedence was never open; "proceed vs replan" was always the lead's; the real gap is the audit consequence

**The question as put.** *When a merged ruling and a frozen plan's scope line collide mid-slice,
which governs and who decides?*

**Ruled: the question contains three separable questions, two of which are already answered in
writing and one of which is genuinely missing. None of the three is a new precedence rule.**

### Part 1 — which governs is already decided, in `docs/plans/README.md`

Ruling 22's lesson applies to a governance question exactly as it applies to a specification one:
sweep before calling anything open. [`README.md`](README.md) in this directory already says it,
in three places:

- **"A filed plan is a record, not an instruction."** Its whole section under that heading: each
  file *"is frozen at its date. It says what was believed, intended and decided *then* — including
  the parts that later turned out to be wrong"*, and *"if a plan is wrong, the correction belongs
  in the document that is still authoritative."*
- **Convention 4** requires the opposite of deference to the plan: *"Re-check for rulings between
  the evidence sweep and the pull request — premises age faster than literals … a decision-maker is
  ruling concurrently and a ruling is not a commit to the tree your sweep pinned."* Its worked
  example is this very slice — six rulings landing in one hour, one of which *"corrected a defect
  the plan would otherwise have shipped."*
- **Convention 5**: *"Apply a ruling at every site it operates, not only where the plan discusses
  it."*

So **the later ruling governs**, and R8's holding restates existing doctrine rather than making
new law. That is worth saying plainly, because it changes what the lead's error was: R8 did not
invent a precedence rule in a domain that belonged to someone else. It applied one that was
already written down.

### Part 2 — who decides splits three ways, and only one part was ever this role's

| Question | Whose | Authority |
|---|---|---|
| Does the ruling govern the plan's scope line? | **Nobody's — already decided** | `docs/plans/README.md`, conventions 4 and 5 |
| Can this ruling be discharged inside this plan's scope at all? | **The decision-maker's** | It is a statement about what the ruling requires, so it belongs to the ruling's author |
| Proceed on the widened touch-set, or replan the slice? | **The lead's, explicitly** | [`../process/delivery-process.md`](../process/delivery-process.md) §3: the Lead *"reviews plan resolutions and decides replan vs. proceed"* |

**So R8's operative half was in charter.** "Proceed rather than split a two-line exemption into a
second process-slice" is a replan-vs-proceed call, and §3 assigns that to the lead in terms. What
R8 did *not* do was ask the middle question before answering the third — it inferred that Ruling
22 could not be honoured inside Task 1.2's scope, correctly, rather than asking. The correct
sequence was **one round trip, not a different decision**, and the record should say so rather
than book a larger error than occurred. The lead's own framing — *"my error to route rather than
rule"* — is more severe than the facts support in one direction and misses the gap in the other.

### Part 3 — the gap that is real, and it is not about precedence

Conventions 4 and 5 are about **literals and premises** ageing — a signature, an enum member, a
fixture name, a measured figure. A **scope line** is different in kind: it is not a fact that can
be wrong, it is a boundary the auditor audits against. Two things follow that nothing currently
says:

1. **Nothing requires anyone to tell the auditor.** R8's most useful sentence is its own:
   *"The auditor must be told this explicitly, or it will correctly flag `compile.py` in the diff
   as a scope violation against the plan it audits from."* That is true, it was handled by hand
   this time, and the process does not require it. An auditor reading a frozen plan and a diff
   has no way to distinguish a ruling-driven widening from drift — and §3's own role table
   charges the auditor with *"fresh context (no memory of implementation reasoning)"*, which is
   exactly the condition under which the distinction is invisible. (That phrase is the process
   document's, **not** `.claude/roles/auditor.md`'s, which carries no context clause at all — a
   gap worth noting separately, since the charter is what the role is spawned from.)
2. **A widened touch-set leaves no artifact.** `CLAUDE.md` §12 requires every decision to land as
   a dated artifact, *"never in chat"*. R8 is in a handover file outside the repository, which
   `docs/plans/README.md` describes as the class that *"dies with its session"* — the same
   objection §15 makes to an inline brief.

**Proposed, not written** (see the note at the head of this record): an obligation in
`docs/process/delivery-process.md` §11 or §12 that when a ruling widens a slice's touch-set
beyond its frozen plan, the PR description names the ruling, the file it forces, and the plan
line it exceeds — and the audit record notes it as ruling-driven rather than as drift. PR #400
in fact did all of this in its own description; the proposal is only to require what this
instance already did well, which is the cheapest kind of process change to accept.

**Acceptance test — the violation that must become expressible.** Today "this diff exceeded its
plan's scope, and no artifact in the repository says why" cannot be checked, because the *why*
lives in a handover file. After the proposed obligation, the expressible violation is a merged PR
whose diff touches a file its plan scopes out with no ruling named in the description and no note
in the audit record. **This ruling is overridden** if a later record treats a frozen plan's scope
line as binding over a merged ruling — the precedence is `docs/plans/README.md`'s, not this
record's, and a contrary holding would need to amend that file rather than cite a newer ruling.

---

## Ruling 27 — R8 is ratified as applied, and Ruling 22 is **not** fully discharged: `rating_algorithm` is `rate_table`'s stranded list-mate

**Ruled: R8 is ratified.** Every claim it makes about the amendment is true against `39cb58e`,
and two of them are stronger than Ruling 22's literal ask. **And Ruling 22's own acceptance test
is failing on `main` right now**, on a branch nobody looked at.

### R8's claims, verified rather than accepted

- **Exempt by type, not by value.**
  [`../../packages/pricing-core/src/pricing_core/rating/compile.py`](../../packages/pricing-core/src/pricing_core/rating/compile.py)`:299`
  declares `_MATURITY_CHECK_EXEMPT = frozenset({"rate_table"})` beside `_APPROVED_OR_BETTER`, with
  a docstring citing FR-OVR-14, `06` §2 and `OQ-RATE-7`; the gate at `:437-438` reads
  `exempt = ref.type in _MATURITY_CHECK_EXEMPT` and skips only for exempt types. This is what
  Ruling 22 required, and it closes the hole a value-keyed exemption would have opened — a
  sentinel that satisfied the gate could have been returned by *any* branch.
- **The sentinel fails closed.** `backend/src/app/platform/rating_versions.py:319` returns
  `status="no_maturity_concept"`, which is not a member of `_APPROVED_OR_BETTER`. Remove
  `rate_table` from the exemption and the pin is refused rather than admitted — the inverse of
  the failure mode Ruling 22 refused (a) for. **Stronger than the ruling asked**, and verified,
  not taken on the record's word.
- **The tripwire is real.** `backend/tests/test_rating_version_compile.py:230-246` asserts
  `"status" not in RateTableVersionRow.__table__.columns` against the live SQLAlchemy table, so it
  trips on a migration rather than on a comment going stale, and its failure message names this
  ruling and `OQ-RATE-7`.
- **The disarmed probe was caught, and by the executor.**
  `packages/pricing-core/tests/test_rating_compile_bundle.py:154-165` re-targets
  `test_an_unapproved_pin_is_refused` from `rate_table` to `model`, and `:169-181` adds
  `test_a_rate_table_pin_compiles_regardless_of_status`. Without the re-target, exempting
  `rate_table` would have left the maturity gate's only positive proof asserting nothing —
  a fix disarming the probe that found it. Credit where it is due: Ruling 22 did not name this,
  and the executor found it.

### The remainder — Ruling 22's acceptance test fires on `main`

Ruling 22's acceptance test reads: *"The ruling is overridden if a build reports `"approved"` for
an artifact whose row has no status column."* Sweeping the class rather than the reported symbol —
every `ResolvedArtifact(status=…)` in the resolver — gives five branches:

| Branch | Status source | `rating_versions.py` |
|---|---|---|
| `rating_algorithm` | **hardcoded `"approved"`** | `:271` |
| `model` | `model.status` | `:293` |
| `rate_table` | `"no_maturity_concept"` sentinel | `:319` |
| `reference_table` | `published`→`approved` bridge, real status otherwise | `:343` |
| `custom_objective` | `objective.status.value` | `:354` |

`RatingAlgorithmRow` (`backend/src/app/db/models.py:1928-1939`) has **no status column** —
`id`, `workspace_id`, `slug`, `version`, `content`, `created_at`, `created_by`, `updated_at`. So
`rating_algorithm` is the identical construction Ruling 22 refused, on the identical premise,
left standing because the decision point named one type and the fix followed the name. This is
the stranded-list-mate failure exactly: an amendment fixing the reported symbol and not the class.

**Two defects that are individually benign and compose badly.** `compile_bundle` never reads the
algorithm's status at all: `resolved_algorithm` is used three times — `:420` resolve, `:421`
`.payload` validate, `:428` `.payload` into `payloads` — and `.status` is not among them, while
the function's own docstring at `:404-405` claims *"the pins resolve to `approved` or better
(FR-OVR-14)"* and FR-RATE-22 makes the algorithm version one of the pins. So today the hardcode is
inert because nothing reads it, and the missing check is invisible because the hardcode would
satisfy it. **Fixing either one alone is worse than fixing neither**: add the algorithm to the
maturity loop and the hardcode makes the new check vacuous on arrival; remove the hardcode without
the loop and nothing changes. They must land together.

**And this case is *cleaner* than `rate_table`'s, which is why it needs no new open question.**
`06` mentions Rating Algorithm six times — as a role-assignment scope (§2, FR-GOV-4), as a
`risk_tier` carrier (FR-GOV-43), in §4.4's dossier section list, and in OQ-GOV-4 — and **never as
an approval-bearing artifact**. It is absent from `06` §2's Governed Artifact enumeration and from
`06` §3.3's evidence table. So unlike Rate Table Version there is no `06`-versus-`03`
contradiction to resolve: the suite consistently gives a Rating Algorithm no approval lifecycle,
and the exemption is simply true rather than provisional.

**Ruled, extending Ruling 22 rather than reopening it:** `rating_algorithm` joins
`_MATURITY_CHECK_EXEMPT` with its own docstring line; the resolver's `:271` returns the same
`"no_maturity_concept"` sentinel instead of `"approved"`; the algorithm is brought into the same
maturity loop as the other four pin kinds so the docstring's claim becomes true; and a second
tripwire asserts `RatingAlgorithmRow` has no `status` column. Because `06` makes no governance
claim here, this exemption carries **no `OQ-`** — the note may say so, so a later reader does not
go looking for one.

This is a follow-up PR on the executor's queue, not a defect in #400: #400 discharged the ruling
as it was written, and the ruling was written naming one type.

### Disposition

- **R8: ratified**, on the strength of the four verifications above rather than on its own account
  of itself.
- **Ruling 22: partially discharged.** The remainder above is owed, and until it lands Ruling 22's
  acceptance test is failing on `main`.
- No spec change. No id minted.

**Acceptance test — the violation that must become expressible.** The sweep that found this is the
test: *every* branch of `_Resolver.resolve` must return either a status its row can contradict or
a sentinel its type is exempt for, and no branch may return a literal member of
`_APPROVED_OR_BETTER` over a row with no status column. That is checkable by reading five lines and
five table definitions, and it is now written down as a class rather than as two instances.
**Overridden** if a sixth branch is added returning a hardcoded passing status.

---

## Findings reported, not ruled

1. **The algorithm pin is outside FR-OVR-14's loop entirely**, which predates PR #400 and is W9's
   — FR-RATE-25's clause (2) as F-W9-3 ([`../audit/register.md`](../audit/register.md)`:25`)
   enumerates it. F-W9-3 records that clause's *"maturity half is enforced"*; it is enforced for
   four of the five pin kinds. Whether that sharpens F-W9-3 or reopens the W9 close is scope, and
   `CLAUDE.md` §12 puts scope outside this role.
2. **A lead ruling lives outside the repository.** R8 and its siblings are in
   `/home/puzhenhao1989/w11-handover-2026-08-29/lead-rulings.md`. `CLAUDE.md` §12 requires every
   decision to land as a dated artifact and not in chat, and `docs/plans/README.md` puts handover
   files in the class that dies with its session. The rulings that bind repository work — R7 and
   R8 at least — belong under `docs/`. Not this role's to move: they are the lead's records.
3. **This is the third instance of Ruling 12's charter finding.** The Tools line in
   [`../../.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) names ruling
   records, the open-questions log and `docs/specs/`. It has now been short of the artifact a
   ruling's disposition needed three times: `docs/contracts/` (Ruling 12), `docs/roadmap.md`
   (Ruling 22, resolved by the lead adopting the row), and `docs/process/delivery-process.md`
   (here). Three instances is a pattern, and meeting it case by case has a cost each time. Worth
   settling as a charter amendment, which is the maintainer's.

---

## Sources — read at `39cb58e`

- `docs/plans/README.md` — the "A filed plan is a record, not an instruction" section and
  conventions 4 and 5.
- `docs/process/delivery-process.md` §3's role table, §5, §11, §12.
- `docs/specs/06-governance.md` §2 `:63-64`, FR-GOV-4 `:81`, FR-GOV-43 `:146`, §3.3 `:105-149`,
  §4.4 `:396`; `docs/specs/03-rating-engine.md` FR-RATE-22 `:133`, FR-RATE-25 `:136`;
  `docs/specs/00-overview.md` FR-OVR-14 `:223`.
- `docs/audit/register.md` F-W9-3 `:25`.
- `/home/puzhenhao1989/w11-handover-2026-08-29/lead-rulings.md` R6, R7, R8 — read in full.
- `git show 39cb58e` — the merge commit message and the `compile.py` diff;
  `packages/pricing-core/src/pricing_core/rating/compile.py:285-300`, `:400-440`;
  `backend/src/app/platform/rating_versions.py:261-355`;
  `backend/src/app/db/models.py:1928-1939`, `:1978-2011`;
  `backend/tests/test_rating_version_compile.py:230-246`;
  `packages/pricing-core/tests/test_rating_compile_bundle.py:154-181`.
