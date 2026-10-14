---
id: FD-8006
family: finding
title: The job-events stream's data payload is a dict built in the handler that no model-schema model owns
status: active
created: 2026-10-14
owner: auditor
tree: 36e2610ab8135bc3b3563464e7f5f719713b168b
corrected_by: []
relates: [FD-1684, PL-9997, SL-9998, WK-1178]
---

# FD-8006 — The job-events stream's `data` payload is a dict built in the handler that no `model-schema` model owns

*(Filed under working id 8006, reserved by the lead, eta "2026-10-14 09:52:44 BST". Text drafted by
the minter (seat minter-d15) on the maintainer's (by delegation) ruling below. The finding's owner
field is the family default; the finding's owning Work is `WK-1178`.)*

## Finding

**Severity: LOW** (the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A), last bullet, in
`~/gi-pricing-plan.local/channel/to-lead.md`): *"The LOW finding (the SSE event `data` dict at
jobs.py:288-295 has no model-schema owner): file it in the next batch, owner WK-1178, P2 backlog."*

`GET /api/v1/jobs/{job_id}/events` builds each event's `data` as a dict literal in the handler:
`id`, `status`, `progress`, `trace_id`. No `model-schema` model owns that shape. `CLAUDE.md` §2 says
*"Nobody hand-writes a shape that already exists in `model-schema`"*, and the same rule is the
reason a shape defined only in a handler cannot be generated into `docs/contracts/` or the
frontend client: the frontend cannot type it from the contract. `model-schema` does own the job
(`Job`, `packages/model-schema/src/model_schema/jobs.py:218`, with `id`, `status`, `progress` and
`trace_id` among its fields); the event payload is a four-field projection of it that nothing
names. It is LOW because the wire works and no source caller reads the stream today (`PL-9997`
premise n). It becomes a real divergence risk the first time a client parses the event.

`PL-9997` DP-4 (i), ruled by the same entry, declares the route's media type `text/event-stream`
with the handler unchanged. That does not type the payload, and the plan's Hand-off raised the
question and did not decide it.

## Evidence

At `origin/main` `36e2610ab8135bc3b3563464e7f5f719713b168b`, `backend/src/app/api/jobs.py`:

```text
288            payload = json.dumps(
289                {
290                    "id": str(row.id),
291                    "status": row.status.value,
292                    "progress": row.progress,
293                    "trace_id": row.trace_id,
294                }
295            )
```

Read with `git show origin/main:backend/src/app/api/jobs.py | sed -n '288,295p'`. The event is
sent at `yield f"event: progress\ndata: {payload}\n\n"` in the same loop.

## Disposition

`fix before close with an owner: WK-1178` (P2 backlog, per the maintainer's ruling): a
`model-schema` model for the event payload (or a ruled decision that the stream stays untyped), so
the handler builds it from the model. The remedy's shape is a design choice and is the owning
Work's planner's to put as a decision point; nothing here picks it. Event that next confirms or
discharges it: `jobs.py`'s event `data` being produced by a `model-schema` model, or a ruling
that records why not.
