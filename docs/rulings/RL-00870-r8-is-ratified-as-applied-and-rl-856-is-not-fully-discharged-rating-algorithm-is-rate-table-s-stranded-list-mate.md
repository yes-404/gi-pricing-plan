---
id: RL-870
family: ruling
title: R8 is ratified as applied, and RL-856 is **not** fully discharged: `rating_algorithm` is `rate_table`'s stranded list-mate
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-ruling-vs-plan-scope.md
---

## RL-870 — R8 is ratified as applied, and RL-856 is **not** fully discharged: `rating_algorithm` is `rate_table`'s stranded list-mate

**Ruled: R8 is ratified.** Every claim it makes about the amendment is true against `39cb58e`,
and two of them are stronger than RL-856's literal ask. **And RL-856's own acceptance test
is failing on `main` right now**, on a branch nobody looked at.

### R8's claims, verified rather than accepted

- **Exempt by type, not by value.**
  [`../../packages/pricing-core/src/pricing_core/rating/compile.py`](../../packages/pricing-core/src/pricing_core/rating/compile.py)`:299`
  declares `_MATURITY_CHECK_EXEMPT = frozenset({"rate_table"})` beside `_APPROVED_OR_BETTER`, with
  a docstring citing FR-20, `06` §2 and `OQ-620`; the gate at `:437-438` reads
  `exempt = ref.type in _MATURITY_CHECK_EXEMPT` and skips only for exempt types. This is what
  RL-856 required, and it closes the hole a value-keyed exemption would have opened — a
  sentinel that satisfied the gate could have been returned by *any* branch.
- **The sentinel fails closed.** `backend/src/app/platform/rating_versions.py:319` returns
  `status="no_maturity_concept"`, which is not a member of `_APPROVED_OR_BETTER`. Remove
  `rate_table` from the exemption and the pin is refused rather than admitted — the inverse of
  the failure mode RL-856 refused (a) for. **Stronger than the ruling asked**, and verified,
  not taken on the record's word.
- **The tripwire is real.** `backend/tests/test_rating_version_compile.py:230-246` asserts
  `"status" not in RateTableVersionRow.__table__.columns` against the live SQLAlchemy table, so it
  trips on a migration rather than on a comment going stale, and its failure message names this
  ruling and `OQ-620`.
- **The disarmed probe was caught, and by the executor.**
  `packages/pricing-core/tests/test_rating_compile_bundle.py:154-165` re-targets
  `test_an_unapproved_pin_is_refused` from `rate_table` to `model`, and `:169-181` adds
  `test_a_rate_table_pin_compiles_regardless_of_status`. Without the re-target, exempting
  `rate_table` would have left the maturity gate's only positive proof asserting nothing —
  a fix disarming the probe that found it. Credit where it is due: RL-856 did not name this,
  and the executor found it.

### The remainder — RL-856's acceptance test fires on `main`

RL-856's acceptance test reads: *"The ruling is overridden if a build reports `"approved"` for
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
`rating_algorithm` is the identical construction RL-856 refused, on the identical premise,
left standing because the decision point named one type and the fix followed the name. This is
the stranded-list-mate failure exactly: an amendment fixing the reported symbol and not the class.

**Two defects that are individually benign and compose badly.** `compile_bundle` never reads the
algorithm's status at all: `resolved_algorithm` is used three times — `:420` resolve, `:421`
`.payload` validate, `:428` `.payload` into `payloads` — and `.status` is not among them, while
the function's own docstring at `:404-405` claims *"the pins resolve to `approved` or better
(FR-20)"* and FR-237 makes the algorithm version one of the pins. So today the hardcode is
inert because nothing reads it, and the missing check is invisible because the hardcode would
satisfy it. **Fixing either one alone is worse than fixing neither**: add the algorithm to the
maturity loop and the hardcode makes the new check vacuous on arrival; remove the hardcode without
the loop and nothing changes. They must land together.

**And this case is *cleaner* than `rate_table`'s, which is why it needs no new open question.**
`06` mentions Rating Algorithm six times — as a role-assignment scope (§2, FR-345), as a
`risk_tier` carrier (FR-365), in §4.4's dossier section list, and in OQ-636 — and **never as
an approval-bearing artifact**. It is absent from `06` §2's Governed Artifact enumeration and from
`06` §3.3's evidence table. So unlike Rate Table Version there is no `06`-versus-`03`
contradiction to resolve: the suite consistently gives a Rating Algorithm no approval lifecycle,
and the exemption is simply true rather than provisional.

**Ruled, extending RL-856 rather than reopening it:** `rating_algorithm` joins
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
- **RL-856: partially discharged.** The remainder above is owed, and until it lands RL-856's
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

1. **The algorithm pin is outside FR-20's loop entirely**, which predates PR #400 and is WK-669's
   — FR-240's clause (2) as F-W9-3 ([`../findings/register.md`](../findings/register.md)`:25`)
   enumerates it. F-W9-3 records that clause's *"maturity half is enforced"*; it is enforced for
   four of the five pin kinds. Whether that sharpens F-W9-3 or reopens the WK-669 close is scope, and
   `CLAUDE.md` §12 puts scope outside this role.
2. **A lead ruling lives outside the repository.** R8 and its siblings are in
   `/home/puzhenhao1989/w11-handover-2026-08-29/lead-rulings.md`. `CLAUDE.md` §12 requires every
   decision to land as a dated artifact and not in chat, and `docs/plans/README.md` puts handover
   files in the class that dies with its session. The rulings that bind repository work — R7 and
   R8 at least — belong under `docs/`. Not this role's to move: they are the lead's records.
3. **This is the third instance of RL-878's charter finding.** The Tools line in
   [`../../.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) names ruling
   records, the open-questions log and `docs/specs/`. It has now been short of the artifact a
   ruling's disposition needed three times: `docs/contracts/` (RL-878), `docs/roadmap.md`
   (RL-856, resolved by the lead adopting the row), and `docs/process/delivery-process.md`
   (here). Three instances is a pattern, and meeting it case by case has a cost each time. Worth
   settling as a charter amendment, which is the maintainer's.

---

## Sources — read at `39cb58e`

- `docs/plans/README.md` — the "A filed plan is a record, not an instruction" section and
  conventions 4 and 5.
- `docs/process/delivery-process.md` §3's role table, §5, §11, §12.
- `docs/specs/06-governance.md` §2 `:63-64`, FR-345 `:81`, FR-365 `:146`, §3.3 `:105-149`,
  §4.4 `:396`; `docs/specs/03-rating-engine.md` FR-237 `:133`, FR-240 `:136`;
  `docs/specs/00-overview.md` FR-20 `:223`.
- `docs/findings/register.md` F-W9-3 `:25`.
- `/home/puzhenhao1989/w11-handover-2026-08-29/lead-rulings.md` R6, R7, R8 — read in full.
- `git show 39cb58e` — the merge commit message and the `compile.py` diff;
  `packages/pricing-core/src/pricing_core/rating/compile.py:285-300`, `:400-440`;
  `backend/src/app/platform/rating_versions.py:261-355`;
  `backend/src/app/db/models.py:1928-1939`, `:1978-2011`;
  `backend/tests/test_rating_version_compile.py:230-246`;
  `packages/pricing-core/tests/test_rating_compile_bundle.py:154-181`.
