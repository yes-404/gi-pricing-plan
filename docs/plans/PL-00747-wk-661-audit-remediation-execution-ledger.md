---
id: PL-747
family: plan
kind: leaf
title: WK-661 Audit Remediation — execution ledger
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-22
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-22-w5-audit-remediation-ledger.md
---

# WK-661 Audit Remediation — execution ledger

Running record for `.planning/PL-00748-wk-661-audit-remediation-sequenced-slice-roadmap.md`. Branch
`worktree-w5-audit-remediation`, worktree `.claude/worktrees/w5-audit-remediation`.

**What this file is for:** the plan says what to do; this says what was *found* while doing
it, including where the plan was wrong. Slice 6's closure record is written from here.

---

## Decisions taken before starting

| Decision | Outcome | Authority |
|---|---|---|
| **OQ-646** — does `execute_job` preserve a handler's `PlatformError.code`? | **(a)** — a dedicated `except PlatformError` clause storing `JobError(code=exc.code, message=exc.detail or exc.title)`, `retryable` unchanged | Maintainer, 2026-08-22, accepting the recommendation already on file |
| **FR-95** — reassignment to WK-690 | **Accepted**, dated 2026-08-22, recorded at `roadmap.md:2589` and `:2985` | Maintainer, 2026-08-22 |
| **FR-106** — build Bühlmann–Straub or supersede it? | **Build.** The question dissolved on inspection: OQ-579 was *already decided* 2026-08-15 — "both … so WK-661 builds two methods rather than choosing one" (`roadmap.md:112`). Superseding would mean overturning a recorded maintainer decision, which §14 does not permit an executing agent to do | Pre-existing decision, verified |
| **NFR-475/476/485** — build a 5M-row fixture? | **No.** Measure at stated smaller scales and write the extrapolation down, which the plan explicitly permits. A 5M × 60 fixture is hours of compute for an extrapolation that a growth curve gives more honestly | Plan, §3d |

---

## Findings — where the plan or the repository was wrong

### F1 — `02` §4.8 carries no immutability requirement id *(slice 1a)*

The plan said to mark the trigger test with "whichever requirement `02` R2 carries — check
§4.8". **§4.8 has none.** R2 is a §1.3 hard rule with no id of its own; §4.8's Invariants
block states a *presence* rule and the ids it cites are about presence, transparency and
lineage. Resolved by tracing to `00` **FR-4** (*"every Artifact is immutable once it
leaves `draft`"*), which is the requirement R2 instantiates, alongside **FR-203**,
which the existing raw-`UPDATE` trigger test already carries. Recorded in the §4.8
amendment.

### F2 — `record_fit` is not where the plan said, and the ordering question resolves cleanly *(slice 1a)*

`record_fit` is `backend/src/app/platform/modelling.py:736`, not
`worker/model_handlers.py`. It writes `fit_result`, `diagnostics_id`, `status` and `job_id`
as **four assignments on one ORM object followed by a single flush** (`:793-797`) — one
`UPDATE`. So the plain guard is safe and the `OLD.diagnostics_id IS NOT NULL` fallback was
not needed. Independently corroborated by `test_model_lifecycle.py:454-461`, which records
that this write order is *forced* by two existing invariants.

### F3 — `CLAUDE.md` §11's alembic command could never have worked *(slice 1a)*

`uv run alembic upgrade head` bare dies with
`InvalidPasswordError: password authentication failed for user "gip"`.
`backend/src/app/config.py:107` defaults to `gip:gip@localhost:5432/gip`;
`deploy/docker-compose.yml` provisions `gipricing:gipricing@…/gipricing`. **The tests never
caught it** because `backend/tests/conftest_db.py:35`'s `DEFAULT_TEST_DSN` carries the
compose credentials itself, and CI sets `GIP_DATABASE_URL` explicitly
(`.github/workflows/python.yml:130`). Corrected in `CLAUDE.md` §11 with the reason.

**Not fixed, deliberately:** changing `config.py`'s default to match compose would remove
the trap at source, but it changes an application-wide default credential and is outside
this plan's scope. **Owner:** raise as an open question if it recurs.

### F4 — `FR-364`'s `peril_structure` justification rested on a false premise *(slice 1c, not in the plan)*

FR-364 and `EVIDENCE_FLOOR`'s docstring both justified `peril_structure`'s empty floor
by saying it "has no §3.3 row at all". **§3.3 has carried a Peril Structure row since
2026-08-14** — four days *before* the claim was written, in the Phase 0 commit that created
the document.

The conclusion survives; the reason does not. The row's **reconciliation** half is enforced
structurally (`review` is reachable only from `reconciled`; a `fail` verdict is refused at
submission), so a floor entry would restate a lifecycle edge. Its **per-peril model
approvals** half is enforced nowhere and sits in `peril_structures.perils` as JSONB, so it
cannot be queried — `model_comparison_if_predecessor`'s case exactly. **Owner: WK-677**
(FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363, evidence enforcement).

### F5 — FR-21's audit was structurally unable to see this hole *(slice 5c)*

`ReconcileRequest.tolerance` was a bare `Decimal` at a wire boundary. Measured, not assumed:
`{"tolerance": 0.1 + 0.2}` validated to `Decimal('0.30000000000000004')`, and the *published
contract* declared `anyOf: [{"type": "number"}, {"type": "string"}]` — research finding F7's
lossy form, which FR-10 forbids. That number decides a reconciliation
(`|ratio - 1| <= tolerance`).

**Why 2026-08-19 missed it:** OQ-547's audit swept fields that *were* `DecimalStr`. A field
that should have been one and was not is invisible to that search. A sweep for bare
`: Decimal` across `backend/src/app/api/` found **exactly one** — this — so the class is now
closed at the wire, and the remaining bare `Decimal`s are internal dataclass and function
parameters that never cross JSON.

**This is a breaking wire change**: a caller sending a JSON number now gets a 422.

---

### F6 — a blanket string replace crossed two error codes that must stay apart *(slice 1b, mine)*

Registering `ARTIFACT_TYPE_NOT_RESOLVABLE` I replaced `"VALIDATION_FAILED"` across
`api/approvals.py` and caught **two** sites. Only one was the unresolvable-type refusal; the
other is the **malformed-reference** branch, where `VALIDATION_FAILED` is correct — there
the caller's input really is bad. `test_a_malformed_artifact_reference_is_refused` caught it
immediately. Restored, and the distinction is now written at both sites rather than left to
the next reader to rediscover.

The general lesson is the one the repo already applies to schemas: a code is a claim about
*which* thing went wrong, and two refusals reachable from one route are exactly where a
blanket edit does damage that still compiles and still returns 422.

### F7 — the mechanism behind three separate staleness bugs *(slice 6a)*

The slice count, the buildable-slice counter and six verdict rows all went stale the same
way, and it is one mechanism rather than three lapses: **a slice's PR updates the row that
describes that slice, and every other place counting or judging slices is unowned.** #116
did it, then #124 and #125 did it again. Verified in the diffs — both #124 and #125 *did*
touch `roadmap.md`, and spent that edit striking their own row.

Named in the roadmap at the count, rather than fixed a third time, because a fourth
recurrence is otherwise certain.

### F8 — the correction was stale before it landed

Slice 6a derived `02`'s requirement count as **124**. By the time I applied it, it was
**125** — the slice's own FR-118, appended an hour earlier. Re-derived with
`scope-audit.py` at the moment of writing: **125 in scope, 110 evidenced (88 %), 15
without**. Recorded inside the correction itself, because a correction that goes stale
between derivation and application is the sharpest possible illustration of why the number
does not belong on the page at all.

## Slice status

| Slice | State |
|---|---|
| 1a — `diagnostics_id` immutability | **done** — migration `9e4c7b21fa08`, enforcement proven three ways, `02` §4.8 amended |
| 1b — FR-386 reference resolution | **done** — fan-out in the route (no registry), 6 of 20 types resolve, unresolvable fails closed with the new `06`-owned `ARTIFACT_TYPE_NOT_RESOLVABLE`; **5 FR-386 markers where there were 0**; enforcement proven (resolver removed → 8 failures). WK-677 owns the durable fix |
| 1c — `custom_metric` evidence floor | **done** — `06` §3.3 row, `EVIDENCE_FLOOR` entry, three negative tests, `metrics.py` docstring, FR-364 amended |
| 2 — FR-115 + OQ-646 | **done** — layer 1 `GLM_FIT_FAILED`; layer 2 the `except PlatformError` clause, marked **FR-403** (platform job machinery, not FR-115). OQ-646 closed in both `open-questions.md` and `07`'s mirror |
| 3 — NFR evidence | in flight |
| 4 — Bühlmann–Straub | in flight |
| 5 — contract half, interfaces, strays | red guard in flight; `tolerance` stray **done** |
| 6 — bookkeeping + closure record | 6a: **8 of 9 items applied** (count, counter, six verdict rows, FR-352, AST parser, requirement count, phase-review skill, custom-metrics entry). Outstanding: the two missing slice records for PRs #124/#125, drafted and verified but not yet inserted. FR-95 acceptance **done** |

## Owed before the branch closes

- **Regenerate contracts once, at the end** — `uv run python scripts/generate-contracts.py`,
  then `--check`. `test_the_published_tolerance_admits_no_json_number` is red until then, by
  design: its failure output is the captured defect.
- Record OQ-646's decision in `docs/open-questions.md` **after** layer 2 lands, so the row
  describes what was built rather than what was chosen.
- `.claude/skills/` update for F3 (§12's maintenance rule).

---

## Later findings

### F9 — the guard tests were three separate blind spots, not one *(slice 5a)*

Fixing the existence test surfaced three defects in the checking machinery itself, none in
the work order:

1. **`_type_map` clobbered property definitions.** It did `properties.update(...)`, so the
   *last* variant naming a field replaced every earlier definition — and a conditional
   refinement is exactly that shape. Following `then` therefore **deleted** the real
   definition and took the walker from 36 paths to 28. Fixed by unioning subtrees per name.
2. **`const` was invisible** to `_scalar_types`, so a `{"const": ...}` branch was typeless
   and produced false mismatches.
3. **`ENVELOPE_FIELDS` was wrong in both directions** — the literal
   `{id, slug, version, dataset_id}`: three real envelope fields out of fourteen, plus
   `dataset_id`, which is not an envelope field at all. It is now read from
   `common/artifact-envelope.schema.json` and applied only where a schema really `allOf`s
   the envelope. The flat exemption had been hiding `TransparencyArtifact.id`/`created_at`
   and `Diagnostics.id` from a check they should always have failed.

**The broken-input proof earned its keep by finding two dead checks** — including the exact
mechanism by which `gbm.quantile_crossing` (FR-199) and `gbm.tree_count` sat absent for
months with every test green: the existence test compares **top-level names only**, and the
type test only narrows when a path stops being shared. A nested-path test was added.

**The sharpest single finding:** `model.schema.json`'s `fit_result` was one flat block
requiring `converged`, which neither `GbmFitResult` nor `EbmFitResult` has — so **no GBM or
EBM fit could ever have validated against the published contract.**

### F10 — `transparency_artifact_id` is superseded, not owed *(§0 question, mine)*

FR-207 listed it declared-and-unbuilt, **owned by WK-661** — so WK-661 could not close while
owing it. FR-137 settled the direction on 2026-08-19 (artifact → model), but the
deciding fact is **cardinality**: `ix_transparency_model` is
`(workspace_id, model_id, created_at)` and **not unique**, so a Model accumulates artifacts
as it is re-derived and a single back-pointer would be wrong the first time a second was
written. A field that cannot express the relationship it names is not unbuilt — it is a
second, lossy source of truth, the defect `GbmSpec.backend` was refused for. **Struck.**

### F11 — a marker was rejected for claiming evidence of unbuilt work *(slice 5a)*

The wrongly-marked error-code test could plausibly have taken `FR-22`, which is about
exactly this reconciliation. The agent rejected it: FR-22 specifies an `audit-docs.py`
check that **does not exist** and is triggered by Phase 1a's exit demo, so marking a passing
test with it would claim evidence for unbuilt work — the same defect class being corrected.
It took `FR-450` instead, which the sibling test already carries. This is the §13
"a marker is a claim, not a proof" rule applied by an agent unprompted.

## Contract regeneration — done

`uv run python scripts/generate-contracts.py` run once at the end, as planned, then
`--check` → **exit 0, 23 contracts match**. `test_the_published_tolerance_admits_no_json_number`
was red by design from the moment it was written and is now green: the published
`ReconcileRequest.tolerance` is `type: string`, not `anyOf: [number, string]`.

### F12 — 6d run against my own writing, and it held *(slice 6d)*

§13's verify-before-signing step exists because a 2026-08-22 slice found a "dated note
2026-08-21, owner WK-661" that had **never been written**. Re-run today:

- **The one outstanding claim of that shape is the already-corrected one** at
  `roadmap.md:3012`. No other "dated note … owner WK-661" claim survives unverified.
- **I then ran it against the two slice records I had just written myself**, which claimed
  `02`'s FR-114 amendment records *which side was wrong and why* about the
  deviance-argmin design. First read of the §4.8 blockquote showed only what was built, and
  the claim looked false. It is not: the correction is at **`02:156-159`**, beside the
  requirement row rather than in the §4.8 note, and carries the measured bias
  (argmin ≈ truth + 0.25, grid-edge at every seed).

Worth recording because the near-miss is the lesson: **the first grep said the obligation
was fabricated.** `git log -S'deviance argmin'` returned nothing only because the text is
hyphenated. An instrument that answers "never written" on a spelling difference is how a
true record gets struck as false — the inverse of the failure 6d was created to catch, and
just as bad.

### F13 — I committed the exact defect this slice was fixing *(mine)*

`scope-audit.py` reported **FR-118 unevidenced** — the requirement I appended myself in
slice 4, roughly two hours earlier. The test proving it
(`test_buhlmann_straub_refuses_a_book_it_cannot_estimate_on`, four parametrised degenerate
cases) carried only `FR-106`.

That is **the same marker-misattribution defect slice 4 had just fixed**: the Bühlmann–Straub
tests were marked `FR-105` while asserting FR-106's content, so `scope-audit.py`
credited the wrong requirement and the gap read as covered. I appended a requirement and did
not mark the test that proves it, which is the identical failure one layer along.

Fixed — the refusal test now carries both markers, and MODEL moved from 110/125 to
**111/125 (89 %)**.

**Worth keeping because of what caught it.** Not review, and not care: the derived count.
Running `scope-audit.py` again *after* editing is the only reason this did not ship inside a
closure record claiming 88 % with a silent hole in it. §13 rule 1's "derive the expected
scope from the specification, then look for evidence" is doing exactly the work it was
written for, against the person applying it.

---

## Gate — both halves, run locally, each exit code read

`CLAUDE.md` §11's warning is that a "gate" covering only Python has been green here while the
frontend was red. Both halves, 2026-08-22:

| Command | Result |
|---|---|
| `uv run ruff check .` | **0** — clean repo-wide |
| `uv run mypy` | **0** — 131 source files |
| `uv run lint-imports` | **0** — 3 contracts kept, 0 broken |
| `uv run pytest tests/ packages/ -q` | **917 passed** |
| `uv run pytest backend/tests -q` | **exit 0** |
| `python3 scripts/audit-docs.py` | **0** — all checks passed |
| `uv run python scripts/req-coverage.py` | **0** — 495 specified, 247 marked |
| `uv run python scripts/generate-contracts.py --check` | **0** — 23 contracts match |
| `pnpm --dir frontend install --frozen-lockfile` | **0** |
| `pnpm --dir frontend generate:api` | **0** |
| `pnpm --dir frontend type-check` | **0** — the one that matters here: the contract changes (`tolerance` → `string`, the six MODEL schemas) cross into TypeScript, and this is what proves the seam still holds |
| `pnpm --dir frontend lint` | **0** |
| `pnpm --dir frontend test` | **0** — 21 files, 131 tests |
| `pnpm --dir frontend build` | **0** |

**MODEL scope, re-derived after the last edit** (`scope-audit.py MODEL`): **125 in scope, 111
evidenced (89 %), 14 without** · **40/40 endpoints published**.
