"""Every catalogue rule names a check that exists.

`01` §4.4 gives each rule a name and an English description; the *check* is the function in
`pricing_core.data.validate` that runs it, and nothing before this test connected the two. A
typo in the catalogue would otherwise surface as a seeded rule that fails at validation time
in a workspace, long after the transcription.
"""

from __future__ import annotations

import pytest

from model_schema import BUILTIN_RULES
from pricing_core.data.validate import CHECKS


@pytest.mark.req("FR-DATA-53")
def test_every_builtin_rule_names_a_registered_check() -> None:
    missing = sorted(
        f"{rule.catalogue_id} -> {rule.check}"
        for rule in BUILTIN_RULES.values()
        if rule.check not in CHECKS
    )
    assert not missing, missing


@pytest.mark.req("FR-DATA-53")
def test_the_registry_is_not_trivially_satisfied() -> None:
    """The check above passes vacuously if `CHECKS` is empty or over-broad.

    Six registered checks back no catalogue rule — `regex`, `relationship`, `expression`,
    `aggregate`, `distribution_compare` and `sql` are the primitives a *custom* rule is
    built from (`01` §4.5). Asserting the gap exists is what proves membership means
    something.
    """
    used = {rule.check for rule in BUILTIN_RULES.values()}
    assert len(CHECKS) > len(used)
    assert {"expression", "sql"} <= set(CHECKS) - used


@pytest.mark.req("FR-DATA-54")
def test_every_catalogue_default_names_a_param_its_check_reads() -> None:
    """A catalogue key its check never reads is silently inert.

    Every check reads params as `.get(key, literal)`, so a misspelled catalogue key falls
    back to the literal and nothing raises. The seeded rule would then advertise a threshold
    it does not honour — which is the failure FR-DATA-54 exists to remove, reintroduced one
    level up.

    Matched as `params.get("key"` rather than as a bare quoted `"key"`. The looser form has
    a demonstrated blind spot: a check's source also contains the *default values* of its
    other params, so `duplicate_claim`, which reads
    `params.get("columns", ["policy_id", ...])`, contains the literal `"policy_id"` while
    reading no such param. A catalogue entry declaring `policy_id` would have passed the
    loose test and been inert — the exact defect this guard exists to catch.
    """
    import inspect

    unread = []
    for rule in BUILTIN_RULES.values():
        if not rule.params:
            continue
        source = inspect.getsource(CHECKS[rule.check])
        unread += [
            f"{rule.catalogue_id} -> {rule.check} never reads {key!r}"
            for key in rule.params
            if f'params.get("{key}"' not in source
        ]
    assert not unread, unread


@pytest.mark.req("FR-DATA-54")
def test_the_anti_drift_check_is_not_trivially_satisfied() -> None:
    """The test above passes vacuously if no rule carries params, or if its pattern matches
    anything. Asserted with the *same* pattern the guard uses, not a looser stand-in: a
    positive control written against a different pattern goes green on what it misses.
    """
    import inspect

    psi = inspect.getsource(CHECKS["psi_column"])
    assert 'params.get("warn_above"' in psi
    assert 'params.get("warn_abovv"' not in psi

    #: The blind spot the pattern was tightened to close, pinned so it cannot reopen: a
    #: param's *default value* is a quoted literal in the same source, and must not read as
    #: evidence that a param of that name is read.
    duplicate_claim = inspect.getsource(CHECKS["duplicate_claim"])
    assert '"policy_id"' in duplicate_claim
    assert 'params.get("policy_id"' not in duplicate_claim

    assert any(rule.params for rule in BUILTIN_RULES.values())
