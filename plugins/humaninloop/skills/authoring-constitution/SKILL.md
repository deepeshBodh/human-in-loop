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
  - 3.1.0 (2025-12-24): Added CLAUDE.md synchronization mandate
  - 3.0.0 (2025-12-20): Hexagonal Architecture adoption, Strategic Abstraction principle
  - 2.1.0 (2025-12-19): Added Unification Trigger to Principle VII
  - 2.0.0 (2025-12-19): Added Principle X - API Consistency
  - 1.8.0 (2025-12-19): Added Exception Registry and Process
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
- [ ] Overview section with project description
- [ ] Core Principles numbered with Roman numerals
- [ ] Technology Stack table complete with rationale
- [ ] Quality Gates table with measurement commands
- [ ] Governance section with amendment process
- [ ] CLAUDE.md Sync Mandate with mapping table
- [ ] Version footer with dates in ISO format

**No Placeholders Rule**:
- [ ] Technology Stack has NO `[PLACEHOLDER]` syntax - all actual tool names
- [ ] Quality Gates has NO `[COMMAND]` placeholders - all actual commands
- [ ] Coverage thresholds are numeric (e.g., "≥80%", NOT "[THRESHOLD]%")
- [ ] Security tools are named (e.g., "Trivy + Snyk", NOT "[SECURITY_COMMAND]")
- [ ] Test commands are complete (e.g., "`pytest --cov`", NOT "`[TEST_COMMAND]`")

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
| **Placeholder syndrome** | `[COMMAND]` instead of actual tool | Use detected tools or industry defaults |
| **Generic thresholds** | "Coverage MUST be measured" | Specify numeric values: "≥80% warning, ≥60% blocking" |
| **Missing secret management** | "Secrets from env" only | Specify secret managers, scanning tools, .gitignore rules |

## Brownfield Mode

When writing constitutions for existing codebases, use the **Essential Floor + Emergent Ceiling** approach.

### Essential Floor (NON-NEGOTIABLE)

Every constitution MUST include principles for these four categories, regardless of codebase state:

| Category | Minimum Requirements | Default Enforcement |
|----------|---------------------|---------------------|
| **Security** | Auth at boundaries, secrets via env/secret managers, input validation, secret scanning in CI | Integration tests, code review, secret scanning tools |
| **Testing** | Automated tests exist, coverage ≥80% (configurable), ratchet rule (coverage MUST NOT decrease) | CI test gate, coverage threshold with warning/blocking levels |
| **Error Handling** | Explicit handling, RFC 7807 Problem Details format, correlation IDs in responses | Schema validation in tests, code review |
| **Observability** | Structured logging, correlation IDs, APM integration, no PII in logs | Config verification, log audit, APM dashboards |

#### Essential Floor Detail Requirements

When writing Essential Floor principles, include these specifics:

**Security Principle MUST address:**
- Secret management: Environment variables OR cloud secret managers (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, etc.)
- Secret scanning: CI MUST run secret scanning tools (e.g., Trivy, Snyk, git-secrets, gitleaks)
- Config file exclusion: Sensitive config files (e.g., `*.local.*`, `appsettings.*.json` with secrets) MUST be in `.gitignore`
- Input validation: All external inputs MUST be validated before processing

**Testing Principle MUST address:**
- Coverage thresholds: Specify numeric values (e.g., warning at <80%, blocking at <60%)
- Ratchet rule: "Coverage baseline MUST NOT decrease" - prevents coverage regression
- Test file conventions: Naming patterns for test files (e.g., `*_test.py`, `*.spec.ts`, `*Test.java`)
- Test organization: How tests mirror source structure

**Error Handling Principle MUST address:**
- Response format: RFC 7807 Problem Details (preferred) or consistent JSON schema
- Error codes: Naming convention (e.g., `ERR_DOMAIN_ACTION`)
- Stack traces: MUST NOT be exposed in production responses
- Correlation: Error responses MUST include correlation/trace IDs

**Observability Principle MUST address:**
- Logging format: Structured JSON logging with standard fields
- APM tools: Name specific tools if detected (e.g., Application Insights, Datadog, New Relic)
- Health checks: Endpoint path and what it validates
- PII prohibition: Logs MUST NOT contain personally identifiable information

**Writing Essential Floor Principles:**

- If codebase **has** the capability → Principle codifies existing pattern with enforcement
- If codebase **lacks** the capability → Principle states "MUST implement" with roadmap gap

Example (Security principle with proper secret management):
```markdown
### I. Security by Default (NON-NEGOTIABLE)

All code MUST follow security-first principles.

- Authentication MUST be enforced at API boundaries
- Secrets MUST be loaded from environment variables or AWS Secrets Manager
- Sensitive config files (`appsettings.*.json`, `.env.local`) MUST be in `.gitignore`
- All external inputs MUST be validated before processing
- CI MUST run secret scanning on every push

**Enforcement**:
- CI runs `trivy fs --scanners secret .` and blocks merge on findings
- CI runs `snyk test` for dependency vulnerabilities
- Code review checklist includes auth verification
- Pre-commit hook runs `gitleaks protect`

**Testability**:
- Pass: Zero secrets in codebase, zero high/critical vulnerabilities, auth on all endpoints
- Fail: Any secret detected OR critical vulnerability OR unauthenticated endpoint

**Rationale**: Security breaches are expensive and damage trust. Defense in depth with automated scanning catches issues before they reach production.
```

Example (codebase has partial testing):
```markdown
### II. Testing Discipline (NON-NEGOTIABLE)

All production code MUST have automated tests.

- New functionality MUST have accompanying tests before merge
- Test coverage MUST be ≥80% (warning) and ≥60% (blocking)
- Coverage baseline MUST NOT decrease (ratchet rule)
- Test files MUST follow naming convention: `*_test.py` or `test_*.py`
- Tests MUST mirror source structure in `tests/` directory

**Enforcement**:
- CI runs `pytest --cov --cov-fail-under=60` and blocks merge on failure
- Coverage report generated on every PR via `pytest-cov`
- Pre-commit hook runs `pytest tests/unit/` for fast feedback
- Coverage ratchet enforced by comparing to baseline in CI

**Testability**:
- Pass: All tests pass AND coverage ≥60% AND coverage ≥ previous baseline
- Fail: Any test fails OR coverage <60% OR coverage decreased

**Rationale**: Tests enable confident refactoring and catch regressions early. The 80% warning/60% blocking thresholds balance coverage with pragmatism. The ratchet rule prevents coverage erosion over time.

> Note: Current coverage is 65%. See GAP-002 in evolution-roadmap.md for improvement plan.
```

### Emergent Ceiling (FROM CODEBASE)

Beyond the essential floor, identify **existing good patterns** worth codifying:

1. **Read codebase analysis** - Look for "Strengths to Preserve" section
2. **Identify patterns** - Naming conventions, architecture patterns, error formats
3. **Codify as principles** - With enforcement mechanisms

#### Common Emergent Ceiling Patterns

Look for these patterns in brownfield analysis and codify if present:

| Pattern Category | What to Look For | Example Principle |
|------------------|------------------|-------------------|
| **Code Quality** | Documentation requirements, API annotations, deprecation handling | "All public APIs MUST have documentation comments" |
| **Architecture** | Layer rules, dependency injection, module boundaries | "Controllers MUST NOT directly access repositories" |
| **API Design** | Response formats, versioning, pagination | "API responses MUST follow RFC 7807 Problem Details" |
| **Authorization** | Role-based access, permission checks | "All endpoints MUST validate user permissions" |
| **Resilience** | Retry policies, circuit breakers, timeouts | "External calls MUST use retry with exponential backoff" |
| **Configuration** | Strongly-typed options, feature flags | "Configuration MUST use strongly-typed options pattern" |

Example (codebase has Code Quality standards):
```markdown
### V. Code Quality Standards

All production code MUST meet documentation and annotation requirements.

- Public APIs MUST have XML documentation comments (or JSDoc, docstrings, etc.)
- API endpoints MUST declare response types (e.g., `[ProducesResponseType]`, OpenAPI annotations)
- Deprecated endpoints MUST return warning headers and log deprecation notices
- Configuration MUST use strongly-typed options pattern (no magic strings)

**Enforcement**:
- CI runs documentation coverage check and warns on missing docs
- OpenAPI spec generated from annotations and validated
- Linter rules enforce no magic strings in configuration

**Testability**:
- Pass: All public APIs documented, all endpoints annotated, zero magic strings
- Fail: Missing documentation on public API OR missing response type annotation

**Rationale**: Documentation enables discoverability and correct usage. Annotations enable tooling and client generation. Strongly-typed configuration prevents runtime errors.
```

Example (codebase has consistent error format):
```markdown
### V. Error Response Format

API error responses MUST follow the established format.

- Error responses MUST include `code`, `message`, and `details` fields
- Error codes MUST use the `ERR_DOMAIN_ACTION` naming convention
- Stack traces MUST NOT be exposed in production responses

**Enforcement**:
- Schema validation in API tests
- Code review checklist item

**Testability**:
- Pass: All error responses match schema
- Fail: Any error response missing required fields

**Rationale**: Consistent error format enables client-side error handling and debugging. Pattern established in existing codebase and proven effective.
```

Example (codebase has Clean Architecture):
```markdown
### VI. Single Responsibility & Layer Discipline

Each module, service, and function MUST have one clear purpose.

- Domain layer handles business logic, not infrastructure concerns
- Adapters handle external system integration, not business logic
- Models define data shape, not behavior
- No "utils" or "helpers" modules—find the right home or create a named module

**Clean Architecture Layers**:

Dependencies MUST flow inward—outer layers depend on inner layers, never reverse:

| Layer | Location | MAY import | MUST NOT import |
|-------|----------|------------|-----------------|
| Domain | `src/domain/` | Python stdlib only | application, adapters, infrastructure |
| Application | `src/application/` | domain, port interfaces | adapters, infrastructure |
| Adapters | `src/adapters/` | application, domain, ports | other adapters directly |
| Infrastructure | `src/infrastructure/` | application (for DI wiring) | domain logic |

**Code Quality Metrics**:

| Metric | Limit | Enforcement |
|--------|-------|-------------|
| Cyclomatic complexity | ≤10 per function | Linter rule in CI |
| Function parameters | ≤5 (use models for more) | Code review |
| File length | ≤300 lines SHOULD, ≤500 MUST | Code review |
| Nesting depth | ≤4 levels | Code review |

**Enforcement**:
- Linter complexity rule configured with `max-complexity = 10` (CI blocks on violation)
- Project structure enforces separation: `domain/`, `application/`, `adapters/`
- Code review MUST reject PRs that mix layers inappropriately
- Type checker strict mode catches type leakage across boundaries

**Testability**:
- Pass: All imports respect layer rules, complexity ≤10, no layer violations
- Fail: Any import from inner to outer layer OR complexity >10

**Rationale**: Clear boundaries make code easier to test, understand, and modify. Mixed responsibilities compound complexity over time.
```

Example (codebase has external service integrations):
```markdown
### VII. Dependency Discipline & Port Interfaces

External dependencies MUST be justified and isolated behind port interfaces.

- New dependencies MUST solve a problem that cannot be reasonably solved in-house
- External service calls MUST be isolated behind port interfaces (enable swapping)
- Version pins MUST be explicit in lock files
- Dependency updates MUST be intentional, not automatic

**Port Interface Requirements**:

All external service calls MUST go through port interfaces:

| External Service | Port Interface Location | Adapter Location |
|------------------|------------------------|------------------|
| AI Providers | `application/ports/outbound/ai_provider.py` | `adapters/outbound/ai/` |
| Storage | `application/ports/outbound/storage.py` | `adapters/outbound/storage/` |
| Database | `application/ports/outbound/repository.py` | `adapters/outbound/persistence/` |
| External APIs | `application/ports/outbound/[service].py` | `adapters/outbound/[service]/` |

**Port Design Rules**:
- Port interfaces MUST be defined as `Protocol` or `ABC` classes
- Port interfaces MUST use domain types in signatures, not SDK types
- Adapters MUST implement port interfaces, not extend them
- One port per logical capability (not per provider)
- Async methods for all I/O operations

**Enforcement**:
- Security scanner blocks merge on known vulnerabilities
- Lock file committed to repo ensures reproducible builds
- Code review MUST justify new dependencies in PR description
- Code review MUST verify external calls use port interfaces

**Testability**:
- Pass: All external calls through ports, no direct SDK usage in domain/application
- Fail: Any external SDK imported in domain layer OR direct HTTP call without port

**Rationale**: Each dependency is a liability—maintenance burden, security surface, potential breaking changes. Isolation via ports enables evolution without rewrite and makes the codebase testable without hitting real external services.
```

### Brownfield Constitution Structure

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

### Brownfield Quality Checklist

Additional checks for brownfield constitutions:

- [ ] All four essential floor categories have principles
- [ ] Existing good patterns identified and codified
- [ ] Gap references included where codebase lacks capability
- [ ] Technology stack matches codebase analysis
- [ ] Quality gates reflect current + target state
- [ ] Evolution Notes section documents brownfield context
