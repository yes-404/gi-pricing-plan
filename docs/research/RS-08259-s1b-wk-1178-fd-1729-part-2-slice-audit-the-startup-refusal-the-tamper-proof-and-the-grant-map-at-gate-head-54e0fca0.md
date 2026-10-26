---
id: RS-8259
family: research
kind: audit
title: S1b (WK-1178, FD-1729 part 2) slice audit — the startup refusal, the trigger-tamper proof and the exact grant map, at gate head 54e0fca0
status: draft
created: 2026-10-26   # working id 8259, unminted
owner: auditor
tree: f1f72eff26a80aa8eb57f0dd421ed7cdfb153c8a
phase: P2
work: WK-1178
corrected_by: []
relates: [LG-8248, SL-8258, FD-1729, OQ-8260, PL-1769, PL-1927, FR-44]
---

# RS-8259 — S1b slice audit (FD-1729 part 2)

*(Working id 8259, reserved by lead 28. Written by `aud-s1b` (auditor, sonnet, effort medium), worktree `.claude/worktrees/aud-s1b`, branch `aud-s1b-2026-10-26`. Docs and diff reading only: no test, no gate, no database. The auditor proposes; the lead adopts (CLAUDE.md §12).)*

## Question

Does `draft/s1b-fd1729` at `4a55dd22e59363ff8874d14008e9af78dcbd853f` (tree `f1f72eff`) = gate head `54e0fca083628964aa1227c0ada467d3d7b3a379` (tree `bb2bd00c`) + one docs-only commit meet PL-1927's S1b section (row 4; acceptance 8–11), PL-1769 S-b, the GO (to-lead "2026-10-26 10:13:45 GMT") and the rulings 22:56:19, 03:54:51, 05:53:25, 08:43:25, 08:46:25 and "2026-10-26 09:33:12 GMT"?

## Method

Scope from the plan and the GO first, then the evidence. Merge-base `git merge-base 4a55dd22 origin/main` = `1e0a8abbc90723ae9c887a901f700b72f6f94cc1` (S1a's squash, #1398). `git diff --stat 1e0a8abb 4a55dd22` = 13 files, +855/−15: `backend/src/app/db/{immutability.py (new),session.py}`, `main.py`, `worker/entrypoint.py`, `backend/tests/{conftest_db.py,test_application_role.py (new),test_artifact_immutability.py,test_tenant_binding.py}`, LG 8248, `docs/{INDEX.md,open-questions.md,roadmap.md,specs/07-platform.md}`. `git diff --stat 54e0fca0 4a55dd22` = 1 file (LG 8248), 1 insertion, 1 deletion — as the brief states. Frontend: `git diff --name-only 1e0a8abb 4a55dd22 -- frontend | wc -l` = 0; `-- deploy docs/contracts` = 0.

## Findings

| # | Class | Finding | Evidence |
|---|---|---|---|
| F1 | **B** | **PL-1927 acceptance 10 is not met on the branch: `FR-44` carries no dated line and the LG carries no postgres-pro review.** Acceptance 10: "`FR-44` (`01-data-management.md:106`) carries `PL-1769` Step 7.1's dated line, completed with the date and both slice ids; the postgres-pro review is in the `LG-`". | `git diff 1e0a8abb 4a55dd22 -- docs/specs/01-data-management.md` = 0 lines. `sed -n 106p` shows the last amendment as "(Amended 2026-10-18, WK-1178 SL-1770 …)"; Step 7.1's text ("**Layer 1 binds.** …Startup refuses an owner, a superuser, or a disabled artifact trigger…") is absent. LG 8248 mentions `postgres-pro` only in the quoted plan (lines 38, 79), never as a review result. The GO names "FR-44, 01:106; acceptance 8–11"; no ruling read defers S1b-4. Must land before the PR (it changes the spec, so it is also the commit's "one commit" rule, CLAUDE.md §2). If the lead rules it owed to the mint, the ruling must be dated and cited. |
| F2 | N | LG 8248 "Gate" and "Audit" sections still read "pending — S1b GO not yet requested", and `GO:`/`MERGE-ACK:` the same, although the GO is confirmed and the gate ran. | LG 8248 lines 24–25 and the Gate/Audit headings. The gate rc table is not copied into the LG (acceptance 10 asks "the full gate rc table is all 0"). Fill at the mint, append-only (placeholders kept per brief 2(f)). |
| F3 | N | The gate's rc table is not "all 0" in the literal sense; it stands only under the maintainer's 1(f). | Below, "Gate of record". |
| F4 | N | The count "120 bound" in LG 8248 is a different predicate from the label count. `owner-subject` rows = 108 of 143; 120 is the LG's "take `owner_database`" count (ast predicate, "same as N3 (RS-1946)"). Not reproduced by me with a different predicate; stated so the count names its predicate. | `python3 -I` ast over `OWNER_FIXTURE_USERS`: `143 {3} 143 108` (rows, arity set, distinct ids, `owner-subject` rows). |
| F5 | N | The `::text` fix (`9bb24a68`) has no red commit of its own; it was found by R3's green failing and is covered by the T3 control (`await assert_least_privilege(connection)  # control: untouched head passes`, test_application_role.py:189). Recorded in LG 8248 as the "real draft bug the red-first found". Acceptable. | LG 8248 build log 09:36 entry; `git merge-base --is-ancestor 5fca0019 70a85145` rc 0. |
| F6 | N | Gate-time audit-docs shows 5 FAILED lines (check 31 ×2, check 32 ×3 incl. `PL-8227` at LG :111); the last was the reason for 4a55dd22. 4a55dd22 rewords :111 to the space form; I did not re-run audit-docs (read-only brief). | `audit_docs.log` tail. The remaining ones are S1b's own working ids and clear at the mint. |

## Checks of the brief, one by one

**(a) Guard check, `backend/src/app/db/immutability.py` at 4a55dd22 — MET.** `:83` `_ENABLED_FOR_EVERY_SESSION = frozenset({"O", "A"})` (R3). `_TRIGGERS` selects `t.tgenabled::text AS enabled` and `md5(p.prosrc) AS body_md5`. `PINNED_GUARD_FUNCTION_MD5` has 15 entries, each 32-hex, 0 empty (read in full). LG 8248 build log "the 15 pins, measured at alembic head `b7e4c2a91d36` (commit `b108e094`)" cites the script (`~/gi-pricing-plan.local/scratch/exec-s1bcut/pins.py`) and the SQL `SELECT p.proname, md5(p.prosrc) FROM pg_trigger t JOIN pg_class c … GROUP BY p.proname, p.prosrc ORDER BY 1`, the same `md5(p.prosrc)` as the check's. Pins are exercised by T8 at the gate (see (g)). `git grep -n pg_has_role -- backend/src` = 1 hit, `immutability.py:45`, with `'MEMBER'` (acceptance 9).

**(b) Red before fix — MET.** `git merge-base --is-ancestor 5fca0019 70a85145` rc 0 (R3 red → fix). Other red pairs are logged in LG 8248 (build log "every red, each log `head=` first and `rc=` last": T1 `2 failed, 18 deselected`, T2 `1 failed, 1 passed`, T3 `2 failed, 2 passed`, T4–T6 `3 failed, 17 deselected` on the owner-DSN run); those are scratch-edit reds, uncommitted by design, per rulings O1 (a)/O2 (c). `9bb24a68` is deliberately after `70a85145` (F5).

**(c) FR-436 patch `f0c8e095` — MET.** The diff touches only `backend/tests/test_tenant_binding.py` (+15): an import, a docstring naming O5 and T3, a local `_skip`, and `monkeypatch.setattr(Database, "assert_least_privilege", _skip)` inside `test_a_database_not_migrated_to_this_revision_stops_startup`, with the comment `# to-lead "2026-10-26 09:33:12 GMT": the FR-436 residue ruled (a): this test only.` — not autouse, not module-level, as the ruling's clause "monkeypatch inside it, not autouse, not module-level" requires. `git grep -n 'setattr.*assert_least\|patch.*assert_least' -- backend packages` = exactly that one line. App callers of `assert_least_privilege` under `backend/src`: `main.py:112`, `worker/entrypoint.py:40`, via `Database.assert_least_privilege` (`session.py:81`) — the patch is a test-scope monkeypatch, undone at teardown, so no app caller is covered outside that test. Note the ruling itself says the 23:11:30 rule is "met in spirit, not letter" because this function is an app-called check; the docstring states both halves. N, not B.

**(d) `OWNER_FIXTURE_USERS` — MET, with a count correction.** `diff 1e0a8abb 4a55dd22 -- conftest_db.py`: all hunks are additions; the first 132 rows equal main's (`ast`: `prefix equal True`); the 11 appended rows are all `owner-subject`, arity 3 (`143 {3} 143` = rows, arity set, distinct ids). The brief says "the 10 owner-subject rows"; it is **11** because the R3 row `test_an_enable_always_trigger_is_accepted` was added at the 09:33:12 ruling ("now 143 (one owner-subject row for R3's ENABLE ALWAYS test)"). Each label is justified by its reason cell (plants a scratch role / tampers a trigger / reads the owner's grants / plants a grant drift / sets ENABLE ALWAYS — all rolled back). Command: `python3 -I /tmp/aud_s1b_count.py backend/tests/conftest_db.py` (an `ast` walk of the `OWNER_FIXTURE_USERS` assignment; the 132 → 143 base is `git show 1e0a8abb:backend/tests/conftest_db.py`). See F4 for "120 bound".

**(e) OQ 8260 — MET.** One row in `docs/open-questions.md` (working-id form, `OQ 8260`, owner WK-1178, options (i)–(iii), recommendation (i)), one in `docs/specs/07-platform.md` §10 (condensed, "Mirrored in `docs/open-questions.md`"; not byte-identical, as OQ-1931's pair), and a roadmap gate row "Before S1b's PR is decided … OQ 8260 … 1 (1 open)". Mirrored both ways. Per the 09:33:12 ruling: "ONE OQ row … mirrored in `open-questions.md` and `07-platform.md` §10".

**(f) Records — MET except as F1/F2.** No minted-form S1b id on the branch: `git grep -n -E '(SL-1948|RS-1949|LG-1947|OQ-1950)' 4a55dd22` = no output. LG 8248 keeps placeholders (GO/MERGE-ACK/Gate/Audit "pending"), build log append-only (13 dated entries, none edited in place that I can see; the 4a55dd22 change is the one-line reword of :111 on the maintainer's ruling). FD-1729 is not closed on this branch (its closure is owed to the PR, R6). `git diff 1e0a8abb 4a55dd22 --stat` shows no register change.

**(g) Full suite coverage — MET.** LG 8248: "head `428853bf` … `2973 passed, 13 skipped, 5 xfailed, 136 warnings in 1990.56s (0:33:10)`, rc=0". `git diff --stat 428853bf 4a55dd22` after that head: `54e0fca0` and `4a55dd22` are LG-only commits (`git log` shows 54e0fca0 and 4a55dd22 are `docs(ledgers)`), so the suite covers all code at the gate head. (I confirm by the commit list, not by re-running a diff of all trees.)

**Frontend — MET.** 0 files under `frontend/` (command above).

## Gate of record (`~/gi-pricing-plan.local/scratch/s1b-gate/gate/`, START head `54e0fca083628964aa1227c0ada467d3d7b3a379` tree `bb2bd00c50214b97db2ffe5b5b5cc526f0ea5b15`, END `2026-10-26T11:28:03+00:00` rc=1)

rc files read: `ruff.rc`: 0 · `mypy.rc`: 0 · `import_linter.rc`: 0 · `contracts.rc`: 0 · `req_coverage.rc`: 0 · **`audit_docs.rc`: 1** · **`pytest.rc`: 1**. gate.log: `pytest summary: 13 failed, 6982 passed, 21 skipped, 5 xfailed, 146 warnings in 3115.31s (0:51:55)`; `| pytest skipped | 21 (<= 21) |`; frontend half all rc=0 (install, generate:api, lint, type-check, test, build); `tree after gate: 0 changed path(s)`.

The 13 FAILED lines are exactly the docs-audit set of 1(f) (finding_citations ×1, audit_docs_ids ×2, process_core_digest ×2, w37_11_ceiling ×1, test_doc_index ×1, register_lint ×3, register_owed ×1, repository_invariants ×2); audit-docs fails only checks 31 and 32 on S1b's own ids (five lines). That is the 1(f) shape, which the lead ruled STANDS (to-lead "2026-10-26 11:29:13 GMT"); conditions owed at the mint: audit-docs rc 0, those tests re-run via run-small on the minted head, CI.

pg_roles rows (gate.log): before `gip_app,gip_app_login`; after provision `gip_app,gip_app_login`; at END `gip_app,gip_app_login`. Demo row: `| demo.py --journey wf-699 | rc=0 |`, `D7 | ok  19985 policies in the sample … sum +489842011 minor units`, keycloak bind source under tools-main; zeros `own-DB count=0 redis RT db 1 dbsize=0 redis RD db 3 dbsize=0`; `END rc parts | python max=1 fe max=0 demo=0 restore rc_kc=0 role rc_role=0 skip rc_skip=0`.

## Not run by me

No test, audit-docs, gate or database was run (brief). `doc-index.py --check` is run by me on this branch and quoted in the commit report.

## Proposed verdict

**NOT-CLEAN**, one blocker: F1 (FR-44's dated line, and the postgres-pro review in the LG, both required by acceptance 10 and absent from the branch). Everything else in the brief's (a)–(g) is met. The fix is docs-only (`docs/specs/01-data-management.md:106` + an LG append + the postgres-pro evidence); it needs no new gate under the docs-only rule (seat-brief item 30) but touches a spec FR, so req-coverage rc 0 is owed. The lead may instead rule F1 owed to the PR/mint with a dated line; then CLEAN.

## Owed to the mint

LG 8248 → LG-1947; SL 8258 → SL-1948; RS 8259 → RS-1949; OQ 8260 → OQ-1950 (the three places: `open-questions.md`, `07-platform.md` §10, the roadmap row); `slice: SL-8258` in LG front matter; FD-1729 closure + register row (R6, in the PR); FR-44's dated line with both slice ids (F1); LG Gate/Audit/GO/MERGE-ACK sections (F2); audit-docs rc 0 and the 13 tests re-run at the minted head (1(f) conditions); mint-repoint 23efc4f97b513b72 and quote-parity; INDEX regenerated.

## 2026-10-26 11:45:43 GMT — Addendum: F1 re-check at c21cc8be368542188968b8035157477a414e8031

Scope: F1 only (PL-1927:224–225 acceptance 10), on `draft/s1b-fd1729` at `c21cc8be368542188968b8035157477a414e8031`, read with `git show <sha>:<path>`; nothing above this heading is edited. Fix commits: `372bfe64` (FR-44's line), `82853038` (LG Step 7.2 section + FD 8265), `c21cc8be` (the two "→ FD 8265" markers moved outside the quote). Authority: to-lead "2026-10-26 11:36:30 GMT" and "2026-10-26 11:38:32 GMT". I propose; the lead adopts.

**Clause (a) — FR-44 carries Step 7.1's line: MET.** Line 106 of `docs/specs/01-data-management.md` at c21cc8be ends, after the original "Layer 1 binds only once the application stops connecting as the owner (FD-1729, SL-1771). ", with the 11:36:30 ruled text; a Python `str.find` of the ruled text (copied from the entry) in the line returns exactly one hit, ending at the line's closing " |" (the table cell), byte for byte. Appended: "*(Amended 2026-10-26, WK-1178 SL-1942 and SL 8258, on FD-1729; SL-1771 was retired 2026-10-26 by its re-cut, PL-1927.)* **Layer 1 binds.** The application and the worker connect as `gip_app_login`, … Until this, every grant and revoke here was inert, and the owner could disable the triggers." The "(FD-1729, SL-1771)" sentence is still present (append-only). `SL 8258` is in space form. `git diff --stat 4a55dd22 c21cc8be -- docs/specs/01-data-management.md`: 1 insertion, 1 deletion (that line only).

**Clause (b) — the postgres-pro review is in the LG: MET.** LG-8248's dated section "2026-10-26 11:41 GMT — PL-1769 Step 7.2" (heading at line 117, to end of file): the review is quoted whole, each line prefixed "> ". With the prefixes stripped, `diff ~/gi-pricing-plan.local/scratch/s1b-gate/pgpro-review-2026-10-26.md` against the quote is EMPTY (0 differing lines; 56 lines, counts "high 2, medium 7, low 10" present). The section declares no id rewrites and none were needed. The two HIGH lines are each followed by a "→ FD 8265" line outside the quote, as ruled in the c21cc8be fix; that is a deliberate variation from the " → FD 8265" suffix in the brief (a marker outside the quote keeps the quote verbatim, which the empty diff confirms). The two (v) query outputs are quoted: `gip_app` and `gip_app_login` both `rolcreaterole` f, `rolsuper` f; `pg_auth_members` one row, `admin_option` f — no route. The 07 census line is present: `git grep -n 'gip_app_login\|GIP_DATABASE_URL' docs/specs/07-platform.md` → no output (rc=1), no 07 line.

**Clause (c) — the full gate rc table is all 0: N (not met literally), the gate STANDS.** The gate's rc files are not all 0: `audit_docs=1`, `pytest=1` (13 failed, the same sorted FAILED ids as S1a's gate), the rest 0. It STANDS under condition 1(f) (to-lead "2026-10-26 11:29:13 GMT"); the rc table of record is the section "Gate of record" above in this RS. Note, outside F1: the LG's own "### Gate" and "### Audit" sections still read "pending — S1b GO not yet requested." at c21cc8be. That is F2 (owed to the mint, in the list above), not an F1 failure; the LG should carry the table before the mint, as the 11:36:30 title says "the gate table into LG 8248".

**No code since the gate.** `git diff --stat 54e0fca0 c21cc8be -- backend scripts deploy frontend packages` is EMPTY (rc 0). `git diff --stat 54e0fca0 c21cc8be` lists 5 docs files only: `docs/INDEX.md`, the FD 8265 essay, `docs/findings/register.md`, the LG, `docs/specs/01-data-management.md` (215 insertions, 3 deletions).

**FD 8265 (11:38:32 (i)): MET** (read to the clauses). The essay (`docs/findings/FD-08265-…`, front matter `id: FD-8265`, hyphen form) and the register row (`register.md:422`, "Filed under working id 8265") exist; severity **HIGH**, owner **WK-1178**, "**fix before close, by Fri 31 Oct 2026**". The essay carries both HIGH routes with `immutability.py:42-57`, the five same-class mediums (predefined roles, `pg_parameter_acl`, function and schema ownership, unconverged `gip_app`, memberships and role settings), the mitigation with `app-login-role.sql:16-17` quoted and the two query outputs, and the remedy (widen `P_OWN`; converge `gip_app` with `WITH INHERIT TRUE, SET FALSE`; amend FR-44; red-first on a planted role; a dated PL delta row with its SL reserved there). Two small variances, neither a defect: the title is "The startup least-privilege check misses CREATEROLE and ADMIN OPTION, two routes to the owner", not the ruled title text; and the essay says the SL is "reserved at that row", as ruled, so none is minted here.

**Quote-parity 82853038..c21cc8be:** confirmed by content, not by the lead's rc. The `git diff` of the LG between the two commits touches only the two HIGH lines and adds the two marker lines; the two quoted HIGH lines at c21cc8be equal the review's text (empty diff above).

**Proposed verdict on F1: CLEAN** — clause (a) met, (b) met, (c) N with the gate standing under 1(f), as the lead has already ruled. Residual for the lead: the LG Gate/Audit sections are still "pending" (F2, owed before the mint). I ran no tests, no gate, no audit-docs.
