#!/usr/bin/env bash
set -e
# Get topological execution order for a DAG pass
# Usage: dag-sort.sh <dag-path>

if [ "$#" -ne 1 ]; then
    echo '{"status":"error","message":"Usage: dag-sort.sh <dag-path>"}' >&2
    exit 1
fi

exec hil-dag sort "$1"
