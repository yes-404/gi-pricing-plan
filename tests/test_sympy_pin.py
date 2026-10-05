"""RL-1289: `sympy` is pinned at exactly 1.14.0, once, in the lock and in pricing-core.

The violation the ruling names is "the derivation version the platform records differs from
the sympy actually pinned". Its first half is checked here: `uv.lock` resolves exactly one
`sympy`, at `1.14.0`, and `pricing-core` declares it with `==`. The checker is a function of
the lock text, so the broken-input cases below run the same code as the real-tree case.
"""

from __future__ import annotations

import pathlib
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PINNED = "1.14.0"


def lock_violations(lock_text: str) -> list[str]:
    """Every way `lock_text` fails RL-1289's pin. An empty list means it holds."""
    packages = tomllib.loads(lock_text).get("package", [])
    versions = [p.get("version") for p in packages if p.get("name") == "sympy"]
    if not versions:
        return ["sympy is absent from the lock"]
    problems = []
    if len(versions) > 1:
        problems.append(f"the lock resolves sympy {len(versions)} times: {versions}")
    problems += [f"the lock resolves sympy {v}, not {PINNED}" for v in versions if v != PINNED]
    return problems


def test_the_lock_resolves_sympy_exactly_once_at_the_pin() -> None:
    assert lock_violations((ROOT / "uv.lock").read_text()) == []


def test_pricing_core_declares_the_exact_pin() -> None:
    project = tomllib.loads((ROOT / "packages/pricing-core/pyproject.toml").read_text())
    assert f"sympy=={PINNED}" in project["project"]["dependencies"]


@pytest.mark.parametrize(
    ("lock_text", "expected"),
    [
        ('[[package]]\nname = "polars"\nversion = "1.44.2"\n', "absent"),
        ('[[package]]\nname = "sympy"\nversion = "1.13.3"\n', "not 1.14.0"),
        (
            '[[package]]\nname = "sympy"\nversion = "1.14.0"\n'
            '[[package]]\nname = "sympy"\nversion = "1.13.3"\n',
            "2 times",
        ),
    ],
)
def test_a_broken_lock_is_reported(lock_text: str, expected: str) -> None:
    """The checker on deliberately broken input. Without these, a checker that returns
    `[]` for everything would pass the real-tree test above."""
    assert any(expected in problem for problem in lock_violations(lock_text))
