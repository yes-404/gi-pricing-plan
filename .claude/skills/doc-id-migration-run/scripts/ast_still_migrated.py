# Copied from ~/gi-pricing-plan.local/handover/ast_still_migrated.py (W37-6 run 2, 2026-09-17).
# Reformatted only for ruff (imports, line length, type hints, statement-per-line);
# logic and output format kept as written.
"""Check whether migration-introduced string values survive, or pre-migration
values got restored, at a later "fixed" ref.

Usage: ast_still_migrated.py <pre> <commit1_migrated> <fixed> <path>
"""
import ast
import subprocess
import sys

a, b, c, f = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]  # pre, commit1 (migrated), fixed


def consts(src: str) -> list[str]:
    t = ast.parse(src)
    ds = set()
    for n in ast.walk(t):
        if (
            isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and n.body
            and isinstance(n.body[0], ast.Expr)
            and isinstance(n.body[0].value, ast.Constant)
            and isinstance(n.body[0].value.value, str)
        ):
            ds.add(id(n.body[0].value))
    return [
        n.value
        for n in ast.walk(t)
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in ds
    ]


def src(r: str) -> str:
    return subprocess.run(["git", "show", f"{r}:{f}"], capture_output=True, text=True).stdout


A, B, C = consts(src(a)), consts(src(b)), consts(src(c))
migrated = set(B) - set(A)  # values introduced by the migration
pre = set(A) - set(B)  # values the migration removed
still = [v for v in set(C) if v in migrated]
restored = [v for v in set(C) if v in pre]
print(
    f"pre-only={len(pre)} migrated-only={len(migrated)} | "
    f"at fixed: restored(pre value present)={len(restored)} "
    f"still-migrated(migrated value present)={len(still)}"
)
for v in sorted(still)[:12]:
    print("  STILL:", repr(v)[:110])
