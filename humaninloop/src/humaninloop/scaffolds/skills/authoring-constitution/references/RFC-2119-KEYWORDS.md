# RFC 2119 Keywords for Constitution Authoring

This document provides detailed guidance on using RFC 2119 keywords in constitution principles.

## Overview

RFC 2119 defines keywords to indicate requirement levels in specifications. Using these precisely ensures principles are unambiguous and enforceable.

## Keyword Definitions

### MUST / REQUIRED / SHALL

**Meaning**: Absolute requirement. No exceptions permitted.

**When to use**:
- Non-negotiable constraints
- Security requirements
- Compliance mandates
- Core architectural rules

**Examples**:
```markdown
- Tests MUST pass before code is merged
- Secrets MUST NOT be committed to version control
- All endpoints MUST validate authentication
- Code MUST pass static analysis with zero errors
```

**Enforcement implication**: Violation blocks deployment/merge automatically.

---

### MUST NOT / SHALL NOT

**Meaning**: Absolute prohibition. Never permitted.

**When to use**:
- Security prohibitions
- Dangerous practices
- Architectural violations

**Examples**:
```markdown
- Production credentials MUST NOT appear in code
- Domain layer MUST NOT import from adapters
- Magic numbers MUST NOT be used without named constants
- Debug logging MUST NOT include PII
```

**Enforcement implication**: Violation blocks deployment/merge automatically.

---

### SHOULD / RECOMMENDED

**Meaning**: Strong recommendation. Valid exceptions may exist but must be justified.

**When to use**:
- Best practices with legitimate exceptions
- Guidelines that improve quality
- Recommendations that may conflict with pragmatic constraints

**Examples**:
```markdown
- Functions SHOULD be under 40 lines
- Classes SHOULD follow Single Responsibility Principle
- Tests SHOULD be independent and isolated
- Error messages SHOULD be user-friendly
```

**Enforcement implication**: Deviation requires documented justification in code review.

---

### SHOULD NOT / NOT RECOMMENDED

**Meaning**: Discouraged practice. Valid exceptions may exist but must be justified.

**When to use**:
- Practices that are generally bad but sometimes necessary
- Patterns to avoid unless there's a good reason

**Examples**:
```markdown
- Functions SHOULD NOT exceed 10 cyclomatic complexity
- Comments SHOULD NOT describe what code does (describe why)
- Tests SHOULD NOT depend on external services
- Mutable global state SHOULD NOT be used
```

**Enforcement implication**: Deviation requires documented justification in code review.

---

### MAY / OPTIONAL

**Meaning**: Truly optional. Implementation choice with no preference.

**When to use**:
- Features teams can adopt at their discretion
- Stylistic choices with no quality impact
- Extensions beyond core requirements

**Examples**:
```markdown
- Teams MAY adopt additional linting rules beyond the minimum
- Functions MAY use early returns for guard clauses
- Tests MAY use property-based testing for complex logic
- Documentation MAY include diagrams for complex flows
```

**Enforcement implication**: No enforcement. Pure team discretion.

## Decision Matrix

| Need | Keyword | Enforcement |
|------|---------|-------------|
| Zero tolerance for violation | MUST / MUST NOT | CI blocks merge |
| Strong preference, exceptions documented | SHOULD / SHOULD NOT | Code review gate |
| Team discretion, no preference | MAY | None |

## Common Mistakes

### Mistake 1: Using SHOULD when you mean MUST

**Wrong**: "Code SHOULD pass tests before merge"
**Right**: "Code MUST pass tests before merge"

If you would reject a PR for violating the rule, it's a MUST.

### Mistake 2: Using MUST for preferences

**Wrong**: "Functions MUST be under 40 lines"
**Right**: "Functions SHOULD be under 40 lines" (with exception for complex algorithms)

If valid exceptions exist, use SHOULD.

### Mistake 3: Omitting keywords entirely

**Wrong**: "Code will be formatted before commit"
**Right**: "Code MUST be formatted before commit"

Always use explicit keywords for enforceable rules.

### Mistake 4: Combining keywords incorrectly

**Wrong**: "Code SHOULD MUST be tested"
**Right**: "Code MUST be tested"

Use one keyword per requirement.

## Keyword Frequency Guidelines

A healthy constitution typically has:

| Keyword | Typical Count | Notes |
|---------|---------------|-------|
| MUST | 10-20 | Core constraints that define the project |
| MUST NOT | 5-10 | Critical prohibitions (security, architecture) |
| SHOULD | 5-15 | Best practices with documented exceptions |
| SHOULD NOT | 3-8 | Anti-patterns to avoid |
| MAY | 2-5 | Optional extensions |

**Warning signs**:
- All MUST and no SHOULD = too rigid, teams will ignore it
- All SHOULD and no MUST = no real constraints, unenforceable
- Too many MAY = not a constitution, just suggestions

## Enforcement Mapping

| Keyword | CI Enforcement | Code Review | Exception Process |
|---------|---------------|-------------|-------------------|
| MUST | Block merge | Verify compliance | Exception Registry required |
| MUST NOT | Block merge | Verify compliance | Exception Registry required |
| SHOULD | Warning only | Verify or document exception | Comment in code sufficient |
| SHOULD NOT | Warning only | Verify or document exception | Comment in code sufficient |
| MAY | None | Optional discussion | Not needed |

## Examples in Context

### Good Principle with Mixed Keywords

```markdown
### III. Code Quality

All code MUST meet quality standards:

- Static analysis MUST pass with zero warnings
- Code formatting MUST comply with configured rules
- Functions SHOULD be under 40 lines (exceptions documented)
- Cyclomatic complexity SHOULD NOT exceed 10 per function
- Teams MAY adopt stricter rules for critical modules

**Enforcement**:
- `ruff check .` MUST exit with code 0 (CI automated)
- Functions over 40 lines SHOULD have comment justifying length
```

### Bad Principle (Keyword Misuse)

```markdown
### III. Code Quality

Code should be clean and well-formatted:

- Analysis will pass without errors
- Functions will be short
- Code may be formatted consistently
```

**Problems**:
- "should be clean" is vague
- "will pass" is not an RFC 2119 keyword
- "may be formatted" makes formatting optional when it should be MUST
