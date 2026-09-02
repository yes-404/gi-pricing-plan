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
        old_body, new_text, redirects_inverse={"RFC-88": "NT-0016"}
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
        old_body, new_text, redirects_inverse={"RFC-88": "NT-0016"}
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
    assert audit.frozen_file_matches_after_migration_stamp(old_body, new_text, order_a)
    assert audit.frozen_file_matches_after_migration_stamp(old_body, new_text, order_b)


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
