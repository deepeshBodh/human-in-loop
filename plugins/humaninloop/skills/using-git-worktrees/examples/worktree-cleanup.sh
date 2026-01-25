#!/bin/bash
# worktree-cleanup.sh - Clean up a git worktree and optionally delete its branch
#
# Usage: ./worktree-cleanup.sh <worktree-path> [--delete-branch]
#
# Examples:
#   ./worktree-cleanup.sh .worktrees/feature-auth
#   ./worktree-cleanup.sh .worktrees/feature-auth --delete-branch

set -euo pipefail

WORKTREE_PATH="${1:?Usage: $0 <worktree-path> [--delete-branch]}"
DELETE_BRANCH="${2:-}"

# Get branch name before removing worktree
BRANCH_NAME=$(git worktree list --porcelain | grep -A2 "worktree.*$WORKTREE_PATH" | grep "branch" | sed 's/branch refs\/heads\///')

if [[ -z "$BRANCH_NAME" ]]; then
    echo "Error: Could not find worktree at $WORKTREE_PATH"
    git worktree list
    exit 1
fi

echo "==> Removing worktree at $WORKTREE_PATH (branch: $BRANCH_NAME)"

# Check for uncommitted changes
if [[ -d "$WORKTREE_PATH" ]]; then
    cd "$WORKTREE_PATH"
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "Warning: Worktree has uncommitted changes"
        git status --short
        read -p "Remove anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        cd - > /dev/null
        git worktree remove --force "$WORKTREE_PATH"
    else
        cd - > /dev/null
        git worktree remove "$WORKTREE_PATH"
    fi
else
    # Path doesn't exist, prune stale entry
    git worktree prune
fi

echo "==> Worktree removed"

# Optionally delete the branch
if [[ "$DELETE_BRANCH" == "--delete-branch" ]]; then
    echo "==> Deleting branch $BRANCH_NAME"
    if git branch -d "$BRANCH_NAME" 2>/dev/null; then
        echo "==> Branch deleted (was merged)"
    else
        read -p "Branch not fully merged. Force delete? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git branch -D "$BRANCH_NAME"
            echo "==> Branch force deleted"
        fi
    fi
fi

# Final prune
git worktree prune

echo "==> Cleanup complete"
git worktree list
