# Copied from ~/gi-pricing-plan.local/handover/ast_tables.py (W37-6 run 2, 2026-09-17).
# Reformatted only for ruff (imports, line length, type hints, statement-per-line,
# context-managed file open); logic and output format kept as written.
"""Compare named top-level constant tables in one file between two refs.

Usage: ast_tables.py <ref_a> <ref_b_or_WORKTREE> <path> <name> [name ...]

`ref_b` may be the literal string `WORKTREE` to read the live working-tree file
instead of a git ref.
"""
import ast
import subprocess
import sys

a, b, f = sys.argv[1], sys.argv[2], sys.argv[3]
names = sys.argv[4:]


def tables(src: str) -> dict[str, str]:
    t = ast.parse(src)
    out = {}
    for n in ast.walk(t):
        if (
            isinstance(n, ast.AnnAssign)
            and isinstance(n.target, ast.Name)
            and n.target.id in names
            and n.value is not None
        ):
            out[n.target.id] = ast.dump(n.value)
        if (
            isinstance(n, ast.Assign)
            and len(n.targets) == 1
            and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id in names
        ):
            out[n.targets[0].id] = ast.dump(n.value)
    return out


sa = subprocess.run(["git", "show", f"{a}:{f}"], capture_output=True, text=True).stdout
if b == "WORKTREE":
    with open(f) as fh:
        sb = fh.read()
else:
    sb = subprocess.run(["git", "show", f"{b}:{f}"], capture_output=True, text=True).stdout
ta, tb = tables(sa), tables(sb)
for n in names:
    if n not in ta:
        print(f"{n}: absent at {a}")
        continue
    if n not in tb:
        print(f"{n}: absent at {b}")
        continue
    print(f"{n}: {'SAME' if ta[n] == tb[n] else 'DIFF'}")
