---
id: FD-9995
family: finding
title: A peril structure has no approval path and the compile resolver has no peril branch, so the day one is added an unapproved peril can be pinned
status: active
created: 2026-09-30
owner: auditor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
corrected_by: []
relates: [WK-1178, FR-237, FR-351, FR-386]
---

# FD-9995 — A peril structure has no approval path and the compile resolver has no peril branch

## Finding

**Severity: low**, on the maintainer's entry of 2026-09-30 11:25:33 BST, "#976's service-account item: LOW (recorded);
perils: LOW FD with a named owner and a tripwire" (`~/gi-pricing-plan.local/channel/to-lead.md`): fail-closed today, so
nothing prices wrongly. **A latent dependency, not a live defect.** Two facts hold at `9f63d0fe` and `65b33479`:

1. **Nothing writes `approved` for a peril structure.** `platform/perils.py` writes only `DRAFT` (`:124`),
   `RECONCILED` (`:256`) and `REVIEW` (`:338`) (re-read at `47d770e8`: unchanged); no other backend code sets `PerilStructureStatus.APPROVED`, and
   `api/approvals.py`'s `_carry_to_the_artifact` has no perils call. Yet **Peril Structure is a Governed Artifact**
   (`06-governance.md:64`).
2. **The compile resolver has no peril branch.** `_Resolver.resolve` in `backend/src/app/platform/rating_versions.py`
   (`:446`, re-pointed by symbol at `47d770e8`) handles rating_algorithm, model, rate_table, reference_table and custom_objective and then raises
   `NOT_FOUND` (the `raise PlatformError("NOT_FOUND", …)` ending the method, `:550-556`) "has no backend table yet (Phase 2); a compile cannot embed it." **That message is stale:** the table exists
   (`PerilStructureRow`, `backend/src/app/db/models.py:1618`); it should be corrected when the branch lands. So a rating version pinning
   `peril_structure:<slug>@<n>` in `pins.models` (`03-rating-engine.md:377-379`, the pins example) cannot compile, whatever the row's status.

The two facts cancel today, but the guard is thin. **Today the missing resolver branch keeps every peril pin out of a compiled
bundle.** When the resolver gains a `peril_structure` branch, `compile_bundle`'s maturity loop
(`pricing_core/rating/compile.py:622-630`, the `all_refs` loop in `compile_bundle`; `_MATURITY_CHECK_EXEMPT = frozenset({"rate_table", "rating_algorithm"})` at `:431`) requires
`approved`, `live` or `retired` (`_APPROVED_OR_BETTER`, `:404`) for a peril pin. With a planted resolver branch, `review` and `reconciled` rows then
fail `PIN_NOT_APPROVED` at that loop, and **only a forced `approved` row compiles** (auditor-close1255's live check of the
planted branch, which took the `approved` row from `NOT_FOUND` to success). So `NOT_FOUND` is not the only guard: the hazard is
the resolver branch **plus** an `approved` written by hand or by a path outside the workflow, and with no approval path the only
way to `approved` is such a write (the FD-1200 and validation-rule class). **Proposed by the auditor; the disposition is the
lead's.**

## Evidence

Measured by the auditor at `9f63d0fe` (a detached worktree, `uv sync --all-packages`, `alembic upgrade head` on a
scratch database made with `createdb -T`; the scratch test is deleted and the database dropped).

**Compile.** A temporary pytest inserted `PerilStructureRow`s directly with status `review`, `reconciled` and
`approved` (the last written straight into the database), pinned each as `peril_structure:ps@N` in `pins.models` of a
draft rating version over the minimal algorithm, and ran the compile route and job with `_run_compile_job` from
`backend/tests/test_rating_version_compile.py`. Output, verbatim:

```text
compile RV pinning peril_structure:ps@1 (row status=review) -> failed NOT_FOUND peril_structure:ps@1 has no backend table yet (Phase 2); a compile cannot embed it.
compile RV pinning peril_structure:ps@2 (row status=reconciled) -> failed NOT_FOUND peril_structure:ps@2 has no backend table yet (Phase 2); a compile cannot embed it.
compile RV pinning peril_structure:ps@3 (row status=approved) -> failed NOT_FOUND peril_structure:ps@3 has no backend table yet (Phase 2); a compile cannot embed it.
```

All three fail, including the forced `approved` row. No score was run: compile fails first.

**Maturity loop (read from source, not run).** `peril_structure` is not in `_MATURITY_CHECK_EXEMPT`
(`compile.py:431`); `_APPROVED_OR_BETTER = frozenset({"approved", "live", "retired"})` (`:404`). A resolver that
returned a peril would be refused with `PIN_NOT_APPROVED` unless its status was one of those.

**Writers of `approved`.** Predicates, at `9f63d0fe`:

- `git grep -n "PerilStructureStatus\.\(APPROVED\|SUPERSEDED\)" -- backend packages examples scripts` finds only
  `packages/model-schema/src/model_schema/perils.py:128-131`, `:421` (the transition table) and
  `packages/model-schema/tests/test_perils.py:409-410`. No backend writer.
- `git grep -n "peril" -- backend/src/app/api/approvals.py` finds `:48` (import), `:345` (a comment) and `:472`
  (the submit-time resolver `perils_service.resolve_artifact_ref`; **a reference check, not a carry**, as at the earlier tree). `_carry_to_the_artifact` (`approvals.py:512`) calls
  modelling, objectives, metrics and rating_versions only; the `:520` comment says a Peril Structure gains a lifecycle "with the slice that builds" it.
- `git grep -n "peril_structures" -- backend/alembic examples scripts`, filtered for `status`, `approved` or
  `insert`, finds nothing.
- The database `CHECK` (`backend/src/app/db/models.py:1671`, the `PerilStructureRow` status `CHECK`) allows `approved`, so a manual `UPDATE` can set it,
  as the test's direct insert did.

## Disposition

**Proposed disposition: carry forward with an owner.** Owner: **WK-1178**, on the maintainer's rule in the entry of
2026-09-30 11:25:33 BST ("If no P2 Work schedules it, the owner is WK-1178, with the trigger 'before any resolver
branch'"). The auditor checked `docs/roadmap.md` at `65b33479` (`grep -n -i peril docs/roadmap.md` finds lines `350`,
`410`, `412`, `496`, all Phase 1b closure text, and `:496` "Bandings, Peril Structure and reconciliation are recorded
as Phase 2"); no P2 Work row names a peril resolver or a peril approval path, so the owner is WK-1178, which confirms the maintainer's fallback. The lead, having checked the P2 roadmap, confirms that no
P2 Work schedules the peril resolver; if a later Work does, ownership moves to it.

**Acceptance is a tripwire test, red first on broken input.** The maintainer's entry of 2026-09-30 11:25:33 BST words it: a
tripwire test "that fails if `_Resolver` resolves peril_structure while `_carry_to_the_artifact` has no peril branch (or
perils.py has no approved writer on the decision path)". **The condition is a disjunction: the test fails when either half
is missing**, so a half-built state (a `_carry_to_the_artifact` peril branch and no writer of `approved`, or the reverse)
does not pass. *(The lead's brief to the auditor said "and"; the entry says "or", and the entry governs. Corrected on
auditor-close1255's audit of #980.)*

**The test is behavioural, not a source or AST scan** (a dispatch dictionary or an indirect call bypasses a scan): insert a
`PerilStructureRow` in each status (`review`, `reconciled`, `approved`), pin it in a rating version's `pins.models`, and assert
that compile stays refused for every one while no approval path exists. Red first: plant a `peril_structure` branch in
`_Resolver.resolve` with no approval path; auditor-close1255 verified that the `approved` row then goes from `NOT_FOUND` to a
successful compile, so the test goes red. It is the same family as #971's A.4 point: the set of tables with an approval-status
enum and their writers is derived, and `peril_structures` currently has zero writers of `approved`. The test names this
record so a later reader can find why it exists.

**Event that next confirms or discharges it:** WK-1178's tripwire test merges, red first. It is discharged in full when
a peril approval path and the resolver branch land together and the tripwire is replaced by a positive test that an
unapproved peril is refused at compile.

Ownership shape: event

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The maintainer's entry of
11:25:33 BST has already agreed a LOW FD, the owner rule and the tripwire acceptance.

*Disclosure: drafted under working id 9995; minted at the merge, when the id is re-read against `origin/main`.*

Amended 2026-10-05 before mint: the code cites above were re-pointed by symbol at `origin/main` `47d770e8` (`_MATURITY_CHECK_EXEMPT` was `:314`, now `compile.py:431`; `_APPROVED_OR_BETTER` `:287` → `:404`; the compile maturity loop `:466-480` → `:622-630`; `_Resolver.resolve` `:417` → `:446`; the stale "no backend table yet (Phase 2)" `NOT_FOUND` is still there at `rating_versions.py:550-556`; `PerilStructureRow` `:1577` → `:1618`; the approvals cites shifted by the lines above). Re-read and unchanged: `perils.py` writes only `DRAFT`/`RECONCILED`/`REVIEW` (`:124`, `:256`, `:338`); `api/approvals.py` has no peril branch in `_carry_to_the_artifact`; no tripwire test exists in `backend/tests` (`git grep -n -i peril -- backend/tests` filtered for "tripwire" or "resolver" is empty). The finding holds and is not covered by a later change.
