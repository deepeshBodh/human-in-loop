# GitHub CLI Commands Reference

Quick reference for `gh` CLI commands used in issue management.

## Search and Query

```bash
# Search for similar issues
gh issue list --search "keyword1 keyword2" --state all

# Filter by label
gh issue list --label "bug" --state open

# Search with repository scope
gh issue list --repo owner/repo --search "in:title,body error"

# Search by author
gh issue list --author username --state all

# Search by assignee
gh issue list --assignee username --state open

# Combined filters
gh issue list --label "bug" --label "priority:high" --state open --assignee @me
```

## Issue Creation

```bash
# Create with interactive prompts
gh issue create

# Create with inline content
gh issue create --title "Bug: Login fails on Safari" --body "Steps to reproduce..."

# Create from file
gh issue create --title "Feature: Export to CSV" --body-file issue-body.md

# Create with labels and assignee
gh issue create --title "Title" --body "Body" --label "bug" --label "priority:high" --assignee username

# Create with milestone
gh issue create --title "Title" --body "Body" --milestone "v2.0"
```

## Status Updates

```bash
# Close with explanation
gh issue close ISSUE_NUMBER --comment "Resolved in PR #123"

# Reopen with context
gh issue reopen ISSUE_NUMBER --comment "Regression observed in v2.1"

# Transfer to another repository
gh issue transfer ISSUE_NUMBER target-repo

# Pin important issue
gh issue pin ISSUE_NUMBER

# Unpin issue
gh issue unpin ISSUE_NUMBER
```

## Issue Editing

```bash
# Add labels
gh issue edit ISSUE_NUMBER --add-label "needs-triage"

# Remove labels
gh issue edit ISSUE_NUMBER --remove-label "stale"

# Change assignee
gh issue edit ISSUE_NUMBER --add-assignee username

# Add to milestone
gh issue edit ISSUE_NUMBER --milestone "v2.0"

# Update title
gh issue edit ISSUE_NUMBER --title "New title"

# Update body
gh issue edit ISSUE_NUMBER --body "New body content"
gh issue edit ISSUE_NUMBER --body-file updated-body.md
```

## Batch Operations

```bash
# Close stale issues (use with caution)
gh issue list --state open --label "stale" --json number -q ".[].number" | \
  xargs -I {} gh issue close {} --comment "Closing as stale. Reopen if still relevant."

# Bulk add label
gh issue list --search "keyword" --json number -q ".[].number" | \
  xargs -I {} gh issue edit {} --add-label "needs-triage"

# Bulk assign to milestone
gh issue list --label "v2-candidate" --json number -q ".[].number" | \
  xargs -I {} gh issue edit {} --milestone "v2.0"

# Remove label from multiple issues
gh issue list --label "wontfix" --json number -q ".[].number" | \
  xargs -I {} gh issue edit {} --remove-label "wontfix"
```

## Viewing and Comments

```bash
# View issue details
gh issue view ISSUE_NUMBER

# View in browser
gh issue view ISSUE_NUMBER --web

# Add comment
gh issue comment ISSUE_NUMBER --body "Comment text"

# Add comment from file
gh issue comment ISSUE_NUMBER --body-file comment.md

# List comments
gh issue view ISSUE_NUMBER --comments
```

## Security Advisories

```bash
# List security advisories
gh api repos/OWNER/REPO/security-advisories

# Create security advisory (requires appropriate permissions)
gh api repos/OWNER/REPO/security-advisories \
  --method POST \
  -f summary="SQL Injection in login form" \
  -f description="The username parameter is not sanitized..." \
  -f severity="critical"
```

## Useful Queries

```bash
# Issues without labels
gh issue list --search "no:label" --state open

# Issues with no assignee
gh issue list --search "no:assignee" --state open

# Issues older than 30 days
gh issue list --search "created:<$(date -v-30d +%Y-%m-%d)" --state open

# Issues mentioning specific text
gh issue list --search "in:body 'error message'"

# Issues by multiple labels (AND)
gh issue list --label "bug" --label "priority:high"

# Count issues by label
gh issue list --label "bug" --json number -q ". | length"
```
