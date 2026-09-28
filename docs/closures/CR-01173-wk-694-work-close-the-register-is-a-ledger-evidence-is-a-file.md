---
id: CR-1173
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-694 Work close — the register is a ledger, evidence is a file
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-28
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-694
corrected_by: []
relates: [FD-1174, FD-1175]
---

# CR-1173 — WK-694 Work close: the register is a ledger, evidence is a file

## Scope

**What closes.** WK-694 is *The register is a ledger, evidence is a file — RFC-896, P1–P5*.
Its roadmap row (`docs/roadmap.md`, `### WK-694`) reads `status: active` at `df8e5811`, and
records *"P1–P5 all merged 2026-08-31"*. This record is filed under the deputy's instruction
of 2026-09-28 (Track A).

**Authority.** The maintainer adopted RFC-896 in the reconciliation, `PL-900:347`:
*"Maintainer acceptance: accepted as proposed, 2026-09-01 — all four dispositions (…, RFC-896
P1–P5, …)"*. The reconciliation's own §3 gives the Work's shape: *"Scope: P1–P5 … Acceptance:
the note's own §8"*. RFC-896's five questions were ruled as `RL-909` (Q1, the ride-ahead PR),
`RL-910` (Q2, red from day one), `RL-911` (Q3, migration on amendment only), `RL-912` (Q4, the
owed list lands verbatim) and `RL-913` (Q5, files are named by the finding id).

**Scope, derived from the note and not from the build log.** Scope comes from RFC-896
(`docs/rfcs/RFC-00896-the-register-is-a-ledger-evidence-is-a-file.md`):

- §2 P1–P5: the grammar, the decay rule, the linter, the ledger/evidence split and the owed-list script;
- §8 acceptance items (a) to (e);
- §5's fifteen-row impact matrix.

The note's §4 non-goals are out of scope.

## Checklist

This close used the `close-workstream` skill and `docs/process/checklists/work-item-close.md`,
both as read at `df8e5811`.

| Step | Result at `df8e5811` |
|---|---|
| Scope from the spec first | Above: P1–P5, (a) to (e), 15 impact rows |
| Each deliverable exists and works | The Evidence tables below |
| The full gate | The docs half only. This close adds no code, and the two scripts' own tests were run (below) |
| New checks non-trivial | Check 29's red fixtures were read and run; one required broken input is missing (FD-1174) |
| NFRs measured | RFC-896 names none |
| Owed list generated | Two blocks below, and the hand reconciliation they need |
| Binding plan-review conditions | Plan review 11's acceptance binds row 15 (below) |
| `CLAUDE.md` §14 question | Raised to the lead (below) |
| Root `README.md` pointers | Unchanged by this close |

## Evidence

**The five parts.** Each was read at `df8e5811`.

| Part | Evidence at main | Verdict |
|---|---|---|
| P1 — the grammar in the register header | `docs/findings/register.md`'s header states the decision vocabulary and the ownership shapes, and check 29 holds every row to them | evidenced |
| P2 — the decay rule | The header says an unowned row that names no event *"decays to the next `CLAUDE.md` §14 plan review"* (`register.md:13`). The check behind it is a length proxy, a known defect: `FD-1023` (register line 128) | evidenced; the defect is deferred (FD-1023) |
| P3 — `scripts/register-lint.py` in the gate | Three rules are built: grammar, resolution format and decay. Check 29 runs it inside `audit-docs.py`, and `test_check_29_is_wired_into_the_docs_gate` asserts the wiring. **The owner-existence and id-uniqueness rules were not built** | partly delivered; the rest is FD-1174 |
| P4 — ledger and evidence split | `docs/findings/README.md` holds the rules. Evidence essays sit beside the register, for example `FD-935`. Migration happens on amendment: `register-lint.py` prints *"94 of 139 row(s) exceed the 1000-character … threshold"* at `df8e5811` | evidenced |
| P5 — `scripts/register-owed.py` | Built and cited by both close checklists and by the lead's charter (its enter step) | evidenced |

**Tests, run rather than cited.** In this record's worktree at `df8e5811`:
`uv run pytest -q -p no:cacheprovider tests/test_register_lint.py tests/test_register_owed.py`
→ **45 passed**, rc 0.

**Acceptance, RFC-896 §8.**

| Item | Evidence at `df8e5811` | Verdict |
|---|---|---|
| (a) The header states the grammar and decay; every open unowned row names its event | The header does (P1, P2). *"Every … names its event"* is checked only by the length proxy that `FD-1023` reports | evidenced; the check's defect is deferred (FD-1023) |
| (b) The linter is red on three named broken inputs | Two red fixtures exist: `test_a_decision_outside_the_grammar_is_refused` and `test_a_resolution_marker_with_no_date_or_reference_is_refused`. **There is no fixture for the third input, a nonexistent owner, and no rule for it** | **not met**; deferred with an owner (FD-1174) |
| (c) It runs green on the live register in CI | `docs.yml` runs `python3 scripts/audit-docs.py`, and check 29 is inside it. On a detached copy at `df8e5811`, audit-docs gives rc 0 and *"All checks passed."*. `register-lint.py` reports *"OK (0 violations)"* | evidenced |
| (d) One new finding landed split, through a real audit | The `timing_ms` finding raised by this Work's own P5 run: its register row (line 103) links `docs/findings/FD-00935-03-4-4-s-timing-ms-example-four-keys-score-one-emits-two.md` | evidenced |
| (e) One real close's owed list is the script's output, cited with its tree, and reconciles | `CR-1005` §9, *"Verbatim output, command and revision named"*, with one disclosed link deviation. `CR-1065` carries two generated blocks, each naming its revision | evidenced |

**The impact matrix, RFC-896 §5.**

| Row | Target | At main | Verdict |
|---|---|---|---|
| 1, 2 | Register header; unowned rows name events | P1 and P2 above | evidenced |
| 3 | The findings directory and its README | `docs/findings/README.md`, beside the register after the W37 migration | evidenced |
| 4, 5 | The two scripts and their tests | Above, 45 passed | evidenced (P3 in part, FD-1174) |
| 6 | Gate wiring | Check 29 inside `audit-docs.py`, which `CLAUDE.md` §11's command list runs | evidenced |
| 7, 8 | Work-item and phase close checklists | Both cite `register-owed.py`, in their Owed list steps | evidenced |
| 9, 10 | Auditor and lead charters | `.claude/roles/auditor.md` (grammar, essays, run the linter first); `.claude/roles/lead.md` (the `register-owed.py` enter step) | evidenced |
| 11, 12 | `close-workstream` §5b; `phase-review`'s agenda of decayed rows | Both present | evidenced |
| 13 | Append the §7 questions to `docs/open-questions.md` | Not done. The questions were ruled directly as `RL-909` to `RL-913`, so no question was ever left open | **accept** (the lead's ruling, 2026-09-28) |
| 14 | The roadmap row | `### WK-694` | evidenced |
| 15 | An adoption plan | None filed. Plan review 11 proposal 11.5 accepts the deviation as deliberate and dated, and the maintainer accepted it on 2026-09-01 (`CR-932`) | accepted deviation |

## Owed list

**Generated, not recalled.** Both runs used `df8e5811`, a committed tree, on a detached copy.
The output is verbatim, and it is evidence, not authority (`RL-912`).

```text
Generated by `python3 scripts/register-owed.py WK-694` against `df8e5811 (detached)`.
Mode: work item 'WK-694'. 0 owed row(s), 0 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

(none)
```

```text
Generated by `python3 scripts/register-owed.py RFC-896` against `df8e5811 (detached)`.
Mode: work item 'RFC-896'. 1 owed row(s), 0 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

- **`register-lint.py` (check 29) was blind to 11 of 59 register rows and printed `OK (0 violations)` throughout (F64)** (work item: 'RFC-896 P5', phase: '2') — accept — the defect is fixed and regression-tested (`f99b55d`, #521); no owner is owed further work. The event that would reopen this row is a future regression in `parse_register`'s blank-line handling — guarded today by `tests/test_register_lint.py`'s new coverage, not by this row
```

**Hand reconciliation, and why it is needed.** The Work key finds nothing. This Work's own
three findings carry work-item cells that no key selects:

| Register row | Its work-item cell | Found by |
|---|---|---|
| line 103, the `timing_ms` example (`FD-935`) | a WK-671 task | neither key |
| line 105, the WK-671 owed-list recurrence | `—` | neither key |
| line 106, check 29's blind rows | `RFC-896 P5` | the `RFC-896` key |

This is the selection-predicate class `FD-1165` reports. Two of the three rows are reconciled
by hand here, because no key finds them. Every row in the two blocks, and both hand-reconciled
rows, appears in the Findings table with a resolution. The table adds nothing beyond them
except the two findings this close files and the known defect `FD-1023`.

## Findings

| Finding | Concerns | Decision | Status |
|---|---|---|---|
| Register line 103 (`FD-935`) | `03` §4.4's `timing_ms` example against `score_one` | **Resolved 2026-08-31**, `RL-931` (PR #528): the example was corrected to the two keys the engine emits | closed |
| Register line 105 | The WK-671 close's owed-list sweep | **deferred with an owner — the maintainer** (`CR-1167`). Reopening a Work close is the maintainer's alone. It does not block this close. Event: the maintainer's own dated ruling on F63 (`CR-1167:82`); not this close's acceptance line | carried |
| Register line 106 | Check 29 read 48 of 59 rows while reporting OK | **accept** — fixed and regression-tested (`f99b55d`, #521) | closed |
| `FD-1023` (register line 128) | The decay rule's check is a length proxy | **deferred with an owner — the lead** (`CR-1167`). Event: the create-read-retire audit's first slice | carried |
| `FD-1174` (filed here) | P3's owner-existence and id-uniqueness rules, and the third broken input of (b), were never built | **not started; deferred with an owner — the lead**. Event: the first slice of WK-1170, the create-read-retire audit | carried |
| `FD-1175` (filed here) | Adopted RFCs still read `status: draft`: 6 of 20, including RFC-896 | **deferred with an owner — the lead**. Event: WK-1170's first slice (lifecycle transitions). RFC-896's status is **not** changed by this close | carried |
| Impact row 13 | Open questions never appended | **accept** — ruled directly (`RL-909` to `RL-913`) | closed |

**Taken over by WK-1170** (the create-read-retire audit, first slice): RFC-896 §8 (b), as
FD-1174; the RFC lifecycle gap, as FD-1175; and the decay check, already routed there as
FD-1023.

**Binding plan-review conditions.** Plan review 11 (`CR-932`) proposal 11.5: *"Accept RFC-896
impact-matrix row 15 as a deliberate, dated deviation … close the row on that basis"*. It was
accepted on 2026-09-01. The artifact it asks for is that dated paragraph in `CR-932` itself,
which exists. No other acceptance clause names WK-694's close. I searched with
`grep -ln 'WK-694\|RFC-896' docs/closures/*.md` at `df8e5811`.

**The `CLAUDE.md` §14 question.** A workstream close raises it. The lead has routed the
proposal to the deputy: one plan review, after the last of today's Work closes, covering all
five. This record does not decide it.

## Verdict

**Proposed by the auditor and adopted by the lead** on 2026-09-28, in the lead's messages of
that day.

| Item | §13 verdict | Owner | Event |
|---|---|---|---|
| P1, P2, P4, P5 | evidenced | — | — |
| P3 | delivered in part; the rest **not started, deferred with an owner** (FD-1174) | the lead | WK-1170's first slice |
| (a) | evidenced; its check's defect **deferred with an owner** (FD-1023) | the lead | WK-1170's first slice |
| (b) | **not met; deferred with an owner** (FD-1174) | the lead | WK-1170's first slice |
| (c), (d), (e) | evidenced | — | — |
| Impact rows 1–12, 14 | evidenced | — | — |
| Impact row 13 | accept | — | — |
| Impact row 15 | accepted deviation (`CR-932` 11.5) | — | — |
| The WK-671 owed-list row (line 105) | **deferred with an owner** | the maintainer | the maintainer's own dated ruling on F63 (`CR-1167:82`); not this close's acceptance line |
| FD-1175 | **deferred with an owner** | the lead | WK-1170's first slice |

No item is left without evidence or a verdict. WK-694's delivery is complete except for
what the table defers, and each deferral names an owner and an event.

**The proposed roadmap change** follows WK-697's closed row and is made only once the line
exists. In the `### WK-694` header block, `status: active` becomes `status: closed`. The row's
sentence is extended with *"**Closed <date> by the deputy's dated line, by delegation, on
`CR-1173`**, with RFC-896 §8 (b) deferred to WK-1170 as FD-1174."*

## Sign-off

The owner is the maintainer. The acceptance line is the deputy's, by the maintainer's
delegation of 2026-09-28, and is written in this record's one follow-up commit. The auditor
filed this record on 2026-09-28.

**Maintainer acceptance:** **2026-09-28 12:33:02 BST — WK-694 (The register is a ledger, evidence is a file — RFC-896, P1–P5) is CLOSED**, written by the deputy by the maintainer's delegation of 2026-09-28, on `CR-1173` (`kind: work`, auditor-a) as read by me at `p2-a2-wk694` `8aa376c7`, with the lead's adoption of its verdicts.
- The scope is taken from RFC-896 (§2 P1–P5, §8 (a)–(e), and §5's fifteen impact rows), not from the build log. P1, P2, P4 and P5 and acceptance items (c), (d) and (e) are evidenced. The two scripts' tests were run: 45 passed.
- **The close is accepted over one acceptance item not met.** RFC-896 §8 (b) requires `register-lint.py` to be red on three named broken inputs. Two exist. **The third, a nonexistent owner, has no rule and no fixture.** P3's owner-existence and id-uniqueness rules were never built. I read this at `8a8cded3`: `scripts/register-lint.py` defines only `check_decision_grammar` (:352), `check_resolution_annotation` (:372) and `check_unowned_decay` (:399). It is accepted as **not started, deferred with an owner**: `FD-1174`, the lead, to be done in the first slice of WK-1170 (the create-read-retire audit, `status: active`). `FD-1175` (adopted RFCs still reading `draft`) and `FD-1023` (the decay check's length proxy) go to the same owner and event.
- Impact row 13 (the questions were ruled directly, `RL-909` to `RL-913`) is accepted. Row 15 is the accepted deviation (`CR-932` 11.5).
- **Register line 105 (F63, the WK-671 close's possible owed-list recurrence) is not disposed by this line.** It is a question of reopening a Work close, which is the maintainer's alone. It is carried as `CR-1167:82` states it: owner **the maintainer**, event **the maintainer's own dated ruling**. The maintainer kept it out of the delegation on 2026-09-27. It does not block this close.
- The `CLAUDE.md` §14 question is answered by my ruling of 11:28 BST today: plan review 15 follows the four paperwork closes.
