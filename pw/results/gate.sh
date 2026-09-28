# wait (max 15 min) until 1-min load <= 12; print the uptime the run starts under
for i in $(seq 1 90); do l=$(cut -d' ' -f1 /proc/loadavg); awk -v l=$l 'BEGIN{exit !(l<=12)}' && break; sleep 10; done
echo "START $(uptime)"
