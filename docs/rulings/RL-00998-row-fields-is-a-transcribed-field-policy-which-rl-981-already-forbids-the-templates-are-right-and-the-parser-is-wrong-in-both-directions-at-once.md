---
id: RL-998
family: ruling
title: `_ROW_FIELDS` is a transcribed field policy, which RL-981 already forbids; the templates are right and the parser is wrong in both directions at once
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-template-parser-conflicts-rulings.md
---

# Two merged slices disagree with the templates they were built against — the row field set and the phase-section form, ruled (2026-09-02)

**What this is.** Two conflicts between already-merged WK-697 deliverables, found by the W37-5
executor while building `doc-id.py migrate` against the merged code, flagged rather than
arbitrated because they are two *other* slices' artifacts disagreeing with each other. They
are ruled below as Rulings 79 and 80. Neither is a `Decision points` row of
[`../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`](../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md);
both were discovered by building against
[`RFC-937`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §1, the same provenance as Rulings 69–72.

**Both resolve the same way, and it is not the way the framing suggested.** The lead's brief
put each as *"the template/spec versus the code"* and warned against defaulting to the code
because it runs. The evidence goes further than that warning: in **both** conflicts the code
is the outlier, and in the second it is outnumbered four artifacts to two — one of the four
being `audit-docs.py`'s own check 30, which *enforces* the form `doc-index.py` rejects. Two
merged slices ship contradictory positions inside the same CI job.

**Nothing in RFC-937 §1 is edited, and neither is
[`docs/process/document-ids.md`](../process/document-ids.md).** Both rulings resolve inside
the implementation — the constraint
[`RL-00983-the-map-plan-roll-up-runs-through-the-slices-and-has-no-catch-all.md`](RL-00983-the-map-plan-roll-up-runs-through-the-slices-and-has-no-catch-all.md)
states for this class in its own opening: *"§1 is the maintainer's own text; `document-ids.md`
§1.1–§1.13 is a verbatim lift of it and says so in its own opening paragraph; §1.6 makes
`process/` the maintainer's, amendable only by an `RFC-` plus an `RL-`."* Verified: §1.6's
ownership table row reads *"Reference — `process/` | maintainer; amendments arrive as `RFC-` +
`RL-`"*. One residual textual divergence inside that maintainer-owned file is recorded under
*Not ruled* below rather than edited here.

**A third conflict was routed here after the two rulings were filed, and it is refuted rather
than ruled** — `docs/_templates/LG.md`'s `slice:` field, reported as *required* and
unsatisfiable. It is not required, and the section near the end of this record shows the
derivation that settles it. **The same section corrects a claim in this record's own first
draft**, which the third conflict's evidence falsified: `migrate` does not destroy
`docs/roadmap.md` — it silently declines to migrate it. Both the refutation and the
self-correction are filed here rather than in a new record, because a reader chasing the
`slice:` question will arrive at this one.

## Authority

- **Both are spec-versus-implementation conflicts**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places with this
  role (*"Rules decision points and spec-vs-code conflicts before a plan or slice can
  proceed"*), and which `CLAUDE.md` §0 requires be resolved rather than quietly reconciled.
- **The lead routed them here under the maintainer's delegation of 2026-09-01**, recorded at
  [`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1, and neither falls in its §2 exclusions: neither is a fact only the maintainer holds,
  neither accepts a close, and neither amends `CLAUDE.md`.
- **Every figure below is measured at `9367eac`** — the W37-5 merge, PR #578, which was
  `origin/main`'s tip while this record was written. **`origin/main` advanced to `ea7088e`
  (PR #579) before it was filed**, and that is stated rather than smoothed over: `ea7088e`
  adds one file under `docs/plans/` and changes none of the artifacts cited here —
  `git diff --stat 9367eac ea7088e -- scripts/ docs/_templates/ docs/process/document-ids.md
  docs/notes/ .github/` is empty — so every citation below holds at both trees. `origin/main`
  then advanced again, to `e471a42` (PR #580), which touches only
  `docs/process/delivery-process.md` and its extract; this branch is rebased onto it and the
  same emptiness holds. The measurement tree stays `9367eac` — that is a fixed fact; which
  commit happens to be `main`'s tip is not, and is why it is not restated as one below.
- **Re-read under `delivery-process.md` §15 Rule 10**, which merged as `e471a42` *while this
  branch was open* — *"a branch open when a ruling merges is re-read against that ruling
  before the branch itself merges."* Applied to this branch: the two commits that landed
  during its life are PR #579 (a planner derivation) and PR #580 (the rule itself). Neither
  is a ruling, and neither changes a conclusion here. PR #579 is noted in RL-998 §1 as a
  live sibling of the same mechanism rather than as a superseding decision.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding F68 — see [`../findings/register.md`](../findings/register.md) —
carried forward with RFC-937's migration as its trigger. It is honoured here, and the check is
not patched from this branch.

1. `git grep -c '^## RL-998 —\|^## RL-999 —' docs/rulings/INDEX.md#2026-09-02-w37-template-parser-conflicts-rulingsmd`
   returns `2`, and `git grep -n '^#\+ Ruling ' docs/plans/` shows 79–80 filling the gap
   immediately after RL-975 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option**, with
   the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour — and each such violation
   is one an artifact can be edited to produce, not a human judgement (RL-975's shape).
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-template-parser-rulings-79-80` names exactly this
   one new file. No note, no template, no script, no workflow and no roadmap row is edited by
   this branch — every change these rulings oblige is work for a named slice.
6. Every claim about a script's behaviour below was produced by **executing that script**
   against the artifacts, not by reading it; the probe and its control are quoted inline.

---

## RL-998 — `_ROW_FIELDS` is a transcribed field policy, which RL-981 already forbids; the templates are right and the parser is wrong in both directions at once

### 1. Verified first, at `9367eac`

[`docs/_templates/WK.md`](../_templates/WK.md) and [`SL.md`](../_templates/SL.md) declare
`tree:`, `corrected_by:` and `relates:` in the fenced block an author is told to copy.
`scripts/doc-index.py:268-270` rejects all three:

```
_ROW_FIELDS = frozenset(
    {"id", "family", "kind", "title", "status", "created", "owner", "phase", "work", "slice"}
)
```

Executing the template's own instruction — *"Copy the block below under the phase section it
belongs to … fill in every placeholder"* — through the parser that consumes it:

```
PROBE 1 — template-literal WK row through scan_roadmap_rows()
  RESULT: HeaderError: roadmap_1.md:23: unknown row field 'tree'
```

| Claim | Verdict |
|---|---|
| The templates declare the three fields | **Confirmed.** `WK.md` and `SL.md` both carry `tree:`, `corrected_by:` and `relates:` inside their ` ```yaml ` block |
| `_ROW_FIELDS` rejects them, uncaught | **Confirmed.** `scripts/doc-index.py:289` raises `HeaderError`; no caller catches it |
| The blast radius is one script | **Refuted, and this is the fact that changes the severity.** `.github/workflows/docs.yml:43` runs `python3 scripts/doc-index.py --check` in CI. Worse, `scripts/audit-docs.py:2183` calls `_doc_index.build_corpus(ROOT)` **unguarded** inside check 39; `check_ids_30_39()` runs at `:2662`, *before* checks 23, 25, 26, 27, 28 and 29 at `:2665-2681`. One malformed row block therefore skips six unrelated checks and suppresses the whole report — a red gate that prints nothing |
| §1.5's closed field set contains the three | **Confirmed.** `document-ids.md:123`, `:127`, `:129`. Unlike `phase:`, `work:`, `slice:` and `plans:`, none of the three carries a per-family applicability comment |
| §1.5's scope reaches a `WK-`/`SL-` row | **Confirmed.** `document-ids.md:109`: *"On every document-family file, every Reference file, and (as a fenced block under the row's heading) every `WK-`/`SL-` row."* |
| The narrowing has a stated basis | **Refuted.** `scripts/doc-index.py:263-267` states it as an inference — *"those are document-family-only **in practice** for these two row families"* — which W37-1's merged templates falsify. No ruling, note or spec clause is cited for it |
| `_ROW_FIELDS` is at least a *subset* of §1.5, as its comment claims | **Confirmed as to §1.5, and beside the point.** It permits `kind:` and `slice:`, which `WK.md`'s own comment forbids by name (*"`kind:`, `slice:`, `plans:`, `supersedes:` and `superseded_by:` do not apply to this family and must not appear here"*). So it is simultaneously **too strict** (three fields rejected) and **too permissive** (two fields admitted) — it is not a principled subset of anything |
| A ruling already governs this | **Confirmed, and it is decisive.** RL-981 §2 point 1: *"the permitted set for a family is the set of keys in that family's template front matter"*, quoted verbatim in [`../plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`](../plans/PL-00960-w37-6-the-migration-run-leaf-plan.md), which adds *"RL-981 makes the template the licensing instrument"* |
| The gate already contains the correct policy | **Confirmed.** `audit-docs.py` check 30 derives the permitted set from the templates. Executing `derive_field_policies()` against the real templates gives `work/slice permitted MINUS doc-index _ROW_FIELDS == ['corrected_by', 'relates', 'tree']` — check 30 blesses precisely what `doc-index.py` rejects |
| The mechanism this ruling leans on is live and load-bearing elsewhere | **Confirmed, and it cuts both ways — recorded so a reader does not think it was missed.** PR #579 (`ea7088e`), merged while this branch was open, found `docs/_templates/LG.md:28` declaring `slice: SL-NNNNN` unconditionally, which under RL-981 makes the field *required* on every ledger and the family unusable. That is the same mechanism as this ruling, producing a defect rather than curing one. It does not weaken the ruling: it shows the licensing instrument must be written with care, and that the remedy is always to fix the template — the route W37-6's leaf plan already takes for `REFERENCE.md` — never to reintroduce a transcription in a reader |
| A test would have caught it | **Refuted, and the near-miss is instructive.** `tests/test_template_headers.py` does feed `WK.md`/`SL.md` to a parser — but re-wraps the fenced block in `---` and calls `_docid.parse_header`, whose grammar *does* accept the three. It exercises a different parser from the one that consumes a row, and passes. `tests/test_doc_index.py` contains zero `_templates` references, and the W37-3 fixture roadmap carries only `id, family, title, status, phase` |

### 2. Ruled

**Chosen: the templates are correct; `_ROW_FIELDS` is the defect; and the remedy is to
*derive* the row field set from the family's template, never to widen a transcription.**
RL-981 already settled which artifact licenses a family's fields, `document-ids.md:109`
already puts row blocks inside §1.5's scope, and check 30 already implements the derivation.
`doc-index.py` is the one place in the gate that transcribed instead.

**Rejected: amend `WK.md`/`SL.md` to drop the three fields.** This is the reading the lead
warned might be right, and the evidence refuses it. It would contradict §1.5's own field set
and its scope sentence, and it would make the templates disagree with check 30, converting a
crash into a silently wrong field policy across the whole corpus. It also cannot be done
without an `RFC-` plus an `RL-` touching `document-ids.md`, since §1.5 is where the three
fields live.

**Rejected: add the three fields to `_ROW_FIELDS` and stop there.** It fixes the reported
symptom and leaves the defect. A transcribed list that happens to agree today drifts again on
the next template edit, and it leaves `kind:`/`slice:` wrongly permitted. RL-981 acceptance
item 2 names this exact signature: *"check 30's verdict is unchanged by editing the template
— the signature of a policy transcribed."*

**Rejected: leave W37-5's workaround as the resolution.** It is one caller conforming to the
consumer. It does not help an author following the template, and it is itself now incorrect —
see *What it obliges*.

**On W37-5's workaround, which the lead asked me to classify: it becomes correct-by-accident
and must be made explicit, not left.** `scripts/doc-id.py:1576-1583` emits `id, family, title,
status, created, owner, phase` (plus `work:` for a slice) and omits all three. Once the field
set is derived from the templates, `migrate`'s output no longer carries fields its own
family's template declares — so the omission stops being a workaround and starts being a
divergence in the writer. The writer must be derived from the same template as the reader.

### 3. What it obliges

1. **`doc-index.py`'s row field policy is derived from `docs/_templates/WK.md` and
   `SL.md`, per family, not from a module-level constant.** `_ROW_FIELDS` as a hand-written
   frozenset is deleted, not extended. Per-family, because the two templates declare different
   sets — `work:` belongs to a slice row and not a work row.
2. **The reader must not become a third transcription.** `scripts/audit-docs.py` already
   imports `scripts/doc-index.py` (`_doc_index = _load_module(...)`), so `doc-index.py` cannot
   import `audit-docs.py` back. `scripts/_docid.py` is the only module both already import and
   is therefore where a shared template reader goes; the alternative is `doc-index.py` owning
   it and `audit-docs.py` consuming it. Which of those two is the executor's call — a third
   independent copy is not.
3. **`_row_header_from_raw` must populate the three fields.** `scripts/doc-index.py:309`,
   `:313` and `:315` hardcode `tree=None`, `corrected_by=()`, `relates=()`. The `Header`
   dataclass already carries them, so this is wiring, not a model change.
4. **`doc-id.py migrate`'s row emission is derived from the same template** so the writer and
   the reader cannot disagree (`scripts/doc-id.py:1576-1583`).
5. **Owner: W37-6.** It is the only open WK-697 slice; W37-1 (templates) and W37-3
   (`doc-index.py`) are merged and closed, and W37-7…11 have not started. W37-6 already owns
   the roadmap restructure into `WK-`/`SL-` rows and the `_ID_SCOPE_ROOTS` widening — it is the
   slice at which this latent defect becomes a live red gate — and its leaf plan already
   carries a task of exactly this species for `REFERENCE.md`, decided on exactly this ground.

### 4. Acceptance — the violation that must become detectable

**The violation: a family template's own example block is rejected, or silently mis-read, by
the parser that consumes that family's blocks.** Today that violation exists and nothing
reports it.

- **A check that copies each row template's fenced block into a roadmap fixture and parses it
  with `doc-index.py`'s row parser.** It must fail today, before the fix, with
  `unknown row field 'tree'` — that is the positive control, and the corpus already supplies
  it. Extend `tests/test_template_headers.py`, which already reads these templates for the
  *other* parser; a second file would repeat the near-miss rather than close it.
- **RL-981 item 2's mutation, applied to `doc-index.py`:** add a key to `WK.md` and a row
  using it parses; remove a key and the same row is rejected. *Violation: the parser's verdict
  is unchanged by editing the template* — the signature of a policy transcribed.
- **A check that `kind:` on a `WK-` row is rejected.** This is the half a fields-added fix
  leaves behind, and it must red.

---
