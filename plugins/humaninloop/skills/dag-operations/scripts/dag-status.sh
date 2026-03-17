#!/usr/bin/env bash
set -e
# Update a node's status in the StrategyGraph
# Targets the current pass by default, or a specific pass via optional argument
# Usage: dag-status.sh <dag-path> <node-id> <new-status> [--verdict <verdict>] [--pass <pass-number>]

if command -v hil-dag >/dev/null 2>&1; then
    HIL_DAG=(hil-dag)
elif uv run hil-dag --help >/dev/null 2>&1; then
    HIL_DAG=(uv run hil-dag)
else
    echo '{"status":"error","message":"hil-dag not found. Install: uv add --dev (Python) or uv tool install (non-Python) humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"}' >&2; exit 1
fi

if [ "$#" -lt 3 ]; then
    echo '{"status":"error","message":"Usage: dag-status.sh <dag-path> <node-id> <new-status> [--verdict <verdict>] [--pass <pass-number>]"}' >&2
    exit 1
fi

CMD=("${HIL_DAG[@]}" status "$1" --node "$2" --status "$3")
shift 3

# Pass through remaining flags (--verdict, --pass)
CMD+=("$@")

exec "${CMD[@]}"
