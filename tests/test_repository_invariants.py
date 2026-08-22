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


@pytest.mark.req("FR-OVR-17")
def test_journey_citations_are_audited_in_ci() -> None:
    """FR-OVR-17(i): the mechanical citation audit, and the marker that makes it visible.

    The check lives in `scripts/audit-docs.py` (check 21) and `docs.yml` runs that script on
    every `docs/**` change, so the enforcement is real. But `req-coverage.py` reads
    `@pytest.mark.req` markers, and a check enforced only by a script reads as an unevidenced
    requirement — the failure re-auditing W1 produced, where half the scope looked missing
    while the enforcement was working perfectly in CI. This test is the link.

    It asserts three things rather than one, because each can rot independently: the check is
    still in the script, CI still runs the script on docs changes, and the audit still passes.

    **What it deliberately does not assert** is FR-OVR-17(ii) — one end-to-end test per
    journey. That is not built, and a marker here claiming the whole requirement is precisely
    the "a marker on an existing test is not evidence" failure the requirement's own text
    refuses.
    """
    audit = (ROOT / "scripts" / "audit-docs.py").read_text(encoding="utf-8")
    assert "FR-OVR-17" in audit, "check 21 is gone from the docs audit"
    assert "_path_segments" in audit, "the citation path parser is gone"

    workflow = (ROOT / ".github" / "workflows" / "docs.yml").read_text(encoding="utf-8")
    assert "scripts/audit-docs.py" in workflow, "CI no longer runs the docs audit"
    assert "docs/**" in workflow, "the docs audit no longer triggers on a docs change"

    result = subprocess.run(
        ["python3", "scripts/audit-docs.py"], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "journey citations:" in result.stdout, "check 21 did not run"
    assert "undeclared" not in result.stdout, result.stdout


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


@pytest.mark.req("FR-PLAT-47")
def test_every_error_code_pricing_core_raises_is_registered_and_declared() -> None:
    """A code `pricing-core` raises reaches the caller through `PlatformError`.

    **Marker corrected 2026-08-22 (W5 audit).** This claimed `FR-OVR-13`, which is *"one
    tenant, one deployment"* (`00` §3, ADR-0006) and has nothing to do with error codes — so
    `req-coverage.py` counted tenant isolation as evidenced by a test that never mentions it.
    `CLAUDE.md` §13: a marker is a claim, not a proof. `FR-PLAT-47` is the requirement this
    test actually evidences — *"RFC 9457 problem responses with stable `code`s"* — and it is
    what `test_the_error_code_registry_matches_the_specs` above already carries for the same
    property approached from the specification side.

    Deliberately **not** `FR-OVR-19`, which is the closest match by wording: that requirement
    specifies an `audit-docs.py` check that does not exist yet, is owned by the maintainer,
    and is triggered by Phase 1a's exit demo. Marking a passing test with it would claim
    evidence for unbuilt work — the same defect being corrected here.

    The fit handler maps a `GlmFitError`/`GbmFitError` code straight across, and
    `PlatformError` refuses a code it does not know — so an unregistered one turns a named
    refusal into `ValueError: unknown error code` **from inside the error path**, at the
    moment the caller most needs the answer.

    This has now happened twice: `GLM_SEPARATION_DETECTED` was unregistered from the spine
    until the diagnostics slice tripped it, and the GBM slice added eleven more codes that
    no test would have exercised until a real fit failed. Checking the *source* rather than
    waiting for a scenario is what makes the next one impossible rather than unlucky.

    `02-modelling.md` is deliberately absent from the spec-versus-registry test above,
    because §5.1's catalogue declares codes whose slices have not been built — so this
    checks the other direction: everything raised must be declared **and** registered, while
    the catalogue may still run ahead.
    """
    import ast
    import re
    import sys

    sys.path.insert(0, str(ROOT / "backend" / "src"))
    from app.errors import MODELLING_ERROR_CODES

    modelling = ROOT / "packages" / "pricing-core" / "src" / "pricing_core" / "modelling"
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in modelling.glob("*.py")}

    # Derived, not listed. This was a literal set of four names until 2026-08-18, and by then
    # the module defined nine error classes — so `PredictionError` and `ObjectiveError` were
    # invisible to the very check written to make an unregistered code impossible, and four
    # of `predict.py`'s codes had been reachable and unregistered since the prediction slice.
    # A hand-maintained list of what to scan fails the same way as a hand-maintained list of
    # what to register, one release later.
    raisers = {
        node.name
        for tree in trees.values()
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name.endswith("Error")
    }
    raised: dict[str, str] = {}

    for path, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else None
            if name not in raisers or not node.args:
                continue
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                raised[first.value] = path.name

    assert raised, "no error codes found — the scan is looking in the wrong place"

    unregistered = {
        code: where for code, where in raised.items()
        if code not in MODELLING_ERROR_CODES
    }
    assert not unregistered, (
        f"raised by pricing-core and unknown to PlatformError: {sorted(unregistered)}. "
        "Add them to MODELLING_ERROR_CODES and to `02` §5.1's catalogue."
    )

    spec = (ROOT / "docs" / "specs" / "02-modelling.md").read_text(encoding="utf-8")
    marker = "**Error codes owned by this module:**"
    block = spec[spec.index(marker) : spec.index("\n\n", spec.index(marker))]
    declared = set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", block))
    undeclared = sorted(code for code in raised if code not in declared)
    assert not undeclared, f"raised and registered but absent from `02` §5.1: {undeclared}"
