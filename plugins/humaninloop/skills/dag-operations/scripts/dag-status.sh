#!/usr/bin/env bash
set -e
# Update a node's status in the StrategyGraph
# Targets the current pass by default, or a specific pass via optional argument
# Usage: dag-status.sh <dag-path> <node-id> <new-status> [<pass-number>]

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
    echo '{"status":"error","message":"Usage: dag-status.sh <dag-path> <node-id> <new-status> [<pass-number>]"}' >&2
    exit 1
fi

CMD=(hil-dag status "$1" --node "$2" --status "$3")
if [ -n "$4" ]; then
    CMD+=(--pass "$4")
fi

exec "${CMD[@]}"
