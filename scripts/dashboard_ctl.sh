#!/bin/zsh
# Dashboard control: start | stop | status | restart. Runs from the main checkout; log in logs/dashboard.log.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; PORT=8771; LOG="$ROOT/logs/dashboard.log"
pid() { lsof -t -nP -iTCP:$PORT -sTCP:LISTEN 2>/dev/null | head -1; }
case "$1" in
  start)   [[ -n "$(pid)" ]] && { echo "already running, pid $(pid)"; exit 0; }
           mkdir -p "$ROOT/logs"; cd "$ROOT" && nohup python3 scripts/fit_dashboard.py --port $PORT >> "$LOG" 2>&1 &
           sleep 1; echo "started pid $(pid) on http://127.0.0.1:$PORT  (log: $LOG)";;
  stop)    P="$(pid)"; [[ -n "$P" ]] && kill "$P" && echo "stopped $P" || echo "not running";;
  status)  P="$(pid)"; [[ -n "$P" ]] && echo "running pid $P on http://127.0.0.1:$PORT" || echo "not running";;
  restart) "$0" stop; sleep 1; "$0" start;;
  *)       echo "usage: $0 start|stop|status|restart"; exit 1;;
esac
