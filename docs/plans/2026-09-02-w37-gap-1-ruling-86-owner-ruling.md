# Gap 1 — Ruling 86 §3 item 2 does not survive; the A-series takes `owner: decision-maker` (2026-09-02)

**What this is.** Gap 1 of `docs/plans/2026-09-02-w37-owner-field-derivation.md` §227: *"does
Ruling 86 item 2 survive its premise failing?"* — framed there and deliberately not answered,
and confirmed by the maintainer on 2026-09-02 as staying with this role. **Ruled below as
Ruling 95.**

**It does not survive, and the decisive evidence is not the failed premise.** §1.6's `RL` row
already contemplates a ruling authored by someone other than the decision-maker, names the
highest such case, and **leaves the owner unchanged**:

```
| **RL** | decision-maker; the maintainer may author one on scope or process |
```

**If a maintainer-authored ruling still has `owner: decision-maker`, a lead-approved one does
too.** The table is not silent on author-versus-owner; it settled the question and Ruling 86
read past it.

**And this is a self-correction rather than a new position.** [Ruling 88](2026-09-02-w37-container-family-and-line-citations-rulings.md)
§2 — filed two records later, and *against* a derivation that recommended the author reading —
already ruled the general principle: *"§1.6's column is 'Owner — creates & amends', not
'author'. It names who is responsible for the document, and it explicitly contemplates a
different drafter."* **Ruling 86 item 2 and Ruling 88 §2 are in direct contradiction and I did
not notice when I wrote the second.** Gap 1 is that contradiction surfacing, and Ruling 88 is
both the later ruling and the general one.

## Authority

- **Routed by the lead on 2026-09-02**, with the maintainer's confirmation that *"gap 1 stays
  with the decision-maker as the derivation proposed"*.
- **It is not the maintainer's, and the lead was right to offer that route.** The exit that
  *would* have been theirs is the one rejected here: making `RL` a standing exception to the
  family table needs *"the departure recorded somewhere a reader of §1.6 will find"*, which is a
  §1 edit. **The answer ruled here restores §1.6 rather than amending it**, so no §1 text
  changes and nothing goes back.
- **Every figure is measured at `64f63ee`**, `origin/main`'s tip when this record was written
  and this branch's base.
- **Ruling 86 is not edited.** An amendment to a filed ruling is a new dated artifact — the rule
  Ruling 86's own siblings state, applied to Ruling 86.

## Acceptance Standard

`audit-docs.py` check 28 requires this section on dated `docs/plans/` files outside four
suffixes while its own docstring disclaims that scope — register finding F68. Honoured; the
check is not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 95 immediately after 94, no duplicate, no skip.
2. §2 names the chosen exit **and** the rejected one, with what each would have cost.
3. §3 says exactly which clause of Ruling 86 item 2 is struck and which survives — the failure
   mode of an amendment is striking more than failed.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-ruling-95-gap1-owner` names exactly this one new file.
6. Every claim about the code was produced by executing it, using **the module's own patterns**,
   never an approximation — §1(d) records what happened when I used an approximation first.

---

## Ruling 95 — `owner:` is who may amend; the A-series takes `decision-maker`

### 1. Verified first, at `64f63ee`

**(a) The table answers the question directly.** §1.6's column header is **"Owner — creates &
amends"**, not "author", and the `RL` row reads *"decision-maker; the maintainer may author one
on scope or process"*. **The row names an exception author and does not make it an exception
owner.** That is the whole case: the standard anticipated author ≠ owner for this family and
resolved it in favour of the table.

**(b) The premise Ruling 86 stood on does fail, as the derivation measured.** Ruling 86 §1(b)
quoted the 2026-08-30 delegation correctly — *"authorise you to approve NT-0012 NT-0013 and
NT-0014 landing on behalf of me"*, read narrowly as *"the landing … and nothing else"* — and
then drew from it a conclusion that narrow reading excludes. **A grant of an act is not a grant
of an ownership**, and amending those rulings later is one of the other purposes the grant
does not reach. The quotation was right; the inference from it was not.

**(c) The contradiction with Ruling 88, in both records' own words.**

| | |
|---|---|
| **Ruling 86 §3 item 2** (`:126`) | *"`owner:` is not `decision-maker` for these three"* |
| **Ruling 88 §2** (`:95`) | *"§1.6's column is 'Owner — creates & amends', **not 'author'** … The planner's authorship is not erased by this; it is in the body and in `was:`."* |

Ruling 88 reached that against a planner derivation recommending the author reading, for the
`RFC` family — whose §1.6 row contemplates a different drafter in exactly the way the `RL` row
does. **Applying Ruling 88's own reasoning to `RL` yields `decision-maker`.**

**(d) What the code does today, run with the module's own pattern.** `_ruling_file_owner`
defaults to `_RULING_DEFAULT_OWNER = "decision-maker"` and departs only where a delegation
heading matches. Executing `_RULING_DELEGATION_HEADING_RE` over every `docs/plans/*.md`:

```
files matching the delegation heading: 1
  lead           docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md
```

matching `### 1.1 The delegation — the maintainer's acceptance authority, delegated to the
lead`. **The departure branch is live and fires for exactly the A-series, producing
`owner: lead`.**

**A false null on the way there, recorded because it is the class this Work keeps meeting.**
My first probe was `git grep -lE '^#+ The delegation'`, which returned **nothing** — the real
pattern is `^#{1,6}\s+[\d.]*\s*The delegation\s*—.*$`, and the heading carries a section number
(`1.1`) my approximation could not cross. **Running an approximation of a script's pattern
instead of the pattern is how a live branch reads as dead**, and it would have made this ruling
report that nothing needed changing.

### 2. Ruled

**Ruling 86 §3 item 2 does not survive as to Rulings A1–A3. They take `owner: decision-maker`,
the value §1.6's `RL` row gives.**

`owner:` is **who may amend**, not who wrote. The attribution concern that motivated Ruling 86
item 2 is real — *a frozen record must not attribute a decision to a role that did not make
it* — and it is **not what this field expresses**. Authorship is preserved where Ruling 88
already put it: in the record's own body, which says who ruled and under what grant, and in
`was:`, which keeps the source path. **Nothing about the A-series' history is lost by this
ruling; only the field that never carried it is corrected.**

**Rejected: it survives, and `RL` becomes a standing ruled exception to the family table.** The
derivation's first exit, and a coherent one. Rejected on three grounds:

1. **It requires §1.6 to be silent on author-versus-owner, and it is not.** §1(a) — the `RL` row
   names the maintainer as a possible author and keeps the owner. An exception cannot be built
   on a silence that does not exist.
2. **It would need a §1 edit to be findable**, by the derivation's own condition — *"recorded
   somewhere a reader of §1.6 will find"* — which is the maintainer's, and which would convert
   a self-inflicted contradiction into a permanent change to the standard.
3. **It would leave Rulings 86 and 88 contradicting**, with the later and more general one
   losing to the earlier and narrower one.

**Rejected: routing it to the maintainer.** Offered by the lead, and declined for the reason in
Authority: the surviving answer restores the table rather than amending it.

### 3. What it obliges — and what is *not* struck

1. **Ruling 86 §3 item 2's first clause is struck as to the A-series.** They take
   `decision-maker`.
2. **Item 2's second clause survives untouched**: `_discover_plain_plans`'s
   `owner="planner"` hardcode is still wrong for the standalone ruling files, and
   **Ruling 87 §3 item 2 — which ruled `decision-maker` for those three — is unaffected and was
   always consistent with the table.** An amendment that struck the whole item would re-open a
   correct ruling; the failure mode of an amendment is striking more than failed.
3. **`_ruling_file_owner`'s departure machinery is removed, not left inert.** With the
   exception gone, `_RULING_DELEGATION_HEADING_RE`, `_RULING_DELEGATION_ROLE_RE` and the
   `NotImplementedError` have no case to serve, and a dead branch that once encoded a reversed
   ruling is worse than no branch. Every `RL-` takes `_RULING_DEFAULT_OWNER`.
4. **The executor's design was right for the world Ruling 86 created**, and PR #603 implemented
   that ruling faithfully — defaulting to the table, departing only on an explicit heading,
   raising rather than guessing. **It is being removed because the ruling it served was wrong,
   not because the implementation was.** Recorded so the removal is not read as a defect
   finding against it.
5. **The lead's earlier objection to #603 on §1.6 grounds was wrong when made and is right
   now.** It was wrong because Ruling 86 governed; it is right because Ruling 95 does. Recorded
   so neither position is re-litigated from the other's date.

### 4. Acceptance — the violation that must become detectable

**The violation: an `RL-` record carries an `owner:` that is not `decision-maker`.**

- **Every emitted `RL-` carries `owner: decision-maker`.** *Violation: an `RL-` whose owner
  varies by document content.* The positive control exists today and must red before the fix:
  `_ruling_file_owner` returns `lead` for `2026-08-30-nt-0012-0013-0014-adoption.md`, measured
  in §1(d).
- **No code path derives an `RL-`'s owner from the document's text.** *Violation: a
  content-derived owner in a family whose owner is a constant.* A grep for the removed
  constants returning nothing is the check; it must fail today, when both exist.
- **Ruling 87's `decision-maker` for the three standalone ruling files still holds after this
  amendment.** *Violation: an amendment that changes a ruling it did not name.* This is the
  collateral-damage check §3 item 2 exists for, and it is cheap: the same assertion as the
  first item, over a different set.

---

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **Whether a `written_by:` or equivalent authorship field should exist** | The derivation names the missing field as the proper home for attribution. Adding a field to §1.5's closed set is a §1 amendment, and Ruling 70 held that adding `decision:` *"is an edit to §1 … and it would have gone back to the maintainer"* | **The maintainer**, via the `RFC-` route, if anyone wants it. **Nothing depends on it**: Ruling 95 does not create the need, it declines to solve attribution with the wrong field |
| **Gap 2 — the 44 `SKILL.md` files with no owner** | The maintainer ruled it theirs as a §1 amendment on 2026-09-02 | **The maintainer**, unchanged |
| **Whether any other merged ruling contradicts a later one** | Gap 1 is one instance, found because a derivation went looking. Whether there are others is a measurement over fifteen ruling records | **The lead**, and it is a natural companion to the acceptance-item sweep already running — same corpus, same read |

## Provenance

Routed by the lead on 2026-09-02 with the maintainer's confirmation, an accurate self-contained
statement of the problem, and a correction of the lead's own earlier objection to PR #603. The
derivation framed both exits fairly. The evidence that decides between them — §1.6's `RL` row
naming a non-decision-maker author without changing the owner — is in neither the derivation nor
the routing brief, and neither is the contradiction with Ruling 88; both were found by reading
the row and my own later ruling after the premise question was already answered.
