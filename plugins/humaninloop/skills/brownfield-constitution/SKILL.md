---
name: brownfield-constitution
description: Use when user asks to "create constitution for existing codebase", "codify existing patterns", or mentions "brownfield", "existing codebase", "essential floor", "emergent ceiling", or "evolution roadmap". Extends authoring-constitution with Essential Floor + Emergent Ceiling approach.
---

# Brownfield Constitution Authoring

## Overview

Write project constitutions for **existing codebases** using the **Essential Floor + Emergent Ceiling** approach. This skill extends `humaninloop:authoring-constitution` with brownfield-specific guidance that respects existing patterns while establishing governance.

The core insight: existing codebases have implicit conventions worth preserving (Emergent Ceiling) but may lack foundational governance in critical areas (Essential Floor). This skill helps codify both.

## When to Use

Use this skill when:

- Creating a constitution for an **existing codebase** (brownfield project)
- The codebase has existing patterns, conventions, or architecture worth preserving
- You need to establish governance without disrupting working code
- The user mentions "brownfield", "existing codebase", or "legacy project"
- Codifying implicit conventions into explicit, enforceable principles

## When NOT to Use

Do NOT use this skill when:

- Starting a **new project from scratch** → use `humaninloop:authoring-constitution` directly
- **Codebase analysis has not been completed** → run `humaninloop:analysis-codebase` first
- The project is **too small to need formal governance** (single-file scripts, prototypes)
- You only need to **validate an existing constitution** → use `humaninloop:validation-constitution`

## Prerequisites

**REQUIRED:** This skill extends `humaninloop:authoring-constitution`. Before using brownfield mode:

1. **Understand core principles**: Read `humaninloop:authoring-constitution` for the Three-Part Principle Rule (Enforcement, Testability, Rationale)
2. **Know RFC 2119 keywords**: See RFC-2119-KEYWORDS.md in `humaninloop:authoring-constitution`
3. **Understand SYNC IMPACT format**: See SYNC-IMPACT-FORMAT.md in `humaninloop:authoring-constitution`
4. **Run codebase analysis**: Execute `humaninloop:analysis-codebase` to understand existing patterns

Brownfield constitutions follow all rules from `humaninloop:authoring-constitution`, plus additional guidance for existing codebases.

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

See [references/ESSENTIAL-FLOOR.md](references/ESSENTIAL-FLOOR.md) for detailed requirements and example principles for each category.

**Writing Essential Floor Principles:**

- If codebase **has** the capability → Principle codifies existing pattern with enforcement
- If codebase **lacks** the capability → Principle states "MUST implement" with roadmap gap

## Emergent Ceiling (FROM CODEBASE)

Beyond the essential floor, identify **existing good patterns** worth codifying:

1. **Read codebase analysis** - Look for "Strengths to Preserve" section
2. **Identify patterns** - Naming conventions, architecture patterns, error formats
3. **Codify as principles** - With enforcement mechanisms

See [references/EMERGENT-CEILING-PATTERNS.md](references/EMERGENT-CEILING-PATTERNS.md) for the pattern library with examples.

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

After completing brownfield constitution, run validation using `humaninloop:validation-constitution`.

## Common Mistakes

### Mistake 1: Skipping Essential Floor Categories

**Problem**: Assuming the codebase "doesn't need" security or observability principles because it "seems simple" or "works fine."

**Why it's wrong**: Essential floor categories exist because these are areas where missing governance causes the most damage. A working codebase without security principles will eventually have a security incident.

**Fix**: Always include all four essential floor categories. If the codebase lacks capability in an area, write the principle with "MUST implement" and reference a roadmap gap.

### Mistake 2: Codifying Bad Patterns from the Codebase

**Problem**: Treating all existing patterns as worth preserving. The emergent ceiling captures whatever is in the codebase, including anti-patterns.

**Why it's wrong**: Some patterns in existing codebases are historical accidents, workarounds, or technical debt. Codifying them as principles locks in bad practices.

**Fix**: Only codify patterns that are **intentionally good**. Ask: "Would I recommend this pattern for a new project?" If no, it's technical debt, not an emergent ceiling pattern.

### Mistake 3: Skipping Codebase Analysis

**Problem**: Writing the brownfield constitution without first running `humaninloop:analysis-codebase`.

**Why it's wrong**: Without analysis, you're guessing about existing patterns. You'll miss good patterns worth preserving and may not accurately assess essential floor status.

**Fix**: Always run codebase analysis first. The analysis output has "Strengths to Preserve" (emergent ceiling input) and gap identification (essential floor status).

### Mistake 4: Writing Aspirational Instead of Enforceable Principles

**Problem**: Writing principles like "Code SHOULD be clean" or "Security SHOULD be considered" without concrete enforcement.

**Why it's wrong**: These principles are unenforceable and untestable. They provide no governance value and will be ignored.

**Fix**: Every principle needs the Three-Part Rule from `humaninloop:authoring-constitution`: specific behavior, enforcement mechanism, and rationale. "Security SHOULD be considered" becomes "Authentication MUST use JWT with rotation, enforced by middleware check, because centralized auth prevents bypass."

### Mistake 5: Ignoring Evolution Notes

**Problem**: Creating the constitution without documenting the brownfield context and gap status.

**Why it's wrong**: Future maintainers won't know which principles reflect existing capability vs. aspirational targets. They can't prioritize improvements.

**Fix**: Always include the Evolution Notes section with essential floor status table and link to evolution roadmap. This makes gaps visible and actionable.

## Related Skills

- `humaninloop:authoring-constitution` - Core authoring (prerequisite)
- `humaninloop:validation-constitution` - Quality validation (use after authoring)
- `humaninloop:analysis-codebase` - Analyze existing codebase before writing
- `humaninloop:authoring-roadmap` - Create evolution roadmap for identified gaps
