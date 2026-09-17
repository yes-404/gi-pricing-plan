---
id: FD-1024
family: finding
title: widening `_ID_SCOPE_ROOTS` reaches no non-markdown file, so 62 of the 65 exempt files stay invisible to checks 30-39
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F87.md
---

# F87 — widening `_ID_SCOPE_ROOTS` reaches no non-markdown file, so 62 of the 65 exempt files stay invisible to checks 30-39

**Raised** 2026-09-02 by `exec-5c-exemption`, from the W37-5c item 3 build. Work item **W37-6**,
scope: the `_ID_SCOPE_ROOTS` widening. Phase 2.

**This is a precondition W37-6 cannot run without, and it was on no list.** It belongs with F80,
F81 and F82 — with one difference that makes it worse than all three: **they abort the run and
name themselves. This one passes.**

## The defect

`scripts/audit-docs.py`'s `_id_scope_documents()` builds the corpus for every one of checks 30-39.
It treats its two kinds of root differently:

| Root kind | How it contributes |
|---|---|
| A **file** | appended verbatim, whatever its extension |
| A **directory** | expanded by `rglob("*.md")` — **markdown only** |

`_ID_SCOPE_ROOTS` is a tuple of *directories* plus one file. So widening it to the whole corpus —
which is what W37-6 does, and what RFC-937 §1.11 check 30 describes as *"every file under `docs/`,
every charter, skill and agent"* — brings in **no non-markdown file at all**. The glob is the gate,
not the roots.

## The measurement

`_ID_SCOPE_ROOTS` substituted with the four post-migration roots
`(docs/, .claude/roles/, .claude/skills/, .claude/agents/)`, then `_id_scope_documents()` called:

| | At merge-base `359936b` | At this branch's head |
|---|---|---|
| Paths collected | 584 | 585 |
| Of those, **not** `.md` | **0** | **0** |
| Of `UNSTAMPABLE_EXEMPTIONS`'s 65 entries, reached | **3** | **3** |

**The two figures this finding rests on are the bolded ones, and neither has moved at any tree
it has been measured at** — `e63332c`, `7186dca`, `c0739ac`, `f61f9a4`, `359936b`. Zero
non-markdown files reached; 3 of 65.

**The collected total is not one of them, and is tree-tagged because it drifts by construction.**
Every markdown file added anywhere under `docs/` moves it: it was 583 at `f61f9a4`, 584 once F86
was filed, 585 with this file. The stamp set moves with it — 415, then 416, then 417 — and
`51 + 363 + 3 = 417` at this head. **This document is inside the corpus it measures**, so a bare
total here would be a self-referential figure that is wrong the moment it is committed. The
invariants are what the finding is about; the totals are context, and they carry their tree.

The three reached are the vendored `SKILL.md` manifests, which are markdown:
`.claude/skills/create-adaptable-composable/SKILL.md`, `.claude/skills/planning-with-files/SKILL.md`,
`.claude/skills/vue-best-practices/SKILL.md`. **The other 62 — the 59 `.json` and 1 `.yaml` under
`docs/contracts/`, `docs/process/delivery-process.core.json` and
`docs/research/file-census-5ef559d.csv` — are reached by nothing.**

Reproduce with the shipped symbols rather than these numbers:

```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location("a", "scripts/audit-docs.py")
m = importlib.util.module_from_spec(spec); sys.modules["a"] = m; spec.loader.exec_module(m)
setattr(m, "_ID_SCOPE_ROOTS", (m.ROOT, m.REPO / ".claude" / "roles",
                               m.REPO / ".claude" / "skills", m.REPO / ".claude" / "agents"))
rels = {p.relative_to(m.REPO).as_posix() for p in m._id_scope_documents()}
len(rels)                                              # drifts with the corpus; tree-tagged above
len([r for r in rels if not r.endswith(".md")])        # 0 — the finding, at every tree
sorted({e.path for e in m.UNSTAMPABLE_EXEMPTIONS} & rels)   # the 3 manifests, at every tree
```

Pinned permanently by **`test_widening_the_scope_roots_alone_reaches_no_non_markdown_file`** in
`tests/test_audit_docs_ids.py`.

**Amended 2026-09-03 (PR #657) — that pin is gone, and it is gone because the thing it pinned
stopped being true.** The word *"permanently"* above is superseded: the test asserted that
widening `_ID_SCOPE_ROOTS` **alone** reaches no non-markdown file, and this finding's own
falsifiable clause — *"discharged when the scope selector reaches a non-markdown file, proven
on one of the 62 rather than a fixture"* — is what its removal discharges. A test whose
subject is a defect cannot outlive the defect's repair; keeping it would have required the
selector to stay broken.

**Replaced, not merely deleted**, by
`test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts` in the
same file. `_id_scope_documents()` now expands a directory root through the shared
`stamp_set_files` predicate instead of `rglob("*.md")`, so with the four post-migration roots
substituted it reaches **all 65** registered files including **all 62** non-markdown ones,
against **0 of 62** before. Proven on `docs/contracts/openapi/gi-pricing.yaml` — one of the 62,
a real register entry, not a fixture, exactly as the clause requires.

**The clause was falsifiable on the glob, not the roots, and that is what was fixed.** Widening
`_ID_SCOPE_ROOTS` is still not the discharge and never was; the glob was.

## Why it is worse than F80, F81 and F82

Those three stop the run. A W37-6 executor meets them, reads the traceback, and fixes something.

**This one is a silent pass.** An executor widens `_ID_SCOPE_ROOTS`, watches checks 30-39 run
green over every markdown file in the corpus, and ships — having validated **nothing** over the 62 files the F83
exemption register exists for, with every signal green and no artifact disagreeing. The exemption
would be carried, cited, and reconciled on every gate run while the population it exempts was
never in scope to be exempted from anything.

**A check that examines zero of the files it was built for, and passes, is the exact failure
`CLAUDE.md` §13 names**: a check that has never printed a failure has not been tested. Here the
check would print failures — just never about these 62.

## What was believed instead, and by whom

**The lead spent the afternoon of 2026-09-02 telling people that check 30 gets wired to the
exemption register when W37-6 widens `_ID_SCOPE_ROOTS`.** That is the natural reading and it is
wrong: widening the roots is *necessary and not sufficient*, and no artifact said so until this
measurement. `exec-5c-stamp-path` confirmed independently that nothing in its own stamp path
assumes otherwise, having checked only because it was told.

**The assumption is the dangerous part, not the glob.** "Widening the roots widens the scope" is
what the name `_ID_SCOPE_ROOTS` invites a reader to believe, and W37-6 will be planned by someone
holding it unless this row is in front of them.

## Custody

Per [`RFC-778`](../rfcs/RFC-00778-seven-deferred-items-with-no-durable-custody.md), a deferred item with
no owner is not deferred, it is lost. Before this record the fact lived only in a passing test —
which pins it for whoever runs the suite, and is invisible to whoever **plans** W37-6, who is the
person who needs it.

## Falsifiable

**On the glob, not the roots.** Discharged when the checks-30-39 scope selector reaches a
non-markdown file — proven on one of the 62, not on a fixture: a `.json` under `docs/contracts/`
must appear in `_id_scope_documents()` and be seen by check 30, which then consults
`UNSTAMPABLE_EXEMPTIONS` and passes it. Re-opened if the selector is narrowed back to markdown
while the register still carries non-markdown entries, which is the state this record exists to
make impossible to reach quietly.

**Not discharged by** widening `_ID_SCOPE_ROOTS` alone, and not by checks 30-39 passing: both are
true today of a scope that contains none of the 62.
