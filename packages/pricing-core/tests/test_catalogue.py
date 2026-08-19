"""The built-in rule catalogue (`01` §4.4) — all 38 rules.

`scope-audit --catalogue VR` proves each id is *named* in the code. That is a claim, not a
proof, in exactly the way a `@pytest.mark.req` marker is. This file is the proof: every
rule gets a case where it fires and a case where it does not, because a check that always
passes and a check that always fails are equally useless and equally invisible.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import uuid4

import polars as pl
import pytest

from model_schema import (
    Profile,
    RuleSetEntry,
    Severity,
    ValidationLayer,
    ValidationRule,
    ValidationRuleSet,
)
from pricing_core.data.profile import profile_frame
from pricing_core.data.validate import CHECKS, ValidationContext, run_validation

EMPTY = ValidationContext(reference_tables={}, reference_frames={})


def rule(check: str, **kwargs: Any) -> ValidationRule:
    """A rule for one check, with sensible target/params defaults."""
    return ValidationRule(
        id=uuid4(),
        slug=check.replace("_", "-"),
        version=1,
        layer=kwargs.pop("layer", ValidationLayer.STRUCTURAL),
        check=check,
        severity=kwargs.pop("severity", Severity.FAIL),
        target=kwargs.pop("target", {"table": "t"}),
        params=kwargs.pop("params", {}),
    )


def run(
    check: str,
    tables: dict[str, pl.DataFrame],
    *,
    context: ValidationContext | None = None,
    **kwargs: Any,
) -> Any:
    return CHECKS[check](rule(check, **kwargs), tables, context or EMPTY)


# -- Layer 1: structural ---------------------------------------------------------------


@pytest.mark.req("FR-DATA-16")
def test_vr_str_2_dtype_match() -> None:
    """VR-STR-2. Counts columns, because a dtype is a property of a column — reporting
    "3 400 000 rows are Int64" would be true and useless."""
    frame = pl.DataFrame({"policy_id": [1, 2], "premium": [1.0, 2.0]})
    declared = {"policy_id": "String", "premium": "Float64"}

    bad = run("dtype_match", {"t": frame}, params={"columns": declared})
    assert bad.violating_rows == 1
    assert bad.measured["mismatched_columns"]["policy_id"]["actual"] == "Int64"

    good = run("dtype_match", {"t": frame}, params={"columns": {"premium": "Float64"}})
    assert good.violating_rows == 0


@pytest.mark.req("FR-DATA-16")
def test_vr_str_5_date_parsed() -> None:
    """VR-STR-5. A date left as a string sorts lexically, so `10/01/2024` precedes
    `02/01/2025` and every period comparison downstream is silently wrong."""
    frame = pl.DataFrame({"start": ["2024-01-01"], "end": [date(2024, 12, 31)]})
    outcome = run("date_parsed", {"t": frame}, params={"columns": ["start", "end"]})
    assert outcome.violating_rows == 1
    assert outcome.offending_sample == ("start",)

    assert run("date_parsed", {"t": frame}, params={"columns": ["end"]}).violating_rows == 0


@pytest.mark.req("FR-DATA-16")
def test_vr_str_6_encoding() -> None:
    """VR-STR-6. A broker feed in the wrong codec produces new "levels" that look like
    genuine categories and quietly split a factor.

    The bad values are built from escapes rather than pasted: a source file containing real
    mojibake is one that every editor and diff tool will offer to "fix".
    """
    replacement = "Bruy\ufffdre"          # a lossy decode left U+FFFD behind
    latin1_of_cp1252 = "Caf\u0092s"        # a C1 control where a curly quote was meant
    frame = pl.DataFrame({"name": [replacement, "Dupont", latin1_of_cp1252]})
    outcome = run("encoding", {"t": frame}, params={"columns": ["name"]})
    assert outcome.violating_rows == 2

    clean = pl.DataFrame({"name": ["Bruy\u00e8re", "Dupont"]})
    assert run("encoding", {"t": clean}, params={"columns": ["name"]}).violating_rows == 0


@pytest.mark.req("FR-DATA-16")
def test_vr_str_8_no_unexpected_columns() -> None:
    """VR-STR-8. An extra column breaks nothing by itself; it is the clearest sign the
    upstream extract changed, and that change usually changed something else too."""
    frame = pl.DataFrame({"a": [1], "b": [2], "surprise": [3]})
    outcome = run("no_unexpected_columns", {"t": frame}, params={"columns": ["a", "b"]})
    assert outcome.violating_rows == 1
    assert outcome.offending_sample == ("surprise",)

    assert (
        run(
            "no_unexpected_columns",
            {"t": frame},
            params={"columns": ["a", "b", "surprise"]},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-7")
def test_vr_str_9_reject_rate() -> None:
    """VR-STR-9 / FR-DATA-7. The default 0.1 % is deliberately tight: a threshold loose
    enough never to fire is one nobody would notice going wrong."""
    clean = pl.DataFrame({"policy_id": [f"P{i}" for i in range(1000)]})
    rejected = pl.DataFrame({"policy_id": ["X1", "X2", "X3", "X4", "X5"]})

    outcome = run("reject_rate", {"t": clean, "_rejected": rejected})
    assert outcome.violating_rows == 5
    assert outcome.measured["reject_rate"] == pytest.approx(5 / 1005, rel=1e-3)

    assert run("reject_rate", {"t": clean, "_rejected": rejected.head(0)}).violating_rows == 0


# -- Layer 2: referential --------------------------------------------------------------


REFERENCE_ROWS = pl.DataFrame(
    {
        "key": ["AB", "AB", "CD"],
        "effective_from": [date(2023, 1, 1), date(2024, 1, 1), date(2023, 1, 1)],
        "effective_to": [date(2024, 1, 1), None, None],
        "payload": [{"factor": 1.0}, {"factor": 1.1}, {"factor": 0.9}],
    }
)


def _with_reference(**frames: pl.DataFrame) -> ValidationContext:
    return ValidationContext(
        reference_tables={"areas": REFERENCE_ROWS}, reference_frames=frames
    )


@pytest.mark.req("FR-DATA-31")
def test_vr_ref_1_reference_resolve_is_effective_dated() -> None:
    """VR-REF-1. A postcode that resolves today may not have existed at inception, and a
    lookup ignoring the date silently rates a 2019 risk on a 2025 territory map."""
    frame = pl.DataFrame(
        {
            "policy_id": ["P1", "P2", "P3"],
            "area": ["AB", "CD", "ZZ"],
            "inception": [date(2023, 6, 1)] * 3,
        }
    )
    outcome = run(
        "reference_lookup",
        {"t": frame},
        context=_with_reference(),
        target={"table": "t", "column": "area"},
        params={"reference_table": "areas", "as_at_column": "inception"},
    )
    assert outcome.violating_rows == 1
    assert outcome.offending_sample == ("ZZ@2023-06-01",)

    # The same keys, before the reference table covers them at all.
    early = frame.with_columns(pl.lit(date(2020, 1, 1)).alias("inception"))
    assert (
        run(
            "reference_lookup",
            {"t": early},
            context=_with_reference(),
            target={"table": "t", "column": "area"},
            params={"reference_table": "areas", "as_at_column": "inception"},
        ).violating_rows
        == 3
    )


@pytest.mark.req("FR-DATA-31")
def test_vr_ref_2_reference_coverage() -> None:
    """VR-REF-2 catches what VR-REF-1 cannot: every value resolving while only a fraction
    of the table is used means the *wrong* reference version is pinned."""
    narrow = pl.DataFrame({"area": ["AB"] * 10})
    outcome = run(
        "reference_coverage",
        {"t": narrow},
        context=_with_reference(),
        target={"table": "t", "column": "area"},
        params={"reference_table": "areas", "min_coverage": 0.9},
    )
    assert outcome.violating_rows == 1
    assert outcome.measured["coverage"] == pytest.approx(0.5)

    wide = pl.DataFrame({"area": ["AB", "CD"]})
    assert (
        run(
            "reference_coverage",
            {"t": wide},
            context=_with_reference(),
            target={"table": "t", "column": "area"},
            params={"reference_table": "areas", "min_coverage": 0.9},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-31")
def test_vr_ref_3_effective_date_in_range() -> None:
    """VR-REF-3. A date after the covered period resolves to the last row for ever, which
    is worse than resolving to nothing — it looks like an answer."""
    frame = pl.DataFrame({"policy_id": ["P1"], "inception": [date(2019, 1, 1)]})
    outcome = run(
        "effective_date_in_range",
        {"t": frame},
        context=_with_reference(),
        params={
            "reference_table": "areas",
            "as_at_column": "inception",
            "key_columns": ["policy_id"],
        },
    )
    assert outcome.violating_rows == 1

    inside = pl.DataFrame({"policy_id": ["P1"], "inception": [date(2024, 6, 1)]})
    assert (
        run(
            "effective_date_in_range",
            {"t": inside},
            context=_with_reference(),
            params={"reference_table": "areas", "as_at_column": "inception"},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-31")
def test_vr_ref_5_code_list_drift() -> None:
    """VR-REF-5 means the *taxonomy* changed; VR-DST-2 means the *book* did. The remedies
    differ — a mapping update, versus a conversation about mix."""
    frame = pl.DataFrame({"area": ["AB", "EF"]})
    outcome = run(
        "code_list_drift",
        {"t": frame},
        context=_with_reference(),
        target={"table": "t", "column": "area"},
        params={"reference_table": "areas"},
    )
    assert outcome.violating_rows == 1
    assert outcome.offending_sample == ("EF",)

    assert (
        run(
            "code_list_drift",
            {"t": pl.DataFrame({"area": ["AB", "CD"]})},
            context=_with_reference(),
            target={"table": "t", "column": "area"},
            params={"reference_table": "areas"},
        ).violating_rows
        == 0
    )


# -- Layer 3: actuarial sanity ---------------------------------------------------------


EXPOSURE = pl.DataFrame(
    {
        "policy_id": ["P1", "P2"],
        "exposure_start": [date(2024, 1, 1), date(2024, 1, 1)],
        "exposure_end": [date(2025, 1, 1), date(2025, 1, 1)],
        "exposure_years": [1.0, 1.0],
        "claim_count": [1, 0],
        "claim_amount_minor": [250_000, 0],
    }
)


@pytest.mark.req("FR-DATA-12")
def test_vr_act_5_claim_date_in_exposure() -> None:
    """VR-ACT-5. Half-open, so a loss on the renewal date belongs to the new term —
    counting it against both would inflate one frequency and deflate the other."""
    claims = pl.DataFrame(
        {"policy_id": ["P1", "P1"], "date_of_loss": [date(2024, 6, 1), date(2025, 1, 1)]}
    )
    outcome = run(
        "claim_date_in_exposure",
        {"t": EXPOSURE, "claim": claims, "policy_exposure": EXPOSURE},
        params={"key_columns": ["policy_id"]},
    )
    # The second claim falls on `exposure_end`, which the half-open interval excludes.
    assert outcome.violating_rows == 1

    assert (
        run(
            "claim_date_in_exposure",
            {"t": EXPOSURE, "claim": claims.head(1), "policy_exposure": EXPOSURE},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-12")
def test_vr_act_6_claim_linkage_complete() -> None:
    """VR-ACT-6. An unlinked claim contributes to a frequency computed over a denominator
    that excludes its own exposure."""
    claims = pl.DataFrame({"policy_id": ["P1", "P404"]})
    outcome = run(
        "claim_linkage_complete",
        {"t": EXPOSURE, "claim": claims, "policy_exposure": EXPOSURE},
    )
    assert outcome.violating_rows == 1

    assert (
        run(
            "claim_linkage_complete",
            {"t": EXPOSURE, "claim": claims.head(1), "policy_exposure": EXPOSURE},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-12")
def test_vr_act_7_claim_not_multi_linked() -> None:
    """VR-ACT-7 is the more dangerous half: a doubly-linked claim is counted twice and,
    unlike an unlinked one, leaves no missing total anywhere to notice."""
    two_terms = pl.DataFrame(
        {
            "policy_id": ["P1", "P1"],
            "exposure_start": [date(2023, 1, 1), date(2024, 1, 1)],
            "exposure_end": [date(2024, 1, 1), date(2025, 1, 1)],
            "exposure_years": [1.0, 1.0],
        }
    )
    claims = pl.DataFrame({"claim_id": ["C1"], "policy_id": ["P1"]})
    # No loss date, so the link is on policy alone and both terms match.
    outcome = run(
        "claim_not_multi_linked",
        {"t": two_terms, "claim": claims, "policy_exposure": two_terms},
    )
    assert outcome.violating_rows == 1

    # With a loss date the period disambiguates and exactly one term matches.
    dated = claims.with_columns(pl.lit(date(2024, 6, 1)).alias("date_of_loss"))
    assert (
        run(
            "claim_not_multi_linked",
            {"t": two_terms, "claim": dated, "policy_exposure": two_terms},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-16")
def test_vr_act_9_claim_amount_sign_counts_rather_than_removes() -> None:
    """VR-ACT-9. Negative incurred is legitimate for recoveries; a platform that deleted
    them would understate recoveries and overstate severity. It must not pass unremarked
    either, because the same number is what a sign error looks like."""
    frame = pl.DataFrame({"claim_amount_minor": [100, -50, 200, 300]})
    outcome = run(
        "claim_amount_sign",
        {"t": frame},
        target={"table": "t", "column": "claim_amount_minor"},
        params={"max_negative_share": 0.1},
    )
    assert outcome.violating_rows == 1
    assert outcome.measured["total_negative_minor"] == -50
    assert frame.height == 4  # nothing removed

    tolerant = run(
        "claim_amount_sign",
        {"t": frame},
        target={"table": "t", "column": "claim_amount_minor"},
        params={"max_negative_share": 0.5},
    )
    assert tolerant.violating_rows == 0


@pytest.mark.req("FR-DATA-16")
def test_vr_act_10_severity_outlier_flags_and_never_removes() -> None:
    """VR-ACT-10. Capping is a modelling decision (OQ-DATA-1), made where its effect on the
    fitted result is visible — not a cleaning step applied silently at ingestion."""
    frame = pl.DataFrame({"claim_amount_minor": [100_00] * 99 + [50_000_00]})
    outcome = run(
        "severity_outlier",
        {"t": frame},
        target={"table": "t", "column": "claim_amount_minor"},
        params={"threshold_minor": 1_000_00},
    )
    assert outcome.violating_rows == 1
    assert outcome.measured["largest_minor"] == 50_000_00
    assert frame.height == 100  # flagged, not removed

    by_percentile = run(
        "severity_outlier",
        {"t": frame},
        target={"table": "t", "column": "claim_amount_minor"},
        params={"percentile": 0.5},
    )
    assert by_percentile.violating_rows > 1


@pytest.mark.req("FR-DATA-16")
def test_vr_act_11_frequency_plausible_catches_a_units_error() -> None:
    """VR-ACT-11. Exposure in months where the model expects years shifts frequency by a
    factor of twelve, and every individual value looks entirely reasonable."""
    in_years = pl.DataFrame(
        {"exposure_years": [1.0] * 100, "claim_count": [1] * 10 + [0] * 90}
    )
    ok = run(
        "frequency_plausible",
        {"t": in_years},
        params={"min_frequency": 0.02, "max_frequency": 0.25},
    )
    assert ok.violating_rows == 0
    assert ok.measured["frequency"] == pytest.approx(0.1)

    in_months = in_years.with_columns(pl.col("exposure_years") / 12)
    bad = run(
        "frequency_plausible",
        {"t": in_months},
        params={"min_frequency": 0.02, "max_frequency": 0.25},
    )
    assert bad.violating_rows == 1
    assert bad.measured["frequency"] == pytest.approx(1.2)


@pytest.mark.req("FR-DATA-16")
def test_vr_act_12_severity_plausible_catches_a_units_error() -> None:
    """VR-ACT-12. Amounts loaded in pounds where the platform stores minor units are out by
    a hundred, and every row still looks like money."""
    minor = pl.DataFrame(
        {
            "exposure_years": [1.0] * 10,
            "claim_count": [1] * 10,
            "claim_amount_minor": [250_000] * 10,
        }
    )
    bounds = {"min_severity_minor": 50_000, "max_severity_minor": 1_000_000}
    assert run("severity_plausible", {"t": minor}, params=bounds).violating_rows == 0

    pounds = minor.with_columns(pl.col("claim_amount_minor") // 100)
    assert run("severity_plausible", {"t": pounds}, params=bounds).violating_rows == 1


@pytest.mark.req("FR-DATA-16")
def test_vr_act_13_zero_claim_cohort() -> None:
    """VR-ACT-13. A level with material exposure that had claims and now has none is almost
    always a join that stopped matching — and the portfolio totals barely move."""
    reference = pl.DataFrame(
        {
            "vehicle_group": ["G1"] * 50 + ["G2"] * 50,
            "exposure_years": [1.0] * 100,
            "claim_count": [1] * 10 + [0] * 40 + [1] * 10 + [0] * 40,
        }
    )
    lost = reference.with_columns(
        pl.when(pl.col("vehicle_group") == "G2")
        .then(0)
        .otherwise(pl.col("claim_count"))
        .alias("claim_count")
    )
    context = ValidationContext(reference_tables={}, reference_frames={"t": reference})
    outcome = run(
        "zero_claim_cohort",
        {"t": lost},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert outcome.violating_rows == 1
    assert outcome.offending_sample == ("G2",)

    assert (
        run(
            "zero_claim_cohort",
            {"t": reference},
            context=context,
            target={"table": "t", "column": "vehicle_group"},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-16")
def test_vr_act_14_development_maturity_warns_and_never_adjusts() -> None:
    """VR-ACT-14 is the platform's *only* treatment of development (§1.2, OQ-DATA-4).

    It flags. A frequency model fitted through the last three months reads IBNR as a
    genuine improvement in claims experience; the warning makes that a visible choice.
    """
    today = date(2025, 6, 30)
    frame = pl.DataFrame(
        {
            "exposure_start": [today - timedelta(days=n) for n in (400, 300, 200, 20, 5)],
            "exposure_years": [1.0] * 5,
        }
    )
    outcome = run("development_maturity", {"t": frame}, params={"immature_months": 3})
    assert outcome.violating_rows == 2
    assert outcome.measured["immature_exposure_share"] == pytest.approx(0.4)
    assert frame.height == 5  # nothing adjusted

    # Materiality, not presence. Measured against the data's own latest period the most
    # recent rows are *always* immature, so a rule firing on any of them would fire on
    # every dataset ever validated — and a warning that always fires gets rubber-stamped.
    tolerant = run(
        "development_maturity",
        {"t": frame},
        params={"immature_months": 3, "max_immature_exposure_share": 0.5},
    )
    assert tolerant.violating_rows == 0


@pytest.mark.req("FR-DATA-16")
def test_vr_act_14_declines_to_guess_on_an_unparsed_period() -> None:
    """A period column still held as a string sorts lexically, so "the most recent three
    months" would select whatever sorts last. VR-STR-5 catches the parse; this declines."""
    frame = pl.DataFrame({"exposure_start": ["2025-06-01", "2024-01-01"]})
    outcome = run("development_maturity", {"t": frame})
    assert outcome.skipped
    assert "VR-STR-5" in outcome.skip_reason


@pytest.mark.req("FR-DATA-16")
def test_vr_act_15_currency_consistency() -> None:
    """VR-ACT-15 fails rather than warns: mixed currency makes every sum in the dataset
    meaningless, and the sums are what the model is fitted on."""
    mixed = pl.DataFrame(
        {"currency": ["GBP", "GBP", "EUR"], "claim_amount_minor": [1, 2, 3]}
    )
    outcome = run("currency_consistency", {"t": mixed}, params={"currency": "GBP"})
    assert outcome.violating_rows == 1
    assert outcome.measured["currencies_present"] == ["EUR", "GBP"]

    assert (
        run("currency_consistency", {"t": mixed.head(2)}, params={"currency": "GBP"})
        .violating_rows
        == 0
    )
    # Without a declared currency the rule still refuses a mixed table.
    assert run("currency_consistency", {"t": mixed}).violating_rows == 3


@pytest.mark.req("FR-DATA-16")
def test_vr_act_16_duplicate_claim() -> None:
    """VR-ACT-16. The double-load signature: a file ingested twice inflates frequency by
    exactly the proportion re-loaded, while every individual row stays valid."""
    claims = pl.DataFrame(
        {
            "policy_id": ["P1", "P1", "P2"],
            "date_of_loss": [date(2024, 3, 1), date(2024, 3, 1), date(2024, 4, 1)],
            "peril": ["AD", "AD", "TP"],
            "claim_amount_minor": [250_000, 250_000, 100_000],
        }
    )
    outcome = run("duplicate_claim", {"t": claims})
    assert outcome.violating_rows == 1
    assert outcome.measured["duplicate_groups"] == 1

    assert run("duplicate_claim", {"t": claims.unique()}).violating_rows == 0


# -- Layer 4: distributional -----------------------------------------------------------


def _profiled(frame: pl.DataFrame, one_ways: list[str] | None = None) -> Profile:
    return profile_frame(frame, dataset_version_id=uuid4(), one_way_columns=one_ways or [])


@pytest.mark.req("FR-DATA-24")
def test_vr_dst_1_psi_column() -> None:
    """VR-DST-1, computed with the same `psi_from_weights` the comparison screen uses — so
    a verdict and the screen an actuary is reading cannot disagree."""
    reference = pl.DataFrame({"vehicle_group": ["G1"] * 500 + ["G2"] * 500})
    shifted = pl.DataFrame({"vehicle_group": ["G1"] * 950 + ["G2"] * 50})
    context = ValidationContext(
        reference_tables={}, reference_frames={}, reference_profile=_profiled(reference)
    )
    outcome = run(
        "psi_column",
        {"t": shifted},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert outcome.violating_rows == 1
    assert outcome.measured["psi"] > 0.25

    steady = run(
        "psi_column",
        {"t": reference},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert steady.violating_rows == 0
    assert steady.measured["psi"] == pytest.approx(0.0, abs=1e-9)


@pytest.mark.req("FR-DATA-24")
def test_vr_dst_2_new_level_and_vr_dst_3_vanished_level() -> None:
    """VR-DST-2 and VR-DST-3. Material weight for the vanished one, because a rare level
    disappearing is noise while a level holding real exposure is a broken join."""
    # G5 is deliberately tiny — 0.2 % of the book. It vanishes too, and must *not* be
    # reported: without a case below the materiality threshold the filter is untested, and
    # removing it entirely would leave every assertion here passing.
    reference = pl.DataFrame(
        {
            "vehicle_group": ["G1"] * 500 + ["G2"] * 398 + ["G3"] * 100 + ["G5"] * 2,
            "exposure_years": [1.0] * 1000,
            "claim_count": [0] * 1000,
            "claim_amount_minor": [0] * 1000,
        }
    )
    context = ValidationContext(
        reference_tables={},
        reference_frames={},
        reference_profile=_profiled(reference, ["vehicle_group"]),
    )
    current = pl.DataFrame({"vehicle_group": ["G1"] * 500 + ["G4"] * 500})

    new = run(
        "new_level",
        {"t": current},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert new.offending_sample == ("G4",)

    gone = run(
        "vanished_level",
        {"t": current},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert set(gone.offending_sample) == {"G2", "G3"}, (
        "G5 vanished too but holds 0.2 % of the exposure — a rare level disappearing is "
        "noise, and reporting it would bury the two that matter"
    )

    assert (
        run(
            "new_level",
            {"t": reference},
            context=context,
            target={"table": "t", "column": "vehicle_group"},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-49")
def test_vr_dst_1_psi_column_excludes_nulls_on_both_sides() -> None:
    """The trap: the reference side (`top_levels`) excludes a null level, the same as
    `_psi` in `profile.py`. If the current side (`_level_counts`) kept it under the key
    `"None"` instead of excluding it too, the two weight maps would disagree about their
    totals and shares for no reason but the null coercion — inventing drift on every
    column that has one. 20 % of this column is null in both versions and nothing else
    moves: PSI must land at (or near) zero, not spike."""
    reference = pl.DataFrame({"vehicle_group": ["G1"] * 400 + ["G2"] * 400 + [None] * 200})
    context = ValidationContext(
        reference_tables={}, reference_frames={}, reference_profile=_profiled(reference)
    )
    outcome = run(
        "psi_column",
        {"t": reference},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert outcome.violating_rows == 0
    assert outcome.measured["psi"] == pytest.approx(0.0, abs=1e-9)


@pytest.mark.req("FR-DATA-49")
def test_vr_dst_3_vanished_level_top_levels_fallback_is_judged_on_exposure() -> None:
    """Ruling 2c: once a version's profile carries per-level `exposure_years`, the
    `top_levels` fallback in `_vanished_level` must judge materiality on exposure, not on
    the count it used to stand in for. G1 is 995 of 1000 rows but a sliver of exposure
    (0.1986 %, immaterial); G2 is 5 rows but nearly all the exposure (99.8 %, material).
    `one_ways=[]` keeps `ctx.reference_profile.one_ways` empty so `_vanished_level` falls
    through past its (already-correct, out-of-scope) primary branch into the `top_levels`
    fallback under test."""
    reference = pl.DataFrame(
        {
            "vehicle_group": ["G1"] * 995 + ["G2"] * 5,
            "exposure_years": [0.001] * 995 + [100.0] * 5,
        }
    )
    context = ValidationContext(
        reference_tables={},
        reference_frames={},
        reference_profile=_profiled(reference, []),
    )
    current = pl.DataFrame({"vehicle_group": ["G3"] * 10})  # both G1 and G2 vanish

    outcome = run(
        "vanished_level",
        {"t": current},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert outcome.offending_sample == ("G2",), (
        "judged on count, G1 (99.5 % of rows) would be the material one and G2 (0.5 % of "
        "rows) would be filtered out as noise — the reverse of the exposure-correct answer"
    )


@pytest.mark.req("FR-DATA-24")
def test_vr_dst_6_mean_shift_is_measured_in_standard_errors() -> None:
    """VR-DST-6. The same 2 % move means different things on ten million observations and
    on four hundred; expressing the threshold in sampling noise makes one setting right for
    both."""
    reference = pl.DataFrame({"premium": [100.0 + (i % 20) for i in range(1000)]})
    context = ValidationContext(
        reference_tables={}, reference_frames={}, reference_profile=_profiled(reference)
    )
    moved = reference.with_columns(pl.col("premium") + 5)
    outcome = run(
        "mean_shift",
        {"t": moved},
        context=context,
        target={"table": "t", "column": "premium"},
    )
    assert outcome.violating_rows == 1
    assert outcome.measured["standard_errors"] > 5

    assert (
        run(
            "mean_shift",
            {"t": reference},
            context=context,
            target={"table": "t", "column": "premium"},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-24")
def test_vr_dst_7_target_rate_shift() -> None:
    """VR-DST-7 — the rule an actuary looks at first, and the one most likely to be a real
    finding rather than a data fault."""
    reference = pl.DataFrame(
        {
            "exposure_years": [1.0] * 1000,
            "claim_count": [1] * 100 + [0] * 900,
            "claim_amount_minor": [250_000] * 100 + [0] * 900,
        }
    )
    context = ValidationContext(reference_tables={}, reference_frames={"t": reference})
    worse = pl.DataFrame(
        {
            "exposure_years": [1.0] * 1000,
            "claim_count": [1] * 150 + [0] * 850,
            "claim_amount_minor": [250_000] * 150 + [0] * 850,
        }
    )
    outcome = run(
        "target_rate_shift",
        {"t": worse},
        context=context,
        params={"metric": "frequency", "max_shift_fraction": 0.15},
    )
    assert outcome.violating_rows == 1
    assert outcome.measured["shift"] == pytest.approx(0.5)

    assert (
        run(
            "target_rate_shift",
            {"t": reference},
            context=context,
            params={"metric": "burning_cost"},
        ).violating_rows
        == 0
    )


@pytest.mark.req("FR-DATA-24")
def test_vr_dst_8_mix_shift_is_on_exposure_not_row_counts() -> None:
    """VR-DST-8, and the distinction is the whole rule.

    Both frames hold the same number of rows per level, so a PSI over row counts is zero.
    The exposure behind those rows has fallen tenfold for one level — every rate depending
    on that mix has moved, and only the exposure-weighted PSI sees it.
    """
    reference = pl.DataFrame(
        {
            "vehicle_group": ["G1"] * 500 + ["G2"] * 500,
            "exposure_years": [1.0] * 1000,
            "claim_count": [0] * 1000,
            "claim_amount_minor": [0] * 1000,
        }
    )
    same_rows_less_exposure = reference.with_columns(
        pl.when(pl.col("vehicle_group") == "G2")
        .then(0.1)
        .otherwise(pl.col("exposure_years"))
        .alias("exposure_years")
    )
    context = ValidationContext(
        reference_tables={},
        reference_frames={},
        reference_profile=_profiled(reference, ["vehicle_group"]),
    )

    counts_only = run(
        "psi_column",
        {"t": same_rows_less_exposure},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert counts_only.measured["psi"] == pytest.approx(0.0, abs=1e-9)

    on_exposure = run(
        "mix_shift_exposure",
        {"t": same_rows_less_exposure},
        context=context,
        target={"table": "t", "column": "vehicle_group"},
    )
    assert on_exposure.violating_rows == 1
    assert on_exposure.measured["exposure_psi"] > 0.10


# -- the catalogue as a whole ----------------------------------------------------------


@pytest.mark.req("FR-DATA-19")
def test_no_check_passes_when_it_has_nothing_to_check() -> None:
    """FR-DATA-19: a rule that cannot run is an `error` or a `skip`, never a `pass`.

    Every registered check, run against a frame holding none of what it needs. A check that
    silently passes when its column is absent is worse than no check, because it is
    mistaken for coverage.
    """
    barren = pl.DataFrame({"unrelated": [1, 2, 3]})
    #: `reject_rate` is exempt and correctly so: a version with no `_rejected` table had
    #: nothing quarantined, and reporting that as a pass is the right answer rather than a
    #: vacuous one. Named here so the exemption is a decision rather than a gap.
    legitimately_passes = {"reject_rate"}
    report = _probe(barren, column="absent", skip=legitimately_passes)

    passed = [r.rule_slug for r in report.results if r.outcome.value == "pass"]
    assert not passed, f"these checks passed with nothing to check: {passed}"


@pytest.mark.req("FR-DATA-19")
def test_no_check_condemns_the_data_when_it_has_no_configuration() -> None:
    """The other direction, and the one that went unnoticed for longer.

    Here the column **exists** and the rule carries no thresholds, domain or pattern — the
    state a half-configured rule set is in. `allowed_values` read the wrong parameter name,
    so its declared domain was always empty and it failed *every* row, naming as offenders
    the very values the author had allowed. Seeding freMTPL2 surfaced it.

    A vacuous fail is worse than a vacuous pass: it blocks a dataset rather than waving one
    through, and it reads exactly like a genuine finding.

    The first version of this test reused the absent-column frame above, so every check
    errored before it could condemn anything and the assertion never bit — which is why the
    column is present here and the two cases are separate tests.
    """
    populated = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(20)],
            "value": [f"V{i % 4}" for i in range(20)],
            "exposure_years": [1.0] * 20,
            "claim_count": [0] * 20,
            "claim_amount_minor": [0] * 20,
        }
    )
    #: Checks that legitimately report on an unconfigured rule, each for a stated reason.
    expected = {
        # No `_rejected` table means nothing was quarantined — a real pass, not a vacuous
        # one, and it is asserted in the test above.
        "reject_rate",
        # A whole-table shape check: with nothing declared, every column present is by
        # definition undeclared. Reporting that is the point of the rule.
        "no_unexpected_columns",
    }
    report = _probe(populated, column="value", skip=expected)

    condemned = [
        r.rule_slug for r in report.results if r.outcome.value in ("fail", "warn")
    ]
    assert not condemned, (
        f"these checks condemned the data with no configuration: {condemned}. A check "
        "whose thresholds, domain or pattern are absent must skip, not refuse a dataset."
    )


def _probe(frame: pl.DataFrame, *, column: str, skip: set[str]) -> Any:
    """Run every registered check against one frame with an otherwise empty rule."""
    entries = tuple(
        RuleSetEntry(
            rule=ValidationRule(
                id=uuid4(),
                slug=f"probe-{name.replace('_', '-')}",
                version=1,
                layer=ValidationLayer.STRUCTURAL,
                check=name,
                severity=Severity.FAIL,
                target={"table": "t", "column": column},
                # The sql probe needs a query to be a query at all; it references the
                # target column so it shares the fate of every other check here.
                params={"query": f"SELECT count(*) FROM t WHERE {column} IS NULL"},
            )
        )
        for name in sorted(CHECKS)
        if name not in skip
    )
    report = run_validation(
        {"t": frame},
        ValidationRuleSet(id=uuid4(), slug="probe", version=1, entries=entries),
        dataset_version_id=uuid4(),
    )
    assert len(report.results) == len(CHECKS) - len(skip)
    return report
