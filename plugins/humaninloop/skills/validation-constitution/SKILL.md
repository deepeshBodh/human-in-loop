---
name: validation-constitution
description: This skill should be used when the user asks to "review constitution", "validate principles", "check quality", or mentions "constitution review", "quality check", "version bump", "anti-patterns", or "constitution audit". Provides checklists, anti-pattern detection, and version bump guidance.
---

# Validating Constitution

## Purpose

Verify constitution quality before finalization. This skill provides checklists, anti-pattern detection, and version bump guidance. Use after authoring with `authoring-constitution` or `brownfield-constitution` skills.

## Quantification Requirements

Vague language MUST be replaced with measurable criteria:

| Vague | Quantified |
|-------|------------|
| "Code should be clean" | "Zero lint warnings from configured rules" |
| "Functions should be short" | "Functions MUST NOT exceed 40 lines" |
| "Tests should cover the code" | "Coverage MUST be ≥80% for new code" |
| "Response should be fast" | "API MUST respond in <200ms p95" |
| "Secure by default" | "All inputs MUST be validated; auth required on all endpoints" |

## Version Bump Rules

| Bump | Trigger | Example |
|------|---------|---------|
| **MAJOR** | Principle removed | Removing "Test-First" principle |
| **MAJOR** | Incompatible redefinition | Changing coverage from 80% to 50% |
| **MINOR** | New principle added | Adding "Observability" principle |
| **MINOR** | Significant expansion | Adding 5 new rules to existing principle |
| **PATCH** | Clarification | Rewording for clarity, typo fixes |
| **PATCH** | Non-semantic change | Formatting, comment updates |

## Quality Checklist

Before finalizing a constitution, verify all items in [QUALITY-CHECKLIST.md](QUALITY-CHECKLIST.md).

**Summary of checks:**
- Principle Quality (Enforcement, Testability, Rationale present)
- Structure Quality (all mandatory sections)
- No Placeholders Rule (actual tools, not `[PLACEHOLDER]`)
- Governance Quality (versioning, amendment process)

## Anti-Patterns to Avoid

See [ANTI-PATTERNS.md](ANTI-PATTERNS.md) for common mistakes and fixes.

**Quick reference:**

| Anti-Pattern | Fix |
|--------------|-----|
| Vague principle | Define specific metrics |
| Missing enforcement | Add CI check, code review rule, or audit |
| Untestable rule | Define layer rules with import constraints |
| Cargo-cult rule | Add rationale explaining the "why" |
| Over-engineering | Start with 5-7 core principles |
| No escape hatch | Define exception registry |
| Placeholder syndrome | Use detected tools or industry defaults |
| Generic thresholds | Specify numeric values |

## Workflow

1. **After authoring**: Run through the Quality Checklist
2. **Review each principle**: Verify three-part rule (Enforcement/Testability/Rationale)
3. **Check for anti-patterns**: Compare against common mistakes
4. **Determine version bump**: Use Version Bump Rules table
5. **Final sign-off**: All checklist items pass

## Related Skills

- [authoring-constitution](../authoring-constitution/SKILL.md) - Core authoring for greenfield
- [brownfield-constitution](../brownfield-constitution/SKILL.md) - Authoring for existing codebases
