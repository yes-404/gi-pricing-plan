---
id: RL-919
family: ruling
title: WK-671 is reopened under its own id: the closure record is appended to, never amended, and the roadmap's status marker moves while its close note stays verbatim
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md
---

# WK-671 reopen, RFC-895 Q2, and bundle resolution on the scoring path (2026-08-30)

**What this is.** Three rulings requested by the lead after the maintainer directed that the
uncompleted part of WK-671 be driven to a real end: how a closed workstream is represented when
work resumes under it, where RFC-895's hook registration lives, and whether a `ref` may be
served from the per-worker memo without a metadata read.

**Numbering continues at 39, 40, 41.** Rulings 1–30 are catalogued in
[`RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md`](RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md);
31–32 there, 33 in
[`RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md`](RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md),
34 in
[`RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md`](RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md),
35 in
[`RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`](RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md),
36 in
[`RL-00917-the-clause-reaches-persistence-and-nfr-499-is-the-defective-one.md`](RL-00917-the-clause-reaches-persistence-and-nfr-499-is-the-defective-one.md),
37 in
[`RL-00915-option-c-the-compiled-bundle-s-blob-key-becomes-part-of-the-version-s-own-metadata.md`](RL-00915-option-c-the-compiled-bundle-s-blob-key-becomes-part-of-the-version-s-own-metadata.md),
38 in
[`RL-00924-option-b-one-computation-taught-to-answer-the-question-it-already-claims-to-answer.md`](RL-00924-option-b-one-computation-taught-to-answer-the-question-it-already-claims-to-answer.md).
**RL-924 was verified as the highest existing** by searching every `## Ruling N` heading
under `docs/plans/`, not taken from the dispatch.

**Read against `origin/main` at `daa6fbe`**, re-fetched at 2026-08-30T11:22Z immediately
before these rulings were written. `HEAD` of the ruling branch was equal to `origin/main` at
that moment.

**Mints no `FR-`/`NFR-`/`OQ-` id and makes no `docs/specs/` or `docs/contracts/` edit.**
Each ruling states its disposition and who applies it.

---

## 0. One thing the dispatch asserted that this record cannot verify

The dispatch relays that *"the maintainer has now directed that the uncompleted part of WK-671
be reopened and driven to a real end"*. **No artifact in the tree at `daa6fbe` carries that
direction.** `docs/plans/INDEX.md#2026-08-30-nt-0012-0013-0014-adoptionmd` §1 quotes three maintainer
messages of 2026-08-30 and §1.1 quotes the delegation; none of them is a reopen instruction,
and §1.1 reads the delegation narrowly — *"It does **not** extend to WK-671's close, WK-672, or any
later phase."* The WK-671 closure record says the same of its own delegation.

So the reopen currently exists only as a relay. `CLAUDE.md` §12: *"Every decision lands as a
dated artifact — a ruling record, an audit record, a plan — never in chat."* **RL-919's
first clause is therefore a precondition, not a formality**: the direction is quoted and dated
in an artifact before any of the shape below is applied. This is not scepticism about the
lead; it is the rule RFC-843 exists to enforce, and the lead's own dispatch says to verify
rather than rule against the relay.

---

## RL-919 — WK-671 is reopened under its own id: the closure record is appended to, never amended, and the roadmap's status marker moves while its close note stays verbatim

**Ruled.** Work resumes under **WK-671**, with the existing slice ids **W11-3** and **W11-4**.
The record takes five parts, in this order. **(ii) below — keeping WK-671 closed and opening new
rows — is refused.**

### 1. Precondition: the direction is quoted and dated first

Before any edit in parts 2–4, the maintainer's reopen direction is recorded verbatim and
dated, in the same place and the same form the adoption record used for the delegation
(`2026-08-30-nt-0012-0013-0014-adoption.md` §1/§1.1). **The lead records it.** Until it
exists, the reopen rests on a relay and the closure record would be annotated on authority
nobody can find.

**Scope of the reopen, stated because the dispatch bundled two different things.** The reopen
covers **FR-253, FR-254 and FR-259** — and, riding with FR-259, NFR-500,
which the closure record §6 tied to it. **Adoption slices E, F and G are not part of it.**
They are a separate Work with its own filed record and its own bounded delegation; folding
them under WK-671 would put two differently-delegated bodies of work under one id and make the
second close ambiguous about which delegation accepted what. They continue under
`2026-08-30-nt-0012-0013-0014-adoption.md`.

### 2. `docs/closures/CR-00927-work-item-record-wk-671-scoring.md` §§1–8 are not edited. Not one word

They are the record of what was believed and evidenced at 2026-08-30: the ten FR verdicts,
the NFR verdicts, the measured-and-failing NFR-489 table in §4, and the §7 plan review.
**A reopen is not a correction.** The close was correct as at its date; the record is not
wrong, and treating the reopen as an amendment would invite a later reader to discount
verdicts that nothing has falsified.

`docs/findings/README.md`'s convention — *"Evidence is write-once. A record that changes after
the fact must say it changed, with the correction dated"* — is satisfied by parts 3 and 4,
which add and date rather than revise.

### 3. One appended, dated section, and one banner line

**`## 9. Reopened <date>`, appended at the end.** Section 9 is minted and never reused
(`CLAUDE.md` §5). It states, and nothing more:

- the direction from part 1, quoted, with its date and who gave it;
- exactly which requirements are back in scope (part 1's list), by id;
- that **§§1–8 are neither corrected nor withdrawn**, and that this section is a change of
  scope rather than a change of belief;
- that §6's *"reassigned — a future batch-scoring slice (36, 37) and a future sampling slice
  (42)"* resolution is **superseded for exactly those rows**, naming them, so §6 read alone
  cannot mislead;
- that the NFR-489 carry-forward row of §6 — *"owner: an architectural ruling before WK-674
  deployment"* — is **discharged by RL-921 below**, with this record's path.

**And one line under the existing title banner**, where every reader passes:
*"Re-opened in part `<date>` — see §9. §§1–8 are the record as at close and are not
amended."* One line, no verdict touched. This is the minimum that stops a partial read from
misleading, and it is the form the write-once convention explicitly sanctions.

**Who applies it: the auditor writes it, the lead files it.** Closure records at
`docs/audit/work/<id>/README.md` are the auditor's by charter (`.claude/roles/auditor.md`,
Owns). The section carries **no §13 verdict**, so nothing in it is the lead's to issue — but
the lead files it, as §12 has the lead file the record.

### 4. The roadmap row: the marker moves, the close note stays whole

`docs/roadmap.md:376`. **The strike and the ✔ come off the row header. Every word of the
existing close note stays, verbatim.** A dated re-open clause is appended naming the three
FRs, pointing at §9 and at the two filed plans.

**Why the marker moves when `CLAUDE.md` §5 makes things permanent.** §5's permanence is about
**ids and section numbers** — the things a reader navigates by. A ✔ is a **status glyph**, and
status is the one thing the roadmap exists to hold *because* it changes; `CLAUDE.md` §0 puts
status in the roadmap for exactly that reason, and `RFC-756` records four incidents of a
status copy going stale. §13's opening sentence forbids *"a roadmap reporting progress the
repository does not have"*. A ✔ over live work is that defect inverted — it reports completion
of work in flight — and it is the reading a scanner will take.

Keeping the close note verbatim is what preserves the record: nothing is deleted, so the row
still says what was closed, on what evidence, and by whom.

**Who applies it: the lead.** `docs/roadmap.md` is named in `.claude/roles/lead.md` as one of
three paths the lead writes that no other charter claims.

### 5. The re-close is a second, appended close — and the old delegation does not cover it

When the reopened work finishes, `## 10. Second close <date>` is appended. It is audited
under `close-workstream` **against the reopened scope only** — FR-RATE-36, 37, 42, NFR-500,
and NFR-489's disposition. It does **not** re-verdict the seven requirements closed on
2026-08-30: re-auditing them would silently replace evidence dated at the close with evidence
dated later, which is the substitution §13's reference rule exists to prevent. If one of them
has since regressed, that is a finding with its own row, not a re-verdict.

**Acceptance of that second close is the maintainer's.** The 2026-08-30 delegation is read
narrowly in two places at once — the adoption record §1.1 (*"covers the landing of RFC-842,
RFC-843 and RFC-895, and nothing else"*) and the closure record's own preamble (*"it covers
this close, not WK-672 and not any later phase"*). **Neither reaches a second WK-671 close.** The
lead cannot self-accept it on the delegation already given; a fresh dated line is required.
Naming this now is the point of the ruling: it is the clause most likely to be assumed
inherited.

### 6. Why (ii) — keep WK-671 closed, open new rows — is refused

It is the cleaner-looking option: no annotation, no moved glyph, every verdict frozen. It is
refused because **it splits one body of work across two ids.** The batch and sampling work
already carries the ids W11-3 and W11-4 in three places — the closure record's §2 slice table,
the filed plan filenames `2026-08-29-w11-3-batch-scoring.md` and
`2026-08-29-w11-4-trace-sampling-persistence.md`, and the rulings those plans cite. A new row
would leave every finding filed against WK-671 needing re-derivation to a new owner, which is a
failure this project has already had once after a slice re-cut.

`docs/findings/README.md`'s naming convention points the same way: *"A work item is named by its
existing id — a PR number, a slice id, or a workstream id. No new id family is minted here."*

**The ruling is overridden** if the closure record's §§1–8 are edited, if the second close
re-verdicts a requirement closed on 2026-08-30, if a second close is accepted on the
2026-08-30 delegation, or if adoption slices E/F/G are recorded under WK-671.

---
