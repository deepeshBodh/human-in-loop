#!/usr/bin/env bash
set -e
# Get topological execution order for a DAG pass
# Usage: dag-sort.sh <dag-path>

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: uv tool install humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"}' >&2; exit 1; }

if [ "$#" -ne 1 ]; then
    echo '{"status":"error","message":"Usage: dag-sort.sh <dag-path>"}' >&2
    exit 1
fi

exec hil-dag sort "$1"
