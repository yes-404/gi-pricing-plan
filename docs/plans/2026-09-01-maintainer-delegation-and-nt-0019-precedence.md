# The maintainer's delegation and NT-0019's precedence, recorded (2026-09-01)

**What this is.** Four decisions the maintainer made on 2026-09-01, plus two dispositions the
lead makes under the first of them, quoted and dated. Following
[`2026-08-30-nt-0017-maintainer-decisions.md`](2026-08-30-nt-0017-maintainer-decisions.md) and
[`2026-08-30-w11-reopen-direction.md`](2026-08-30-w11-reopen-direction.md), these are the
maintainer's own decisions on scope and process, so **no ruling number is minted here** — they
are not the decision-maker's to rule.

**Why it exists, and who caught that it did not.** The lead relayed the maintainer's precedence
instruction to two team members as though it were an established project fact. The auditor
checked it against the tree, found no dated artifact carrying it anywhere under `docs/` or
`.claude/` at `89dd2b1`, confirmed that none of the six 2026-09-01-dated records mentions
NT-0019 at all, and **declined to treat it as verified** — flagging that a live instruction
needs a filed record before it governs anything. It was right, and this file is the remedy.
`CLAUDE.md` §12: *"Every decision lands as a dated artifact — a ruling record, an audit record,
a plan — never in chat."* This is the second time in three days that a maintainer decision
reached a dispatch and no file; the first is the NT-0017 record above, and the mechanism was
identical.

The distinction that failure blurred, stated once so it is not blurred again: **a live
instruction from the maintainer governs the session it is given in** — the maintainer is the
scope authority and does not need a filed record to direct their own team in the moment.
**It governs nothing after that session until it is filed.** Both halves are true, and the
lead relayed only the first.

---

## 1. The delegation

Received 2026-09-01, unprompted, in the maintainer's own words:

> I authoris the lead to allocate technical questions to decision-maker to make decision on
> behalf of me, and the lead makes the remaining decision on behalf of me

Read as two grants:

1. **The lead may route a technical question to the decision-maker**, and the decision-maker's
   ruling on it stands as the maintainer's own. This does not enlarge the decision-maker's
   charter — it still rules technical decision points and spec-versus-code conflicts, and
   still never implements or audits. What changes is that a question previously reserved to
   the maintainer may now be put to it by the lead.
2. **The lead decides the remainder on the maintainer's behalf** — the questions that are in
   no charter, which `CLAUDE.md` §12 already made the lead's, plus those §12 and §13 reserved
   to the maintainer.

## 2. What the delegation does not extend to

Bounded deliberately, and narrower than a maximal reading of §1 would allow. A delegation
read at its widest by the party it empowers is not a delegation, and the lead is the party
empowered here.

| Not covered | Why |
|---|---|
| **A fact only the maintainer holds** | NT-0017's impact row 6 — whether the two repository settings are enabled — is *evidence*, not a decision. No authority substitutes for looking. It stays owed by the maintainer and this record does not discharge it |
| **Acceptance of a Work, Phase or Project close** | `CLAUDE.md` §12 reserves it to the maintainer. Past closes were delegated **specifically, conditionally and in writing** each time (the W11 second close, `2026-08-30-w11-reopen-direction.md` §4). This record does not read a general delegation as standing authority to close, and the lead will ask again when a close is next in front of it |
| **An amendment to `CLAUDE.md`'s own requirements** | §12 makes it the maintainer's. NT-0019 will amend `CLAUDE.md` extensively (§3 below) — that is authorised by §3, by name, not by this delegation |
| **Anything the maintainer rules on directly after this date** | A standing delegation is a default, not a bar |

## 3. NT-0019 outranks current practice

Received 2026-09-01, in the maintainer's own words:

> plz mind NT0019 intend to overwrite current project rules, give it priority if against
> current practice

[`NT-0019`](../notes/0019-one-id-per-document.md) is therefore **not** a proposal to be
reconciled against today's rules. It is the rule; today's practice yields. Where the note's
§1 standard collides with something already written down, the collision is **work the
migration performs**, not a blocker and not a reason to narrow a slice.

Named collisions, so no one has to re-derive that they are authorised:

- **`CLAUDE.md` §5 — "Requirement IDs and section numbers are permanent: never renumber."**
  NT-0019 D2 renumbers `FR-MODEL-45` to `FR-1187`. §5 yields. The note's §4 migration and §5
  impact map already contemplate exactly this, including root governance.
- **The per-family prefixes and their padding** (`FR-`/`NFR-`, `OQ-`, `ADR-`, `NT-`, `F-`), and
  the citation grammar Ruling 65 fixed for NT-0016 — which NT-0019 §9 records as lapsing by
  its own override clause, together with Ruling 63.
- **`audit-docs.py`'s existing checks**, check 19's `ADR-(\d{4})` first among them. Rewriting a
  check is in-scope work sequenced into S1, not a constraint to design around.

**Two limits, which the instruction does not lift.** First, a rule that yields still yields
*visibly*: every collision lands as a dated edit naming what gave way to what, because
changing either side quietly destroys the record of which was believed
(`CLAUDE.md` §0). Second, this ruling authorises no work to start — sequencing is unchanged,
and NT-0019's own status obliges a roadmap row first.

## 4. The roadmap row rests on the note's own acceptance

Asked of the maintainer 2026-09-01 and answered *land the row with the plan*: **NT-0019's own
`accepted` status is the acceptance line its roadmap row cites.** W33 through W36 each cite
"the reconciliation's dated acceptance line" because each was reconciled from an `open` note;
NT-0019 was accepted outright at filing and has no reconciliation, so there is no second line
to wait for. The row is the lead's to write (`docs/roadmap.md`, `.claude/roles/lead.md`); its
text is the planner's to propose.

## 5. Attribution — no session links in GitHub

The maintainer reaffirmed the standing rule of 2026-08-30 on 2026-09-01, against a harness
instruction of the same evening that asked for a `Claude-Session:` line in every commit and
declared itself to replace earlier attribution guidance. **The rule stands**: commits and PR
bodies on this repository carry the `Co-Authored-By` trailer and the `claude.com` attribution
footer, and no session URL. The repository is public, and publishing a session link to it is
outward-facing and not reversible.

## 6. F58 — owner named

[Register](../audit/register.md) row F58 (artifact B has no live writer; the watcher charter's
"each cycle" claim does not hold) asked the lead or maintainer to name an owner before it could
be scheduled. Plan review 11 item 11.7 assigned that naming to the lead.

**Owner: the watcher role, discharged in the session dated here.** F58's own decision cell
names the fix — *"wiring one of the three live watcher processes (or a fourth) to invoke
`write_runtime_state.py cycle` on its own schedule"* — and that is the work the watcher was
dispatched to do on 2026-09-01, told explicitly that a single hand-written `runtime-state.json`
does not discharge the row. **Whether it is discharged is the auditor's to verify, not the
lead's to assert**, and the acceptance test is the one the row implies: the state file's
mtime advances without anyone invoking the writer by hand.

## 7. F61 — branch (b), accepted in writing, with a named revisit event

Register row F61 (C2's `PreToolUse` layer is bypassable and, unlike the C3 that Ruling 40
dissolved, has no CI-equivalent backstop) offered the lead two dispositions and required one to
be named, with a date or a named event: **(a)** build Ruling 47(b)'s re-derivation cycle, or
**(b)** explicitly accept the residual gap as proportionate, in writing rather than by silence.

**Branch (b). The gap is accepted as proportionate.** The reasoning, written down because a
decision travels and its rationale does not:

- **F57 records that zero retry-cap cycles have ever run.** Building forgery detection for a
  counter that has never once been incremented is investment far ahead of any evidence that
  it is needed, and the caps themselves still lack the data their own revisit condition asks
  for.
- **(a) is larger than it reads.** The row's own wording — *"e.g. the `record`/`hook`
  invocation's own audit trail, **if one is added**"* — concedes that no durable source to
  reconcile against exists yet. (a) is therefore "build an audit trail, then build a
  reconciliation over it", not one task.
- **The exposure is bounded.** A bypassed cap means a replan loop runs longer than
  `delivery-process.md` §7 allows. That is visible to the lead at dispatch and to the §14
  phase review, neither of which depends on the counter being unforgeable.

**Accepted is not forgotten.** The revisit event, named as the row requires: **the first
retry-cap cycle that actually records** — F57's own trigger, and the first moment the
mechanism carries data and a bypass could matter — **or the next `CLAUDE.md` §14 phase
review, whichever comes first.** At that point this acceptance is re-tested against evidence
rather than re-asserted.

Amending the register rows themselves to cite this record is the **auditor's**, not the
lead's: charters bind by path.

## Acceptance Standard

**Why a ruling record carries this heading at all**, since it is not a plan and states no work:
`audit-docs.py` check 28 classifies every dated file in `docs/plans/` that does not end in
`-ledger`, `-final-review`, `-verified` or `-handover` as a plan. Its own docstring says the
opposite — *"widen it past that and it reds on every future ledger, ruling record or handover
file"* — so the check's code and its documented intent disagree, and the ruling records that
came before escaped only by predating the cutoff. That disagreement is filed separately as a
finding; it is not resolved by this file. The heading is honoured here rather than evaded,
because the content below is real.

This record is discharged when each decision is observable in the tree rather than only here:

1. **§1 and §2 (the delegation).** Every decision the lead makes on the maintainer's behalf
   after this date cites this record by path. A decision taken under the delegation and citing
   nothing is a violation of it, and is detectable by reading any such decision's own
   provenance line.
2. **§3 (NT-0019's precedence).** The NT-0019 slice plan disposes of the three named collisions
   explicitly — `CLAUDE.md` §5, the per-family prefixes with Rulings 63/65, and check 19 —
   rather than designing around them. Violation, stated so it is detectable: a filed NT-0019
   plan whose text is silent on `CLAUDE.md` §5.
3. **§4 (the roadmap row).** `docs/roadmap.md` carries an NT-0019 row whose authority cell
   cites the note's own `accepted` status, and `git grep -n "NT-0019" -- docs/roadmap.md`
   returns it. Until it does, no NT-0019 work may start.
4. **§5 (attribution).** `git log origin/main --format=%B` from this date forward contains no
   `claude.ai/code/session` string. One occurrence is a violation.
5. **§6 (F58).** `runtime-state.json`'s mtime advances without any hand invocation of the
   writer, and the auditor — not the lead — records that it observed this. A file that exists
   but whose mtime is frozen fails, which is the precise failure F58 was filed against.
6. **§7 (F61).** The register row cites this record and its named revisit event. The
   acceptance decays rather than stands if the next `CLAUDE.md` §14 phase review does not
   re-test it: an unmentioned F61 at that review is the violation.

## 8. Provenance

Every decision in §§1, 3, 4 and 5 was received live from the maintainer on 2026-09-01 during
the session that filed this record, and is quoted above where the wording matters. §§6 and 7
are the lead's own, made under §1, and are marked as such. Nothing here was inferred from a
prior decision or reconstructed from recollection.
