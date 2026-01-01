---
name: clarification-patterns
description: Shared knowledge for gap classification and clarification handling. Provides patterns for grouping gaps into questions, applying user answers, and managing the Priority Loop. Used by spec-clarify agent for both gap classification mode and answer application mode.
---

# Clarification Patterns Skill

## Purpose

Comprehensive guidance for handling the clarification lifecycle: from identifying gaps, grouping them into focused questions, to applying user answers and maintaining traceability. This skill serves as a shared reference for any agent working with gaps and clarifications.

## Quick Reference

| Task | Reference |
|------|-----------|
| Group gaps into clarifications | [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) - Grouping Rules |
| Generate clarification questions | [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) - Question Generation |
| Apply user answers to spec | [APPLICATION.md](APPLICATION.md) - Basic Replacement |
| Handle gap-derived clarifications | [APPLICATION.md](APPLICATION.md) - Gap-Derived Handling |
| Handle round 3 (final) | [APPLICATION.md](APPLICATION.md) - Round 3 Special Handling |
| Full workflow procedures | [PROCEDURES.md](PROCEDURES.md) |

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Gap** | Quality issue identified by checklist validation (CHK → FR) |
| **Clarification** | Question derived from gap(s) with ID format `C{iter}.{n}` |
| **Priority** | `Critical` and `Important` must resolve; `Minor` can defer |
| **Grouping** | Combining related gaps into single clarification to reduce user fatigue |
| **Stale Gap** | Gap unresolved after 3 iterations - requires escalation |

## Clarification ID Formats

| Format | Source | Example |
|--------|--------|---------|
| `Q-S{n}` | Spec writing phase | Q-S1, Q-S2 |
| `C{iter}.{n}` | Gap classification (Priority Loop) | C1.1, C2.3 |

## Key Constraints

- Maximum 3 clarifications per iteration
- Only process Critical + Important gaps (Minor deferred)
- Must group related gaps to reduce user fatigue
- Must update traceability for audit trail
- Must detect stale gaps after 3 iterations

## Workflow Position

This skill supports the spec-clarify agent in dual-mode operation:

1. **Gap Classification Mode** (before user interaction)
   - Groups gaps from checklist validation
   - Generates clarification questions
   - Updates Gap Priority Queue with `clarifying` status

2. **Answer Application Mode** (after user interaction)
   - Applies user answers to spec
   - Updates Gap Priority Queue with `resolved` status
   - Validates spec quality

## Related Skills

- **spec-writing**: Reference for quality validation criteria and requirement formats
