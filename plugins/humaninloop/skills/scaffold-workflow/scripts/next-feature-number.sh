#!/usr/bin/env bash
#
# next-feature-number.sh - Determine the next sequential feature number
#
# Usage: next-feature-number.sh [specs_dir]
# Output: Zero-padded 3-digit number (e.g., "005")
#
# Behavior:
#   - Fetches all remote branches (if git available)
#   - Scans both local/remote branches and specs directory
#   - Returns the next available number (max + 1)
#   - Zero-pads to 3 digits
#   - Starts at 001 if no existing features found
#
# Examples:
#   ./next-feature-number.sh
#   # Output: 001 (if no features exist)
#
#   ./next-feature-number.sh specs/
#   # Output: 005 (if highest existing is 004)
#

set -e

# Optional specs directory argument
SPECS_DIR="${1:-specs}"

# Function to find the repository root by searching for existing project markers
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ] || [ -d "$dir/.humaninloop" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Function to get highest number from specs directory
get_highest_from_specs() {
    local specs_dir="$1"
    local highest=0

    if [ -d "$specs_dir" ]; then
        for dir in "$specs_dir"/*; do
            [ -d "$dir" ] || continue
            dirname=$(basename "$dir")
            number=$(echo "$dirname" | grep -o '^[0-9]\+' || echo "0")
            number=$((10#$number))
            if [ "$number" -gt "$highest" ]; then
                highest=$number
            fi
        done
    fi

    echo "$highest"
}

# Function to get highest number from git branches
get_highest_from_branches() {
    local highest=0

    # Get all branches (local and remote)
    branches=$(git branch -a 2>/dev/null || echo "")

    if [ -n "$branches" ]; then
        while IFS= read -r branch; do
            # Clean branch name: remove leading markers and remote prefixes
            clean_branch=$(echo "$branch" | sed 's/^[* ]*//; s|^remotes/[^/]*/||')

            # Extract feature number if branch matches pattern ###-*
            if echo "$clean_branch" | grep -q '^[0-9]\{3\}-'; then
                number=$(echo "$clean_branch" | grep -o '^[0-9]\{3\}' || echo "0")
                number=$((10#$number))
                if [ "$number" -gt "$highest" ]; then
                    highest=$number
                fi
            fi
        done <<< "$branches"
    fi

    echo "$highest"
}

# Function to check existing branches (local and remote) and return next available number
check_existing_branches() {
    local specs_dir="$1"

    # Fetch all remotes to get latest branch info (suppress errors if no remotes)
    git fetch --all --prune 2>/dev/null || true

    # Get highest number from ALL branches (not just matching short name)
    local highest_branch=$(get_highest_from_branches)

    # Get highest number from ALL specs (not just matching short name)
    local highest_spec=$(get_highest_from_specs "$specs_dir")

    # Take the maximum of both
    local max_num=$highest_branch
    if [ "$highest_spec" -gt "$max_num" ]; then
        max_num=$highest_spec
    fi

    # Return next number
    echo $((max_num + 1))
}

# Resolve repository root
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT=$(git rev-parse --show-toplevel)
    HAS_GIT=true
else
    REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
    if [ -z "$REPO_ROOT" ]; then
        # If no repo root found, use current directory
        REPO_ROOT="$(pwd)"
    fi
    HAS_GIT=false
fi

# Resolve specs directory relative to repo root if not absolute
if [[ "$SPECS_DIR" != /* ]]; then
    SPECS_DIR="$REPO_ROOT/$SPECS_DIR"
fi

# Determine next feature number
if [ "$HAS_GIT" = true ]; then
    NEXT_NUMBER=$(check_existing_branches "$SPECS_DIR")
else
    # Fall back to local directory check only
    HIGHEST=$(get_highest_from_specs "$SPECS_DIR")
    NEXT_NUMBER=$((HIGHEST + 1))
fi

# Output zero-padded 3-digit number
printf "%03d\n" "$NEXT_NUMBER"
