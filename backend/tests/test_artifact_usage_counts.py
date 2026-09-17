"""FR-167: the per-page usage aggregate behind each library row's `usage_count`.

The library rows count Model Specs; `objectives.usage` and `metrics.usage` answer the same
question for one artifact. These tests pin the three things that make the aggregate usable
as a row value: the shape (a count per ref, an unused ref absent rather than zero), the
JSONB reading on each side (a top-level scalar for objectives, an array for metrics), and
the **budget** — one statement per page, which FR-167 makes part of the requirement
rather than an implementation note.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from backend.tests.test_custom_objectives import _objective
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_jobs_gbm import _gbm_spec
from sqlalchemy import event

from app.db.models import ModelRow
from app.db.session import Database
from app.platform import metrics, objectives
from model_schema import (
    GbmFunctionRef,
    GlmSpec,
    OffsetSpec,
    Principal,
    new_uuid7,
)


def _objective_spec(ref: str) -> dict[str, object]:
    """A GBM spec naming `ref` as its objective, built through `model-schema` (§2)."""
    return _gbm_spec(
        new_uuid7(),
        (new_uuid7(),),
        objective=GbmFunctionRef(kind="custom", ref=ref),
    ).model_dump(mode="json")


def _metric_spec(refs: tuple[str, ...]) -> dict[str, object]:
    """A GBM spec whose `eval_metrics` array names each of `refs`."""
    return _gbm_spec(
        new_uuid7(),
        (new_uuid7(),),
        eval_metrics=tuple(GbmFunctionRef(kind="custom", ref=ref) for ref in refs),
    ).model_dump(mode="json")


def _glm_spec() -> dict[str, object]:
    """A GLM spec, which carries **no `eval_metrics` key at all**.

    `eval_metrics` is declared on `GbmSpec` only, so the metric aggregate's lateral
    expansion meets a missing key on every workspace holding a GLM. A GBM with an empty
    array would not exercise it — `()` serialises to `[]`, which expands to nothing.
    """
    return GlmSpec(
        model_family_slug=f"glm-{new_uuid7().hex[-6:]}",
        dataset_version_id=new_uuid7(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
    ).model_dump(mode="json")


async def _model(
    database: Database,
    workspace_id: UUID,
    spec: dict[str, object],
    *,
    status: str = "draft",
) -> UUID:
    """Insert one Model row carrying `spec`. No fit: the aggregate reads the spec column.

    `ck_models_fitted_model_has_a_fit_result` and its diagnostics twin let `draft` and
    `archived` stand alone; anything further along carries both, so they are supplied.
    """
    beyond_draft = status not in ("draft", "archived")
    async with database.unit_of_work() as session:
        row = ModelRow(
            workspace_id=workspace_id,
            model_family_slug=str(spec["model_family_slug"]),
            version=1,
            status=status,
            dataset_version_id=UUID(str(spec["dataset_version_id"])),
            spec=spec,
            spec_hash=f"v3:sha256:{new_uuid7().hex}{new_uuid7().hex}",
            fit_result={"fitted": True} if beyond_draft else None,
            diagnostics_id=new_uuid7() if beyond_draft else None,
        )
        session.add(row)
        await session.flush()
        return row.id


@pytest.mark.req("FR-167")
async def test_objective_usage_counts_are_returned_per_ref(
    database: Database, workspace_id: UUID
) -> None:
    """One call, several refs, a count each — the shape a page needs.

    Two objective refs, one used by two models and one by none, plus a model in another
    workspace naming the used ref so the scoping is exercised rather than assumed.
    """
    used = f"custom_objective:used-{new_uuid7().hex[-6:]}@1"
    unused = f"custom_objective:unused-{new_uuid7().hex[-6:]}@1"
    other_workspace = new_uuid7()

    await _model(database, workspace_id, _objective_spec(used))
    await _model(database, workspace_id, _objective_spec(used))
    await _model(database, other_workspace, _objective_spec(used))

    async with database.session() as session:
        counts = await objectives.usage_counts(
            session, workspace_id=workspace_id, refs=[used, unused]
        )

    assert counts[used] == 2, "the other workspace's model is not this workspace's count"
    assert unused not in counts, "an unused ref is absent, not zero — the caller supplies zero"


@pytest.mark.req("FR-167")
async def test_metric_usage_counts_expand_the_eval_metrics_array(
    database: Database, workspace_id: UUID
) -> None:
    """`eval_metrics` is a JSONB **array**, so a model may reference several metrics.

    The objective side reads one scalar; this side must count a model once per metric it
    names, and must not miss a metric that is second in the array.

    The GLM row carries no `eval_metrics` key at all — the field is on `GbmSpec` only — and
    is here as a regression guard on the lateral expansion meeting one. It is honest to say
    that no mutation of the implementation makes *this row alone* fail: `jsonb_array_elements`
    is strict, so a missing key expands to nothing rather than raising, and the row simply
    drops out of the join. The plan for this slice asserted the opposite and was wrong; the
    row stays because the shape it exercises is real, not because it bites.
    """
    first = f"custom_metric:first-{new_uuid7().hex[-6:]}@1"
    second = f"custom_metric:second-{new_uuid7().hex[-6:]}@1"

    await _model(database, workspace_id, _metric_spec((first, second)))
    await _model(database, workspace_id, _metric_spec((second,)))
    await _model(database, workspace_id, _glm_spec())

    async with database.session() as session:
        counts = await metrics.usage_counts(
            session, workspace_id=workspace_id, refs=[first, second]
        )

    assert counts == {first: 1, second: 2}


@pytest.mark.req("FR-167")
async def test_a_count_matches_the_detail_route_blast_radius(
    database: Database, workspace_id: UUID
) -> None:
    """The row and the detail route must not disagree about the same artifact.

    A row saying 3 beside a `/usage` page listing 5 is the kind of inconsistency an actuary
    reports as a data bug and an auditor reports as something worse. Note the models here
    are `draft`, `fitted` and `archived`: `usage` applies no status filter, so neither may
    the aggregate.
    """
    actor: Principal = await _actuary(database, workspace_id)
    row = await _objective(database, workspace_id, actor)
    ref = f"custom_objective:{row.slug}@{row.version}"

    for status in ("draft", "fitted", "archived"):
        await _model(database, workspace_id, _objective_spec(ref), status=status)

    async with database.session() as session:
        counts = await objectives.usage_counts(
            session, workspace_id=workspace_id, refs=[ref]
        )
        blast = await objectives.usage(
            session, workspace_id=workspace_id, actor=actor, objective_id=row.id
        )

    assert counts[ref] == len(blast.models) == 3


@pytest.mark.req("FR-167")
async def test_one_page_of_refs_costs_one_query(
    database: Database, workspace_id: UUID
) -> None:
    """**The budget is the requirement.** One aggregate per page, never one per row.

    Asserted with a counter because an N+1 implementation returns identical results and
    would stay correct-looking until a workspace held a few hundred artifacts — the exact
    failure FR-167 says it is stating the budget to prevent.
    """
    refs = [f"custom_objective:page-{n}-{new_uuid7().hex[-6:]}@1" for n in range(25)]
    await _model(database, workspace_id, _objective_spec(refs[0]))

    statements: list[str] = []
    engine = database.engine.sync_engine

    def _record(conn, cursor, statement, parameters, context, executemany) -> None:
        statements.append(statement)

    async with database.session() as session:
        event.listen(engine, "before_cursor_execute", _record)
        try:
            counts = await objectives.usage_counts(
                session, workspace_id=workspace_id, refs=refs
            )
        finally:
            event.remove(engine, "before_cursor_execute", _record)

    assert counts == {refs[0]: 1}
    assert len(statements) == 1, f"{len(statements)} statements for 25 refs:\n" + "\n".join(
        statements
    )


@pytest.mark.req("FR-167")
async def test_an_empty_page_asks_the_database_nothing(
    database: Database, workspace_id: UUID
) -> None:
    """A page with no rows is a real case — the first screen of an empty workspace.

    Counted rather than merely asserted empty: `IN ()` returns nothing anyway, so `== {}`
    alone would pass with the guard deleted and prove nothing about the round trip.
    """
    statements: list[str] = []
    engine = database.engine.sync_engine

    def _record(conn, cursor, statement, parameters, context, executemany) -> None:
        statements.append(statement)

    async with database.session() as session:
        event.listen(engine, "before_cursor_execute", _record)
        try:
            assert (
                await objectives.usage_counts(session, workspace_id=workspace_id, refs=[]) == {}
            )
            assert await metrics.usage_counts(session, workspace_id=workspace_id, refs=[]) == {}
        finally:
            event.remove(engine, "before_cursor_execute", _record)

    assert statements == [], f"an empty page cost {len(statements)} statements"
