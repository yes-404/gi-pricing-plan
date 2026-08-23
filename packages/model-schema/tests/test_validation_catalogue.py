"""The catalogue against `01` §4.4, which is the only place these 38 rules are named."""

from __future__ import annotations

import pytest

from model_schema import BUILTIN_RULES, Severity, ValidationLayer, builtin_rule


@pytest.mark.req("FR-DATA-16")
def test_the_catalogue_holds_every_rule_01_section_4_4_names() -> None:
    """Counts per layer, from the four tables at `01` lines 361-413.

    Asserted as counts *and* as ids because a count alone passes if a rule is duplicated
    and another is missing — which is exactly the failure a hand-transcribed table of 38
    rows produces.
    """
    per_layer = {
        ValidationLayer.STRUCTURAL: 9,
        ValidationLayer.REFERENTIAL: 5,
        ValidationLayer.ACTUARIAL_SANITY: 16,
        ValidationLayer.DISTRIBUTIONAL: 8,
    }
    assert len(BUILTIN_RULES) == sum(per_layer.values()) == 38
    for layer, count in per_layer.items():
        got = [r.catalogue_id for r in BUILTIN_RULES.values() if r.layer is layer]
        assert len(got) == count, f"{layer}: {got}"

    prefixes = {"STR": 9, "REF": 5, "ACT": 16, "DST": 8}
    for prefix, count in prefixes.items():
        expected = {f"VR-{prefix}-{n}" for n in range(1, count + 1)}
        assert expected <= set(BUILTIN_RULES), sorted(expected - set(BUILTIN_RULES))


@pytest.mark.req("FR-DATA-16")
def test_a_catalogue_id_is_its_own_key_and_its_layer() -> None:
    for key, rule in BUILTIN_RULES.items():
        assert key == rule.catalogue_id
        assert rule.layer.value.startswith(
            {"STR": "struct", "REF": "refer", "ACT": "actuar", "DST": "distrib"}[
                key.split("-")[1]
            ]
        )


@pytest.mark.req("FR-DATA-16")
def test_slugs_are_unique_and_match_the_rule_slug_pattern() -> None:
    """`ValidationRule.slug` is `^[a-z0-9][a-z0-9-]{1,62}$` and a seeded row uses it.

    A duplicate slug would collide on `uq_validation_rule_version` at seed time — in the
    migration, on a live database, which is the worst place to discover it.
    """
    import re

    slugs = [rule.slug for rule in BUILTIN_RULES.values()]
    assert len(set(slugs)) == len(slugs)
    for slug in slugs:
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", slug), slug


@pytest.mark.req("FR-DATA-16")
def test_every_severity_is_warn_or_fail() -> None:
    """`Severity` has exactly two members; the committed JSON Schema claims three.

    Task 2 resolves that divergence by generating the schema. This test is what stops it
    coming back through the catalogue.
    """
    assert {r.severity for r in BUILTIN_RULES.values()} <= {Severity.WARN, Severity.FAIL}


@pytest.mark.req("FR-DATA-16")
def test_an_unknown_catalogue_id_is_refused_by_name() -> None:
    with pytest.raises(ValueError, match="VR-STR-99"):
        builtin_rule("VR-STR-99")


@pytest.mark.req("FR-DATA-16")
def test_a_known_catalogue_id_returns_its_rule() -> None:
    """Beside the refusal, because a refusal test alone passes if the accessor always raises."""
    rule = builtin_rule("VR-STR-1")
    assert rule.slug == "column-presence"
    assert rule.check == "column_presence"
    assert rule.severity is Severity.FAIL
