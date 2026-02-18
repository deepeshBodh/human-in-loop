#!/usr/bin/env bash
set -e
# Validate a node catalog
# Usage: dag-catalog-validate.sh <catalog-path>

if [ "$#" -ne 1 ]; then
    echo '{"status":"error","message":"Usage: dag-catalog-validate.sh <catalog-path>"}' >&2
    exit 1
fi

exec hil-dag catalog-validate "$1"
