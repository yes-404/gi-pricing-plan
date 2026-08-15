"""The `sql` escape hatch and its sandbox (`01` §4.5, NFR-DATA-9, OQ-DATA-3).

Every test here attempts the attack rather than asserting the configuration. A sandbox
verified by reading its settings is a sandbox nobody has tried to escape — and the settings
that matter are the ones whose absence is silent.
"""

from __future__ import annotations

from uuid import uuid4

import polars as pl
import pytest

from model_schema import (
    RuleSetEntry,
    Severity,
    ValidationLayer,
    ValidationRule,
    ValidationRuleSet,
)
from pricing_core.data.validate import (
    CHECKS,
    SqlCheckError,
    ValidationContext,
    run_validation,
)

FRAME = pl.DataFrame(
    {
        "policy_id": [f"P{i}" for i in range(10)],
        "exposure_years": [1.0] * 8 + [-0.5, 0.0],
        "claim_count": [0] * 10,
    }
)
CONTEXT = ValidationContext(reference_tables={}, reference_frames={})


def _rule(query: str, **params: object) -> ValidationRule:
    return ValidationRule(
        id=uuid4(),
        slug="custom-sql",
        version=1,
        layer=ValidationLayer.ACTUARIAL_SANITY,
        check="sql",
        severity=Severity.FAIL,
        target={"table": "exposure"},
        params={"query": query, **params},
    )


def _run(query: str, **params: object):
    return CHECKS["sql"](_rule(query, **params), {"exposure": FRAME}, CONTEXT)


@pytest.mark.req("FR-DATA-21")
def test_a_counting_query_reports_violating_rows() -> None:
    """The happy path: the query answers the rule's question with a number."""
    outcome = _run("SELECT count(*) FROM exposure WHERE exposure_years <= 0")
    assert outcome.violating_rows == 2
    assert outcome.measured == {"violating_rows": 2}


@pytest.mark.req("FR-DATA-21")
def test_a_boolean_query_is_an_assertion() -> None:
    outcome = _run("SELECT min(exposure_years) > 0 FROM exposure")
    assert outcome.violating_rows == 1  # the assertion does not hold

    outcome = _run("SELECT max(exposure_years) <= 1 FROM exposure")
    assert outcome.violating_rows == 0


@pytest.mark.req("NFR-DATA-9")
@pytest.mark.parametrize(
    "query",
    [
        "SELECT 1; DROP TABLE exposure",
        "SELECT 1 /* hide the semicolon */ ; DELETE FROM exposure",
        "DROP TABLE exposure",
        "CREATE TABLE evil AS SELECT 1",
        "UPDATE exposure SET exposure_years = 1",
        "COPY exposure TO '/tmp/leak.csv'",
        "INSTALL httpfs",
        "ATTACH '/tmp/other.db' AS other",
    ],
)
def test_only_a_single_select_is_accepted(query: str) -> None:
    """NFR-DATA-9: cannot write, cannot load extensions, cannot reach another database.

    Parsed by DuckDB rather than pattern-matched. A regex over SQL is a guess, and the
    comment case above is exactly what it guesses wrong.
    """
    with pytest.raises(SqlCheckError):
        _run(query)


@pytest.mark.req("NFR-DATA-9")
@pytest.mark.parametrize(
    "query",
    [
        "SELECT count(*) FROM read_csv('/etc/passwd')",
        "SELECT count(*) FROM read_parquet('/etc/hostname')",
        "SELECT * FROM glob('/etc/*')",
    ],
)
def test_the_query_cannot_read_outside_the_registered_tables(query: str) -> None:
    """NFR-DATA-9: cannot read outside the target version's data.

    The tables are registered as views from frames already in memory, so the query has
    something to read without the connection having a path to anything else. These are
    single SELECTs and pass the statement check — the file system refusal is a separate
    control, which is why both exist.
    """
    with pytest.raises(SqlCheckError) as excinfo:
        _run(query)
    assert "Permission" in str(excinfo.value) or "disabled" in str(excinfo.value)


@pytest.mark.req("NFR-DATA-9")
def test_a_runaway_query_is_interrupted_at_its_budget() -> None:
    """NFR-DATA-9: *killed* at its time budget, not reported on after it finishes.

    The engine's per-rule budget is checked after a check returns, which is fine for a
    Polars expression and useless against a query that would run for an hour. This one
    generates ten billion rows; without the interrupt the test would not finish.
    """
    with pytest.raises(SqlCheckError) as excinfo:
        _run("SELECT count(*) FROM range(10000000000)", timeout_s=0.5)
    assert "budget" in str(excinfo.value)


@pytest.mark.req("FR-DATA-19")
def test_a_broken_sql_rule_becomes_an_error_and_the_others_still_run() -> None:
    """FR-DATA-19: rules are independent, and an unrun rule is never a pass.

    The whole reason the escape hatch is survivable: a user's SQL that does not parse
    fails that rule and no other.
    """
    good = RuleSetEntry(rule=_rule("SELECT count(*) FROM exposure WHERE claim_count < 0"))
    broken = RuleSetEntry(rule=_rule("SELECT 1; DROP TABLE exposure"))
    rule_set = ValidationRuleSet(
        id=uuid4(), slug="s", version=1, entries=(broken, good)
    )

    report = run_validation({"exposure": FRAME}, rule_set, dataset_version_id=uuid4())
    outcomes = {result.rule_id: result.outcome.value for result in report.results}
    assert outcomes[broken.rule.id] == "error"
    assert outcomes[good.rule.id] == "pass"


@pytest.mark.req("NFR-DATA-9")
def test_a_query_returning_a_table_is_refused() -> None:
    """A rule reports a number of violating rows. A query returning a table has not
    answered the question the rule asks, and guessing which column meant what would make
    the rule's meaning depend on the shape of its output."""
    with pytest.raises(SqlCheckError):
        _run("SELECT policy_id, exposure_years FROM exposure")
