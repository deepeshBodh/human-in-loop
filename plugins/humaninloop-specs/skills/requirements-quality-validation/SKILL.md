---
name: requirements-quality-validation
description: Domain taxonomy for evaluating requirements quality. Provides 8 quality dimensions, validation principles ("Unit Tests for English"), anti-patterns, required patterns, and item generation guidelines. Referenced by any agent that generates or validates requirements checklists.
---

# Requirements Quality Validation Skill

## Purpose

Comprehensive domain knowledge for generating and evaluating requirements quality checklists. This skill codifies the "Unit Tests for English" philosophy - treating requirements documents like testable code, where each checklist item validates a specific quality aspect of the written requirements.

## Quick Reference

| Task | Reference |
|------|-----------|
| Understand quality dimensions | [DIMENSIONS.md](DIMENSIONS.md) |
| Apply validation principles | [PRINCIPLES.md](PRINCIPLES.md) |
| Avoid anti-patterns | [ANTI-PATTERNS.md](ANTI-PATTERNS.md) |
| Generate checklist items | [GENERATION.md](GENERATION.md) |

## Core Concept: Unit Tests for English

**Your checklists are UNIT TESTS FOR REQUIREMENTS WRITING.**

You test whether the REQUIREMENTS THEMSELVES are:
- Complete (all necessary requirements documented?)
- Clear (unambiguous and specific?)
- Consistent (aligned without conflicts?)
- Measurable (can be objectively verified?)
- Covering all scenarios (edge cases addressed?)

**You NEVER test whether the implementation works.**

## Quality Dimension Summary

| Dimension | Purpose | Question Pattern |
|-----------|---------|------------------|
| Completeness | All requirements documented? | "Are [requirements] defined for [scenario]?" |
| Clarity | Unambiguous and specific? | "Is [term] quantified with specific criteria?" |
| Consistency | Aligned without conflicts? | "Are requirements consistent between [A] and [B]?" |
| Measurability | Can be objectively verified? | "Can [criterion] be objectively measured?" |
| Coverage | All scenarios addressed? | "Are requirements defined for [alternate flow]?" |
| Edge Case | Boundary conditions defined? | "Are boundary requirements defined for [limit]?" |
| Gap | Missing requirement indicator | "[Gap]" tag in checklist item |
| Ambiguity | Vague language indicator | "[Ambiguity]" tag in checklist item |

## Consolidation Thresholds

| Threshold | Action |
|-----------|--------|
| Items <= 40 | Accept |
| Items > 40 | Apply consolidation rules |
| Traceability >= 80% | Accept |
| Traceability < 80% | Add missing markers |

## When to Load Additional Files

- **Creating a new checklist?** Load [GENERATION.md](GENERATION.md) for item templates
- **Validating existing checklist?** Load [PRINCIPLES.md](PRINCIPLES.md) for validation rules
- **Reviewing for anti-patterns?** Load [ANTI-PATTERNS.md](ANTI-PATTERNS.md) for prohibited patterns
- **Understanding quality dimensions?** Load [DIMENSIONS.md](DIMENSIONS.md) for full taxonomy
