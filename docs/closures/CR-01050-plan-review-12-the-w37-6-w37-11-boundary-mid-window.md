---
id: CR-1050
family: closure
kind: review
title: Plan review 12 — the W37-6/W37-11 boundary, mid-window
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-03
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 12 — the W37-6/W37-11 boundary, mid-window, 2026-09-03

**Base tree: `198ea5d`**, clean, `git status --short` empty, checked in a session worktree
(`worktree-w37-planner`) branched from `main` at that commit.

**Trigger, stated plainly because it is not one of the skill's two fixed ones.** This review
was commissioned neither at a workstream close nor before a phase exit demo
(`.claude/skills/phase-review` §"When") — W37-6 has not closed; it is mid-window, on its
second renewal, extended today to `23:00Z` with the fail count reset. The commissioning
question is a plan-shape one that surfaced *during* execution — whether the W37-6/W37-11 cut
still holds — and `CLAUDE.md` §14 licenses exactly this ("the plan is a working hypothesis,
re-tested while the phase is still open"), but the review below cannot yet answer question 1
(completion) against a closed workstream's evidence, because none exists: `docs/roadmap.md`'s
WK-697 row still reads *"W37-6 has not run and its go-ahead has not been asked for"* at its most
recent edit and has not been updated through the delegation, both renewals, or either halted
window. That staleness is itself this review's first finding (§4 below), not a defect in the
review's method.

**Two premises in this review's own commissioning brief do not survive verification, and are
corrected here rather than acted on.**

1. **"RFC-937 §7(b)–(k) hold at W37-11's close, not at W37-6's" is not what the filed record
   says.** `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md:426` states acceptance items (a)–(k) as one
   list with no per-item owner; the owner split lives in
   `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:828`, and it reads **"Scope:
   acceptance items (j) and (k), and the closure record"** for Slice W37-11 — nothing wider.
   Items (a)–(h) are exactly what W37-6's own seven-condition gate measures at its own tree
   (`docs/rulings/RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md` §2, §7.3), and the W37-11 slice text
   says it *collects* "the §7 (a)-(h) evidence from W37-6's ledger" rather than re-establishing
   it. So the correct reading is **(a)–(h) [and (i), the H-row table] are W37-6's to establish;
   (j) and (k), plus synthesising the rest into one closure record, are W37-11's** — not a
   `(a)` / `(b)-(k)` split. This matters for question 5 below: the map plan drew a narrow line,
   and the practice observed in this window is wider than that line, which is the real finding,
   sharper than the brief's version of it.
2. **"RL-989's class-6 extension ratification" and "the lettered-ruling nested-span floor"
   do not resolve against `docs/` at `198ea5d`.** `git grep` for "class-6", "class 6",
   "ratif", "nested-span", "nested span" and "lettered" across `docs/` finds RL-989's own
   six-class permitted-diff predicate (`docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`
   and siblings) and `_discover_lettered_rulings` (the Ruling-A1–A3 discovery function,
   `docs/findings/FD-01027-check-37-reds-on-95-of-95-post-migration-rulings-unconditional-on-the-flag-day-because-its-section-detector-cannot-see-a-level-heading.md`), but no ratification of a class-6 *extension*, and no finding
   or ruling naming a "nested-span floor" in any form. Two live worktrees not this one
   (`agent-a225faa49dba12dea`, `agent-a5894b03d1bda7b8d`) are mid-task per the shared task list
   (#26 "File RL-1042 as §2.5 of the RL-1041 record", #27 "Append §8 to the delegation
   record") — these items most likely exist there, unmerged, and the citation should be
   re-verified against `main` once they land rather than carried into a closure record now.
   **Not filed as findings against the brief** — a brief is not a governed artifact — but named
   here per this review's own instruction to flag what does not verify.

---

#### Register rows decayed to this review

`python3 scripts/register-owed.py review`, run against the clean tree above, returns **21 owed
rows**, one further excluded as opening with a resolution marker (F28, unrelated to WK-697 and not
re-verified here — out of this review's scope). Split by whether the row predates WK-697 or was
filed inside this window, because the two need different treatment.

**Eleven rows predate WK-697 and are not re-derived here** (`FR-240`/`F-W9-3`, F27, F29, F31,
F33, F48, F58, F61, F63, F74, F75) — per the skill's own rule, "if a fresh audit has just
covered this, say so and move on": reviews 9–11 (2026-08-30/31) already answered these in
detail and none has moved since (`git diff --stat 567eea2..198ea5d -- docs/findings/register.md`
touches none of their rows' line ranges outside annotation). **What has not happened is a
maintainer acceptance date on reviews 9, 10 or 11** — all three still read `pending` at this
tree. That is a standing gap this review surfaces rather than owns: eleven register rows have
sat with a written recommendation and no dated decision for three-plus days while a fourth
review (this one) opens behind them. **Recommendation:** the maintainer date reviews 9–11
alongside this one, or say explicitly they are superseded by whatever this review's own
acceptance covers — leaving four open `pending` lines stacked in one file is the shape
`CLAUDE.md` §14's "never in chat" rule exists to prevent silently accumulating.

**Ten rows are WK-697's own** (F86, F87, F88 limb 2, F89, F90, F91, F92, F93, F94, F96). Verified
directly against `docs/findings/register.md` at `198ea5d`, not recalled from the brief:

| Row | Register text (verified) | This review's disposition |
|---|---|---|
| F86 | RL-909's decay rule — carry forward, explicit decay, no owner, written 2026-09-02 at W37-5c's close | **No change.** The disposition was already made at the right event; this review does not re-open it. |
| F87 | `_ID_SCOPE_ROOTS` widening reaches no non-markdown file — **fix before close, W37-6** | **Affirm the existing verdict, and make it explicit against drift**: this is a W37-6 precondition by its own text. It must not migrate to W37-11 by informal practice; if it is still open when W37-6's gate is next measured, the gate — not the closure record — is where it is discharged. |
| F88 (limb 2) | `docs/findings/register.md` reached by no discovery function — limb 1 discharged, limb 2 open, owner W37-6, decays to the §14 review **at that close** if undischarged | **Not yet decayed here** — its named event is W37-6's close, which has not happened. Listed for completeness; no disposition owed from this review. |
| F89 | Fixture pollution in concurrent gate runs — carry forward unowned, decay event **is** the next §14 review, named for that purpose | **Accept as a known, disclosed W37-6 risk.** No fix mandated: F89's own text gives three shapes and picks none, and manufacturing a choice here would be exactly the "not decided here, decided anyway" pattern `.claude/skills/phase-review` warns against. Carry into W37-6's own closure record as a disclosed risk, not a blocking defect. |
| F90 | Check 37 / `###`-nesting — dispositioned by RL-1039/1040, re-measured at `15ed00d` | **No change.** Already ruled at the right authority level (maintainer, via D1/D2), already re-measured; this review's job is not to re-litigate a ruling. |
| F91 | RFC-895 runtime-state writer stale since 02:02Z on 2026-09-02 — carry forward unowned | **No change.** Confirmed independently: `write_runtime_state.py show` at this tree still reports `written_at: 2026-09-02T02:02:13Z`, position pinned at slice `W37-4` — nineteen hours and seven slices stale. Decay event is the next watcher re-arm; not this review's to own. |
| F92 | 53 files deferred out of §4 step 5's Reference stamp set — **reassigned 2026-09-03 from W37-6 to W37-11**, on the maintainer's own offer (verified: `git log -1 --format=%B db19be8` quotes the maintainer offering W37-11 or the Work's closure record, and the lead choosing W37-11) | **No change — and cited as the one correctly-authorised precedent for question 5.** This is what a real W37-6→W37-11 boundary move looks like: dated, ruled, sourced to a maintainer offer. The items discussed under question 5 below are not held to the same standard, and F92 is the contrast that makes the gap visible. |
| F93 | RFC-937 §1.5 vendored-manifest header requirement contradicts the maintainer's own exemption ruling — unowned, decay event named as "the next amendment to RFC-937, failing which the next §14 review" | **Decayed here. Disposition: carry forward, unowned, into W37-11's closure record** — this is exactly the shape W37-11's charter already names ("a verdict for every requirement of the note that has no evidence"), and RFC-937 is not otherwise due an amendment before then. Not a W37-6 gate item: it does not stop or blind the run. |
| F94 | Ruling-heading census predicate divergence — unowned, decay event named as **W37-6's closure record**, failing that the next §14 review | **Not yet decayed here** by its own text (names W37-6's closure record first). No disposition owed. |
| F96 | A ruling omitting `## Ruling N` migrates as `PL-`/`owner: planner` silently — unowned, two live instances fixed in-PR, mechanism gap and one pre-existing instance not | **Decayed here — and this review disagrees with treating it as W37-11's by default.** This is a migration-correctness defect of the same class as F90 and the dangling-link class that produced gate condition 7 (§2 below): something the corpus can carry silently past the one-way write. **Recommendation: fix-before-close, W37-6**, or promote to an eighth gate condition on the pattern of Amendment 1 — not carried to W37-11's closure record, which is a synthesis document, not a bug backlog. |

---

#### 1. Completion — derived, not recalled

Not run fresh here: `scope-audit.py`/`req-coverage.py` measure requirement-to-code coverage,
and nothing in this window's evidence bears on that axis — WK-697 is a documentation-corpus
migration, not a requirement delivery, so the closest completion measure is RFC-937 §7's own
acceptance items, and W37-6 has not closed. **Answer: not applicable to derive a completion
number now; the honest statement is that `docs/roadmap.md`'s WK-697 row is itself out of date**
(§4 below) and should not be read as evidence either way until the next update.

#### 2. Omission — what would nobody notice was missing?

**A live example, found by this review rather than relayed from the brief.** `scripts/doc-id.py`
builds `token_map` with a bare assignment, no collision guard:

```
if d.old_token is not None and d.prefix != "FD":
    token_map[d.old_token] = canon
```

(`scripts/doc-id.py:5802`, read directly.) Two drafts sharing one `old_token` — the shared
task list's live item #25 names `OQ-539` claimed by two generated ids — silently overwrite
each other; the second write wins and the first is unresolvable by name in every citation the
sweep rewrites. **This is the same defect *shape* as three things already found and fixed or
ruled this window**: the `grep -c` false-zero (Amendment 2), the 36-dangling-link class (gate
condition 7), and F90's detector-blind-to-real-input pattern — a check, a map, or a scan that
returns a clean answer over a population it cannot actually see the collision in. **What would
catch this earlier than the gate**: an `assert tok not in token_map` (or an explicit
last-writer-wins decision, stated) at the exact line above, mirroring the
`assert classified == seen` pattern `docs/findings/register.md`'s own header already names as the
right shape for this class (line 34). **Recommendation, not a code change (§0's table — this
is squarely inside W37-6's own scope, so it is code, but not this review's to write): file it
as a register row today**, disposed as **fix before close, W37-6**, not deferred — it is a
silent-corruption class inside the one-way commit, the exact thing gate condition 7 exists to
catch, and it was found before the write only because someone happened to look, which is
`CLAUDE.md` §13's "a check that has never printed a failure has not been tested" from the other
side: a map that has never been asked to prove it has no collision has not been tested either.

**The broader pattern, stated once rather than four times**: every repeat-defect class this
window (citation-rewrite gaps across six mechanisms, the `grep -c` false zero, the 36 dangling
links, and now `token_map`) shares one shape — a **relayed or unguarded aggregate** standing in
for a **verified population**. Amendment 2 (relayed verification does not count) already fixes
the *reporting* half. It does not fix the *construction* half — a script producing the
aggregate with no internal guard. **Is gate-catching the right design, or should there be a
plan-level change?** Both — gate-catching is correct as a backstop (that is what caught all
four), but a backstop that has now caught the same shape four times in one window is evidence
for a class-level rule, not four individual fixes. Recommend: `.claude/skills/python-package`
or `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` gains one line — every `dict` built inside
`doc-id.py`'s migration path from a per-document key either asserts no prior key, or documents
why the overwrite is intended — checked once, cheaply, rather than found once per instance.

#### 3. Skills and research — gap analysis

**No skill claims coverage it does not have, on this window's evidence.** `dev-commands`,
`git-hygiene` and `phase-review` were all read fresh for this review and matched what they
described. **One skill is silently ahead of the code, in the direction §14 exists to catch
early rather than late**: `.claude/skills/close-workstream` is `W37-11`'s named executor skill,
and its checklist (per its own description) audits "one workstream against its own scope" —
but W37-11's scope, as this review's premise-correction above narrowed it back to (j)/(k) plus
synthesis, is not the scope currently accumulating against its name (F92, and the candidates
discussed under question 5). No action recommended here beyond what question 5 already says;
naming it once is enough.

#### 4. Document drift

**`docs/roadmap.md`'s WK-697 row is stale, confirmed by direct read (§ preamble above)** — it
predates the delegation, both renewals, and both halted windows. This is the same defect class
RFC-756 exists to name (a duplicated/carried status going stale) and F95 exists to exemplify
one level down.

**F95's register row is stale, verified directly rather than taken from the handover.**
`docs/findings/register.md:136` reads: *"not started, `WF` half; `FD` half in progress."*
`docs/roadmap.md:382` and `git log` both show `2f0467e` (PR #671, "implement the FD and WF
document families... `none` 110 → 0") merged before this tree. **The row's Decision cell has
not been updated since**, and no citation on the row points at `2f0467e`. Recommend: the
auditor's next touch of the register updates this cell to the delivered state, citing the
PR — this review does not edit the register (`.claude/roles/planner.md` does not own it).

**Three findings discussed in the renewed-window handover's §7 have not yet been filed as
register rows at all** — verified by their absence from `docs/findings/register.md` at this tree:
the `F<n>` low-range ambiguity (three independent audit eras reusing the token, `F12` alone
naming three findings), the `was:`-path corruption in `_rewrite_citations`, and the F23/F24/F25
structural drift in `docs/findings/register.md`. The shared task list's own items #17
and #19 ("File four findings from #671 at the run's closure record") confirm this is known and
pending, not missed. **Recommendation: file them before the next go-ahead ask**, each with
Amendment 3's field where it applies, and each disposed by class rather than left to whichever
document happens to mention them — a finding that exists only as handover prose is exactly the
shape `docs/findings/register.md`'s own header warns against ("a deleted row leaves every citation
to it dangling" applies with equal force to a row that was never written).

#### 5. Shape — is the W37-6/W37-11 cut still right?

**This is the sharpest question, and the answer is: the map plan's cut is still coherent; the
window's *practice* has drifted wider than it, without a matching amendment.**

The map plan (`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:828`) gives W37-11 a
narrow charter: acceptance items (j) and (k), and a closure record that **synthesises** evidence
already produced elsewhere plus a verdict on every requirement without evidence. It is not a
general remediation bucket for defects the migration run itself produces. Weighed against that
charter, three different things are currently being routed to "W37-11" by three different
mechanisms, and only one of them is properly authorised:

1. **F92 (53 deferred Reference-stamp files) — properly authorised.** A dated maintainer offer,
   a lead's named choice between two options, recorded in a squash-commit body and echoed in
   the register row. This is what a boundary move should look like.
2. **Amendment 3's backfill clause ("the backfill is W37-11's") — the mechanism is right, the
   destination is under-specified.** Amendment 3 itself (flagging a merged-but-unimplemented
   ruling) is the smallest fix for a real gap (six decided-but-unimplemented items in one
   window) and is already working as designed — RL-1041's own record carries
   `implementation: owed` exactly as specified. But "the backfill is W37-11's" was written as a
   blanket routing rule before any concrete backfill existed to route. Now one does: RL-1047
   requires seven maintainer-authored prose documents to migrate as `RL-`/`owner: maintainer`
   rather than `PL-`/`owner: planner`, and that rewrite has not landed (shared task list #20,
   "in progress"). **This is corpus-migration correctness, the same class as F90 and F96, not
   closure synthesis** — if it ships unfixed, the migrated corpus itself is wrong on its own
   ruled terms, which is precisely what W37-6's gate exists to catch before the one-way write,
   not what W37-11's closure record exists to narrate after it.
3. **F12's citation ambiguity, the `was:` corruption, F23/F24/F25's structural drift, and now
   `token_map`'s collision — routed to "W37-11" informally, by nobody's dated ruling.** These
   are not in the map plan's W37-11 scope, they are not F92-shaped authorised moves, and three
   of them are not even filed as register rows yet (§4 above). They are migration-defect fixes
   of exactly the kind gate condition 7 was promoted to catch, being informally destined for a
   closure-record workstream whose charter is to *write down what happened*, not *fix what the
   run got wrong*.

**Recommendation: split the "owed to W37-11" pile along the line the map plan already drew**,
rather than re-cutting the workstream. Corpus-correctness defects — anything that makes the
migrated tree itself non-compliant with RFC-937's own ruled terms (RL-1047's implementation,
the `token_map` guard, F96's silent-fallback, the `was:` corruption) — are **W37-6 fix-before-
close items**, on F87/F88's own precedent and gate condition 7's own precedent (a repeated
defect class gets promoted into the gate, not deferred past it). Genuinely downstream,
design-shaped items — F12's alias-resolver (a tool W37-11's successors need, not a defect in
the corpus itself), F93's documentation-consistency verdict, F94's predicate note — stay
W37-11's, matching its charter. **This is not a re-cut**: no slice moves, no id changes, no
new row. It is a recommendation that "owed to W37-11" stop being used as a catch-all label for
anything found late in W37-6's window, because that is the omission question (2) recurring at
the workstream-shape level — a label doing a filing job it was never scoped to do, and nobody
would notice until W37-11 opens holding more than `close-workstream`'s own charter describes.

**No re-cut of W37-6 vs W37-7…W37-10 vs W37-11 as workstreams is recommended.** The eleven-slice
structure and its dependency chain (`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:364-
368`) still fit the work as evidenced; the defect is in *routing*, not in the *cut*.

---

#### Proposal summary

| # | Question | Finding | Recommendation |
|---|---|---|---|
| 1 | Completion | Not derivable — W37-6 open, roadmap row stale | No number claimed; fix the roadmap row when W37-6 closes |
| 2 | Omission | `token_map`'s ID-half has no collision guard, the fourth instance of one repeat-defect shape this window | File today as fix-before-close, W37-6; add a class-level guard rule to the migration-path convention |
| 3 | Skills | `close-workstream`'s charter for W37-11 is narrower than current practice is routing to it | No skill edit; resolved by proposal 5 |
| 4 | Drift | Roadmap WK-697 row stale; F95's register cell stale (verified against `2f0467e`); three found-not-filed findings (F12 range, `was:` corruption, F23/24/25) | Update the register cell; file the three findings before the next go-ahead ask |
| 5 | Shape | Map plan's W37-11 cut (items (j)/(k) + synthesis) is coherent; practice is routing corpus-correctness fixes to it beyond that charter, informally | Route corpus-correctness defects to W37-6 fix-before-close (or a promoted gate condition); keep design/synthesis items on W37-11; no workstream re-cut |

**Two corrections to this review's own commissioning brief**, recorded per the skill's own
rule rather than silently acted on: the RFC-937 §7 owner split is (a)-(i) W37-6 / (j)-(k)
W37-11, not (a) vs. (b)-(k); and "RL-989's class-6 extension ratification" / "the
lettered-ruling nested-span floor" do not resolve against `docs/` at this tree and should be
re-cited, not carried forward, once the two live worktrees' pending PRs land.

#### Sources

- `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md:424-430` (§7 acceptance, §8 sequencing) — read
  directly.
- `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:364-368,824-844,892-894` (dependency
  table, Slice W37-11, spec-coverage map) — read directly.
- `docs/rulings/RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md` (all seven sections) — read directly
  in full.
- `docs/plans/PL-01038-w37-6-handover-at-the-close-of-the-delegated-window-2026-09-03.md`,
  `docs/plans/PL-01034-w37-6-handover-at-the-halt-of-the-renewed-delegated-window-2026-09-03.md` — read directly in full.
- `docs/findings/register.md` rows F86–F96, F92, F95 — read directly at `198ea5d`.
- `docs/roadmap.md:382` (WK-697 row) — read directly.
- `scripts/doc-id.py:5802` (`token_map` assignment) — read directly.
- `python3 scripts/register-owed.py review`, run against `198ea5d` — 21 owed rows, 1 excluded.
- `python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show` — run this
  session, confirming F91's staleness figure.
- `git log -1 --format=%B db19be8` — run this session, confirming F92's reassignment source.
- Shared task list (this session's `TaskList`), items #17, #19, #20, #25–28 — read directly, for
  the in-progress items §2 and the premise-correction cite.
- `git grep` for "class-6", "ratif", "nested-span", "lettered" across `docs/` — run this
  session, returning no ratification or nested-span-floor citation.

**Maintainer acceptance:** _pending_
