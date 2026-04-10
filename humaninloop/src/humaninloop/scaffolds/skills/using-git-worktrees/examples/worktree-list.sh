#!/bin/bash
# worktree-list.sh - List all worktrees with additional status info
#
# Usage: ./worktree-list.sh
#
# Shows: path, branch, commit, uncommitted changes, disk usage

set -euo pipefail

echo "==> Git Worktrees"
echo ""

git worktree list --porcelain | while read -r line; do
    case "$line" in
        worktree\ *)
            WORKTREE_PATH="${line#worktree }"
            ;;
        HEAD\ *)
            HEAD="${line#HEAD }"
            ;;
        branch\ *)
            BRANCH="${line#branch refs/heads/}"

            # Get status
            if [[ -d "$WORKTREE_PATH" ]]; then
                cd "$WORKTREE_PATH"
                CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
                SIZE=$(du -sh "$WORKTREE_PATH" 2>/dev/null | cut -f1)
                cd - > /dev/null

                if [[ "$CHANGES" -gt 0 ]]; then
                    STATUS="$CHANGES uncommitted"
                else
                    STATUS="clean"
                fi
            else
                STATUS="MISSING"
                SIZE="N/A"
            fi

            printf "%-50s %-20s %-8s %s\n" "$WORKTREE_PATH" "$BRANCH" "$SIZE" "($STATUS)"
            ;;
        detached)
            BRANCH="(detached)"
            ;;
        "")
            # Reset for next entry
            WORKTREE_PATH=""
            HEAD=""
            BRANCH=""
            ;;
    esac
done

echo ""
echo "==> Summary"
TOTAL=$(git worktree list | wc -l | tr -d ' ')
echo "Total worktrees: $TOTAL"
