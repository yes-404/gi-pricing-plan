#!/bin/bash
# SL-1455 Task 0 RERUN, asyncio debug mode OFF (maintainer ruling to-lead "2026-10-12 00:16:39 BST").
# PRE-REGISTERED with run.sh, t0_app.py, t0_driver.py and t0_analyse.py. Same wrapper as the first run:
#   flock -w 7200 /tmp/slots/gate-1 flock -w 600 /tmp/slots/gate-2 flock -w 600 /tmp/slots/small-test \
#     timeout 5700 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1455-t0/run2.sh \
#     > /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1455-t0/wrapper-rerun.out 2>&1
# Arms: bench-nogbm and bench-gbm. Rate: 25 rps, 3 repeats each, 20 s measured per repeat, one py-spy
# SAMPLING pass per arm (--nonblocking). The READING RULE is in t0_analyse.py (reading_rule) and in LG-9932.
# A TRUE ALONE window: no co-tenant, pollers included (the lead pauses them); run.sh records pgrep at OPEN/CLOSE.
set -u
export T0_ASYNCIO_DEBUG=0 T0_ARMS=bench-nogbm,bench-gbm T0_RATES=25 T0_RUNS=3 T0_SECONDS=20
exec bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1455-t0/run.sh
