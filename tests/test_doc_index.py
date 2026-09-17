"""`scripts/doc-index.py` — RFC-937 §1.4's generated `INDEX.md`, its derived `execution`
column (§1.7), its ownership matrix (§1.6) and its phase report (§1.10 (c)).

`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`, Slice W37-3. This slice is
fixture-scoped on purpose (the slice's own text: "`doc-index.py` is built here but cannot be
run against the live corpus until W37-6, because before the migration there are no ids to
index") — every test here runs against the synthetic corpus at
`tests/fixtures/docs-ids/w37-3-corpus/`, never against the repository's own `docs/`.

No `@pytest.mark.req` marker: this is correctness of a governance tool, not evidence for a
numbered platform requirement — the same reasoning `tests/test_register_lint.py`,
`tests/test_scope_audit.py` and `tests/test_file_census.py` give for their own scripts.

`CLAUDE.md` §13: "a generated artifact matching its source proves neither correct." Several
tests below do not just assert a value against the fixture as committed — they mutate a copy
of the fixture (a ledger's `plans:`, a slice's `status:`, the ownership table itself) and
assert the generator's output *changes* in the direction the mutation implies, which a test
that only re-derives the same fixture once cannot show.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "doc-index.py"
CORPUS = ROOT / "tests" / "fixtures" / "docs-ids" / "w37-3-corpus"

# `scripts/doc-index.py` has a hyphen and is not importable by name — load it by path, the
# same way `tests/test_register_lint.py` loads `scripts/register-lint.py`. The explicit
# `SCRIPT.exists()` check gives a clean `ModuleNotFoundError` instead of the
# harder-to-read `FileNotFoundError` `spec_from_file_location` + `exec_module` raise for a
# missing target (verified empirically in `tests/test_file_census.py`).
if not SCRIPT.exists():
    raise ModuleNotFoundError(f"No module named 'doc_index': not found at {SCRIPT}")
_spec = importlib.util.spec_from_file_location("_doc_index_under_test", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
doc_index = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = doc_index  # dataclasses needs the module in sys.modules
_spec.loader.exec_module(doc_index)


def _build(root: Path) -> Any:
    return doc_index.build_corpus(root)


def _header(corpus: Any, ref: str) -> Any:
    record = corpus.by_id(ref)
    assert record is not None, f"fixture missing: {ref}"
    return record.header


def _run(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd
    )


# --- the corpus scan: every family, one row per id --------------------------------------


def test_corpus_carries_every_family_nt_0019_1_2_names() -> None:
    corpus = _build(CORPUS)
    families = {h.family for h in corpus.headers()}
    expected = {
        "requirement", "open question", "work", "slice", "workflow", "decision",
        "proposal", "plan", "ledger", "ruling", "research", "closure", "finding",
    }
    assert expected <= families, expected - families


def test_every_header_has_a_unique_id() -> None:
    corpus = _build(CORPUS)
    ids = [h.id for h in corpus.headers() if h.id]
    assert len(ids) == len(set(ids)), "duplicate id in the fixture corpus"


# --- relative links embedded in a copied cell: rebased for INDEX.md's own depth --------


def test_rebase_relative_links_is_a_no_op_when_source_and_dest_are_the_same_dir() -> None:
    """`open-questions.md` and `INDEX.md` are both direct `docs/` children, so a link
    copied from one into the other needs no rewrite — the identity case."""
    text = "See [the plan](2026-01-01-x.md) and [an anchor](#foo)."
    same = Path("docs")
    assert doc_index._rebase_relative_links(text, same, same) == text


def test_rebase_relative_links_climbs_one_level_for_a_specs_sourced_cell() -> None:
    """The live defect (check 1, 20 hits): a link written correctly in `docs/specs/x.md`
    (one level below `docs/`) reproduced verbatim in `docs/INDEX.md` (`docs/` itself)
    silently loses a directory level."""
    text = "See [research](../research/track-a-findings.md) F5."
    rebased = doc_index._rebase_relative_links(
        text, Path("docs/specs"), Path("docs")
    )
    assert rebased == "See [research](research/track-a-findings.md) F5."


def test_rebase_relative_links_preserves_a_fragment_and_skips_absolute_and_anchor_forms() -> (
    None
):
    text = (
        "[frag](../research/x.md#section) and [ext](https://example.com/y.md) "
        "and [anchor only](#z)"
    )
    rebased = doc_index._rebase_relative_links(text, Path("docs/specs"), Path("docs"))
    assert "[frag](research/x.md#section)" in rebased
    assert "[ext](https://example.com/y.md)" in rebased, "an absolute URL must not be touched"
    assert "[anchor only](#z)" in rebased, "a pure intra-document anchor must not be touched"


def test_scan_bold_id_rows_rebases_a_link_embedded_in_a_requirement_cell(
    tmp_path: Path,
) -> None:
    """End-to-end: a requirement row's own description cell carries a relative link
    written for its source file's depth (`docs/specs/`); `docs/INDEX.md`'s copy of that
    same cell must still resolve, one directory level shallower.

    Red before the fix: `render_index`'s row for FR-1460 carries the link string
    unchanged (`../research/track-a-findings.md`), which resolves outside `docs/`
    entirely from `docs/INDEX.md`'s own location — check 1's own broken-link scan on the
    real migrated corpus, 20 hits, all in `docs/INDEX.md`.
    """
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    spec = root / "specs" / "00-overview.md"
    text = spec.read_text(encoding="utf-8")
    before = "| **FR-1460** | Fixture requirement A | active |"
    after = (
        "| **FR-1460** | Fixture requirement A, see "
        "[research](../research/track-a-findings.md) | active |"
    )
    assert before in text
    spec.write_text(text.replace(before, after), encoding="utf-8")
    (root / "research").mkdir(exist_ok=True)
    (root / "research" / "track-a-findings.md").write_text("# findings\n", encoding="utf-8")

    corpus = _build(root)
    index_text = doc_index.render_index(corpus)

    assert "](research/track-a-findings.md)" in index_text, (
        "the rebased link (correct from docs/INDEX.md's own location) is missing"
    )
    assert "](../research/track-a-findings.md)" not in index_text, (
        "the un-rebased link (correct only from docs/specs/, one level too many '../' "
        "from docs/INDEX.md) must not survive into the rendered index"
    )


# --- the execution column: RFC-937 §1.7's seven cases, derived not stored ---------------


def test_execution_not_started() -> None:
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1300"), corpus) == "not started"


def test_execution_in_progress() -> None:
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1302"), corpus) == "in progress"


def test_execution_executed() -> None:
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1305"), corpus) == "executed"


def test_execution_closed() -> None:
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1307"), corpus) == "closed"


def test_execution_superseded_names_the_successor() -> None:
    corpus = _build(CORPUS)
    result = doc_index.derive_execution(_header(corpus, "PL-1310"), corpus)
    assert result == "superseded → PL-1311"


def test_execution_retired() -> None:
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1312"), corpus) == "retired"


def test_execution_terminal_for_a_review_plan() -> None:
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1314"), corpus) == "terminal"


def test_execution_is_none_for_a_non_plan_family() -> None:
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "WK-1200"), corpus) is None
    assert doc_index.derive_execution(_header(corpus, "SL-1201"), corpus) is None
    assert doc_index.derive_execution(_header(corpus, "LG-1304"), corpus) is None


def test_map_plan_rolls_up_any_in_progress_wins() -> None:
    corpus = _build(CORPUS)
    # PL-1320's slices route to PL-1300 ("not started"), PL-1302 ("in progress"),
    # PL-1305 ("executed") and PL-1307 ("closed") — "in progress" must win (RL-983
    # row 3, §1.7's own rule).
    assert doc_index.derive_execution(_header(corpus, "PL-1320"), corpus) == "in progress"


def test_map_plan_rolls_up_all_closed() -> None:
    corpus = _build(CORPUS)
    # PL-1329's two slices both route to a "closed" leaf plan (RL-983 row 5, §1.7's
    # own rule).
    assert doc_index.derive_execution(_header(corpus, "PL-1329"), corpus) == "closed"


# --- RL-983 (docs/rulings/RL-00983-the-map-plan-roll-up-runs-through-the-slices-and-has-no-catch-all.md): the map-plan
# roll-up runs through the slices, and has no catch-all. Four regression fixtures, one per
# named defect, each pinning the WRONG value an earlier version of `_rollup_map_plan`
# produced (a `work:`-proxy enumeration over leaf plans, completed with a trailing
# `return "not started"`), per the ruling's own §4 acceptance items.


def test_ruling_72_item_1_the_invisible_slice() -> None:
    """`WK-1500` has three slices: one `closed` (via `PL-1511`), two with no plan at all
    and a `draft` slice row. The old `work:`-proxy enumeration counted only the plans —
    `[closed]` — and read `closed`. The two unplanned slices must not be invisible.
    """
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1510"), corpus) == "in progress"


def test_ruling_72_item_2_mid_flight() -> None:
    """`WK-1600` has one `closed` slice and one unplanned `draft` slice. `states ==
    ["closed", "not started"]` matched no branch of the old catch-all chain and fell to
    `return "not started"`.
    """
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1610"), corpus) == "in progress"


def test_ruling_72_item_3_replanned_then_completed() -> None:
    """`SL-1701`'s leaf plan `PL-1711` was superseded by `PL-1712`, which then closed. The
    old code enumerated `PL-1711` too (it shares `work: WK-1700`), read its raw derived
    value `"superseded → PL-1712"`, matched no branch, and returned `"not started"` — on
    the *normal replan path*, not an edge case. The superseded plan must be excluded from
    the slice's live leaf plan, not counted alongside its successor.
    """
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1710"), corpus) == "closed"


def test_ruling_72_item_4_no_catch_all_every_slice_retired() -> None:
    """`WK-1800`'s two slices are both `retired`, with no leaf plans. The old code's
    `children` list was empty (`if not children: return "not started"`), producing
    `"not started"` — a value from a default, not a rule. Every child being *excluded* as
    retired must roll up to `retired` (row 2), never fall through to a default.
    """
    corpus = _build(CORPUS)
    assert doc_index.derive_execution(_header(corpus, "PL-1810"), corpus) == "retired"


def test_rollup_precedence_table_has_no_catch_all() -> None:
    """RL-983's substance: an unenumerated combination of child states raises rather
    than defaulting. No corpus fixture can legitimately produce this input — the four
    states `_slice_child_state` can return (`not started`, `in progress`, `executed`,
    `closed`) exhaust every row of the table in every non-empty combination — so this
    calls the precedence function directly with a value it cannot actually produce, the
    same way the ruling's own record proves the *shape* of the missing safety net rather
    than a reachable scenario.
    """
    with pytest.raises(ValueError, match="matches no row"):
        doc_index._apply_rollup_precedence(["superseded → PL-9999"])


def test_header_dataclass_has_no_execution_field() -> None:
    """The column is derived, never stored — RFC-937 §1.7. If `Header` ever grew an
    `execution` field, that would be the parser accepting a written value instead of this
    module computing one.
    """
    field_names = {f.name for f in dataclasses.fields(doc_index.Header)}
    assert "execution" not in field_names


def test_no_fixture_file_writes_an_execution_field() -> None:
    for md in sorted(CORPUS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        assert "execution:" not in text, f"{md} writes an execution field on disk"


def test_execution_derivation_reacts_to_a_changed_ledger(tmp_path: Path) -> None:
    """`CLAUDE.md` §13: prove the derivation reads the corpus, not the plan id — a
    hardcoded per-id lookup table could not react to either mutation below.

    RFC-937 §1.7's "in progress" row is an *or*: "that `LG-` is active, or the `SL-` is
    active." `PL-1302` satisfies both independently (its ledger is active and its slice is
    active), so clearing only one leaves "in progress" unchanged — itself a useful check of
    the *or*, done first below. Clearing both must turn it into "not started".
    """
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    ledger = root / "ledgers" / "LG-01304-in-progress.md"
    ledger_text = ledger.read_text(encoding="utf-8")
    assert "plans: [PL-1302]" in ledger_text
    ledger.write_text(ledger_text.replace("plans: [PL-1302]", "plans: []"), encoding="utf-8")

    corpus = _build(root)
    assert doc_index.derive_execution(_header(corpus, "PL-1302"), corpus) == "in progress", (
        "the slice alone is still active — the *or* must still hold"
    )

    roadmap = root / "roadmap.md"
    roadmap_text = roadmap.read_text(encoding="utf-8")
    before = "title: Alpha, active slice\nstatus: active"
    after = "title: Alpha, active slice\nstatus: draft"
    assert before in roadmap_text
    roadmap.write_text(roadmap_text.replace(before, after), encoding="utf-8")

    corpus = _build(root)
    assert doc_index.derive_execution(_header(corpus, "PL-1302"), corpus) == "not started"


# --- the ownership matrix: RFC-937 §1.6, one row per role -------------------------------


def test_reporter_and_watcher_rows_exist_and_are_empty() -> None:
    matrix = doc_index.ownership_matrix()
    assert "reporter" in matrix
    assert "watcher" in matrix
    assert matrix["reporter"] == ()
    assert matrix["watcher"] == ()


def test_every_other_role_owns_at_least_one_family() -> None:
    matrix = doc_index.ownership_matrix()
    for role in ("decision-maker", "maintainer", "planner", "executor", "auditor", "lead"):
        assert matrix[role], f"{role} unexpectedly owns nothing"


def test_ownership_matrix_catches_a_real_disagreement(monkeypatch: Any) -> None:
    """`CLAUDE.md` §13 again: the empty reporter/watcher rows must come from *deriving*
    that neither name appears in the owner table, not from a hardcoded empty tuple. Adding
    a cell that names "reporter" must make its row non-empty on the next call.
    """
    mutated = (*doc_index._OWNERSHIP_TABLE, ("mutated family", "reporter drafts it"))
    monkeypatch.setattr(doc_index, "_OWNERSHIP_TABLE", mutated)
    matrix = doc_index.ownership_matrix()
    assert matrix["reporter"] == ("mutated family",)
    assert matrix["watcher"] == ()  # unaffected — still names no role


def test_index_md_ownership_matrix_section_shows_reporter_and_watcher_as_empty() -> None:
    corpus = _build(CORPUS)
    rendered = doc_index.render_index(corpus)
    assert "| reporter |  |" in rendered
    assert "| watcher |  |" in rendered


# --- the phase report: RFC-937 §1.10 (c) / Acceptance Standard item 10 -----------------


def test_phase_report_contains_every_1_10_c_element() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    for phrase in (
        "Works closed and retired",
        "Slices planned versus delivered",
        "Plans superseded per Work",
        "Rulings per Work",
        "Findings opened versus discharged",
        "unowned-decay",
        "carried in from an earlier phase",
        "no inbound citation outside INDEX.md",
        "closure record being filed",
    ):
        assert phrase in report, phrase


def test_phase_report_works_closed_and_retired() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    assert "1 closed (WK-1200)" in report
    assert "1 retired (WK-1210)" in report


def test_phase_report_slices_planned_versus_delivered() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    assert "5 planned, 1 delivered" in report


def test_phase_report_plans_superseded_and_rulings_per_work() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    assert "WK-1200: 1" in report  # one superseded plan and one ruling, both under WK-1200
    assert "WK-1210: 0" in report


# --- RL-982 (docs/rulings/RL-00982-the-phase-report-s-findings-element-is-phase-scoped-from-the-register-project-wide-is-a-defect-not-correct-behaviour.md): the findings
# element is phase-scoped from `findings/register.md`, never from an `FD-` essay's header
# (which, after RL-981, does not even carry `decision:` any more). The fixture register
# holds: FD-1450 (P9, unowned, active), FD-1451 (P9, resolved -> closed), FD-1452 (P9,
# accept -> retired), FD-1453 (P8, unowned by design, active — the carry-in for P9).


def test_phase_report_findings_figures_are_scoped_from_the_register() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    assert "3 opened in P9" in report
    assert "2 discharged" in report
    assert "1 unowned-decay in P9" in report
    assert "1 unowned-decay carried in from an earlier phase" in report


def test_findings_figures_positive_control_over_the_fixture_register() -> None:
    """`CLAUDE.md` §13: the unowned predicate is tested against a positive control — the
    fixture register must contain at least one row the predicate matches (FD-1450) and at
    least one it does not (FD-1451, resolved; FD-1452, accepted), so "small" cannot be
    confused with "correct".
    """
    rows, data_lines = doc_index._parse_register(CORPUS / "findings" / "register.md")
    assert len(rows) == data_lines == 4
    unowned = {r.finding_id for r in rows if r.unowned}
    not_unowned = {r.finding_id for r in rows if not r.unowned}
    assert unowned == {"FD-1450", "FD-1453"}
    assert not_unowned == {"FD-1451", "FD-1452"}


def test_findings_register_status_derivation() -> None:
    rows, _ = doc_index._parse_register(CORPUS / "findings" / "register.md")
    by_id = {r.finding_id: r for r in rows}
    assert by_id["FD-1450"].status == "active"
    assert by_id["FD-1451"].status == "closed"  # a "Resolved" annotation
    assert by_id["FD-1452"].status == "retired"  # the "accept" disposition


def test_findings_register_unscoped_symptom_does_not_recur(tmp_path: Path) -> None:
    """RL-982 acceptance item 1's named violation: "the opened count equals the
    register's total row count." Build a register with rows in two phases and confirm
    `--phase P2` counts only P2's own rows, never the whole table.
    """
    register = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
        "| FD-2000 | x | WK-1 | P1 | unowned |\n"
        "| FD-2001 | x | WK-2 | P2 | unowned |\n"
        "| FD-2002 | x | WK-2 | P2 | fix before close — Resolved 2026-01-01, PR #1 |\n"
    )
    path = tmp_path / "register.md"
    path.write_text(register, encoding="utf-8")
    rows, data_lines = doc_index._parse_register(path)
    assert len(rows) == data_lines == 3
    opened, discharged, unowned_decay, carry_in = doc_index._findings_figures(rows, "P2")
    assert opened == 2  # not 3 — the project-wide symptom this must not reproduce
    assert discharged == 1
    assert unowned_decay == 1
    assert carry_in == 1  # FD-2000, P1, unowned, active


def test_findings_register_coverage_mismatch_raises_rather_than_undercounting(
    tmp_path: Path,
) -> None:
    """RL-982 acceptance item 2: a register row the parser cannot read must break the
    report, never silently produce a smaller, plausible number. A five-cell row is
    well-formed; this one has four.
    """
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    register_path = root / "findings" / "register.md"
    text = register_path.read_text(encoding="utf-8")
    broken = text + "| FD-3000 | broken row | P9 | unowned |\n"  # only 4 cells
    register_path.write_text(broken, encoding="utf-8")

    corpus = _build(root)
    with pytest.raises(ValueError, match="coverage mismatch"):
        doc_index.phase_report(corpus, "P9", root)


def test_phase_report_uncited_list_includes_the_uncited_and_excludes_the_cited() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    # RS-1440 is cited nowhere; WF-1400 is cited by the P9 phase section's own exit
    # criteria line. Both carry `phase: P9`, so both are candidates — only one is uncited.
    assert "RS-1440" in report
    assert "WF-1400" not in report


def test_phase_report_days_to_closure_only_covers_actually_closed_plans() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    # PL-1307 is the only plan in P9 whose derived execution is "closed"; PL-1310
    # (superseded), PL-1314 (terminal) and PL-1320 (map, "in progress") share WK-1200 with
    # the same CR but must not be listed here.
    assert "PL-1307 -> CR-1309: 16 days" in report
    assert "PL-1310 ->" not in report
    assert "PL-1314 ->" not in report
    assert "PL-1320 ->" not in report


def test_phase_report_reacts_to_a_changed_slice(tmp_path: Path) -> None:
    """`CLAUDE.md` §13: prove "slices delivered" is computed, not copied from the fixture
    as authored — closing a second slice must move the count from 1 to 2.
    """
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    roadmap = root / "roadmap.md"
    text = roadmap.read_text(encoding="utf-8")
    before = "title: Alpha, active slice\nstatus: active"
    after = "title: Alpha, active slice\nstatus: closed"
    assert before in text
    roadmap.write_text(text.replace(before, after), encoding="utf-8")

    corpus = _build(root)
    report = doc_index.phase_report(corpus, "P9", root)
    assert "5 planned, 2 delivered" in report


# --- `--check`: byte-stable against regeneration (RFC-937 §7 (c)) ----------------------


def test_check_exits_0_on_a_freshly_generated_index(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    generate = _run("--root", str(root))
    assert generate.returncode == 0, generate.stderr
    check = _run("--root", str(root), "--check")
    assert check.returncode == 0, check.stdout + check.stderr


def test_check_exits_1_on_a_one_row_stale_index(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    assert _run("--root", str(root)).returncode == 0

    # Stale exactly one row: change a title after `INDEX.md` was generated, without
    # regenerating it.
    target = root / "plans" / "PL-01300-not-started-leaf.md"
    text = target.read_text(encoding="utf-8")
    assert "Not-started leaf" in text
    renamed = text.replace("Not-started leaf", "Not-started leaf (renamed)")
    target.write_text(renamed, encoding="utf-8")

    check = _run("--root", str(root), "--check")
    assert check.returncode == 1


def test_check_exits_0_against_an_empty_pre_migration_corpus(tmp_path: Path) -> None:
    """Found while wiring `--check` into `.github/workflows/docs.yml` as a gate step
    (W37-4, `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`): before this fix,
    `--check` treated a missing `docs/INDEX.md` as unconditionally stale, so running it
    against today's real, pre-migration `docs/` — no `INDEX.md`, zero governed records —
    exited 1. That would have red the docs workflow on every push until W37-6 migrates the
    corpus, for a file only the migration creates; `python3 scripts/audit-docs.py exits 0
    on the real tree` is this slice's own acceptance line, and a sibling gate step failing
    unconditionally would defeat it regardless of `audit-docs.py` itself.

    Broken-input pairing: `test_check_exits_1_on_a_one_row_stale_index` above proves
    `--check` still reds when records exist and the index is one row behind; this proves
    it does not also red when there is nothing to index yet — the two together pin the
    exact boundary the fix draws (`not corpus.records`, not merely "file missing").
    """
    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    result = _run("--root", str(empty_root), "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "nothing to check yet (pre-migration)" in result.stdout, result.stdout
    assert not (empty_root / "INDEX.md").exists()


def test_check_exits_1_when_records_exist_but_index_was_never_generated(tmp_path: Path) -> None:
    """The other half of the boundary: records exist (so there is something to be stale
    against) but `INDEX.md` was never generated at all — must still fail, not be waved
    through by the same "nothing to check yet" path the empty-corpus case above takes.
    """
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    assert not (root / "INDEX.md").exists()
    result = _run("--root", str(root), "--check")
    assert result.returncode == 1
    assert "governed record(s) were found" in result.stdout, result.stdout


def test_regenerating_twice_produces_byte_identical_output(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    shutil.copytree(CORPUS, root)
    assert _run("--root", str(root)).returncode == 0
    first = (root / "INDEX.md").read_bytes()
    assert _run("--root", str(root)).returncode == 0
    second = (root / "INDEX.md").read_bytes()
    assert first == second


def test_default_action_refuses_to_write_an_empty_index(tmp_path: Path) -> None:
    """Found while building this slice: running the default (write) action against a tree
    with none of RFC-937's family directories yet (today's pre-migration `docs/`, or any
    empty directory) makes every file fail `parse_header`'s harmless "no front matter" case,
    so `build_corpus` returns zero records — and the write path must not then happily
    overwrite whatever `INDEX.md` is there with a near-empty file that looks like success.
    """
    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    result = _run("--root", str(empty_root))
    assert result.returncode == 1
    assert not (empty_root / "INDEX.md").exists()


def test_generated_index_never_leaves_the_committed_fixture_dirty() -> None:
    """Guard against the exact mistake this suite must not make: `--check`/`--show`/
    `--phase` are read-only and must never write `INDEX.md` into the tracked fixture tree.
    """
    assert not (CORPUS / "INDEX.md").exists()


# --- `--show`: prints an execution value for each of the seven cases -------------------


def test_cli_show_prints_execution_for_each_case() -> None:
    cases = {
        "PL-1300": "not started",
        "PL-1302": "in progress",
        "PL-1305": "executed",
        "PL-1307": "closed",
        "PL-1310": "superseded → PL-1311",
        "PL-1312": "retired",
        "PL-1314": "terminal",
    }
    for plan_id, expected in cases.items():
        result = _run("--root", str(CORPUS), "--show", plan_id)
        assert result.returncode == 0, result.stderr
        assert f"execution: {expected}" in result.stdout, (plan_id, result.stdout)


def test_cli_show_unknown_id_fails_loudly() -> None:
    result = _run("--root", str(CORPUS), "--show", "PL-99999")
    assert result.returncode != 0


def test_cli_phase_report_end_to_end() -> None:
    result = _run("--root", str(CORPUS), "--phase", "P9")
    assert result.returncode == 0, result.stderr
    assert "Phase report — P9" in result.stdout
    assert "5 planned, 1 delivered" in result.stdout


# --- rendering: `render_index` is what `--check`/the default action both use -----------


def test_render_index_is_deterministic_across_calls() -> None:
    corpus = cast("Any", _build(CORPUS))
    first = doc_index.render_index(corpus)
    second = doc_index.render_index(corpus)
    assert first == second
