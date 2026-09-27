---
id: RL-999
family: ruling
title: the phase section is plain fields under its heading; the fence requirement in `scan_phase_sections` is the defect, and its unbounded lookahead is what makes the failure silent instead of loud
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

## RL-999 — the phase section is plain fields under its heading; the fence requirement in `scan_phase_sections` is the defect, and its unbounded lookahead is what makes the failure silent instead of loud

### 1. Verified first, at `9367eac`

The lead's brief described this as the parser taking `blocks[0]` *"with no fallback"*, so that
RFC-937 §1.3's unfenced illustration would fail to parse. **That is not what happens, and the
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
PROBE 2 — RFC-937 §1.3-literal (unfenced) phase section through scan_phase_sections()
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
| The lead's "no fallback → crash" framing | **Corrected.** `if not blocks: continue` exists; the failure is silent misattribution, not an error. Severity goes **up**, not down: a crash is safe, wrong governance data is the class RFC-937 exists to prevent |
| RFC-937 §1.3 shows the unfenced form | **Confirmed**, and `document-ids.md` §1.3 is byte-identical to it apart from heading depth: `diff` of the two ranges reports exactly one changed line, `###` versus `##` |
| §1.5's fenced-block rule extends to a phase section | **Refuted.** `document-ids.md:109` enumerates its scope as document-family files, Reference files and `WK-`/`SL-` rows. A phase section is none of the three — the same scope-sentence reasoning RL-981 used to keep `decision:` out of §1.5 |
| The family's own template settles it | **Confirmed, and it is explicit.** [`docs/_templates/PHASE.md`](../_templates/PHASE.md): *"This is the one section §1 defines that is **not** built from the closed header field set of §1.5 — a phase section is plain fields under a heading, exactly as shown below, not YAML front matter"*, and its body is unfenced. It even pre-resolves the spelling: *"Field spelling matches RFC-937 §1.3's own illustration verbatim ('exit criteria', two words, not `exit_criteria`)"* |
| Only the spec opposes the parser | **Refuted, and this is decisive.** `scripts/audit-docs.py:1129` declares `_EXPECTED_NO_BLOCK_TEMPLATES = frozenset({"PHASE.md"})`, commented *"no `---`, no fence, no `id:`, no `family:` — **checked, not merely assumed**, by `derive_field_policies`"*. W37-4's merged check 30 **enforces** that `PHASE.md` has no fence, while W37-3's `scan_phase_sections` requires one. Both run in the same CI job |
| The tally | Unfenced: RFC-937 §1.3, `document-ids.md` §1.3, `docs/_templates/PHASE.md`, `audit-docs.py` check 30. Fenced: `doc-index.py:366-370`, and `doc-id.py:1531-1541`, whose own docstring at `:1552` says it followed the module *"not inferred from RFC-937 §1.3's own plain, unfenced illustration"*. **Four to two, and the two are one decision and its downstream copy** |
| The field *names* are wrong too | **Refuted.** `_PHASE_SECTION_FIELDS` (`scripts/doc-index.py:115`) is `("status", "opened", "target", "gates", "exit criteria", "works")` — an exact match for `PHASE.md`, `exit criteria` included. W37-3 read the template for names and departed from it only on form |
| A test pins the fenced form | **Refuted.** `tests/test_doc_index.py` asserts nothing about the phase block's fence; the only test that exercises it, `tests/test_doc_id_migrate.py`, feeds `migrate`'s own output back to `build_corpus` — writer and reader sharing one mistake |

### 2. Ruled

**Chosen: the phase section is plain `key: value` lines directly under its `## P<n> — <title>`
heading, as RFC-937 §1.3, `document-ids.md` §1.3, `PHASE.md` and check 30 all have it.
`scan_phase_sections` is wrong and changes.** The illustration's normativity — which the lead
correctly flagged as mine to decide — **does not have to be reached**: the family's own
template states the rule in prose, and RL-981 already made a template the licensing
instrument. Where the template and a merged parser disagree, the template wins, exactly as in
RL-998.

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
   RL-998's reason and because it is what makes the acceptance test below possible. It
   matches today, so this is hardening, not repair. `audit-docs.py`'s `_TEMPLATE_FAMILY`
   rightly excludes `PHASE.md` from *family* policy — a phase has no family — which does not
   bar reading the same file for the phase section's field names.
4. **`doc-id.py`'s `_PHASE_TEMPLATE` (`:1531-1541`) is re-emitted unfenced**, and the docstring
   at `:1552` recording the discrepancy is replaced by a citation to this ruling.
5. **Owner: W37-6**, for RL-998's reasons. Both fixes are in the same two files.

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
- **RL-981 item 2's mutation, applied to `PHASE.md`:** rename `works:` in the template and
  a phase section using the old name stops being read. *Violation: the parser's verdict is
  unchanged by editing the template.*

---

## Not ruled — and where each goes

Three things surfaced while verifying that are **not** this role's, listed so none is lost.

| Item | Why not mine | Where it goes |
|---|---|---|
| **`migrate` does not restructure `docs/roadmap.md` at all, and cannot tell that from success.** See the correction immediately below — an earlier draft of this row claimed the opposite and was wrong | A code defect in merged W37-5, not a spec-versus-code conflict: RFC-937 §4 step 3 describes the *target* shape and names no source shape, and §5 (`:313`) classifies `roadmap.md` as **M + H** with the restructure on the M side. The spec is right; the script's legacy patterns are the defect | **The lead**, as a finding against W37-5, sibling to the closure-record defect already tracked (task #31 — the same species: a discovery function under-matching the real corpus). A W37-6 precondition |
| **Whether check 30 ever reaches a `WK-`/`SL-` row block after W37-6 widens `_ID_SCOPE_ROOTS`.** Check 30 walks *files* and reads front matter; a row block is embedded mid-document, which `parse_header` cannot reach by `doc-index.py`'s own account. If it does not reach them, the derived row policy is enforced by nothing even post-migration, and RL-998's acceptance test is the only thing standing | A fact to establish by measurement, not a decision. I did not run it — it needs the post-migration corpus, which does not exist at `9367eac` | **W37-6's executor**, as a measurement before its acceptance items are signed off. If the answer is "no", it is a new finding, not a re-ruling |
| **`exit_criteria` versus `exit criteria` inside `document-ids.md`.** §1.5 (`:134`) writes `exit_criteria`; §1.3's illustration (`:75`) writes `exit criteria`. The two sections of one maintainer-owned file disagree, and `PHASE.md` and `_PHASE_SECTION_FIELDS` both follow §1.3 | RL-999 settles what the *implementation* does, which is all that was routed here. Correcting the standard's text is an `RFC-` plus an `RL-` under §1.6, and `CLAUDE.md` §12 reserves the note itself to the maintainer | **The maintainer**, via the `RFC-` route, at whatever point §1 is next opened. Nothing is blocked meanwhile: no artifact reads `exit_criteria`, so the divergence is textual only |

## Correction to this record's own first draft — the roadmap is not destroyed; it is silently not migrated

**What the first draft of the row above said, and what was wrong with it.** It said
`_restructure_roadmap` *"replaces the entire roadmap … On the real tree this discards every
phase narrative, workstream table, closure record and decision gate."* **That is false, and
the error was mine.** I traced the call graph — one caller, on the real `migrate` path — and
stopped there, without checking the guard's condition against the real corpus. A task was
opened on the strength of it before this correction landed.

`scripts/doc-id.py:1688` guards that call with `if roadmap_drafts:`. `roadmap_drafts` comes
from `_discover_roadmap`, which returns `[]` the moment `_ROADMAP_LEGACY_PHASE_RE` fails.
Running the script's **own three patterns** — not an approximation of them — against the real
`docs/roadmap.md` at `e471a42`:

```
_ROADMAP_LEGACY_PHASE_RE  -> 0 match(es)     ^## Phase <id> — <title>
_ROADMAP_LEGACY_WORK_RE   -> 0 match(es)     ^### W<n> — <title> / status:
_ROADMAP_LEGACY_SLICE_RE  -> 0 match(es)     ^- **W<n>-<m>** <title> — status:

How works and slices are ACTUALLY written today:
  work as a TABLE ROW  | **WK-697** |   : 30
  slice as a TABLE ROW | **W37-1** | : 0
  slice as a BULLET    - **W37-1**   : 0
```

**So `_restructure_roadmap` is never reached, and the roadmap is untouched.** The real defect
is the inverse and is worse in a different way: **§4 step 3 is a silent no-op.** Thirty Works
exist — as table rows — and `migrate` converts none of them, mints zero `WK-` and zero `SL-`
rows, and reports success. It cannot detect this, because the module's own idempotency
argument (`scripts/doc-id.py:788-793`) *defines* "discovery finds nothing" as "already
migrated": **"nothing matched" and "already done" are the same observation to this script.**

**Why the correction is filed rather than the row quietly rewritten.** A retraction gets the
least review of anything in a record, and this one reverses a claim severe enough to have
opened a task. Both statements are recorded so a reader can see which was believed and why the
second is better evidenced — the same reason `CLAUDE.md` §0 refuses a silent reconciliation.

## The third conflict, refuted — `slice:` is permitted, not required, and no ruling is minted

Routed here after the two rulings above were filed: `docs/_templates/LG.md:28` declares
`slice: SL-NNNNN` unconditionally, which — the report ran — makes it **required** under
RL-981, while no `SL-` row exists to name, blocking the `slice:` field of all 16
`-ledger.md` files.

**The premise is false, and it fails at the first step.** RL-981 governs the **permitted**
set — *"the permitted set for a family is the set of keys in that family's template front
matter"*. Required-ness is a **separate mechanism** that RL-981 does not touch:
`scripts/audit-docs.py:1251-1254` computes `required = frozenset(_CORE_HEADER_FIELDS) &
permitted`, plus `{"id"}` for a non-reference family, and `_CORE_HEADER_FIELDS` is
`("family", "title", "status", "created", "owner")`. Executing `derive_field_policies()`
against the real templates:

```
ledger:
   permitted = [corrected_by, created, family, id, owner, phase, plans,
                relates, slice, status, title, tree, work]
   required  = [created, family, id, owner, status, title]
   -> 'slice' permitted? True   REQUIRED? False
```

**A ledger with no `slice:` passes check 30 today.** Independently, check 33's `slice:`
sub-clause is not implemented either — `check_cross_references`'s own docstring
(`scripts/audit-docs.py:1630-1636`) states that *"`work:`/`slice:`/`phase:` resolving to
roadmap rows … are not implemented against the live scope"*. The blocker does not exist on
either check.

**The residual concern is answered by a field the template already permits.** The planner's
reason for not taking its own recommendation was that §1.7 derives a plan's execution axis
through slices, so a ledger without `slice:` goes invisible. But §1.7's own table routes the
terminal row through *either* axis — *"a `CR-` cites the plan's `slice:`/`work:`"* — and
`work:` is in the ledger's permitted set, as the derivation above shows. **`work:` is the
available axis while no slice rows exist.** No template edit, and option (e) is unnecessary
rather than rejected.

**Why no ruling number is minted.** A ruling records a decision between live options. Here
there is a refuted premise and, beneath it, a code defect — and the code defect is not a
spec-versus-code conflict either: §4 step 3 names a *target* shape only, and §5 (`:313`) puts
the restructure on the **M** side, so the specification says what it should and the script does
not do it. Nothing is left to decide, so nothing is ruled; a permanent number is not spent on
a question that dissolved. **`SL-` rows being absent is not a defect to fix in the standard**:
§4 step 3 converts slices that exist in the roadmap, there are none in any shape, and the
clause is therefore vacuous rather than unsatisfiable. Minting `SL-` rows out of the map plan's
slice table would be *creating* governed rows rather than converting them — outside §4's "one
scripted PR, once" over existing things, and a scope question for the maintainer if anyone
wants it.

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
