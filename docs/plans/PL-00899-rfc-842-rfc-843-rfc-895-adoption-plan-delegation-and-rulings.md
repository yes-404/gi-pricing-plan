---
id: PL-899
family: plan
kind: leaf
title: RFC-842 / RFC-843 / RFC-895 adoption — plan, delegation and rulings
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-30
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md
---

# RFC-842 / RFC-843 / RFC-895 adoption — plan, delegation and rulings

**Filed 2026-08-30 against `origin/main` @ `2e4684b`.** This is the adoption's own record under
`docs/process/delivery-process.md` §14: the slice cut, the maintainer's delegation, and each
ruling made under it. It is a working record, revised in place with dated entries, not frozen.

---

## 1. The maintainer's instructions, dated and quoted

Three separate messages on 2026-08-30, in the order given. Quoted rather than paraphrased,
because each changed what the team was doing.

1. **Scope** — *"after slice 2 ends, start adoption of NT0012 NT0013 and NT0014"*, following
   *"stop when slice 2 ends, file all the handover files, and do cleanup"*. WK-671 is **stopped,
   not closed**; the adoption is the next Work.
2. **Weight** — *"I think the quick implementation could help the work move more efficient"*.
   The full §14 ceremony is disproportionate here; the mechanism is what pays.
3. **Granularity** — *"slice ends could be the smallest granularity I think to cut in
   adoptions"*. So: cut into slices, land each on its own. A Slice closes on a clean audit and
   the lead's merge (`CLAUDE.md` §12), which is what lets them flow without a checkpoint each.

### 1.1 The delegation — the maintainer's acceptance authority, delegated to the lead

> *"authorise you to approve RFC-842 RFC-843 and RFC-895 landing on behalf of me"*
> — the maintainer, 2026-08-30

**This is recorded here rather than left in chat because of what it is.** `CLAUDE.md` §12
reserves acceptance of a Work close to the maintainer and says plainly that four things are
never a role's — this being one of them. A delegation of that authority is therefore the
highest-consequence decision in this adoption, and an undated one in a transcript is exactly
the artifact the same section forbids: *"Every decision lands as a dated artifact — a ruling
record, an audit record, a plan — never in chat."*

**Scope of the delegation, read narrowly and deliberately so:**

- It covers **the landing of RFC-842, RFC-843 and RFC-895**, and nothing else.
- It does **not** extend to WK-671's close, WK-672, or any later phase. Those remain the
  maintainer's, and WK-671 in particular is stopped with its §13 audit unrun.
- It does **not** convert the lead into the maintainer for other purposes. Precedent for a
  bounded delegation of this kind is the **M2 delegation** cited in RL-860.

---

## 2. Slice cut

| Slice | Content | State |
|---|---|---|
| **A** | The 2-char `§12`→`§15` fix, the core JSON filed, `CLAUDE.md` §15 and `delivery-process.md` §10 pointed at it | **MERGED** `33b5ef1` (#448) |
| **B** | Check 26 — the drift check, **inside `audit-docs.py`** | **MERGED** `0be9c3c` (#451) |
| **C** | RFC-842's two rules given durable homes | **this record's RL-902/A2** |
| **D** | RFC-843's "remove the relay" | **this record's RL-904** |
| **E** | Runtime state file (RFC-895 artifact B) + watcher | not started |
| **F** | Plan validator C1 + the acceptance-standard field in `writing-plans` | not started |
| **G** | Hooks C2 and C3 | not started — **blocked on RFC-895 Q2** |

**The design decision worth inheriting, from slice B.** Putting the drift check *inside*
`scripts/audit-docs.py` rather than in a new script deletes impact-matrix rows 2 and 21
entirely and means **RFC-895's open question Q2 — where hook registration lives — never has to
be answered for C4.** Q2 still gates C2 and C3, which genuinely need hooks. At `2e4684b` there
is still no `.claude/settings.json` and no `.claude/hooks/`.

---

## 3. Rulings under the delegation

### RL-902 — RFC-842's credential-lifetime rule lands in `.claude/skills/secret-hygiene`

RFC-842 left this open, offering *"whichever role's charter owns posting to an external
channel"* as a candidate.

**Rejected, and the reason matters more than the choice.** The rule is general — *any* value a
later session must reuse is borrowed, not stored, if it lives in a job directory, a handover
file, or a session's memory. Landing a general rule in one role's charter binds one role to a
rule that applies to all of them, and leaves every other role free to repeat the failure. It
also splits the subject: `secret-hygiene` already exists and already owns credential handling.

**Ruled: `.claude/skills/secret-hygiene`.** One source, and the skill a session already opens
when it is about to do the thing the rule governs.

### RL-903 — RFC-842's search-by-shape rule lands in `.claude/skills/close-workstream`

The note describes it as needing *"a search-discipline note or skill"*, which does not exist
under that name.

**Ruled: beside `close-workstream`'s existing "A false zero argues" section** (`:310`). That
section already reasons about a search returning nothing and the nothing being used as
evidence. RFC-842's rule is the same failure one step earlier — searching for the *container's
name* rather than the *thing's shape*, so the zero is manufactured by the query. Putting the
general rule against the worked example is one source; a new skill would be a second place to
look and a second place to go stale.

Cross-referenced from `secret-hygiene`, because the instance that produced the rule was a
credential and that is where someone will be standing when they need it.

### RL-904 — RFC-843's "remove the relay" lands in `delivery-process.md` §15

**Ruled: immediately after §15's existing third bullet**, the one that already states
*"Verify against the primary source; never implement against a relay."*

The two are one rule with two halves, and separating them is what let the weaker half land
alone in the first place. The existing bullet says **do not trust a relay**; this says **do not
create one**. A reader who finds only the first concludes the fix is more careful reading,
which is precisely the conclusion RFC-843's eight instances refute — the lead was reading
carefully each time.

---

## 4. Acceptance, under §1.1's delegation

| Slice | Accepted | Date |
|---|---|---|
| A | Clean gate, merged `33b5ef1` | 2026-08-30 |
| B | Clean gate + six-mutation proof with a silent negative control, merged `0be9c3c` | 2026-08-30 |
| C, D | *pending the PR that implements Rulings A1–A3* | — |

**E, F and G are not accepted and not started.** The delegation covers them when they land; it
does not pre-approve them. G stays blocked on Q2.

---

## 5. What this adoption inherits, and must not inherit silently

The §14 plan review at WK-671's close **did not run** — the run stopped before the close. It was
carrying **F27(c), F29 and F33** as *one* gate-coverage item, on the reasoning that a single
mechanism answers all three and a partial fix on any one row is not the target shape.

RFC-895's C4 is a mechanism of exactly that family. So:

- **F33 is materially advanced**, not by this adoption but alongside it: `c8d3c81` (#450)
  extended mypy's `files` to the test trees, `examples/fremtpl2` and two skill directories,
  and `uv run mypy` now reports **no issues across 163 source files**. The three test suites'
  own debt (144 / 107 / 1243 errors) is reported and unfixed.
- **F27(c) and F29 remain open and are not this adoption's by default.** They are named here so
  that a later reader cannot mistake silence for a decision. **Whoever runs slice E or F must
  either take them deliberately or record that they left them.**
