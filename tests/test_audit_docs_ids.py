"""`scripts/audit-docs.py` checks 30-39 — NT-0019's id-standard audit
(docs/notes/0019-one-id-per-document.md §1.11), Slice W37-4
(`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`).

Ten broken-input proofs, one per check (the plan's own "a fixture that trips two checks
proves neither"): each fixture below is loaded as the *entire* `_ID_SCOPE_ROOTS` for a
call to `check_ids_30_39()` — every one of the ten checks, run together — and the
assertion is that every failure produced names the *one* targeted check number, while
the fixture is built (verified check by check while it was written) so that no other
check's own rule fires on the same content. Four checks are proven a different way
because their mechanism cannot be exercised through `_ID_SCOPE_ROOTS` alone, and each
says why at its own test: check 32 gates on `docs/INDEX.md` and is proven on its pure
`citation_problems_in_file` function with an explicit `index_ids` set; check 33's
map-plan roll-up raise (Ruling 72) needs a `docs/`-shaped corpus `doc_index.build_corpus`
can walk, which two flat scope roots cannot be; check 34's freeze predicate (DP-7) needs
an old/new pair, which is a merge-base comparison no file in `_ID_SCOPE_ROOTS` has yet;
check 39's byte-stability runs over the whole real `docs/` tree by design (`ROOT`, not
`_ID_SCOPE_ROOTS`), and `ROOT` feeds constants (`_TEMPLATES_DIR`, `NOTES`) bound once at
import time, so monkeypatching it for a shared-orchestrator run would desynchronise them.
Check 38 is warn-only by NT-0019's own words ("never fails the gate") — there is no
broken input that reds it, so its proof is the opposite shape: it never calls `fail()`,
proven directly rather than assumed.

`tests/fixtures/docs-ids/` is the shared fixture root W37-2 created and W37-3 extended;
this slice adds `w37-4-checks/` (one fixture per check-30-39 broken-input proof) and
`w37-4-rollup-raise/` (a `docs/`-shaped corpus for the Ruling 72 roll-up raise, alongside
the existing `w37-3-corpus/`).

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence
for a numbered platform requirement — the same reasoning `tests/test_doc_id.py` and
`tests/test_doc_index.py` give for their own scripts.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types
from datetime import date

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"
FIXTURES = ROOT / "tests" / "fixtures" / "docs-ids"
CHECKS_FIXTURES = FIXTURES / "w37-4-checks"


def _load_by_path(name: str, path: pathlib.Path) -> types.ModuleType:
    """Load a hyphenated `scripts/` module by path — `audit-docs.py` cannot be
    `import`ed by name. Same idiom `tests/test_doc_id.py` and `tests/test_doc_index.py`
    already use for their own scripts.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def audit() -> types.ModuleType:
    """A fresh load of `audit-docs.py` per test — cheap (no I/O beyond parsing this one
    file and the two it loads by path in turn), and it means no test has to remember to
    reset every piece of state a previous test might have left mutated. Function-scoped
    rather than module-scoped for exactly that reason: `_ID_SCOPE_ROOTS` is reassigned by
    nearly every test below, and a shared module would need its own careful save/restore
    around each one. No teardown: the loaded module is simply garbage-collected once the
    test's own reference (and `sys.modules`' entry, overwritten by the next test's load)
    goes out of use.
    """
    return _load_by_path("_audit_docs_under_test", SCRIPT)


def _run_all_ten(audit: types.ModuleType, roots: tuple[pathlib.Path, ...]) -> list[str]:
    """Run every one of checks 30-39 with `_ID_SCOPE_ROOTS` pointed at `roots`, and
    return the resulting `failures` list. `notes`/`failures` are reset first so a
    fixture's own prior use (there is none in practice, since `audit` is function-scoped)
    can never leak between calls.
    """
    audit.failures.clear()
    audit.notes.clear()
    # `setattr`, not `audit._ID_SCOPE_ROOTS = roots`: `types.ModuleType`'s stub declares
    # `__getattr__` (so any *read* on a dynamically-loaded module type-checks as `Any`),
    # but no `__setattr__` — mypy has no fallback for an *assignment* to a name it cannot
    # statically find, and flags it `[attr-defined]` everywhere that name is then used in
    # the file, reads included. `setattr` sidesteps this the same way a plain read does.
    setattr(audit, "_ID_SCOPE_ROOTS", roots)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.check_ids_30_39()
    return list(audit.failures)


def _only_check(failures: list[str], n: int) -> bool:
    """True when `failures` is non-empty and every entry names check `n` — the "exactly
    one check reds" proof the plan's own broken-input standard asks for.
    """
    if not failures:
        return False
    prefix = f"check {n}:"
    return all(msg.startswith(prefix) for msg in failures)


# =========================================================================================
# Check 30 — header present and parseable; no unknown field; required fields per family
# (Ruling 70).
# =========================================================================================


def test_check_30_reds_alone_on_an_unknown_field(audit: types.ModuleType) -> None:
    """Ruling 70 §4 item 1: a fixture `FD-` essay whose front matter carries `decision:`
    must fail check 30 — `decision:` is a register-row field (Ruling 70), not this
    essay's, so `_docid.parse_header` puts it in `.extra` and check 30 must reject it.
    """
    failures = _run_all_ten(audit, (CHECKS_FIXTURES / "check30-unknown-field.md",))
    assert _only_check(failures, 30), failures
    assert any("decision" in f for f in failures), failures


def test_check_30_reds_alone_on_a_ledger_prs_field(audit: types.ModuleType) -> None:
    """Ruling 70 §4 item 4: a fixture ledger header carrying `prs:` must fail check 30 —
    `docs/_templates/LG.md` does not declare it (a ledger's PR list lives in its `## PRs`
    body section instead), so it is not a permitted field despite §1.5's parenthesis.
    """
    failures = _run_all_ten(audit, (CHECKS_FIXTURES / "check30-ledger-prs.md",))
    assert _only_check(failures, 30), failures
    assert any("prs" in f for f in failures), failures


def test_check_30_positive_control_a_clean_finding_essay_passes(
    audit: types.ModuleType,
) -> None:
    """Positive control: a finding essay carrying exactly `docs/_templates/FD.md`'s own
    field set, and nothing more, must pass every one of the ten checks — proving the
    unknown-field rule does not false-positive on a legitimately clean header.
    """
    failures = _run_all_ten(
        audit, (CHECKS_FIXTURES / "check30-good-finding" / "findings",)
    )
    assert failures == [], failures


def test_check_30_field_policy_changes_with_the_template(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 70 §4 item 2: "add a key to one template's front matter and a header using
    that key must become permitted; remove it and the same header must red" — proven
    directly against `derive_field_policies`'s own mechanism, on a *copy* of the real
    templates (never the real `docs/_templates/`, which this test must not mutate).
    """
    import shutil

    templates_copy = tmp_path / "templates"
    shutil.copytree(audit._TEMPLATES_DIR, templates_copy)
    setattr(audit, "_TEMPLATES_DIR", templates_copy)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment

    before = audit.derive_field_policies()
    assert "extra_test_field" not in before["decision"].permitted

    adr = templates_copy / "ADR.md"
    text = adr.read_text(encoding="utf-8")
    assert "relates: []" in text, "fixture assumption: ADR.md's own field list changed"
    widened = text.replace("relates: []", "relates: []\nextra_test_field: x")
    adr.write_text(widened, encoding="utf-8")

    after = audit.derive_field_policies()
    assert "extra_test_field" in after["decision"].permitted, (
        "adding a key to the template did not widen the derived permitted set — the "
        "policy is not actually being read from the template"
    )


def test_check_30_silent_empty_coverage_is_impossible(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 70 §4 item 3: "check 30 parses zero of the thirteen files under
    docs/_templates/ and still exits 0" must become impossible. Deleting one template
    (any one; `PHASE.md` here) must raise loudly rather than silently deriving a smaller,
    equally-plausible-looking policy — the exact failure mode a naive
    `_docid.parse_header`-based reader hit first (0 of 13 parse, on the *raw*, un-stripped
    templates, because every one opens with an HTML comment).
    """
    import shutil

    templates_copy = tmp_path / "templates"
    shutil.copytree(audit._TEMPLATES_DIR, templates_copy)
    (templates_copy / "PHASE.md").unlink()
    setattr(audit, "_TEMPLATES_DIR", templates_copy)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment

    with pytest.raises(RuntimeError, match="expected exactly"):
        audit.derive_field_policies()


def test_check_30_reports_the_full_thirteen_template_coverage_on_the_real_tree(
    audit: types.ModuleType,
) -> None:
    """The naive failure mode, pinned against the *real* `docs/_templates/`: this must
    report all thirteen, not a silently smaller number that happens to look complete.
    """
    policies = audit.derive_field_policies()
    # Ten document families with a `---` block, plus the two row families (WK, SL) with
    # a fenced block — twelve total; PHASE.md carries no family and contributes none.
    assert len(policies) == 12, policies
    assert set(policies) == {
        "decision", "closure", "finding", "ledger", "plan", "reference", "proposal",
        "ruling", "research", "workflow", "work", "slice",
    }


# =========================================================================================
# Check 31 — id/filename/directory agreement; numbers unique and contiguous; `created`
# non-decreasing.
# =========================================================================================


def test_check_31_reds_alone_on_a_header_filename_mismatch(audit: types.ModuleType) -> None:
    failures = _run_all_ten(audit, (CHECKS_FIXTURES / "check31" / "plans",))
    assert _only_check(failures, 31), failures
    assert "PL-1920" in failures[0], failures
    assert "PL-1921" in failures[0], failures


def test_check_31_exempts_templates_by_path(audit: types.ModuleType) -> None:
    """NT-0019 §1.4: "`_templates/` is exempt from check 31 by path." Pointing
    `_ID_SCOPE_ROOTS` at the real templates directory alone must not trip check 31 on the
    `NNNNN`/`XX-NNNNN` placeholders every template carries.
    """
    failures = _run_all_ten(audit, (audit._TEMPLATES_DIR,))
    assert not any(f.startswith("check 31:") for f in failures), failures


# =========================================================================================
# Check 32 — citation resolution and padding hygiene. Proven on the pure function
# directly: production gates the whole check on docs/INDEX.md existing (see module
# docstring), so a scope-rooted fixture cannot exercise it the way the other checks are.
# =========================================================================================


def test_check_32_flags_a_citation_that_does_not_resolve(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "doc.md"
    f.write_text("See PL-9999 for detail.\n", encoding="utf-8")
    problems = audit.citation_problems_in_file(f, index_ids=set())
    assert any("PL-9999" in p and "does not resolve" in p for p in problems), problems


def test_check_32_positive_control_a_resolving_citation_is_silent(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "doc.md"
    f.write_text("See PL-9999 for detail.\n", encoding="utf-8")
    problems = audit.citation_problems_in_file(f, index_ids={"PL-9999"})
    assert problems == [], problems


def test_check_32_flags_a_padded_id_outside_a_link_target(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """NT-0019 §1.1 rule 2: "citations write the integer, never padding ... no
    exception". A padded id in plain prose (not a link target) must be flagged even when
    it does resolve.
    """
    f = tmp_path / "doc.md"
    f.write_text("See PL-01240 for detail.\n", encoding="utf-8")
    problems = audit.citation_problems_in_file(f, index_ids={"PL-1240"})
    assert any("padded id" in p for p in problems), problems


def test_check_32_does_not_flag_a_padded_id_inside_a_link_target(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "doc.md"
    f.write_text("See [PL-1240](../plans/PL-01240-slug.md) for detail.\n", encoding="utf-8")
    problems = audit.citation_problems_in_file(f, index_ids={"PL-1240"})
    assert problems == [], problems


def test_check_32_flags_a_link_whose_text_and_target_disagree(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "doc.md"
    f.write_text("See [PL-1240](../plans/PL-01241-slug.md) for detail.\n", encoding="utf-8")
    problems = audit.citation_problems_in_file(f, index_ids={"PL-1240", "PL-1241"})
    assert any("cites PL-1240" in p and "PL-1241" in p for p in problems), problems


def test_check_32_ignores_ids_inside_a_fenced_code_block(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """document-ids.md's own §1.4 directory-tree diagram carries padded ids
    (`PL-01240-batch-frame-contract.md`) inside a fenced block, illustrating the
    filename convention rather than citing a real document — must not be flagged."""
    f = tmp_path / "doc.md"
    f.write_text("```\nplans/ PL-01240-batch-frame-contract.md\n```\n", encoding="utf-8")
    problems = audit.citation_problems_in_file(f, index_ids=set())
    assert problems == [], problems


def test_check_32_is_gated_on_index_md_and_skips_cleanly_pre_migration(
    audit: types.ModuleType,
) -> None:
    """Production behaviour: on the real tree, `docs/INDEX.md` does not exist yet, so
    check 32 must skip with a note rather than reading document-ids.md's own
    illustrative, sometimes-padded ids as citation violations (see module docstring).
    """
    assert not (audit.ROOT / "INDEX.md").is_file(), "fixture assumption: no real INDEX.md"
    audit.failures.clear()
    audit.notes.clear()
    audit.check_citations()
    assert audit.failures == []
    assert any("no docs/INDEX.md yet" in n for n in audit.notes), audit.notes


# =========================================================================================
# Check 33 — supersedes/superseded_by symmetry; status vocabulary and per-family subset;
# the map-plan roll-up raise (Ruling 72).
# =========================================================================================


def test_check_33_reds_alone_on_a_status_outside_the_vocabulary(
    audit: types.ModuleType,
) -> None:
    failures = _run_all_ten(audit, (CHECKS_FIXTURES / "check33-bad-status.md",))
    assert _only_check(failures, 33), failures
    assert any("nonsense" in f for f in failures), failures


def test_check_33_reds_alone_on_asymmetric_supersedes(audit: types.ModuleType) -> None:
    failures = _run_all_ten(
        audit, (CHECKS_FIXTURES / "check33-supersedes" / "adrs",)
    )
    assert _only_check(failures, 33), failures
    assert "ADR-1930" in failures[0], failures
    assert "ADR-1931" in failures[0], failures


def test_check_33_rollup_raise_surfaces_more_than_one_live_leaf_plan(
    audit: types.ModuleType,
) -> None:
    """Ruling 72: "a slice with more than one live leaf plan is a check 33 disagreement,
    not a case to resolve silently." `doc-index.py`'s own precedence table has no
    catch-all (its last row raises); this proves check 33 surfaces that raise rather than
    swallowing it, exactly the obligation Ruling 72 §3 states for this slice.
    """
    fixture_root = FIXTURES / "w37-4-rollup-raise"
    corpus = audit._doc_index.build_corpus(fixture_root)
    problems = audit.rollup_raise_problems(corpus)
    assert len(problems) == 1, problems
    assert "PL-1910" in problems[0]
    assert "SL-1901" in problems[0]
    assert "more than one live leaf plan" in problems[0]


def test_check_33_rollup_raise_is_silent_on_the_w37_3_corpus(
    audit: types.ModuleType,
) -> None:
    """Negative control for the test above: W37-3's own fixture corpus (which Ruling 72
    was ruled to fix, and which now implements the fix) must produce *no* roll-up raise —
    proving the raise fires on the specific defect, not on every map plan indiscriminately.
    """
    corpus = audit._doc_index.build_corpus(FIXTURES / "w37-3-corpus")
    problems = audit.rollup_raise_problems(corpus)
    assert problems == [], problems


# =========================================================================================
# Check 34 — freeze (DP-7): a frozen family's diff against its merge-base touches only
# the allowed fields. Proven on the pure predicate directly: it compares an explicit
# old/new `Header` pair, which no file in `_ID_SCOPE_ROOTS` has a merge-base history for.
# =========================================================================================


def _header(audit: types.ModuleType, **overrides: object) -> object:
    """A minimal, valid `_docid.Header` for `frozen_diff_is_permitted`'s tests — every
    field defaulted to its "nothing here" value, overridden per test.
    """
    base: dict[str, object] = {
        "id": "PL-1240", "family": "plan", "kind": "leaf", "title": "t", "status": "draft",
        "created": date(2026, 9, 1), "owner": "planner", "phase": None, "work": None,
        "slice_": None, "tree": "abc1234", "plans": (), "supersedes": (),
        "superseded_by": None, "corrected_by": (), "corrects": None, "relates": (),
        "was": None, "vendored": False, "origin": None, "extra": {},
    }
    base.update(overrides)
    return audit._docid.Header(**base)


def test_check_34_refuses_a_body_change(audit: types.ModuleType) -> None:
    old = _header(audit)
    new = _header(audit)
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="original body\n", new_body="edited body\n"
    )
    assert ok is False
    assert "body changed" in reason


def test_check_34_permits_a_forward_status_change(audit: types.ModuleType) -> None:
    old = _header(audit, status="draft")
    new = _header(audit, status="active")
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="same\n", new_body="same\n"
    )
    assert ok is True, reason


def test_check_34_refuses_a_status_change_away_from_terminal(audit: types.ModuleType) -> None:
    old = _header(audit, status="closed")
    new = _header(audit, status="active")
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="same\n", new_body="same\n"
    )
    assert ok is False
    assert "terminal" in reason


def test_check_34_permits_an_appended_corrected_by_entry(audit: types.ModuleType) -> None:
    old = _header(audit, corrected_by=())
    new = _header(audit, corrected_by=("RL-99",))
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="same\n", new_body="same\n"
    )
    assert ok is True, reason


def test_check_34_refuses_a_reordered_corrected_by_entry(audit: types.ModuleType) -> None:
    old = _header(audit, corrected_by=("RL-1", "RL-2"))
    new = _header(audit, corrected_by=("RL-2", "RL-1"))
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="same\n", new_body="same\n"
    )
    assert ok is False
    assert "corrected_by" in reason


def test_check_34_refuses_an_unrelated_field_change(audit: types.ModuleType) -> None:
    old = _header(audit, title="original title")
    new = _header(audit, title="edited title")
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="same\n", new_body="same\n"
    )
    assert ok is False
    assert "title" in reason


def test_check_34_permits_a_ledger_plans_append(audit: types.ModuleType) -> None:
    old = _header(audit, family="ledger", plans=("PL-1",))
    new = _header(audit, family="ledger", plans=("PL-1", "PL-2"))
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="same\n", new_body="same\n"
    )
    assert ok is True, reason


def test_check_34_refuses_a_plans_append_on_a_non_ledger_family(
    audit: types.ModuleType,
) -> None:
    old = _header(audit, family="plan", plans=())
    new = _header(audit, family="plan", plans=("PL-2",))
    ok, reason = audit.frozen_diff_is_permitted(
        old, new, old_body="same\n", new_body="same\n"
    )
    assert ok is False
    assert "plans" in reason


def test_check_34_migration_stamp_allowance_reproduces_the_merge_base(
    audit: types.ModuleType,
) -> None:
    """Ruling 68's DP-7 disposition, the second predicate: stripping the new header and
    inverting REDIRECTS.csv's mapping must reproduce the merge-base body exactly.
    """
    old_body = "This note cites NT-0016 for background.\n"
    new_text = "---\nid: RFC-164\nfamily: proposal\n---\nThis note cites RFC-88 for background.\n"
    assert audit.frozen_file_matches_after_migration_stamp(
        old_body, new_text, redirects_inverse={"RFC-88": "NT-0016"}, allocated_ids={"RFC-164"}
    )


def test_check_34_migration_stamp_allowance_rejects_a_real_content_change(
    audit: types.ModuleType,
) -> None:
    old_body = "This note cites NT-0016 for background.\n"
    new_text = (
        "---\nid: RFC-164\nfamily: proposal\n---\n"
        "This note cites RFC-88 for background, and one extra sentence.\n"
    )
    assert not audit.frozen_file_matches_after_migration_stamp(
        old_body, new_text, redirects_inverse={"RFC-88": "NT-0016"}, allocated_ids={"RFC-164"}
    )


def test_check_34_migration_stamp_allowance_is_order_independent_under_prefix_collision(
    audit: types.ModuleType,
) -> None:
    """Found by W37-5, applying this predicate against a real multi-id `REDIRECTS.csv`
    rather than the single-entry maps every other test here uses: NT-0019's citation rule
    is the bare integer, so two live ids are routinely in a literal prefix relationship
    (`PL-1` and `PL-12` both exist in most real corpora). Inverting the shorter token
    first used to consume part of the longer one's own digits before its own map entry
    was ever reached, corrupting it and making a genuinely clean migration read as a
    violation — a false failure, not a missed one, but still a check that lied about a
    correct migration. Regression-tested here with two independent dict insertion
    orders, so the fix (apply longest `new_token` first, `scripts/audit-docs.py`) cannot
    silently regress back to depending on dict order.
    """
    old_body = "See 2026-01-01-alpha and 2026-06-01-zulu for context.\n"
    new_text = "---\nid: RL-9\n---\nSee PL-1 and PL-12 for context.\n"
    order_a = {"PL-1": "2026-01-01-alpha", "PL-12": "2026-06-01-zulu"}
    order_b = {"PL-12": "2026-06-01-zulu", "PL-1": "2026-01-01-alpha"}
    assert audit.frozen_file_matches_after_migration_stamp(
        old_body, new_text, order_a, allocated_ids={"RL-9"}
    )
    assert audit.frozen_file_matches_after_migration_stamp(
        old_body, new_text, order_b, allocated_ids={"RL-9"}
    )


def test_check_34_reds_alone_on_a_dangling_corrected_by_entry(
    audit: types.ModuleType,
) -> None:
    """The one check-34 sub-clause that *is* live over `_ID_SCOPE_ROOTS` today: "every
    `corrected_by:` entry is a record whose `corrects:` names this file." Two files in
    `tests/fixtures/docs-ids/w37-4-checks/check34-dangling-corrected-by/rulings/` — the
    frozen one (`RL-1950`) claims a corrector (`RL-1951`) that does not `corrects:` back
    to it (it corrects `RL-1999` instead). Real fixture files, not `tmp_path`: every
    check-30-39 function renders paths relative to the module's own `REPO`, and a file
    outside the real repository tree cannot be `.relative_to()`'d against it.
    """
    failures = _run_all_ten(
        audit, (CHECKS_FIXTURES / "check34-dangling-corrected-by" / "rulings",)
    )
    assert _only_check(failures, 34), failures
    assert "RL-1951" in failures[0], failures


# =========================================================================================
# Check 35 — owner: is a role filename or `maintainer`, permitted by the directory's
# README.md where one exists and declares a list.
# =========================================================================================


def test_check_35_reds_alone_on_an_unrecognised_owner(audit: types.ModuleType) -> None:
    failures = _run_all_ten(audit, (CHECKS_FIXTURES / "check35-bad-owner.md",))
    assert _only_check(failures, 35), failures
    assert "some-random-person" in failures[0], failures


def test_check_35_valid_owners_include_every_real_role_and_maintainer(
    audit: types.ModuleType,
) -> None:
    assert "maintainer" in audit._VALID_OWNERS
    for role in ("auditor", "decision-maker", "executor", "lead", "planner", "reporter", "watcher"):
        assert role in audit._VALID_OWNERS, audit._VALID_OWNERS


def test_check_35_readme_allowlist_is_enforced_when_a_readme_declares_one(
    audit: types.ModuleType,
) -> None:
    """`tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/` carries both
    `doc.md` and its own `README.md` ("Permitted owners: planner, lead"). `_ID_SCOPE_ROOTS`
    is pointed at `doc.md` directly, not the directory: `readme_owner_allowlist` looks up
    `doc.md`'s parent directory's `README.md` regardless of scope (a plain filesystem
    check), but `_id_scope_documents` would otherwise also walk the README itself in as a
    second scope document — and a bare `README.md` with no header of its own would then
    also red check 30, contaminating this check-35 proof.
    """
    fixture_dir = CHECKS_FIXTURES / "check35-readme-allowlist"
    assert (fixture_dir / "README.md").is_file(), "fixture assumption"
    failures = _run_all_ten(audit, (fixture_dir / "doc.md",))
    assert _only_check(failures, 35), failures
    assert "permitted-owner list" in failures[0], failures
    assert "permitted-owner list" in failures[0], failures


def test_check_35_no_readme_allowlist_clause_when_none_is_declared(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """No fixed README format is specified by NT-0019 anywhere (`docs/ READMEs` is
    Slice W37-10's to write); a README that exists but states no "Permitted owners:"
    line must yield `None` — no clause to enforce, not an empty (and therefore
    everything-fails) allow-list.
    """
    readme = tmp_path / "README.md"
    readme.write_text("This directory holds fixture documents.\n", encoding="utf-8")
    assert audit.readme_owner_allowlist(readme) is None


# =========================================================================================
# Check 36 — Redirects (Ruling 67/DP-2): the legacy-form sweep, its exclusion list, and
# the was:/REDIRECTS.csv clauses.
# =========================================================================================


def test_check_36_positive_control_catches_every_named_family(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 67 §4 item 2: one line per family carrying a complete legacy identifier —
    NT-0016, FR-MODEL-45, F-W9-3, F27, wf-01, Ruling 62, ADR-0001, W11-3, docs/audit/,
    .claude/notes/ — and the sweep must return every one, using the *shipped* constant.
    """
    f = tmp_path / "legacy.md"
    f.write_text(
        "NT-0016\nFR-MODEL-45\nF-W9-3\nF27\nwf-01\nRuling 62\nADR-0001\nW11-3\n"
        "docs/audit/register.md\n.claude/notes/0001-x.md\n",
        encoding="utf-8",
    )
    hits = audit.sweep_legacy_forms([f], repo_root=tmp_path)
    joined = "\n".join(hits)
    for token in ("NT-0016", "FR-MODEL-45", "F-W9-3", "F27", "wf-01", "Ruling 62",
                  "ADR-0001", "W11-3", "docs/audit/", ".claude/notes/"):
        assert token in joined, (token, hits)


def test_check_36_pattern_does_not_self_match_its_own_bare_prefix(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 67 Part 1's exact finding: NT-0019 §7 (d) as originally written matched its
    own text on `NT-00`, the bare prefix fragment inside its own alternation, because it
    required no digits to follow. The fixed pattern must not match a bare `NT-00`
    fragment that is not followed by two more digits — proving the "complete identifier,
    never a proper prefix" rule directly on the exact string that broke the original.
    """
    f = tmp_path / "self-reference.md"
    f.write_text("the alternation begins NT-00|F-W[0-9]|...\n", encoding="utf-8")
    hits = audit.sweep_legacy_forms([f], repo_root=tmp_path)
    assert hits == [], hits


def test_check_36_exclusion_entries_are_load_bearing(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 67 §4 item 1: removing an exclusion entry must make the sweep return at
    least one hit from the file class that entry names — proving the entry is not dead
    weight. `REDIRECTS.csv` is the one entry that exists today.
    """
    redirects = tmp_path / "REDIRECTS.csv"
    redirects.write_text("old_id,new_id,old_path,new_path\nNT-0016,RFC-88,a,b\n", encoding="utf-8")

    excluded = audit.sweep_legacy_forms(
        [redirects], repo_root=tmp_path, excluded_paths=("REDIRECTS.csv",)
    )
    assert excluded == [], excluded

    not_excluded = audit.sweep_legacy_forms([redirects], repo_root=tmp_path, excluded_paths=())
    assert any("NT-0016" in hit for hit in not_excluded), not_excluded


# W37-5's seven `tests/fixtures/docs-migration/` entries, added to the shipped
# `LEGACY_FORM_EXCLUDED_PATHS` alongside the pre-existing `docs/REDIRECTS.csv` one tested
# above. Listed here rather than read back off `audit.LEGACY_FORM_EXCLUDED_PATHS` so a
# stray removal from the shipped tuple fails this test loudly (a missing path 404s the
# `is_file()` assert) instead of silently shrinking the parametrize set to green.
_W37_5_FIXTURE_EXCLUSIONS: tuple[str, ...] = (
    "tests/fixtures/docs-migration/docs/adr/0001-example-decision.md",
    "tests/fixtures/docs-migration/docs/notes/0001-example-note.md",
    "tests/fixtures/docs-migration/docs/plans/2026-08-12-example-rulings.md",
    "tests/fixtures/docs-migration/docs/roadmap.md",
    "tests/fixtures/docs-migration/docs/specs/00-overview.md",
    "tests/fixtures/docs-migration/.claude/skills/vendored-example-skill/SKILL.md",
    "tests/fixtures/docs-migration/.claude/skills/vendored-example-skill/references/extra.md",
)


@pytest.mark.parametrize("entry", _W37_5_FIXTURE_EXCLUSIONS)
def test_check_36_w37_5_fixture_exclusions_are_load_bearing(
    audit: types.ModuleType, entry: str
) -> None:
    """Ruling 67 §4 item 1, applied to the seven `tests/fixtures/docs-migration/` entries
    W37-5 added to the shipped `LEGACY_FORM_EXCLUDED_PATHS` (contrast
    `test_check_36_exclusion_entries_are_load_bearing` above, which proves the same
    property for the one pre-existing entry, `docs/REDIRECTS.csv`).

    Each is excluded only because the fixture corpus's own *discovery-defining* legacy
    shape — the thing that makes it recognisable to `migrate` as that shape at all, not
    incidental prose — is itself a legacy form: an ADR's own `ADR-0001` title, a note's
    own `NT-0001` title, a multi-ruling file's own `## Ruling N` headings, the roadmap
    fixture's own `W1-1`/`W1-2` row keys, the spec fixture's own `**FR-EX-1**`-shaped bold
    ids, and the vendored pair's shared `FR-EX-1` citation (proving NT-0019 §1.5's
    vendored carve-out needs the same token on both sides of the manifest boundary).
    These are real, permanently un-migrated test fixtures under git, not `tmp_path`
    synthetic input — unlike a governed document, a fixture's citations are never
    rewritten, so its exclusion never shrinks (Ruling 67 §2's residue class names this
    exact case: "the fixtures ... of the migration").

    This sweeps the real (unfiltered) `docs-migration` file straight off disk against the
    shipped constant with and without the one entry under test, proving each is load
    bearing on its own: with the real constant, the file contributes no hit; with that
    single entry removed (every other exclusion, `docs/REDIRECTS.csv` included, stays in
    force), the sweep must return at least one hit, and every hit returned must come from
    this exact file and no other — the sweep is scoped to `[path]` alone, so there is
    nowhere else a hit could come from.
    """
    path = ROOT / entry
    assert path.is_file(), path  # the entry must still name a real, tracked fixture file

    excluded_with_entry = audit.sweep_legacy_forms([path], repo_root=ROOT)
    assert excluded_with_entry == [], excluded_with_entry

    reduced = tuple(p for p in audit.LEGACY_FORM_EXCLUDED_PATHS if p != entry)
    assert len(reduced) == len(audit.LEGACY_FORM_EXCLUDED_PATHS) - 1, entry

    hits_without_entry = audit.sweep_legacy_forms([path], repo_root=ROOT, excluded_paths=reduced)
    assert hits_without_entry != [], entry
    assert all(hit.startswith(entry + ":") for hit in hits_without_entry), hits_without_entry


def test_check_36_was_lines_are_excluded_wherever_they_appear(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "migrated.md"
    f.write_text("---\nwas: NT-0016\n---\n\nNo other legacy form here.\n", encoding="utf-8")
    hits = audit.sweep_legacy_forms([f], repo_root=tmp_path)
    assert hits == [], hits


def test_check_36_one_shared_constant_drives_the_sweep_entirely(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 67 §4 item 3 ("one definition, not two"): mutating the pattern list must
    change `sweep_legacy_forms`'s behaviour — proving the function has no second,
    hardcoded copy of the pattern anywhere in its own body.
    """
    import re

    f = tmp_path / "custom.md"
    f.write_text("CUSTOM-TOKEN-123\n", encoding="utf-8")
    assert audit.sweep_legacy_forms([f], repo_root=tmp_path) == []

    custom_patterns = (("custom token", re.compile(r"\bCUSTOM-TOKEN-\d+\b")),)
    hits = audit.sweep_legacy_forms([f], repo_root=tmp_path, patterns=custom_patterns)
    assert any("CUSTOM-TOKEN-123" in hit for hit in hits), hits


def test_check_36_reds_alone_when_a_was_field_has_no_redirects_row(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Live clause today: `was:` on an in-scope header with no matching REDIRECTS.csv
    row must fail. Built under `tmp_path`, not a committed fixture: a real (if
    empty-of-rows) `REDIRECTS.csv` tracked in the repository trips
    `backend/tests/test_lineage.py::test_no_reference_rows_are_bundled_in_the_repository`
    (FR-DATA-32) — found on this slice's own CI run, which scans the whole tree for
    `*.csv`/`*.parquet`/`*.xlsx` outside two narrow, unrelated exemptions and does not
    know or care that this one is empty. `check_redirects` is called directly (not
    through `_run_all_ten`'s ten-check orchestrator) specifically so this test needs no
    `audit.REPO` reassignment: the orchestrator's other checks (30's field-policy note,
    39's whole-tree scan) depend on `REPO`/`_TEMPLATES_DIR` staying mutually consistent,
    which a `tmp_path` tree run through only `check_redirects` never needs to be.
    """
    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    (docs_root / "REDIRECTS.csv").write_text(
        "old_id,new_id,old_path,new_path\n", encoding="utf-8"
    )
    doc = docs_root / "doc.md"
    doc.write_text(
        "---\nfamily: reference\ntitle: t\nstatus: active\ncreated: 2026-09-02\n"
        "owner: maintainer\ntree: fixture\nwas: NT-0099\ncorrected_by: []\nrelates: []\n"
        "---\n\n# t\n\nDeliberately not restated: repeating the was: value here would "
        "also trip clause 3's sweep.\n",
        encoding="utf-8",
    )
    setattr(audit, "ROOT", docs_root)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    setattr(audit, "_ID_SCOPE_ROOTS", (doc,))  # noqa: B010 -- ditto
    audit.failures.clear()
    audit.notes.clear()
    audit.check_redirects()
    assert audit.failures == ["check 36: `was: NT-0099` has no docs/REDIRECTS.csv row"]
    assert "NT-0099" in audit.failures[0]


def test_check_36_is_gated_on_redirects_csv_and_skips_cleanly_pre_migration(
    audit: types.ModuleType,
) -> None:
    """Production behaviour, found while building this slice: the sweep is a
    *post*-migration invariant. Before `docs/REDIRECTS.csv` exists, document-ids.md's own
    lift of NT-0019 legitimately cites NT-0016, NT-0015, NT-0003 and Ruling 64 in prose,
    and names `docs/audit/` describing its own dissolution — indistinguishable from a
    survivor by pattern alone. Running the sweep unconditionally on the real tree reds on
    all five; this proves the gate, not just asserts it.
    """
    assert not (audit.ROOT / "REDIRECTS.csv").is_file(), "fixture assumption: no real REDIRECTS.csv"
    audit.failures.clear()
    audit.notes.clear()
    setattr(audit, "_ID_SCOPE_ROOTS", (audit.ROOT / "process" / "document-ids.md",))  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.check_redirects()
    assert audit.failures == [], audit.failures
    assert any("post-migration invariant" in n for n in audit.notes), audit.notes


# =========================================================================================
# Check 37 — shape: required ## sections per family template.
# =========================================================================================


def test_check_37_reds_alone_on_a_missing_required_section(audit: types.ModuleType) -> None:
    failures = _run_all_ten(audit, (CHECKS_FIXTURES / "check37" / "adrs",))
    assert _only_check(failures, 37), failures
    assert "Consequences" in failures[0], failures


def test_check_37_reference_family_requires_no_section(audit: types.ModuleType) -> None:
    """`docs/_templates/REFERENCE.md`'s own comment: "NT-0019 does not prescribe this
    family's body shape" — an empty derived list means nothing is required, checked
    directly against the real template.
    """
    assert audit.required_sections("reference") == ()


def test_check_37_every_document_family_template_declares_at_least_one_section(
    audit: types.ModuleType,
) -> None:
    for family in ("decision", "closure", "finding", "ledger", "plan", "proposal",
                   "ruling", "research", "workflow"):
        assert audit.required_sections(family), family


# =========================================================================================
# Check 38 — loop signal, warn-only. Never fails the gate: the proof is that it never
# calls fail(), not that some input reds it (there is none, by NT-0019's own design).
# =========================================================================================


def test_check_38_never_fails_regardless_of_scope(audit: types.ModuleType) -> None:
    for roots in (
        (),
        (CHECKS_FIXTURES / "check30-unknown-field.md",),
        (audit._TEMPLATES_DIR,),
    ):
        audit.failures.clear()
        audit.notes.clear()
        setattr(audit, "_ID_SCOPE_ROOTS", roots)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
        audit.check_loop_signal()
        assert audit.failures == [], (roots, audit.failures)
        assert audit.notes, "check 38 must still say something, even though it never fails"


# =========================================================================================
# Check 39 — docs/INDEX.md byte-stable; PR-title/ledger cross-reference (noted, not
# checked — needs GitHub context this tool does not have).
# =========================================================================================


def test_check_39_reds_when_records_exist_but_index_is_missing(
    audit: types.ModuleType,
) -> None:
    corpus_root = FIXTURES / "w37-3-corpus"
    assert not (corpus_root / "INDEX.md").exists(), "fixture must not carry a committed INDEX.md"
    setattr(audit, "ROOT", corpus_root)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.failures.clear()
    audit.notes.clear()
    audit.check_index_stable()
    assert len(audit.failures) == 1, audit.failures
    assert "check 39:" in audit.failures[0]
    assert "does not" in audit.failures[0]


def test_check_39_reds_on_a_stale_index(audit: types.ModuleType, tmp_path: pathlib.Path) -> None:
    import shutil

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "w37-3-corpus", root)
    fresh = audit._doc_index.render_index(audit._doc_index.build_corpus(root))
    (root / "INDEX.md").write_text(fresh + "\n", encoding="utf-8")  # one byte stale

    setattr(audit, "ROOT", root)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.failures.clear()
    audit.notes.clear()
    audit.check_index_stable()
    assert len(audit.failures) == 1, audit.failures
    assert "stale" in audit.failures[0]


def test_check_39_passes_on_a_freshly_generated_index(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    import shutil

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "w37-3-corpus", root)
    corpus = audit._doc_index.build_corpus(root)
    (root / "INDEX.md").write_text(audit._doc_index.render_index(corpus), encoding="utf-8")

    setattr(audit, "ROOT", root)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.failures.clear()
    audit.notes.clear()
    audit.check_index_stable()
    assert audit.failures == [], audit.failures
    assert any("byte-stable" in n for n in audit.notes), audit.notes


def test_check_39_is_silent_on_the_real_pre_migration_tree(audit: types.ModuleType) -> None:
    assert not (audit.ROOT / "INDEX.md").is_file(), "fixture assumption: no real INDEX.md"
    audit.failures.clear()
    audit.notes.clear()
    audit.check_index_stable()
    assert audit.failures == [], audit.failures
    assert any("nothing to check yet" in n for n in audit.notes), audit.notes


# =========================================================================================
# F76: `check_index_stable`'s `_doc_index.build_corpus(ROOT)` call is the *last* of the
# ten `check_ids_30_39()` makes, which `main()` runs immediately before six further
# checks with no exception boundary between any of them
# (`check_open_question_mirror_status`, `check_finding_citations`,
# `check_process_core_drift`, `check_process_core_digest`,
# `check_plan_acceptance_standard` [check 28], `check_register_grammar` [check 29]). An
# uncaught exception there — a malformed header anywhere in the real tree — used to abort
# `main()` before any of the six ran, and before the report of every check that already
# ran was ever printed. Two distinct, verified ways `build_corpus` can raise: a
# `WK-`/`SL-` row block naming an unknown field (`_doc_index.HeaderError`, not this
# module's own `_docid.HeaderError` — see the guard's own comment) and a row block whose
# `created:` is not ISO-8601 (`_row_header_from_raw`'s unguarded `date.fromisoformat`
# raises `ValueError`, a second, distinct escape `HeaderError`-only handling would miss).
# =========================================================================================


def test_check_39_corpus_build_failure_is_a_clean_fail_not_a_crash(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The row field named here (`bogus_field`) is deliberately not `tree` — NT-0019's
    own F76 trigger, and the field Ruling 79 is correcting `doc-index.py`'s
    `_ROW_FIELDS` to accept, in parallel with this guard. A fixture pinned to `tree`
    would stop reproducing `HeaderError` the moment that fix lands, silently turning
    this proof into one that passes for the wrong reason. `bogus_field` is not, and can
    never legitimately become, an NT-0019 §1.5 row field.
    """
    import shutil

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "w37-3-corpus", root)
    with (root / "roadmap.md").open("a", encoding="utf-8") as fh:
        fh.write(
            "\n### WK-9999 — Malformed fixture row (deliberately broken)\n\n"
            "```yaml\n"
            "id: WK-9999\n"
            "family: work\n"
            "title: Malformed fixture row\n"
            "status: active\n"
            "phase: P9\n"
            "bogus_field: this must never become a legal NT-0019 row field\n"
            "```\n"
        )
    # The fixture really does reproduce the crash this guard exists for — proven
    # directly against the unguarded mechanism, not assumed from the fixture's own
    # construction (the trap this row's brief names: does it red for the reason I think
    # it reds?).
    with pytest.raises(audit._doc_index.HeaderError, match="bogus_field"):
        audit._doc_index.build_corpus(root)

    setattr(audit, "ROOT", root)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.failures.clear()
    audit.notes.clear()
    audit.check_index_stable()  # must not raise
    assert len(audit.failures) == 1, audit.failures
    assert "check 39:" in audit.failures[0]
    assert "bogus_field" in audit.failures[0], audit.failures


def test_check_39_corpus_build_failure_on_a_malformed_row_date_is_also_a_clean_fail(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The second, distinct way `build_corpus` can crash: `created:` is itself a legal
    row field (`doc-index.py`'s `_ROW_FIELDS`), so `_parse_row_block` accepts the line
    without complaint — the crash is `_row_header_from_raw`'s own unguarded
    `date.fromisoformat`, which raises `ValueError`, never `_docid.HeaderError`. A guard
    written to catch only `HeaderError` would still let this one propagate.
    """
    import shutil

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "w37-3-corpus", root)
    with (root / "roadmap.md").open("a", encoding="utf-8") as fh:
        fh.write(
            "\n### WK-9998 — Malformed fixture row (deliberately broken date)\n\n"
            "```yaml\n"
            "id: WK-9998\n"
            "family: work\n"
            "title: Malformed fixture row bad date\n"
            "status: active\n"
            "phase: P9\n"
            "created: not-a-real-date\n"
            "```\n"
        )
    with pytest.raises(ValueError, match="not-a-real-date"):
        audit._doc_index.build_corpus(root)

    setattr(audit, "ROOT", root)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.failures.clear()
    audit.notes.clear()
    audit.check_index_stable()  # must not raise
    assert len(audit.failures) == 1, audit.failures
    assert "check 39:" in audit.failures[0]


def test_check_ids_30_39_completes_when_check_39s_corpus_is_malformed(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """F76's own claim, proven at the exact call site the finding names: before the
    guard, this malformed corpus made `check_ids_30_39()` itself raise — which, inside
    `main()`, aborts the script before `check_open_question_mirror_status`,
    `check_finding_citations`, `check_process_core_drift`, `check_process_core_digest`,
    `check_plan_acceptance_standard` (check 28) and `check_register_grammar` (check 29)
    ever run, and before any note from the checks that already ran is ever printed.
    `check_ids_30_39()` returning normally is the exact mechanism by which `main()`'s
    next statement — and the six checks after it — are reached at all, so this is the
    orchestrator-level proof; `test_the_real_tree_passes_all_ten_checks` below already
    covers the equivalent real-tree, real-`main()` shape end to end when nothing is
    broken.
    """
    import shutil

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "w37-3-corpus", root)
    with (root / "roadmap.md").open("a", encoding="utf-8") as fh:
        fh.write(
            "\n### WK-9997 — Malformed fixture row (deliberately broken)\n\n"
            "```yaml\n"
            "id: WK-9997\n"
            "family: work\n"
            "title: Malformed fixture row\n"
            "status: active\n"
            "phase: P9\n"
            "bogus_field: this must never become a legal NT-0019 row field\n"
            "```\n"
        )
    setattr(audit, "ROOT", root)  # noqa: B010 -- mypy needs setattr here; see _run_all_ten's comment
    audit.failures.clear()
    audit.notes.clear()
    audit.check_ids_30_39()  # must not raise — the exact call site F76 names
    assert any(f.startswith("check 39:") for f in audit.failures), audit.failures


def test_doc_index_header_error_is_not_this_modules_docid_header_error(
    audit: types.ModuleType,
) -> None:
    """The trap the guard's own comment names, checked directly rather than trusted:
    `doc-index.py` reloads `scripts/_docid.py` under its own module instance
    (`scripts/doc-index.py:85-90`) instead of sharing `audit-docs.py`'s, so
    `_doc_index.HeaderError` and `_docid.HeaderError` are two distinct class objects
    built from the same source — `except _docid.HeaderError` around a `_doc_index` call
    would type-check and silently fail to match. If this test ever starts failing (the
    two becoming the same object, e.g. via a future shared-loader refactor), the guard's
    `except` clause should be revisited, not this test weakened.
    """
    assert audit._docid.HeaderError is not audit._doc_index.HeaderError


# =========================================================================================
# "A check that examines zero documents and passes is indistinguishable from a check
# that works" unless its own note says so. Measured directly against the real,
# unmodified pre-migration tree — today's actual state, where checks 31, 32, 34, 36, 38
# and 39 examine zero governed documents and checks 30, 33, 35 and 37 examine the same
# one (`document-ids.md`) — never against a fixture built to make every check non-zero,
# which would prove nothing about the blind spot this exists to close.
# =========================================================================================


def test_every_check_30_to_39_reports_how_many_documents_it_examined(
    audit: types.ModuleType,
) -> None:
    """Every one of the ten must print at least one note starting `check N:` that
    carries an explicit digit — a qualitative "skipped" or "nothing to warn about" reads
    identical whether the check ran over one document or none, which is exactly the
    invisible-zero condition this proves closed. Digit presence, not a specific count:
    the real tree's own numbers (0 vs 1, which check finds which) are asserted more
    precisely by each check's own dedicated tests above; this test's job is only that
    every one of the ten states *a* number, on the exact input where it is easiest to
    state none.
    """
    audit.failures.clear()
    audit.notes.clear()
    audit.check_ids_30_39()
    for n in range(30, 40):
        prefix = f"check {n}:"
        own_notes = [note for note in audit.notes if note.startswith(prefix)]
        assert own_notes, (n, audit.notes)
        # The digit must appear *after* the prefix: "check 32:" already contains "3"
        # and "2" in the check number itself, so scanning the whole note would pass
        # trivially on every check regardless of whether it ever states a count —
        # exactly the kind of check that cannot attest to its own coverage.
        assert any(
            any(c.isdigit() for c in note[len(prefix):]) for note in own_notes
        ), (n, own_notes)


# =========================================================================================
# The whole-tree acceptance line this slice's plan states directly: the real audit must
# exit 0, and the two sibling CI steps this slice wires in must also exit 0 pre-migration.
# =========================================================================================


def test_the_real_tree_passes_all_ten_checks() -> None:
    import subprocess

    result = subprocess.run(
        ["python3", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed." in result.stdout, result.stdout
    for n in range(30, 40):
        assert f"check {n}" in result.stdout, (n, result.stdout)


def test_doc_id_check_exits_0_on_the_real_tree() -> None:
    import subprocess

    result = subprocess.run(
        ["python3", str(ROOT / "scripts" / "doc-id.py"), "check"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_doc_index_check_exits_0_on_the_real_tree() -> None:
    import subprocess

    result = subprocess.run(
        ["python3", str(ROOT / "scripts" / "doc-index.py"), "--check"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# =========================================================================================
# Check 35, second clause — F83's register of files that cannot carry a header, and the
# condition-2 reconciliation that keeps it equal to the tree.
#
# Every proof below runs against the **real, unmodified corpus** rather than a fixture:
# the thing under test is a statement about this repository's own files, and a fixture
# tree would prove only that the reconciliation works on a tree nobody ships. What each
# test mutates is the *register*, which is the artifact F83 makes falsifiable.
# =========================================================================================


def _register_without(audit: types.ModuleType, path: str) -> tuple[object, ...]:
    """The real register minus the entry for `path`, asserting it was actually there —
    a "remove X" helper that silently removes nothing turns every test using it green.
    """
    kept = tuple(e for e in audit.UNSTAMPABLE_EXEMPTIONS if e.path != path)
    assert len(kept) == len(audit.UNSTAMPABLE_EXEMPTIONS) - 1, path
    return kept


def _run_check_35(audit: types.ModuleType) -> list[str]:
    audit.failures.clear()
    audit.notes.clear()
    audit.check_owner()
    return list(audit.failures)


def test_f83_register_reconciles_clean_against_the_real_tree(
    audit: types.ModuleType,
) -> None:
    """The positive control. It has to come first: every red-on-broken-input test below
    is worthless if the check reds on the unmodified tree too, and a reconciliation that
    is *always* red is indistinguishable from one that is always right.
    """
    assert _run_check_35(audit) == []
    note = next(n for n in audit.notes if "F83 register" in n)
    # The note must state both live populations. A reconciliation reporting no numbers
    # reads identically whether it compared 65 entries against 415 files or nothing
    # against nothing — the invisible-zero condition checks 30-39 are pinned against.
    assert f"{len(audit.UNSTAMPABLE_EXEMPTIONS)} exemption(s)" in note
    assert "file(s) in NT-0019's stamp set" in note


def test_f83_register_reds_naming_an_unstampable_file_it_does_not_list(
    audit: types.ModuleType,
) -> None:
    """F83's falsifiable clause, verbatim: "an unstamped in-scope file absent from the
    exempt list must red". Proven by dropping a real entry rather than by planting a
    file, so the file the check names is one that genuinely exists in this tree.
    """
    dropped = "docs/contracts/openapi/gi-pricing.yaml"
    setattr(audit, "UNSTAMPABLE_EXEMPTIONS", _register_without(audit, dropped))  # noqa: B010
    failures = _run_check_35(audit)
    assert len(failures) == 1, failures
    assert dropped in failures[0]
    assert "not in the F83 exemption register" in failures[0]


def test_f83_register_reds_on_an_entry_for_a_file_that_can_carry_a_header(
    audit: types.ModuleType,
) -> None:
    """The other direction. `docs/contracts/README.md` is markdown, sits in the same
    directory as the 60 exempt artifacts, and is the file F83 singles out as deliberately
    *not* exempt ("the exemption is scoped to the files that physically cannot, not to
    the directory"). Exempting it would hide a stampable file from checks 30-39.
    """
    entry = audit.UnstampableExemption("docs/contracts/README.md", "r", "r")
    setattr(audit, "UNSTAMPABLE_EXEMPTIONS", (*audit.UNSTAMPABLE_EXEMPTIONS, entry))  # noqa: B010
    failures = _run_check_35(audit)
    assert len(failures) == 1, failures
    assert "docs/contracts/README.md" in failures[0]
    assert "CAN carry a header" in failures[0]


def test_f83_register_names_both_sides_when_the_two_totals_cancel(
    audit: types.ModuleType,
) -> None:
    """**The property F83 condition 2 actually asks for**, and the one a total-only check
    cannot have: two errors in opposite directions leave the count unchanged.

    Here one real entry is dropped and one bogus entry added, so `len(register)` is
    *exactly* what it was and `len(cannot)` is *exactly* what it was — a check that
    compared the two totals passes this input while the register disagrees with the tree
    in two places. Ruling 83's rule ("name every unmatched unit, never compare counts")
    and `.claude/skills/docs-audit` §"a total validates the total, and nothing else",
    which was written the same day after precisely this failure.
    """
    dropped = "docs/process/delivery-process.core.json"
    bogus = audit.UnstampableExemption("docs/contracts/README.md", "r", "r")
    mutated = (*_register_without(audit, dropped), bogus)
    assert len(mutated) == len(audit.UNSTAMPABLE_EXEMPTIONS)  # the totals cancel
    setattr(audit, "UNSTAMPABLE_EXEMPTIONS", mutated)  # noqa: B010

    failures = _run_check_35(audit)
    assert len(failures) == 2, failures
    assert any(dropped in f and "not in the F83 exemption register" in f for f in failures)
    assert any("docs/contracts/README.md" in f and "CAN carry a header" in f for f in failures)


def test_f83_register_reds_on_a_stale_entry_naming_no_tracked_file(
    audit: types.ModuleType,
) -> None:
    """An entry outliving the file it exempts. Distinguished from the "can carry a
    header" case by its own message, because the fixes differ: one is a deletion, the
    other is a stamping.
    """
    entry = audit.UnstampableExemption("docs/contracts/schemas/gone.json", "r", "r")
    setattr(audit, "UNSTAMPABLE_EXEMPTIONS", (*audit.UNSTAMPABLE_EXEMPTIONS, entry))  # noqa: B010
    failures = _run_check_35(audit)
    assert len(failures) == 1, failures
    assert "not in NT-0019's stamp set" in failures[0]


def test_f83_register_reds_on_a_duplicated_entry(audit: types.ModuleType) -> None:
    """A duplicate inflates the register against the tree while every path in it is
    individually legitimate — the one corruption that dedup-by-dict would otherwise
    swallow in silence.
    """
    entry = audit.UNSTAMPABLE_EXEMPTIONS[0]
    setattr(audit, "UNSTAMPABLE_EXEMPTIONS", (*audit.UNSTAMPABLE_EXEMPTIONS, entry))  # noqa: B010
    failures = _run_check_35(audit)
    assert any("listed twice" in f and entry.path in f for f in failures), failures


def test_f83_register_reds_on_an_entry_missing_its_reason_or_ruling(
    audit: types.ModuleType,
) -> None:
    """F83 condition 1: "an exemption list whose entries carry no justification is
    indistinguishable from a list of things nobody got round to". The dataclass forces
    both fields to be *passed*; this is what forces them to be non-empty.
    """
    real = audit.UNSTAMPABLE_EXEMPTIONS[0]
    for blanked in (
        audit.UnstampableExemption(real.path, "", real.ruling),
        audit.UnstampableExemption(real.path, real.reason, "   "),
    ):
        mutated = (blanked, *audit.UNSTAMPABLE_EXEMPTIONS[1:])
        setattr(audit, "UNSTAMPABLE_EXEMPTIONS", mutated)  # noqa: B010
        failures = _run_check_35(audit)
        assert any("F83 condition 1" in f for f in failures), (blanked, failures)


def test_unstampable_reason_refuses_a_non_vendored_file_that_will_not_parse(
    audit: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The conjunction in `unstampable_reason` is load-bearing and must not loosen to
    "anything that raises HeaderError". A *non*-vendored markdown file with broken front
    matter is a defect to fix, not a file to exempt: if it were exemptible, the easiest
    way to silence checks 30-39 on any document would be to corrupt its header.

    Proven on the real tree's own markdown, which is non-vendored by construction — every
    one of them must come back stampable.
    """
    for rel in ("docs/README.md", "docs/roadmap.md", "CLAUDE.md"):
        assert audit.unstampable_reason(rel) is None, rel
    # …and the three vendored manifests that *do* fail to parse must come back exempt.
    assert audit.unstampable_reason(".claude/skills/vue-best-practices/SKILL.md") is not None


def test_nt0019_stamp_set_is_the_ruled_corpus_measured_against_git(
    audit: types.ModuleType,
) -> None:
    """Coverage validated from **outside** the check.

    Nothing inside check 35 can notice that `nt0019_stamp_set` has silently narrowed: a
    smaller stamp set produces fewer unstampable files, and the reconciliation stays
    green while the check has stopped looking. So the corpus is pinned here against
    `git ls-files` directly rather than against a second copy of the same predicate.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        capture_output=True, check=True,
    ).stdout.decode().split("\x00")
    tracked = [p for p in tracked if p]
    stamp_set = set(audit.nt0019_stamp_set())

    # 1. Every tracked file under docs/ — RFC §4's "every file under `docs/`". This is
    #    the clause that carries all 62 non-markdown exemptions; if it narrows to `*.md`
    #    the register silently becomes a list of three.
    docs = {p for p in tracked if p.startswith("docs/")}
    assert docs
    assert docs <= stamp_set

    # 2. The three `.claude/` roots, each named separately: a single "some .claude file
    #    is present" assertion passes while two of the three globs are broken.
    for prefix in (".claude/roles/", ".claude/agents/"):
        members = {p for p in tracked if p.startswith(prefix)}
        assert members, prefix
        assert members <= stamp_set, prefix
    manifests = {
        p for p in tracked
        if p.startswith(".claude/skills/") and p.endswith("/SKILL.md") and p.count("/") == 3
    }
    assert manifests
    assert manifests <= stamp_set

    # 3. Every tracked README.md, wherever it lives — the clause derived from what §5.2
    #    reaches rather than from the RFC's table of six, which omits
    #    `.claude/notes/README.md`.
    readmes = {p for p in tracked if p.rsplit("/", 1)[-1] == "README.md"}
    assert readmes
    assert readmes <= stamp_set

    # 4. Nothing untracked leaks in. The corpus is `git ls-files`, never a working-tree
    #    walk: a walk picks up `.venv/` and `graphify-out/`, which differ between two
    #    checkouts of the same commit (`scripts/doc-id.py` records the measurement).
    assert stamp_set <= set(tracked)

    # 5. The set is exactly its four clauses — no fifth source, no accidental widening.
    assert stamp_set == docs | manifests | readmes | {
        p for p in tracked if p.startswith((".claude/roles/", ".claude/agents/"))
    }


def test_f83_reconciliation_reds_when_the_corpus_cannot_be_read(
    audit: types.ModuleType,
) -> None:
    """`audit-docs.py`'s first git dependency, failing.

    The dangerous shape is not a traceback, it is a *pass*: an unreadable corpus yields
    zero unstampable files, which reconciles against any register as cleanly as a
    perfectly correct one. So the failure has to be raised, not inferred from emptiness.
    """
    def boom() -> list[str]:
        raise RuntimeError("could not invoke git: [Errno 2] No such file or directory")

    setattr(audit, "nt0019_stamp_set", boom)  # noqa: B010
    failures = _run_check_35(audit)
    assert len(failures) == 1, failures
    assert "cannot enumerate NT-0019's stamp set" in failures[0]
    assert "could not invoke git" in failures[0]


# =========================================================================================
# Check 35, third clause — F83 condition 2 over the ENFORCED scope, proven by simulating
# W37-6's widened `_ID_SCOPE_ROOTS` rather than waiting for it.
#
# A check that is vacuous today and first executes inside the irreversible commit is the
# hazard this slice exists to remove: printing a zero keeps it from reading as an
# invisible zero, and is not the same as having run it. `.claude/skills/python-test`
# §"a discovery call is a claim; simulate the pending change".
# =========================================================================================

#: NT-0019 §1.11 check 30's own words for the post-migration scope: "every file under
#: `docs/`, every charter, skill and agent".
def _widened_roots(audit: types.ModuleType) -> tuple[pathlib.Path, ...]:
    return (
        audit.ROOT,
        audit.REPO / ".claude" / "roles",
        audit.REPO / ".claude" / "skills",
        audit.REPO / ".claude" / "agents",
    )


def _post_migration_roots(audit: types.ModuleType) -> tuple[pathlib.Path, ...]:
    """The widened scope as it stands *after* the migration: everything stampable
    stamped, leaving only the files that cannot be.

    `_id_scope_documents` yields a *file* root verbatim — only *directory* roots go
    through its markdown glob — so a tuple of file paths models an arbitrary scope
    exactly. That is the whole reason this simulation is possible without a fixture tree.
    """
    registered = {e.path for e in audit.UNSTAMPABLE_EXEMPTIONS}
    roots: list[pathlib.Path] = []
    for rel in audit.nt0019_stamp_set():
        path = audit.REPO / rel
        try:
            header = audit._docid.parse_header(path)
        except audit._docid.HeaderError:
            header = None
        if header is not None or (rel in registered and rel.endswith(".md")):
            roots.append(path)
    return tuple(roots)


def test_scope_clause_reds_from_inside_the_migration_commit(
    audit: types.ModuleType,
) -> None:
    """D14's "enforcement red from the migration PR", proven now rather than discovered
    then. Widen the roots without stamping anything and clause (b) must red in bulk — a
    green here would mean the clause cannot see the migration it exists to gate.
    """
    setattr(audit, "_ID_SCOPE_ROOTS", _widened_roots(audit))  # noqa: B010
    audit.failures.clear()
    unstamped = audit._check_scope_unstamped_are_registered()
    assert unstamped > 300, unstamped
    assert len(audit.failures) > 300, len(audit.failures)


def test_scope_clause_is_green_once_the_migration_has_stamped_everything(
    audit: types.ModuleType,
) -> None:
    """The state W37-6 has to reach: the only unstamped files left in the enforced scope
    are the ones the register accounts for. The positive control for the test below.
    """
    setattr(audit, "_ID_SCOPE_ROOTS", _post_migration_roots(audit))  # noqa: B010
    audit.failures.clear()
    unstamped = audit._check_scope_unstamped_are_registered()
    assert unstamped == 3, unstamped  # the three vendored manifests, and only those
    assert audit.failures == []


def test_scope_clause_reds_by_name_on_an_unregistered_unstamped_file_in_scope(
    audit: types.ModuleType,
) -> None:
    """F83's falsifiable clause under the scope it was written for. Identical input to
    the test above but for one register entry, so the difference in outcome is
    attributable to the register and to nothing else.
    """
    dropped = ".claude/skills/vue-best-practices/SKILL.md"
    kept = tuple(e for e in audit.UNSTAMPABLE_EXEMPTIONS if e.path != dropped)
    assert len(kept) == len(audit.UNSTAMPABLE_EXEMPTIONS) - 1, dropped
    setattr(audit, "_ID_SCOPE_ROOTS", _post_migration_roots(audit))  # noqa: B010
    setattr(audit, "UNSTAMPABLE_EXEMPTIONS", kept)  # noqa: B010
    audit.failures.clear()
    audit._check_scope_unstamped_are_registered()
    assert len(audit.failures) == 1, audit.failures
    assert dropped in audit.failures[0]
    assert "not in the F83 exemption register" in audit.failures[0]


def test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts(
    audit: types.ModuleType,
) -> None:
    """**`F87` discharged, on the selector rather than on the roots.**

    This test replaces `test_widening_the_scope_roots_alone_reaches_no_non_markdown_file`,
    which pinned the defect: `_id_scope_documents` expanded a directory root with
    `rglob("*.md")`, so a fully widened scope reached **3** of the register's 65 — the
    vendored manifests, which are markdown — and **none** of the 62 non-`.md` files the
    register mostly consists of. The glob was the gate, not the roots, and F87's own
    falsifiable clause says so: *"not discharged by widening `_ID_SCOPE_ROOTS`, and not by
    checks 30-39 passing"*.

    The assertion is therefore made on one of the 62 rather than on a fixture: a real
    `.json` under `docs/contracts/`, named from the register itself so this cannot pass
    against a file the register does not carry.
    """
    setattr(audit, "_ID_SCOPE_ROOTS", _widened_roots(audit))  # noqa: B010
    rels = {p.relative_to(audit.REPO).as_posix() for p in audit._id_scope_documents()}
    assert rels, "the widened scope collected nothing at all — the simulation is broken"

    registered = {e.path for e in audit.UNSTAMPABLE_EXEMPTIONS}
    missing = registered - rels
    assert not missing, sorted(missing)

    non_markdown = sorted(r for r in registered if not r.endswith(".md"))
    assert len(non_markdown) == 62, len(non_markdown)
    assert set(non_markdown) <= rels

    # Named individually, so the proof is "one of the 62" and not "62 of something".
    exemplar = "docs/contracts/openapi/gi-pricing.yaml"
    assert exemplar in registered, "the register no longer carries the exemplar"
    assert exemplar in rels
    assert any(r.startswith("docs/contracts/") and r.endswith(".json") for r in rels)


def test_check_30_passes_a_registered_unstampable_file_that_is_now_in_scope(
    audit: types.ModuleType,
) -> None:
    """The second half of `F87`'s clause: the non-markdown file the selector now reaches
    is *"seen by check 30, which then consults `UNSTAMPABLE_EXEMPTIONS` and passes it"*.

    Run on one real `.json` alone, as a file root — so the only thing that can red is
    check 30's treatment of that file — and then again with its register row removed, so
    the pass is attributable to the register and to nothing else. Without the second run
    this is a check that has never printed a failure (`CLAUDE.md` §13).
    """
    exemplar = "docs/contracts/openapi/gi-pricing.yaml"
    entry = next(e for e in audit.UNSTAMPABLE_EXEMPTIONS if e.path == exemplar)

    setattr(audit, "_ID_SCOPE_ROOTS", (audit.REPO / exemplar,))  # noqa: B010
    assert [p.relative_to(audit.REPO).as_posix() for p in audit._id_scope_documents()] == [
        exemplar
    ]
    audit.failures.clear()
    audit.notes.clear()
    audit.check_header_fields()
    assert audit.failures == [], audit.failures
    assert any("1 skipped as registered unstampable" in n for n in audit.notes), audit.notes

    kept = tuple(e for e in audit.UNSTAMPABLE_EXEMPTIONS if e.path != entry.path)
    assert len(kept) == len(audit.UNSTAMPABLE_EXEMPTIONS) - 1
    setattr(audit, "UNSTAMPABLE_EXEMPTIONS", kept)  # noqa: B010
    audit.failures.clear()
    audit.notes.clear()
    audit.check_header_fields()
    assert len(audit.failures) == 1, audit.failures
    assert exemplar in audit.failures[0]
    assert audit.failures[0].startswith("check 30:")


# =========================================================================================
# One stamp-set definition, two consumers — `scripts/_docid.py`'s `in_stamp_set` (NT-0019
# §4 step 5), read by `audit-docs.py` (the F83 reconciliation corpus, and — through
# `_docid.stamp_set_files` — the checks-30-39 enforced scope) and by `doc-id.py` (what
# `migrate` stamps). Before the extraction each script stated the rule for itself and the
# two had already drifted: `F87`.
# =========================================================================================


def _doc_id_module() -> types.ModuleType:
    """`scripts/doc-id.py`, loaded by path. `scripts/` goes on `sys.path` first because
    that module does a plain `import _docid`, which a `spec_from_file_location` load does
    not arrange for on its own — the same preamble `tests/test_doc_id.py` carries.
    """
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return _load_by_path("_doc_id_for_stamp_set_equality", ROOT / "scripts" / "doc-id.py")


def test_the_two_stamp_set_consumers_read_one_definition(
    audit: types.ModuleType,
) -> None:
    """Set equality over the **real corpus**, not a fixture, and reported by naming both
    sides of the symmetric difference rather than by comparing two totals — two totals are
    invariant under a compensating pair of errors (Ruling 83).

    This is the test the extraction exists to make possible. `audit-docs.py` reaches the
    corpus through `scripts/file-census.py`'s `git_ls_files(REPO)`; `doc-id.py` reaches it
    through its own `git_ls_files(root, ".")`. Two entry points, two corpus readers, one
    predicate — and the equality is the claim that the second fact is what makes the first
    two agree.
    """
    docid = _doc_id_module()
    from_audit = set(audit.nt0019_stamp_set())
    from_migrate = set(docid.nt0019_stamp_set(ROOT))

    assert from_audit, "the audit-side stamp set is empty — the corpus read failed"
    assert not from_audit ^ from_migrate, sorted(from_audit ^ from_migrate)

    # The population is the one NT-0019 §4 step 5 describes, not merely a shared one: a
    # predicate both consumers read from the same wrong place would satisfy the equality
    # above and nothing else here.
    assert any(r.startswith("docs/contracts/") for r in from_audit)
    assert ".claude/roles/lead.md" in from_audit
    assert not any(r.startswith("scripts/") and not r.endswith("README.md") for r in from_audit)


def test_the_equality_reds_when_one_consumer_reads_a_different_definition(
    audit: types.ModuleType,
) -> None:
    """The broken-input proof for the test above (`CLAUDE.md` §13: a check that has never
    printed a failure has not been tested).

    Only `audit-docs.py`'s view of `_docid` is replaced, so the two consumers genuinely
    disagree — which is the state the extraction removed and which nothing before it could
    detect. `audit.nt0019_stamp_set` resolves `_docid` as a module global at call time,
    which is what makes the substitution reach it.
    """
    docid = _doc_id_module()
    real = audit._docid

    class _NarrowedDocid:
        """`_docid` with `docs/contracts/` dropped from the stamp set — the exact
        narrowing that would put the F83 register's 59 `.json` entries back outside the
        corpus they are reconciled against.
        """

        def __getattr__(self, name: str) -> object:
            return getattr(real, name)

        def nt0019_stamp_set(self, tracked: object) -> list[str]:
            return [
                rel
                for rel in real.nt0019_stamp_set(tracked)
                if not rel.startswith("docs/contracts/")
            ]

    setattr(audit, "_docid", _NarrowedDocid())  # noqa: B010
    from_audit = set(audit.nt0019_stamp_set())
    from_migrate = set(docid.nt0019_stamp_set(ROOT))

    difference = from_audit ^ from_migrate
    assert difference, "the substitution changed nothing — this proof is vacuous"
    assert all(r.startswith("docs/contracts/") for r in difference), sorted(difference)


def test_check_35_owner_clause_is_a_no_op_for_every_registered_file(
    audit: types.ModuleType,
) -> None:
    """Check 35's *owner* clause cannot fire on any of the 65, which is why F83's
    disposition ("a `generated: true` exemption in check 35") is a no-op on its own and
    the register had to bring its own enforcement.

    `check_owner` skips on `header is None` **and** on `HeaderError`, so this covers the
    three unparseable manifests as well as the 62 headerless files — the wider claim, and
    the true one.
    """
    for entry in audit.UNSTAMPABLE_EXEMPTIONS:
        path = audit.REPO / entry.path
        try:
            header = audit._docid.parse_header(path)
        except audit._docid.HeaderError:
            continue  # check_owner's own `except ... : continue`
        assert header is None, entry.path  # check_owner's own `if header is None`


# ---------------------------------------------------------------------------------------
# Ruling 102 §2 row (g), the other half — the check must be able to *see* the defect.
#
# Ruling 102's acceptance names as a violation "the (g) fix accepted without
# `NFR-RATE-13/14` exercised as a broken-input proof", and its work-list entry names a
# trap: the mangled citations "must not be treated as a citation-token class and thereby
# excused from §7 (g)'s 'neither header nor citation-token' requirement."
#
# That excusing was literal, not hypothetical. This predicate inverted REDIRECTS.csv with
# `str.replace`, a substring operation with no notion of where an identifier ends. Given
# the mangled `NFR-775/14`, it replaced `NFR-775` and produced `NFR-RATE-13/14` — the
# merge-base bytes exactly — so §7 (g) reported the corruption as a clean citation-token
# rewrite. §7 (g)'s figure could have been computed on the migrated tree and still read
# empty. The inverse now applies the same whole-identifier rule the forward rewrite does,
# so a token that was substituted inside a longer identifier fails to invert and the file
# is reported.
# ---------------------------------------------------------------------------------------


def test_check_34_migration_stamp_allowance_reds_on_ruling_102s_mangled_citation(
    audit: types.ModuleType,
) -> None:
    """Ruling 102 §2's named broken input, at the predicate that was excusing it."""
    old_body = "close the hand-compiled owed list **lost NFR-RATE-13/14** (F41)\n"
    new_text = (
        "---\nid: RL-9\n---\n"
        "close the hand-compiled owed list **lost NFR-775/14** (F41)\n"
    )
    assert not audit.frozen_file_matches_after_migration_stamp(
        old_body,
        new_text,
        redirects_inverse={"NFR-775": "NFR-RATE-13"},
        allocated_ids={"RL-9"},
    ), (
        "a substring inverse un-mangles `NFR-775/14` back to the merge-base bytes and "
        "reports the corruption as a clean citation-token rewrite"
    )


def test_check_34_migration_stamp_allowance_reds_on_a_mangled_hyphen_range(
    audit: types.ModuleType,
) -> None:
    """The same laundering, on the continuation shape Ruling 102's examples do not name.
    `FR-RATE-46-49` is a range; the head alone was rewritten, leaving `FR-712-49`."""
    old_body = "see FR-RATE-46-49 for the range\n"
    new_text = "---\nid: RL-9\n---\nsee FR-712-49 for the range\n"
    assert not audit.frozen_file_matches_after_migration_stamp(
        old_body, new_text, redirects_inverse={"FR-712": "FR-RATE-46"}, allocated_ids={"RL-9"}
    )


def test_check_34_migration_stamp_allowance_still_inverts_an_adjectival_suffix(
    audit: types.ModuleType,
) -> None:
    """The positive control for the inverse's own boundary rule: `OQ-500-shaped` is the
    whole new id plus an English suffix, and must still invert. A rule that refused every
    hyphen would turn this correct migration into a false (g) violation."""
    old_body = "an OQ-GOV-7-shaped hole\n"
    new_text = "---\nid: RL-9\n---\nan OQ-500-shaped hole\n"
    assert audit.frozen_file_matches_after_migration_stamp(
        old_body, new_text, redirects_inverse={"OQ-500": "OQ-GOV-7"}, allocated_ids={"RL-9"}
    )
