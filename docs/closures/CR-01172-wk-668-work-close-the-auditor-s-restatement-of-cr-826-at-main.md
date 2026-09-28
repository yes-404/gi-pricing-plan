---
id: CR-1172
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-668 Work close — the auditor's restatement of CR-826 at main
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-28
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-668
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
---

# CR-1172 — WK-668 Work close: the auditor's restatement of CR-826 at main

## Scope

**What closes.** WK-668, *Spike S1/S2 resolution and ADR-706 confirmation*, the Phase 2
entry gate. The roadmap row (`docs/roadmap.md`, `### WK-668`) says only: *"Must complete
before WK-669. If S1 fails, this phase is re-planned"*. Its `status:` reads `active` at
`df8e5811`.

**Why this record exists.** `CR-826` (`docs/closures/CR-00826-work-item-record-wk-668-phase-2-entry-gate.md`)
is the Work's original closure record, filed 2026-08-27 by #288 (`cdedef83`) against the
tree `e2d32ac` (#287). It says *"Closed 2026-08-27"*, but its Sign-off carries an auditor
close-confirmation only, and no maintainer line. A Work close is the maintainer's alone
(`CLAUDE.md` §13). `CR-826` is write-once and pre-migration, so it cannot be amended. This
record restates it at main, resolves each of its citations there, and carries the close to
the maintainer's line. It is filed on the deputy's instruction of 2026-09-28 (Track A).

**Scope, derived from the plan and the specification, not from `CR-826`.** The Work's plan
is `PL-817` (`docs/plans/PL-00817-wk-668-implementation-plan-spike-s1-s2-resolution-and-adr-706-confirmation.md`),
Tasks T1–T7. The requirements it confirms are in `docs/specs/03-rating-engine.md`:

- **FR-273, FR-274, FR-275, FR-276** — the four engine-boundary requirements spike S1
  produced (integer minor units across the binding, guarded division, the scale cap of 28,
  the expression vocabulary validated against the engine).
- **NFR-501, NFR-502** — `nthread=1` per `model_call`, and no `response_model` validation
  on the scoring response (spike S2).
- **ADR-706** — a dated confirmation at Phase 2 entry (PL-817 T5).

PL-817's success criterion: *"Then ADR-706 is confirmed and WK-669 proceeds."* Its failure
criterion re-opens ADR-706 and re-plans Phase 2. The output is a decision record, not a
build. PL-817's four Phase 1b carry-forwards are stated there as *"None blocks WK-668"*, and
they are not in this Work's scope.

## Checklist

The `close-workstream` skill and `docs/process/checklists/work-item-close.md`, both as they
read at `df8e5811`.

| Step | Result at `df8e5811` |
|---|---|
| Scope from the spec first | Above: PL-817 T1–T7, six requirements, one ADR addendum |
| Each deliverable exists and works | The Evidence table below; each citation resolved at main |
| The full gate | Not run: this Work adds no code. The docs checks run on this record's committed tree (Readings) |
| New checks non-trivial | None introduced by WK-668 |
| NFRs measured | NFR-501 and NFR-502 were measured by the Work (`CR-826`'s T4 row); the figures are re-read below, not re-measured |
| Owed list generated | The block below |
| Binding plan-review conditions | None names WK-668's close (below) |
| `CLAUDE.md` §14 question | Raised to the lead (below) |
| Root `README.md` pointers | Unchanged by this close |

## Evidence

**Each `CR-826` deliverable, re-read at `df8e5811`.**

| PL-817 task | Evidence at main | Verdict |
|---|---|---|
| T1 — `zen-engine` installed and pinned | `packages/pricing-core/pyproject.toml:53` pins `"zen-engine==0.53.0"`, the S1 version; `uv.lock` carries it; `docs/research/w8-spike-resolution.md` §T1 records the wheel and the import | evidenced |
| T2/T3 — S1 re-run, requirements confirmed | `docs/research/w8-spike-resolution.md:18`: *"21 checks, 0 failed"*, results beside FR-273 to FR-276. At main the four requirements also carry test markers: `@pytest.mark.req` for FR-273 to FR-276 in `packages/pricing-core/tests/test_rating_compile.py` and backend tests (predicate: `grep -rlE 'req\("(FR-273\|FR-274\|FR-275\|FR-276\|NFR-501\|NFR-502)"' backend packages --include=*.py`, 5 files) | evidenced |
| T4 — S2 latency re-run | `docs/research/w8-spike-resolution.md:83`: NFR-501 `nthread=1` p99 **1.626 ms**, 3.3 % of the 50 ms budget; `:93`: NFR-502's validation p99 **0.070 ms**. The `03` NFR-502 row carries *"Amended 2026-08-27, WK-668 — the premise's ~1 ms figure was not reproduced."* | evidenced |
| T5 — ADR-706 confirmed | `docs/adrs/ADR-00706-gorules-zen-engine-executes-rating-dags.md:80`, *"Addendum — 2026-08-27: S1 and S2 confirmed at Phase 2 entry"*, which reads *"This addendum does not change the decision … **WK-669 proceeds** on this basis."* | evidenced |
| T6 — the success decision recorded | The same addendum. WK-669 then proceeded and is `status: closed` in the roadmap (`CR-838`) | evidenced |
| T7 — the closure record and the register | `CR-826` exists at the path above; this record completes the maintainer half | evidenced, pending the line |

**The claim, not only the citation.** The pricing-core test files that carry the FR-273 to
FR-276 and NFR-501 markers were run at `df8e5811` in this record's worktree:
`uv run pytest -q packages/pricing-core/tests/test_rating_compile.py packages/pricing-core/tests/test_gbm.py`
→ **129 passed, 1 xfailed**, rc 0. The three backend files (`test_score.py`,
`test_rating_algorithms.py`, `test_startup_self_check.py`) were not run here; their
evidence is WK-669's and WK-671's closes, not this Work's.

**`CR-826`'s citations, resolved at `df8e5811`.**

| # | `CR-826` cites | Resolution at main | Resolves? |
|---|---|---|---|
| 1 | The audited tree `e2d32ac` (#287) | A commit; `git merge-base --is-ancestor e2d32ac origin/main` exits 0 | yes |
| 2 | `PL-817` by its path | The file exists at `docs/plans/PL-00817-…`; its pre-migration dated path maps to it in `docs/REDIRECTS.csv` line 147 | yes |
| 3 | `docs/research/w8-spike-resolution.md` §T1, §T2, §T4 | The file exists at that path and holds each section | yes, with a note (Finding 3) |
| 4 | `docs/adrs/ADR-00706-…` Addendum 2026-08-27 | Exists at line 80; the quoted sentence is present | yes |
| 5 | FR-273, FR-274, FR-275, FR-276, NFR-501, NFR-502 | Each is a row in `docs/specs/03-rating-engine.md`; `docs/REDIRECTS.csv` maps their pre-migration ids to them (lines 1342, 1371, 1373, 1374, 1554, 1499) | yes |
| 6 | `03` NFR-502's amendment (#287) | The dated sentence quoted above is in the NFR-502 row | yes |
| 7 | *close-workstream §0a* | `.claude/skills/close-workstream/SKILL.md`, *"0a. Evidence is not only markers"* | yes |
| 8 | `docs/findings/register.md` | Exists | yes |
| 9 | `CR-826`'s own former path | `docs/REDIRECTS.csv` line 60 maps it to `CR-826` | yes |
| 10 | Its two finding rows, in the retired workstream-finding form | Internal to `CR-826`, never register rows; `docs/REDIRECTS.csv` has no row for either | **no** — as ids. Both are closed in `CR-826` itself; see Findings |
| 11 | *"to be built by"* a workstream range, in the first finding row | The migration rewrote the range's first end to `WK-669` and left the second end in its retired form | **no** — the text no longer names a range. See Finding 1 |
| 12 | PL-817 T7's filing directory, a retired audit path | The record moved; row 9 is its resolution | yes, through row 9 |

## Owed list

**Generated, not recalled.** Run at `df8e5811`, a committed tree, in this record's worktree.
The output is verbatim, and it is evidence, not authority (RL-912).

```text
Generated by `python3 scripts/register-owed.py WK-668` against `df8e5811 (`p2-a1-wk668`)`.
Mode: work item 'WK-668'. 1 owed row(s), 0 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

- **NFR-502/501 (F-W9-1)** (work item: 'W9-3', phase: '2') — carry forward with an owner — the WK-671 scoring workstream; WK-668's measurements recorded (NFR-502 p99 0.070 ms, NFR-501 p99 1.626 ms)
```

The one row is `docs/findings/register.md:59`, the NFR-502/501 row. `docs/REDIRECTS.csv` line 292 maps its
retired id to a new row id, which has no `docs/INDEX.md` entry of its own. It matches WK-668 only because its Decision cell quotes WK-668's measurements.
Its work item is a WK-669 slice, and its owner is the WK-671 scoring workstream. It is
therefore not WK-668's residue; its resolution is in the Findings table. Every id in the
block appears in that table with a resolution, and the table adds nothing the block does
not carry except the three findings named there as having no register row.

## Findings

| Finding | Concerns | Decision | Status |
|---|---|---|---|
| The owed row (register line 59, NFR-502/501) | NFR-502 and NFR-501, carried out of WK-669 | **reassigned** (already) — WK-671 owns it, and `CR-927` §1 names it in WK-671's scope; `CR-927` verdicts NFR-501 *"delivered"* (*"Measured in WK-668: p99 1.626 ms"*) and NFR-502 *"owed, not delivered"*, carried forward. Not WK-668's to discharge | closed for WK-668 |
| Finding 1 — no register row | `CR-826`'s first finding row: the migration rewrote a workstream range into a string that is half new id and half retired form, so the sentence no longer resolves | **accept** — `CR-826` is write-once; this record states the reading: the range meant the Phase 2 build workstreams, WK-669 onward. No FD proposed | closed |
| Finding 2 — no register row | `CR-826` says *"Closed 2026-08-27"* while the roadmap row says `status: active` and no maintainer line exists | **fix before close** — this record, and the maintainer's line below | closed-with-findings when the line lands |
| Finding 3 — no register row | `docs/research/w8-spike-resolution.md` carries no RFC-937 header and has no `docs/INDEX.md` row; it is WK-668's only measurement evidence | **accept** for this close — the file resolves by path, and its content is re-read above. Whether an unheadered research file is in the create-read-retire audit's population is that Work's question, not this close's | closed |

`CR-826`'s own two finding rows stay as `CR-826` records them: both `closed`, one
*"accept"*, one *"resolved"*. Re-read at main, neither needs reopening: the requirements
now carry markers, and the NFR-502 amendment is in the spec.

**Binding plan-review conditions.** None. Searched with
`grep -ln 'WK-668' docs/closures/*.md docs/rulings/*.md` at `df8e5811`. The one plan review
among the hits, `CR-830`, names WK-668 only as the source of an amendment. No acceptance
clause names WK-668's close.

**The `CLAUDE.md` §14 question.** A workstream close raises it. Plan review 14 (`CR-1167`)
was held at the WK-697 close on 2026-09-27. Whether this close, which records a decision
taken on 2026-08-27, triggers another review is raised to the lead; it is not decided
here.

## Verdict

**Proposed by the auditor, for the lead's adoption.**

| Item | Verdict | Owner | Event |
|---|---|---|---|
| T1–T6 | evidenced | — | — |
| T7 | evidenced; the maintainer half pending | the maintainer | the dated line below |
| FR-273 to FR-276, NFR-501 | evidenced (the Work's measurement, and test markers at main) | — | — |
| NFR-502 | evidenced as a design rule; its isolated measurement is reassigned to WK-671 | WK-671's carried row | `CR-927` |
| Findings 1–3 | as the table gives | — | — |

No item is left without evidence or a verdict. The Work's success criterion is met:
ADR-706 is confirmed, and WK-669 proceeded.

**The proposed roadmap change**, made only once the line exists, in the form of WK-697's
closed row: `status: active` → `status: closed` in the `### WK-668` header block, and the
row's sentence extended with *"**Closed <date> by the deputy's dated line, by delegation, on
`CR-1172`, linked as `closures/CR-01172-wk-668-work-close-the-auditor-s-restatement-of-cr-826-at-main.md` from the roadmap.**"*

## Sign-off

Owner: the maintainer. The acceptance line is the deputy's by the maintainer's delegation of 2026-09-28, written in this record's one follow-up commit. Auditor: the restatement filed 2026-09-28.

**Maintainer acceptance:** _pending — the maintainer's dated line_
