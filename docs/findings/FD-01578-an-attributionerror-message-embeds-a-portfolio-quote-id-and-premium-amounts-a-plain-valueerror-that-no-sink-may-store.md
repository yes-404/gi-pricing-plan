---
id: FD-1578
family: finding
title: An AttributionError message embeds a portfolio quote_id and premium amounts, and AttributionError is a plain ValueError — no sink may store its text, and the platform's safe-text helper renders its type only
status: draft
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: auditor
tree: 3519a919e30aa6993d40b22df212dd57bbd4a685
corrected_by: []
relates: [WK-673, SL-1387, SL-1388, PL-1501, LG-9440, FR-1397, NFR-499]
---

# FD-1578 — AttributionError carries portfolio input in its message

*Disclosure: drafted under working id 9453; minted as FD-1578 on 2026-10-10, in the D5 batch mint PR.*

**DRAFT**, filed on `draft/d6-fd9453-oq9454`, no PR, at the lead's ruling (`to-lead.md`, "2026-10-10 02:47:13 BST — RULING: S4 S-B sinks, option (1): all 3 sinks use safe_error_text; the leak test is red-first; one product FD (owner WK-673)", item 4: *"FD (product, not process; owner WK-673): AttributionError is a plain ValueError whose message at analysis.py:1041 (merged in S3) embeds a portfolio quote_id. Remedy: input-free messages, then CodedError. It rides D5 or the next batch. Severity proposed by the auditor. On main today, no production sink stores it (S4 is the first caller), which goes in the FD's evidence."*). All line numbers are at `origin/main` `3519a919` (tree `a732799c`; the file is `packages/pricing-core/src/pricing_core/rating/analysis.py`, last changed by `e40ab532`, #1243) unless marked.

## Finding

`AttributionError` (`analysis.py:493`, `class AttributionError(ValueError)`) is a plain `ValueError` carrying a `code`. Two of its raise sites build the message from portfolio input:

1. **`analysis.py:1041-1045`**, in `attribute`:
   `raise AttributionError(_ATTRIBUTION_FAILED, f"policy {q} is quoted in the baseline and the candidate but has no premium under the subset bundle for changes [{ids}]")`.
   `q` iterates `compared` (`:1035-1039`), the portfolio's `quote_id` values (`read_portfolio` requires the `quote_id` column, `:110-116`). So the message names one policy of the book.
2. **`_reconcile(q, …)`** (call at `:1060`; the function at `:911-926`), whose `label` is that same `q`:
   `f"attribution does not reconcile for {label}: the Shapley parts sum to {sum(parts)} minor units, not the total change {total}"` and the sibling at `:922-925`. The message carries the policy's `quote_id` **and** its premium change in minor units (`total`, `sum(parts)`). The portfolio-level call at `:1070` uses the label `"the portfolio"`, which is an aggregate and names no policy.

`pricing_core.safe_error` (`safe_error.py`) keeps a message only if the exception is a `ValidationError` (`safe_error_detail`, `:119-126`) or a `CodedError` (`:64`, "its text is `CODE: message`, and the message is input-free"). An `AttributionError` is neither, so `safe_error_text` (`:128-134`) returns `AttributionError` and nothing else. Two consequences, one per direction of the fix:

- A sink that stores `str(exc)` stores a quote id and a premium change (NFR-499, `03` `:1404`, whose clarification says the clause "governs persistence, not only log output").
- A sink that uses `safe_error_text` is safe, and an operator then sees the type name and the Job's `code` and nothing that says which policy failed or why.

The other raise sites carry no portfolio value: `:549`, `:564` (fixed text), `:720` (change ids), `:868` (change ids in the pairs), `:1019-1021` (the subset's change ids, and `safe_error_text(exc)` of the compile error, already the safe form). `PortfolioFrameError` (`:88`, also a plain `ValueError`) was checked for the same defect and does **not** have it: its messages at `:111`, `:116`, `:120`, `:123`, `:125`, `:145` and `:217` name a column, a dtype or a row count, and the column names are the contract's reserved or declared names (`_STAMPED`, `_FRAME_COLUMNS`, the spec's `segments`); a count is a count of rows, not a value. It has the second consequence (a safe-text sink renders the type only), not the first.

## Evidence

**1. No production sink stores it on `main` today.** At `3519a919` the `attribute` and `AttributionError` are named only by `packages/pricing-core/tests/test_rating_attribution.py` and `scripts/measure-attribution-cost.py` (`git grep -n -E 'AttributionError|\battribute\(' -- backend/src scripts packages '*.py'`, excluding `analysis.py` itself); nothing under `backend/src/` names either. S4 (`SL-1388`, `PL-1501`) is the first caller. So the defect is latent on `main`.

**2. S4 first stored it, then did not.** On `origin/sl-1388-wk673-s4-backend-job-routes`, the three new sinks (`backend/src/app/api/dislocation_runs.py:183`, `backend/src/app/platform/dislocation_runs.py:253`, `backend/src/app/worker/dislocation_handlers.py:236`) first built the message with `str(exc)` (`2a01db1e^`, `dislocation_handlers.py:234`: `PlatformError(exc.code, …, 422, str(exc))`). Commit `2a01db1e` ("route the three error sinks through safe_error_text", ruling 02:43:18 and 02:47:13) changed all three to `safe_error_text(exc)`. `LG-9440` (commit `648ee30e`), the entry "Plan delta NFR-499, 2026-10-10", records the red-first test: `test_a_run_that_does_not_reconcile_fails_with_attribution_reconciliation_failed` (`048708c3`) raises the `:1041` text for policy `Q000` and asserts the stored Job error and the `GET /api/v1/jobs/{id}` body hold no `Q000`; RED at `6ed5da3f` (`str(exc)`), GREEN at `048708c3`.

**3. What that test does and does not show.** It monkeypatches `attribute` to raise the `:1041` text; it does not reach `:1041` through a constructed portfolio, because that error needs a subset bundle that drops a compared policy and no fixture builds one (`LG-9440`'s own note). The leak path (message text in the sink) is shown; the raise path (a real portfolio reaching `:1041`) is not.

**4. The guard is by caller.** Nothing in `pricing_core` prevents the next caller (S5's submission path, `SL-1547`, or a CLI) from storing `str(exc)`. The S4 fix removes three sinks; the defect stays in the exception.

*Not run:* no check was run for this draft (brief: git and file edits only). Every quote above was read from the tree named; none was executed.

## Severity and remedy

**Proposed severity: MEDIUM (the auditor proposes; the lead decides).** Reason: the content is policy-level input (a quote id, a premium change) leaving through a stored Job error and an API body, which is the class NFR-499 names; it misprices nothing, and today it is reachable by no stored path, so it is not HIGH. It is not LOW because the only guard is a per-sink choice, and a sink that gets it wrong discloses silently, with no failing test unless that sink's author writes the red one S4 wrote.

**Remedy, in order (the ruling's):**
1. **Input-free messages.** Rewrite the two messages so that neither names a `quote_id` nor an amount (for example, the count of affected policies and the change ids, which are derived names, not data). Where the failing policy must stay findable, that is the remedy slice's design choice and goes to `docs/open-questions.md` if it is open.
2. **Then make `AttributionError` (not `PortfolioFrameError`, whose messages are already input-free) a `CodedError`.** `safe_error_text` then keeps the message, so an operator regains the hint safely. `CodedError` is a `ValueError`, so every `except ValueError` and the `.code` attribute are unchanged. Step 2 is only safe after step 1: promoting the class first would make the allow-list store the quote id.
3. **A test over the class:** every `AttributionError` raised through `attribute` on a portfolio with a known `quote_id` and known amounts holds neither in `safe_error_text(exc)`; it fails on `2a01db1e^`'s `str(exc)` form.

**Owner: WK-673** (the ruling). Event that next confirms or discharges it: the remedy's PR with test 3 red at its parent commit; or S5's merge if it adds a fourth sink first, in which case that slice's ACK checks the sink's text.
