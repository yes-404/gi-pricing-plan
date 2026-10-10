"""The approval guard's declarations (WK-674 Slice 2a, PL-1303 Acceptance 1, RL-1301 A.4.1).

Every mapped `status` column declares itself: its vocabulary `StrEnum`
(`info={"status_vocabulary": ...}`) or the explicit non-approval marker
(`info={"approval_capable": False}`). The guarded set is derived from those declarations,
and four independent cross-checks refuse a wrong marker, each read from the models and the
code rather than from a list.
"""

from __future__ import annotations

import ast
import enum
import re
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import CheckConstraint, Column, Enum, Integer, MetaData, String, Table

from app.db import models
from app.db.base import Base
from app.db.models import approval_guarded_tables

_PLATFORM = Path(__file__).resolve().parents[1] / "src" / "app" / "platform"

#: The derived set at the tree PL-1303 was written against, re-derived at 22fe674b, plus
#: `deployment_requests`, which WK-674 Slice 2 (PL-1392 Acceptance 13) adds.
EXPECTED_GUARDED = {
    "approval_requests",
    "custom_metrics",
    "custom_objectives",
    "deployment_requests",
    "models",
    "peril_structures",
    "rating_versions",
    "validation_rule_sets",
    "validation_rules",
}


def _status_columns(metadata: MetaData) -> list[tuple[Table, Column[Any]]]:
    return [(t, t.c["status"]) for t in metadata.tables.values() if "status" in t.c]


def _status_check_texts(table: Table) -> list[str]:
    """The SQL text of every CHECK that constrains `status`."""
    return [
        str(c.sqltext)
        for c in table.constraints
        if isinstance(c, CheckConstraint) and re.search(r"\bstatus\b", str(c.sqltext))
    ]


def _check_enumerates_approved(text: str) -> bool:
    """The fourth leg: `status IN (...)` or `status = ANY (ARRAY[...])` naming 'approved'.

    An implication (`status <> 'x' OR ...`), an inequality or any other predicate does not
    count: `dataset_versions`' CHECK is satisfied by 'approved' without naming it.
    """
    for m in re.finditer(r"\bstatus\s+IN\s*\(([^)]*)\)", text, flags=re.IGNORECASE):
        if "'approved'" in m.group(1):
            return True
    for m in re.finditer(r"\bstatus\s*=\s*ANY\s*\(\s*ARRAY\[([^\]]*)\]", text, flags=re.IGNORECASE):
        if "'approved'" in m.group(1):
            return True
    return False


def _enum_with_approved(col: Column[Any]) -> bool:
    enum_class = getattr(col.type, "enum_class", None)
    return isinstance(col.type, Enum) and enum_class is not None and hasattr(enum_class, "APPROVED")


def _default_is_approved(col: Column[Any]) -> bool:
    default = getattr(col.default, "arg", None)
    server = getattr(col.server_default, "arg", None)
    return default == "approved" or str(server).strip("'\"") == "approved"


def _tables_written_by_the_carry() -> set[str]:
    """Tables whose row an `apply_approval_decision` moves (RL-1301 A.4.1, third leg).

    Derived from the code: in each platform module that defines `apply_approval_decision`,
    the variable that gets `.status = …` is bound by a `select(<Row>)`; that Row's table is
    written by the carry. `ApprovalRequestRow` is named by the request parameter and never
    bound this way.
    """
    rows = {m.class_.__name__: m.local_table.name for m in Base.registry.mappers}
    out: set[str] = set()
    for path in sorted(_PLATFORM.glob("*.py")):
        tree = ast.parse(path.read_text())
        fns = {
            n.name: n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        start = fns.get("apply_approval_decision")
        if start is None:
            continue
        reachable, todo = {start.name: start}, [start]
        while todo:
            for n in ast.walk(todo.pop()):
                if isinstance(n, ast.Name) and n.id in fns and n.id not in reachable:
                    reachable[n.id] = fns[n.id]
                    todo.append(fns[n.id])
        for fn in reachable.values():
            assigned = {
                t.value.id
                for n in ast.walk(fn)
                if isinstance(n, ast.Assign)
                for t in n.targets
                if isinstance(t, ast.Attribute)
                and t.attr == "status"
                and isinstance(t.value, ast.Name)
            }
            for n in ast.walk(fn):
                if not (isinstance(n, ast.Assign) and len(n.targets) == 1):
                    continue
                target = n.targets[0]
                if not (isinstance(target, ast.Name) and target.id in assigned):
                    continue
                for call in ast.walk(n.value):
                    if (
                        isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Name)
                        and call.func.id == "select"
                        and call.args
                        and isinstance(call.args[0], ast.Name)
                        and call.args[0].id in rows
                    ):
                        out.add(rows[call.args[0].id])
    return out


def _declaration_failures(metadata: MetaData, carried: set[str]) -> list[str]:
    """Every way a `status` column fails to declare itself correctly; empty when sound."""
    failures: list[str] = []
    for table, col in _status_columns(metadata):
        name = f"{table.name}.status"
        vocab = col.info.get("status_vocabulary")
        marker = col.info.get("approval_capable")
        if vocab is None and marker is None:
            failures.append(f"{name}: declares neither a vocabulary nor the non-approval marker")
            continue
        if vocab is not None and marker is not None:
            failures.append(f"{name}: declares both a vocabulary and the marker")
            continue
        if vocab is not None:
            if not (isinstance(vocab, type) and issubclass(vocab, enum.StrEnum)):
                failures.append(f"{name}: status_vocabulary is not a StrEnum")
            continue
        if marker is not False:
            failures.append(f"{name}: approval_capable may only be False")
            continue
        reasons = []
        checks = _status_check_texts(table)
        if any("'approved'" in c for c in checks):
            reasons.append("its CHECK names 'approved'")
        if _default_is_approved(col):
            reasons.append("its default is 'approved'")
        if table.name in carried or table.name == "approval_requests":
            reasons.append("the approval carry writes its table")
        if _enum_with_approved(col):
            reasons.append("it is Enum-typed with an APPROVED member")
        if any(_check_enumerates_approved(c) for c in checks):
            reasons.append("a CHECK enumerates its vocabulary including 'approved'")
        if reasons:
            failures.append(f"{name}: carries the non-approval marker but " + "; ".join(reasons))
    return failures


def _vocabulary_with_approved(metadata: MetaData) -> set[str]:
    return {
        t.name
        for t, c in _status_columns(metadata)
        if hasattr(c.info.get("status_vocabulary"), "APPROVED")
    }


# -- the real models ------------------------------------------------------------------


@pytest.mark.req("FR-351")
def test_every_mapped_status_column_declares_itself() -> None:
    """No `status` column escapes by omission, and none carries a wrong marker."""
    assert _status_columns(Base.metadata), "no status columns found: the walker is blind"
    assert _declaration_failures(Base.metadata, _tables_written_by_the_carry()) == []


@pytest.mark.req("FR-351")
def test_the_guarded_set_is_derived_from_the_declarations() -> None:
    derived = _vocabulary_with_approved(Base.metadata)
    assert derived == EXPECTED_GUARDED
    assert approval_guarded_tables() == EXPECTED_GUARDED
    assert len(derived) == 9


@pytest.mark.req("FR-351")
def test_the_carry_walker_reaches_the_five_artifact_tables() -> None:
    """A walker that stopped descending would make the third leg vacuous. `deployment_requests`
    joined the four with WK-674 Slice 2's deployment branch of the carry (`PL-1392` Task 5);
    `validation_rules` joined them with the validation-rule branch (`PL-1408` Task 3, FD-1356);
    `peril_structures` joined them with the Peril Structure branch (`PL-1461` Task 3, FD-1456).
    The set is exact, so it fails both for a carried kind it omits and for a listed kind the
    carry no longer writes."""
    assert _tables_written_by_the_carry() == {
        "models",
        "custom_objectives",
        "custom_metrics",
        "rating_versions",
        "deployment_requests",
        "validation_rules",
        "peril_structures",
    }


@pytest.mark.req("FR-351")
def test_validation_tables_declare_their_constants_as_an_enum() -> None:
    from app.platform import validation_rules as vr

    vocab = models.ValidationRuleStatus
    assert {vocab.DRAFT, vocab.REVIEW, vocab.APPROVED} == set(vocab)
    assert (vr.DRAFT, vr.REVIEW, vr.APPROVED) == ("draft", "review", "approved")


# -- planted cases: red on broken input -----------------------------------------------


def _scratch(*columns: Column[Any], checks: tuple[str, ...] = ()) -> MetaData:
    md = MetaData()
    Table(
        "planted",
        md,
        Column("id", Integer, primary_key=True),
        *columns,
        *[CheckConstraint(c) for c in checks],
    )
    return md


def test_a_planted_status_column_with_neither_declaration_fails() -> None:
    md = _scratch(Column("status", String(16)))
    failures = _declaration_failures(md, set())
    assert len(failures) == 1
    assert "neither" in failures[0]


def test_a_planted_marker_on_a_column_whose_check_names_approved_fails() -> None:
    md = _scratch(
        Column("status", String(16), info={"approval_capable": False}),
        checks=("status IN ('draft', 'approved')",),
    )
    failures = _declaration_failures(md, set())
    assert any("CHECK names 'approved'" in f for f in failures)
    assert any("enumerates its vocabulary" in f for f in failures)


def test_a_planted_marker_on_an_approved_default_fails() -> None:
    md = _scratch(
        Column("status", String(16), default="approved", info={"approval_capable": False})
    )
    assert any("default" in f for f in _declaration_failures(md, set()))


def test_a_planted_marker_on_a_table_the_carry_writes_fails() -> None:
    md = _scratch(Column("status", String(16), info={"approval_capable": False}))
    assert any("carry" in f for f in _declaration_failures(md, {"planted"}))


class _Vocab(enum.StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"


def test_a_planted_marker_on_an_enum_with_approved_fails() -> None:
    md = _scratch(
        Column("status", Enum(_Vocab, name="planted_status"), info={"approval_capable": False})
    )
    assert any("Enum-typed" in f for f in _declaration_failures(md, set()))


def test_the_fourth_leg_ignores_a_check_that_does_not_enumerate_the_vocabulary() -> None:
    """`status <> 'validated' OR …` is satisfied by 'approved' without naming it."""
    assert not _check_enumerates_approved(
        "status <> 'validated' OR validation_report_id IS NOT NULL"
    )
    assert not _check_enumerates_approved("status <> 'approved' OR approved_by IS NOT NULL")
    assert _check_enumerates_approved("status IN ('draft', 'approved')")
    assert _check_enumerates_approved("status = ANY (ARRAY['draft'::text, 'approved'::text])")


def test_a_planted_vocabulary_and_marker_together_fail() -> None:
    md = _scratch(
        Column("status", String(16), info={"status_vocabulary": _Vocab, "approval_capable": False})
    )
    assert any("both" in f for f in _declaration_failures(md, set()))
