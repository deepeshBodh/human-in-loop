<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 -> 1.0.0 (MAJOR: Initial constitution for brownfield project)

Modified principles: N/A (initial creation)

Added sections:
- Core Principles (I-VIII)
- Technology Stack
- Quality Gates
- Governance
- CLAUDE.md Synchronization

Removed sections:
- None

Configuration changes:
- Created constitution from brownfield analysis

Templates requiring updates:
- CLAUDE.md: complete (synced 2026-01-13)

Follow-up TODOs:
- GAP-001: Set up pytest for validator testing
- GAP-002: Add GitHub Actions CI workflow

Previous reports:
- (none - initial version)
-->

# HumanInLoop Plugin Marketplace Constitution

> project_type: brownfield
> Version: 1.0.0
> Ratified: 2026-01-13
> Last Amended: 2026-01-13

This constitution establishes enforceable governance for the HumanInLoop Claude Code Plugin Marketplace. Every principle includes enforcement mechanisms, testability criteria, and rationale. RFC 2119 keywords (MUST, SHOULD, MAY, MUST NOT, SHOULD NOT) define requirement levels.

---

## Core Principles

### Essential Floor Principles

#### I. Security by Default (NON-NEGOTIABLE)

All code artifacts MUST follow security best practices appropriate to a documentation and plugin repository.

- Secrets MUST NOT be committed to the repository
- `.gitignore` MUST exclude sensitive patterns (*.env, *.pem, credentials, secrets)
- Input validation MUST be present in all Python validators before processing user-provided file paths
- Shell scripts MUST validate arguments before processing

**Enforcement**:
- Pre-commit hook or CI check runs `git secrets --scan` (when CI is configured)
- Code review MUST verify no hardcoded secrets in PRs
- `.gitignore` patterns auditable via `cat .gitignore | grep -E "(env|pem|credential|secret)"`

**Testability**:
- Pass: `grep -r "API_KEY\|PASSWORD\|SECRET" --include="*.py" --include="*.sh" plugins/` returns no matches (excluding test fixtures)
- Pass: `.gitignore` contains patterns for `.env`, `*.pem`, `credentials`
- Fail: Any hardcoded secret detected in source files

**Rationale**: Even in documentation repositories, secrets can leak through example code or test fixtures. The .gitignore and scanning approach prevents accidental exposure without requiring complex secret management infrastructure.

---

#### II. Testing Discipline (NON-NEGOTIABLE)

All Python validation scripts MUST have automated tests with measurable coverage.

- Test files MUST exist for each Python validator in `plugins/humaninloop/skills/*/scripts/`
- Test files MUST use pytest framework and follow `test_*.py` naming convention
- Coverage MUST be measured for all validator functions
- Coverage SHOULD be >= 80% for validator functions (warning threshold)
- Coverage MUST NOT fall below 60% for validator functions (blocking threshold)
- New validators MUST include tests in the same PR

**Enforcement**:
- CI runs `pytest plugins/ --cov --cov-fail-under=60` (when configured)
- Code review MUST verify test files accompany new validators
- Coverage report generated on each PR

**Testability**:
- Pass: `pytest plugins/ --cov` completes with exit code 0
- Pass: Coverage >= 60% for `plugins/humaninloop/skills/*/scripts/*.py`
- Fail: Any validator script without corresponding `test_*.py` file
- Fail: Coverage drops below 60%

**Rationale**: The Python validators are critical to workflow quality. Without tests, validator bugs silently produce incorrect results, undermining the entire specification-driven development process. The 60% blocking threshold ensures coverage cannot regress significantly.

**Gap Status**: GAP-001 - Testing infrastructure not yet configured. See `.humaninloop/memory/evolution-roadmap.md`.

---

#### III. Error Handling Standards (NON-NEGOTIABLE)

All scripts MUST handle errors explicitly with contextual information.

- Python validators MUST return structured JSON output with `checks`, `summary`, and `issues` fields
- Python validators MUST exit with code 0 on success, code 1 on validation failure or error
- Shell scripts MUST use `set -e` or explicit error checking
- Shell scripts MUST exit with code 1 and stderr message on failure
- Error messages MUST include the file path, line number (when applicable), and check name

**Enforcement**:
- Code review MUST verify JSON output structure in Python validators
- Code review MUST verify exit code handling in all scripts
- Existing validators serve as reference implementation

**Testability**:
- Pass: `python validate-requirements.py nonexistent.md` exits with code 1 and outputs JSON with `error` field
- Pass: All Python validators output JSON matching schema: `{"checks": [...], "summary": {"passed": N, "failed": M}}`
- Fail: Any validator returns non-JSON output or incorrect exit code

**Rationale**: Consistent error handling enables reliable CI integration and debugging. The JSON output pattern allows downstream tools to parse results programmatically. Exit codes enable shell-level orchestration.

---

#### IV. Observability Requirements (NON-NEGOTIABLE)

All validation scripts MUST produce machine-parseable output for integration with external tools.

- Python validators MUST output JSON to stdout (not stderr)
- Validation results MUST include check name, pass/fail status, and issue list
- Summary section MUST include total, passed, and failed counts
- No PII or sensitive data MAY appear in output

**Enforcement**:
- Code review MUST verify JSON output format
- Existing validators (`validate-requirements.py`, `validate-user-stories.py`, `validate-openapi.py`, `validate-model.py`) serve as reference patterns

**Testability**:
- Pass: `python validate-requirements.py spec.md | jq .summary` succeeds
- Pass: Output can be piped to `jq` without parsing errors
- Fail: Output contains unparseable data before or after JSON

**Rationale**: Structured output enables CI/CD integration, dashboards, and trend analysis. Without machine-parseable output, validation results require manual interpretation.

**Gap Status**: GAP-002 - No structured logging framework for non-validation operations. Acceptable for current scope.

---

### Emergent Ceiling Principles

#### V. Validator Script Pattern

All Python validation scripts MUST follow the established validator pattern.

- Validators MUST have a docstring header with description, checks list, usage, and output format
- Validators MUST define a `validate_file(file_path: str) -> dict` entry function
- Validators MUST use `if __name__ == '__main__':` pattern for CLI invocation
- Check results MUST use structure: `{"check": "name", "passed": bool, "issues": []}`
- Validators MUST include file path in output for traceability

**Enforcement**:
- Code review MUST compare new validators against `validate-requirements.py` as reference
- PR template includes checklist item: "New validators follow established pattern"

**Testability**:
- Pass: New validator has docstring with Usage and Output sections
- Pass: New validator has `validate_file` function returning dict with `checks` and `summary`
- Fail: Validator uses different output structure or lacks docstring

**Rationale**: Consistency enables maintainability. New contributors can understand any validator by learning the pattern once. The pattern also enables potential automation for validator generation.

---

#### VI. ADR Discipline

Architectural decisions MUST be documented in Architecture Decision Records.

- ADRs MUST be created for decisions affecting agent architecture, skill organization, or workflow structure
- ADRs MUST follow the Context/Decision/Rationale/Consequences format
- ADRs MUST be placed in `docs/decisions/` with filename `XXX-descriptive-name.md`
- ADR numbers MUST be sequential (001, 002, 003...)
- ADRs MUST include Status (Proposed, Accepted, Deprecated, Superseded)

**Enforcement**:
- Code review for architectural changes MUST include ADR or justification for why ADR is not needed
- ADR index in `docs/decisions/README.md` MUST be kept current

**Testability**:
- Pass: All files in `docs/decisions/` (except README.md) contain Status, Context, Decision, Rationale, Consequences sections
- Pass: ADR numbers are sequential with no gaps
- Fail: Architectural change merged without corresponding ADR

**Rationale**: ADRs preserve decision context for future maintainers. Without them, teams cargo-cult decisions they don't understand or reverse decisions without knowing the original constraints.

---

#### VII. Skill Structure Requirements

All skills MUST follow the established skill organization pattern.

- Skills MUST have a `SKILL.md` entry point file
- `SKILL.md` MUST be under 200 lines (progressive disclosure principle)
- Skills SHOULD have bundled resource files for detailed content (e.g., `PATTERNS.md`, `EXAMPLES.md`)
- Skill directories MUST use kebab-case naming with category prefix (`authoring-*`, `validation-*`, `patterns-*`, `analysis-*`)
- Skills with validation logic MUST include scripts in a `scripts/` subdirectory

**Enforcement**:
- Code review MUST verify skill structure
- Plugin discovery validates `SKILL.md` presence

**Testability**:
- Pass: `wc -l plugins/humaninloop/skills/*/SKILL.md | awk '$1 > 200 {print "FAIL: "$2}'` returns no output
- Pass: All skill directories contain `SKILL.md`
- Fail: Skill directory missing `SKILL.md` or SKILL.md exceeds 200 lines

**Rationale**: Progressive disclosure keeps token usage efficient when skills are loaded. Category prefixes enable alphabetical grouping and quick identification of skill purpose.

---

#### VIII. Conventional Commits

All commits MUST follow Conventional Commits specification with scope.

- Format: `type(scope): description`
- Valid types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`
- Scope MUST identify affected plugin or area (e.g., `humaninloop`, `constitution`, `spec`)
- Description MUST be imperative mood, lowercase, no period
- Breaking changes MUST include `BREAKING CHANGE:` footer or `!` after type

**Enforcement**:
- CLAUDE.md instructs AI agents to follow this convention
- Code review MUST verify commit message format
- CHANGELOG.md updates MUST reference conventional commit types

**Testability**:
- Pass: `git log --oneline -20 | grep -E "^[a-f0-9]+ (feat|fix|docs|refactor|chore|test|ci)\([a-z-]+\): "` matches all recent commits
- Fail: Commit message does not match pattern

**Rationale**: Conventional commits enable automated changelog generation, semantic versioning decisions, and clear history for debugging. The scope requirement ensures changes are traceable to specific components.

---

## Technology Stack

| Category | Choice | Rationale |
|----------|--------|-----------|
| Primary Content | Markdown | Universal readability, version control friendly |
| Shell Scripts | Bash | POSIX-compatible, available on all target platforms |
| Validation Scripts | Python 3.x | Rich stdlib for text processing, JSON handling |
| Test Framework | pytest (required) | Standard for Python, good assertion introspection |
| Plugin Architecture | Claude Code Plugin System | Native integration with Claude Code |
| Version Control | Git | Industry standard, GitHub integration |
| GitHub Integration | `gh` CLI | Scriptable, consistent across workflows |

---

## Quality Gates

| Gate | Requirement | Measurement | Enforcement |
|------|-------------|-------------|-------------|
| Validator Syntax | Valid Python | `python -m py_compile <file>` | CI automated (when configured) |
| Shell Script Syntax | Valid Bash | `bash -n <file>` | CI automated (when configured) |
| Validator Tests | All pass | `pytest plugins/ --tb=short` | CI automated (when configured) |
| Validator Coverage | >= 60% | `pytest --cov --cov-fail-under=60` | CI automated (blocking) |
| Validator Coverage | >= 80% | `pytest --cov` | CI automated (warning) |
| JSON Schema | Valid output | `python <validator> <input> \| jq .` | CI automated (when configured) |
| Commit Format | Conventional | Pattern match on commit message | Code review |
| ADR Presence | Required for arch changes | Manual review | Code review |

---

## Governance

### Amendment Process

1. Propose change via PR to `.humaninloop/memory/constitution.md`
2. Document rationale for change in PR description
3. Review impact on existing code and CLAUDE.md
4. Obtain maintainer approval
5. Update version per semantic versioning
6. Update CLAUDE.md to reflect changes

### Version Policy

- **MAJOR**: Principle removal or incompatible redefinition
- **MINOR**: New principle or significant expansion
- **PATCH**: Clarification, typo fixes, or wording improvement

### Exception Registry

Approved exceptions to constitution principles MUST be recorded in `docs/constitution-exceptions.md` (create when first exception is approved).

Exception record format:
| Field | Required |
|-------|----------|
| Exception ID | EXC-XXX |
| Principle | Which principle is excepted |
| Scope | Which files/areas are affected |
| Justification | Why exception is needed |
| Approved By | Maintainer who approved |
| Date | When approved |
| Expiry | When exception should be reviewed |
| Tracking Issue | GitHub issue for resolution |

### Approvers

In absence of CODEOWNERS file, project maintainers have approval authority. Maintainers are identified by repository admin access.

---

## CLAUDE.md Synchronization

The `CLAUDE.md` file at repository root MUST remain synchronized with this constitution. It serves as the primary agent instruction file and MUST contain all information necessary for AI coding assistants to operate correctly.

**Mandatory Sync Artifacts**:

| Constitution Section | CLAUDE.md Section | Sync Rule |
|---------------------|-------------------|-----------|
| Core Principles (I-VIII) | Development Guidelines | MUST list key constraints |
| Technology Stack | (embedded in structure) | MUST match project reality |
| Quality Gates | (embedded in workflow) | MUST match exactly |
| Conventional Commits | Commit Conventions | MUST match exactly |
| Governance | Development Workflow | MUST include amendment rules |

**Synchronization Process**:

When amending this constitution:

1. Update constitution version and content
2. Update CLAUDE.md to reflect changes in mapped sections
3. Verify CLAUDE.md reflects current constitution version
4. Include both files in the same commit
5. PR description MUST note "Constitution sync: CLAUDE.md updated"

**Enforcement**:

- Code review MUST verify CLAUDE.md is updated when constitution changes
- Sync drift between files is a blocking issue for PRs that modify either file

**Rationale**: If CLAUDE.md diverges from the constitution, agents will operate with outdated or incorrect guidance, undermining the governance this constitution establishes.

---

## Evolution Notes

This constitution was created from brownfield analysis of the HumanInLoop Plugin Marketplace.

**Essential Floor Status** (from codebase-analysis.md):

| Category | Status | Gap |
|----------|--------|-----|
| Security | partial | N/A (appropriate for repo type) |
| Testing | absent | GAP-001: Configure pytest |
| Error Handling | present | - |
| Observability | partial | GAP-002: Acceptable for current scope |

**Emergent Ceiling Patterns Codified**:

1. Validator Script Pattern (from 5 existing validators)
2. ADR Discipline (from 5 existing ADRs)
3. Skill Structure Requirements (from 16 existing skills)
4. Conventional Commits (from CLAUDE.md and CONTRIBUTING.md)

See `.humaninloop/memory/evolution-roadmap.md` for improvement plan addressing gaps.

---

**Version**: 1.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-13
