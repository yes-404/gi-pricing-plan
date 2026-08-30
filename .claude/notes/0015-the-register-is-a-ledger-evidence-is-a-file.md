# NT-0015 — The register is a ledger; evidence is a file

| | |
|---|---|
| **Raised** | 2026-08-30, distilled from a register-consultation session working against `docs/audit/register.md` at tree `7db62ca` (register read in full at that tree) |
| **Status** | `open` — proposed, not adopted. Nothing here is in force |
| **Deliverable** | Spec change first, then code, per `CLAUDE.md` §0's table — P1/P2 amend `docs/audit/register.md`'s header (a doc change) before P3's linter and P5's query script are written; the §5 impact matrix names 15 targets if adopted |
| **Owner** | The decision-maker rules §7's five open questions; the lead runs the plan gate; the maintainer accepts the adoption's close (`CLAUDE.md` §12 — a Work close is the maintainer's, never a role's). No acceptor is named for the proposal as a whole yet, which is what `open` means here |
| **Lands in** | Nothing yet. The §5 impact matrix: `docs/audit/register.md`'s header and its unowned rows, a new `docs/audit/findings/` directory, `scripts/register-lint.py` and `scripts/register-owed.py` (+ tests), gate wiring, two close checklists, `.claude/roles/auditor.md` and `lead.md`, two skills, `docs/open-questions.md`, `docs/roadmap.md`, plus an adoption plan |
| **Sequencing / Trigger** | §6's adoption sketch: an optional ride-ahead PR (P1+P2 only, no tooling) may land now as a lead-mergeable docs PR ahead of the rest — §7 Q1 recommends this. Otherwise: Freeze → Reconcile (decision-maker rules §7) → Plan (one Work, four slices, S4 after S2) → Implement / audit / pilot (first real close uses P5 output) / close, maintainer accepting |

---

One-line thesis: `docs/audit/register.md` has evolved a real discipline — ownership
grammar, write-once amendments, verified-against-the-diff closure — that today lives
entirely in the auditor's head and the reader's pattern-matching. Name the grammar, give
unowned rows a decay rule, lint what is named, split the ledger from the evidence, and
generate the owed list a close currently compiles by hand.

## 1. Motivation — each item cites the register's own testimony

1. **The grammar is real but unwritten.** Thirty-plus rows use a consistent decision
   vocabulary (`fix before close`, `accept — with instrument / measured / alternative
   instrument`, `carry forward — with owner / with trigger / phase boundary /
   unowned-needs-authorisation`, `split verdict`, plus F48's *provisional owner*) and five
   distinct ownership shapes. None of it is specified anywhere; a new agent learns it by
   reading 30 rows or not at all.
2. **Unowned rows have no decay path.** F45(ii)+F46, F47, and F28's carried P5 are
   *correctly* unowned — each says why — but nothing structurally forces them onto an
   agenda. This is NT-0005's "deferred items with no durable custody" shape, sitting inside
   the very artifact built to prevent it.
3. **Row discipline is enforced by vigilance, not mechanism.** Three rows confess in-place
   corrections of their own first versions (F27: "a bare count in this area has now aged
   four times in one day"; F28's rule-6 collision; F31's precursor). The discipline held —
   because the auditor caught it. §13's own standard: a check that has never printed a
   failure has not been tested.
4. **Evidence has outgrown the table.** F27 and F-W9-3 are multi-thousand-word forensic
   essays inside table cells. As evidence they are exemplary; as ledger rows they destroy
   scannability and force every correction to be an edit of an ever-growing cell. The
   header's claim — "one row per open finding" — is true in letter and defeated in shape.
5. **The owed list is compiled by hand at the moment of highest load.** F41, verbatim: the
   W11 close's owed list "already runs to thirteen items — a list that lost NFR-RATE-13/14
   for two workstreams even though a register row, F-W9-1, existed for them the whole
   time." Re-derivation at close time is exactly where things get lost.

## 2. Proposal — five parts, separable, in dependency order

- **P1. Specify the grammar in the register header.** One paragraph enumerating the
  decision vocabulary and the ownership shapes (workstream / event / trigger /
  next-toucher / unowned-pending-authorisation / provisional). Nothing new is invented;
  the header describes what the rows already do. *(Can ride ahead as a standalone PR with
  P2 — see §6.)*
- **P2. Decay rule for unowned rows.** Header sentence: *"An unowned row must name the
  event that next confirms or assigns its owner; absent a named event, it defaults to the
  next §14 review."* Apply it to the current unowned rows in the same PR (one line each).
- **P3. `scripts/register-lint.py`, wired into the gate.** Deterministic, no LLM —
  NT-0014's C-class, pointed at this file. Checks: every Decision parses to a P1 shape;
  every unowned row names its decay event (P2); every *resolved* annotation carries a date
  and a PR or SHA; every named owner is a roadmap row that exists, a dated ruling record,
  or a named event; every finding id is unique. Red on violation. TDD against deliberately
  broken fixture rows — enforcement proven on broken input (§13).
- **P4. Split ledger from evidence.** Evidence essays move to
  `docs/audit/findings/<id>.md` (write-once, dated amendments quoting what they supersede
  — the convention the rows already follow). The register row becomes the index entry:
  id, concerns, work item, phase, decision, owner, status, link. A row then changes only
  when *status* changes — NT-0003's duplicated-status lesson applied to the register
  itself. Migration is incremental: new findings use the split immediately; existing long
  rows migrate opportunistically when next amended, never in one bulk rewrite (§7 Q3).
- **P5. `scripts/register-owed.py <work-id | phase | review>`.** Prints every open row
  owned by or blocking the named close, from the parseable fields P1/P3/P4 guarantee. The
  close checklists cite the script's output with the tree; the closure record's owed list
  is thereafter generated, not recalled.

## 3. Authority and custody rules

- The register (and, after P4, the findings files) remain the record; scripts are views
  and guards, never a second source — same rule as NT-0014 §3.
- Writing rows and findings files stays where the auditor's charter puts it ("Owns:
  register deferral rows"); P3/P5 change *checking*, not custody.
- The auditor's delegated closure authority (exercised on F50/F51) is unchanged; P3 merely
  verifies the closure annotation's form (date + SHA/PR), never its substance.
- Reopening a Work close remains the maintainer's alone (CLAUDE.md §13); nothing here
  touches that.

## 4. Non-goals

- **Not** per-clause requirement-marker granularity (F35/F36/F43/F44/F48's shared shape).
  Real, already decided elsewhere (OQ-PLAT-15 option f), owned by `req-coverage.py`'s
  owner. Bundling it here would be the scope-blur the register keeps catching in others.
- **Not** a bulk rewrite of existing rows (see P4's incremental rule).
- **Not** a schema/JSON register. The table stays markdown and human-first; P3 parses it
  as-is. (If NT-0014's core-extract pattern later earns extension here, that is its own
  note.)
- **Not** any change to what verdicts exist or who decides them.

## 5. Impact matrix — draft, verify every target on filing

| # | File | Change | Nature |
|---|---|---|---|
| 1 | `docs/audit/register.md` header | P1 grammar paragraph + P2 decay sentence | Amend |
| 2 | `docs/audit/register.md` unowned rows (F45/F46, F47, F28-P5 at `7db62ca`; re-enumerate on filing) | Name each row's decay event per P2 | Amend, one line each |
| 3 | `docs/audit/findings/` | New directory; README stating the write-once amendment convention and the row↔file link rule | New |
| 4 | `scripts/register-lint.py` (+ tests) | P3 | New |
| 5 | `scripts/register-owed.py` (+ tests) | P5 | New |
| 6 | CI / gate wiring (CLAUDE.md §11 command list; verify §) | Add P3 to the gate; P5 is on-demand, not gated | Amend |
| 7 | `docs/audit/checklists/work-item-close.md` | Owed list is `register-owed.py` output, cited with tree; carried findings written per P1 grammar | Amend |
| 8 | `docs/audit/checklists/phase-close.md` | Same at phase level | Amend |
| 9 | `.claude/roles/auditor.md` | Rows per P1 grammar; long evidence to `findings/<id>.md` per P4; run P3 before proposing a register PR | Amend |
| 10 | `.claude/roles/lead.md` | Enter step: `register-owed.py` for the layer being entered (replaces "relevant findings" recall) | Amend |
| 11 | `.claude/skills/close-workstream/SKILL.md` | Cite P5 output; verify §/step on filing | Amend |
| 12 | `.claude/skills/phase-review/SKILL.md` | §14 review agenda includes all rows decayed to it (P2) | Amend |
| 13 | `docs/open-questions.md` | §7 questions on filing | Append |
| 14 | `docs/roadmap.md` | Adoption as a Work item | Amend |
| 15 | Adoption plan `docs/plans/<date>-nt-0015-adoption.md` | §6 skeleton | New |

Deliberately unchanged: `docs/audit/plan-reviews.md`, `closure-records.md`, existing
`docs/audit/work/**` records (never retro-edited), the decision vocabulary itself, and
`req-coverage.py` (non-goal 1).

## 6. Adoption sketch (maps to §14's workflow)

0. **Ride-ahead PR (optional, before filing):** P1+P2 alone — header paragraph, decay
   sentence, one line per unowned row. No tooling, no role changes; lead-mergeable as a
   docs PR. If taken, this note files as the mechanism half only.
1. Freeze — file as NT-00XX after numbering check.
2. Reconcile — decision-maker rules §7; lead gates the plan.
3. Plan — one Work, slices: S1 header+decay (if not ridden ahead) → S2 linter+gate →
   S3 findings-dir + checklist/role pointers → S4 owed-query + close wiring. S4 after S2
   (parses the same fields); S3 parallel-safe but sequential per §8 anyway.
4–7. Implement / audit / pilot (first real close uses P5 output) / close, maintainer
   accepting.

## 7. Open questions (decision-maker, at reconcile)

- **Q1 — Does the ride-ahead PR (P1+P2) go now,** decoupled from this note, or land as S1?
  Recommendation: now; it is one docs PR and every day of delay is another hand-parsed row.
- **Q2 — Lint severity on legacy rows:** red-gate immediately, or warn on rows predating
  P1 and red only on new/amended rows? Recommendation: warn-then-red with a dated
  flag-day, same posture as NT-0014's Q3 on legacy plans.
- **Q3 — Migration trigger for P4:** opportunistic-on-amendment only (recommended), or
  also a one-time migration of the worst offenders (F27, F-W9-3) as a dedicated slice?
- **Q4 — Does `register-owed.py` output land *in* the closure record verbatim** (generated
  block, marked as such) or is it cited by command+tree only? Recommendation: verbatim
  block + citation — the record should survive the script changing.
- **Q5 — Findings file naming** where ids carry both forms (`FR-RATE-25 (F-W9-3)`):
  file by the F-id, cross-link the requirement id? Needs one rule before P4 lands.

## 8. Acceptance standard (draft)

Complete when, verifiably: **(a)** the header specifies grammar + decay and every open
unowned row names its event; **(b)** `register-lint.py` is red on a fixture row with an
unparseable decision, a dateless resolution, and a nonexistent owner — three deliberately
broken inputs, each named; **(c)** it runs green on the live register in CI; **(d)** one
new finding has landed split (row + `findings/<id>.md`) through a real audit, not a
fixture; **(e)** one real close's owed list is `register-owed.py` output cited with its
tree, and reconciles against the register with zero hand-added or hand-dropped items.
Each report names command, totals, tree (§15).

---
*Inbox provenance: distilled from the register-consultation session of 2026-08-30
(consistency check at `7db62ca`). Row citations (F27, F41, F45–F48, F50/F51, F-W9-3,
F28/P5) are to that tree and must be re-verified on filing — the register amends daily.*
