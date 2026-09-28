---
id: CR-1176
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-695 Work close — file taxonomy, reference coding and custody
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-28
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: 62d5fbae554be573ff4801d1bce45c575161c90d
phase: P2
work: WK-695
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
---

# CR-1176 — WK-695 Work close: file taxonomy, reference coding and custody

## Scope

**What closes.** WK-695 is *File taxonomy, reference coding and custody — RFC-897 Stages
2–5*. Its roadmap row (`docs/roadmap.md`, `### WK-695`) reads `status: active` at `62d5fbae`.
This record is filed under the deputy's instruction of 2026-09-28 (Track C).

**Scope, derived from the note and the row, not from the build log.** The scope is RFC-897
(`docs/rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md`)
Stages 2 to 5 (§4 to §7), built against the ruled inputs `RL-941` to `RL-948`. Its acceptance
is the note's §11, items (a) to (g). Stages 0 and 1, and the notes move, are not WK-695's.
They are the investigation plan `PL-929`'s four slices, and all four are ancestors of main
(`git merge-base --is-ancestor` exits 0 for each):

- Slice 1: `cbf1365`, #540
- Slice 2: `4f95fb3`, #537
- Slice 3: `9e70469`, #545
- Slice 4: `1ec453b`, #544

**The row's own supersession clause decides most of the scope.** The row carries *"SUPERSEDED
IN PART 2026-09-02 by WK-697"*. RFC-937 §9 *"replaces **Stages 2 and 5** outright"*, and
*"**Stages 3 and 4 survive** … they become the two downstream Works RFC-937 §8's closing
sentence names"*. The lead recorded that disposition under the maintainer's delegation at
`docs/rulings/RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`.
The two downstream Works are now roadmap rows:

- WK-1169, the charter investigation;
- WK-1170, the create-read-retire audit.

They were minted by `CR-1167` Proposal 5.1, accepted by delegation on 2026-09-27, and are both
`status: active`. WK-697 itself is closed, on `CR-1164`.

## Checklist

This close used the `close-workstream` skill and `docs/process/checklists/work-item-close.md`,
both as read at `62d5fbae`.

| Step | Result at `62d5fbae` |
|---|---|
| Scope from the spec first | Above: RFC-897 Stages 2–5 and §11 (a)–(g) |
| Each deliverable exists and works | The Evidence table below. Each stage is delivered elsewhere or carried |
| The full gate | Not run: this close adds no code. The census tests and the scan-root test were run (below) |
| New checks non-trivial | None introduced by WK-695 |
| NFRs measured | RFC-897 names none |
| Owed list generated | Two blocks below |
| Binding plan-review conditions | `CR-1167` Proposal 5.1 (below) |
| `CLAUDE.md` §14 question | Answered by the deputy's ruling of 2026-09-28: plan review 15 follows the four paperwork closes, and this is one of them |
| Root `README.md` pointers | Unchanged by this close |

## Evidence

**The four stages.**

| Stage | What it was | Where it went, at `62d5fbae` | Verdict |
|---|---|---|---|
| 2 — the reference-coding standard | Filename grammar and header per category, citation forms, a `file-lint.py` in the gate | Replaced by RFC-937's standard (§1) and built by WK-697: the header templates in `docs/_templates/`, `scripts/doc-id.py` and audit-docs checks 30–39. `CR-1164` §2 records ten broken-input proofs. No `file-lint.py` exists; the checks took its place | **reassigned** — delivered by WK-697 (`CR-1164`) |
| 5 — migration and enforcement | The prospective standard from a flag-day; legacy migrating on amendment | Replaced by RFC-937 §4's one-time migration (`71f5a22`, #782). The row's *"never a bulk rename"* constraint was lifted by RFC-937 §9 | **reassigned** — delivered by WK-697 (`CR-1164`) |
| 3 — the ownership map | The category × role matrix in `docs/process/`, each cell citing its charter line (RL-945) | Not built as a WK-695 deliverable. It is WK-1169's subject: *"the ownership table of `document-ids.md` section 1.6 made binding in each role charter"* | **deferred with an owner** — WK-1169, event its first slice |
| 4 — the workflow-loop audit | The create/read/retire triple per category; verdicts over the unreferenced population (RL-943) | Not built as a WK-695 deliverable. It is WK-1170's subject: *"the process step for each transition in the state machines of `document-ids.md` section 1.2"* | **deferred with an owner** — WK-1170, event its first slice |

**Acceptance, RFC-897 §11.**

| Item | Evidence at `62d5fbae` | Verdict |
|---|---|---|
| (a) The census script runs green in the gate, and its output at the close tree is committed | `scripts/file-census.py` exists, and audit-docs loads it (`_FILE_CENSUS_PATH`). Its tests run in the gate's pytest half: `uv run pytest -q tests/test_file_census.py` → 29 passed. **The only committed output is `docs/research/file-census-5ef559d.csv`, at `5ef559d`, not at a close tree** | first half evidenced; the committed close-tree census is **reassigned** to WK-1170, whose Stage 4 work consumes it |
| (b) Every tracked file resolves to exactly one category | Replaced by RFC-937's families: `doc-id.py check` rc 0 and `docs/INDEX.md` at `62d5fbae`. The residual population is RFC-937 §7 (g), a standing, disclosed FAIL deferred by `CR-1164` | **reassigned** — WK-697 |
| (c) The category × role matrix has no unfiled empty row | Stage 3 | **deferred with an owner** — WK-1169 |
| (d) The unreferenced plans each carry a verdict | Stage 4 | **deferred with an owner** — WK-1170 |
| (e) `file-lint.py` is red on three broken fixtures | Replaced by checks 30–39 and their broken-input proofs (`CR-1164` §2) | **reassigned** — WK-697 |
| (f) One new file of each high-traffic category is born through the updated skills | Born under RFC-937's templates after the migration: `PL-1144` (plan), `RL-1145` (ruling), `LG-1148` (ledger) | **reassigned** — WK-697 |
| (g) The notes move's own acceptance holds at the close tree | The move landed (`1ec453b`, #544). RFC-937 then migrated the note family to `RFC-` (D7). The directory (g) tests no longer exists at `62d5fbae`, and `scripts/audit-docs.py:176` resolves `NOTES` to `docs/rfcs/` after the migration. Item (g) cannot be measured as written | **reassigned** — WK-697; overtaken by the migration |

## Owed list

**Generated, not recalled.** Both runs used `62d5fbae`, a committed tree, in this record's
worktree. The output is verbatim, and it is evidence, not authority (`RL-912`).

```text
Generated by `python3 scripts/register-owed.py WK-695` against `62d5fbae (`p2-c2-wk695`)`.
Mode: work item 'WK-695'. 0 owed row(s), 0 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

(none)
```

```text
Generated by `python3 scripts/register-owed.py RFC-897` against `62d5fbae (`p2-c2-wk695`)`.
Mode: work item 'RFC-897'. 2 owed row(s), 0 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

- **Roster publishing emits a constant (F31)** (work item: 'WK-671 restart cleanup', phase: '2') — **deferred with an owner — the lead**, 2026-09-27 (`CR-1167`, plan review 14; accepted by delegation 2026-09-27 16:18:24 BST). Event: the charter investigation's first slice (it is a charter clause). `watcher.md:26-28` still states the derivation; `:33-40` marks it UNIMPLEMENTED. It is disclosed, not fixed. This supersedes the owner and event of the opening kept below: carry forward — **(b)'s owner decided: the §14 review**, as a fourth charter amendment beside R6's three (RL-860) — drop `watcher.md`'s clause describing derived roster state, which now has no implementation at all, the honest state and better than one that lies. **(a) needs no owner: already discharged** — `update-roster.sh` was always handover-local; "do not carry it forward" is satisfied by not carrying it, not by removing anything from this repository. **A successor either builds the derivation or the charter drops the claim** — the one thing it must not do is inherit a constant with a live timestamp. Same shape as pilot finding P6 (a documented mechanism nothing performs), sharpened: here a freshness indicator updates while the content it vouches for is frozen, which is `RFC-789`'s "a boundary metric reads zero by construction" in a different dress. ***Verified still open 2026-08-31*** — review 9 (`docs/closures/CR-00925-plan-review-9-at-wk-671-s-close.md:760-762`, proposal 5.3) drafted exactly this row's "charter drops the claim" branch and recommended applying it, but stated explicitly it is "not decided here." At `036337e` neither branch is yet taken: `watcher.md:11-24` still describes the derivation (with the UNIMPLEMENTED caveat) rather than dropping it, and no derivation has been built. The owner (the §14 review) has now acted — drafted, not applied — so this row's discharge is the maintainer's acceptance of proposal 5.3 followed by the role-file edit, not further register work. ***Amended 2026-09-01*** — the sentence above read *review 10* (`docs/closures/CR-00925-plan-review-9-at-wk-671-s-close.md:760-762`, proposal 5.3); corrected to **review 9**: plan-reviews.md carries exactly one proposal 5.3, and it sits in review 9's section (prose `:1979-1981`, table row `:2066`; review 9 spans `:1233-2150`, review 10 begins `:2151`). Found auditing the RFC-897 landing package (PR #549). The discharge sentence's unqualified *proposal 5.3* is thereby review 9's
- **`audit-docs.py`'s notes scan root skips silently when absent (F56)** (work item: 'RFC-897 investigation', phase: '2') — carry forward with an owner — `docs/plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md` Slice 1 (merged as a proposal, `826d636`, #508) names this exact defect, cuts a scan-root hard-fail as its first slice specifically because this hole blocks the notes-directory move safely, and specifies the TDD test and acceptance criteria. Proposal only as of this filing — nothing scheduled, the acceptance line undated — so the owner is named, not yet discharged
```

**Reconciliation.** The Work key finds nothing. The note key finds two rows, and both are in
the Findings table with a resolution. As with `FD-1165`'s class, a row whose Work-item cell
names neither key would not be found. I also searched every cell of `docs/findings/register.md` with
`grep -n 'WK-695\|RFC-897' docs/findings/register.md`. It returns one more row, line 110, the
runtime-state writer (`FD-1007`). That row names WK-695 only as a command argument in its
reproduction (`cycle --work WK-695`), so it is not about this Work and is not owed by it.

## Findings

| Finding | Concerns | Decision | Status |
|---|---|---|---|
| The roster-constant row (register, the note key's first hit) | Roster publishing emits a constant | Already **deferred with an owner — the lead** (`CR-1167`). Event: the charter investigation's first slice, WK-1169. Not WK-695's to discharge | carried |
| The scan-root row (register line 97) | `audit-docs.py`'s notes scan root skipped silently when absent | **Resolved 2026-09-28**, set in place in this PR. Fixed by `cbf1365` (#540). Verified at `62d5fbae`: `scripts/audit-docs.py:461` reads `if not NOTES.is_dir():` and fails with *"does not exist — checks 16-20 cannot run"*. Check 25's loop at `:793` fails a missing root the same way. `tests/test_audit_docs_scan_roots.py` gives 1 passed | closed |
| Acceptance (a), second half | No census committed at a close tree | **reassigned** to WK-1170 | carried |
| Acceptance (g) | Measures a directory the migration removed | **reassigned** to WK-697; it cannot be measured as written | closed |

**Binding plan-review conditions.** `CR-1167` Proposal 5.1, accepted by delegation on
2026-09-27. It mints the two downstream Works *"so that the deferrals … wait on a row with a
status rather than on a name"*. The artifact it asks for is the two rows, and both exist
(`### WK-1169`, `### WK-1170`). No other acceptance clause names WK-695's close.

## RFC-897 disposition

The maintainer instructed on 2026-09-28 that RFC-897 lands with this close. The deputy relayed
the instruction and set its form. RFC-897's header moves to `closed` in this record's follow-up
commit, and only its `status:` field changes, because the family is frozen. This section is the
account of where each part of RFC-897 went. Every citation was read at `62d5fbae`.

**Adoption, as a dated fact** (the deputy's wording, verbatim): adopted 2026-09-01: Stages 0–1 by the maintainer's acceptance of PL-929 (`f57d335`, #532); Stages 2–5 as one Work row by `PL-900` §8's acceptance block; the header was never moved `draft → active` (FD-1175).

`f57d335` is PR #532, dated 2026-09-01. Its subject records the investigation plan (`PL-929`)
"accepted as filed", and it is an ancestor of main. `PL-900`'s acceptance line is at `:347`, inside its section 8.

| RFC-897 part | Where it landed | Status |
|---|---|---|
| Stage 0 — the census (§2) | `scripts/file-census.py` and its tests (29 passed at `62d5fbae`), built by `PL-929` Slice 2 (`4f95fb3`, #537). The committed census is `docs/research/file-census-5ef559d.csv`, and `docs/research/RS-00952-file-census-rfc-897-stage-0.md` describes it | delivered |
| Stage 1 — the taxonomy (§3) | The draft is `PL-929` Slice 3 (`9e70469`, #545), `docs/research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md`. The rulings are `RL-941` to `RL-951` and `RL-988` | delivered |
| §3a — the notes move | `PL-929` Slice 4 (`1ec453b`, #544). Its precondition was Slice 1's scan-root fix (`cbf1365`, #540) | delivered; later overtaken by RFC-937's note-family migration |
| Stage 2 — the reference-coding standard (§4) | Delivered by WK-697 under RFC-937 (`CR-1164`) | reassigned |
| Stage 3 — the ownership map (§5) | Transferred to WK-1169; its roadmap row carries it from this close | deferred with an owner |
| Stage 4 — the workflow-loop audit (§6) | Transferred to WK-1170; its roadmap row carries it from this close | deferred with an owner |
| Stage 5 — migration and enforcement (§7) | Delivered by WK-697 under RFC-937 (`CR-1164`) | reassigned |
| §11 (a) — the census in the gate, its close-tree output committed | Script and tests evidenced; the close-tree census goes to WK-1170 | split: evidenced / reassigned |
| §11 (b) — every file in exactly one category | WK-697: RFC-937's families, `doc-id.py check`, `docs/INDEX.md` | reassigned |
| §11 (c) — no unfiled empty matrix row | WK-1169 | deferred with an owner |
| §11 (d) — the unreferenced plans carry verdicts | WK-1170 | deferred with an owner |
| §11 (e) — a linter red on three broken fixtures | WK-697: checks 30–39 and their broken-input proofs (`CR-1164` §2) | reassigned |
| §11 (f) — one new file per high-traffic category, born through the skills | WK-697: `PL-1144`, `RL-1145`, `LG-1148` | reassigned |
| §11 (g) — the notes move's own acceptance | The move landed (#544). The directory it measures was removed by RFC-937's migration | reassigned; cannot be measured as written |

## Verdict

**Proposed by the auditor, and adopted by the lead** on 2026-09-28.

| Item | §13 verdict | Owner | Event |
|---|---|---|---|
| Stage 2; (b), (e), (f) | **reassigned** — delivered by WK-697 (`CR-1164`) | — | — |
| Stage 5 | **reassigned** — delivered by WK-697 (`CR-1164`) | — | — |
| (g) | **reassigned** — overtaken by WK-697's migration | — | — |
| Stage 3; (c) | **deferred with an owner** | WK-1169 | its first slice |
| Stage 4; (d) | **deferred with an owner** | WK-1170 | its first slice |
| (a) | the script and tests are evidenced; the committed close-tree census is **reassigned** | WK-1170 | its first slice |
| The scan-root row | resolved in this PR | — | — |

No item is left without evidence or a verdict. WK-695 built none of its four stages itself:
two were delivered by the Work that superseded them, and two are carried by the Works minted
for them.

**The proposed roadmap change** is made only once the line exists, in WK-697's closed-row form.
In the `### WK-695` header block, `status: active` becomes `status: closed`. The row gets the
appended text *"**Closed 2026-09-28 by the deputy's dated line, by delegation, on `CR-1176`**,
with Stages 2 and 5 delivered by WK-697 (`CR-1164`) and Stages 3 and 4 taken over by WK-1169
and WK-1170."*

## Sign-off

The owner is the maintainer. The acceptance line is the deputy's, by the maintainer's
delegation of 2026-09-28, and is written in this record's one follow-up commit. The auditor
filed this record on 2026-09-28.

**Maintainer acceptance:** _pending — the maintainer's dated line_
