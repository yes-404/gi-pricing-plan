"""A coded error names the field and the constraint, never the value (NFR-499, RL-917).

`pricing_core.safe_error` keeps the text of a coded error (`CODE: message`) as it stands, so the
rule holds only while every raise site that can concern a quote input is input-free. This file
holds that: each such site has a case that plants a sentinel where the value would be, drives it
through `score_one` AND `score_batch`, and checks the sentinel is absent while the field and the
constraint are present. **A coverage guard** enumerates the raise sites by AST and fails when one
is added without a case, or without an entry in the input-free list below.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import polars as pl
import pytest
from test_rating_runtime import _gbm_model_payload, _rate_table_payload, _train_tiny_booster
from test_rating_score import _algorithm_payload, _ctx, _version

from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ArtifactResolver, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_batch, score_one

_SENTINEL = "SENTINEL-quote-input-3c9d0a17"
_BIG = 987654321

_SRC = Path(__file__).resolve().parents[1] / "src" / "pricing_core" / "rating"

#: The quote-input raise sites, one case each: the site's key, the input that trips it, the
#: fragments (field, constraint) the message must keep, and the values that must not appear.
#: `_row_to_ctx`'s site is reached only through `score_batch` (a row's `effective_date`).
_CASES: dict[str, tuple[dict[str, Any], tuple[str, ...], tuple[str, ...]]] = {
    "required": ({"driver_age": None}, ("'driver_age'", "is required"), ()),
    "bool": ({"flag": _SENTINEL}, ("'flag'", "must be bool"), ()),
    "int": ({"driver_age": _SENTINEL}, ("'driver_age'", "must be int"), ()),
    "decimal": ({"ratio": _SENTINEL}, ("'ratio'", "must be numeric"), ()),
    "string": ({"code": [_SENTINEL]}, ("'code'", "must be a string"), ()),
    "pattern": ({"code": _SENTINEL}, ("'code'", "does not match", "[A-Z]{3}"), ()),
    "date": ({"start": [_SENTINEL]}, ("'start'", "must be a date string"), ()),
    "enum": ({"channel": _SENTINEL}, ("'channel'", "is not in", "'direct'", "'broker'"), ()),
    "min": ({"driver_age": -_BIG}, ("'driver_age'", "declared minimum 17"), (str(_BIG),)),
    "max": ({"driver_age": _BIG}, ("'driver_age'", "declared maximum 99"), (str(_BIG),)),
    "effective_date": (
        {"effective_date": _SENTINEL},
        ("effective_date", "ISO-8601"),
        (),
    ),
}

#: Every other `_raise_named` site under `pricing_core/rating`, with why it is input-free.
_INPUT_FREE = {
    ("score.py", "_check_purpose_mount"): 1,  # `purpose` is a closed set of literals
    ("score.py", "_check_billing_surface"): 1,  # names the constant billing-surface keys
    ("score.py", "_check_lookup_misses"): 2,  # step ids only
    ("score.py", "_reraise_engine_failure"): 1,  # the engine error is reduced to its type name
    ("score.py", "score_one"): 1,  # a fixed sentence about a missing rating_version_ref
    ("compile.py", "compile_bundle"): 5,  # artifact-level (compile time), no quote is involved
}
#: The functions holding the quote-input sites, whose count must equal the cases.
_INPUT_SITES = {("score.py", "_validate_inputs"), ("score.py", "_row_to_ctx")}


def _raise_sites() -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for name in ("score.py", "compile.py"):
        tree = ast.parse((_SRC / name).read_text(encoding="utf-8"))

        def visit(node: ast.AST, function: str, name: str = name) -> None:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                function = node.name
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_raise_named"
            ):
                counts[(name, function)] = counts.get((name, function), 0) + 1
            for child in ast.iter_child_nodes(node):
                visit(child, function)

        visit(tree, "<module>")
    return counts


@pytest.mark.req("NFR-499")
def test_every_quote_input_raise_site_has_a_sentinel_case() -> None:
    sites = _raise_sites()
    input_sites = sum(count for key, count in sites.items() if key in _INPUT_SITES)
    assert input_sites == len(_CASES), (
        f"{input_sites} quote-input raise sites, {len(_CASES)} sentinel cases: a site was added "
        "or removed without a case (test_quote_input_raise_sites.py)"
    )
    others = {key: count for key, count in sites.items() if key not in _INPUT_SITES}
    assert others == _INPUT_FREE, (
        "a `_raise_named` site is not accounted for: give it a sentinel case, or list it in "
        f"_INPUT_FREE with why it is input-free. Found {others}"
    )


@pytest.mark.req("NFR-499")
def test_the_guard_counts_an_injected_raise_site(tmp_path: Path, monkeypatch) -> None:
    """Positive control: a new `_raise_named` in a listed function makes the guard fail."""
    source = (_SRC / "score.py").read_text(encoding="utf-8").replace(
        "def _check_billing_surface(ctx: QuoteContext) -> None:\n",
        "def _check_billing_surface(ctx: QuoteContext) -> None:\n"
        '    _raise_named("INPUT_CONTRACT_VIOLATION", f"leaks {ctx.inputs!r}")\n',
        1,
    )
    (tmp_path / "score.py").write_text(source, encoding="utf-8")
    (tmp_path / "compile.py").write_text((_SRC / "compile.py").read_text(encoding="utf-8"))
    monkeypatch.setattr(f"{__name__}._SRC", tmp_path)
    with pytest.raises(AssertionError, match="not accounted for"):
        test_every_quote_input_raise_site_has_a_sentinel_case()


def _algorithm() -> dict[str, Any]:
    payload = copy.deepcopy(_algorithm_payload())
    payload["input_contract"] += [
        {"name": "flag", "type": "bool", "nullable": False},
        {"name": "ratio", "type": "decimal", "nullable": False},
        {"name": "code", "type": "string", "nullable": False, "pattern": "^[A-Z]{3}$"},
        {"name": "start", "type": "date", "nullable": False},
    ]
    return payload


class _Resolver:
    def __init__(self) -> None:
        self._payloads: dict[str, dict[str, Any]] = {
            "rating_algorithm:score-fixture@1": _algorithm(),
            "rate_table:motor-expense@1": _rate_table_payload(),
            "model:motor-freq@1": _gbm_model_payload(_train_tiny_booster()),
        }

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payloads[str(ref)])


async def _bundle() -> CompiledBundle:
    resolver: ArtifactResolver = _Resolver()
    return load_bundle(await compile_bundle(_version(), resolver))


_VALID: dict[str, Any] = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
    "flag": True, "ratio": 1.5, "code": "ABC", "start": "2026-01-01",
}


def _row(inputs: dict[str, Any], effective_date: str) -> dict[str, Any]:
    ctx = _ctx(inputs=inputs)
    assert ctx.options is not None
    assert ctx.options.rating_version_ref is not None
    return {
        "quote_id": "Q1", "purpose": "new_business", "effective_date": effective_date,
        "rating_version_ref": str(ctx.options.rating_version_ref), **inputs,
    }


@pytest.mark.req("NFR-499")
async def test_the_baseline_case_scores_so_each_case_trips_only_its_own_site() -> None:
    bundle = await _bundle()
    result = await score_one(bundle, _ctx(inputs=_VALID))
    assert result.outcome == "quoted"


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("site", sorted(_CASES))
async def test_a_coded_input_error_names_the_field_and_constraint_and_never_the_value(
    site: str,
) -> None:
    overrides, keep, forbid = _CASES[site]
    bundle = await _bundle()
    effective_date = overrides.get("effective_date", "2026-09-01")
    inputs = {**_VALID, **{k: v for k, v in overrides.items() if k != "effective_date"}}
    forbidden = (_SENTINEL, *forbid)

    # `score_batch`: one row, so its column keeps the bad value's own type.
    frame = pl.DataFrame([_row(inputs, effective_date)]).lazy()
    out = score_batch(bundle, frame).collect().to_dicts()[0]
    assert out["outcome"] == "error"
    assert out["error_code"] == "INPUT_CONTRACT_VIOLATION", out
    message = out["error_message"]
    for fragment in keep:
        assert fragment in message, (site, message)
    for value in forbidden:
        assert value not in message, (site, message)

    # `score_one`: the single-quote path (the `/score` route's source of its 422 detail).
    if site != "effective_date":
        with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION") as caught:
            await score_one(bundle, _ctx(inputs=inputs))
        for fragment in keep:
            assert fragment in str(caught.value), (site, str(caught.value))
        for value in forbidden:
            assert value not in str(caught.value), (site, str(caught.value))
