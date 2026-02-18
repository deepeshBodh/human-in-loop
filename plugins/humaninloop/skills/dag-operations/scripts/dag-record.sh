#!/usr/bin/env bash
set -e
# Record analysis results (status + evidence + trace) for a node
# Usage: dag-record.sh <dag-path> <node-id> <status> <evidence-json> <trace-json>

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -ne 5 ]; then
    echo '{"status":"error","message":"Usage: dag-record.sh <dag-path> <node-id> <status> <evidence-json> <trace-json>"}' >&2
    exit 1
fi

exec hil-dag record "$1" --node "$2" --status "$3" --evidence "$4" --trace "$5"
