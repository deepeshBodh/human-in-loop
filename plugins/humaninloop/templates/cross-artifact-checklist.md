# Cross-Artifact Consistency Checklist

Use this lightweight checklist to verify previous artifacts remain consistent with the new artifact, without re-reading them in full.

## Purpose

This checklist enables **incremental validation**—fully reviewing only the new artifact while performing quick consistency checks on previous artifacts. This preserves rigor while eliminating redundant full re-reads.

## Quick Consistency Checks

### Entity Name Consistency
- [ ] New artifact uses same entity names as data-model.md
- [ ] No new entities introduced that aren't in data-model.md
- [ ] Spelling/casing matches exactly

### Requirement Traceability
- [ ] New artifact references FR-XXX / US-XXX IDs correctly
- [ ] No orphaned requirements (mentioned but not addressed)
- [ ] No invented requirements (addressed but not in spec)

### Decision Consistency
- [ ] New artifact honors decisions from research.md
- [ ] No contradictions with chosen technologies/approaches
- [ ] Rationale still applies

### Naming Conventions
- [ ] API endpoints follow patterns established in research
- [ ] Field names match data model attributes
- [ ] Error codes are consistent

## How to Use

1. **Extract entity mentions** from new artifact
2. **Grep previous artifacts** for those entity names
3. **Spot-check 2-3 requirement IDs** trace correctly
4. **Verify technology choices** match research decisions
5. **Flag inconsistencies** as Important issues

## Time Budget

| Previous Artifact | Max Time |
|-------------------|----------|
| research.md | 1-2 minutes |
| data-model.md | 1-2 minutes |
| Total per phase | 2-3 minutes |

This checklist replaces full re-read of previous artifacts (5-10 minutes each).

## When to Escalate

Escalate to full re-review if:
- 2+ consistency issues found in one artifact
- Contradictions detected between artifacts
- Entity names don't match at all
- Requirement IDs are systematically wrong

## Issue Classification

Issues found via consistency check are classified as:

| Issue Type | Severity | Example |
|------------|----------|---------|
| Entity name mismatch | Important | "User" vs "Account" inconsistency |
| Missing requirement trace | Important | FR-003 not addressed in contracts |
| Decision contradiction | Critical | Using JWT when research chose sessions |
| Minor spelling variance | Minor | "userId" vs "user_id" |
