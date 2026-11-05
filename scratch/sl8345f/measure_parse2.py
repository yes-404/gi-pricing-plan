# ruff: noqa
from decimal import Decimal
from pricing_core.rating.compile import cell_parses
for s in ["0." + "1"*k for k in (20,25,26,27,28,29,30)]:
    print("0.+%d dp (%d digits):" % (len(s)-2, len(Decimal(s).as_tuple().digits)), cell_parses(s))
for k in (27,28,29,30):
    s = "1"*k + ".5"
    print("int part %d + .5 (%d digits, 1 dp):" % (k, k+1), cell_parses(s))
s = "0.15967315159416064262391"  # step-7 prefix: dp count probe
for k in range(20, 30):
    print("dp", k, cell_parses("0.1596731515941606426239122222"[:2+k]))
