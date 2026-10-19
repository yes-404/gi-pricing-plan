---
id: RL-8132
family: ruling
title: PL-1766 D5.8 write set: deployment_switch.py replaces bundle_slot.py as the switch-core home (distinct concerns, verified bbc3f774)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-19   # filed 2026-10-19 under working id 8132
owner: decision-maker
tree: 1aab7a21fc5732ac6c0ea0c47d02ac4980638220
phase: P2
work: WK-674
slice: SL-1259
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1766, LG-1824, WK-674]
---

# RL-8132 — PL-1766 D5.8 write set: deployment_switch.py replaces bundle_slot.py as the switch-core home (distinct concerns, verified bbc3f774)

Filed 2026-10-19 under working id 8132 (a working id until a later seat mints it). The ruling is the maintainer's (by delegation). Its source is the entry "2026-10-19 04:43:27 BST" in `~/gi-pricing-plan.local/channel/to-lead.md`.

## How this was ruled

The source is the entry "2026-10-19 04:43:27 BST" in `~/gi-pricing-plan.local/channel/to-lead.md`. The file is local, so the whole entry is quoted below, copied from it by `sed`. The entry's Record section asks for this RL and its note that commit fae910ae's "D5.8" citation predates the ruling.

## Verified first, at 1aab7a21fc5732ac6c0ea0c47d02ac4980638220

- `docs/plans/PL-01766-*` line 236 begins "**D5.8 — the write set, re-derived.**"; the set lists `platform/bundle_slot.py` and ends "Fifteen paths in all"; lines 243-244 say any path outside it is a stop to the lead.
- `backend/src/app/platform/bundle_slot.py:99` reads `class BundleSlot:`; `backend/src/app/platform/deployment_switch.py:102` reads `class LiveRefs:`; `backend/src/app/main.py:145` reads `await score.hydrate_for_switch(database, blob_store, running.state.bundle_slot, message)`. These match the entry's claims at this tree (the entry verified them at bbc3f774).
- Commit fae910ae (author date 2026-10-18T22:09:04Z), subject "feat(platform): T1 — the two-phase deployment switch core and the per-process live ref (SL-1259; PL-1766 D5.6, D5.8, D5.9)", cites D5.8 and was written before this ruling (dated 2026-10-19 04:43:27 BST).

## Ruled

The maintainer's entry "2026-10-19 04:43:27 BST", verbatim:

> - **Verified at bbc3f774:**
>   - `platform/bundle_slot.py:99` `BundleSlot` is "a bounded, per-worker holding tier for hydrated bundles", the bundle CACHE.
>   - `platform/deployment_switch.py:102` `LiveRefs` is the per-(workspace, environment) pointer to the live deployment, plus the PREPARE/COMMIT protocol (:154-231).
>   - The switch hydrates INTO the slot (`main.py:145` `hydrate_for_switch(…, bundle_slot, …)`).
>   So the new module is a distinct concern and not a second live mechanism. Placing D5.6/D5.9's switch core and live ref there is the cleaner home.
> - **Ruled:**
>   - (1) `backend/src/app/platform/deployment_switch.py` is IN D5.8's write set, in place of `bundle_slot.py` for the switch core/live ref; bundle_slot.py stays the cache, untouched.
>   - (2) The four registration edits (model_schema/__init__.py +6, scripts/generate-contracts.py +6, scripts/audit-docs.py +4, tests/test_audit_docs_ids.py 7 lines) are IN, as mechanical consequences of D5.8's model-schema/contract entries and of my 02:45:42 ruling.
>   - (3) `docs/specs/06-governance.md` +2 is IN under my 23:22:15 ruling ("06 gets a pointer only"). Verify the +2 lines ARE only that pointer; anything more is a stop.
>   - (4) The auditor's reading is CONFIRMED: `backend/tests/*` = D5.8's "backend/tests/", and `docs/contracts/schemas/generated/*` = "the regenerated contract".
> - **Record:**
>   - LG 8127 cites this stamp at the walk;
>   - D26 carries an RL "PL-1766 D5.8 write set: deployment_switch.py replaces bundle_slot.py as the switch-core home (distinct concerns, verified bbc3f774)";
>   - the RL notes that commit fae910ae's "D5.8" citation predates this ruling. No amend.

Items (1) to (4) of "**Ruled:**" in the quote are the ruling. The entry's last bullet, quoted above, says: commit fae910ae's "D5.8" citation predates this ruling, and there is no amend. That is stated here and not repeated as a quotation of anything else.

## What it obliges

- `LG-1824` cites the stamp "2026-10-19 04:43:27 BST" at the audit walk.
- `PL-1766` is not edited; this record stands beside it.
- Commit fae910ae is not amended.

## Acceptance — the violation that must become detectable

This ruling answers a write-set scope question; no check can fail on a broken input. The violation to catch by reading: *Violation: a change to `backend/src/app/platform/bundle_slot.py` beyond what the cache already does, or a switch-core change outside `deployment_switch.py` and the four registration edits and the 06 pointer.* The audit walk of SL-1259's write set against this record's items (1) to (4) is the check.
