# Two merged slices disagree with the templates they were built against — the row field set and the phase-section form, ruled (2026-09-02)

**What this is.** Two conflicts between already-merged W37 deliverables, found by the W37-5
executor while building `doc-id.py migrate` against the merged code, flagged rather than
arbitrated because they are two *other* slices' artifacts disagreeing with each other. They
are ruled below as Rulings 79 and 80. Neither is a `Decision points` row of
[`2026-09-01-nt-0019-id-standard-map-plan.md`](2026-09-01-nt-0019-id-standard-map-plan.md);
both were discovered by building against
[`NT-0019`](../notes/0019-one-id-per-document.md) §1, the same provenance as Rulings 69–72.

**Both resolve the same way, and it is not the way the framing suggested.** The lead's brief
put each as *"the template/spec versus the code"* and warned against defaulting to the code
because it runs. The evidence goes further than that warning: in **both** conflicts the code
is the outlier, and in the second it is outnumbered four artifacts to two — one of the four
being `audit-docs.py`'s own check 30, which *enforces* the form `doc-index.py` rejects. Two
merged slices ship contradictory positions inside the same CI job.

**Nothing in NT-0019 §1 is edited, and neither is
[`docs/process/document-ids.md`](../process/document-ids.md).** Both rulings resolve inside
the implementation — the constraint
[`2026-09-02-w37-field-set-and-rollup-rulings.md`](2026-09-02-w37-field-set-and-rollup-rulings.md)
states for this class in its own opening: *"§1 is the maintainer's own text; `document-ids.md`
§1.1–§1.13 is a verbatim lift of it and says so in its own opening paragraph; §1.6 makes
`process/` the maintainer's, amendable only by an `RFC-` plus an `RL-`."* Verified: §1.6's
ownership table row reads *"Reference — `process/` | maintainer; amendments arrive as `RFC-` +
`RL-`"*. One residual textual divergence inside that maintainer-owned file is recorded under
*Not ruled* below rather than edited here.

## Authority

- **Both are spec-versus-implementation conflicts**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places with this
  role (*"Rules decision points and spec-vs-code conflicts before a plan or slice can
  proceed"*), and which `CLAUDE.md` §0 requires be resolved rather than quietly reconciled.
- **The lead routed them here under the maintainer's delegation of 2026-09-01**, recorded at
  [`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
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
  is a ruling, and neither changes a conclusion here. PR #579 is noted in Ruling 79 §1 as a
  live sibling of the same mechanism rather than as a superseding decision.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding F68 — see [`../audit/register.md`](../audit/register.md) —
carried forward with NT-0019's migration as its trigger. It is honoured here, and the check is
not patched from this branch.

1. `git grep -c '^## Ruling 79 —\|^## Ruling 80 —' docs/plans/2026-09-02-w37-template-parser-conflicts-rulings.md`
   returns `2`, and `git grep -n '^#\+ Ruling ' docs/plans/` shows 79–80 filling the gap
   immediately after Ruling 78 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option**, with
   the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour — and each such violation
   is one an artifact can be edited to produce, not a human judgement (Ruling 78's shape).
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-template-parser-rulings-79-80` names exactly this
   one new file. No note, no template, no script, no workflow and no roadmap row is edited by
   this branch — every change these rulings oblige is work for a named slice.
6. Every claim about a script's behaviour below was produced by **executing that script**
   against the artifacts, not by reading it; the probe and its control are quoted inline.

---

## Ruling 79 — `_ROW_FIELDS` is a transcribed field policy, which Ruling 70 already forbids; the templates are right and the parser is wrong in both directions at once

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
| A ruling already governs this | **Confirmed, and it is decisive.** Ruling 70 §2 point 1: *"the permitted set for a family is the set of keys in that family's template front matter"*, quoted verbatim in [`2026-09-02-w37-6-migration-run-leaf-plan.md`](2026-09-02-w37-6-migration-run-leaf-plan.md), which adds *"Ruling 70 makes the template the licensing instrument"* |
| The gate already contains the correct policy | **Confirmed.** `audit-docs.py` check 30 derives the permitted set from the templates. Executing `derive_field_policies()` against the real templates gives `work/slice permitted MINUS doc-index _ROW_FIELDS == ['corrected_by', 'relates', 'tree']` — check 30 blesses precisely what `doc-index.py` rejects |
| The mechanism this ruling leans on is live and load-bearing elsewhere | **Confirmed, and it cuts both ways — recorded so a reader does not think it was missed.** PR #579 (`ea7088e`), merged while this branch was open, found `docs/_templates/LG.md:28` declaring `slice: SL-NNNNN` unconditionally, which under Ruling 70 makes the field *required* on every ledger and the family unusable. That is the same mechanism as this ruling, producing a defect rather than curing one. It does not weaken the ruling: it shows the licensing instrument must be written with care, and that the remedy is always to fix the template — the route W37-6's leaf plan already takes for `REFERENCE.md` — never to reintroduce a transcription in a reader |
| A test would have caught it | **Refuted, and the near-miss is instructive.** `tests/test_template_headers.py` does feed `WK.md`/`SL.md` to a parser — but re-wraps the fenced block in `---` and calls `_docid.parse_header`, whose grammar *does* accept the three. It exercises a different parser from the one that consumes a row, and passes. `tests/test_doc_index.py` contains zero `_templates` references, and the W37-3 fixture roadmap carries only `id, family, title, status, phase` |

### 2. Ruled

**Chosen: the templates are correct; `_ROW_FIELDS` is the defect; and the remedy is to
*derive* the row field set from the family's template, never to widen a transcription.**
Ruling 70 already settled which artifact licenses a family's fields, `document-ids.md:109`
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
the next template edit, and it leaves `kind:`/`slice:` wrongly permitted. Ruling 70 acceptance
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
5. **Owner: W37-6.** It is the only open W37 slice; W37-1 (templates) and W37-3
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
- **Ruling 70 item 2's mutation, applied to `doc-index.py`:** add a key to `WK.md` and a row
  using it parses; remove a key and the same row is rejected. *Violation: the parser's verdict
  is unchanged by editing the template* — the signature of a policy transcribed.
- **A check that `kind:` on a `WK-` row is rejected.** This is the half a fields-added fix
  leaves behind, and it must red.

---

## Ruling 80 — the phase section is plain fields under its heading; the fence requirement in `scan_phase_sections` is the defect, and its unbounded lookahead is what makes the failure silent instead of loud

### 1. Verified first, at `9367eac`

The lead's brief described this as the parser taking `blocks[0]` *"with no fallback"*, so that
NT-0019 §1.3's unfenced illustration would fail to parse. **That is not what happens, and the
difference changes the remedy.** `scripts/doc-index.py:366-370`:

```
rest = "\n".join(lines[idx + 1 :])
blocks = _fenced_yaml_blocks(rest)
if not blocks:
    continue
_heading_level, _base_lineno, content = blocks[0]
```

`rest` is *everything after the heading to the end of the file*, so `blocks[0]` is the first
fenced block anywhere below — in a real roadmap, the first `WK-` row. Unknown keys are then
skipped silently. Executing the standard's own illustration through it, with the phase's real
`status: active` and the first Work's `status: retired` deliberately made to differ:

```
PROBE 2 — NT-0019 §1.3-literal (unfenced) phase section through scan_phase_sections()
  RESULT: phase='P2' title='Rating engine live' status='retired' works=() fields={'status': 'retired'}

PROBE 3 (control) — the same corpus, phase block fenced
  RESULT: phase='P2' status='active' works=('WK-01201',)
```

**It does not crash and it is not dropped. It reports the phase as `retired`, borrowing the
status of the Work beneath it, and reports no attached Works at all** — while §1.3 calls
`phase:` attachment *"the whole attachment mechanism"*. A roadmap written to the accepted
standard yields an index that silently misstates the phase.

| Claim | Verdict |
|---|---|
| The lead's "no fallback → crash" framing | **Corrected.** `if not blocks: continue` exists; the failure is silent misattribution, not an error. Severity goes **up**, not down: a crash is safe, wrong governance data is the class NT-0019 exists to prevent |
| NT-0019 §1.3 shows the unfenced form | **Confirmed**, and `document-ids.md` §1.3 is byte-identical to it apart from heading depth: `diff` of the two ranges reports exactly one changed line, `###` versus `##` |
| §1.5's fenced-block rule extends to a phase section | **Refuted.** `document-ids.md:109` enumerates its scope as document-family files, Reference files and `WK-`/`SL-` rows. A phase section is none of the three — the same scope-sentence reasoning Ruling 70 used to keep `decision:` out of §1.5 |
| The family's own template settles it | **Confirmed, and it is explicit.** [`docs/_templates/PHASE.md`](../_templates/PHASE.md): *"This is the one section §1 defines that is **not** built from the closed header field set of §1.5 — a phase section is plain fields under a heading, exactly as shown below, not YAML front matter"*, and its body is unfenced. It even pre-resolves the spelling: *"Field spelling matches NT-0019 §1.3's own illustration verbatim ('exit criteria', two words, not `exit_criteria`)"* |
| Only the spec opposes the parser | **Refuted, and this is decisive.** `scripts/audit-docs.py:1129` declares `_EXPECTED_NO_BLOCK_TEMPLATES = frozenset({"PHASE.md"})`, commented *"no `---`, no fence, no `id:`, no `family:` — **checked, not merely assumed**, by `derive_field_policies`"*. W37-4's merged check 30 **enforces** that `PHASE.md` has no fence, while W37-3's `scan_phase_sections` requires one. Both run in the same CI job |
| The tally | Unfenced: NT-0019 §1.3, `document-ids.md` §1.3, `docs/_templates/PHASE.md`, `audit-docs.py` check 30. Fenced: `doc-index.py:366-370`, and `doc-id.py:1531-1541`, whose own docstring at `:1552` says it followed the module *"not inferred from NT-0019 §1.3's own plain, unfenced illustration"*. **Four to two, and the two are one decision and its downstream copy** |
| The field *names* are wrong too | **Refuted.** `_PHASE_SECTION_FIELDS` (`scripts/doc-index.py:115`) is `("status", "opened", "target", "gates", "exit criteria", "works")` — an exact match for `PHASE.md`, `exit criteria` included. W37-3 read the template for names and departed from it only on form |
| A test pins the fenced form | **Refuted.** `tests/test_doc_index.py` asserts nothing about the phase block's fence; the only test that exercises it, `tests/test_doc_id_migrate.py`, feeds `migrate`'s own output back to `build_corpus` — writer and reader sharing one mistake |

### 2. Ruled

**Chosen: the phase section is plain `key: value` lines directly under its `## P<n> — <title>`
heading, as NT-0019 §1.3, `document-ids.md` §1.3, `PHASE.md` and check 30 all have it.
`scan_phase_sections` is wrong and changes.** The illustration's normativity — which the lead
correctly flagged as mine to decide — **does not have to be reached**: the family's own
template states the rule in prose, and Ruling 70 already made a template the licensing
instrument. Where the template and a merged parser disagree, the template wins, exactly as in
Ruling 79.

**Rejected: amend §1.3's illustration to show a fence.** I had this as the likely answer
before reading `PHASE.md`, on two real arguments — that §1.5 fences embedded blocks, and that
bare `key: value` lines under a heading render as one run-on paragraph in Markdown. Both are
refuted or outweighed: §1.5 scopes itself away from phase sections, and `PHASE.md` shows the
form was chosen deliberately and with its own stated reasoning. Adopting it would also require
editing the maintainer's `document-ids.md` and contradicting merged check 30.

**Rejected: accept both forms.** Two grammars for one block is what the parser's own docstring
rightly refuses (*"one fixed grammar … never a second one"*), and a lenient reader would keep
the silent-misattribution path alive for the unfenced case.

**The code's procedural error is separate from its behavioural one, and worth naming.**
`scan_phase_sections` resolved an apparent spec ambiguity unilaterally and recorded the
resolution only in a docstring. `CLAUDE.md` §0 forbids exactly that: *"stop and resolve it
rather than quietly making either match the other."* W37-5 did the right thing with the same
discovery — it flagged it, in code and in its PR description — which is why this is being ruled
at all.

**On the second workaround: `doc-id.py`'s `_PHASE_TEMPLATE` is a latent bug and needs
unwinding**, which is the answer to the lead's question for this conflict. It is not
correct-by-accident like the row omission; it emits a form three governing artifacts reject.

### 3. What it obliges

1. **`scan_phase_sections` reads plain `key: value` lines directly beneath the phase heading**,
   stopping at the next heading or the first line that is not `key: value`.
2. **The unbounded lookahead goes.** `rest = "\n".join(lines[idx + 1:])` at
   `scripts/doc-index.py:366` must not survive the fix in any form. This is the defect that
   turns a missing block into a wrong answer rather than a loud one, and it is **independent
   of the fence question** — a bounded scan is required whichever grammar is read.
3. **`_PHASE_SECTION_FIELDS` is derived from `PHASE.md`, not transcribed** (`:115`), for
   Ruling 79's reason and because it is what makes the acceptance test below possible. It
   matches today, so this is hardening, not repair. `audit-docs.py`'s `_TEMPLATE_FAMILY`
   rightly excludes `PHASE.md` from *family* policy — a phase has no family — which does not
   bar reading the same file for the phase section's field names.
4. **`doc-id.py`'s `_PHASE_TEMPLATE` (`:1531-1541`) is re-emitted unfenced**, and the docstring
   at `:1552` recording the discrepancy is replaced by a citation to this ruling.
5. **Owner: W37-6**, for Ruling 79's reasons. Both fixes are in the same two files.

### 4. Acceptance — the violation that must become detectable

**The violation: a phase section written exactly as `PHASE.md` shows it is not read, or is
read as something else.** Today it is read as something else, and nothing reports it.

- **`PHASE.md`'s own body, placeholders filled, parsed by `scan_phase_sections`, must yield
  the phase it describes.** It must fail today, before the fix — the positive control the
  corpus already supplies.
- **A phase section carrying no fields must produce no phase, or a loud failure — never a
  phase built from a later block.** Probe 2 above is the fixture: a `## P<n>` heading whose
  Work row's `status:` differs from the phase's. *Violation: the parser reports a phase whose
  field values appear nowhere between its heading and the next.* This one must survive the
  fence decision — it is a test of the bound, not of the grammar.
- **Ruling 70 item 2's mutation, applied to `PHASE.md`:** rename `works:` in the template and
  a phase section using the old name stops being read. *Violation: the parser's verdict is
  unchanged by editing the template.*

---

## Not ruled — and where each goes

Three things surfaced while verifying that are **not** this role's, listed so none is lost.

| Item | Why not mine | Where it goes |
|---|---|---|
| **`_restructure_roadmap` replaces the entire roadmap.** `scripts/doc-id.py:1586-1588` writes `"# Roadmap (fixture)\n\n"` plus the generated rows over `docs/roadmap.md`. It has exactly one caller (`:1691`), on the real `migrate` path, not a fixture-only one. On the real tree this discards every phase narrative, workstream table, closure record and decision gate, and titles the result "(fixture)" | A code defect in merged W37-5, not a spec-versus-code conflict. I verified the call graph but not whether the loss is intended and repaired elsewhere in W37-6's supervised run | **The lead**, as a finding against W37-5, sibling to the closure-record defect already tracked. It is a W37-6 precondition either way. Not covered by W37-6's leaf plan — `grep -niE "fixture\)\|roadmap.*prose\|restructure_roadmap"` over it returns nothing |
| **Whether check 30 ever reaches a `WK-`/`SL-` row block after W37-6 widens `_ID_SCOPE_ROOTS`.** Check 30 walks *files* and reads front matter; a row block is embedded mid-document, which `parse_header` cannot reach by `doc-index.py`'s own account. If it does not reach them, the derived row policy is enforced by nothing even post-migration, and Ruling 79's acceptance test is the only thing standing | A fact to establish by measurement, not a decision. I did not run it — it needs the post-migration corpus, which does not exist at `9367eac` | **W37-6's executor**, as a measurement before its acceptance items are signed off. If the answer is "no", it is a new finding, not a re-ruling |
| **`exit_criteria` versus `exit criteria` inside `document-ids.md`.** §1.5 (`:134`) writes `exit_criteria`; §1.3's illustration (`:75`) writes `exit criteria`. The two sections of one maintainer-owned file disagree, and `PHASE.md` and `_PHASE_SECTION_FIELDS` both follow §1.3 | Ruling 80 settles what the *implementation* does, which is all that was routed here. Correcting the standard's text is an `RFC-` plus an `RL-` under §1.6, and `CLAUDE.md` §12 reserves the note itself to the maintainer | **The maintainer**, via the `RFC-` route, at whatever point §1 is next opened. Nothing is blocked meanwhile: no artifact reads `exit_criteria`, so the divergence is textual only |

## Provenance

- **Found by** the W37-5 executor, building `doc-id.py migrate` against merged W37-1 and W37-3.
  It flagged both in code and in its PR description and arbitrated neither, which is why the
  first thing this record could do was reproduce them rather than re-derive them.
- **Relayed by** the lead, which asked for verification against the shipped artifacts rather
  than against its own framing. That was the right instruction and it changed two things: the
  Conflict-2 failure mode is silent misattribution rather than a crash, and `PHASE.md` — an
  artifact the framing did not mention — is what settles Conflict 2 without reaching the
  question of whether an illustration is normative.
- **Numbering.** Rulings 73–78 merged as `6d03a5e` (PR #577). The maximum ruling number over
  every ref is **78**: `for ref in $(git for-each-ref --format='%(refname)' refs/heads
  refs/remotes); do git grep -hoE 'Ruling [0-9]+' "$ref" -- docs/; done | grep -oE '[0-9]+' |
  sort -n | uniq | tail`. **79 and 80 are unused**: the same sweep for
  `Ruling (79|80|81)` over `refs/heads`, `refs/remotes` and `refs/tags`, across all paths,
  returns nothing, as does a `grep -rInE` over the working tree's `docs/` and `.claude/`.
  **Both sweeps were re-run after `origin/main` advanced to `ea7088e`** — 42 refs, still a
  maximum of 78 and still no use of 79, 80 or 81 — because a number verified free at one tip
  is not free at the next, and PR #579 landed between the two checks.
- **Probes.** The three probe results quoted above were produced by executing
  `scripts/doc-index.py` as exported verbatim from `origin/main` at `9367eac` against
  constructed roadmap fixtures, outside any worktree. Probe 3 is the control for probe 2: the
  same corpus with the fence as the only variable.
