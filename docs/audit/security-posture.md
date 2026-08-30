# Repository security posture

**What this is.** The security configuration of `yes-404/gi-pricing-plan` as a **public**
repository: what is enforced, what is not, and what was deliberately left alone. Every row
states whether it was **measured** or merely read, because a setting nobody has verified is a
setting nobody has.

**Why it exists.** The audit performed when the repository went public, and the decisions
taken from it, lived only in a local handover file — a directory whose own README says *"never
a git repo, never pushed, nothing here is a record."* A security decision that survives only
in operational scratch is not recorded at all. `CLAUDE.md` §12: every decision lands as a dated
artifact.

**Scope note.** This is the *repository platform's* posture — GitHub settings, rulesets,
workflow trust. It is not the *product's* security requirements, which are numbered NFRs in
`docs/specs/` and are audited as requirements.

---

## 1. Went public 2026-08-30, and what was checked at the time

Audited before and around publication, findings recorded here rather than left in the
handover:

- **No `pull_request_target`** in any workflow — the trigger that runs fork code with write
  scope.
- **No self-hosted runners.** All jobs are GitHub-hosted.
- **Zero secret references in workflows** — `grep -rn "secrets\." .github/workflows/` returns
  nothing, re-verified 2026-08-30. There is no secret for a malicious workflow to exfiltrate,
  which is why the read-only token below costs nothing.
- **462 commits scanned** for credential material at the time of publication: clean.
- **`examples/` is freMTPL2 only** — a public dataset. No policy, claims or exposure data has
  ever been in the tree.
- **One localhost default credential**, inside a `SecretStr`, which **fails closed** outside
  development.
- **Production guards hold**: `dev_auth_enabled` is refused in UAT and PROD; TLS and OIDC are
  required.

**One accepted exposure, with an instrument rather than a fix.** 73 commits on the now-public
`main` carry a `claude.ai/code/session_…` trailer (113 occurrences, 14 distinct session ids;
**no tracked file contains one**). Register row **F49**: accepted on the maintainer's ruling,
because removing them means rewriting public history and invalidating every SHA cited across
the register, the plans and the closure records. The instrument is a **squash-time strip**,
proven on real merges and landed in `docs/process/delivery-process.md` §15 and
`.claude/skills/git-hygiene`.

## 2. `main` is governed by a ruleset

**`main-protection`** (id 21860967), set 2026-08-30 14:04Z, replacing a two-rule predecessor.
Targets `~DEFAULT_BRANCH` only — **feature branches are unconstrained**, verified by pushing
and deleting one under it.

`deletion` · `non_fast_forward` · `required_linear_history` · `pull_request`, with
`allowed_merge_methods: ["squash"]`, `required_review_thread_resolution: true`, and
**`bypass_actors: []`** — no exceptions, including for the token this team uses.

**`required_approving_review_count` is 0, and that is correct rather than a gap.** Every pull
request in this repository is authored by the same account the automation's token belongs to,
and **GitHub does not permit an account to approve its own pull request**. Any non-zero count
would deadlock every merge permanently, with no one able to supply the approval.
`require_extra_approval_for_unattributed_changes` is *on* and carries the same hazard; it was
**tested empirically** rather than assumed safe — a probe PR carrying the usual author and the
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer reported `reviewDecision: ""`
and merged. The full parameter table and the reasoning are in `.claude/skills/git-hygiene`.

## 3. Settings as at 2026-08-30, after that day's changes

Read back from the API after each write — **never inferred from a call's exit code**, because
several of these accept a write and silently keep the old value.

| Setting | State | Note |
|---|---|---|
| Secret scanning | **enabled** | Turned on 2026-08-30; was disabled |
| Secret scanning **push protection** | **enabled** | Turned on 2026-08-30. A push carrying a recognised secret is refused |
| Vulnerability alerts | **enabled** | Turned on 2026-08-30; previously returned 404 |
| Fork-PR workflow approval | **`all_external_contributors`** | Tightened 2026-08-30 from `first_time_contributors`. No effect on this team, which is not external |
| `default_workflow_permissions` | `read` | **Already correct** before the review — it had been carried on a to-do list as outstanding, wrongly |
| `can_approve_pull_request_reviews` | `false` | Already correct |
| Action refs | **SHA-pinned** | All seven refs across three workflows |
| `allow_forking` | `true` | Normal for a public repo |
| `web_commit_signoff_required` | `false` | Not required |

**Two settings refuse to change**, reported rather than claimed: `secret_scanning_non_provider_patterns`
and `secret_scanning_validity_checks`. The `PATCH` returns 200 and the value stays `disabled` —
almost certainly they require GitHub Advanced Security rather than being available here. **A
200 is not a confirmation**; both were caught only by reading the value back.

## 4. Open, with the reason each is open

- **Dependabot security updates — a policy decision, deliberately not taken by the lead.**
  Enabling it opens pull requests authored by `dependabot[bot]`, and the maintainer's standing
  instruction of 2026-08-30 is to **merge only pull requests authored by `yes-404`** and report
  the rest. Those PRs would therefore accumulate unmerged by rule. Vulnerability *alerts* are
  enabled, so detection is not lost. If the updates are wanted, `dependabot[bot]` needs an
  explicit carve-out from the merge rule.
- **`sha_pinning_required` is not enabled.** The pins in §3 are the prerequisite and are now in
  place; enforcing it is a further, separate change.
- **`allowed_actions` is `all`.** Any action from any author may run. Restricting it to
  GitHub-owned, verified creators plus explicit patterns for the two third-party actions in use
  (`astral-sh/setup-uv`, `pnpm/action-setup`) is real hardening and is scheduled, deliberately,
  for a gap between slices — a wrong pattern breaks every workflow at once.

## 5. The standing rule this posture depends on

**Merge only pull requests authored by `yes-404`; report any other author.** Measured
2026-08-30: **all 466 pull requests** in the repository's history are `yes-404`-authored, and
the fork count was **0**. The rule and its query live in `.claude/skills/git-hygiene`; the
merge authority it bounds is `.claude/roles/lead.md`'s.

**It is enforced by a person reading an author field.** No ruleset expresses "only this
author may be merged", and `CLAUDE.md` §13 is explicit that a check which has never printed a
failure has not been tested. Treat this control as the weakest one on the page.
