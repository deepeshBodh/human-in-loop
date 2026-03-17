#!/usr/bin/env bash
set -e
# Record analysis results (status + evidence + trace) for a node
# Targets the current pass by default, or a specific pass via optional argument
# Usage: dag-record.sh <dag-path> <node-id> <status> <evidence-json> <trace-json> [--pass <pass-number>] [--verdict <verdict>]

if command -v hil-dag >/dev/null 2>&1; then
    HIL_DAG=(hil-dag)
elif uv run hil-dag --help >/dev/null 2>&1; then
    HIL_DAG=(uv run hil-dag)
else
    echo '{"status":"error","message":"hil-dag not found. Install: uv add --dev (Python) or uv tool install (non-Python) humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"}' >&2; exit 1
fi

if [ "$#" -lt 5 ]; then
    echo '{"status":"error","message":"Usage: dag-record.sh <dag-path> <node-id> <status> <evidence-json> <trace-json> [--pass <pass-number>] [--verdict <verdict>]"}' >&2
    exit 1
fi

DAG_PATH="$1"; NODE_ID="$2"; STATUS="$3"; EVIDENCE="$4"; TRACE="$5"
shift 5

CMD=("${HIL_DAG[@]}" record "$DAG_PATH" --node "$NODE_ID" --status "$STATUS" --evidence "$EVIDENCE" --trace "$TRACE")

# Parse optional named flags
while [ "$#" -gt 0 ]; do
    case "$1" in
        --pass)    CMD+=(--pass "$2"); shift 2 ;;
        --verdict) CMD+=(--verdict "$2"); shift 2 ;;
        *)
            # Legacy: bare number treated as pass for backward compat
            CMD+=(--pass "$1"); shift ;;
    esac
done

exec "${CMD[@]}"
