#!/usr/bin/env bash
set -e
# Validate a DAG pass against a catalog
# Usage: dag-validate.sh <dag-path> <catalog-path>

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -ne 2 ]; then
    echo '{"status":"error","message":"Usage: dag-validate.sh <dag-path> <catalog-path>"}' >&2
    exit 1
fi

exec hil-dag validate "$1" --catalog "$2"
