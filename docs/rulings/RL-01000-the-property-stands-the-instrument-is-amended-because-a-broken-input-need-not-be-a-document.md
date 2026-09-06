---
id: RL-1000
family: ruling
title: the property stands; the instrument is amended, because a broken input need not be a document
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-vacuous-acceptance-item-ruling.md
---

# A vacuously-true acceptance item does not satisfy itself — RL-986 §4's `slice:` clause, ruled (2026-09-02)

**What this is.** The executor implementing [RL-986](RL-00986-the-ten-wk-661-slice-records-become-lg-carrying-work-and-no-slice-no-template-edit-is-needed.md)
found that its second acceptance item cannot fail: `_stamp_header` never writes `slice:`, so a
check that *"no emitted `LG-` carries a `slice:` whose value resolves to no roadmap row"* guards
nothing. Flagged rather than silently satisfied or silently ignored, which was right. **Ruled
below as RL-1000.**

**The lead's reading is correct and its proposed remedy is not adopted**, because a better one
keeps the property instead of narrowing it. **The broken input does not have to be a fixture
document — it can be a mutation of the writer**, which is the shape RL-981 item 2 already
established and Rulings 79 and 80 already use.

**One correction, and it changes what a reader would do with the report.** The routing brief
quotes the skip as `elif key in ("phase", "work", "slice", "deliverable", "lands_in",
"trigger"): continue` and dates it to `614c92c`. **At `614c92c` that line already reads
`elif key in ("slice", "deliverable", "lands_in", "trigger")`** — `phase` and `work` were split
out into separately-guarded branches *by `614c92c` itself*, the RL-986 implementation. §1(a)
has both. Acting on the quoted form would mean believing RL-986's positive obligation —
`work:` resolved to WK-661's `WK-` id — is unimplementable. It is implemented.

## Authority

- **This interprets a merged ruling of this role's own**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places here; the
  lead correctly declined to decide it. **It is not the maintainer's**: no §1 text is read,
  amended, or relied on beyond §1.2's already-settled field set, and the answer changes an
  acceptance item's instrument rather than the standard.
- **It lands as a new dated artifact, never an edit to RL-986** — the same rule RL-994
  applied to RL-979.
- **Every figure is measured at `d47a5f5`**, `origin/main`'s tip when this record was written and
  this branch's base; the two-commit comparison in §1(a) names its own trees.

## Acceptance Standard

`audit-docs.py` check 28 requires this section on dated `docs/plans/` files outside four
suffixes while its own docstring disclaims that scope — register finding F68. Honoured; the
check is not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 94 immediately after 93, no duplicate, no skip.
2. The substituted acceptance item names a broken input that **exists and can be produced**, and
   §2 says what produces it.
3. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
4. `git diff --stat origin/main...docs/w37-ruling-94-vacuous-acceptance` names exactly this one
   new file.
5. Every code quotation is taken from the tree named beside it, not from a report.

---

## RL-1000 — the property stands; the instrument is amended, because a broken input need not be a document

### 1. Verified first

**(a) What the code actually says, at both trees.**

```
$ git show 614c92c:scripts/doc-id.py | grep -n 'elif key in ("slice"'
928:        elif key in ("slice", "deliverable", "lands_in", "trigger"):
$ sed -n '946p' scripts/doc-id.py                      # d47a5f5
        elif key in ("slice", "deliverable", "lands_in", "trigger"):
```

`phase` and `work` are **not** in that tuple at either tree. They are separately guarded:

```python
elif key == "phase":
    if phase is None: continue
    line = re.sub(r"phase:\s*\S+", f"phase: {phase}", line)
elif key == "work":
    if work is None: continue
    line = re.sub(r"work:\s*\S+", f"work: {work}", line)
```

and the `LG-` path passes both (`scripts/doc-id.py:2151`, `phase=phase_value,
work=work_value`). `_stamp_header`'s own docstring records the change: *"`phase`/`work` are
optional (default `None`, **dropped exactly as before RL-986** — every caller but
`_write_document_drafts`'s `LG-` path leaves them unset)"*.

**So RL-986 §2's positive obligation is implemented, and §4's third acceptance item — a
resolving `work:` — is live rather than vacuous. Only the `slice:` item is vacuous.** The
report's quoted tuple is the pre-`614c92c` form; the observation about `slice` survived a fix
that changed the line it cited.

**(b) The vacuity is real.** `slice` is skipped unconditionally for every caller, so no emitted
`LG-` can carry the key, so no value of it can fail to resolve. Nothing is ever wrong because
nothing is ever written.

**(c) And `slice:` is supposed to remain writable.** RL-986 §3 item 5: *"`slice:` stays
permitted for every other ledger. Nothing here narrows the field; a ledger cut from a map plan
carries it as the template shows."* The skip is a *"no data source"* decision for this
migration, not a narrowing of the family — which is why an amendment that redefines the property
as *"no `LG-` carries a `slice:` at all"* would have to be widened again the moment one does.

### 2. Ruled

**Vacuously true does not satisfy an acceptance item whose form is "must red on deliberately
broken input." `CLAUDE.md` §13 is explicit — *a check that has never printed a failure has not
been tested* — and the lead's reading is adopted.**

**But the property is not narrowed. The instrument is.** RL-986 §4's second item is
substituted:

**Struck:**

> A check that no emitted `LG-` carries a `slice:` whose value resolves to no roadmap row.
> *Violation: a `slice:` naming nothing.* … it must red on a deliberately broken fixture
> carrying `slice: SL-99999`.

**Substituted:**

> **A check that counts the `slice:` values on emitted `LG-` records and requires every one to
> resolve to an `SL-` row, printing the count it checked.** *Violation: a `slice:` naming
> nothing.* The passing state today is a count of **zero**, and the check must **say so** rather
> than pass silently — a boundary metric that reads zero by construction reports where the
> boundary sits, not that anything was verified ([`RFC-789`](../rfcs/RFC-00789-zero-calls-above-200k-tokens-measures-the-compaction-cap-not-discipline.md)).
> **The deliberately broken input is a one-line mutation of `_stamp_header`** — remove `slice`
> from the skip tuple so the template's `slice: SL-NNNNN` placeholder is emitted — after which
> the check must red. It is not a fixture document.

**Why this and not the lead's invariant.** The proposal — *no emitted `LG-` carries a `slice:` at
all* — is a real check with a real failing case, and it is **narrower than the ruling it serves**
(§1(c)): it encodes this migration's "no data source" state as the rule, so it would red
correctly today and wrongly the first time a ledger legitimately carries a slice. The
substituted form fails on the same mutation, and stays right afterwards.

**Why the broken input may be a writer mutation.** The struck clause said *"fixture"*, and that
word is what made it unbuildable — a fixture document cannot carry a key the writer refuses to
emit. **RL-981 item 2 already established the other shape**, and Rulings 79 and 80 both use
it: *"add a key to `WK.md` and a row using it parses; remove a key and the same row is
rejected."* A mutation of the producer is a deliberately broken input in exactly the sense §13
means. **The struck clause was over-specified, not wrong.**

### 3. What it obliges

1. **RL-986 §4's second item is read as substituted from this record's date.** RL-986 is
   not edited; its other three items stand, and its third — the resolving `work:` — is live.
2. **The count is printed.** A check whose passing state is zero says which zero it counted, or
   it is the `_ID_SCOPE_ROOTS` shape the lead correctly named: true, and telling you nothing.
3. **W37-5b's closure record can discharge this deferral** by naming this ruling, rather than
   carrying it forward.
4. **Nothing goes to the maintainer.** The lead asked to be told if it did. It does not: no §1
   text is amended and the field set is untouched.

### 4. Acceptance — the violation that must become detectable

**The violation: an acceptance item passes because nothing exercises it.**

- **The `slice:` check reds under the `_stamp_header` mutation of §2**, and its output names the
  count it checked in both states. *Violation: a check that passes identically before and after
  a mutation to the thing it checks* — the signature §13 describes and the one the struck clause
  could not detect.
- **RL-986 §4's third item is exercised too**, since §1(a) shows it is live: an emitted `LG-`
  with `work=None` must red. *Violation: assuming an item is satisfied because its sibling was
  found vacuous.*

---

## The sweep now has two shapes, and it is still not mine

RL-994 routed onward *"whether other filed acceptance items name unbuildable fixtures"*. **This
is a second instance arriving by a different route, and the two are different failure modes:**

| Shape | How it arises | Instance |
|---|---|---|
| **Invalidated** | The item was constructible when written; a later change removed the thing it named | RL-979 §4 item 2, after `#609` demoted the heading levels |
| **Vacuous at birth** | The item was never constructible; the code path it names has never existed | RL-986 §4 item 2, from the day it was written |

**The second is worse**, because nothing about the repository changed to signal it — there is no
commit to notice. It is found only by trying to build the check, which is what the executor did.

**Still a measurement rather than a decision, so still the lead's**, per RL-994. What this
record adds is that the sweep looks for two shapes, and that the *vacuous-at-birth* one is
detectable statically: **an acceptance item naming a value that no code path writes.** Fourteen
ruling records now carry acceptance items.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **The sweep over filed acceptance items** | A measurement. RL-994 routed it; this sharpens what it looks for | **The lead**, unchanged |
| **Whether `slice:` should gain a data source in this migration** | RL-986 §3 item 3 already settled that no `SL-` row is minted, and the refutation section of the template-parser record settled that the clause is vacuous rather than unsatisfiable | **Nobody — already decided.** Named here so it is not re-opened by this ruling's mention of the key |
| **Whether the pre-`614c92c` quotation reached anything else** | §1(a) corrects it here; whether it was acted on elsewhere is a fact I have not checked | **The lead** — one grep, and worth it because the stale form implies `work:` is unwritable |

## Provenance

Routed by the lead on 2026-09-02, opening with the possibility that it had never been routed at
all — it had not, and the doubt was well placed. The vacuity was found by the executor
implementing RL-986 and flagged rather than silently satisfied. The lead's reading of §13 is
adopted; its proposed remedy is not, for the reason in §2; and its code quotation is corrected in
§1(a) because the correction changes what a reader would conclude about RL-986's other items.
