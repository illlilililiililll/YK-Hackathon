#!/bin/bash
# usage: wait_rows.sh <results.jsonl relative to ~/ykrun> <target rows> <max seconds>
F="$HOME/ykrun/$1"
end=$(( $(date +%s) + $3 ))
while [ "$(date +%s)" -lt "$end" ]; do
  n=$(wc -l < "$F" 2>/dev/null || echo 0)
  [ "$n" -ge "$2" ] && break
  sleep 5
done
echo "rows: $(wc -l < "$F" 2>/dev/null || echo 0) / $2   $(date +%T)"
