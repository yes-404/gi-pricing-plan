---
family: reference
title: docs/ledgers — what execution actually did
status: active                  # active → retired (§1.2a)
created: 2026-09-06
owner: lead
corrected_by: []
relates: []                      # ids only
---

# docs/ledgers — what execution actually did

An `LG-` record is the execution ledger for one plan: task by task, what was done, what was
found, and what changed from the plan. Its `work:` names the work item it belongs to and,
where the ledger is slice-scoped, its `slice:` names the slice.

**A ledger is the counterpart to a plan, not a summary of it.** The plan
([`../plans/`](../plans/README.md)) says what was intended; the ledger says what happened,
including the parts that diverged. Neither is edited to agree with the other — that is the
same rule `CLAUDE.md` §0 applies to a spec and its code, and for the same reason.

[`../INDEX.md`](../INDEX.md) is the index.
