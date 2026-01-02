---
name: clarification-patterns
description: Spec-specific clarification handling patterns. Extends prioritization-patterns from humaninloop-core for gap grouping and staleness detection. Adds specification clarification generation, answer application, and Priority Loop management.
---

# Clarification Patterns Skill

## Purpose

Specification-specific guidance for handling the clarification lifecycle: generating clarification questions from gaps, applying user answers to specs, and managing the Priority Loop. This skill **extends** prioritization-patterns from humaninloop-core.

## Core Skill Composition

> **ADR-006 Compliance**: This skill extends core skills rather than duplicating them.

| Core Skill | What We Use | Spec-Specific Extension |
|------------|-------------|------------------------|
| prioritization-patterns/GROUPING.md | Grouping algorithm, domain extraction | FR/CHK traceability context |
| prioritization-patterns/STALENESS.md | Detection algorithm, thresholds | [KNOWN GAP] marker handling |
| prioritization-patterns/SEVERITY.md | Critical/Important/Minor classification | User story priority mapping |

When the agent declares `skills: clarification-patterns, prioritization-patterns`, both skill sets are available.

## Quick Reference

| Task | Reference |
|------|-----------|
| Group gaps into clarifications | [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) - Grouping Rules |
| Generate clarification questions | [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) - Question Generation |
| Apply user answers to spec | [APPLICATION.md](APPLICATION.md) - Basic Replacement |
| Handle gap-derived clarifications | [APPLICATION.md](APPLICATION.md) - Gap-Derived Handling |
| Handle round 3 (final) | [APPLICATION.md](APPLICATION.md) - Round 3 Special Handling |
| Workflow patterns | [WORKFLOW-PATTERNS.md](WORKFLOW-PATTERNS.md) |

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

## Skill Composition Note

> **Architecture**: Skills are atomic—they do not depend on other skills directly. When an agent needs knowledge from multiple skills, it declares them in its `skills:` field (e.g., `skills: clarification-patterns, spec-writing`). The agent then has access to all declared skills during execution.
