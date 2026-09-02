# Findings register

A worked example of the legacy findings register shape: a table with a Finding-id column
using the bare `F<n>` form. The migration script rewrites each Finding-id cell to its newly
assigned id and records the old bare form in the redirects file.

| Finding id | Concerns | Work item | Phase | Decision |
|---|---|---|---|---|
| F1 | Example concern one | — | P1a | carry forward — fixture only |
| F2 | Example concern two | — | P1a | fix before close — fixture only |
