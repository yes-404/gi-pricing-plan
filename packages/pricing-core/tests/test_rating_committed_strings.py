"""The committed rating strings, checked both ways (PL-1314 acceptance 10; RL-1312 "Stored data").

Every authored rating string committed in a fixture, an example, a bench script or the spec is
extracted and run through the allow-list, the division guard and the determinism and scale
checks. Every string a committed test expects to be accepted passes all of them, and every
deliberate negative fixture stays refused under the code its own test asserts.

The predicate is `_authored_strings` below: FD-1317's line-scoped regex over tracked text files,
plus an `ast` walk of every tracked `.py` file for a dict entry or keyword named `expr`,
`condition`, `key_expr` or `clamp_bounds`, plus a walk of every tracked `.json` file. A string
built by a helper, an f-string or a variable is not seen by it; the whole suite, which validates
every algorithm it builds, is the second instrument.

Out of scope: data-preparation `expression` strings, which `pricing_core.data.expressions` parses
under `02` §4.6 and the rating engine never sees (RL-1312).
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path

import pytest

from pricing_core.rating.compile import STRING_CHECKS

_ROOT = Path(__file__).resolve().parents[3]
_FIELDS = ("expr", "condition", "key_expr", "clamp_bounds")
_SKIP_PREFIXES = (
    "node_modules/", "docs/INDEX.md", "frontend/src/api/generated", "uv.lock", "docs/plans/",
    "docs/rulings/", "docs/findings/", "docs/ledgers/", "docs/research/", "docs/rfcs/",
    "docs/closures/",
)
#: `02` §4.6 data-preparation expressions, not rating strings.
_DATA_PREPARATION = (
    "packages/pricing-core/tests/test_expression_profiles.py",
    "packages/pricing-core/tests/test_prepare.py",
    "scripts/bench-data.py",
)
_KEY = re.compile(
    r"""["']?\b(condition|expr|key_expr)\b["']?\]?\s*[:=]\s*"""
    r"""(?:"((?:[^"\\\n]|\\.)*)"|'((?:[^'\\\n]|\\.)*)')"""
)
_CLAMP = re.compile(r"""clamp_bounds\b["']?\]?\s*[:=]\s*\{([^}\n]*)\}""")
_BOUND = re.compile(
    r"""["'](?:min|max)["']\s*:\s*(?:"((?:[^"\\\n]|\\.)*)"|'((?:[^'\\\n]|\\.)*)')"""
)


def _flat(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.List | ast.Tuple):
        return [text for element in node.elts for text in _flat(element)]
    if isinstance(node, ast.Dict):
        return [text for value in node.values for text in _flat(value)]
    return []


def _json_strings(value: object, under_properties: bool = False) -> list[str]:
    """Authored strings in a JSON value.

    A field-named key directly under a JSON Schema `properties` is a property *definition*;
    its `title` is a generated label ("Clamp Bounds"), not an expression, so only that one
    key is ignored there. Every other string in the definition is still scanned.
    """
    if isinstance(value, dict):
        out: list[str] = []
        for key, item in value.items():
            if key in _FIELDS:
                scanned = item
                if under_properties and isinstance(item, dict):
                    scanned = {k: v for k, v in item.items() if k != "title"}
                out += [t for t in _json_flat(scanned)]
            out += _json_strings(item, under_properties=key == "properties")
        return out
    if isinstance(value, list):
        return [text for item in value for text in _json_strings(item)]
    return []


def _json_flat(item: object) -> list[str]:
    if isinstance(item, str):
        return [item]
    if isinstance(item, list):
        return [text for element in item for text in _json_flat(element)]
    if isinstance(item, dict):
        return [text for element in item.values() for text in _json_flat(element)]
    return []


def _authored_strings() -> set[tuple[str, int, str, str]]:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=_ROOT, capture_output=True, text=True, check=True
    ).stdout.split("\n")
    found: set[tuple[str, int, str, str]] = set()
    for path in tracked:
        if not path or path.startswith(_SKIP_PREFIXES) or path in _DATA_PREPARATION:
            continue
        try:
            text = (_ROOT / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if path.endswith((".py", ".json", ".yaml", ".yml", ".ts", ".vue", ".md", ".toml", ".js")):
            for number, line in enumerate(text.split("\n"), 1):
                for match in _KEY.finditer(line):
                    found.add((path, number, match.group(1), match.group(2) or match.group(3)))
                for match in _CLAMP.finditer(line):
                    for inner in _BOUND.finditer(match.group(1)):
                        found.add((path, number, "clamp_bounds", inner.group(1) or inner.group(2)))
        if path.endswith(".py"):
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    for key, value in zip(node.keys, node.values, strict=True):
                        if isinstance(key, ast.Constant) and key.value in _FIELDS:
                            found |= {(path, key.lineno, str(key.value), t) for t in _flat(value)}
                elif isinstance(node, ast.keyword) and node.arg in _FIELDS:
                    found |= {(path, node.value.lineno, node.arg, t) for t in _flat(node.value)}
        if path.endswith(".json"):
            try:
                found |= {(path, 0, "json", t) for t in _json_strings(json.loads(text))}
            except ValueError:
                continue
    return found


def _codes(text: str) -> set[str]:
    return {found[0] for check in STRING_CHECKS if (found := check(text)) is not None}


#: Each deliberate negative fixture, and the code its own test asserts (still refused).
_NEGATIVES: dict[str, set[str]] = {
    # test_rating_compile.py: test_a_non_deterministic_expression_is_refused
    "risk_premium_minor * expense_factor + now()": {"EXPRESSION_NON_DETERMINISTIC"},
    # test_rating_compile.py: test_a_foreign_function_is_refused
    "foo(risk_premium_minor)": {"EXPRESSION_INVALID_VOCABULARY"},
    # test_rating_algorithms.py, test_rating_compile.py, test_rating_compile_bundle.py:
    # the unguarded-division tests
    "risk_premium_minor / expense_factor": {"EXPRESSION_UNGUARDED_DIVISION"},
    # test_rating_algorithms.py: test_a_masked_division_in_a_condition_is_refused_at_save_time
    "((office_premium_minor / expense_factor) ?? 0) >= 100": {"EXPRESSION_UNGUARDED_DIVISION"},
    # test_rating_score.py: bundles built by hand to bypass the save check (RL-1313 DP-G4);
    # `_compile_with` tests refuse the masked forms at compile
    "office_premium_minor / sanity_floor_minor <= 2": {"EXPRESSION_UNGUARDED_DIVISION"},
    "sanity_cap_minor / sanity_floor_minor": {"EXPRESSION_UNGUARDED_DIVISION"},
    "risk_premium_minor * expense_factor * (1 / (expense_factor - expense_factor))": {
        "EXPRESSION_UNGUARDED_DIVISION"
    },
}


@pytest.fixture(scope="module")
def committed() -> set[tuple[str, int, str, str]]:
    return _authored_strings()


@pytest.mark.req("FR-244")
def test_the_extractor_finds_the_committed_strings(
    committed: set[tuple[str, int, str, str]],
) -> None:
    """A sanity floor: the predicate sees the score fixture's and the spec example's strings."""
    texts = {text for _, _, _, text in committed}
    assert "risk_premium_minor * expense_factor" in texts
    assert "office_premium_minor >= min_premium_minor" in texts
    assert len(texts) >= 30


@pytest.mark.req("FR-244")
def test_every_committed_string_is_accepted_or_a_declared_negative(
    committed: set[tuple[str, int, str, str]],
) -> None:
    unexplained = []
    for path, line, field, text in sorted(committed):
        codes = _codes(text)
        expected = _NEGATIVES.get(text, set())
        if codes != expected and not (expected and expected <= codes):
            unexplained.append(f"{path}:{line} [{field}] {text!r}: {sorted(codes)}")
    assert unexplained == []


@pytest.mark.req("FR-244")
def test_every_declared_negative_is_still_committed(
    committed: set[tuple[str, int, str, str]],
) -> None:
    texts = {text for _, _, _, text in committed}
    assert set(_NEGATIVES) <= texts


@pytest.mark.req("FR-244")
def test_a_property_definition_title_is_ignored_and_nothing_else_in_it() -> None:
    """Broken-input proof for the narrowed JSON predicate (WK-1250 Slice 1).

    Only the generated `title` under `properties` is skipped; a `default` carrying a real
    expression in the same definition is still scanned, and a field-named key outside
    `properties` is scanned whole.
    """
    # Built from parts so this test's own source is not an authored string to the scan above.
    field, bad = "ex" + "pr", "fo" + "o(1)"
    schema = {"properties": {field: {"title": "T", "default": bad}}}
    assert _json_strings(schema) == [bad]
    assert _json_strings({field: {"title": "T"}}) == ["T"]
