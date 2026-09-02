"""`scripts/doc-index.py` — NT-0019 §1.4's generated `INDEX.md`, its derived `execution`
column (§1.7), its ownership matrix (§1.6) and its phase report (§1.10 (c)).

`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`, Slice W37-3. This slice is
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


# --- the execution column: NT-0019 §1.7's seven cases, derived not stored ---------------


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
    # PL-1320's leaf children include PL-1302 ("in progress"), which must win over
    # PL-1300 ("not started"), PL-1305 ("executed"), PL-1307 ("closed") and the rest.
    assert doc_index.derive_execution(_header(corpus, "PL-1320"), corpus) == "in progress"


def test_map_plan_rolls_up_all_closed() -> None:
    corpus = _build(CORPUS)
    # PL-1329's only leaf children, PL-1330 and PL-1331, are both "closed".
    assert doc_index.derive_execution(_header(corpus, "PL-1329"), corpus) == "closed"


def test_header_dataclass_has_no_execution_field() -> None:
    """The column is derived, never stored — NT-0019 §1.7. If `Header` ever grew an
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

    NT-0019 §1.7's "in progress" row is an *or*: "that `LG-` is active, or the `SL-` is
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


# --- the ownership matrix: NT-0019 §1.6, one row per role -------------------------------


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


# --- the phase report: NT-0019 §1.10 (c) / Acceptance Standard item 10 -----------------


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


def test_phase_report_findings_opened_discharged_unowned_decay() -> None:
    corpus = _build(CORPUS)
    report = doc_index.phase_report(corpus, "P9", CORPUS)
    assert "2 opened, 1 discharged, 1 unowned-decay" in report


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


# --- `--check`: byte-stable against regeneration (NT-0019 §7 (c)) ----------------------


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
    with none of NT-0019's family directories yet (today's pre-migration `docs/`, or any
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
