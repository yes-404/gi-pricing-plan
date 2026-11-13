"""WK-2113 S3: `hydrate` is the one hydration point for a stored Bundle (FD-1495 B1).

No database: the audit write is captured, so these run in the small lane. Pins, in order:

* a refused load is a 409 problem with the named code (DP-2), never a raw `CodedError`;
* ONE Audit Event per process per hash (DP-1), written in its own `unit_of_work`, while every
  request is still refused: the refused-hash memo de-duplicates the event and decides nothing;
* the refused hash is not left in the slot, and `_compiled_for`'s "store down" degradation
  cannot serve it (a HELD refused bundle is planted);
* the census: `hydrate` is the only caller of `load_bundle` and `_fetch_bundle` the only
  `slot.put` caller under `backend/src` (instrument proven by a planted second caller).
"""

from __future__ import annotations

import ast
import shutil
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from app.api import score
from app.errors import PlatformError
from app.platform import bundle_hydration
from app.platform.bundle_hydration import REFUSAL_ACTION, hydrate
from app.platform.bundle_slot import BundleSlot
from model_schema import ArtifactRef
from pricing_core.rating.compile import Bundle
from pricing_core.rating.runtime import load_bundle

FIXTURES = Path(__file__).parent / "fixtures" / "stored_bundles"
SRC = Path(__file__).resolve().parents[1] / "src"
CODE = "CONTROL_FACTOR_IN_RATEABLE_PATH"
REF = ArtifactRef(type="rating_version", slug="rv-offender", version=1)


def _bundle(name: str) -> Bundle:
    return Bundle.model_validate_json((FIXTURES / name).read_text())


class _FakeDatabase:
    """Only `unit_of_work` is used by `hydrate`; each entry is one transaction."""

    def __init__(self) -> None:
        self.transactions = 0

    @asynccontextmanager
    async def unit_of_work(self) -> AsyncIterator[object]:
        self.transactions += 1
        yield object()


@pytest.fixture
def events(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    recorded: list[dict[str, Any]] = []

    async def record(_session: object, **fields: Any) -> None:
        recorded.append(fields)

    monkeypatch.setattr(bundle_hydration.audit, "record", record)
    return recorded


async def _refused(slot: BundleSlot, database: _FakeDatabase, name: str = "offender.bundle.json"):
    with pytest.raises(PlatformError) as refused:
        await hydrate(
            _bundle(name),
            slot=slot,
            database=database,  # type: ignore[arg-type]
            workspace_id=uuid4(),
            ref=REF,
        )
    return refused.value


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-243")
@pytest.mark.asyncio
async def test_a_refused_load_is_a_409_problem_with_the_code_and_one_audit_event(
    events: list[dict[str, Any]],
) -> None:
    database = _FakeDatabase()
    error = await _refused(BundleSlot(), database)
    assert (error.code, error.status_code) == (CODE, 409)
    detail = str(error)
    for needle in (str(REF), "yoa", "region_x_yoa"):
        assert needle in detail
    assert _bundle("offender.bundle.json").content_hash in detail
    assert len(events) == 1
    assert database.transactions == 1
    event = events[0]
    assert event["action"] == REFUSAL_ACTION
    assert event["entity_ref"] == str(REF)
    assert event["before"] is None
    assert "yoa" in event["after"]["refusal"]
    assert event["after"]["note"] == "first refusal in this worker"


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
async def test_a_repeat_is_refused_again_but_audited_once_per_process(
    events: list[dict[str, Any]],
) -> None:
    slot, database = BundleSlot(), _FakeDatabase()
    first = await _refused(slot, database)
    second = await _refused(slot, database)
    assert (second.code, second.status_code) == (first.code, first.status_code)
    assert len(events) == 1, "DP-1: one event per process per hash"
    # A different process (a fresh slot) audits it again.
    await _refused(BundleSlot(), database)
    assert len(events) == 2


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
async def test_the_memo_never_makes_a_hash_clean(events: list[dict[str, Any]]) -> None:
    """A hash covers the pins, not the carried payloads: the clean twin shares the offender's
    hash, and having refused the one must not excuse (or refuse) the other without the guard."""
    slot, database = BundleSlot(), _FakeDatabase()
    await _refused(slot, database)
    clean = _bundle("clean.bundle.json")
    assert clean.content_hash == _bundle("offender.bundle.json").content_hash
    compiled = await hydrate(
        clean,
        slot=slot,
        database=database,  # type: ignore[arg-type]
        workspace_id=uuid4(),
        ref=REF,
    )
    assert compiled.content_hash == clean.content_hash
    assert len(events) == 1


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
async def test_an_audit_write_that_fails_is_retried_not_swallowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def broken(_session: object, **_fields: Any) -> None:
        raise RuntimeError("audit store down")

    monkeypatch.setattr(bundle_hydration.audit, "record", broken)
    slot, database = BundleSlot(), _FakeDatabase()
    with pytest.raises(RuntimeError, match="audit store down"):
        await _refused(slot, database)
    assert slot.first_refusal(_bundle("offender.bundle.json").content_hash) is True


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("NFR-497")
@pytest.mark.asyncio
async def test_a_held_refused_bundle_is_evicted_and_not_served_when_the_store_is_down(
    events: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Condition (3), finding (1): `_compiled_for` serves the slot's held bundle when the
    metadata store fails with a raw exception. A refused hash must not be in the slot to serve."""
    slot, database = BundleSlot(), _FakeDatabase()
    offender = _bundle("offender.bundle.json")
    held = load_bundle(_bundle("clean.bundle.json"))  # same hash: a pre-guard hold, planted
    slot.put(REF, held)
    assert slot.hash_for(REF) == offender.content_hash

    await _refused(slot, database)  # the refusal evicts the hash and its ref memo
    assert slot.get(offender.content_hash) is None
    assert slot.hash_for(REF) is None

    async def store_down(*_a: Any, **_k: Any) -> Any:
        raise ConnectionError("metadata store down")

    monkeypatch.setattr(score, "_fetch_bundle", store_down)
    with pytest.raises(ConnectionError):
        await score._compiled_for(
            database,
            None,
            slot,
            database=database,  # type: ignore[arg-type]
            workspace_id=uuid4(),
            ref=REF,
        )


# --------------------------------------------------------------------------------------
# The census (condition 3(i)): by AST, over backend/src.
# --------------------------------------------------------------------------------------


def _callers(root: Path, name: str, receiver: str | None) -> list[tuple[str, str]]:
    """(file, enclosing function) of every call of `name` (bare, or `<receiver>.name`)."""
    found: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text())

        def visit(node: ast.AST, function: str, path: Path = path) -> None:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                function = node.name
            if isinstance(node, ast.Call):
                target = node.func
                if receiver is None and isinstance(target, ast.Name) and target.id == name:
                    found.append((str(path.relative_to(root)), function))
                if (
                    receiver is not None
                    and isinstance(target, ast.Attribute)
                    and target.attr == name
                    and isinstance(target.value, ast.Name)
                    and target.value.id == receiver
                ):
                    found.append((str(path.relative_to(root)), function))
            for child in ast.iter_child_nodes(node):
                visit(child, function, path)

        visit(tree, "<module>")
    return found


@pytest.mark.req("FR-243")
def test_hydrate_is_the_only_caller_of_load_bundle_and_fetch_bundle_the_only_slot_put() -> None:
    assert _callers(SRC, "load_bundle", None) == [("app/platform/bundle_hydration.py", "hydrate")]
    # Two sites, both in `_fetch_bundle`: the slot-hit memo refresh and the post-hydrate put.
    assert _callers(SRC, "put", "slot") == [("app/api/score.py", "_fetch_bundle")] * 2


@pytest.mark.req("FR-243")
def test_the_census_sees_a_planted_second_caller(tmp_path: Path) -> None:
    """Instrument proof: a scratch copy with one planted `load_bundle(` and one `slot.put(`."""
    copy = tmp_path / "src"
    shutil.copytree(SRC, copy, ignore=shutil.ignore_patterns("__pycache__"))
    (copy / "app" / "planted.py").write_text(
        "def sneaky(bundle, slot, ref):\n"
        "    compiled = load_bundle(bundle)\n"
        "    slot.put(ref, compiled)\n"
    )
    assert ("app/planted.py", "sneaky") in _callers(copy, "load_bundle", None)
    assert ("app/planted.py", "sneaky") in _callers(copy, "put", "slot")


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("NFR-498")
@pytest.mark.asyncio
async def test_a_governance_refusal_is_never_deduplicated_and_names_the_acting_principal(
    events: list[dict[str, Any]],
) -> None:
    """Amendment 3 (b) without a database: a refused deploy, a refused score, a second refused
    deploy, a repeated score = three events, the two deploys as the acting principal."""
    from model_schema import ActorKind, Principal

    slot, database = BundleSlot(), _FakeDatabase()
    actor = Principal(kind=ActorKind.USER, id=uuid4(), display="deployer")
    requester = Principal(kind=ActorKind.USER, id=uuid4(), display="scorer")

    async def refuse(**extra: Any) -> None:
        with pytest.raises(PlatformError):
            await hydrate(
                _bundle("offender.bundle.json"),
                slot=slot,
                database=database,  # type: ignore[arg-type]
                workspace_id=uuid4(),
                ref=REF,
                **extra,
            )

    await refuse(acting=actor)
    await refuse(requester=requester)
    await refuse(acting=actor)
    await refuse(requester=requester)
    assert len(events) == 3
    assert [e["actor"].id for e in events if e["actor"] is actor] == [actor.id, actor.id]
    scored = [e for e in events if e["actor"] is not actor]
    assert scored[0]["after"]["requested_by"] == str(requester.id)
    assert "requested_by" not in events[0]["after"]
