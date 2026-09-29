---
id: FD-1193
family: finding
title: GitHub security coverage gaps
status: active
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: [FD-1194]
---

# FD-1193 — GitHub security coverage gaps

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the
maintainer's instruction ("yes record and implement") as relayed in the deputy's entry in the lead's local channel file `to-lead.md` stamped
2026-09-28 13:10:06 BST (item 2, "FD-A"). The evidence is the deputy's security review, read
by him at `e29daee6` without changing anything.

## Finding

Three of the review's six findings are **repository settings or token scopes**, and they are the
maintainer's:

- **S1:** code scanning is not configured.
- **S5:** secret scanning's non-provider patterns and validity checks are off.
- **S6:** the team's token cannot read the alert lists.

The other three, S2's version-update half, S3 and S4, are `FD-1194`'s. The automated-security-
fixes half of S2 is a setting, so it is also the maintainer's.

## Evidence

The deputy's table, verbatim:

| # | Finding | Evidence (command → result) |
|---|---|---|
| S1 | Code scanning not configured | `gh api repos/yes-404/gi-pricing-plan/code-scanning/default-setup` → `"state":"not-configured"`, languages actions/javascript-typescript/python; no CodeQL workflow in `.github/workflows/` |
| S2 | No Dependabot version updates; automated security fixes off | `git cat-file -e origin/main:.github/dependabot.yml` → absent; `gh api …/automated-security-fixes` → `{"enabled":false}`; `…/vulnerability-alerts` → 204 (alerts ON) |
| S3 | 3 dev-only frontend advisories | `pnpm --dir frontend audit --json` → high 1 (`js-yaml` 4.3.1 < 4.3.2, via `openapi-typescript>@redocly/openapi-core>js-yaml`); moderate 2 (`vitest` and `@vitest/mocker` 4.1.10 < 4.1.11, path traversal) |
| S4 | 3 workflows have no `permissions:` block (docs, frontend, history-policy) | `grep -c '^\s*permissions:'` → 0, 0, 0; python.yml → 1. Mitigated today: `gh api …/actions/permissions/workflow` → `"default_workflow_permissions":"read"` |
| S5 | Secret scanning's non-provider patterns and validity checks are off (scanning and push protection are on) | `gh api repos/yes-404/gi-pricing-plan --jq .security_and_analysis` |
| S6 | The alert lists cannot be read by the team's token | dependabot/code-scanning/secret-scanning `…/alerts` → HTTP 403 "Resource not accessible by personal access token" |
| — | Python: clean | `uv export --frozen --all-packages --no-hashes --no-emit-workspace` (colour off) → 111 packages; `uvx pip-audit -r … --no-deps --disable-pip` → "No known vulnerabilities found" |
| — | Workflow supply chain: clean | every `uses:` pinned to a 40-hex SHA; 0 `pull_request_target`; 0 untrusted `github.event.*` text in run steps |

## Disposition

**Deferred with an owner — the maintainer.** Event: the maintainer's dated line that the
settings are enabled, or declined with a reason. Nobody on the team changes a repository
setting (the same entry).
