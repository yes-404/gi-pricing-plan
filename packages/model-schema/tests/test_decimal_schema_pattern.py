"""FR-10: a `Decimal` on the wire keeps its string pattern in every generated contract.

Pydantic 2.14 stopped putting `^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d*$` on the string branch of a
bare `Decimal`'s JSON Schema, which loosened the published, money-semantic contract
silently (#1314). Two guards, because the two Pydantic modes differ:

* the *validation* shape is `anyOf: [number, string, ...]` — recognisable in the committed
  `docs/contracts`, so that is walked directly;
* the *serialization* shape of a `Decimal` is a bare `{"type": "string"}`, which no walk can
  tell from any other string, so every `Decimal`-annotated field of every `model_schema`
  model is checked at the source, in both modes.
"""

import copy
import importlib
import json
import pkgutil
import typing
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

import model_schema
from model_schema.money import SchemaDecimal

CONTRACTS = Path(__file__).resolve().parents[3] / "docs" / "contracts"


def _string_branches(node: Any) -> list[dict[str, Any]]:
    """Every `{"type": "string"}` schema node under `node`, `$ref`s not followed."""
    found: list[dict[str, Any]] = []
    if isinstance(node, dict):
        if node.get("type") == "string":
            found.append(node)
        for value in node.values():
            found.extend(_string_branches(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_string_branches(value))
    return found


def _decimal_union_unpatterned(node: Any, path: str = "") -> list[str]:
    """Paths of `anyOf: [number, string]` unions whose string branch has no pattern."""
    bad: list[str] = []
    if isinstance(node, dict):
        any_of = node.get("anyOf")
        if isinstance(any_of, list):
            types = [b.get("type") for b in any_of if isinstance(b, dict)]
            if "number" in types and "string" in types:
                bad += [
                    f"{path}/anyOf"
                    for b in any_of
                    if b.get("type") == "string" and "pattern" not in b
                ]
        for key, value in node.items():
            bad += _decimal_union_unpatterned(value, f"{path}/{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            bad += _decimal_union_unpatterned(value, f"{path}/{i}")
    return bad


#: Number|string unions that are NOT a `Decimal` and so carry no pattern, by EXACT schema path
#: (`<contract file>/<path inside it>`, no wildcard). `DislocationMover.columns` holds the
#: portfolio's non-money factor values (a postcode, a vehicle age, a float density): its
#: `str | int | float | bool | None` is a free JSON scalar, so a Decimal pattern on its string
#: branch would refuse every non-numeric value. FR-10's scope is money, and a decimal column
#: arrives as a plain string by `_json_value`. Maintainer 2026-10-22, SL-1551 decimal guard (3).
_NOT_A_DECIMAL: frozenset[str] = frozenset(
    {
        "openapi/generated.json/components/schemas/DislocationMover"
        "/properties/columns/additionalProperties/anyOf"
    }
)


def _decimal_union_findings(
    docs: dict[str, Any], exempt: frozenset[str] = _NOT_A_DECIMAL
) -> tuple[list[str], list[str]]:
    """`(patternless unions not exempted, exemptions that no longer match a patternless union)`."""
    found = {f"{name}{p}" for name, doc in docs.items() for p in _decimal_union_unpatterned(doc)}
    return sorted(found - exempt), sorted(exempt - found)


def _committed_contracts() -> dict[str, Any]:
    files = sorted(CONTRACTS.glob("**/*.json"))
    assert files, "no contracts found: the test would pass vacuously"
    return {str(f.relative_to(CONTRACTS)): json.loads(f.read_text()) for f in files}


@pytest.mark.req("FR-10")
def test_committed_contracts_keep_the_pattern_on_every_decimal_union():
    docs = _committed_contracts()
    unions = sum(len(json.dumps(d).split('"type": "number"')) - 1 for d in docs.values())
    assert unions, "no number|string union found: the predicate no longer sees a Decimal"
    bad, stale = _decimal_union_findings(docs)
    assert not bad, f"Decimal string branch without its pattern: {bad}"
    assert not stale, f"exempted path no longer a patternless number|string union: {stale}"


@pytest.mark.req("FR-10")
def test_the_exemption_is_exact_a_patternless_decimal_elsewhere_stays_red():
    docs = copy.deepcopy(_committed_contracts())
    docs["openapi/generated.json"]["components"]["schemas"]["SomeMoneyShape"] = {
        "properties": {"amount": {"anyOf": [{"type": "number"}, {"type": "string"}]}}
    }
    bad, stale = _decimal_union_findings(docs)
    assert bad == [
        "openapi/generated.json/components/schemas/SomeMoneyShape/properties/amount/anyOf"
    ]
    assert not stale


@pytest.mark.req("FR-10")
def test_an_exemption_whose_path_vanished_fails_as_stale():
    docs = copy.deepcopy(_committed_contracts())
    columns = docs["openapi/generated.json"]["components"]["schemas"]["DislocationMover"][
        "properties"
    ]["columns"]
    columns["additionalProperties"] = {"type": "string"}
    bad, stale = _decimal_union_findings(docs)
    assert not bad
    assert stale == sorted(_NOT_A_DECIMAL)


def _models() -> list[type[BaseModel]]:
    for info in pkgutil.iter_modules(model_schema.__path__):
        importlib.import_module(f"model_schema.{info.name}")
    seen: dict[str, type[BaseModel]] = {}
    stack = list(BaseModel.__subclasses__())
    while stack:
        cls = stack.pop()
        stack.extend(cls.__subclasses__())
        if cls.__module__.startswith("model_schema.") and not cls.__name__.startswith("_"):
            seen[f"{cls.__module__}.{cls.__qualname__}"] = cls
    return list(seen.values())


def _mentions_decimal(annotation: Any) -> bool:
    if annotation is Decimal:
        return True
    return any(_mentions_decimal(a) for a in typing.get_args(annotation))


@pytest.mark.req("FR-10")
@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_every_decimal_field_schema_string_branch_carries_the_pattern(mode):
    checked = 0
    bad: list[str] = []
    for model in _models():
        try:
            props = model.model_json_schema(mode=mode).get("properties", {})  # type: ignore[arg-type]
        except Exception:
            continue
        fields = {n: f.annotation for n, f in model.model_fields.items()}
        fields |= {n: c.return_type for n, c in model.model_computed_fields.items()}
        for name, annotation in fields.items():
            if not _mentions_decimal(annotation):
                continue
            field = model.model_fields.get(name)
            prop = props.get((field.alias if field else None) or name)
            if prop is None:
                continue
            checked += 1
            bad += [
                f"{model.__name__}.{name}"
                for b in _string_branches(prop)
                if "pattern" not in b
            ]
    assert checked >= 15, f"only {checked} Decimal fields reached: the predicate went blind"
    assert not bad, f"{mode}: Decimal string branch without its pattern: {sorted(set(bad))}"


@pytest.mark.req("FR-10")
@pytest.mark.parametrize("good", ["12.30", "-0.5", "0", ".5", 7, Decimal("1.5")])
def test_schema_decimal_accepts_exact_values(good):
    assert TypeAdapter(SchemaDecimal).validate_python(good) == Decimal(str(good))


@pytest.mark.req("FR-10")
@pytest.mark.parametrize("bad", ["abc", "1.2.3", "--1", "+", "", "NaN-ish"])
def test_schema_decimal_refuses_non_decimal_strings(bad):
    with pytest.raises(ValidationError):
        TypeAdapter(SchemaDecimal).validate_python(bad)
