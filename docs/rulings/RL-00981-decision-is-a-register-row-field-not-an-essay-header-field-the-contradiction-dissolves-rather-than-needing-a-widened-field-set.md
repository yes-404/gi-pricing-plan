---
id: RL-981
family: ruling
title: `decision:` is a register-row field, not an essay header field; the contradiction dissolves rather than needing a widened field set
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md
---

# WK-697's field-set defects — where `decision:` lives, how a finding is scoped to a phase, and how a map plan rolls up, ruled (2026-09-02)

**What this is.** Three defects in RFC-937's field specification, found during execution by
the W37-3 executor and relayed by the lead. They are ruled below as Rulings 70, 71 and 72.
None is a `Decision points` row of
[`../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`](../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md);
all three were discovered by building against
[`RFC-937`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §1, which is the same provenance as
RL-990 in
[`RL-00990-rfc-937-1-5-s-vendored-parenthesis-is-a-gloss-not-a-detector-the-set-is-declared-and-reconciled-and-the-exemption-reaches-only-the-blanket-passes.md`](RL-00990-rfc-937-1-5-s-vendored-parenthesis-is-a-gloss-not-a-detector-the-set-is-declared-and-reconciled-and-the-exemption-reaches-only-the-blanket-passes.md).

**They are ruled now rather than after W37-4 because W37-4 builds checks 30–39 against
exactly this field set.** Check 30 requires *"no unknown field; required fields per family"*;
check 33 is built on the `execution` derivation RL-983 settles. A check written against a
defective field specification is a check that enforces the defect.

**Nothing in RFC-937 §1 is edited, and neither is
[`docs/process/document-ids.md`](../process/document-ids.md).** §1 is the maintainer's own
text; `document-ids.md` §1.1–§1.13 is a verbatim lift of it and says so in its own opening
paragraph; §1.6 makes `process/` the maintainer's, amendable only by an `RFC-` plus an `RL-`.
All three rulings resolve inside the implementation, which is the constraint RL-990 set for
this class and which this record follows.

## Authority

- **All three are spec-versus-implementation conflicts**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) and
  [`delivery-process.md`](../process/delivery-process.md) §3 already place with this role
  (*"Rules decision points and spec-vs-code conflicts before a plan or slice can proceed"*).
- **The lead routed them here under the maintainer's delegation of 2026-09-01**, recorded at
  [`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1: *"I authoris the lead to allocate technical questions to decision-maker to make decision
  on behalf of me."* **The routing is recorded because it happened, not because it was
  needed** — as with RL-990, the charter already reaches these, so none of the three rests
  on the delegation. That distinction matters: a reader must be able to tell which rulings
  would fall if the delegation were withdrawn, and none of these three would.
  **The maintainer did not rule any of these personally.**
- **Nothing here reopens D0–D14.** D0 (*"register dispositions live in `decision:`"*) is
  load-bearing for RL-981 and is applied, never questioned.
- **Nothing was declined**, and the boundary that would have made me decline is stated at the
  end under *What would have gone back to the maintainer*. Two of the three came within one
  step of it.

**Numbering continues at 70.** Verified rather than relayed:
`git grep -hoE '^#+ Ruling [0-9]+' origin/main -- docs/plans` yields a maximum of **69**, and
`git grep -nE '\bRuling 7[0-9]\b' origin/main -- docs .claude` returns nothing.

**Evidence tree.** Every measurement below was taken at `f226891`, `origin/main` when this
session started, and re-confirmed at **`2204ffb`** — `origin/main` after W37-2 merged as #567
mid-session, which this record is rebased onto. The `docs/` corpus is unchanged between the
two: `git show --name-only --format= 2204ffb -- docs` is empty, so every count over the note,
the templates and the registers holds at both. The one exception is the three defects in
RL-983, which are read from `origin/w37-3-doc-index` at `1c487b8`, the **unmerged** W37-3
branch, and are named with that revision each time. Where a figure is quoted from another
document, the tree that document states is named with it.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding (F68) — see [`../findings/register.md`](../findings/register.md) —
carried forward with RFC-937's migration as its trigger. It is honoured here rather than
evaded, and the check is not patched from this branch.

1. `git grep -c '^## RL-873[0-2] —' docs/rulings/INDEX.md#2026-09-02-w37-field-set-and-rollup-rulingsmd`
   returns `3`, and `git grep -n '^#\+ Ruling ' docs/plans/` shows 70–72 filling the gap
   immediately after RL-990 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option** in its
   opening paragraph, with the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-field-set-rulings-70-72` names exactly this one new
   file. No note, no frozen plan, no template, no script and no roadmap row is edited by this
   branch — every change these rulings oblige is work for a named slice.
6. Every numeric claim below names the tree it was measured at and the command that produced
   it, per `CLAUDE.md` §13's reference rule.

---

## RL-981 — `decision:` is a register-row field, not an essay header field; the contradiction dissolves rather than needing a widened field set

### 1. Verified first, at `f226891`

The reported contradiction is that RFC-937 §1.2a mandates `decision:` on every finding while
§1.5 declares the header field set closed (*"Unknown field → lint failure"*) and does not name
`decision:` among the family-specific extras it lists.

| Claim | Verdict |
|---|---|
| §1.5's extras parenthesis omits `decision:` | **Confirmed.** It names `deliverable`, `lands_in`, `trigger` for RFC; `gates`, `exit_criteria` for a phase section; `prs:` for a ledger. `decision:` is absent |
| §1.2a mandates `decision:` on a finding | **Confirmed, and the wording is the answer.** *"A finding's **register** disposition ... lives in its own `decision:` field"*. §1.2's FD row: *"`decision:` carries the **register** disposition"*. D0: *"**register** dispositions live in `decision:`"*. Three independent statements, each scoping the field to the register |
| The note says where the register carries it | **Confirmed, and this is the fact the report did not reach.** §5.2's migration cell for `findings/register.md` reads: *"each **row** gains `status:` (`active`, or `closed` where a **Resolved** annotation exists) and `decision:` (the existing Decision cell); the phase register's rows merge in with `phase: P1b` (RFC-756: no second copy)"*. The carrier is the register row, named as such |
| §1.5's closed field set governs the register row | **Refuted.** §1.5 scopes itself: *"On every document-family file, every Reference file, and (as a fenced block under the row's heading) every `WK-`/`SL-` row."* An `FD-` register row is none of the three. §1.5 governs the **essay's** front matter, and `decision:` was never a candidate for it |
| So §1.2a and §1.5 contradict | **Refuted.** They address different carriers. The apparent collision comes from reading §1.5's field set as the finding's whole field set, which its own scope sentence rules out |
| W37-1's merged `docs/_templates/FD.md` put `decision:` in the essay's front matter | **Confirmed**, with a comment declaring it *"this family's declared extra (§1.2's family table)"*. It is the only template extra at `f226891` outside §1.5's parenthesis — an `awk` over the front matter of all thirteen files in `docs/_templates/` returns RFC's three, LG's `plans:` (already in the closed set) and FD's `decision:`, and nothing else |
| An essay can carry `decision:` safely | **Refuted, and this is decisive independent of the wording.** §1.2 makes an `FD-` a *"living row + frozen essay"*, and check 34 permits a frozen file only `status:` (forward only), `superseded_by:`, an append to `corrected_by:`, or — ledgers only — an append to `plans:`. A disposition changes: register row F61's Decision cell at `f226891` still reads *"Two dispositions are open, not one"*, while [`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md) §7 chose branch (b) and left amending the row to the auditor — a change to that field is owed right now. An essay-borne `decision:` is therefore illegal to update under check 34, or legal only by removing `finding` from check 34's frozen set — which surrenders body-freeze protection on the essay to make one metadata field writable. Both horns are worse than putting the field where the note already puts it |
| §1.5's parenthesis is exhaustive after all | **Confirmed in one direction, refuted in the other, and the divergence runs both ways.** With `decision:` off the essay, every remaining template extra is one §1.5 names. But `prs:`, which §1.5 assigns to a ledger, is declared in no template: `docs/_templates/LG.md` records PRs in a `## PRs` body section instead. So the parenthesis is neither a complete register of extras nor a licensing instrument; its own sentence names the template as both |

### 2. Ruled

**Chosen: `decision:` is a field of the `FD-` register row and is not permitted in an `FD-`
essay's front matter.** The note says so three times in §1 and once in §5.2, its own freeze
machinery makes the alternative unmaintainable, and it needs no widening of §1.5's closed
field set — so **nothing in §1 moves.** §1.2a's *"so `status:` and `decision:` cannot be
confused"* is satisfied at the carrier level as well as the name level: the status the essay
carries and the disposition the row carries are on different artifacts.

**Rejected: reading §1.5's parenthesis as a gloss and licensing `decision:` on the essay via
the template.** This was the reading W37-1 implemented and it is the reading RL-990 applied
to the *vendored* parenthesis in the same paragraph, so it deserved the weight it got. It
fails here for a reason that did not apply there: RL-990's parenthesis was a **detector**
for a set, and a wrong detector can be replaced by a declaration. This parenthesis sits behind
a **scope sentence** that excludes the register row outright, and the field's own three
definitions name the register. Licensing it onto the essay would also put a mutable value in a
frozen file, which no amount of template declaration fixes.

**Rejected: adding `decision:` to §1.5's closed field set.** That is an edit to §1 —
the maintainer's text, byte-identical in `document-ids.md` — and it would have gone back to
the maintainer rather than being ruled here. It is unnecessary, which is why the question does
not arise.

**Rejected: keeping `decision:` on both the row and the essay.** §5.2's own parenthetical
*"(RFC-756: no second copy)"* is aimed at the phase register, but the mechanism it names is
general and this is the same mechanism: two copies of a value that changes, one of them in a
frozen file, is [`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md) with the staler
copy guaranteed in advance.

**The mechanism, in three parts.**

1. **The per-family header field policy is read from `docs/_templates/`, never transcribed
   from §1.5's parenthesis.** §1.5's operative clause is *"declared in that family's template
   and permitted only there"* — the template is the licensing instrument the sentence itself
   names, and it is machine-readable. The permitted set for a family is the set of keys in
   that family's template front matter; the required subset is that set less the keys the
   template's own comment marks conditional. **The parenthesis is illustration of why extras
   exist, not the register of which ones do** — at `f226891` it diverges from the templates in
   both directions at once.
2. **The consequence for `prs:`, stated so it is not re-derived.** §1.5 names it; no template
   declares it; therefore it is not a permitted ledger header field, and a ledger writing it
   fails check 30. `LG.md`'s `## PRs` body section is this repository's ledger PR record, and
   §1.9's PR-title lint reads that. `LG.md`'s comment gains one line saying so, so the next
   reader of §1.5 does not re-open it.
3. **The template's front matter is not at line 1, and this is measured, not predicted.** Every
   file in `docs/_templates/` opens with an HTML comment block, and `scripts/_docid.py`'s
   `parse_header` returns `None` unless `lines[0]` is exactly `---`. Running it over the
   directory at `2204ffb` — the merged W37-2 parser — returns **0 of 13 templates parsed**. A
   check 30 that consumes the templates through the shared parser therefore derives an
   **empty** policy and passes everything, silently, and does so on the very first run. The
   template reader must skip a leading comment block, and check 30 must assert its own coverage
   over `_templates/` rather than infer it from a green run.

### 3. What it obliges

- **W37-4** builds check 30 to reject `decision:` in an `FD-` essay header and to require it on
  every register row; derives the per-family permitted set from `docs/_templates/`; and asserts
  template-parse coverage.
- **W37-4** corrects `docs/_templates/FD.md`: `decision:` comes out of the front matter, and
  the template comment states where the field lives and cites RFC-937 §5.2. The `## Disposition`
  body section stays — it explains the row's value and is the essay's job. **W37-1 is not
  reopened**; the correction is a one-file edit inside the slice that consumes the template.
- **W37-4** adds the `prs:` line to `docs/_templates/LG.md`'s comment.
- **W37-6** rewrites the register's header prose — which §5.2 already requires (*"header prose
  rewritten"*) — so that the row's field set is declared there in one place, since a register
  row is not a header-bearing record and §1.5's template mechanism does not reach it.
- **Nothing in `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` or `docs/process/document-ids.md` is
  edited.** §1 stays byte-identical to the maintainer's original.

### 4. Acceptance — the violation that must become detectable

1. **The field on the wrong carrier.** A fixture `FD-` essay whose front matter carries
   `decision:` must fail check 30, and a fixture register row with no `decision:` must fail
   check 30. **Violation: either passes.**
2. **A hardcoded field policy.** Add a key to one template's front matter and a header using
   that key must become permitted; remove it and the same header must red. **Violation: check
   30's verdict on that header is unchanged by editing the template** — which is the signature
   of a policy transcribed into the checker instead of read from the declaration §1.5 names.
3. **Silent empty coverage.** **Violation: check 30 parses zero of the thirteen files under
   `docs/_templates/` and still exits 0.** The count must be reported, not inferred from
   greenness; a check that has never seen a template cannot be enforcing a template-derived
   policy. This is not a hypothetical: the shared parser as merged at `2204ffb` returns exactly
   that zero today, so a check 30 built on it starts in the violating state.
4. **The ledger extra.** A fixture ledger header carrying `prs:` must fail check 30.
   **Violation: it passes** — which would mean the policy came from the parenthesis after all.

---
