#!/bin/bash
# worktree-setup.sh - Create and configure a git worktree with project setup
#
# Usage: ./worktree-setup.sh <branch-name> [base-branch]
#
# Examples:
#   ./worktree-setup.sh feature/auth          # Creates from current HEAD
#   ./worktree-setup.sh feature/auth main     # Creates from main branch

set -euo pipefail

BRANCH_NAME="${1:?Usage: $0 <branch-name> [base-branch]}"
BASE_BRANCH="${2:-HEAD}"

# Determine worktree directory
if [[ -d ".worktrees" ]]; then
    WORKTREE_DIR=".worktrees"
elif [[ -d "worktrees" ]]; then
    WORKTREE_DIR="worktrees"
else
    WORKTREE_DIR=".worktrees"
    mkdir -p "$WORKTREE_DIR"
fi

WORKTREE_PATH="$WORKTREE_DIR/$BRANCH_NAME"

echo "==> Creating worktree at $WORKTREE_PATH"

# Safety: verify directory is ignored
if [[ "$WORKTREE_DIR" == ".worktrees" || "$WORKTREE_DIR" == "worktrees" ]]; then
    if ! git check-ignore -q "$WORKTREE_DIR" 2>/dev/null; then
        echo "==> Adding $WORKTREE_DIR to .gitignore"
        echo "$WORKTREE_DIR/" >> .gitignore
        git add .gitignore
        git commit -m "chore: add $WORKTREE_DIR to gitignore"
    fi
fi

# Create the worktree
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" "$BASE_BRANCH"
cd "$WORKTREE_PATH"

echo "==> Running project setup"

# Auto-detect and run setup
if [[ -f "package.json" ]]; then
    if [[ -f "pnpm-lock.yaml" ]]; then
        pnpm install
    elif [[ -f "yarn.lock" ]]; then
        yarn install
    else
        npm install
    fi
elif [[ -f "Cargo.toml" ]]; then
    cargo build
elif [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
elif [[ -f "pyproject.toml" ]]; then
    if command -v poetry &>/dev/null; then
        poetry install
    else
        pip install -e .
    fi
elif [[ -f "go.mod" ]]; then
    go mod download
elif [[ -f "Gemfile" ]]; then
    bundle install
else
    echo "==> No recognized project file, skipping dependency install"
fi

echo "==> Worktree ready at: $(pwd)"
echo "==> Branch: $BRANCH_NAME"
