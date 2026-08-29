# W11 Task 1.2 — what a `rate_table` pin reports as its maturity (2026-08-29)

**What this is.** A decision point raised by the audit of PR #400
(`feat/w11-task-1-2-rating-compile-job`), which blocks its merge. The leaf plan
[`2026-08-29-w11-1-evaluator-core.md`](2026-08-29-w11-1-evaluator-core.md)`:833-835` tells the
executor that `compile_bundle` *"refuses any pin whose `status` is not approved-or-better
(`PIN_NOT_APPROVED`, FR-OVR-14). Return the row's real status, as the `model` branch already
does — **never a hardcoded `"approved"`**."* `RateTableVersionRow` has no status column, so the
instruction cannot be followed as written. The auditor named three forks: **(a)** hardcode
`approved`, **(b)** exempt `rate_table` from the check, **(c)** state the spec gap.

**Numbering continues at 22.** Rulings 1–5 are the prework record's, 6–13 the Slice 1 record's,
14–15 [`2026-08-29-w11-slice2-rulings.md`](2026-08-29-w11-slice2-rulings.md)'s, 16–21
[`2026-08-29-w11-slices-2-4-rulings.md`](2026-08-29-w11-slices-2-4-rulings.md)'s.

**Mints one `OQ-` id — `OQ-RATE-7` — and no `FR-`/`NFR-` id and no error code.** Read against
`origin/main` at `06bdac5`, with `HEAD` identical.

---

## Ruling 22 — the resolver reports no maturity for a `rate_table`, and the exemption is declared and self-invalidating

**Ruled: (b) and (c) together. (a) is refused.**

### The framing is corrected first, because no fork is safe under the one it arrived with

The decision point was put as a spec **silence** — `03` §3.3 gives rate tables no maturity
concept, zero hits for approval or maturity. That is true of `03` and false of the suite.
`06` says twice, in two independent places, that a Rate Table Version is approval-bearing:

- **`06` §2's glossary** ([`../specs/06-governance.md`](../specs/06-governance.md)`:64`) defines
  a **Governed Artifact** as *"Any artifact with an approval-bearing lifecycle: Dataset Version,
  Validation Rule, Model, Custom Objective, Custom Metric, Peril Structure, **Rate Table
  Version**, Rating Version, Optimisation Run (when cited as evidence)."* That is definitional
  and enumerative, not incidental.
- **`06` §3.3** (`:119`) gives it required evidence — *"Change note; diff vs previous; diff vs
  technical seed where seeded (`03` FR-RATE-16/17)"* — and FR-GOV-19 (`:109`) makes required
  evidence *"enforced at submission"*, which presupposes a submission and therefore a lifecycle.

Meanwhile `03` §3.3 (FR-RATE-14, 15, 16, 17, 62, 18, 19, 20, 21) specifies immutability, change
notes, diffs, bulk operations, validation and a rateable/diagnostic flag, and **no status**; and
`RateTableVersionRow` ([`../../backend/src/app/db/models.py`](../../backend/src/app/db/models.py)`:1989-2003`)
has thirteen columns and no `status` among them. `rate_table` **is** a member of
`ARTIFACT_TYPES` ([`../../packages/model-schema/src/model_schema/refs.py`](../../packages/model-schema/src/model_schema/refs.py)`:21-28`),
so the reference is well-formed; there is simply nothing behind it to be mature.

So this is a **contradiction between `06` and both `03` and the implementation**, not a gap a
code choice may quietly fill. `CLAUDE.md` §0: stop and resolve rather than make either match the
other. Resolving it is a spec change of real size and is raised as `OQ-RATE-7` below rather than
decided here.

### Why (a) — hardcode `"approved"` — is refused

1. **It puts a constant where a discriminator is read.** `compile.py:422-429` loops over rate
   tables, models, reference tables and custom objectives and refuses any whose status is not in
   `_APPROVED_OR_BETTER` (`:286`, `{"approved", "live", "retired"}`). A reader sees one gate over
   four pin kinds. Under (a), for one kind the gate cannot fail. The plan's `:835` instruction is
   that rule, and it is right.
2. **It fails open exactly when the control becomes real.** `06` already says the lifecycle
   ought to exist. Whoever adds a status column adds submission and approval with it — and
   `compile_bundle` goes on being told `"approved"` for a `draft` rate table version, so a Rating
   Version compiles, and later deploys, against an unapproved rate change, with nothing failing.
   A rate change *is* the price. This is the mispricing class, not a tidiness one.
3. **The PR's own justification does not survive its neighbour.** The `reference_table` branch
   immediately below translates a real lifecycle —
   `status = "approved" if version.status == "published" else version.status` — and its comment
   says why that is safe: *"A real `draft` version still reports its own, non-mature status, so
   an unpublished pin is still refused."* There, the literal is one branch of a live conditional
   over a column that can hold something else. For `rate_table` the same literal is the whole
   function, over no column at all. The two look alike and are not, and the resemblance is what
   makes (a) read as consistent.
4. **"Immutable, therefore approved" conflates two properties.** The PR's comment argues rate
   tables are *"immutable-on-write … never a draft phase"*. A Model version is immutable too and
   still carries an approval lifecycle. Immutability says the content will not change; maturity
   says somebody accepted it. `06` §3.3 asks for evidence on a Rate Table Version precisely
   because a rate change needs the second.

### Why (b) alone is not enough, and the two things that make it sufficient

A bare exemption fails open the same way (a) does — a skip nobody revisits. What separates a
deferral from a silence is that the exemption is **declared as data** and **self-invalidating**:

- **Declared.** `pricing_core` carries a named constant beside `_APPROVED_OR_BETTER` — the name
  is Task 1.2's, the content is not: `rate_table` and nothing else. Its docstring cites
  FR-OVR-14, `06` §2's Governed Artifact row and `OQ-RATE-7`, and states that membership is
  expected to be temporary. The resolver then reports each artifact's **real** maturity where one
  exists and invents none where it does not.
- **Self-invalidating.** A test asserts that `RateTableVersionRow` exposes no `status`
  attribute. The day a status column is added, that test goes red and names this record. The
  precedent for a declaration guarded in both directions is
  `backend/tests/test_contracts.py`'s `test_every_one_sided_slug_is_declared`, whose docstring
  says it *"keeps the set equal to the corpus in both directions — a one-sided slug without a
  declaration fails, and a declared slug that gained the other side fails too."*

### What this ruling deliberately does not touch

`_APPROVED_OR_BETTER` is not widened, and the `reference_table`, `model` and `custom_objective`
branches PR #400 ships are unchanged.

### Disposition

- **PR #400**: the `rate_table` branch stops returning `status="approved"`; the exemption
  constant and its docstring land in `pricing_core`; the self-invalidating test lands in
  `backend/tests/`. Nothing else in the PR changes.
- **Spec change in this commit**: `OQ-RATE-7` raised in `03` §10, mirrored into
  [`../open-questions.md`](../open-questions.md), and placed on
  [`../roadmap.md`](../roadmap.md) §10's *Before Phase 3* gate — which re-opens, following the
  precedent of the two gates already re-opened on 2026-08-22.

**Acceptance test — the violation that must become expressible.** Today *"a Rating Version
compiled against an unapproved rate table"* is not a statement any test can make, because no rate
table version has a maturity to be unapproved by. After this ruling two violations become
expressible, and both are red-on-arrival guards rather than assertions about today: (1)
`rate_table_versions` gaining a `status` column while `rate_table` is still exempt — the test
above fails and names this record; (2) a resolver branch returning a status literal that its row
cannot contradict, which is the general form of the `:835` rule and of which `rate_table` was the
only instance in PR #400. **The ruling is overridden** if any build reports `"approved"` for an
artifact whose row has no status column.

---

## `OQ-RATE-7`, as raised

**Question.** `06` makes a Rate Table Version a Governed Artifact with an approval-bearing
lifecycle (`06:64`) and required evidence at submission (`06:119`); `03` §3.3 gives it no
lifecycle and `rate_table_versions` has no status column. Which side is right?

- **(a) `03` and the code are the incomplete side.** A Rate Table Version gains
  `draft → review → approved`, a status column and migration, a `06` §4.2 policy entry and an
  `EVIDENCE_FLOOR` key; `compile_bundle` reads a real maturity and this ruling's exemption is
  deleted. Honours both `06` locations and makes the compile gate mean something for the artifact
  that most directly sets the price. Costs a migration on a shipped table, a submission path, and
  a decision on whether existing versions are retro-approved.
- **(b) `06` is the wrong side.** A Rate Table Version is governed *through* the Rating Version
  that pins it, never on its own: `06` §3.3's **Rating Version** row already requires *"rate table
  diffs"* as evidence, so approving both approves one change twice — on the most frequently
  edited artifact in the platform, where FR-RATE-18's bulk operations and FR-RATE-20's imports
  each mint versions. Costs striking Rate Table Version from `06` §2's Governed Artifact list and
  from `06` §3.3, and makes this ruling's exemption the specified behaviour rather than a stopgap.
- **(c) Split by phase.** Ungoverned individually in Phase 2; the lifecycle arrives in Phase 3
  with the rest of `06`'s surface (W17, which owns FR-GOV-9..19). Defers rather than answers, and
  leaves `06` saying something untrue for a phase.

**Recommendation: (b), and the deciding test is checkable rather than a matter of taste** — *is a
Rate Table Version ever pinned by more than one Rating Version?* If reuse across Rating Versions
is real, (a) earns its cost, because one approval then covers many prices and the compile gate is
the only place that can check it. If each rate change is pinned by exactly one Rating Version,
(b) is right and (a) is approving the same change twice. FR-RATE-15's *"The previous version stays
referenceable by existing Rating Versions"* says reuse is at least possible; nothing measured says
how common it is, and nothing in Phase 2 will until rating versions are being cut in numbers.
**Owner: maintainer.** Placed at the *Before Phase 3* gate because `06`'s surface is Phase 3's and
answering it later leaves `06` §3.3 naming evidence for an artifact that cannot be submitted.

---

## Findings reported, not ruled

1. **`compile_bundle`'s gate is absolute where FR-OVR-14 is relative.** FR-OVR-14
   ([`../specs/00-overview.md`](../specs/00-overview.md)`:223`) reads *"An artifact may only
   reference artifacts that are in a state **at least as mature as its own**"*, a relative rule;
   `compile.py:424` applies an absolute floor of approved-or-better to every pin regardless of the
   Rating Version's own status, and cites FR-OVR-14 in the message. A `draft` Rating Version
   compiling is refused a `draft` pin by the code and permitted one by the requirement as
   written. Which side is wrong is a real question and is **not** this decision point; it is
   F-W9-3's clause (2) territory ([`../audit/register.md`](../audit/register.md)`:25`).
2. **`rate_table` is a fourth instance of Ruling 20's class.** `06` §3.3 gives Rate Table Version
   required evidence and `06` §4.2 has no `rate_table` policy entry, so a submission would be
   refused with *"No approval policy for this artifact type"* before evidence is consulted —
   after `peril_structure` (2026-08-18), `custom_metric` (2026-08-20) and `deployment`
   (Ruling 20). Latent for the same reason: nothing submits one. It becomes live with
   `OQ-RATE-7`'s answer, and only under option (a).
3. **A stale next-free marker, which will mislead the next ruling.**
   [`2026-08-29-w11-slices-2-4-planning-readiness.md`](2026-08-29-w11-slices-2-4-planning-readiness.md)'s
   D5 row says a question there *"Needs an `OQ-RATE` (next free `OQ-RATE-7`)"*. This record takes
   `OQ-RATE-7`; **D5's is `OQ-RATE-8`.** A frozen document's next-free marker ages the moment
   anyone else allocates, and D5 is still unruled.
4. **Charter boundary, named rather than routed around — a second instance of Ruling 12's
   finding.** [`../../.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md)'s
   Tools line grants writes to *"ruling records, the open-questions log, and `docs/specs/`* and
   does not name [`../roadmap.md`](../roadmap.md).
   [`../../.claude/skills/spec-change/SKILL.md`](../../.claude/skills/spec-change/SKILL.md) —
   which the same charter makes mandatory — requires a new `OQ-` to reach `docs/roadmap.md` §10's
   gate table **in the same commit**, and records four questions (OQ-DATA-7, OQ-OVR-6, OQ-PLAT-6,
   OQ-MODEL-8) that were raised, mirrored correctly, and invisible to the plan until 2026-08-15
   because it did not. **I have made the gate-row edit**, on the reading that a grant to raise a
   question which cannot discharge that question's own mandatory coupled edit is incoherent, and
   that a partial mint is the documented defect rather than the cautious option. **Flagged, not
   assumed:** if the maintainer reads the grant as excluding `docs/roadmap.md`, strike that one
   row and route it — nothing else in this PR depends on it, and Ruling 12's finding then has its
   second instance and should be settled rather than met case by case.

5. **Nine open questions are on no decision-gate row, found while discharging finding 4's
   obligation.** Running the `docs-audit` skill's coverage check over the tree with `OQ-RATE-7`
   added reports `OQ-RATE-7` correctly placed and **nine others missing**: OQ-MODEL-32, -33, -34,
   OQ-OVR-10, -11, -12, -17, OQ-PLAT-12 and OQ-PLAT-17. `extra` and `duplicated` are both `none`,
   and every row's `N (M open)` count reconciles against its own contents, so this is coverage
   only. It is pre-existing — this PR only adds to that section — and it is the *fifth* instance
   of the failure the skill records for OQ-DATA-7, OQ-OVR-6, OQ-PLAT-6 and OQ-MODEL-8: raised,
   mirrored, and invisible to the plan. Placing nine questions on gates is planning work and is
   the lead's, not this role's; reported with the enumerating command so it is re-derivable rather
   than trusted.

---

## Sources — read at `06bdac5`

- `docs/specs/03-rating-engine.md` §3.3 `:130-147`, FR-RATE-25 `:136`, §10 `:800-813`.
- `docs/specs/06-governance.md` §2 `:64`, FR-GOV-19 `:109`, §3.3 `:119`, §4.2 `:251-348`.
- `docs/specs/00-overview.md` FR-OVR-14 `:223`.
- `docs/audit/register.md` F-W9-3 `:25`.
- `docs/plans/2026-08-29-w11-1-evaluator-core.md:820-845`.
- `packages/pricing-core/src/pricing_core/rating/compile.py:286-296`, `:414-430`;
  `packages/model-schema/src/model_schema/refs.py:19-28`;
  `packages/model-schema/src/model_schema/approvals.py:101-108`, `:202-261`;
  `backend/src/app/db/models.py:1978-2011`; `backend/tests/test_contracts.py`'s
  `ONE_SIDED_SLUGS` docstring.
- PR #400's diff, read directly via `gh pr diff 400` — the `rate_table`, `reference_table`,
  `model` and `custom_objective` resolver branches.
