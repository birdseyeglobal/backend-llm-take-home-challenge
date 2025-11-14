#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./start_service_dev.sh [--debug] [PORT]
# Examples:
#   ./start_service_dev.sh                 # normal run on 3070
#   ./start_service_dev.sh 3080            # normal run on 3080
#   ./start_service_dev.sh --debug         # debugpy attach on 3070
#   ./start_service_dev.sh --debug 3080    # debugpy attach on 3080

DEBUG_MODE="false"
PORT_FROM_ARG=""

# Parse args: optional --debug flag and optional PORT positional
for arg in "$@"; do
  case "$arg" in
    --debug)
      DEBUG_MODE="true"
      ;;
    *)
      if [[ -z "${PORT_FROM_ARG}" ]]; then
        PORT_FROM_ARG="$arg"
      else
        echo "Unexpected argument: $arg" >&2
        exit 1
      fi
      ;;
  esac
done

PORT="${PORT_FROM_ARG:-3070}"

# Environment defaults from the old script
export BETTER_EXCEPTIONS=1
export LOG_JSON_FORMAT="0"
export LOG_LEVEL="DEBUG"
if [[ "$DEBUG_MODE" == "true" ]]; then
  # Debug mode: start uvicorn under debugpy, wait for VS Code to attach on 127.0.0.1:5678
  exec poetry run python -Xfrozen_modules=off -m debugpy \
    --listen 127.0.0.1:5678 \
    --wait-for-client \
    -m uvicorn app.main:app \
    --host 127.0.0.1 \
    --port "${PORT}" \
    --reload
else
  # Default behavior, matching the old script
  exec poetry run uvicorn app.main:app \
    --host 127.0.0.1 \
    --port "${PORT}" \
    --reload
fi
