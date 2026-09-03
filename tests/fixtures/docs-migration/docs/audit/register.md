# Findings register

A worked example of the register's real shape (Ruling 83 §1(g); `scripts/register-lint.py`
and this file's own header prose on the real tree): a table whose Finding-id column is
compound, `<description> (F<n>)`, never a bare `F<n>` on its own — replacing this
fixture's former invented bare-cell shape, which the real `docs/audit/register.md` has
never used. The migration script records the old compound cell's token in the redirects
file; per the maintainer's 2026-09-03 ruling (W37-6) it does **not** rewrite the
parenthesised id in place — `F<n>` stays a resolver alias to W37-11, so this cell is
unchanged by `migrate`.

| Finding id | Concerns | Work item | Phase | Decision |
|---|---|---|---|---|
| First fixture finding (F1) | Example concern one | — | P1a | carry forward — fixture only |
| Second fixture finding (F2) | Example concern two | — | P1a | fix before close — fixture only |
| Third fixture finding (F3) | Example concern three | — | P1a | **Resolved 2026-08-21** — fixture only, PR #1 |
