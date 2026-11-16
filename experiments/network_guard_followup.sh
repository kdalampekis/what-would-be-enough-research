#!/usr/bin/env bash
# Pause the run processes while the provider cannot be reached (laptop moved, Wi-Fi lost, sleep/wake), and
# resume them when it can. Pausing changes nothing in any protocol: it only keeps calls from failing with
# local connection errors, which would use up a job's limited retry attempts. Every pause and resume is
# logged in results/raw/network_guard.log. Approved by the project owner on 2026-11-14.
# Usage: experiments/network_guard_followup.sh &     (same guard, for the follow-up runs; stop it with: pkill -f network_guard_followup.sh)
cd "$(dirname "$0")/.."
LOG=results/raw/network_guard.log
HOST=https://api.prod.adaptionlabs.ai/
PATTERN='experiments/run_followup\.py'
state=up; fails=0
reachable() { curl -s -m 4 -o /dev/null "$HOST"; }   # any HTTP response counts; only a failed connection does not
echo "$(date -u +%FT%TZ) guard started" >> "$LOG"
while true; do
  if reachable; then
    fails=0
    if [ "$state" = down ]; then
      sleep 3   # let the connection settle
      if reachable; then
        pkill -CONT -f "$PATTERN"; state=up
        echo "$(date -u +%FT%TZ) provider reachable: resumed $(pgrep -f "$PATTERN" | wc -l | tr -d ' ') processes" >> "$LOG"
      fi
    fi
  else
    fails=$((fails + 1))
    if [ "$state" = up ] && [ "$fails" -ge 2 ]; then
      pkill -STOP -f "$PATTERN"; state=down
      echo "$(date -u +%FT%TZ) provider unreachable: paused $(pgrep -f "$PATTERN" | wc -l | tr -d ' ') processes" >> "$LOG"
    fi
  fi
  sleep 3
done
