# Findings register

A worked example of the register's real shape (Ruling 83 §1(g); `scripts/register-lint.py`
and this file's own header prose on the real tree): a table whose Finding-id column is
compound, `<description> (F<n>)`, never a bare `F<n>` on its own — replacing this
fixture's former invented bare-cell shape, which the real `docs/audit/register.md` has
never used. The migration script rewrites the parenthesised id and records the old
compound cell's token in the redirects file.

| Finding id | Concerns | Work item | Phase | Decision |
|---|---|---|---|---|
| First fixture finding (F1) | Example concern one | — | P1a | carry forward — fixture only |
| Second fixture finding (F2) | Example concern two | — | P1a | fix before close — fixture only |
