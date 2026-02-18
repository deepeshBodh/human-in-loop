#!/usr/bin/env bash
set -e
# Add a catalog node to a DAG pass with edge inference
# Usage: dag-assemble.sh <dag-path> <catalog-path> <node-id>

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -ne 3 ]; then
    echo '{"status":"error","message":"Usage: dag-assemble.sh <dag-path> <catalog-path> <node-id>"}' >&2
    exit 1
fi

exec hil-dag assemble "$1" --catalog "$2" --node "$3"
