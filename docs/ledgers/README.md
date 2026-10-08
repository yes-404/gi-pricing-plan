---
family: reference
title: docs/ledgers — what execution actually did
status: active                  # active → retired (§1.2a)
created: 2026-09-17
owner: lead
corrected_by: []
relates: []                      # ids only
---

# docs/ledgers — what execution actually did

An `LG-` record is the execution ledger for one plan: task by task, what was done, what was
found, and what changed from the plan. Its `work:` names the work item it belongs to and,
where the ledger is slice-scoped, its `slice:` names the slice.

**No new `LG-` after Lean P2 L1.** For a slice dispatched after the maintainer's entry
"2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items 1, 3 and 5 APPROVED; IN PRACTICE NOW;
the files are amended through RFC 9479 P6 (the maintainer's amendment, by delegation)" in
`to-lead.md`, the ledger is the "Audit and ledger" section of the slice's `SL-` row in
`docs/roadmap.md` (`docs/_templates/SL.md`). The ledgers here stay as written. *(Amended 2026-10-08 by the maintainer (dated line by delegation), on RFC-9479 P6.)*

**A ledger is the counterpart to a plan, not a summary of it.** The plan
([`../plans/`](../plans/README.md)) says what was intended; the ledger says what happened,
including the parts that diverged. Neither is edited to agree with the other — that is the
same rule `CLAUDE.md` §0 applies to a spec and its code, and for the same reason.

[`../INDEX.md`](../INDEX.md) is the index.
