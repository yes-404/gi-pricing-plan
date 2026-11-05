# ruff: noqa
"""cell_parses before (6291e196^ = c836b932) and after (6291e196 = e6d141ba) R2's change, and the raw zen error."""
from decimal import Decimal, InvalidOperation
import zen
def before(raw):
    try:
        return isinstance(zen.evaluate_expression(raw), (int, float))
    except (RuntimeError, ValueError):
        return False
def after(raw):
    try:
        Decimal(raw)
        r = zen.evaluate_expression(raw)
    except (InvalidOperation, RuntimeError, ValueError):
        return False
    return isinstance(r, (int, float)) and not isinstance(r, bool)
for n in (28, 29, 30):
    s = "1" + "2" * (n - 1)
    try: v = repr(zen.evaluate_expression(s))
    except Exception as e: v = f"{type(e).__name__}: {e}"[:150]
    print(f"{n} digits int  before={before(s)} after={after(s)} zen -> {v}")
for k in (28, 29):
    s = "0." + "1" * k
    try: v = repr(zen.evaluate_expression(s))
    except Exception as e: v = f"{type(e).__name__}: {e}"[:150]
    print(f"0.+{k}dp before={before(s)} after={after(s)} zen -> {v}")
diff = []
cands = ["1", "1.5", "-1.5", "+1", "0", "-0", "1_000", "1e5", "1.36e-7", "1E+2", ".5", "5.", " 1", "1 ", "Infinity", "NaN", "-Infinity", "0x10", "1+1", "true", "false", "٣", "1,5", "", "1" * 29, "1" * 30, "0." + "1" * 28, "0." + "1" * 29]
for c in cands:
    b, a = before(c), after(c)
    if b != a: diff.append((c, b, a))
print("inputs where before != after:", diff)
