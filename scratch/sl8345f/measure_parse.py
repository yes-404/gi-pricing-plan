# ruff: noqa
from pricing_core.rating.compile import cell_parses
for n in range(10, 45):
    s = "1." + "2" * (n - 1)
    i = "1" + "2" * (n - 1)
    print(n, "digits dec:", cell_parses(s), " int:", cell_parses(i))
