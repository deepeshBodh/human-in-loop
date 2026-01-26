---
name: authoring-constitution
description: Use when creating or updating project constitution, when user asks to "write principles", "define governance", or mentions "constitution", "governance", "principles", "enforcement", or "amendment process". Core skill for greenfield projects.
---

# Authoring Constitution

## Overview

Write project constitutions that teams actually follow. Every principle must be enforceable, testable, and justified. Vague aspirations are rejected in favor of actionable constraints with measurable criteria.

## When to Use

- User asks to "create a constitution" or "define governance"
- Starting a new greenfield project that needs governance
- User wants to "write principles" or "define constraints"
- Establishing quality gates and enforcement mechanisms
- Defining amendment processes and version policies

## When NOT to Use

- **Brownfield projects with existing code**: **REQUIRED** alternative - Use `humaninloop:brownfield-constitution` instead, which provides Essential Floor + Emergent Ceiling approach
- **Reviewing an existing constitution**: **OPTIONAL** - Use `humaninloop:validation-constitution` for quality checks
- **Syncing CLAUDE.md after constitution changes**: **OPTIONAL** - Use `humaninloop:syncing-claude-md` for synchronization

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Vague principles | "Code should be clean" has no enforcement | Add specific, measurable criteria: "Functions MUST be ≤40 lines" |
| Missing enforcement | Principles without verification become suggestions | Every principle needs CI automation, code review checklist, or audit process |
| Untestable criteria | "Good architecture" can't be verified | Define binary pass/fail: "No domain imports from infrastructure layer" |
| No rationale | Future maintainers don't know why rules exist | Explain the failure mode prevented and success enabled |
| Skipping SYNC IMPACT | Constitution changes without audit trail | Always update the SYNC IMPACT REPORT header with version changes |
| CLAUDE.md drift | AI assistants operate with outdated guidance | Include CLAUDE.md Sync Mandate section; update both files together |

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

What pass/fail looks like. A principle without testable criteria is merely an aspiration.

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

See [references/RFC-2119-KEYWORDS.md](references/RFC-2119-KEYWORDS.md) for detailed usage.

## Mandatory Constitution Sections

Every constitution MUST include these sections:

### 1. SYNC IMPACT REPORT (Header)

Track changes as HTML comment at file top. This provides an audit trail of constitution evolution.

```html
<!--
SYNC IMPACT REPORT
==================
Version change: X.Y.Z → A.B.C (MAJOR|MINOR|PATCH: Brief rationale)

Modified principles: [List or "None (enforcement details updated)"]

Added sections:
- [New section name]

Removed sections:
- [Removed section name] (or "None")

Configuration changes:
- [File/path change]: [old] → [new]
- [Structural change description]

Templates requiring updates:
- CLAUDE.md: [Status - updated ✅ or pending ⚠️]
- [Other templates]: [Status]

Follow-up TODOs:
- [Any deferred items] (or "None")

Previous reports:
- X.Y.Z (YYYY-MM-DD): [One-line summary of that version's changes]
- W.X.Y (YYYY-MM-DD): [One-line summary]
- ...
-->
```

**Version History Best Practice**: Maintain a rolling log of previous versions in the SYNC IMPACT REPORT. This provides:
- Quick reference for what changed when
- Context for understanding current state
- Audit trail for compliance reviews

Example from mature constitution:
```html
<!--
Previous reports:
  - 3.1.0 (YYYY-MM-DD): Added CLAUDE.md synchronization mandate
  - 3.0.0 (YYYY-MM-DD): Adopted hexagonal architecture, added strategic abstraction principle
  - 2.1.0 (YYYY-MM-DD): Added unification trigger to API consistency principle
  - 2.0.0 (YYYY-MM-DD): Added API consistency principle
  - 1.8.0 (YYYY-MM-DD): Added exception registry and process
-->
```

See [references/SYNC-IMPACT-FORMAT.md](references/SYNC-IMPACT-FORMAT.md) for complete format.

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

**Greenfield Recommendation**: Beyond the Essential Floor (I-IV: Security, Testing, Error Handling, Observability), greenfield constitutions SHOULD include architectural principles. See [references/RECOMMENDED-PATTERNS.md](references/RECOMMENDED-PATTERNS.md) for:

- **Hexagonal Architecture** (Ports & Adapters) - Layer rules, dependency flow, port interfaces
- **Single Responsibility & Module Boundaries** - Complexity limits, separation of concerns
- **Dependency Discipline** - Justification, isolation, vulnerability scanning

These patterns establish good foundations from day one. It's easier to start with architectural discipline than to retrofit it later.

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

Define synchronization requirements. This is critical because AI coding assistants read CLAUDE.md as their primary instruction source.

```markdown
## CLAUDE.md Synchronization

The `CLAUDE.md` file at repository root MUST remain synchronized with this constitution.
It serves as the primary agent instruction file and MUST contain all information
necessary for AI coding assistants to operate correctly.

**Mandatory Sync Artifacts**:

| Constitution Section | CLAUDE.md Section | Sync Rule |
|---------------------|-------------------|-----------|
| Core Principles (I-X) | Principles Summary | MUST list all principles with enforcement keywords |
| Layer Import Rules | Architecture section | MUST replicate layer rules table |
| Technology Stack | Technical Stack | MUST match exactly |
| Quality Gates | Quality Gates | MUST match exactly |
| Development Workflow | Development Workflow | MUST match branch/review rules |
| Project Management | Project Management | MUST include tool conventions |

**Synchronization Process**:

When amending this constitution:

1. Update constitution version and content
2. Update CLAUDE.md to reflect all changes in the Mandatory Sync Artifacts table
3. Verify CLAUDE.md version matches constitution version
4. Include both files in the same commit
5. PR description MUST note "Constitution sync: CLAUDE.md updated"

**Enforcement**:

- Code review MUST verify CLAUDE.md is updated when constitution changes
- CLAUDE.md MUST display the same version number as the constitution
- Sync drift between files is a blocking issue for PRs that modify either file

**Rationale**: If CLAUDE.md diverges from the constitution, agents will operate with
outdated or incorrect guidance, undermining the governance this constitution establishes.
```

**OPTIONAL:** Use `humaninloop:syncing-claude-md` for implementation guidance.

---

## Related Skills

- **For architectural patterns**: See [references/RECOMMENDED-PATTERNS.md](references/RECOMMENDED-PATTERNS.md) for hexagonal architecture, single responsibility, and dependency discipline principles
- **For brownfield projects**: **REQUIRED** alternative - Use `humaninloop:brownfield-constitution` which extends this skill with Essential Floor + Emergent Ceiling approach
- **For validation**: **OPTIONAL** - Use `humaninloop:validation-constitution` after authoring to verify quality
