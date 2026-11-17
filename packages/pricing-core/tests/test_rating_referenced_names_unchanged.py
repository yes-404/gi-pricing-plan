"""#1712 S7c: `referenced_names` returns the same set as before `string_reads` was factored out.

The maintainer's condition on 683a3641: for every fixture algorithm, the new function equals
the old one. The old function below is the body of `referenced_names` at main 11ca1cd5
(`git show origin/main:packages/pricing-core/src/pricing_core/rating/references.py`), copied
as it was; only its helpers carry an `_OLD` prefix so they cannot shadow the new module's.
"""

from __future__ import annotations

import importlib
import json
import re
from collections.abc import Callable, Iterator, Mapping
from pathlib import Path
from typing import Any

import pytest

from pricing_core.rating.authored import EXPRESSION_FIELDS
from pricing_core.rating.references import referenced_names

# --- the old function, verbatim from main 11ca1cd5 (helpers renamed `_OLD_*` / `_old_*`) ------
_OLD_STRING = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
_OLD_NAME = re.compile(r"(?<![\w.$])([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*\()")
_OLD_KEYWORDS = frozenset({"true", "false", "null", "and", "or", "not", "in"})
_OLD_STAMPED_DATE = "effective_date"
_OLD_EVALUATED = frozenset(name for _, name in EXPRESSION_FIELDS)


def _old_names_in(text: str) -> set[str]:
    return {m for m in _OLD_NAME.findall(_OLD_STRING.sub(" ", text)) if m not in _OLD_KEYWORDS}


def _old_as_list(value: Any) -> list[str]:
    if value is None:
        return []
    return [str(v) for v in (value if isinstance(value, list) else [value])]


def _old_referenced_names(node: Mapping[str, Any]) -> frozenset[str]:
    """Declared `consumes` plus every name the node's evaluated fields read."""
    names = set(_old_as_list(node.get("consumes")))
    for field in _OLD_EVALUATED:
        value = node.get(field)
        if isinstance(value, Mapping):
            value = list(value.values())
        for text in [value] if isinstance(value, str) else value or []:
            if not isinstance(text, str):  # an absent clamp bound is None
                continue
            if field == "as_at" and text == _OLD_STAMPED_DATE:
                continue  # the quote's stamped date: FR-221 declares no one (FR-246 clarified)
            names |= _old_names_in(text)
    names |= set((node.get("feature_map") or {}).keys())
    return frozenset(names)


# --- the corpus: every algorithm the rating test fixtures and the 03 examples build ---------
#: (module, zero-argument builder) of every fixture in `tests/test_rating_*.py` that returns an
#: algorithm, a fragment or a mounted set; the builders needing arguments are listed with theirs.
_FIXTURES: list[tuple[str, str, dict[str, Any]]] = [
    ("test_rating_attribution", "_candidate_payload", {}),
    ("test_rating_compile", "valid_algorithm", {}),
    ("test_rating_compile_bundle", "valid_algorithm_payload", {}),
    ("test_rating_compile_bundle", "_fragment_payload", {}),
    ("test_rating_compile_bundle", "_mounted_payload", {}),
    ("test_rating_declared_reads", "_undeclared_clamp_payload", {}),
    ("test_rating_glm_expression_inputs", "_shared_input_algorithm", {}),
    ("test_rating_glm_model_call", "algorithm_payload", {}),
    ("test_rating_glm_model_call", "_area_algorithm", {}),
    ("test_rating_glm_numeric_term", "_algorithm", {}),
    ("test_rating_load_bundle_control_guard", "_algorithm", {}),
    ("test_rating_lookup_as_at", "_algo", {}),
    ("test_rating_peril_scoring", "_peril_algorithm", {}),
    ("test_rating_peril_scoring", "_scoring_algorithm", {}),
    ("test_rating_pin_membership", "_table_algo", {}),
    ("test_rating_pin_membership", "_lookup_algo", {}),
    ("test_rating_pin_membership", "_veh_payloads", {}),
    ("test_rating_purpose_mount", "_cancel_clamp_fragment_payload", {}),
    ("test_rating_runtime", "_algorithm_payload", {}),
    ("test_rating_runtime", "_algorithm_payload_with_constraint", {}),
    ("test_rating_runtime", "_mounted_payloads", {}),
    ("test_rating_score", "_algorithm_payload", {}),
    ("test_rating_score", "_table_and_lookup_payload", {}),
    ("test_rating_score_batch", "_decimal_output_algorithm_payload", {}),
    ("test_rating_compile", "_probe_algorithm", {"producer": "expression", "declared": "decimal"}),
    ("test_rating_glm_model_call", "_typed_outputs_algorithm",
     {"call_type": "glm", "output_type": "decimal"}),
    ("test_rating_column_collision", "algorithm", {"feature_map": {"a": "b"}}),
    ("test_rating_compile_completeness", "_algorithm", {"feature_map": {"a": "b"}}),
    ("test_rating_pin_membership", "_veh_algo", {"kind": "table", "ref": "rate_table:v@1"}),
]
_SPEC_03 = Path(__file__).resolve().parents[3] / "docs/specs/03-rating-engine.md"
_JSON_FENCE = re.compile(r"^```json\s+schema=\w+[^\n]*\n(.*?)^```", re.M | re.S)


def _nodes(value: Any) -> Iterator[dict[str, Any]]:
    """Every step or fragment-body node (a dict with a `step_id`) anywhere inside `value`."""
    if isinstance(value, dict):
        if "step_id" in value:
            yield value
        for inner in value.values():
            yield from _nodes(inner)
    elif isinstance(value, (list, tuple)):
        for inner in value:
            yield from _nodes(inner)


def _corpus() -> list[tuple[str, list[dict[str, Any]]]]:
    corpus: list[tuple[str, list[dict[str, Any]]]] = []
    for module, name, kwargs in _FIXTURES:
        built: Callable[..., Any] = getattr(importlib.import_module(module), name)
        corpus.append((f"{module}.{name}", list(_nodes(built(**kwargs)))))
    for n, body in enumerate(_JSON_FENCE.findall(_SPEC_03.read_text()), start=1):
        corpus.append((f"03-rating-engine.md example {n}", list(_nodes(json.loads(body)))))
    return corpus


@pytest.mark.req("FR-246")
def test_referenced_names_returns_the_same_set_as_before_for_every_fixture_algorithm() -> None:
    corpus = _corpus()
    steps = 0
    for label, nodes in corpus:
        for node in nodes:
            steps += 1
            assert referenced_names(node) == _old_referenced_names(node), (label, node["step_id"])
    print(f"compared {len(corpus)} algorithms, {steps} steps")
    assert len(corpus) >= len(_FIXTURES) + 1 and steps > 100, "the corpus read empty"
