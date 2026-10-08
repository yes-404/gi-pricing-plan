---
id: FD-1491
family: finding
title: A bulk operation takes no change note and writes a machine-generated one, so FR-229's required change note is not the author's
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-673, FR-229, FR-233, FR-1186]
---

# FD-1491 — the bulk-operation route has no place for a change note

*Disclosure: drafted under working id 9700; minted as FD-1491 on 2026-10-08, in the T2 batch mint PR. Note: in the quoted channel entry, the working ids FD 9700 and FD 9699 stand as the channel wrote them (minted FD-1491 and FD-1490).*

**Filed** by auditor-gaps on the lead's order of 2026-10-05, from the exit-demo draft's gap row A6. `tree:` is `origin/main` at filing, and the reproduction ran at that tree.

## Finding

**Severity LOW, ruled; owner WK-673 (ruled 2026-10-05 15:15:21 BST by the maintainer (by delegation)); no deadline ruled.** Severity: the maintainer's (by delegation) entry "2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap findings" (`channel/to-lead.md`, local) says "FD 9700 (#1134) LOW and FD 9699 (#1135) LOW: as proposed." That entry names no owner and no deadline. The owner was then ruled at 2026-10-05 15:15:21 BST by the maintainer (by delegation): WK-673, because FR-229's required change note is `03`'s (`03-rating-engine.md:120`) and sits on WK-673's rate-table edit path (the earlier proposal was WK-1178). The claim as
drafted was "bulk takes no note". Verified, with one correction: a bulk operation does write a `change_note`, but the
caller cannot supply it. The service builds it from the operation's own name and parameters. A new version made by a
bulk uplift therefore records `uplift_table: percentage=0.10`, never why.

FR-229 (`docs/specs/03-rating-engine.md:120`): "Editing produces a new version with a required change note."
FR-1186 (`:128`) restates it: "FR-229's change note is still required on every version." The note is required and is
present on every row (`RateTableVersionRow.change_note` is `nullable=False`, `backend/src/app/db/models.py:2081`), so the column's rule holds.
The requirement's purpose, a human reason recorded with the edit, does not: seed (`SeedFromModelRequest._change_note_is_required`, `model_schema/rating.py:892`, which refuses an empty note) takes one; import writes `import: {filename}`
(`platform/rate_tables.py:456`); bulk writes a string it derives.

## Evidence

### 1. The route and the shapes carry no note

`POST /rate-tables/{slug}@{version}/bulk-operation` (`backend/src/app/api/rate_tables.py:112-156`, `bulk_operate_rate_table`) takes
`body: dict[str, Any]`, reads only `body.get("kind")` and `body.get("parameters")`, and passes neither a note nor
the rest of the body to `service.bulk_operation`. A `change_note` key beside `kind` is read by no line, so it is
dropped silently. Each operation's parameters model is `extra="forbid"` (`model_schema/rating.py`,
`UpliftTableParameters` and its siblings), so the key inside `parameters` is refused. The four pricing-core
operations that build a version (`return _new_version(` in `rate_tables/operations.py`) take no note argument: `uplift_table(table, *, percentage)`.

### 2. Reproduction, at `caa4e411a9c07a389cf47092a923c7761b2b92dc`, through the service seam with no database

```python
import sys, inspect
sys.path.insert(0,"packages/pricing-core/tests")
from decimal import Decimal
from test_rate_table_bulk_ops import _version
from pricing_core.rate_tables import operations as ops
print("uplift_table signature:", inspect.signature(ops.uplift_table))
print("baseline note:", _version().change_note)
d = ops.uplift_table(_version(), percentage=Decimal("0.10"))
print("derived note :", d.change_note)
from app.platform.rate_tables import _dispatch_operation
d2 = _dispatch_operation("uplift_table", {"percentage":"0.10","change_note":"Q4 rate review, approved by CFO"}, _version())
```

Output (`uv run python`, 2026-10-05):

```
uplift_table signature: (table: 'RateTableVersion', *, percentage: 'Decimal') -> 'RateTableVersion'
baseline note: baseline version
derived note : uplift_table: percentage=0.10
pydantic_core._pydantic_core.ValidationError: 1 validation error for UpliftTableParameters
change_note
  Extra inputs are not permitted [type=extra_forbidden, input_value='Q4 rate review, approved by CFO', input_type=str]
```

`_dispatch_operation` is the function the route's service calls; the last statement raises, so the caller has no
way to attach a reason. The HTTP route was not run: the test database does not exist in this worktree.

## Disposition

Open. Filed by the auditor, 2026-10-05; severity is the maintainer's (by delegation) (13:20:26 BST entry above), the owner is WK-673 (ruled 2026-10-05 15:15:21 BST by the maintainer (by delegation)), and the verdict is the lead's.

Two readings of FR-229 are possible, and choosing between them is the spec's, not this record's: (a) the note must be
the author's words on every path, so bulk gains a required `change_note` and the derived string becomes a prefix or is
dropped; (b) a derived note is enough where the operation's parameters are the whole reason, which FR-229 would then
say. Today the spec says (a) and the code does (b), without a ruling. Red first: a bulk call with no author note is
refused, and a call with one records it.
