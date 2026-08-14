"""Preparation recipes (`01` §3.2, FR-DATA-9..14)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import polars as pl
import pytest

from pricing_core.data.expressions import (
    ExpressionError,
    compile_expression,
    referenced_columns,
)
from pricing_core.data.prepare import (
    STEP_TYPES,
    RecipeError,
    apply_recipe,
    attach_claims,
    explode_period,
    pseudonymise,
)

# -- FR-DATA-9: exactly the declared step types --------------------------------------------


@pytest.mark.req("FR-DATA-9")
def test_the_declared_step_types_are_exactly_the_fifteen_the_spec_names() -> None:
    assert {
        "rename", "cast", "parse_date", "trim_whitespace", "normalise_case", "map_values",
        "fill_null", "derive_expression", "filter_rows", "deduplicate", "join_table",
        "derive_exposure", "explode_period", "attach_claims", "pseudonymise",
    } == STEP_TYPES


@pytest.mark.req("FR-DATA-9")
def test_an_undeclared_step_is_refused_not_ignored() -> None:
    """Negative: a step that silently does nothing is worse than one that fails, because
    the version it produces looks prepared."""
    with pytest.raises(RecipeError, match="not one of the declared step types"):
        apply_recipe({"t": pl.DataFrame({"a": [1]})}, [{"step": "run_python"}])


@pytest.mark.req("FR-DATA-9")
def test_steps_apply_in_order_each_seeing_the_last() -> None:
    frame = pl.DataFrame({"Gross Premium": ["  100 ", " 200 "]})
    result = apply_recipe(
        {"t": frame},
        [
            {"step": "rename", "params": {"columns": {"Gross Premium": "premium"}}},
            {"step": "trim_whitespace", "params": {"columns": ["premium"]}},
            {"step": "cast", "params": {"columns": {"premium": "int"}}},
        ],
    )
    assert result.tables["t"].get_column("premium").to_list() == [100, 200]
    assert [s["step"] for s in result.stats["steps"]] == ["rename", "trim_whitespace", "cast"]


# -- FR-DATA-10: the restricted expression grammar -------------------------------------------


@pytest.mark.req("FR-DATA-10")
def test_arithmetic_and_conditionals_are_permitted() -> None:
    frame = pl.DataFrame({"premium": [100.0, 200.0], "exposure": [1.0, 0.5]})
    derived = frame.with_columns(
        compile_expression("premium / exposure").alias("rate"),
        compile_expression("premium if exposure > 0.75 else 0").alias("annual_only"),
    )
    assert derived.get_column("rate").to_list() == [100.0, 400.0]
    assert derived.get_column("annual_only").to_list() == [100.0, 0.0]


@pytest.mark.req("FR-DATA-10")
@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('ls')",
        "open('/etc/passwd').read()",
        "premium.__class__",
        "[x for x in premium]",
        "(lambda: 1)()",
        "eval('1')",
        "premium[0]",
        "f'{premium}'",
    ],
)
def test_anything_outside_the_grammar_is_refused(expression: str) -> None:
    """FR-DATA-10: no network, no filesystem, no builtins.

    The property is not that these strings were blacklisted — it is that the expression is
    *translated* rather than evaluated, so only what the translator can build exists. Each
    of these fails on a node type the grammar does not admit.
    """
    with pytest.raises((ExpressionError, SyntaxError)):
        compile_expression(expression)


@pytest.mark.req("FR-DATA-10")
def test_statistical_functions_are_excluded() -> None:
    """FR-DATA-10 excludes them: a preparation step that could take a mean over the column
    it derives would make the result depend on which rows the extract happened to hold."""
    with pytest.raises(ExpressionError, match="not an allowed function"):
        compile_expression("mean(premium)")


@pytest.mark.req("FR-DATA-10")
def test_referenced_columns_are_reported_for_lineage() -> None:
    assert referenced_columns("round(premium / exposure) + abs(adjustment)") == {
        "premium", "exposure", "adjustment",
    }


# -- FR-DATA-11: exposure is preserved exactly ------------------------------------------------


@pytest.mark.req("FR-DATA-11")
def test_splitting_a_period_preserves_total_exposure_exactly() -> None:
    """The post-condition FR-DATA-11 requires, checked rather than assumed.

    Apportioning with floats loses fractions of a policy-year per split; across a million
    policies that is a visible error in every frequency denominator.
    """
    frame = pl.DataFrame(
        {
            "policy_id": ["P1"],
            "exposure_start": [date(2026, 1, 1)],
            "exposure_end": [date(2027, 1, 1)],
            "exposure_years": [1.0],
        }
    )
    exploded = explode_period(frame, boundaries=[date(2026, 7, 1)])

    assert exploded.height == 2
    total = sum(Decimal(str(v)) for v in exploded.get_column("exposure_years").to_list())
    assert total == Decimal("1.0")


@pytest.mark.req("FR-DATA-11")
def test_an_awkward_split_still_sums_exactly() -> None:
    """A third of a year does not divide cleanly; the last fragment absorbs the remainder."""
    frame = pl.DataFrame(
        {
            "policy_id": ["P1"],
            "exposure_start": [date(2026, 1, 1)],
            "exposure_end": [date(2026, 12, 31)],
            "exposure_years": [0.997],
        }
    )
    exploded = explode_period(
        frame, boundaries=[date(2026, 4, 15), date(2026, 8, 3), date(2026, 11, 27)]
    )
    total = sum(Decimal(str(v)) for v in exploded.get_column("exposure_years").to_list())
    assert exploded.height == 4
    assert total == Decimal("0.997")


@pytest.mark.req("FR-DATA-11")
def test_a_row_with_no_boundary_inside_it_is_untouched() -> None:
    frame = pl.DataFrame(
        {
            "policy_id": ["P1"],
            "exposure_start": [date(2026, 1, 1)],
            "exposure_end": [date(2026, 6, 1)],
            "exposure_years": [0.42],
        }
    )
    assert explode_period(frame, boundaries=[date(2027, 1, 1)]).height == 1


# -- FR-DATA-12: linkage is reported, not silently dropped --------------------------------------


@pytest.mark.req("FR-DATA-12")
def test_claims_link_to_the_exposure_row_covering_the_loss() -> None:
    exposure = pl.DataFrame(
        {
            "policy_id": ["P1", "P1"],
            "exposure_start": [date(2026, 1, 1), date(2026, 7, 1)],
            "exposure_end": [date(2026, 7, 1), date(2027, 1, 1)],
        }
    )
    claims = pl.DataFrame(
        {"claim_id": ["C1", "C2"], "policy_id": ["P1", "P1"],
         "date_of_loss": [date(2026, 3, 1), date(2026, 9, 1)]}
    )
    result = attach_claims(exposure, claims)
    assert result.counts == {"linked": 2, "unlinked": 0, "multi_linked": 0}


@pytest.mark.req("FR-DATA-12")
def test_an_unlinked_claim_is_returned_not_dropped() -> None:
    """Negative: a claim that fails to link is the most important row in the file — either
    a data error or a policy the exposure table does not know about."""
    exposure = pl.DataFrame(
        {"policy_id": ["P1"], "exposure_start": [date(2026, 1, 1)],
         "exposure_end": [date(2026, 7, 1)]}
    )
    claims = pl.DataFrame(
        {"claim_id": ["C1"], "policy_id": ["UNKNOWN"], "date_of_loss": [date(2026, 3, 1)]}
    )
    result = attach_claims(exposure, claims)
    assert result.counts["unlinked"] == 1
    assert result.unlinked.get_column("claim_id").to_list() == ["C1"]


@pytest.mark.req("FR-DATA-12")
def test_a_loss_on_a_renewal_date_belongs_to_the_new_term() -> None:
    """The period is half-open, matching how the policy was actually in force."""
    exposure = pl.DataFrame(
        {
            "policy_id": ["P1", "P1"],
            "exposure_start": [date(2026, 1, 1), date(2026, 7, 1)],
            "exposure_end": [date(2026, 7, 1), date(2027, 1, 1)],
        }
    )
    claims = pl.DataFrame(
        {"claim_id": ["C1"], "policy_id": ["P1"], "date_of_loss": [date(2026, 7, 1)]}
    )
    result = attach_claims(exposure, claims)
    assert result.counts["linked"] == 1
    assert result.linked.get_column("exposure_start").to_list() == [date(2026, 7, 1)]


@pytest.mark.req("FR-DATA-12")
def test_a_claim_table_without_an_identifier_is_refused() -> None:
    """Negative: without one, unlinked claims cannot be reported individually."""
    with pytest.raises(RecipeError, match="identifying column"):
        attach_claims(
            pl.DataFrame({"policy_id": ["P1"], "exposure_start": [date(2026, 1, 1)],
                          "exposure_end": [date(2027, 1, 1)]}),
            pl.DataFrame({"policy_id": ["P1"], "date_of_loss": [date(2026, 3, 1)]}),
        )


# -- FR-DATA-13: pseudonymisation ----------------------------------------------------------------


@pytest.mark.req("FR-DATA-13")
def test_the_same_customer_maps_to_the_same_token_across_versions() -> None:
    """What makes longitudinal analysis possible without holding the identity."""
    first = pseudonymise(
        pl.DataFrame({"customer_id": ["A", "B"]}), column="customer_id", key="ws-key"
    )
    second = pseudonymise(
        pl.DataFrame({"customer_id": ["B", "A"]}), column="customer_id", key="ws-key"
    )
    assert first.get_column("customer_id").to_list() == list(
        reversed(second.get_column("customer_id").to_list())
    )


@pytest.mark.req("FR-DATA-13")
def test_a_different_workspace_key_gives_a_different_token() -> None:
    """The token is meaningless outside the workspace that produced it."""
    a = pseudonymise(pl.DataFrame({"customer_id": ["A"]}), column="customer_id", key="ws-1")
    b = pseudonymise(pl.DataFrame({"customer_id": ["A"]}), column="customer_id", key="ws-2")
    assert a.get_column("customer_id")[0] != b.get_column("customer_id")[0]


@pytest.mark.req("FR-DATA-13")
def test_the_original_identifier_does_not_survive() -> None:
    tokenised = pseudonymise(
        pl.DataFrame({"customer_id": ["alice@example.com"]}), column="customer_id", key="k"
    )
    assert "alice" not in tokenised.get_column("customer_id")[0]


@pytest.mark.req("FR-DATA-13")
def test_pseudonymising_without_a_key_is_refused() -> None:
    """Negative: a keyless hash is reversible by anyone who can guess the identifier space,
    and customer ids are guessable."""
    with pytest.raises(RecipeError, match="workspace key"):
        pseudonymise(pl.DataFrame({"customer_id": ["A"]}), column="customer_id", key="")


# -- FR-DATA-14: a recipe is replayable -----------------------------------------------------


@pytest.mark.req("FR-DATA-14")
def test_replaying_a_recipe_reproduces_the_same_parquet_bytes() -> None:
    """FR-DATA-14: `replay(recipe, source_bytes) == stored version`, byte-for-byte on the
    parquet content hash, given pinned library versions.

    This is what makes a Preparation Recipe *evidence* rather than a description. A
    reviewer disputing a figure can re-derive the dataset from the source file and the
    recipe and get the identical artifact — and if they cannot, one of the two is wrong,
    which is exactly what they need to know.
    """
    import hashlib
    import io

    source = pl.DataFrame(
        {
            "Policy ID": ["P1", "P2", "P3", "P2"],
            "Gross Premium": ["  100 ", " 200 ", "300", " 200 "],
            "Exposure": [1.0, 0.5, 0.25, 0.5],
        }
    )
    recipe = [
        {"step": "rename", "params": {"columns": {"Policy ID": "policy_id",
                                                  "Gross Premium": "premium",
                                                  "Exposure": "exposure_years"}}},
        {"step": "trim_whitespace", "params": {"columns": ["premium"]}},
        {"step": "cast", "params": {"columns": {"premium": "int"}}},
        {"step": "deduplicate", "params": {"columns": ["policy_id"]}},
        {"step": "derive_expression",
         "params": {"column": "rate", "expression": "premium / exposure_years"}},
        {"step": "filter_rows", "params": {"expression": "exposure_years > 0.3"}},
    ]

    def run_and_hash() -> str:
        result = apply_recipe({"t": source}, recipe)
        buffer = io.BytesIO()
        result.tables["t"].write_parquet(buffer, compression="uncompressed")
        return hashlib.sha256(buffer.getvalue()).hexdigest()

    first, second = run_and_hash(), run_and_hash()
    assert first == second


@pytest.mark.req("FR-DATA-14")
def test_a_changed_recipe_produces_a_different_artifact() -> None:
    """Negative: replayability is only meaningful if the recipe actually determines the
    result. If any recipe gave the same bytes, the guarantee would be vacuous."""
    import hashlib
    import io

    source = pl.DataFrame({"premium": [100, 200], "exposure_years": [1.0, 0.5]})

    def run_and_hash(recipe: list[dict]) -> str:
        result = apply_recipe({"t": source}, recipe)
        buffer = io.BytesIO()
        result.tables["t"].write_parquet(buffer, compression="uncompressed")
        return hashlib.sha256(buffer.getvalue()).hexdigest()

    with_filter = run_and_hash([{"step": "filter_rows",
                                 "params": {"expression": "exposure_years > 0.75"}}])
    without = run_and_hash([{"step": "filter_rows",
                             "params": {"expression": "exposure_years > 0"}}])
    assert with_filter != without
