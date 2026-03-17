#!/usr/bin/env bash
set -e
# Freeze a completed pass in the StrategyGraph
# Supports triggered_by edges via --triggered-nodes, --trigger-source, and --reason
# Usage: dag-freeze.sh <dag-path> <outcome> <detail> [--triggered-nodes <node>...] [--trigger-source <gate-node>] [--reason <reason>]

command -v hil-dag >/dev/null 2>&1 || { echo '{"status":"error","message":"hil-dag not found. Install: uv tool install humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"}' >&2; exit 1; }

if [ "$#" -lt 3 ]; then
    echo '{"status":"error","message":"Usage: dag-freeze.sh <dag-path> <outcome> <detail> [--triggered-nodes <node>...] [--reason <reason>]"}' >&2
    exit 1
fi

DAG_PATH="$1"
OUTCOME="$2"
DETAIL="$3"
shift 3

exec hil-dag freeze "$DAG_PATH" --outcome "$OUTCOME" --detail "$DETAIL" "$@"
