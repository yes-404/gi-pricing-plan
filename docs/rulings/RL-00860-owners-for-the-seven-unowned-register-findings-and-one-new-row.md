---
id: RL-860
family: ruling
title: owners for the seven unowned register findings, and one new row
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

## RL-860 — owners for the seven unowned register findings, and one new row

**Authority, stated rather than assumed.** This discharges a maintainer delegation recorded at
M2 in the lead's rulings file, 2026-08-29 20:30Z, quoting the maintainer verbatim: *"for unowned
findings assign to decision maker to decide"*. **It reached me as the lead's record of the
maintainer's words, not from the maintainer directly**, so it is cited as what it is. It
supersedes M1's carve-out reserving owner assignment to the maintainer. It does **not** touch
`CLAUDE.md` §12's reserved list — the four §13 verdicts and the merge stay the lead's — and
nothing below claims otherwise.

**Decided, not written into the register.** Each owner below is a decision; transcribing it into
`docs/findings/register.md`'s Decision cell is a mechanical edit, and that file is an audit artifact
`CLAUDE.md` §12 has the lead file after an auditor proposes. This is the **fourth** instance of
the charter-grant finding first filed as RL-878 (`docs/contracts/`, `docs/roadmap.md`,
`docs/process/delivery-process.md`, now `docs/findings/register.md`) and it is getting expensive to
meet case by case. The wording for each cell is given below so the transcription is a copy, not a
re-derivation.

| Row | Owner | What that owner must do |
|---|---|---|
| **F-W9-3** *(cheap half)* | **WK-671**, in RL-859's follow-up PR | Point `FR-240`-marked tests at the mechanisms that already run — clauses (1), (2)'s maturity half, (3). That PR is already in `compile_bundle` and its tests |
| **F-W9-3** *(expensive half)* | **The §14 review at WK-671's close** | Place clauses (4), (5) and (6)'s transitive half on a workstream **or** accept them as not-built with a reason. Validation code for these exists nowhere |
| **F26** `.claude/` CI gap | **WK-671** | Land the `paths:` filter and the content check **before** the charter amendments R6 is holding for the §14 review, which land into exactly that unwatched directory |
| **F27(c)** + **F29** + **the new row below** | **The §14 review at WK-671's close**, as **one** gate-coverage item | Decide whether it becomes a workstream row or a maintainer task. One mechanism answers all three |
| **F30** `balance-watch` | **WK-671** | Delete the `ceiling_meter` import, `CEILING_METER_DIR` and the `live_limit_events` block, and say in `SKILL.md` that the maintainer's manual 5-hour relay replaced them; **and, unconditionally, make the arm banner state whether limit-event detection is active** |
| **F31** roster constant | **The §14 review**, as a fourth charter amendment beside R6's three | Drop `watcher.md`'s derived-roster-state clause. Nothing in the repository needs removing — `update-roster.sh` was always handover-local, so "do not carry it forward" is discharged by not carrying it |
| **F32** RL-882's premise | **This role — discharged in this record** | Done above. The register row can be marked resolved with a pointer here |

### Three of these are not pass-throughs, and here is why each is where it is

**F-W9-3 splits because its two halves have different costs and different homes.** The cheap half
is evidence for mechanisms that already run, and RL-859's follow-up is touching that exact file
and those exact tests — attaching it there costs almost nothing and is visible to the same
auditor. It does **not** reopen WK-669: `CLAUDE.md` §13 reserves that to the maintainer, and this is a
missing marker, not a defect in what WK-669 delivered. The register row is marked resolved with a
pointer rather than WK-669's close being touched.

**F27(c), F29 and the mypy gap are one finding wearing three coats.** All three are the same
categorical hole the Slice 1 record's third finding already named — *the gate checks documents
against documents and code against code, and nothing checks a document against the artifact it
specifies*. Placing them as three items invites three partial fixes; placing them as one names the
mechanism. **One constraint on that mechanism, derived from RL-887 and binding on whoever
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
expressible violation is a row in `docs/findings/register.md` whose Decision cell names no owner —
checkable by reading one column, and `CLAUDE.md` §13's "silence is not a verdict" applied to the
register rather than to a requirement. **This ruling is overridden** if a row is filed with
"unowned" or "owner TBD" in that cell.

---

## Sources — read at `24b537d`

- `packages/pricing-core/src/pricing_core/rating/compile.py:299`, `:428-450`;
  `backend/src/app/platform/rating_versions.py:261-271`;
  `backend/src/app/db/models.py:1920`;
  `packages/pricing-core/tests/test_rating_runtime.py:259`.
- `docs/specs/06-governance.md` §2 `:63-64`, FR-345 `:81`, FR-367 `:148`, FR-365 `:146`,
  §3.3, §4.4; `docs/specs/03-rating-engine.md` FR-237 `:133`, FR-240 `:136`;
  `docs/specs/00-overview.md` FR-20 `:223`.
- `docs/findings/register.md` F-W9-3 `:25`, F32 `:38`.
- [`RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption-is-declared-and-self-invalidating.md`](RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption-is-declared-and-self-invalidating.md)
  RL-856, read for its acceptance test;
  [`RL-00870-r8-is-ratified-as-applied-and-rl-856-is-not-fully-discharged-rating-algorithm-is-rate-table-s-stranded-list-mate.md`](RL-00870-r8-is-ratified-as-applied-and-rl-856-is-not-fully-discharged-rating-algorithm-is-rate-table-s-stranded-list-mate.md) RL-870;
  [`RL-00887-finding-3-the-framing-was-wrong-and-the-class-is-bigger-and-mostly-benign.md`](RL-00887-finding-3-the-framing-was-wrong-and-the-class-is-bigger-and-mostly-benign.md) RL-882;
  [`../plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](../plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)`:1074-1082`;
  [`../plans/README.md`](../plans/README.md) conventions 1 and 5.
