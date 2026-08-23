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
