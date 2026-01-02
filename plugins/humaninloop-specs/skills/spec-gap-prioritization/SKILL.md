---
name: spec-gap-prioritization
description: Specification-specific gap prioritization and grouping rules. Extends prioritization-patterns from humaninloop-core with spec-domain filtering (Critical/Important only), FR-based grouping, stale detection thresholds, and clarification ID formats. Used by gap-classifier and validators during specification Priority Loop.
---

# Spec Gap Prioritization Skill

## Purpose

Domain knowledge for prioritizing, filtering, and grouping specification gaps into focused clarification questions. This skill extends the generic prioritization-patterns from humaninloop-core with specification-specific rules for the Priority Loop workflow.

## Core Skill Composition

> **Skill Extension Pattern**: This skill extends core skills rather than duplicating them.

| Core Skill | What We Use | Spec-Specific Extension |
|------------|-------------|------------------------|
| prioritization-patterns/GROUPING.md | Grouping algorithm | FR/CHK traceability context |
| prioritization-patterns/STALENESS.md | Detection algorithm | [KNOWN GAP] marker handling |
| prioritization-patterns/SEVERITY.md | Critical/Important/Minor | User story priority mapping |

When the agent declares `skills: spec-gap-prioritization, prioritization-patterns`, both skill sets are available.

## Quick Reference

| Task | Reference |
|------|-----------|
| Filter gaps by priority | [FILTERING.md](FILTERING.md) |
| Group related gaps | [GROUPING.md](GROUPING.md) |
| Detect stale gaps | [STALENESS.md](STALENESS.md) |
| Generate clarification questions | [QUESTIONS.md](QUESTIONS.md) |

## Key Constraints

- **Maximum 3 clarifications per iteration** - Prevents user fatigue
- **Only process Critical + Important** - Minor gaps are deferred
- **Must group related gaps** - Reduces redundant questions
- **Stale threshold: 3 iterations** - Escalate after 3 attempts
- **Must update traceability** - Maintain audit trail

## Gap Priority Levels

| Priority | Definition | Action |
|----------|------------|--------|
| Critical | Blocks understanding of core functionality | Must resolve immediately |
| Important | Affects significant functionality | Must resolve before completion |
| Minor | Polish, edge cases, nice-to-have | Defer to later iterations |

## Clarification ID Formats

| Format | Source | Example |
|--------|--------|---------|
| `Q-S{n}` | Spec writing phase (initial) | Q-S1, Q-S2, Q-S3 |
| `C{iter}.{n}` | Gap classification (Priority Loop) | C1.1, C1.2, C2.1 |

## Workflow Position

This skill supports gap handling across two workflow phases:

1. **Initial Specification (Phase A5)**
   - Gap classifier receives validation gaps
   - Filters to Critical + Important
   - Groups into max 3 clarifications

2. **Priority Loop (Phase B)**
   - Re-validates after answers applied
   - Detects stale gaps (3+ iterations)
   - Generates new clarifications for remaining gaps

## State Update Patterns

### Gap Priority Queue Entry

```markdown
| Priority | Gap ID | CHK Source | FR Reference | Question | Status | Stale Count |
|----------|--------|------------|--------------|----------|--------|-------------|
| Critical | G-001 | CHK015 | FR-003 | Auth failure handling | clarifying | 0 |
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Gap identified, not yet addressed |
| `clarifying` | Question presented to user |
| `resolved` | User answer applied |
| `deferred` | Minor gap, deferred to later |
| `escalated` | Stale gap, user decision required |

## When to Load Additional Files

- **Filtering gaps?** Load [FILTERING.md](FILTERING.md)
- **Grouping for questions?** Load [GROUPING.md](GROUPING.md)
- **Checking staleness?** Load [STALENESS.md](STALENESS.md)
- **Generating questions?** Load [QUESTIONS.md](QUESTIONS.md)
