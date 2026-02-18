#!/usr/bin/env bash
set -e
# Add a catalog node to a StrategyGraph with edge inference
# Auto-creates the StrategyGraph if the file does not exist (bootstrap)
# Usage: dag-assemble.sh <dag-path> <catalog-path> <node-id> [<workflow-id>]

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
    echo '{"status":"error","message":"Usage: dag-assemble.sh <dag-path> <catalog-path> <node-id> [<workflow-id>]"}' >&2
    exit 1
fi

CMD=(hil-dag assemble "$1" --catalog "$2" --node "$3")
if [ -n "$4" ]; then
    CMD+=(--workflow "$4")
fi

exec "${CMD[@]}"
