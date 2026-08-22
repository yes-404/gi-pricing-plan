# SDD ledger — plan: .planning/2026-08-19-psi-comparison-selector.md

Spec: `docs/specs/01-data-management.md` §5.3 / FR-DATA-28 / `01` §4.4 VR-DST-1 — read, reachable.
Branch: `feat/psi-comparison-selector`. BASE at start: `e8f3bda`.
Decision gate answered by the maintainer before execution: **route query (option A)**.

## Pre-flight scan

### Pairs sharing a file or an interface

| Tasks | Produces → consumes | Finding |
|---|---|---|
| T1 → T6 | `docs/open-questions.md` OQ-DATA-11 row; `01` §10 mirror | Both edit the same two files. T1 writes §10 + the OQ row; T6 edits §5.3 and the OQ row's status. Different sections — no textual overlap. **But see Ruling 1**: T1's Step 6 asks the maintainer a question already answered. |
| T2 → T4 | `ColumnComparison` type export | Consistent. T4's `driftFor()` return type needs it; T2 adds it. |
| T2 → T5 | `psiBand(psi: number)` narrowed | Consistent. T5's `band` computed guards `psi != null` before calling. |
| T3 → T4 | `referenceId: Ref<string \| null>`, `siblings: Ref<DatasetVersion[]>` | Consistent. T4's watcher and `referenceLabel` consume both under those exact names. |
| T4 → T5 | `driftFor(name): ColumnComparison \| null \| undefined` | Consistent. T5's prop union is written identically. |
| T3 → T4 | `COMPARISON` test fixture: declared `unknown = null` in T3 Step 1, replaced by a typed `ProfileComparison` in T4 Step 1 | Consistent and flagged in both places. T3's `stub()` passes it to `json()` which takes `unknown`; nothing reads it in T3. |
| T3, T4, T5 | all three modify `ProfileView.vue` and `ProfileView.test.ts` | Sequential only. No parallel dispatch of these three. |

### Per-task self-consistency

| Task | Tests specified vs code specified | Finding |
|---|---|---|
| T1 | docs only, no tests | Agrees with itself. |
| T2 | `profiles.test.ts` — threshold test + a `@ts-expect-error` null test | **DEFECT — see Ruling 2.** The null test's runtime assertion (`expect(() => psiBand(null)).toBeDefined()`) is vacuous, and `.claude/skills/vue-frontend` states type assertions in a `*.test.ts` are tests that can never fail. |
| T3 | selector tests vs the `<select>` and `load()` extension | Agrees. `version.id` in Step 5 refers to the local const already in `load()` (existing line 48), not the route prop. |
| T4 | row-count and 404 tests vs the watcher and template | Agrees. |
| T5 | 6 component tests vs the two-root `v-if`/`v-else-if` template | Agrees. Two false roots render comment placeholders, so `textContent.trim()` is `""`. |
| T6 | docs only, no tests | Agrees. Step 4 is conditional on T1's outcome — see Ruling 1. |

### Rulings made before execution

**Ruling 1 — T1 Step 6 records the decision rather than asking for it.** The maintainer
answered the decision gate (route query) when commissioning this execution, so the plan's
"ask the maintainer and stop" step is already satisfied. T1 writes the OQ-DATA-11 row as
**decided 2026-08-19** in one commit, striking the question and prefixing the id per the
convention of the decided rows above it. T6 Step 4 becomes a verification, not an edit.
*Cost if wrong:* the OQ row records a decision the maintainer did not make — visible in the
PR diff and cheap to reword.

**Ruling 2 — T2's type-level assertion moves to `profiles.test-d.ts`.** The plan puts a
`@ts-expect-error` null-refusal test in `profiles.test.ts`, where its only runtime assertion
is `toBeDefined()` on a function reference — vacuous, and the exact defect the review rubric
names. `.claude/skills/vue-frontend` records the repo rule: *"`expectTypeOf` is erased at
runtime. A type assertion in a `*.test.ts` is a test that can never fail... Type assertions go
in `*.test-d.ts`"*, and `vitest.config.ts` runs typecheck over `src/**/*.test-d.ts`. So T2
creates **two** files: `profiles.test.ts` with the threshold test only, and
`profiles.test-d.ts` asserting `psiBand`'s parameter type refuses `null`. The spec intent —
an unmeasured PSI cannot be banded — is unchanged; only the instrument that proves it moves to
the one that can actually fail. *Cost if wrong:* one extra small file; the threshold coverage
is identical either way.

**Ruling 3 — the plan's own frontend test-count estimates are not acceptance criteria.**
The plan states "the suite is 115 now" and similar. Ruling 2 changes the count. Implementers
report the real number the run prints; a mismatch with the plan's arithmetic is not a finding.
*Cost if wrong:* none — the gate is the exit code, not the tally.

## Environment (established by the controller before Task 1)

A fresh worktree has no `frontend/node_modules` and no generated API client — both are
git-ignored. Controller ran, all exit 0:
- `pnpm --dir frontend install --frozen-lockfile`
- `pnpm --dir frontend generate:api` (openapi-typescript 7.13.0)
- `pnpm --dir frontend test` — **baseline 113 passed, 18 files, `Type Errors no errors`**

That last line confirms Ruling 2's premise: `vitest run` executes the `*.test-d.ts` typecheck
pass, so a type-level assertion there can actually fail. `pnpm` is at `~/.npm-global/bin`,
not on the default PATH.

## Task log

Task 1: implementer DONE — commit `cb8480d`, `audit-docs.py` exit 0, 66 questions all mirrored
(65 + 1). Implementer flagged a **plan defect**: the brief's Step 3 showed `01` §10 as a bullet
list; the real file uses a two-column table. It followed the file. Ruling: the file is right and
the plan's example was invented — no action beyond noting it here, since §10's format is not
something this slice changes.

Task 1: review — spec ✅, quality Not approved. 1 Important (false cost claim: "eleven existing
view tests"; verified — 10 view test *files*, 0 mocking vue-router, 11 `it()` blocks in
`ProfileView.test.ts`. The plan meant the latter; the sentence reads as the former and so reads
as false in a permanent record). Fix round 1 dispatched.

Task 1: **Ruling: no new `FR-` id for OQ-DATA-11.** The reviewer noted every other
`decided (in spec)` row cites a numbered requirement and this one cites none. Where a view holds
transient UI state is not a requirement-level contract — `01` §5.3's Contents column already
carries the obligation, and an FR for it could only assert "the URL has a query param", which is
a requirement nothing can meaningfully test. *Cost if wrong:* a later slice wanting a normative
anchor appends one; the decision text is already in the spec file either way.

Task 1: **Ruling: the ⚠️ (roadmap:763's Pinia row now stale) is not a Task 1 gap.** Task 6
Step 3 owns that row and rewrites it. Editing it here would put the same claim in two commits.
*Cost if wrong:* none while Task 6 runs; if Task 6 were dropped the row would stay stale, so
Task 6 must not be skipped.

Task 1: fix round 1/5 (1 addressed, 0 open; commits cb8480d..c113a00). Re-review: ADDRESSED,
no new breakage, audit-docs still 0 / 66 mirrored.
Task 1: complete (commits e8f3bda..c113a00, review clean).

Task 2: implementer DONE — commit `6434dbf`, 115 tests / 20 files, lint 0, type-check 0.
Ruling 2 vindicated: the `.test-d.ts` assertion produced a real TypeCheckError before the fix
and passes after, so the instrument can actually go red. Review: spec ✅, quality Approved,
zero findings (reviewer confirmed `toEqualTypeOf<number>()` is strict enough to catch a
re-widened signature).
Task 2: complete (commits c113a00..6434dbf, review clean).

Python baseline in this worktree (controller, before Task 3 landed): `uv sync --all-packages
--dev` 0, ruff 0, mypy 0, lint-imports **3 kept / 0 broken**. This slice touches no Python, so
Task 6 should see these unchanged.

Task 3: implementer DONE — commit `04fc769`, 119 tests / 20 files, lint 0, type-check 0.
**Two plan defects found and fixed by the implementer:**
(i) the brief's `stub()` matched the versions list with `url.includes("/versions")`, which also
matches `getVersion()`'s single-version lookup `/datasets/{slug}/versions/{n}` — narrowed to
`/\/versions(\?|$)/`. My pre-flight scan warned about a `/versions` vs `/profile` collision and
named the wrong pair; the real collision is list-vs-single-lookup.
(ii) the brief's `<option :value="null">` cannot round-trip to `""` because a native `<option>`
with no `value` attribute falls back to its text content — implementer added a
`referenceSelection` computed bridging `""` ↔ `null`, keeping `referenceId` as
`Ref<string | null>` per the declared interface.
Both deviations sent to the reviewer for judgement on merit rather than accepted on report.

Task 3: review — spec ✅, quality Not approved. Both deviations judged **correct and kept**. The
reviewer mutation-tested: changing the URL write-back to a literal `"zzz"` and forcing every
option `disabled` each left **all 119 tests passing** — two tests that do not gate.

Task 3: **Ruling: three findings reclassified Minor → Important.** (a) the stale `?against` left
in the URL when the query names an unprofiled version — the address bar then advertises a
comparison the view refuses, which is user-visible incorrectness in the feature this task
delivers, not a cosmetic gap; (b) the disabled-option test that passes with *everything*
disabled; (c) the "back/forward" claim in the OQ-DATA-11 row. The slice's entire subject is
guards that actually fail, so a test proven not to gate is not a minor here. *Cost if wrong:*
one extra fix round on work that was otherwise shippable.

Task 3: **Ruling: narrow the back/forward claim rather than build back/forward.** Seeding runs
only in `onMounted`, so a query-only navigation does not re-seed. Making it re-seed needs a
watcher on the query that can round-trip against the write-back watcher, for a capability no
requirement asks for. The row is corrected to claim reload-survival and shareability only.
*Cost if wrong:* if someone later wants back/forward, it is a watcher plus a guard — additive,
and the row does not have to be un-said.

Task 3: deferred minors (parked, for the final review to triage): redundant `router.replace`
fired on mount when `?against` is already valid; `truncated` and the empty-state branch
untested; preservation of other query keys untested; non-numeric / nonexistent `?against`
correct by construction but untested; `COMPARISON` placeholder dead until Task 4.

Task 3: fix round 1/5 (5 addressed, 0 open; commits 04fc769..b39a825). Re-reviewer **re-ran the
mutation proof itself** rather than trusting the report: mutating `String(chosen.version)` →
`"zzz"` produced 1 failed / 119 passed, failing exactly at the new assertion; restored and
verified; `git status` clean afterwards. 120 tests, audit-docs 0 / 66.
Task 3: complete (commits 6434dbf..b39a825, review clean).

Interfaces Task 3 actually left behind (Task 4 and 5 must build on these, not on the brief):
- `referenceId: Ref<string | null>` (a version **id**), `siblings: Ref<DatasetVersion[]>`,
  `truncated: Ref<boolean>`.
- `referenceSelection` — a computed bridging the `<select>`'s `""` to `referenceId`'s `null`.
- `load()` is now **two** try/catch blocks: the profile block sets `problem`; the siblings block
  swallows its `ProblemError` so a failing versions list cannot blank a loaded profile.
- the `?against` ignore branch explicitly clears the key via `router.replace`.
- `stub()` already carries the `compare` third parameter and its `/compare` branch, and the
  `COMPARISON: unknown = null` placeholder is in place awaiting Task 4's typed fixture.

Task 4: implementer DONE — commit `e1372b8`, 122 tests / 20 files, lint 0, type-check 0.
Review: spec ✅, quality **Approved**, one Minor. Reviewer ran its own mutation (forcing
`referenceLabel` to `""`) and found exactly one failing test — a mutation the implementer's own
proof had not covered — then restored, `git status` clean.
Task 4: minor (deferred → carried into Task 5 as mandatory): `defineExpose({ driftFor })` was
added purely to silence `@typescript-eslint/no-unused-vars` while `driftFor` has no caller. The
reviewer verified lint really does fail without it, but judged the cited precedent
(`defineExpose({ isProblem })` in `FactorWorkbenchView.vue`) **not genuine** — that one papers
over an import that is never called anywhere in the file, i.e. pre-existing dead code. Task 5
mounts `ColumnDrift` and gives `driftFor` a real template caller, so the expose **must be
removed there**, not left optional.
Task 4: complete (commits b39a825..e1372b8, review clean — 1 minor carried forward).

Observation for the final review (pre-existing, NOT introduced by this branch):
`FactorWorkbenchView.vue:257` exposes `isProblem`, which that file never calls in script,
template or its own test. Out of scope for this slice; worth a separate cleanup.

Task 5: implementer DONE — commit `5603a8e`, 129 tests / 21 files, lint / type-check / build 0.
`defineExpose({ driftFor })` deleted as required. Review: spec ✅, quality Not approved.
The reviewer judged the **re-aimed guard correct and stronger than the one it replaced** —
mutation-proved: the old amber/red-only assertion would have passed against an *emerald*
null-is-stable band, and the added `/^PSI /` check is what catches it. Narrowing was exactly as
far as the change forced.

Task 5: **Ruling: three findings reclassified Minor → Important.** (a) the view's `undefined`
pass-through is unpinned — mutating the mount to `?? null` makes every card read "new in this
version" pre-comparison with a green suite; (b) the re-aim dropped `not.toContain("psi-")`,
which the change did not require and which still holds — narrowing a guard further than forced
is weakening it, and I have held that line all branch; (c) the mean-shift render is asserted
nowhere. A reviewer has now caught non-gating assertions on this branch four times, so a test
that cannot fail is the defect class here, not a nicety. *Cost if wrong:* one extra fix round on
work already passing its gates.

Task 5: the finding that justifies the round — the reviewer swapped `TONE`'s `stable` and
`shifted` colours and **all 129 tests passed**, so a column past VR-DST-1's 0.10 warn threshold
could render in the calm tone. That is this slice's own defect one band over.

Task 5: fix round 1/5 (4 addressed, 0 open; commits 5603a8e..add19db). Test-only diff (24
insertions, 0 deletions, no production file). Re-reviewer re-ran two proofs itself — swapping
`TONE` now fails both new colour tests; mounting `driftFor(...) ?? null` now fails the
pre-comparison assertion. Tree clean. 131 tests / 21 files.
Task 5: complete (commits e1372b8..add19db, review clean).

Task 6: implementer DONE — commit `6ddca5d`, docs only, not pushed, no PR (I scoped the push
and PR out of the task; the branch's ending is mine). **Full gate green, both halves, every
number as predicted:** audit-docs 0 / 66 questions · req-coverage 482 requirements, 227 marked ·
generate-contracts --check 0, **21 contracts match** · ruff 0 · mypy 0 (125 files) ·
lint-imports 3 kept / 0 broken · **pytest 1339 passed, zero skipped** · demo-guide 11 passed ·
clean-`node_modules` reinstall 0 · generate:api / lint / type-check 0 · **131 tests / 21 files** ·
build 0.
Task 6: declared deviation — my brief named two roadmap rows; the implementer found **two more**
stale mentions of this selector in the same file ("still absent … zero callers" in the §5.3 views
row, and the "Six §5.3 Contents items" tracking row) which would have contradicted the rows the
brief did resolve. It fixed both and documented rather than silently expanding scope. Sent to
review for judgement on necessity, accuracy and style.
Task 6: review — spec ✅, quality Approved, zero findings. Reviewer independently verified all six
factual claims against source and found no stale "unbuilt" claim left in either document; judged
the two extra roadmap edits necessary, accurate and in style.
Task 6: complete (commits add19db..6ddca5d, review clean).

Branch pushed and opened as **PR #119** on the maintainer's instruction; CI settled **CLEAN**.

Final whole-branch review (9 commits, e8f3bda..6ddca5d): **approve**, one Important. Traced the
feature end to end and found no seam defect — both watchers read live state, nothing watches the
query so `router.replace` cannot loop, and vue-router 4 resolves a duplicate replace rather than
rejecting (so the parked redundant-replace is genuinely inert). Verified `psiBand`'s 0.10/0.25
against `validate.py:1459-1464`'s actual `warn_above`/`fail_above` defaults — §5.3's "cannot
disagree about one number" claim holds.
Final review: **Important — the comparison's direction is unpinned.** Inverting
`compareProfiles(versionId.value, id)` left all 131 tests passing; an inverted comparison is not
a crash but a plausible-looking backwards drift screen. One fix dispatch sent.
Final review triage of parked items — all five judged **fine to defer**: redundant on-mount
replace (inert), `truncated`/empty-state (no numeric or governance claim), other-query-key
preservation (correct by construction, no other key exists on this route), non-numeric/nonexistent
`?against` (hand-edited URL only, though the cleanup is asymmetric with the unprofiled case —
worth a follow-up), and `FactorWorkbenchView`'s dead expose (pre-existing, out of scope).
Two further deferred minors it added: stale comparison on deselection unpinned; the view-level
"new in this version" wiring unpinned (its `undefined` sibling is pinned).

