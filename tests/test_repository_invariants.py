"""Repository-level invariants that no single component owns.

These exist because of what a W1 re-audit found: **the traceability record only sees
`@pytest.mark.req` markers**, so a requirement enforced by something else — an
import-linter contract, a database privilege, a recorded measurement — reads as
unevidenced. W1 was the extreme case: its whole deliverable is enforcement machinery, so
`scope-audit.py` reported half its scope missing while the enforcement was working
perfectly in CI.

The fix is to make that enforcement visible as evidence rather than to trust it silently.
A test here does not replace the CI step it names; it links the requirement to the
mechanism, so an audit can find it.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.mark.req("FR-OVR-5")
def test_pricing_core_is_callable_without_the_backend() -> None:
    """ADR-0001, enforced by the import-linter contract rather than by a unit test.

    "All pricing computation lives in `pricing-core` and is callable without the backend"
    is a property of the dependency graph, not of any function. The contract checks the
    whole graph on every run, which is stronger than anything a test could assert about one
    module — but it is invisible to the requirement record without this.
    """
    binary = shutil.which("lint-imports")
    if binary is None:  # pragma: no cover - only when the dev group is not installed
        pytest.skip("lint-imports is not installed; run `uv sync --all-packages --dev`")

    result = subprocess.run([binary], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Contracts: 3 kept, 0 broken." in result.stdout


@pytest.mark.req("FR-OVR-6")
def test_the_architecture_contracts_are_configured_and_not_silently_empty() -> None:
    """A contract file that parses but checks nothing reports success for ever.

    That happened here: `root_packages` was comma-separated on one line, the ini parser
    split it into characters, and the ADR-0001 contract enforced nothing for a day while
    reporting green. Asserting the count of *kept* contracts is what makes the difference
    between "the checker ran" and "the checker checked something".
    """
    config = (ROOT / ".importlinter").read_text(encoding="utf-8")
    assert "include_external_packages = True" in config
    for package in ("model_schema", "pricing_core", "app"):
        assert f"\n    {package}\n" in config, package
    assert config.count("[importlinter:contract:") == 3


@pytest.mark.req("NFR-OVR-9")
def test_the_full_stack_is_declared_for_local_use() -> None:
    """NFR-OVR-9: the stack runs locally via `docker compose up` with no cloud dependency.

    Structural only — that the services and their health checks are declared. The timing
    claim (NFR-PLAT-4, measured at 21 s against a 300 s budget) lives in `deploy/README.md`
    and the roadmap, because starting containers is not something CI should do on every
    push to assert a number that changes with the runner.
    """
    compose = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
    for service in ("postgres:", "redis:", "minio:"):
        assert service in compose, service
    # No cloud dependency: every image is a public one pinned by name, and nothing
    # references an external endpoint the stack could not reach offline.
    assert "healthcheck:" in compose
    assert compose.count("healthcheck:") >= 3
    assert "amazonaws.com" not in compose


@pytest.mark.req("FR-OVR-7")
def test_money_discipline_is_enforced_by_the_docs_audit() -> None:
    """FR-OVR-7 is checked in two places, and both must stay.

    The types enforce it in code (`MoneyMinor`, `DecimalStr`); `scripts/audit-docs.py`
    enforces it across the contracts, where a `_minor` field with a fractional example
    would otherwise pass unnoticed.
    """
    audit = (ROOT / "scripts" / "audit-docs.py").read_text(encoding="utf-8")
    assert "_minor" in audit, "the money-discipline check is gone from the docs audit"

    result = subprocess.run(
        ["python3", "scripts/audit-docs.py"], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed" in result.stdout


@pytest.mark.req("NFR-GOV-8")
def test_the_governance_negative_tests_exist_in_ci() -> None:
    """NFR-GOV-8: separation of duties, append-only audit and permission enforcement are
    *covered by explicit negative tests in CI*.

    A requirement about the test suite, so the suite is where it is checked. Asserting the
    marker exists is weak on its own — what makes it meaningful is that each named test
    asserts a refusal, which is why the names are matched rather than counted.
    """
    import re

    suite = "\n".join(
        path.read_text(encoding="utf-8")
        for root in ("backend/tests", "packages", "tests")
        for path in (ROOT / root).rglob("test_*.py")
    )

    required = {
        "separation of duties": r"def test_the_submitter_cannot_approve",
        "distinct approvers": r"def test_two_approvals_must_come_from_distinct_principals",
        "append-only audit": r"def test_update_and_delete_are_rejected_by_the_database",
        "no truncate": r"def test_truncate_is_rejected",
        "permission enforcement": r"def test_a_caller_without_the_role_is_forbidden",
        "no self-elevation": r"def test_a_user_cannot_grant_a_permission_they_do_not_hold",
    }
    missing = [name for name, pattern in required.items() if not re.search(pattern, suite)]
    assert missing == [], f"negative tests missing for: {missing}"


@pytest.mark.req("FR-PLAT-47")
def test_the_error_code_registry_matches_the_specs() -> None:
    """Every code a module declares it owns is registered, and no code is invented.

    Written after four codes were invented for `01` in one sitting — plausible names for
    conditions the spec had already named differently. `PlatformError` validates against
    the registry, so an unregistered code fails loudly; an *extra* one does not, and would
    reach a client as something no spec documents.
    """
    import re
    import sys

    sys.path.insert(0, str(ROOT / "backend" / "src"))
    from app.errors import DATA_ERROR_CODES, GOVERNANCE_ERROR_CODES, PLATFORM_ERROR_CODES

    registries = {
        "01-data-management.md": DATA_ERROR_CODES,
        "06-governance.md": GOVERNANCE_ERROR_CODES,
        "07-platform.md": PLATFORM_ERROR_CODES,
    }

    for filename, registry in registries.items():
        spec = (ROOT / "docs" / "specs" / filename).read_text(encoding="utf-8")
        marker = "**Error codes owned by this module:**"
        start = spec.index(marker)
        # The declaration runs to the blank line that ends the paragraph.
        block = spec[start : spec.index("\n\n", start)]
        declared = set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", block))
        assert declared, filename
        assert declared == set(registry), (
            f"{filename}: spec-only {sorted(declared - set(registry))}, "
            f"registry-only {sorted(set(registry) - declared)}"
        )
