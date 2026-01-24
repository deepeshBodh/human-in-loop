---
name: syncing-claude-md
description: This skill should be used when the user asks to "sync CLAUDE.md", "update agent instructions", "propagate constitution changes", or mentions "CLAUDE.md sync", "agent instructions", or "constitution alignment". Ensures CLAUDE.md mirrors constitution sections per explicit mapping rules.
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

## Sync Rules

Two primary sync rules govern how content transfers:

**MUST list all with enforcement**: Principles are summarized but preserve enforcement keywords, metrics, and thresholds. Rationale is omitted.

**MUST match exactly**: Tables are copied directly with no summarization.

See [SECTION-TEMPLATES.md](SECTION-TEMPLATES.md) for detailed templates and examples for each sync rule.

## Synchronization Process

The sync process follows six steps:

1. **Read Both Files**: Load constitution and CLAUDE.md
2. **Extract Mapped Sections**: Locate corresponding sections per mapping
3. **Identify Gaps**: Create gap report showing drift
4. **Generate Updates**: Prepare specific changes needed
5. **Apply Updates**: Update CLAUDE.md with synchronized content
6. **Validate Alignment**: Verify all mapped sections match

See [SYNC-PATTERNS.md](SYNC-PATTERNS.md) for detailed process steps, validation checklists, and conflict resolution.

## CLAUDE.md Structure

CLAUDE.md should include these sections for proper sync:

- **Project Overview**: Brief description
- **Principles**: Synchronized from constitution Core Principles
- **Technical Stack**: Exact match from constitution Technology Stack
- **Quality Gates**: Exact match from constitution Quality Gates
- **Development Workflow**: From constitution Governance
- **Project Structure**: If present in constitution
- **Version Footer**: Version and last synced date

See [SECTION-TEMPLATES.md](SECTION-TEMPLATES.md) for the complete structure template.

## Sync Triggers

CLAUDE.md synchronization MUST occur when:

1. **Constitution amended**: Any version bump requires sync check
2. **New principle added**: MUST appear in Principles Summary
3. **Principle removed**: MUST be removed from Principles Summary
4. **Quality gate changed**: MUST update Quality Gates table
5. **Tech stack changed**: MUST update Technical Stack table
6. **Governance changed**: MUST update Development Workflow

## Quick Validation

Before completing synchronization, verify:

- [ ] All Core Principles listed with enforcement
- [ ] Technology Stack table matches exactly
- [ ] Quality Gates table matches exactly
- [ ] Version numbers match (constitution = CLAUDE.md)
- [ ] No contradictions between files

See [SYNC-PATTERNS.md](SYNC-PATTERNS.md) for the complete validation checklist.

## Commit Convention

When syncing, use this commit format:

```
docs: sync CLAUDE.md with constitution vX.Y.Z

- Updated Principles Summary (added Principle VII)
- Updated Quality Gates (coverage 70% -> 80%)
- Version aligned to X.Y.Z
```

## Anti-Patterns

| Anti-Pattern | Problem |
|--------------|---------|
| Full duplication | CLAUDE.md becomes constitution copy |
| Stale sync | CLAUDE.md lags behind constitution |
| Missing version | No version tracking in CLAUDE.md |
| Partial sync | Some sections synced, others not |
| Summary drift | Summarization loses enforcement |

See [SYNC-PATTERNS.md](SYNC-PATTERNS.md) for detailed anti-patterns and fixes.
