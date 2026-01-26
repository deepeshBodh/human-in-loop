---
name: syncing-claude-md
description: Use when user asks to "sync CLAUDE.md", "update agent instructions", "propagate constitution changes", or mentions "CLAUDE.md sync", "agent instructions", or "constitution alignment".
---

# Syncing CLAUDE.md

## Overview

Ensure CLAUDE.md (the primary AI agent instruction file) remains synchronized with the constitution. CLAUDE.md serves a different audience (AI agents) than the constitution (human governance), so synchronization is selective—specific sections map with explicit sync rules.

## When to Use

- Constitution has been amended (any version bump)
- New principle added to constitution
- Principle removed from constitution
- Quality gate thresholds changed
- Technology stack updated
- Governance rules modified
- User explicitly requests CLAUDE.md sync
- After running `humaninloop:authoring-constitution` or `humaninloop:brownfield-constitution`

## When NOT to Use

- **Constitution does not exist yet**: Create constitution first with `humaninloop:authoring-constitution`
- **CLAUDE.md is intentionally project-specific**: Some projects customize CLAUDE.md beyond constitution scope
- **No mapped sections changed**: If amendment only touches rationale or non-mapped sections, sync may not be needed
- **Draft constitution not yet ratified**: Wait until constitution is approved before syncing

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Full duplication | CLAUDE.md becomes constitution copy, loses agent-focused format | Use selective sync per mapping table |
| Stale sync | CLAUDE.md lags behind constitution, agents use outdated rules | Sync on every constitution version bump |
| Missing version | No version tracking makes drift undetectable | Always include version footer in CLAUDE.md |
| Partial sync | Some sections synced, others forgotten | Use validation checklist before completing |
| Summary drift | Summarization loses enforcement keywords and thresholds | Preserve MUST/SHOULD/MAY and numeric thresholds |

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

**Consequences of Drift:**
- Agents may use deprecated technology choices
- Quality gates may be bypassed due to outdated thresholds
- Principles may be violated because agents are unaware of new rules
- Commit conventions may be inconsistent
- Code review may miss violations that the constitution now prohibits

**Benefits of Synchronization:**
- Agents always operate with current governance rules
- Quality gates are consistently enforced
- New principles are immediately actionable
- Version tracking provides audit trail
- Human and AI guidance remain aligned

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

## Sync Rules

Two primary sync rules govern how content transfers:

### Rule 1: MUST List All With Enforcement

Principles are summarized but preserve enforcement keywords, metrics, and thresholds. Rationale is omitted because CLAUDE.md focuses on actionable rules, not justification.

**What to preserve:**
- RFC 2119 keywords (MUST, SHOULD, MAY, MUST NOT, SHOULD NOT)
- Numeric thresholds (coverage ≥80%, complexity ≤10)
- Enforcement mechanisms (CI blocks, code review required)
- Quality gate commands (`pytest --cov-fail-under=80`)

**What to omit:**
- Rationale sections (why the rule exists)
- Historical context
- Detailed examples (unless critical for understanding)

### Rule 2: MUST Match Exactly

Tables are copied directly with no summarization. This applies to:
- Technology Stack tables
- Quality Gates tables
- Layer Import Rules
- Project Structure (if present)

**Why exact match:** These sections contain precise configuration that agents must follow exactly. Summarization risks losing critical details like specific tool versions or threshold values.

See [references/SECTION-TEMPLATES.md](references/SECTION-TEMPLATES.md) for detailed templates and examples for each sync rule.

## Synchronization Process

The sync process follows six steps:

### Step 1: Read Both Files

Load the constitution and CLAUDE.md. Verify both files exist and are readable. If CLAUDE.md does not exist, create it from the section templates.

### Step 2: Extract Mapped Sections

For each row in the Mandatory Sync Mapping table, locate the corresponding sections in both files. Note any missing sections.

### Step 3: Identify Gaps

Create a gap report documenting drift between files:

```markdown
## Sync Gap Report

**Constitution Version**: 2.1.0
**CLAUDE.md Version**: 2.0.0

### Gaps Found

| Section | Constitution | CLAUDE.md | Gap Type |
|---------|--------------|-----------|----------|
| Quality Gates | coverage ≥80% | coverage ≥70% | Value mismatch |
| Principles | 7 principles | 6 principles | Missing content |
| Version | 2.1.0 | 2.0.0 | Version drift |

### Recommended Actions
1. Update CLAUDE.md Quality Gates: 70% → 80%
2. Add Principle VII to Principles Summary
3. Update version footer to 2.1.0
```

### Step 4: Generate Updates

Prepare specific changes needed. For each gap, draft the exact text change required. Preview changes before applying.

### Step 5: Apply Updates

Update CLAUDE.md with synchronized content. Apply changes section by section, preserving any CLAUDE.md-specific content not in the mapping.

### Step 6: Validate Alignment

Run the Quick Validation checklist. All items must pass before considering sync complete.

See [references/SYNC-PATTERNS.md](references/SYNC-PATTERNS.md) for detailed process steps, validation checklists, and conflict resolution.

## CLAUDE.md Structure

CLAUDE.md includes these sections for proper sync:

### Required Sections

| Section | Source | Sync Rule | Notes |
|---------|--------|-----------|-------|
| Project Overview | Manual | N/A | Brief description of project purpose |
| Principles | Constitution Core Principles | List with enforcement | Omit rationale, keep keywords |
| Technical Stack | Constitution Technology Stack | Exact match | Copy table directly |
| Quality Gates | Constitution Quality Gates | Exact match | Copy table directly |
| Development Workflow | Constitution Governance | List with enforcement | Include commit conventions |
| Version Footer | Constitution version | Exact match | Format: `Version X.Y.Z | Last synced: YYYY-MM-DD` |

### Optional Sections

These sections may exist in CLAUDE.md but are not synchronized from the constitution:

- **Project Structure**: Include if constitution defines directory structure
- **Architecture**: Include if constitution defines layer rules or import restrictions
- **IDE Setup**: Project-specific, not from constitution
- **Local Development**: Project-specific, not from constitution
- **Troubleshooting**: Project-specific, not from constitution

Optional sections are preserved during sync—they are not deleted or modified.

See [references/SECTION-TEMPLATES.md](references/SECTION-TEMPLATES.md) for the complete structure template.

## Sync Triggers

CLAUDE.md synchronization MUST occur when:

1. **Constitution amended**: Any version bump requires sync check
2. **New principle added**: MUST appear in Principles Summary
3. **Principle removed**: MUST be removed from Principles Summary
4. **Quality gate changed**: MUST update Quality Gates table
5. **Tech stack changed**: MUST update Technical Stack table
6. **Governance changed**: MUST update Development Workflow

## Conflict Resolution

When CLAUDE.md contains content that conflicts with the constitution:

### Scenario 1: CLAUDE.md Has Extra Content

CLAUDE.md may contain project-specific sections not in the constitution (e.g., IDE setup, local development tips). These sections are allowed and should be preserved during sync.

**Action:** Keep extra sections. Only update mapped sections.

### Scenario 2: CLAUDE.md Has Different Values

A mapped section in CLAUDE.md contains different values than the constitution (e.g., different coverage threshold).

**Action:** Constitution is authoritative. Overwrite CLAUDE.md with constitution values.

### Scenario 3: Constitution Section Missing

A mapped section exists in CLAUDE.md but not in the constitution.

**Action:** Flag for review. Either add section to constitution or remove from CLAUDE.md.

### Scenario 4: Version Mismatch

CLAUDE.md version does not match constitution version.

**Action:** Always align versions. CLAUDE.md version MUST match constitution version after sync. If constitution is v2.1.0, CLAUDE.md footer must show v2.1.0.

## Quick Validation

Before completing synchronization, verify:

- [ ] All Core Principles listed with enforcement keywords preserved
- [ ] Technology Stack table matches exactly (no omissions)
- [ ] Quality Gates table matches exactly (thresholds identical)
- [ ] Version numbers match (constitution = CLAUDE.md)
- [ ] No contradictions between files
- [ ] Extra CLAUDE.md sections preserved (not deleted)

See [references/SYNC-PATTERNS.md](references/SYNC-PATTERNS.md) for the complete validation checklist.

## Commit Convention

When syncing, use this commit format:

```
docs: sync CLAUDE.md with constitution vX.Y.Z

- Updated Principles Summary (added Principle VII)
- Updated Quality Gates (coverage 70% -> 80%)
- Version aligned to X.Y.Z
```

## Referenced Files

This skill includes detailed reference documentation:

| File | Purpose | When to Use |
|------|---------|-------------|
| [references/SECTION-TEMPLATES.md](references/SECTION-TEMPLATES.md) | Templates for each CLAUDE.md section | When creating or restructuring CLAUDE.md |
| [references/SYNC-PATTERNS.md](references/SYNC-PATTERNS.md) | Detailed sync patterns, validation checklists, edge cases | When resolving complex sync scenarios |

## Related Skills

- **For constitution authoring**: **OPTIONAL:** Use humaninloop:authoring-constitution before syncing (greenfield)
- **For brownfield projects**: **OPTIONAL:** Use humaninloop:brownfield-constitution before syncing
- **For validation**: **OPTIONAL:** Use humaninloop:validation-constitution to verify constitution quality
