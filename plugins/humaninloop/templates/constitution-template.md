<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0 (MAJOR: Initial constitution)

Rationale for bump:
- Initial ratification of project constitution
- Establishes core principles for development governance

Modified Sections: N/A (initial version)

Added Sections:
- Core Principles
- Technology Stack
- Quality Gates
- Governance
- CLAUDE.md Synchronization

Removed Sections: None

Templates Alignment:
- ⚠️ CLAUDE.md: Requires sync after constitution creation
- ⚠️ Other templates: Review for constitution compliance

Follow-up TODOs:
- Sync CLAUDE.md with constitution content
- Review existing code for constitution compliance

Previous Reports: None (initial version)
-->

# [PROJECT_NAME] Constitution

## Overview

<!--
INSTRUCTION: Brief project description (2-3 sentences) and purpose of this constitution.
Include: What the project does, primary technology, and governance goals.
-->

[PROJECT_DESCRIPTION]

This constitution establishes enforceable development standards for [PROJECT_NAME]. It codifies principles that protect quality, security, and maintainability while enabling rapid, confident delivery.

---

## Core Principles

<!--
INSTRUCTION: Define 5-10 core principles. Each principle MUST have:
1. Enforcement - How compliance is verified
2. Testability - Pass/fail criteria
3. Rationale - Why this constraint exists

Use RFC 2119 keywords: MUST, SHOULD, MAY, MUST NOT, SHOULD NOT
-->

### I. [PRINCIPLE_1_NAME]
<!-- Example: Test-First Development (NON-NEGOTIABLE) -->

[PRINCIPLE_1_DESCRIPTION]
<!--
Example:
All production code MUST be written following test-driven development practices:
- Tests MUST be written before implementation code
- Tests MUST fail before implementation begins (Red phase)
- Implementation MUST only satisfy the failing tests (Green phase)
-->

**Enforcement**:
- [How compliance is verified - CI check, code review, tooling]
- [Specific commands or processes that enforce this]

**Testability**:
- Pass: [What passing looks like]
- Fail: [What failure looks like]

**Rationale**: [Why this constraint exists—what failure mode it prevents, what success it enables]

---

### II. [PRINCIPLE_2_NAME]
<!-- Example: Code Quality & Maintainability -->

[PRINCIPLE_2_DESCRIPTION]

**Enforcement**:
- [Verification method]

**Testability**:
- Pass: [Criteria]
- Fail: [Criteria]

**Rationale**: [Why this matters]

---

### III. [PRINCIPLE_3_NAME]
<!-- Example: Architecture & Design -->

[PRINCIPLE_3_DESCRIPTION]

**Enforcement**:
- [Verification method]

**Testability**:
- Pass: [Criteria]
- Fail: [Criteria]

**Rationale**: [Why this matters]

---

### IV. [PRINCIPLE_4_NAME]
<!-- Example: Security by Default -->

[PRINCIPLE_4_DESCRIPTION]

**Enforcement**:
- [Verification method]

**Testability**:
- Pass: [Criteria]
- Fail: [Criteria]

**Rationale**: [Why this matters]

---

### V. [PRINCIPLE_5_NAME]
<!-- Example: Error Handling & Resilience -->

[PRINCIPLE_5_DESCRIPTION]

**Enforcement**:
- [Verification method]

**Testability**:
- Pass: [Criteria]
- Fail: [Criteria]

**Rationale**: [Why this matters]

---

<!-- Add more principles as needed (VI, VII, VIII...) -->

## Technology Stack

<!--
INSTRUCTION: Document mandated technology choices with rationale.
This section MUST match exactly in CLAUDE.md.
-->

| Category | Choice | Rationale |
|----------|--------|-----------|
| Language | [LANGUAGE] [VERSION] | [Why this choice] |
| Framework | [FRAMEWORK] | [Why this choice] |
| Testing | [TEST_FRAMEWORK] | [Why this choice] |
| Linting | [LINTER] | [Why this choice] |
| Type Checking | [TYPE_CHECKER] | [Why this choice] |
| CI/CD | [CI_PLATFORM] | [Why this choice] |

## Quality Gates

<!--
INSTRUCTION: Define automated checks that block merge.
This section MUST match exactly in CLAUDE.md.

CRITICAL: Replace ALL placeholders with actual tool names and commands.
- Use tools detected in codebase analysis
- Use industry-standard defaults if not detected
- NEVER leave [PLACEHOLDER] syntax in final constitution

Examples by stack:
- Python: `ruff check .`, `pytest --cov-fail-under=80`, `pip-audit`
- Node.js: `eslint .`, `npm test -- --coverage`, `npm audit`
- .NET: `dotnet build --warnaserror`, `dotnet test /p:CollectCoverage=true`, `dotnet list package --vulnerable`
- Go: `golangci-lint run`, `go test -coverprofile=coverage.out`, `govulncheck ./...`
-->

| Gate | Requirement | Measurement | Enforcement |
|------|-------------|-------------|-------------|
| Static Analysis | Zero errors | `[actual lint command]` | CI automated |
| Type Checking | Zero errors | `[actual type check command]` | CI automated |
| Test Suite | All tests pass | `[actual test command]` | CI automated |
| Test Coverage | ≥80% (warning), ≥60% (blocking) | `[actual coverage command]` | CI automated |
| Security Scan | No high/critical vulnerabilities | `[actual security tool, e.g., Trivy, Snyk]` | CI automated |
| Secret Scan | No secrets in code | `[actual secret scanner, e.g., gitleaks, Trivy]` | CI automated |
| Code Review | ≥1 approval | PR status | Branch protection |

## Project Structure

<!--
INSTRUCTION: Define the expected folder organization.
Include if your project has specific structure requirements.
-->

```
[PROJECT_ROOT]/
├── [SOURCE_DIR]/
│   ├── [LAYER_1]/        # [Purpose]
│   ├── [LAYER_2]/        # [Purpose]
│   └── [LAYER_3]/        # [Purpose]
├── [TEST_DIR]/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
└── [CONFIG_FILES]
```

### Layer Import Rules

<!--
INSTRUCTION: Define dependency rules if using layered architecture.
-->

| Layer | MAY Import | MUST NOT Import |
|-------|------------|-----------------|
| [LAYER_1] | [Allowed layers] | [Prohibited layers] |
| [LAYER_2] | [Allowed layers] | [Prohibited layers] |
| [LAYER_3] | [Allowed layers] | [Prohibited layers] |

## Governance

<!--
INSTRUCTION: Specify who approves constitution changes.
Options:
- CODEOWNERS file (recommended): Reference GitHub/GitLab CODEOWNERS
- Named role: "Tech Lead", "Principal Engineer", "Architecture Board"
- Team reference: "@org/team-name"
-->

### Approvers

Constitution amendments MUST be approved by: [APPROVER - e.g., CODEOWNERS, @org/architecture-team, Tech Lead]

### Amendment Process

1. Propose change via PR to constitution file
2. Document rationale for change in PR description
3. Review impact on existing code and templates
4. Obtain approval from designated approvers (see above)
5. Update version per semantic versioning rules below
6. Update CLAUDE.md to reflect changes (mandatory sync)

### Version Policy

- **MAJOR**: Principle removal or incompatible redefinition
- **MINOR**: New principle added or significant expansion of existing principle
- **PATCH**: Clarification, wording improvement, or non-semantic refinement

### Exception Registry

When a principle cannot be followed, approved exceptions MUST be recorded in `docs/constitution-exceptions.md` with:

| Field | Description |
|-------|-------------|
| Exception ID | Unique identifier (EX-001, EX-002, etc.) |
| Principle | Which principle is being deviated from |
| Scope | File(s) or component(s) affected |
| Justification | Why the exception is necessary |
| Approved By | Reviewer who approved |
| Approved Date | ISO date of approval (YYYY-MM-DD) |
| Expiry | Date by which must be resolved, or "Permanent" with justification |
| Tracking Issue | Link to issue for resolution (if applicable) |

### Exception Process

1. Document the specific constraint preventing compliance in PR description
2. Propose the minimal deviation required with quantified scope
3. Obtain explicit approval in code review
4. Add entry to Exception Registry
5. Add TODO comment in code with exception ID reference: `# EX-001: <reason>`

### Compliance Review

- All PRs MUST include constitution compliance verification
- Quarterly audits SHOULD assess codebase alignment with principles
- Violations MUST be tracked and addressed within current sprint

## CLAUDE.md Synchronization

The `CLAUDE.md` file at repository root MUST remain synchronized with this constitution. It serves as the primary instruction file for AI coding assistants and MUST contain accurate governance information.

### Mandatory Sync Mapping

| Constitution Section | CLAUDE.md Section | Sync Rule |
|---------------------|-------------------|-----------|
| Core Principles | Principles Summary | MUST list all principles with enforcement keywords |
| Technology Stack | Technical Stack | MUST match exactly |
| Quality Gates | Quality Gates | MUST match exactly |
| Project Structure | Project Structure | MUST match if present |
| Governance | Development Workflow | MUST include versioning and commit rules |

### Synchronization Process

When amending this constitution:

1. Update constitution version and content
2. Update CLAUDE.md to reflect all changes in the Mandatory Sync Mapping table
3. Verify CLAUDE.md version matches constitution version
4. Include both files in the same commit
5. PR description MUST note "Constitution sync: CLAUDE.md updated"

### Enforcement

- Code review MUST verify CLAUDE.md is updated when constitution changes
- CLAUDE.md MUST display the same version number as the constitution
- Sync drift between files is a blocking issue for PRs that modify either file

---

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
