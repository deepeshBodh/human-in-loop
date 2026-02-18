#!/usr/bin/env bash
set -e
# Add a catalog node to a StrategyGraph with edge inference
# Auto-creates the StrategyGraph if the file does not exist (bootstrap)
#
# Usage (by node ID):
#   dag-assemble.sh <dag-path> <catalog-path> --node <id> [--workflow <wf>]
#
# Usage (by capability tags):
#   dag-assemble.sh <dag-path> <catalog-path> --capability-tags <t1> [<t2>...] [--node-type <type>] [--workflow <wf>]

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: cd humaninloop_brain && uv sync"}' >&2; exit 1; }

if [ "$#" -lt 3 ]; then
    echo '{"status":"error","message":"Usage: dag-assemble.sh <dag-path> <catalog-path> --node <id> | --capability-tags <t1> [<t2>...] [--node-type <type>] [--workflow <wf>]"}' >&2
    exit 1
fi

DAG_PATH="$1"
CATALOG_PATH="$2"
shift 2

CMD=(hil-dag assemble "$DAG_PATH" --catalog "$CATALOG_PATH")

while [ "$#" -gt 0 ]; do
    case "$1" in
        --node)
            CMD+=(--node "$2")
            shift 2
            ;;
        --capability-tags)
            shift
            CMD+=(--capability-tags)
            while [ "$#" -gt 0 ] && [[ "$1" != --* ]]; do
                CMD+=("$1")
                shift
            done
            ;;
        --node-type)
            CMD+=(--node-type "$2")
            shift 2
            ;;
        --workflow)
            CMD+=(--workflow "$2")
            shift 2
            ;;
        --pass)
            CMD+=(--pass "$2")
            shift 2
            ;;
        *)
            echo "{\"status\":\"error\",\"message\":\"Unknown argument: $1\"}" >&2
            exit 1
            ;;
    esac
done

exec "${CMD[@]}"
