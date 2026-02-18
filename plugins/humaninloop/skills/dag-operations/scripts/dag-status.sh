#!/usr/bin/env bash
set -e
# Update a node's status in a DAG pass
# Usage: dag-status.sh <dag-path> <node-id> <new-status>

if [ "$#" -ne 3 ]; then
    echo '{"status":"error","message":"Usage: dag-status.sh <dag-path> <node-id> <new-status>"}' >&2
    exit 1
fi

exec hil-dag status "$1" --node "$2" --status "$3"
