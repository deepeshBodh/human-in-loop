#!/usr/bin/env bash
set -e
# Create a new empty DAG pass
# Usage: dag-create.sh <workflow-id> <pass-number> <output-path>

if [ "$#" -ne 3 ]; then
    echo '{"status":"error","message":"Usage: dag-create.sh <workflow-id> <pass-number> <output-path>"}' >&2
    exit 1
fi

exec hil-dag create "$1" --pass "$2" --output "$3"
