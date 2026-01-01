---
name: spec-writing
description: Reference manual for writing high-quality feature specifications. Provides decision frameworks, quality examples, and procedural guidance. Can be referenced by any agent that works with specifications (spec-writer, clarify, checklist validators).
---

# Spec Writing Skill

## Purpose

Comprehensive guidance for generating consistent, testable specifications from natural language descriptions. This skill serves as a shared reference manual for any agent that writes, validates, or interprets specifications.

## Quick Reference

| Task | Reference |
|------|-----------|
| Determine priority (P1/P2/P3) | [FRAMEWORKS.md](FRAMEWORKS.md) - Priority Assessment |
| Decide when to clarify vs assume | [FRAMEWORKS.md](FRAMEWORKS.md) - Clarification Threshold |
| Choose MUST/SHOULD/MAY | [FRAMEWORKS.md](FRAMEWORKS.md) - Requirement Strength |
| Calibrate quality (good vs bad) | [EXAMPLES.md](EXAMPLES.md) |
| Write spec sections | [PROCEDURES.md](PROCEDURES.md) - Phase 2 |
| Handle ambiguity | [PROCEDURES.md](PROCEDURES.md) - Phase 3 |
| Update workflow artifacts | [PROCEDURES.md](PROCEDURES.md) - Phase 4 |

## Core Principles

1. **Technology-agnostic**: Describe WHAT users need, not HOW to implement
2. **Testable**: Every requirement must have observable, measurable criteria
3. **User-focused**: Success criteria measure user outcomes, not technical metrics
4. **Concise**: No padding—only information that adds value

## Common Anti-Patterns

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| **Technology leakage** | "Store in PostgreSQL" | "Persist user preferences" |
| **Untestable requirements** | "System should be fast" | "Response within 2 seconds" |
| **Over-clarification** | 5+ markers | Max 3; assume lower-impact decisions |
| **Implementation in spec** | "API returns JSON..." | "System provides task data" |
| **Vague acceptance** | "User can do the thing" | Given/When/Then format |
| **Missing edge cases** | Only happy path | Include: limits, failures, concurrency |

## When to Load Additional Files

- **Writing a new spec?** Load [PROCEDURES.md](PROCEDURES.md) for templates
- **Prioritizing stories?** Load [FRAMEWORKS.md](FRAMEWORKS.md) for P1/P2/P3 signals
- **Unsure about quality?** Load [EXAMPLES.md](EXAMPLES.md) for calibration
- **Validating existing spec?** Load [EXAMPLES.md](EXAMPLES.md) to compare
