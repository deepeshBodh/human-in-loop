#!/usr/bin/env bash
set -e
# Validate a node catalog
# Usage: dag-catalog-validate.sh <catalog-path>

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -ne 1 ]; then
    echo '{"status":"error","message":"Usage: dag-catalog-validate.sh <catalog-path>"}' >&2
    exit 1
fi

exec hil-dag catalog-validate "$1"
