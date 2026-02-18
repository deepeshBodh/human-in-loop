#!/usr/bin/env bash
set -e
# Update a node's status in a DAG pass
# Usage: dag-status.sh <dag-path> <node-id> <new-status>

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -ne 3 ]; then
    echo '{"status":"error","message":"Usage: dag-status.sh <dag-path> <node-id> <new-status>"}' >&2
    exit 1
fi

exec hil-dag status "$1" --node "$2" --status "$3"
