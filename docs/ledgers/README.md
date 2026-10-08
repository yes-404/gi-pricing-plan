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

**From Lean P2 L1 (a'), a slice's `LG-` is its one paperwork file.** For a slice dispatched after
the maintainer's entry "2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items 1, 3 and 5
APPROVED; IN PRACTICE NOW; the files are amended through RFC 9479 P6 (the maintainer's amendment,
by delegation)" in `to-lead.md`, its ledger here has five sections — Scope (quoting its Work-plan
row), Task list, Gate, Audit, Build log — quotes the GO and MERGE-ACK headers, and lands in the
slice's one PR with no per-slice plan (`docs/_templates/LG.md`). (L1 as corrected to (a') by the maintainer's entry "2026-10-08 12:02:08 BST — #1240 P6 flagged readings RULED: (1) REJECTED, and my 11:51:58 L1 (a) wording CORRECTED (the slice's one file is its LG-, not text under the roadmap row); (2) ACCEPTED".) The ledgers here
already stay as written. *(Amended 2026-10-08 by the maintainer (dated line by delegation), on RFC-9479 P6.)*

**A ledger is the counterpart to a plan, not a summary of it.** The plan
([`../plans/`](../plans/README.md)) says what was intended; the ledger says what happened,
including the parts that diverged. Neither is edited to agree with the other — that is the
same rule `CLAUDE.md` §0 applies to a spec and its code, and for the same reason.

[`../INDEX.md`](../INDEX.md) is the index.
