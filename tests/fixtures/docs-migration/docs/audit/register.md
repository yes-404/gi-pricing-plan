# Findings register

A worked example of the legacy findings register shape: a table with a Finding-id column
using the bare `F<n>` form. `doc-id.py migrate` rewrites each Finding-id cell to its newly
assigned `FD-<n>` and records the old bare form in `docs/REDIRECTS.csv` (NT-0019 §4 step 1
assigns the number; step 6 rewrites the citation).

| Finding id | Concerns | Work item | Phase | Decision |
|---|---|---|---|---|
| F1 | Example concern one | — | P1a | carry forward — fixture only |
| F2 | Example concern two | — | P1a | fix before close — fixture only |
