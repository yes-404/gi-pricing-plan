"""The validation engine (`01` §3.3, FR-DATA-15/16/19/20/22).

Pure: frames in, report out. These run with no database and no platform, which is what
lets a disputed failure be settled in a notebook against the same rule set.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import polars as pl
import pytest

from model_schema import (
    Acknowledgement,
    OverallOutcome,
    RuleOutcome,
    RuleSetEntry,
    Severity,
    ValidationLayer,
    ValidationRule,
    ValidationRuleSet,
)
from pricing_core.data.validate import CHECKS, register_check, run_validation

EXPOSURE = pl.DataFrame(
    {
        "policy_id": ["P1", "P2", "P3", "P4"],
        "exposure_start": ["2026-01-01", "2026-01-01", "2026-02-01", "2026-03-01"],
        "exposure_end": ["2026-07-01", "2026-07-01", "2026-08-01", "2026-09-01"],
        "exposure_years": [0.5, 0.5, 0.5, 0.5],
        "peril": ["AD", "AD", "TP", "AD"],
    }
)


def _rule(check: str, *, layer=ValidationLayer.ACTUARIAL_SANITY, severity=Severity.FAIL,
          slug="a-rule", target=None, params=None, tolerance=None) -> ValidationRule:
    return ValidationRule(
        id=uuid4(), slug=slug, version=1, layer=layer, check=check, severity=severity,
        target=target or {"table": "policy_exposure"},
        params=params or {}, tolerance=tolerance or {},
    )


def _set(*rules: ValidationRule, overrides=None) -> ValidationRuleSet:
    overrides = overrides or {}
    return ValidationRuleSet(
        id=uuid4(), slug="test-set", version=1,
        entries=tuple(
            RuleSetEntry(rule=r, severity_override=overrides.get(r.slug)) for r in rules
        ),
    )


def _run(rule_set: ValidationRuleSet, tables=None, **kw):
    return run_validation(
        tables or {"policy_exposure": EXPOSURE},
        rule_set,
        dataset_version_id=uuid4(),
        **kw,
    )


# -- FR-DATA-19: independence, and an unrun rule is never a pass ---------------------------


@pytest.mark.req("FR-DATA-19")
def test_one_rule_erroring_does_not_stop_the_others() -> None:
    """A run that abandoned the rest would report one problem where there are nine."""
    broken = _rule("range", slug="broken", target={"table": "policy_exposure", "column": "nope"},
                   params={"min_exclusive": 0})
    good = _rule(
        "range", slug="good",
        target={"table": "policy_exposure", "column": "exposure_years"},
        params={"min_exclusive": 0},
    )
    report = _run(_set(broken, good))

    by_slug = {r.rule_slug: r for r in report.results}
    assert by_slug["broken"].outcome is RuleOutcome.ERROR
    assert by_slug["good"].outcome is RuleOutcome.PASS
    assert len(report.results) == 2


@pytest.mark.req("FR-DATA-19")
def test_an_errored_rule_is_never_a_pass() -> None:
    """FR-DATA-19's sentence, asserted: an unrun rule blocks validation.

    "The rule that would have caught it timed out" and "the rule passed" must never look
    the same in a report an actuary relies on.
    """
    report = _run(_set(_rule("no_such_check", slug="unknown")))
    assert report.results[0].outcome is RuleOutcome.ERROR
    assert report.results[0].error_reason == "unknown_check"
    assert report.overall is OverallOutcome.ERROR
    assert report.permits_validation is False


@pytest.mark.req("FR-DATA-19")
def test_a_rule_exceeding_its_budget_is_an_error_with_reason_timeout() -> None:
    import time

    @register_check("deliberately_slow")
    def _slow(rule, tables, ctx):
        from pricing_core.data.validate import CheckOutcome

        time.sleep(0.05)
        return CheckOutcome()

    try:
        report = _run(_set(_rule("deliberately_slow", slug="slow")), rule_budget_s=0.01)
        assert report.results[0].outcome is RuleOutcome.ERROR
        assert report.results[0].error_reason == "timeout"
        assert report.permits_validation is False
    finally:
        CHECKS.pop("deliberately_slow", None)


@pytest.mark.req("FR-DATA-19")
def test_a_duplicate_check_registration_is_refused() -> None:
    """Negative: two implementations of one name makes meaning depend on import order."""
    with pytest.raises(ValueError, match="already registered"):
        register_check("range")(lambda rule, tables, ctx: None)  # type: ignore[arg-type,return-value]


# -- `01` §4.6: the overall outcome is derived --------------------------------------------


@pytest.mark.req("FR-DATA-17")
def test_a_clean_run_passes() -> None:
    report = _run(
        _set(
            _rule(
                "range",
                target={"table": "policy_exposure", "column": "exposure_years"},
                params={"min_exclusive": 0, "max_inclusive": 1.05},
            )
        )
    )
    assert report.overall is OverallOutcome.PASS
    assert report.permits_validation is True


@pytest.mark.req("FR-DATA-17")
def test_an_unacknowledged_warning_is_pass_with_warnings_and_still_blocks_promotion() -> (
    None
):
    """`01` §4.6, as amended 2026-08-14: the two questions are separate.

    `overall` is a function of the rule results alone, so a warning is
    `pass_with_warnings` from the moment the report is written — the state *every* report
    with warnings is in before anyone has looked at it. Whether the version may be promoted
    is the second question, and FR-DATA-17 answers it at promotion from
    `unacknowledged_warnings`, which is a fact about the report rather than inside it.

    This test asserted `FAIL` until 2026-08-17, encoding the pre-amendment rule. It was not
    a harmless stale assertion: the property it pinned deadlocked promotion for every
    dataset version carrying a warning, since `dataset.validate` reads
    `permits_validation`, acknowledgement happens afterwards, and re-validating regenerates
    the warning unacknowledged. `wf-01` B8/B9 is what asked for the state that shows it.
    """
    warning = _rule("range", slug="warn-rule", severity=Severity.WARN,
                    target={"table": "policy_exposure", "column": "exposure_years"},
                    params={"max_inclusive": 0.1})
    report = _run(_set(warning))

    assert report.results[0].outcome is RuleOutcome.WARN
    assert report.unacknowledged_warnings == 1
    assert report.overall is OverallOutcome.PASS_WITH_WARNINGS
    assert report.permits_validation is True


@pytest.mark.req("FR-DATA-17")
def test_an_acknowledged_warning_permits_validation() -> None:
    warning = _rule("range", slug="warn-rule", severity=Severity.WARN,
                    target={"table": "policy_exposure", "column": "exposure_years"},
                    params={"max_inclusive": 0.1})
    report = _run(_set(warning))
    acknowledged = report.model_copy(
        update={
            "results": (
                report.results[0].model_copy(
                    update={
                        "acknowledgement": Acknowledgement(
                            user_id=uuid4(), at=datetime.now(UTC),
                            justification="Expected: mid-term adjustments in this extract.",
                        )
                    }
                ),
            )
        }
    )
    assert acknowledged.overall is OverallOutcome.PASS_WITH_WARNINGS
    assert acknowledged.permits_validation is True


@pytest.mark.req("FR-DATA-17")
def test_a_failure_blocks_validation_however_many_warnings_are_acknowledged() -> None:
    failing = _rule("range", slug="fail-rule", severity=Severity.FAIL,
                    target={"table": "policy_exposure", "column": "exposure_years"},
                    params={"max_inclusive": 0.1})
    report = _run(_set(failing))
    assert report.overall is OverallOutcome.FAIL
    assert report.permits_validation is False


# -- FR-DATA-21 / §4.3: an override may only raise ------------------------------------------


@pytest.mark.req("FR-DATA-21")
def test_an_override_may_raise_a_warning_to_a_failure() -> None:
    rule = _rule("range", slug="tightened", severity=Severity.WARN,
                 target={"table": "policy_exposure", "column": "exposure_years"},
                 params={"max_inclusive": 0.1})
    report = _run(_set(rule, overrides={"tightened": Severity.FAIL}))
    assert report.results[0].outcome is RuleOutcome.FAIL


@pytest.mark.req("FR-DATA-21")
def test_an_override_may_not_lower_a_failure_to_a_warning() -> None:
    """Negative: lowering severity in a rule set would be a way to pass validation without
    changing anything a reviewer sees. Lowering means editing the rule (FR-DATA-21)."""
    rule = _rule("range", slug="weakened", severity=Severity.FAIL)
    with pytest.raises(ValueError, match="may only raise"):
        RuleSetEntry(rule=rule, severity_override=Severity.WARN)


# -- FR-DATA-16: four layers -----------------------------------------------------------------


@pytest.mark.req("FR-DATA-16")
def test_a_rule_set_missing_a_layer_reports_it() -> None:
    """FR-DATA-16: an empty layer is a configuration warning, surfaced rather than silent.

    Silence would let a rule set lose its whole distributional layer in an edit and still
    look complete.
    """
    report = _run(_set(_rule("range", layer=ValidationLayer.ACTUARIAL_SANITY,
                             target={"table": "policy_exposure", "column": "exposure_years"},
                             params={"min_exclusive": 0})))
    assert set(report.empty_layers) == {
        ValidationLayer.STRUCTURAL,
        ValidationLayer.REFERENTIAL,
        ValidationLayer.DISTRIBUTIONAL,
    }


@pytest.mark.req("FR-DATA-16")
def test_a_rule_set_covering_every_layer_reports_none_empty() -> None:
    rules = [
        _rule("not_null", slug="structural-rule", layer=ValidationLayer.STRUCTURAL,
              target={"table": "policy_exposure", "column": "policy_id"}),
        _rule("cross_table_key", slug="referential-rule", layer=ValidationLayer.REFERENTIAL,
              target={"table": "policy_exposure", "column": "policy_id"},
              params={"references_table": "policy_exposure", "references_column": "policy_id"}),
        _rule("range", slug="actuarial-rule", layer=ValidationLayer.ACTUARIAL_SANITY,
              target={"table": "policy_exposure", "column": "exposure_years"},
              params={"min_exclusive": 0}),
        _rule("volume_shift", slug="distributional-rule", layer=ValidationLayer.DISTRIBUTIONAL,
              target={"table": "policy_exposure"}),
    ]
    report = _run(_set(*rules))
    assert report.empty_layers == ()


# -- FR-DATA-20: every non-pass carries its evidence -----------------------------------------


@pytest.mark.req("FR-DATA-20")
def test_a_failure_records_measurement_threshold_rows_and_sample() -> None:
    frame = pl.DataFrame(
        {"policy_id": ["P1", "P2", "P3"], "exposure_years": [0.5, -0.1, 0.0]}
    )
    rule = _rule("range", target={"table": "policy_exposure", "column": "exposure_years"},
                 params={"min_exclusive": 0, "key_columns": ["policy_id"]})
    report = _run(_set(rule), tables={"policy_exposure": frame})
    result = report.results[0]

    assert result.outcome is RuleOutcome.FAIL
    assert result.affected_rows == 2
    assert result.measured["violating_rows"] == 2
    assert result.threshold["min_exclusive"] == 0
    assert set(result.offending_sample) == {"P2", "P3"}
    assert result.detail


@pytest.mark.req("FR-DATA-20")
def test_the_offending_sample_is_capped_at_a_hundred_keys() -> None:
    """A failing rule on five million rows must not put five million keys in a report."""
    frame = pl.DataFrame(
        {"policy_id": [f"P{i}" for i in range(500)], "exposure_years": [-1.0] * 500}
    )
    rule = _rule("range", target={"table": "policy_exposure", "column": "exposure_years"},
                 params={"min_exclusive": 0, "key_columns": ["policy_id"]})
    report = _run(_set(rule), tables={"policy_exposure": frame})
    assert report.results[0].affected_rows == 500
    assert len(report.results[0].offending_sample) == 100


@pytest.mark.req("FR-DATA-20")
def test_the_affected_exposure_fraction_is_reported() -> None:
    """Row counts mislead: 2 rows of 5 sounds small until they carry 80 % of exposure."""
    frame = pl.DataFrame(
        {
            "policy_id": ["P1", "P2", "P3"],
            "exposure_years": [8.0, 1.0, 1.0],
        }
    )
    rule = _rule("range", target={"table": "policy_exposure", "column": "exposure_years"},
                 params={"max_inclusive": 1.05})
    report = _run(_set(rule), tables={"policy_exposure": frame})
    assert report.results[0].affected_exposure_fraction == pytest.approx(0.8)


@pytest.mark.req("FR-DATA-20")
def test_a_passing_rule_carries_no_offending_sample() -> None:
    """Negative: evidence for a pass is noise, and a sample on a passing rule reads as a
    finding to anyone skimming the report."""
    rule = _rule("range", target={"table": "policy_exposure", "column": "exposure_years"},
                 params={"min_exclusive": 0})
    result = _run(_set(rule)).results[0]
    assert result.offending_sample == ()
    assert result.affected_rows is None


# -- FR-DATA-22: a report is interpretable after the rules change ----------------------------


@pytest.mark.req("FR-DATA-22")
def test_the_report_records_the_rule_set_and_rule_versions() -> None:
    rule = _rule("range", target={"table": "policy_exposure", "column": "exposure_years"},
                 params={"min_exclusive": 0})
    rule_set = _set(rule)
    report = _run(rule_set)
    assert report.rule_set_id == rule_set.id
    assert report.rule_set_version == rule_set.version
    assert report.results[0].rule_version == rule.version


# -- the checks themselves --------------------------------------------------------------------


@pytest.mark.req("FR-DATA-16")
def test_structural_checks_find_their_violations() -> None:
    frame = pl.DataFrame({"policy_id": ["P1", "P1", None], "peril": ["AD", "XX", "AD"]})
    rules = [
        _rule("not_null", slug="nulls", layer=ValidationLayer.STRUCTURAL,
              target={"table": "t", "column": "policy_id"}),
        _rule("unique_key", slug="key", layer=ValidationLayer.STRUCTURAL,
              target={"table": "t"}, params={"columns": ["policy_id"]}),
        _rule("allowed_values", slug="domain", layer=ValidationLayer.STRUCTURAL,
              target={"table": "t", "column": "peril"}, params={"values": ["AD", "TP"]}),
        _rule("column_presence", slug="present", layer=ValidationLayer.STRUCTURAL,
              target={"table": "t"}, params={"columns": ["policy_id", "missing_col"]}),
    ]
    report = _run(_set(*rules), tables={"t": frame})
    outcomes = {r.rule_slug: r.outcome for r in report.results}
    assert outcomes == {
        "nulls": RuleOutcome.FAIL,
        "key": RuleOutcome.FAIL,
        "domain": RuleOutcome.FAIL,
        "present": RuleOutcome.FAIL,
    }


@pytest.mark.req("FR-DATA-16")
def test_actuarial_checks_find_overlaps_and_bad_periods() -> None:
    frame = pl.DataFrame(
        {
            "policy_id": ["P1", "P1", "P2"],
            "exposure_start": ["2026-01-01", "2026-04-01", "2026-01-01"],
            "exposure_end": ["2026-07-01", "2026-10-01", "2025-12-01"],
        }
    )
    rules = [
        _rule("no_overlap", slug="overlap", target={"table": "t"},
              params={"key_column": "policy_id", "start_column": "exposure_start",
                      "end_column": "exposure_end"}),
        _rule("period_consistent", slug="period", target={"table": "t"},
              params={"start_column": "exposure_start", "end_column": "exposure_end"}),
    ]
    report = _run(_set(*rules), tables={"t": frame})
    outcomes = {r.rule_slug: r.outcome for r in report.results}
    assert outcomes["overlap"] is RuleOutcome.FAIL   # P1's second interval starts inside the first
    assert outcomes["period"] is RuleOutcome.FAIL    # P2 ends before it starts


@pytest.mark.req("FR-DATA-16")
def test_a_referential_check_finds_an_unresolved_key() -> None:
    claims = pl.DataFrame({"claim_id": ["C1", "C2"], "policy_id": ["P1", "UNKNOWN"]})
    rule = _rule("cross_table_key", slug="linkage", layer=ValidationLayer.REFERENTIAL,
                 target={"table": "claim", "column": "policy_id"},
                 params={"references_table": "policy_exposure", "references_column": "policy_id"})
    report = _run(_set(rule), tables={"claim": claims, "policy_exposure": EXPOSURE})
    assert report.results[0].outcome is RuleOutcome.FAIL
    assert report.results[0].offending_sample == ("UNKNOWN",)


@pytest.mark.req("FR-DATA-16")
def test_a_distributional_check_without_a_reference_is_skipped_not_passed() -> None:
    """Negative: a distributional rule with nothing to compare against has not passed.

    Reporting it as a pass would make the first version of a dataset look stable.
    """
    rule = _rule("volume_shift", slug="volume", layer=ValidationLayer.DISTRIBUTIONAL,
                 target={"table": "policy_exposure"})
    report = _run(_set(rule))
    assert report.results[0].outcome is RuleOutcome.SKIPPED
    assert "reference" in report.results[0].detail


@pytest.mark.req("FR-DATA-16")
def test_a_distributional_check_detects_a_volume_shift() -> None:
    reference = EXPOSURE.head(2)
    rule = _rule("volume_shift", slug="volume", layer=ValidationLayer.DISTRIBUTIONAL,
                 severity=Severity.WARN, target={"table": "policy_exposure"},
                 params={"max_shift_fraction": 0.2})
    report = _run(_set(rule), reference_frames={"policy_exposure": reference})
    assert report.results[0].outcome is RuleOutcome.WARN
    assert report.results[0].measured["ratio"] == 2.0


@pytest.mark.req("FR-DATA-16")
def test_a_tolerance_lets_a_known_level_of_violation_pass() -> None:
    frame = pl.DataFrame({"policy_id": ["P1", "P2"], "exposure_years": [0.5, -0.1]})
    rule = _rule("range", target={"table": "t", "column": "exposure_years"},
                 params={"min_exclusive": 0}, tolerance={"max_violating_rows": 1})
    report = _run(_set(rule), tables={"t": frame})
    assert report.results[0].outcome is RuleOutcome.PASS


@pytest.mark.req("FR-DATA-18")
def test_an_acknowledgement_does_not_carry_forward_to_the_next_report() -> None:
    """FR-DATA-18: an acknowledgement is scoped to `(version, rule, report)`.

    Each run produces a fresh report whose results carry no acknowledgements, so
    re-validating cannot inherit a previous acceptance. That is the property the
    requirement exists for: a warning accepted last month, on last month's evidence, must
    not silently accept this month's data — the two may be the same rule and a different
    problem.
    """
    warning = _rule(
        "range", slug="warn-rule", severity=Severity.WARN,
        target={"table": "policy_exposure", "column": "exposure_years"},
        params={"max_inclusive": 0.1},
    )
    rule_set = _set(warning)

    first = _run(rule_set)
    accepted = first.model_copy(
        update={
            "results": (
                first.results[0].model_copy(
                    update={
                        "acknowledgement": Acknowledgement(
                            user_id=uuid4(), at=datetime.now(UTC),
                            justification="Accepted for the 2026H1 extract.",
                        )
                    }
                ),
            )
        }
    )
    assert accepted.permits_validation is True

    # A second run of the same rule set over the same data: same finding, no acceptance.
    second = _run(rule_set)
    assert second.id != accepted.id
    assert second.results[0].acknowledgement is None
    assert second.unacknowledged_warnings == 1
    # The outcome is unchanged — it never depended on acknowledgement (§4.6, amended). What
    # the fresh report loses is the acceptance, and that is what blocks promotion.
    assert second.overall is OverallOutcome.PASS_WITH_WARNINGS


@pytest.mark.req("FR-DATA-24")
def test_distributional_rules_answer_from_a_stored_profile() -> None:
    """FR-DATA-24: distributional rules use pre-computed profile aggregates rather than
    re-scanning the reference version.

    A null rate and a row count are both already in a Profile. Loading ten million
    reference rows to recompute one of them is exactly the re-scan the requirement rules
    out — and at that size it is not a slow answer, it is an out-of-memory error.

    No reference *frame* is supplied here at all. If the checks still re-scanned they would
    skip, and a skipped distributional layer is how a mix shift reaches a model.
    """
    from pricing_core.data.profile import profile_frame

    reference_frame = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(400)],
            "exposure_years": [1.0] * 400,
            "vehicle_group": [None if i % 100 == 0 else f"G{i % 5}" for i in range(400)],
        }
    )
    reference_profile = profile_frame(reference_frame, dataset_version_id=uuid4())

    # Half the rows, and a much higher null rate: both rules should fire.
    current = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(200)],
            "exposure_years": [1.0] * 200,
            "vehicle_group": [None if i % 4 == 0 else f"G{i % 5}" for i in range(200)],
        }
    )

    rules = (
        RuleSetEntry(
            rule=ValidationRule(
                id=uuid4(), slug="null-shift", version=1,
                layer=ValidationLayer.DISTRIBUTIONAL, check="null_rate_shift",
                severity=Severity.WARN,
                target={"table": "exposure", "column": "vehicle_group"},
                params={"max_shift_pp": 5.0},
            )
        ),
        RuleSetEntry(
            rule=ValidationRule(
                id=uuid4(), slug="volume-shift", version=1,
                layer=ValidationLayer.DISTRIBUTIONAL, check="volume_shift",
                severity=Severity.WARN,
                target={"table": "exposure"},
                params={"max_shift_fraction": 0.2},
            )
        ),
    )
    report = run_validation(
        {"exposure": current},
        ValidationRuleSet(id=uuid4(), slug="s", version=1, entries=rules),
        dataset_version_id=uuid4(),
        reference_profile=reference_profile,
    )

    outcomes = {result.rule_slug: result for result in report.results}
    assert outcomes["null-shift"].outcome is RuleOutcome.WARN
    assert outcomes["null-shift"].measured["reference_null_rate"] == pytest.approx(0.01)
    assert outcomes["volume-shift"].outcome is RuleOutcome.WARN
    assert outcomes["volume-shift"].measured["reference_rows"] == 400
    # Neither skipped, which is the claim: no reference frame was supplied.
    assert all(r.outcome is not RuleOutcome.SKIPPED for r in report.results)
