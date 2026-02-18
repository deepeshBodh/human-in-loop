#!/usr/bin/env bash
set -e
# Freeze a completed DAG pass
# Usage: dag-freeze.sh <dag-path> <outcome> <detail> <rationale>

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -ne 4 ]; then
    echo '{"status":"error","message":"Usage: dag-freeze.sh <dag-path> <outcome> <detail> <rationale>"}' >&2
    exit 1
fi

exec hil-dag freeze "$1" --outcome "$2" --detail "$3" --rationale "$4"
