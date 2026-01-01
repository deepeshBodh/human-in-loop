---
name: spec-clarify
description: Reference manual for processing clarification answers and updating specifications. Provides workflows for answer application, gap resolution, and context synchronization. Can be referenced by any agent handling specification refinement.
---

# Spec Clarify Skill

## Purpose

Comprehensive guidance for processing user answers to clarification questions and updating feature specifications accordingly. This skill covers the complete clarification workflow from answer application through context synchronization.

## Quick Reference

| Task | Reference |
|------|-----------|
| Process user answers | [PROCEDURES.md](PROCEDURES.md) - Phase 2 |
| Handle gap-derived clarifications | [PATTERNS.md](PATTERNS.md) - Gap-Derived Handling |
| Apply cascading updates | [PROCEDURES.md](PROCEDURES.md) - Phase 3 |
| Validate quality | [PROCEDURES.md](PROCEDURES.md) - Phase 5 |
| Update context files | [PROCEDURES.md](PROCEDURES.md) - Phase 6 |
| Handle round 3 (final) | [PATTERNS.md](PATTERNS.md) - Round 3 Special Handling |
| See application examples | [PATTERNS.md](PATTERNS.md) - Application Patterns |

## Core Workflow Overview

```
Phase 1: Context Loading
    ↓
Phase 2: Answer Application (replace [NEEDS CLARIFICATION] markers)
    ↓
Phase 2b: Gap-Derived Clarifications (from Priority Loop)
    ↓
Phase 3: Cascading Updates (related sections)
    ↓
Phase 4: Issue Scanning (new ambiguities?)
    ↓
Phase 5: Quality Validation
    ↓
Phase 6: Context Updates (specify-context.md, index.md)
    ↓
Phase 7: Checklist Updates
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Clarification Marker** | `[NEEDS CLARIFICATION: Question? Options: A, B, C]` in specs |
| **Answer ID** | Format `C{n}` for spec clarifications, `C{iter}.{n}` for gap-derived |
| **Gap-Derived** | Clarifications from Priority Loop, reference CHK and FR sources |
| **Round 3 Finality** | Final round—make assumptions, never add new markers |

## Related Skills

- **spec-writing**: Reference for quality validation criteria and requirement formats
- **clarification-patterns**: Gap classification, grouping, and answer application patterns
