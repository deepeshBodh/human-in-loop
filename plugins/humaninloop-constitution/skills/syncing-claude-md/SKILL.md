---
name: syncing-claude-md
description: Ensure CLAUDE.md mirrors constitution sections per explicit mapping. Use when synchronizing CLAUDE.md with constitution, validating alignment, or when you see "CLAUDE.md sync", "agent instructions", or need to propagate constitution changes to CLAUDE.md.
---

# Syncing CLAUDE.md

## Purpose

Ensure CLAUDE.md (the primary AI agent instruction file) remains synchronized with the constitution. CLAUDE.md serves a different audience (AI agents) than the constitution (human governance), so synchronization is selective—specific sections map with explicit sync rules.

## Why CLAUDE.md Sync Matters

```
┌─────────────────────────────────────────────────────────────────┐
│                    TWO AUDIENCES                                 │
├────────────────────────────┬────────────────────────────────────┤
│       CONSTITUTION         │           CLAUDE.MD                │
├────────────────────────────┼────────────────────────────────────┤
│ Audience: Humans           │ Audience: AI Agents                │
│ Purpose: Governance        │ Purpose: Runtime Instructions      │
│ Format: Detailed           │ Format: Actionable                 │
│ Contains: Rationale        │ Contains: Rules + Commands         │
│ Updated: Deliberately      │ Updated: Must track constitution   │
└────────────────────────────┴────────────────────────────────────┘
```

If CLAUDE.md diverges from the constitution, AI agents operate with outdated or incorrect guidance, undermining governance.

## Mandatory Sync Mapping

The following sections MUST be synchronized:

| Constitution Section | CLAUDE.md Section | Sync Rule |
|---------------------|-------------------|-----------|
| Core Principles | Principles Summary | MUST list all principles with enforcement keywords |
| Technology Stack | Technical Stack | MUST match exactly (table format) |
| Quality Gates | Quality Gates | MUST match exactly (table format) |
| Governance | Development Workflow | MUST include versioning rules and commit conventions |
| Project Structure | Project Structure | MUST match if present in constitution |
| Layer Import Rules | Architecture | MUST replicate dependency rules |

## Sync Rule Definitions

### MUST list all with enforcement

Principles appear in CLAUDE.md as a summarized list including enforcement keywords:

**Constitution (detailed)**:
```markdown
### I. Test-First Development (NON-NEGOTIABLE)

All production code MUST be written following test-driven development...

**Enforcement**:
- CI MUST verify test-before-implementation order
- Coverage MUST meet 80% minimum

**Testability**:
- Pass: All tests pass, coverage ≥80%
- Fail: Tests missing or coverage below threshold

**Rationale**: Tests written after implementation...
```

**CLAUDE.md (summarized)**:
```markdown
## Principles

1. **Test-First Development** (NON-NEGOTIABLE): TDD mandatory. CI enforces test-before-implementation. Coverage ≥80%.
2. **Code Quality**: Zero lint warnings. Functions ≤40 lines. Cyclomatic complexity ≤10.
3. ...
```

### MUST match exactly

Tables are copied directly with no summarization:

**Constitution**:
```markdown
## Technology Stack

| Category | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12 | Type hints, performance |
| Framework | FastAPI | Async-first, Pydantic |
```

**CLAUDE.md**:
```markdown
## Technical Stack

| Category | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12 | Type hints, performance |
| Framework | FastAPI | Async-first, Pydantic |
```

## Synchronization Process

### Step 1: Read Both Files

```bash
# Read current constitution
cat .humaninloop/memory/constitution.md

# Read current CLAUDE.md
cat CLAUDE.md
```

### Step 2: Extract Mapped Sections

For each section in the sync mapping:
1. Locate section in constitution
2. Locate corresponding section in CLAUDE.md
3. Compare content per sync rule

### Step 3: Identify Gaps

Create a gap report:

```markdown
## Sync Gap Report

| Constitution Section | CLAUDE.md Section | Status | Gap |
|---------------------|-------------------|--------|-----|
| Core Principles (7) | Principles Summary | ⚠️ Drift | Missing Principle VII |
| Technology Stack | Technical Stack | ✅ Aligned | - |
| Quality Gates | Quality Gates | ⚠️ Drift | Coverage changed to 70% |
| Governance | Development Workflow | ✅ Aligned | - |
```

### Step 4: Generate Updates

For each gap, generate the CLAUDE.md update:

```markdown
## Required CLAUDE.md Updates

### Update 1: Add Missing Principle
**Location**: Principles Summary section
**Action**: Add item 7

```markdown
7. **Dependency Management**: Dependencies MUST be evaluated before adoption. Flutter Favorites preferred. Quarterly updates required.
```

### Update 2: Fix Coverage Threshold
**Location**: Quality Gates table, row 4
**Action**: Change coverage from 70% to 80%
```

### Step 5: Apply Updates

Update CLAUDE.md with synchronized content. Ensure:
- Version in CLAUDE.md matches constitution version
- All mapped sections are updated
- No orphaned references to old content

### Step 6: Validate Alignment

After updates, re-run comparison to verify:
- [ ] All mapped sections present in CLAUDE.md
- [ ] Content matches per sync rules
- [ ] Version numbers match
- [ ] No contradictions between files

## CLAUDE.md Structure Template

CLAUDE.md should follow this structure for proper sync:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with this codebase.

## Project Overview

[Brief project description]

## Principles

[Synchronized from Constitution Core Principles]

1. **[Principle I Name]**: [Summary with enforcement]
2. **[Principle II Name]**: [Summary with enforcement]
...

## Technical Stack

[Synchronized from Constitution Technology Stack - exact match]

| Category | Choice | Rationale |
|----------|--------|-----------|
| ... | ... | ... |

## Quality Gates

[Synchronized from Constitution Quality Gates - exact match]

| Gate | Requirement | Measurement | Enforcement |
|------|-------------|-------------|-------------|
| ... | ... | ... | ... |

## Development Workflow

[Synchronized from Constitution Governance]

### Branch Strategy
[From governance or conventions]

### Commit Conventions
[Conventional commits or project standard]

### Code Review Requirements
[From governance]

## Project Structure

[Synchronized if present in constitution]

```
project/
├── src/
│   ├── domain/
│   └── ...
```

---

**Version**: X.Y.Z (synced with constitution)
**Last Synced**: YYYY-MM-DD
```

## Sync Validation Checklist

Before completing synchronization:

**Completeness**:
- [ ] All Core Principles listed with enforcement
- [ ] Technology Stack table matches exactly
- [ ] Quality Gates table matches exactly
- [ ] Governance rules reflected in Development Workflow
- [ ] Project Structure matches if present

**Accuracy**:
- [ ] Version numbers match (constitution = CLAUDE.md)
- [ ] No contradictions between files
- [ ] Enforcement keywords preserved
- [ ] Thresholds and metrics accurate

**Format**:
- [ ] Tables properly formatted
- [ ] Principles numbered consistently
- [ ] Section headers match mapping

## Sync Triggers

CLAUDE.md synchronization MUST occur when:

1. **Constitution amended**: Any version bump requires sync check
2. **New principle added**: MUST appear in Principles Summary
3. **Principle removed**: MUST be removed from Principles Summary
4. **Quality gate changed**: MUST update Quality Gates table
5. **Tech stack changed**: MUST update Technical Stack table
6. **Governance changed**: MUST update Development Workflow

## Commit Convention

When syncing, use this commit format:

```
docs: sync CLAUDE.md with constitution vX.Y.Z

- Updated Principles Summary (added Principle VII)
- Updated Quality Gates (coverage 70% → 80%)
- Version aligned to X.Y.Z
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Full duplication** | CLAUDE.md becomes constitution copy | Use selective sync with summarization |
| **Stale sync** | CLAUDE.md lags behind constitution | Always sync on constitution amendment |
| **Missing version** | No version tracking in CLAUDE.md | Add version footer that matches constitution |
| **Partial sync** | Some sections synced, others not | Use checklist to verify all mapped sections |
| **Summary drift** | Summarization loses enforcement | Preserve enforcement keywords in summary |
| **Orphaned content** | Removed constitution content stays in CLAUDE.md | Check for removals during sync |

## Automation Opportunities

Consider automating sync validation:

```bash
# Script: validate-claude-md-sync.sh

#!/bin/bash
# Compare constitution version with CLAUDE.md version
CONST_VERSION=$(grep "^\*\*Version\*\*:" .humaninloop/memory/constitution.md | head -1)
CLAUDE_VERSION=$(grep "^\*\*Version\*\*:" CLAUDE.md | head -1)

if [ "$CONST_VERSION" != "$CLAUDE_VERSION" ]; then
  echo "ERROR: Version mismatch"
  echo "Constitution: $CONST_VERSION"
  echo "CLAUDE.md: $CLAUDE_VERSION"
  exit 1
fi

echo "✅ Versions aligned"
```

This can be added to CI to catch sync drift.
