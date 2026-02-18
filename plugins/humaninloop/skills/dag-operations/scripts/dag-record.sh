#!/usr/bin/env bash
set -e
# Record analysis results (status + evidence + trace) for a node
# Targets the current pass by default, or a specific pass via optional argument
# Usage: dag-record.sh <dag-path> <node-id> <status> <evidence-json> <trace-json> [<pass-number>]

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -lt 5 ] || [ "$#" -gt 6 ]; then
    echo '{"status":"error","message":"Usage: dag-record.sh <dag-path> <node-id> <status> <evidence-json> <trace-json> [<pass-number>]"}' >&2
    exit 1
fi

CMD=(hil-dag record "$1" --node "$2" --status "$3" --evidence "$4" --trace "$5")
if [ -n "$6" ]; then
    CMD+=(--pass "$6")
fi

exec "${CMD[@]}"
