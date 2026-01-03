---
name: authoring-constitution
description: Write enforceable, testable constitution content with proper principle structure, governance sections, and quality gates. Use when creating constitutions, writing principles, defining governance, or when you see "constitution", "governance", "principles", "enforcement", "quality gates", or "amendment process".
---

# Authoring Constitution

## Purpose

Write project constitutions that teams actually follow. Every principle must be enforceable, testable, and justified. Vague aspirations are rejected in favor of actionable constraints with measurable criteria.

## The Three-Part Principle Rule

Every principle MUST have three components. A principle without all three is incomplete and should not be accepted.

### 1. Enforcement

How compliance is verified. Without enforcement, a principle is a suggestion.

```markdown
**Enforcement**:
- CI runs `ruff check .` and blocks merge on violations
- Code review MUST verify test files accompany new functionality
- Quarterly audit checks exception registry for staleness
```

**Enforcement Types**:

| Type | Examples | Strength |
|------|----------|----------|
| **CI Automated** | Linting, tests, coverage gates | Strongest—no human judgment needed |
| **Code Review** | Architecture compliance, security review | Strong—explicit checklist item |
| **Tooling** | Pre-commit hooks, IDE plugins | Medium—can be bypassed |
| **Audit** | Quarterly review, compliance check | Weaker—periodic, not continuous |

### 2. Testability

What pass/fail looks like. If you can't test it, it's not a principle—it's an aspiration.

```markdown
**Testability**:
- Pass: `flutter analyze` exits with code 0
- Pass: All functions have ≤10 cyclomatic complexity
- Fail: Any file exceeds 400 lines without documented exception
```

**Testability Requirements**:
- Binary outcome (pass or fail)
- Measurable threshold where applicable
- Observable without subjective judgment
- Reproducible by any team member

### 3. Rationale

Why this constraint exists. Future maintainers need this to evaluate if the rule is still relevant.

```markdown
**Rationale**: Tests written after implementation tend to validate what was built rather than what was intended. Test-first ensures requirements drive implementation, catches defects early, and produces inherently testable, modular code.
```

**Rationale Requirements**:
- Explains the failure mode this prevents
- Describes the success this enables
- Provides context for future evaluation
- Justifies the enforcement overhead

## Principle Writing Format

```markdown
### I. [Principle Name]

[Declarative statement of the constraint using RFC 2119 keywords]

- [Specific rule 1]
- [Specific rule 2]
- [Specific rule 3]

**Enforcement**:
- [How compliance is verified]
- [Specific commands or processes]

**Testability**:
- [Pass/fail criteria]
- [Measurable thresholds]

**Rationale**: [Why this constraint exists—what failure it prevents, what success it enables]
```

## RFC 2119 Keywords

Use precise language for requirements:

| Keyword | Meaning | Example |
|---------|---------|---------|
| **MUST** | Absolute requirement; no exceptions | "Tests MUST pass before merge" |
| **MUST NOT** | Absolute prohibition | "Secrets MUST NOT be committed" |
| **SHOULD** | Recommended; valid exceptions exist | "Functions SHOULD be under 40 lines" |
| **SHOULD NOT** | Discouraged; valid exceptions exist | "Magic numbers SHOULD NOT appear" |
| **MAY** | Optional; implementation choice | "Teams MAY adopt additional linting rules" |

See [RFC-2119-KEYWORDS.md](RFC-2119-KEYWORDS.md) for detailed usage.

## Mandatory Constitution Sections

Every constitution MUST include these sections:

### 1. SYNC IMPACT REPORT (Header)

Track changes as HTML comment at file top:

```html
<!--
SYNC IMPACT REPORT
==================
Version change: X.Y.Z → A.B.C (MAJOR|MINOR|PATCH: Brief rationale)

Rationale for bump:
- [Why this version increment]

Modified Sections:
- [Section]: [What changed]

Added Sections:
- [New section name]

Removed Sections:
- [Removed section name] (or "None")

Templates Alignment:
- ✅ [template]: [status]
- ⚠️ [template]: [pending action]

Follow-up TODOs:
- [Any deferred items]

Previous Reports:
- X.Y.Z (YYYY-MM-DD): [Summary]
-->
```

See [SYNC-IMPACT-FORMAT.md](SYNC-IMPACT-FORMAT.md) for complete format.

### 2. Core Principles

Numbered principles (I, II, III...) with Enforcement/Testability/Rationale.

**Naming Conventions**:
- Use Roman numerals (I, II, III, IV, V...)
- Name captures the constraint domain
- Mark non-negotiable principles explicitly: `(NON-NEGOTIABLE)`

**Common Principle Categories**:

| Category | Examples |
|----------|----------|
| **Development Process** | Test-First, Code Review, Documentation |
| **Code Quality** | Linting, Complexity Limits, Coverage |
| **Architecture** | Layer Rules, Dependency Flow, Module Boundaries |
| **Security** | Auth, Secrets, Input Validation |
| **Operations** | Observability, Error Handling, Performance |
| **Governance** | Versioning, Dependencies, Exceptions |

### 3. Technology Stack

Document mandated technology choices with rationale:

```markdown
## Technology Stack

| Category | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12 | Type hints, performance, ecosystem |
| Framework | FastAPI | Async-first, Pydantic integration |
| Testing | pytest | Fixtures, parametrization, plugins |
| Linting | ruff | Fast, replaces multiple tools |
```

### 4. Quality Gates

Define automated checks that block merge:

```markdown
## Quality Gates

| Gate | Requirement | Measurement | Enforcement |
|------|-------------|-------------|-------------|
| Static Analysis | Zero errors | `ruff check .` | CI automated |
| Type Checking | Zero errors | `pyright` | CI automated |
| Test Suite | All pass | `pytest` | CI automated |
| Coverage | ≥80% | `pytest --cov-fail-under=80` | CI automated |
| Security | No vulnerabilities | `pip-audit` | CI automated |
```

### 5. Governance

Define how the constitution itself evolves:

```markdown
## Governance

### Amendment Process
1. Propose change via PR to constitution file
2. Document rationale for change
3. Review impact on existing code
4. Obtain team consensus
5. Update version per semantic versioning

### Version Policy
- **MAJOR**: Principle removal or incompatible redefinition
- **MINOR**: New principle or significant expansion
- **PATCH**: Clarification or wording improvement

### Exception Registry
Approved exceptions MUST be recorded in `docs/constitution-exceptions.md` with:
- Exception ID, Principle, Scope, Justification
- Approved By, Date, Expiry, Tracking Issue

**Version**: X.Y.Z | **Ratified**: YYYY-MM-DD | **Last Amended**: YYYY-MM-DD
```

### 6. CLAUDE.md Sync Mandate

Define synchronization requirements:

```markdown
## CLAUDE.md Synchronization

The `CLAUDE.md` file MUST remain synchronized with this constitution.

**Mandatory Sync Mapping**:

| Constitution Section | CLAUDE.md Section | Sync Rule |
|---------------------|-------------------|-----------|
| Core Principles | Principles Summary | MUST list all with enforcement |
| Technology Stack | Technical Stack | MUST match exactly |
| Quality Gates | Quality Gates | MUST match exactly |
| Governance | Development Workflow | MUST match versioning rules |
```

See [syncing-claude-md skill](../syncing-claude-md/SKILL.md) for implementation.

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

Before finalizing a constitution, verify:

**Principle Quality**:
- [ ] Every principle has Enforcement section
- [ ] Every principle has Testability section
- [ ] Every principle has Rationale section
- [ ] All MUST statements have enforcement mechanisms
- [ ] All quantifiable criteria have specific thresholds
- [ ] No vague language without measurable criteria

**Structure Quality**:
- [ ] SYNC IMPACT REPORT present as HTML comment
- [ ] Core Principles numbered with Roman numerals
- [ ] Technology Stack table complete with rationale
- [ ] Quality Gates table with measurement commands
- [ ] Governance section with amendment process
- [ ] CLAUDE.md Sync Mandate with mapping table
- [ ] Version footer with dates in ISO format

**Governance Quality**:
- [ ] Version follows semantic versioning
- [ ] Amendment process is actionable
- [ ] Exception registry format defined
- [ ] Compliance review expectations set

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Vague principle** | "Code should be maintainable" | Define specific metrics (complexity, length) |
| **Missing enforcement** | Principle has no verification method | Add CI check, code review rule, or audit |
| **Untestable rule** | "Architecture should be clean" | Define layer rules with import constraints |
| **Cargo-cult rule** | Rule copied without understanding | Add rationale explaining the "why" |
| **Over-engineering** | 50 principles for a 3-person team | Start with 5-7 core principles |
| **No escape hatch** | No exception process | Define exception registry |
