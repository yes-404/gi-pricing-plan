"""WK-2113 S3, condition (4): the stored-bundle sweep, red first, on a planted offender.

`scripts/sweep-stored-bundles.py` is READ-ONLY. It walks every stored Rating Version with a
Bundle and reports each whose carried GLM Factors put a `control`-intent Factor under a rateable
path (the closure test `control_factor_in`, the one definition every guard shares), so an operator
learns BEFORE the upgrade which versions `load_bundle` will refuse (RL: S3 design (C)+(B)).

Interface this test fixes, which the S3 plan may rename but must keep the behaviour of:

* `sweep(versions, out)` is the pure core: `versions` is a list of dicts
  `{"slug", "version", "status", "bundle_hash", "bundle"}` (`bundle` is the parsed Bundle JSON, or
  `None` for a version never compiled); it prints to `out` and returns the exit code.
* The CLI (`_main`) reads the same dicts from `rating_versions` and calls `sweep`.
* Output order is the contract: the DENOMINATORS print first (`versions: N`, `with a bundle: M`,
  `checked: K`), then one `OFFENDER ...` line per offender, then `offenders: J`. A zero over an
  empty corpus is vacuous (CLAUDE.md §13), so the denominators come before any verdict.

RED today: the script does not exist, so the module-level load fails (`FileNotFoundError`).
The fixtures are bundles compiled by `gen/make_fixtures.py` (see the README), committed as JSON.
"""

from __future__ import annotations

import importlib.util
import io
import json
import pathlib
from typing import Any

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "stored_bundles"

_spec = importlib.util.spec_from_file_location(
    "sweep_stored_bundles", ROOT / "scripts" / "sweep-stored-bundles.py"
)
assert _spec is not None
assert _spec.loader is not None
sweep_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sweep_module)


#: `content_hash` covers the pins, not the carried Factor payloads (`_carry_glm_inputs`: "the
#: Bundle's shape and `bundle_hash` are unchanged"), so the offender and the clean
#: fixture share one hash.
#: The clean row is given its own hash here only so the tests can tell the two rows apart.
_CLEAN_ROW_HASH = "sha256:" + "c" * 64


def _version(slug: str, version: int, fixture: str | None) -> dict[str, Any]:
    bundle = json.loads((FIXTURES / fixture).read_text()) if fixture else None
    row_hash = (
        None
        if bundle is None
        else (_CLEAN_ROW_HASH if fixture == "clean.bundle.json" else bundle["content_hash"])
    )
    return {
        "slug": slug,
        "version": version,
        "status": "approved",
        "bundle_hash": row_hash,
        "bundle": bundle,
    }


def _run(versions: list[dict[str, Any]]) -> tuple[int, list[str]]:
    out = io.StringIO()
    rc = sweep_module.sweep(versions, out)
    return rc, out.getvalue().splitlines()


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_an_offender_is_reported_by_version_hash_and_operand_with_a_non_zero_rc() -> None:
    offender = _version("motor-freq", 3, "offender.bundle.json")
    rc, lines = _run([offender, _version("motor-clean", 1, "clean.bundle.json")])
    assert rc != 0
    hit = [line for line in lines if line.startswith("OFFENDER")]
    assert len(hit) == 1
    assert "motor-freq@3" in hit[0]
    assert offender["bundle_hash"] in hit[0]
    assert "yoa" in hit[0]  # the control operand
    assert "region_x_yoa" in hit[0]  # reached through this interaction
    assert "motor-clean" not in hit[0]
    assert _CLEAN_ROW_HASH not in hit[0]


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_a_clean_risk_by_risk_version_alone_is_rc_zero() -> None:
    """Instrument-red cell: the sweep must not report everything."""
    rc, lines = _run([_version("motor-clean", 1, "clean.bundle.json")])
    assert rc == 0
    assert not [line for line in lines if line.startswith("OFFENDER")]
    assert "offenders: 0" in lines


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_the_denominators_print_before_any_verdict() -> None:
    versions = [
        _version("motor-freq", 3, "offender.bundle.json"),
        _version("motor-clean", 1, "clean.bundle.json"),
        _version("motor-draft", 1, None),  # a version with no bundle yet
    ]
    _, lines = _run(versions)
    assert lines[:3] == ["versions: 3", "with a bundle: 2", "checked: 2"]
    assert lines.index("versions: 3") < min(
        i for i, line in enumerate(lines) if line.startswith("OFFENDER")
    )
    assert lines[-1] == "offenders: 1"


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_an_empty_corpus_prints_its_zero_denominators_not_a_bare_pass() -> None:
    rc, lines = _run([])
    assert rc == 0
    assert lines[:3] == ["versions: 0", "with a bundle: 0", "checked: 0"]


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_a_bundle_that_cannot_be_read_is_counted_and_fails_the_sweep() -> None:
    """Fail closed: a bundle the sweep cannot parse is not shown clean (rc non-zero, named)."""
    broken = _version("motor-clean", 1, "clean.bundle.json")
    broken["bundle"] = {"content_hash": "x" * 64}
    rc, lines = _run([broken])
    assert rc != 0
    assert any(line.startswith("UNREADABLE") and "motor-clean@1" in line for line in lines)
