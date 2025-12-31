#!/bin/bash
# sample.sh - Example shell script for Claude Code plugin
# Demonstrates script integration with Claude Code plugins

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Plugin root is available via environment variable
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}"

# Function to display usage
usage() {
    echo -e "${BLUE}Sample Script - Example Plugin${NC}"
    echo ""
    echo "Usage: $0 [command] [args...]"
    echo ""
    echo "Commands:"
    echo "  greet [name]    Display a greeting"
    echo "  info            Show plugin information"
    echo "  list-files      List plugin files"
    echo "  help            Show this help message"
    echo ""
}

# Greet command
cmd_greet() {
    local name="${1:-World}"
    echo -e "${GREEN}Hello, ${name}!${NC}"
    echo "This greeting comes from sample.sh in the example-plugin."
}

# Info command
cmd_info() {
    echo -e "${BLUE}Plugin Information${NC}"
    echo "=================="
    echo "Plugin Root: ${PLUGIN_ROOT}"
    echo "Script Location: $0"
    echo "Shell: $SHELL"
    echo "Date: $(date)"
}

# List files command
cmd_list_files() {
    echo -e "${BLUE}Plugin Files${NC}"
    echo "============"
    if [ -d "$PLUGIN_ROOT" ]; then
        find "$PLUGIN_ROOT" -type f -name "*.md" -o -name "*.sh" -o -name "*.json" 2>/dev/null | sort
    else
        echo "Plugin root not found: $PLUGIN_ROOT"
    fi
}

# Main command dispatcher
main() {
    local command="${1:-help}"
    shift 2>/dev/null || true

    case "$command" in
        greet)
            cmd_greet "$@"
            ;;
        info)
            cmd_info
            ;;
        list-files)
            cmd_list_files
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            usage
            exit 1
            ;;
    esac
}

main "$@"
