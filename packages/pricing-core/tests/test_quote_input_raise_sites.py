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
import shutil
from pathlib import Path
from typing import Any

import polars as pl
import pytest
from test_rating_runtime import _gbm_model_payload, _rate_table_payload, _train_tiny_booster
from test_rating_score import _algorithm_payload, _ctx, _version

from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ArtifactResolver, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import _batch_error_code, score_batch, score_one
from pricing_core.safe_error import CodedError

_SENTINEL = "SENTINEL-quote-input-3c9d0a17"
_BIG = 987654321

#: The whole package, by glob: a raise site added in any pricing_core module is counted by
#: default (maintainer, 2026-09-29, Q889-a). Keys below are paths relative to it.
_SRC = Path(__file__).resolve().parents[1] / "src" / "pricing_core"
#: Files under `_SRC` the census leaves out, each with why. Empty: none needs leaving out.
_EXCLUDED: dict[str, str] = {}

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

#: Every other raise site under `pricing_core/rating` (a `_raise_named` call, a `CodedError(`
#: construction, or a `_model_call_failure(` call), with why it is input-free.
_INPUT_FREE = {
    ("rating/score.py", "_check_purpose_mount"): 1,  # `purpose` is a closed set of literals
    ("rating/score.py", "_check_billing_surface"): 1,  # names the constant billing-surface keys
    # FR-213's refusal: names the declared step outputs the inputs collide with, never a value
    ("rating/score.py", "_check_no_shadowed_produced_names"): 1,
    # FR-221 as_at refusal: step id and field name only, never the value
    # (test_rating_lookup_as_at.py drives it with a sentinel)
    ("rating/score.py", "_check_as_at_values"): 1,
    ("rating/score.py", "_check_lookup_misses"): 2,  # step ids only
    ("rating/score.py", "_reraise_engine_failure"): 1,  # engine error is reduced to its type name
    # RL-1346's refusal: clause, rung names and minor-unit differences from `ladder_violations`
    # (`test_the_ladder_refusal_never_carries_a_quote_input` drives it with a sentinel).
    ("rating/score.py", "build_scoring_result"): 1,
    ("rating/score.py", "score_one"): 1,  # a fixed sentence about a missing rating_version_ref
    ("rating/score.py", "_raise_named"): 1,  # the constructor helper itself (`from None`)
    # The model-call sentinel re-raised as a coded error: its text is `MODEL_CALL_FAILED: ` plus a
    # static sentence built in `runtime.py`, never a model's or the engine's own error text.
    ("rating/score.py", "_check_model_call_sentinel"): 1,
    ("rating/runtime.py", "_load_boosters"): 1,  # step id and ref string, no quote
    ("rating/runtime.py", "_check_graph_matches_inlined_algorithm"): 1,  # a node id
    # `_model_call_failure`: step id and the pinned model_type; and, for a Peril Structure pin
    # (PL-1461 Task 4), step id and ref string, no quote; the refusal text of `_ModelCallRefusal`;
    # and, for a GLM or peril component scorer failure (PL-1464, the 2026-10-10 03:20:34 BST ruling),
    # the error code and the ref string only, through the one shared `except`:
    # f"{exc.code}: {ref_str} could not be scored for this quote (FR-255)", never the model's
    # text (`test_a_glm_failure_reports_its_code_and_never_the_models_text` drives it).
    ("rating/runtime.py", "handler"): 3,
    ("rating/compile.py", "check_step_refs_pinned"): 1,  # step id and ref string, no quote
    ("rating/compile.py", "compile_bundle"): 5,  # artifact-level (compile time), no quote
    # PL-1471 (SL-1472), each at compile time over pinned artifacts, never a quote:
    # model ref, objective ref and its status
    ("rating/compile.py", "_refuse_unapproved_objectives"): 1,
    # rate table ref, key name and Factor ref
    ("rating/compile.py", "_refuse_control_factor_keys"): 1,
    # model ref, a fitted feature name and the Factor's slug@version
    ("rating/compile.py", "_refuse_control_factor_model_calls"): 1,
    ("rating/compile.py", "_check_peril_model_calls"): 1,  # :815 step id, ref, names
    ("rating/compile.py", "_resolve_peril_components"): 2,  # :839, :851 refs, peril, status
    # mount point, port and value names (WK-1250 Slice 2)
    ("rating/compile.py", "_refuse_mount_port_type_mismatch"): 1,
    ("rating/compile.py", "_raise_named"): 1,  # the constructor helper itself (`from None`)
    # WK-1250 Slice 2 (SL-1340), `inline.py`: each at compile and load time over pinned artifacts,
    # never a quote. The text names a mount point, a port or a step id (authored identifiers), an
    # artifact ref, or the first graph-invariant message (step ids and value names).
    ("rating/inline.py", "_raise_named"): 1,  # the constructor helper itself (`from None`)
    ("rating/inline.py", "_port_mapping"): 4,  # mount point and port names
    ("rating/inline.py", "_inline_one"): 1,  # mount point and port names
    ("rating/inline.py", "mounted_fragments"): 3,  # mount point, artifact ref
    ("rating/inline.py", "inline_mounts"): 3,  # mount point, artifact ref, namespaced names
}
#: The functions holding the quote-input sites, whose count must equal the cases.
_INPUT_SITES = {("rating/score.py", "_validate_inputs"), ("rating/score.py", "_row_to_ctx")}


#: `PlatformError` cannot be raised in this package (import-linter), so a hit is a violation.
_SITE_NAMES = ("_raise_named", "CodedError", "_model_call_failure", "PlatformError")


def _source_files() -> list[Path]:
    return sorted(
        p for p in _SRC.rglob("*.py")
        if "__pycache__" not in p.parts and p.relative_to(_SRC).as_posix() not in _EXCLUDED
    )


def _raise_sites() -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for path in _source_files():
        name = path.relative_to(_SRC).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))

        def visit(node: ast.AST, function: str, name: str = name) -> None:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                function = node.name
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in _SITE_NAMES
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


def _guard_against(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, replace: tuple[str, str]
) -> None:
    """Run the guard against a copy of the package with `replace[0]` swapped for `replace[1]`
    in `rating/score.py`."""
    copy_root = tmp_path / "pricing_core"
    shutil.copytree(_SRC, copy_root, ignore=shutil.ignore_patterns("__pycache__"))
    target = copy_root / "rating" / "score.py"
    source = target.read_text(encoding="utf-8")
    assert replace[0] in source
    target.write_text(source.replace(*replace, 1), encoding="utf-8")
    monkeypatch.setattr(f"{__name__}._SRC", copy_root)


@pytest.mark.req("NFR-499")
def test_the_guard_counts_an_injected_raise_site_outside_the_input_functions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Positive control: a new `_raise_named` in a listed input-free function fails the guard."""
    _guard_against(monkeypatch, tmp_path, (
        "def _check_billing_surface(ctx: QuoteContext) -> None:\n",
        "def _check_billing_surface(ctx: QuoteContext) -> None:\n"
        '    _raise_named("INPUT_CONTRACT_VIOLATION", f"leaks {ctx.inputs!r}")\n',
    ))
    with pytest.raises(AssertionError, match="not accounted for"):
        test_every_quote_input_raise_site_has_a_sentinel_case()


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize(
    ("function_head", "label"),
    [
        ("def _row_to_ctx(row: Mapping[str, Any]) -> QuoteContext:\n", "_row_to_ctx"),
        (
            "def _validate_inputs(algorithm: RatingAlgorithm, "
            "inputs: Mapping[str, Any]) -> None:\n",
            "_validate_inputs",
        ),
    ],
)
def test_the_guard_counts_an_injected_raise_site_inside_an_input_function(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, function_head: str, label: str
) -> None:
    """Positive control on the functions that hold the quote-input sites: one more site there,
    with no case added, fails the guard on the count of sites against cases."""
    _guard_against(monkeypatch, tmp_path, (
        function_head,
        function_head + '    _raise_named("INPUT_CONTRACT_VIOLATION", "a new site")\n',
    ))
    with pytest.raises(AssertionError, match="quote-input raise sites"):
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


@pytest.mark.req("NFR-499")
async def test_a_batch_error_row_is_byte_identical_to_the_pre_change_form_minus_the_value() -> None:
    """`origin/main`'s `_batch_error_code` (`score.py:887-891`) returned `(code, rest)` for a
    `CODE: message` text, so an error row carried `error_code = "INPUT_CONTRACT_VIOLATION"` and
    `error_message` = the message half. For the maximum site that message was `input
    'driver_age'=987654321 is above the declared maximum 99`; the value is the only thing
    removed. The code is still parsed out, and it is still the contract (FR-403)."""
    bundle = await _bundle()
    inputs = {**_VALID, "driver_age": _BIG}
    out = score_batch(bundle, pl.DataFrame([_row(inputs, "2026-09-01")]).lazy()).collect()
    row = out.to_dicts()[0]
    assert row["error_code"] == "INPUT_CONTRACT_VIOLATION"
    assert row["error_message"] == "input 'driver_age' is above the declared maximum 99"
    assert _batch_error_code(CodedError("INPUT_CONTRACT_VIOLATION: a message")) == (
        "INPUT_CONTRACT_VIOLATION",
        "a message",
    )



def _refusal_bundle_payload() -> Any:
    from test_rating_ladder_exact import _clamp_variant

    return _clamp_variant({"min": "min_premium_minor"}, "office_premium_minor >= 0")


async def _assert_the_ladder_refusal_is_input_free() -> None:
    """An authored R0 quote (the clamp binds, its condition says it does not) with a sentinel as
    its `quote_id`, through `score_one` and `score_batch`: the code is there, the sentinel not."""
    from test_rating_ladder_exact import _CLAMP_INPUTS, _compile_payload, _context

    bundle = await _compile_payload(_refusal_bundle_payload())
    ctx = _context(**_CLAMP_INPUTS).model_copy(update={"quote_id": _SENTINEL})
    with pytest.raises(ValueError, match="LADDER_RECONCILIATION_FAILED") as caught:
        await score_one(bundle, ctx)
    assert _SENTINEL not in str(caught.value)
    row = {
        "quote_id": _SENTINEL, "purpose": "new_business", "effective_date": "2026-09-01",
        "rating_version_ref": str(ctx.options.rating_version_ref),  # type: ignore[union-attr]
        **_CLAMP_INPUTS,
    }
    out = score_batch(bundle, pl.DataFrame([row]).lazy()).collect().to_dicts()[0]
    assert out["error_code"] == "LADDER_RECONCILIATION_FAILED"
    assert _SENTINEL not in out["error_message"]


@pytest.mark.req("NFR-499")
async def test_the_ladder_refusal_never_carries_a_quote_input() -> None:
    await _assert_the_ladder_refusal_is_input_free()


@pytest.mark.req("NFR-499")
async def test_the_ladder_refusal_check_fails_on_a_message_that_carries_an_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Red on broken input: a refusal message that carries a quote input fails the check above."""
    from pricing_core.rating import score as score_module

    monkeypatch.setattr(score_module, "ladder_violations", lambda *_: [f"R0: {_SENTINEL}"])
    with pytest.raises(AssertionError):
        await _assert_the_ladder_refusal_is_input_free()
