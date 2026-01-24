---
name: brownfield-constitution
description: This skill should be used when the user asks to "create constitution for existing codebase", "codify existing patterns", or mentions "brownfield", "existing codebase", "essential floor", "emergent ceiling", or "evolution roadmap". Extends authoring-constitution with Essential Floor + Emergent Ceiling approach.
---

# Brownfield Constitution Authoring

## Prerequisites

This skill extends the [authoring-constitution](../authoring-constitution/SKILL.md) skill. Before using brownfield mode:

1. **Understand core principles**: Read `authoring-constitution` for the Three-Part Principle Rule (Enforcement, Testability, Rationale)
2. **Know RFC 2119 keywords**: See [authoring-constitution/RFC-2119-KEYWORDS.md](../authoring-constitution/RFC-2119-KEYWORDS.md)
3. **Understand SYNC IMPACT format**: See [authoring-constitution/SYNC-IMPACT-FORMAT.md](../authoring-constitution/SYNC-IMPACT-FORMAT.md)

Brownfield constitutions follow all rules from `authoring-constitution`, plus additional guidance for existing codebases.

## Purpose

Write project constitutions for **existing codebases** using the **Essential Floor + Emergent Ceiling** approach.

- **Essential Floor**: Four NON-NEGOTIABLE categories every constitution MUST address
- **Emergent Ceiling**: Good patterns from the codebase worth codifying

## Essential Floor (NON-NEGOTIABLE)

Every constitution MUST include principles for these four categories, regardless of codebase state:

| Category | Minimum Requirements | Default Enforcement |
|----------|---------------------|---------------------|
| **Security** | Auth at boundaries, secrets via env/secret managers, input validation, secret scanning in CI | Integration tests, code review, secret scanning tools |
| **Testing** | Automated tests exist, coverage ≥80% (configurable), ratchet rule (coverage MUST NOT decrease) | CI test gate, coverage threshold with warning/blocking levels |
| **Error Handling** | Explicit handling, RFC 7807 Problem Details format, correlation IDs in responses | Schema validation in tests, code review |
| **Observability** | Structured logging, correlation IDs, APM integration, no PII in logs | Config verification, log audit, APM dashboards |

See [ESSENTIAL-FLOOR.md](ESSENTIAL-FLOOR.md) for detailed requirements and example principles for each category.

**Writing Essential Floor Principles:**

- If codebase **has** the capability → Principle codifies existing pattern with enforcement
- If codebase **lacks** the capability → Principle states "MUST implement" with roadmap gap

## Emergent Ceiling (FROM CODEBASE)

Beyond the essential floor, identify **existing good patterns** worth codifying:

1. **Read codebase analysis** - Look for "Strengths to Preserve" section
2. **Identify patterns** - Naming conventions, architecture patterns, error formats
3. **Codify as principles** - With enforcement mechanisms

See [EMERGENT-CEILING-PATTERNS.md](EMERGENT-CEILING-PATTERNS.md) for the pattern library with examples.

**Common Pattern Categories:**

| Pattern Category | What to Look For |
|------------------|------------------|
| **Code Quality** | Documentation requirements, API annotations, deprecation handling |
| **Architecture** | Layer rules, dependency injection, module boundaries |
| **API Design** | Response formats, versioning, pagination |
| **Authorization** | Role-based access, permission checks |
| **Resilience** | Retry policies, circuit breakers, timeouts |
| **Configuration** | Strongly-typed options, feature flags |
| **Error Handling** | Error display guidelines, data resilience |
| **Observability** | Log levels, context requirements, crash reporting |
| **Product Analytics** | Event categories, naming conventions, funnel tracking |
| **Naming Conventions** | File/class/variable naming, directory structure |

## Brownfield Constitution Structure

```markdown
# [Project] Constitution

<!-- SYNC IMPACT REPORT -->

## Core Principles

### Essential Floor Principles
I. Security by Default
II. Testing Discipline
III. Error Handling Standards
IV. Observability Requirements

### Emergent Ceiling Principles
V. [Pattern from codebase]
VI. [Pattern from codebase]
...

## Technology Stack
[From codebase analysis]

## Quality Gates
[From codebase analysis + essential floor requirements]

## Governance
[Standard governance section]

## Evolution Notes

This constitution was created from brownfield analysis.

**Essential Floor Status** (from codebase-analysis.md):
| Category | Status | Gap |
|----------|--------|-----|
| Security | partial | GAP-001 |
| Testing | partial | GAP-002 |
| Error Handling | present | - |
| Observability | absent | GAP-003 |

See `.humaninloop/memory/evolution-roadmap.md` for improvement plan.
```

## Brownfield Quality Checklist

Additional checks for brownfield constitutions (beyond standard checklist):

- [ ] All four essential floor categories have principles
- [ ] Existing good patterns identified and codified
- [ ] Gap references included where codebase lacks capability
- [ ] Technology stack matches codebase analysis
- [ ] Quality gates reflect current + target state
- [ ] Evolution Notes section documents brownfield context

After completing brownfield constitution, run validation using [validation-constitution](../validation-constitution/SKILL.md) skill.

## Related Skills

- [authoring-constitution](../authoring-constitution/SKILL.md) - Core authoring (prerequisite)
- [validation-constitution](../validation-constitution/SKILL.md) - Quality validation (use after authoring)
- [analysis-codebase](../analysis-codebase/SKILL.md) - Analyze existing codebase before writing
