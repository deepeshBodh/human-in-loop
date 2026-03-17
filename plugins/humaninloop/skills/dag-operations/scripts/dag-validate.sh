#!/usr/bin/env bash
set -e
# Validate a DAG pass against a catalog
# Usage: dag-validate.sh <dag-path> <catalog-path>

if command -v hil-dag >/dev/null 2>&1; then
    HIL_DAG=(hil-dag)
elif uv run hil-dag --help >/dev/null 2>&1; then
    HIL_DAG=(uv run hil-dag)
else
    echo '{"status":"error","message":"hil-dag not found. Install: uv add --dev (Python) or uv tool install (non-Python) humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"}' >&2; exit 1
fi

if [ "$#" -ne 2 ]; then
    echo '{"status":"error","message":"Usage: dag-validate.sh <dag-path> <catalog-path>"}' >&2
    exit 1
fi

exec "${HIL_DAG[@]}" validate "$1" --catalog "$2"
