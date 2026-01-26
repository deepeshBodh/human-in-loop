---
name: using-git-worktrees
description: >
  This skill MUST be invoked when the user says "create worktree", "isolated workspace",
  "parallel branch work", "git worktree", "feature isolation", or "branch workspace".
  SHOULD also invoke when starting feature work that needs isolation from current workspace.
---

# Using Git Worktrees

## Overview

Create isolated workspaces sharing the same repository for parallel branch work. Follow systematic directory selection and safety verification to ensure reliable isolation.

**Violating the letter of the rules is violating the spirit of the rules.** Skipping safety verification "just this once" or assuming directory locations are the most common causes of worktree problems.

## When to Use

- Starting feature work requiring isolation from current workspace
- Working on multiple branches simultaneously
- Executing implementation plans in a clean environment (**OPTIONAL:** pairs with `humaninloop:plan`)
- Testing changes without affecting the main working directory
- Parallel code review while continuing development

## When NOT to Use

- **Single-branch workflows**: No need for isolation when working linearly
- **Quick fixes on current branch**: Worktrees add overhead for simple changes
- **Non-git repositories**: Worktrees are git-specific
- **Temporary experiments**: A simple branch may suffice
- **When disk space is constrained**: Each worktree duplicates working files

## Red Flags - STOP and Restart Properly

If any of these thoughts arise, STOP immediately:

- "The directory is probably already ignored"
- "I know where worktrees go in this project"
- "Tests are slow, I'll skip baseline verification"
- "This is a simple project, safety checks are overkill"
- "User wants to start quickly, I'll verify later"
- "I've done this before, I can skip the priority order"

**All of these mean:** Rationalization is occurring. Restart with proper process.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Directory is probably ignored" | Probably =/= verified. One `git check-ignore` command takes seconds. Always verify. |
| "I know where worktrees go here" | Knowledge =/= following process. Check existing directories, then CLAUDE.md, then ask. |
| "Tests are slow" | Slow tests =/= skip tests. Baseline verification prevents hours of debugging wrong baseline. |
| "Simple project" | Simple projects have caused the biggest worktree pollution. Process exists because of them. |
| "Will verify later" | Later rarely comes. Worktree contents in git history are permanent mistakes. Do it now. |
| "User seems impatient" | Impatience is not permission. Explain why verification matters. |

## Core Process

### Step 1: Directory Selection

Follow this priority order strictly:

**1.1 Check Existing Directories**

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

If found, use that directory. If both exist, `.worktrees` takes precedence.

**1.2 Check CLAUDE.md Configuration**

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

If a preference is specified, use it without asking.

**1.3 Ask User**

Only when no directory exists AND no CLAUDE.md preference:

```
No worktree directory found. Where should worktrees be created?

1. .worktrees/ (project-local, hidden)
2. ~/worktrees/<project-name>/ (global location)

Which is preferred?
```

**No exceptions:**
- Not for "obvious" projects
- Not for "standard" setups
- Not when "everyone uses .worktrees"
- Not even if user says "just use the usual place"

### Step 2: Safety Verification

**For project-local directories (.worktrees or worktrees):**

MUST verify directory is ignored before creating worktree:

```bash
# Verify directory is ignored (respects local, global, and system gitignore)
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If NOT ignored:**

1. Add appropriate line to `.gitignore`
2. Commit the change: `git add .gitignore && git commit -m "chore: add worktree directory to gitignore"`
3. Proceed with worktree creation

**Why critical:** Prevents accidentally committing worktree contents to repository. Worktree contents in git history cannot be fully removed without history rewriting.

**For global directories (e.g., ~/worktrees):**

No gitignore verification needed - outside project entirely.

**No exceptions:**
- Not for "I'm pretty sure it's already ignored"
- Not for "this repo has good gitignore defaults"
- Not when "I'll check after creating the worktree"
- Not even for "the user said don't worry about it"

### Step 3: Create Worktree

```bash
# Get project name
project=$(basename "$(git rev-parse --show-toplevel)")

# Determine full path based on location type
# For project-local:
path=".worktrees/$BRANCH_NAME"
# For global:
path="$HOME/worktrees/$project/$BRANCH_NAME"

# Create worktree with new branch
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### Step 4: Run Project Setup

Auto-detect and run appropriate setup commands:

| File | Setup Command |
|------|---------------|
| `package.json` | `npm install` or `yarn install` or `pnpm install` |
| `Cargo.toml` | `cargo build` |
| `requirements.txt` | `pip install -r requirements.txt` |
| `pyproject.toml` | `poetry install` or `pip install -e .` |
| `go.mod` | `go mod download` |
| `Gemfile` | `bundle install` |

Skip setup only if no recognizable project file exists.

### Step 5: Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
# Use project-appropriate command
npm test        # Node.js
cargo test      # Rust
pytest          # Python
go test ./...   # Go
bundle exec rspec  # Ruby
```

**If tests fail:** Report failures with details. Ask whether to proceed or investigate.

**If tests pass:** Report success with test count.

**If no test command available:** Note this and proceed, but warn that baseline is unverified.

**No exceptions:**
- Not for "tests are slow, user wants to start"
- Not for "I ran tests recently in the main worktree"
- Not when "this is a simple feature, baseline doesn't matter"
- Not even for "user explicitly asked to skip testing"

### Step 6: Report Completion

```
Worktree ready at <full-path>
Branch: <branch-name>
Tests: <N> passing, 0 failures (or "no test suite detected")
Ready to implement <feature-name>
```

After implementation is complete, follow the cleanup workflow in the Multi-Worktree Management section.

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored first) |
| `worktrees/` exists | Use it (verify ignored first) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md, then ask user |
| Directory not ignored | Add to .gitignore, commit, then proceed |
| Tests fail during baseline | Report failures, ask before proceeding |
| No package manager file | Skip dependency install, note it |
| No test suite | Proceed with warning about unverified baseline |

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Skipping ignore verification | Worktree contents get tracked, pollute git status, potentially committed | Always run `git check-ignore` for project-local directories |
| Assuming directory location | Creates inconsistency, violates project conventions | Follow priority: existing > CLAUDE.md > ask |
| Proceeding with failing tests | Cannot distinguish new bugs from pre-existing issues | Report failures, get explicit permission |
| Hardcoding setup commands | Breaks on projects using different tools | Auto-detect from project files |
| Skipping user prompt | Creates worktrees where user does not want them | When ambiguous, always ask |

## Error Recovery

### Worktree Creation Fails

| Error | Cause | Resolution |
|-------|-------|------------|
| `fatal: '<path>' already exists` | Directory exists from previous attempt | Remove directory: `rm -rf <path>`, then retry |
| `fatal: '<branch>' is already checked out` | Branch active in another worktree | Use different branch name or remove existing worktree |
| `fatal: not a git repository` | Not in a git repo | Navigate to git repository root first |
| `fatal: invalid reference` | Base branch doesn't exist | Verify branch name, fetch from remote if needed |

### Recovery Steps

1. **Check worktree state:** `git worktree list`
2. **Identify stuck entries:** Look for paths that no longer exist
3. **Prune stale entries:** `git worktree prune`
4. **Force remove if needed:** `git worktree remove --force <path>`

### Locked Worktrees

If a worktree shows as locked:

```bash
# Check lock status
git worktree list --porcelain | grep -A1 locked

# Unlock (only if certain no process is using it)
git worktree unlock <path>
```

## Multi-Worktree Management

### Listing Active Worktrees

```bash
git worktree list
# Output:
# /path/to/main        abc1234 [main]
# /path/to/.worktrees/feature-a  def5678 [feature-a]
# /path/to/.worktrees/feature-b  ghi9012 [feature-b]
```

### Switching Between Worktrees

Each worktree is independent. Simply `cd` to the desired worktree path. No checkout or stash required.

### Cleanup Workflow

After branch is merged or abandoned:

```bash
# 1. Return to main worktree
cd /path/to/main

# 2. Remove the worktree
git worktree remove .worktrees/feature-name

# 3. Delete the branch (if merged)
git branch -d feature-name

# 4. Prune any stale references
git worktree prune
```

For comprehensive cleanup after feature completion, follow the steps above.

### Disk Space Considerations

Each worktree duplicates working files (not git objects). Monitor disk usage:

```bash
# Check worktree sizes
du -sh .worktrees/*

# Remove largest/oldest worktrees first when space constrained
```

## Reference Commands

```bash
# List all worktrees
git worktree list

# Create worktree with new branch
git worktree add <path> -b <branch-name>

# Create worktree from existing branch
git worktree add <path> <existing-branch>

# Remove a worktree
git worktree remove <path>

# Force remove (uncommitted changes)
git worktree remove --force <path>

# Prune stale worktree entries
git worktree prune

# Lock worktree (prevent accidental removal)
git worktree lock <path>

# Unlock worktree
git worktree unlock <path>
```

## Example Scripts

Working shell scripts are available in `examples/`:

- [examples/worktree-setup.sh](examples/worktree-setup.sh) - Complete worktree creation with safety checks
- [examples/worktree-cleanup.sh](examples/worktree-cleanup.sh) - Safe removal with uncommitted change detection
- [examples/worktree-list.sh](examples/worktree-list.sh) - Enhanced listing with status and disk usage
