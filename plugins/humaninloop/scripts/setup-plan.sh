#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
FORCE=false

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --force)
            FORCE=true
            ;;
        --help|-h)
            echo "Usage: $0 [--json] [--force]"
            echo "  --json    Output results in JSON format"
            echo "  --force   Overwrite existing plan.md without prompting"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *)
            echo "WARNING: Unknown argument '$arg' ignored" >&2
            ;;
    esac
done

# Get script directory and load common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get all paths and variables from common functions
eval $(get_feature_paths)

# Check if we're on a proper feature branch (only for git repos)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# Ensure the feature directory exists
mkdir -p "$FEATURE_DIR"

# Check if plan.md already exists
if [[ -f "$IMPL_PLAN" ]] && ! $FORCE; then
    echo "ERROR: plan.md already exists at $IMPL_PLAN" >&2
    echo "Use --force to overwrite, or delete the file manually." >&2
    exit 1
fi

# Copy plan template if it exists (check plugin templates first, then fallback)
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$PLUGIN_ROOT/templates/plan-template.md"
if [[ ! -f "$TEMPLATE" ]]; then
    # Fallback to user project templates
    TEMPLATE="$REPO_ROOT/.humaninloop/templates/plan-template.md"
fi

if [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$IMPL_PLAN"
    echo "Copied plan template to $IMPL_PLAN"
else
    echo "Warning: Plan template not found"
    # Create a basic plan file if template doesn't exist
    touch "$IMPL_PLAN"
fi

# Output results
if $JSON_MODE; then
    printf '{"FEATURE_DIR":"%s","FEATURE_SPEC":"%s","IMPL_PLAN":"%s","TASK_MAPPING":"%s","TASKS":"%s","RESEARCH":"%s","DATA_MODEL":"%s","QUICKSTART":"%s","CONTRACTS_DIR":"%s","BRANCH":"%s","HAS_GIT":"%s"}\n' \
        "$FEATURE_DIR" "$FEATURE_SPEC" "$IMPL_PLAN" "$TASK_MAPPING" "$TASKS" "$RESEARCH" "$DATA_MODEL" "$QUICKSTART" "$CONTRACTS_DIR" "$CURRENT_BRANCH" "$HAS_GIT"
else
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "IMPL_PLAN: $IMPL_PLAN"
    echo "TASK_MAPPING: $TASK_MAPPING"
    echo "TASKS: $TASKS"
    echo "RESEARCH: $RESEARCH"
    echo "DATA_MODEL: $DATA_MODEL"
    echo "QUICKSTART: $QUICKSTART"
    echo "CONTRACTS_DIR: $CONTRACTS_DIR"
    echo "BRANCH: $CURRENT_BRANCH"
    echo "HAS_GIT: $HAS_GIT"
fi
