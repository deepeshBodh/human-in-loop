# SYNC-PATTERNS.md

Reference file for synchronization patterns, detection strategies, and validation procedures.

## Purpose

This file provides detailed guidance on detecting sync needs, performing synchronization, handling conflicts, and validating alignment between constitution and CLAUDE.md.

---

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
| Core Principles (7) | Principles Summary | Warning: Drift | Missing Principle VII |
| Technology Stack | Technical Stack | Aligned | - |
| Quality Gates | Quality Gates | Warning: Drift | Coverage changed to 70% |
| Governance | Development Workflow | Aligned | - |
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

---

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

---

## Sync Triggers

CLAUDE.md synchronization MUST occur when:

1. **Constitution amended**: Any version bump requires sync check
2. **New principle added**: MUST appear in Principles Summary
3. **Principle removed**: MUST be removed from Principles Summary
4. **Quality gate changed**: MUST update Quality Gates table
5. **Tech stack changed**: MUST update Technical Stack table
6. **Governance changed**: MUST update Development Workflow

---

## Commit Convention

When syncing, use this commit format:

```
docs: sync CLAUDE.md with constitution vX.Y.Z

- Updated Principles Summary (added Principle VII)
- Updated Quality Gates (coverage 70% -> 80%)
- Version aligned to X.Y.Z
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Full duplication** | CLAUDE.md becomes constitution copy | Use selective sync with summarization |
| **Stale sync** | CLAUDE.md lags behind constitution | Always sync on constitution amendment |
| **Missing version** | No version tracking in CLAUDE.md | Add version footer that matches constitution |
| **Partial sync** | Some sections synced, others not | Use checklist to verify all mapped sections |
| **Summary drift** | Summarization loses enforcement | Preserve enforcement keywords in summary |
| **Orphaned content** | Removed constitution content stays in CLAUDE.md | Check for removals during sync |

---

## Conflict Resolution

### Version Mismatch

If constitution and CLAUDE.md versions differ:
1. Constitution is authoritative
2. Update CLAUDE.md to match constitution version
3. Review all mapped sections for drift

### Content Conflict

If CLAUDE.md has content not in constitution:
1. Determine if content is CLAUDE.md-specific (allowed)
2. If it maps to constitution section, constitution is authoritative
3. Remove or update conflicting content

### Merge Strategy

When updating sections:
1. **Tables**: Replace entire table from constitution
2. **Principles**: Replace entire list, preserving numbering
3. **Text sections**: Update specific paragraphs, preserve structure

---

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

echo "Versions aligned"
```

This can be added to CI to catch sync drift.

---

## Detection Patterns

### Detecting What Needs Syncing

**Version-based detection**:
```bash
# Extract version numbers and compare
diff <(grep "Version" constitution.md) <(grep "Version" CLAUDE.md)
```

**Section-based detection**:
- Compare principle counts
- Compare table row counts
- Check for missing section headers

**Content-based detection**:
- Diff technology stack tables
- Diff quality gate thresholds
- Compare principle enforcement keywords
