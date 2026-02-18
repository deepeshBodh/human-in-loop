<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 -> 2.0.0 (MAJOR: Full rewrite reflecting DAG infrastructure, humaninloop_brain package, deprecation of legacy validators, CI mandate, and revised principle set)

Modified principles:
- I. Security by Default: Updated to include secret scanning mandate, expanded .gitignore patterns
- II. Testing Discipline: Split into humaninloop_brain (90% blocking) and legacy validators (deprecated, no threshold)
- III. Error Handling Standards: Added humaninloop_brain patterns (FrozenPassError, ValidationViolation), expanded exit code convention
- IV. Observability Requirements: Added DAG pass JSON as observability artifact, distinguished CLI tools from web services
- V. Structured Output Pattern: Renamed from "Validator Script Pattern", expanded to cover 12 Python entry points
- VI. ADR Discipline: Updated to 7 ADRs, added index maintenance requirement
- VII. Skill Structure Requirements: REMOVED hard 200-line limit per user decision, replaced with progressive disclosure guidance
- VIII. Conventional Commits: Unchanged in substance
- IX. Deterministic Infrastructure: NEW - separation of Python infrastructure from LLM agents
- X. Pydantic Entity Modeling: NEW - frozen models, type-status validation, model validators

Added sections:
- Principle IX (Deterministic Infrastructure)
- Principle X (Pydantic Entity Modeling)
- Two-codebase distinction in Technology Stack
- CI/CD mandate in Quality Gates

Removed sections:
- None (all v1.0.0 principles preserved or evolved)

Configuration changes:
- Coverage threshold: 60%/80% (validators) -> 90% blocking (humaninloop_brain) + deprecated (legacy validators)
- Technology Stack: Added uv, Pydantic 2.x, NetworkX 3.x, hatchling
- Quality Gates: Added humaninloop_brain-specific gates with actual commands
- Skill line limit: 200 lines hard limit -> progressive disclosure (no numeric limit)
- CI/CD: "when configured" -> P1 MANDATE

Templates requiring updates:
- CLAUDE.md: pending (sync required after constitution ratification)

Follow-up TODOs:
- GAP-001: Create GitHub Actions CI workflow for humaninloop_brain
- GAP-002: Deprecate and migrate legacy plugin validators to humaninloop_brain
- GAP-003: Add secret scanning to CI pipeline

Previous reports:
- 1.0.0 (2026-01-13): Initial brownfield constitution with 8 principles, 2 gaps identified
-->

# HumanInLoop Plugin Marketplace Constitution

> project_type: brownfield
> Version: 2.0.0
> Ratified: 2026-02-18
> Last Amended: 2026-02-18

This constitution establishes enforceable governance for the HumanInLoop Claude Code Plugin Marketplace. Every principle includes enforcement mechanisms, testability criteria, and rationale. RFC 2119 keywords (MUST, SHOULD, MAY, MUST NOT, SHOULD NOT) define requirement levels per RFC 2119.

This project contains two distinct codebases:

| Codebase | Location | Nature | Status |
|----------|----------|--------|--------|
| **humaninloop_brain** | `humaninloop_brain/` | Python package (uv-managed, tested, DAG infrastructure) | Active development |
| **Plugin validators** | `plugins/humaninloop/skills/*/scripts/` | Standalone Python scripts (untested) | Deprecated -- migrate to humaninloop_brain |

Principles apply to both codebases unless explicitly scoped.

---

## Core Principles

### Essential Floor Principles

#### I. Security by Default (NON-NEGOTIABLE)

All code artifacts MUST follow security best practices appropriate to a documentation and plugin repository.

- Secrets MUST NOT be committed to the repository
- `.gitignore` MUST exclude sensitive patterns: `.env`, `.env.local`, `.env.*.local`, `*.pem`, `credentials`, `secrets`
- Input validation MUST be present in all Python code before processing user-provided file paths or external data
- Shell scripts MUST validate arguments before processing
- Pydantic models MUST validate all inputs via model validators (enforced by Pydantic runtime)
- CI MUST run secret scanning on every push (when CI is configured -- see GAP-003)

**Enforcement**:
- CI runs `git secrets --scan` or equivalent secret scanner and blocks merge on findings (GAP-003: not yet configured)
- Code review MUST verify no hardcoded secrets in PRs
- `.gitignore` patterns auditable via inspection of `.gitignore` file
- Pydantic model validators enforce input constraints at runtime

**Testability**:
- Pass: `grep -rn "API_KEY\|PASSWORD\|SECRET_KEY\|PRIVATE_KEY" --include="*.py" --include="*.sh" humaninloop_brain/ plugins/` returns no matches (excluding test fixtures and documentation)
- Pass: `.gitignore` contains patterns for `.env`, `.env.local`, `.env.*.local`, `*.pem`
- Pass: All Pydantic models with external input have model validators
- Fail: Any hardcoded secret detected in source files
- Fail: `.gitignore` missing required exclusion patterns

**Rationale**: Even in documentation repositories, secrets can leak through example code, test fixtures, or configuration files. The `.gitignore` and scanning approach prevents accidental exposure. Pydantic validation at model boundaries catches malformed input before it propagates through the DAG infrastructure.

---

#### II. Testing Discipline (NON-NEGOTIABLE)

All Python code MUST have automated tests with measurable coverage. This project has two codebases with distinct testing requirements.

**humaninloop_brain (active)**:
- Test coverage MUST NOT fall below 90% (blocking CI gate)
- Coverage baseline MUST NOT decrease (ratchet rule)
- Test files MUST use pytest and follow `test_*.py` naming in `test_<module>/` directories
- New functionality MUST include tests in the same PR
- Test fixtures MUST be JSON files in `tests/fixtures/` for DAG scenario testing
- Tests MUST include unit, subprocess integration, and end-to-end levels

**Plugin validators (deprecated)**:
- Legacy validators (`validate-requirements.py`, `validate-user-stories.py`, `validate-openapi.py`, `validate-model.py`, `check-artifacts.py`) are marked for deprecation
- During the deprecation period, legacy validators MAY remain untested
- New validation logic MUST be built in `humaninloop_brain`, not as new plugin validators
- Migration of validation logic from plugin validators to `humaninloop_brain` SHOULD be tracked in the evolution roadmap

**Enforcement**:
- CI runs `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` and blocks merge on failure (GAP-001: CI not yet configured)
- Code review MUST verify test files accompany new `humaninloop_brain` functionality
- Coverage report generated on each PR
- Code review MUST reject new standalone validator scripts in `plugins/`

**Testability**:
- Pass: `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` exits with code 0
- Pass: Coverage >= previous baseline (ratchet rule -- currently 98%)
- Pass: No new Python validator scripts added to `plugins/humaninloop/skills/*/scripts/`
- Fail: Coverage drops below 90% in humaninloop_brain
- Fail: New functionality in humaninloop_brain merged without tests
- Fail: New standalone validator script created instead of adding to humaninloop_brain

**Rationale**: The humaninloop_brain package is the foundation of DAG workflow execution. Its 98% coverage (190 tests) demonstrates that high coverage is achievable and sustainable. The 90% blocking threshold maintains this standard while allowing minor gaps in error-path edge cases. Legacy validators are deprecated because maintaining two testing standards creates governance confusion -- consolidation into humaninloop_brain provides a single, well-tested codebase.

---

#### III. Error Handling Standards (NON-NEGOTIABLE)

All scripts and packages MUST handle errors explicitly with contextual information for debugging.

- Python code MUST return structured JSON output with `checks`, `summary`, and `issues` fields (see Principle V)
- Exit codes MUST follow the project convention:
  - `0` = success
  - `1` = validation failure (expected, actionable)
  - `2` = unexpected error (bug, environment issue)
- Shell scripts MUST use `set -e` or explicit error checking
- Shell scripts MUST exit with code 1 and stderr message on failure
- Error messages MUST include sufficient context: file path, node ID, edge ID, or check name as applicable
- Custom exceptions MUST be used for domain-specific error conditions (e.g., `FrozenPassError` for immutability violations)
- `ValidationViolation` objects MUST include `code`, `severity`, `message`, and optional `node_id`/`edge_id` for traceability

**Enforcement**:
- Code review MUST verify JSON output structure in Python entry points
- Code review MUST verify exit code handling (0/1/2 convention) in all CLI tools
- Tests MUST verify error paths return correct exit codes and structured output
- Pydantic `ValidationViolation` schema enforces required fields at runtime

**Testability**:
- Pass: `hil-dag validate nonexistent.json` exits with code 2 and outputs JSON with error details
- Pass: All Python entry points output JSON matching the structured output schema
- Pass: `FrozenPassError` raised when attempting to mutate a frozen DAG pass
- Pass: `ValidationViolation` objects always include `code`, `severity`, `message`
- Fail: Any entry point returns non-JSON output or uses exit code outside {0, 1, 2}
- Fail: Error message lacks context (e.g., "validation failed" without identifying which node or check)

**Rationale**: Consistent error handling enables reliable CI integration, debugging, and downstream tool composition. The three-tier exit code convention (success/expected-failure/unexpected-error) enables shell-level orchestration. Structured violations with node/edge IDs enable programmatic error routing in DAG workflows.

---

#### IV. Observability Requirements (NON-NEGOTIABLE)

All validation tools and CLI commands MUST produce machine-parseable output for integration with external tools. Observability requirements are scoped to CLI tool output, not web service logging (this project has no web services).

- Python entry points MUST output JSON to stdout (not stderr)
- Validation results MUST include check name, pass/fail status, and issue list
- Summary section MUST include total, passed, and failed counts
- DAG pass JSON MUST serve as the primary observability artifact for workflow execution, containing execution trace entries with timestamps, node IDs, actions, and details
- No PII or sensitive data MAY appear in output
- stderr MUST be reserved for human-readable diagnostic messages (progress indicators, warnings)

**Enforcement**:
- Code review MUST verify JSON output format for all new CLI subcommands
- Existing entry points (`hil-dag create`, `hil-dag validate`, `hil-dag sort`, `hil-dag status`, `hil-dag freeze`, `hil-dag assemble`, `hil-dag catalog-validate`) serve as reference patterns
- Tests MUST verify output is valid JSON parseable by `jq`

**Testability**:
- Pass: `hil-dag validate pass.json | jq .summary` succeeds without parsing errors
- Pass: All CLI subcommand output can be piped to `jq .` without errors
- Pass: DAG pass JSON includes `execution_trace` array with `timestamp`, `node_id`, `action` fields
- Pass: Output contains only structural data (node IDs, edge IDs, violation codes) -- no PII
- Fail: Output contains unparseable data before or after JSON
- Fail: DAG pass JSON missing execution trace entries

**Rationale**: Structured JSON output enables CI/CD integration, composable tooling (piping commands), and trend analysis. For CLI tools (not web services), stdout JSON is the observability layer -- there are no APM dashboards or health check endpoints to configure. DAG pass JSON with execution traces provides workflow-level observability equivalent to structured logging in service-oriented architectures.

---

### Emergent Ceiling Principles

#### V. Structured Output Pattern

All Python entry points MUST follow the established structured output pattern for consistency and composability.

This project has 12 Python entry points that produce structured JSON:
- 7 `hil-dag` CLI subcommands (create, assemble, validate, sort, status, freeze, catalog-validate)
- 5 legacy plugin validators (validate-requirements, validate-user-stories, validate-openapi, validate-model, check-artifacts)

**Output schema**:
```json
{
  "checks": [
    {"check": "<name>", "passed": true/false, "issues": [...]}
  ],
  "summary": {"total": N, "passed": M, "failed": K}
}
```

- All Python entry points MUST output JSON conforming to this schema (or a documented superset)
- Entry points MUST be invocable from the command line via `if __name__ == '__main__':` or CLI framework (argparse)
- Legacy validators MUST have a docstring header with description, checks list, usage, and output format
- New entry points MUST be added to `humaninloop_brain` CLI, not as standalone scripts

**Enforcement**:
- Code review MUST compare new entry points against existing `hil-dag` subcommands as reference
- Tests MUST validate output JSON schema for each entry point
- `validation_result_to_output()` helper function in humaninloop_brain MUST be used for new entry points

**Testability**:
- Pass: Every Python entry point produces JSON matching the structured output schema
- Pass: `python <entry_point> <valid_input> | jq '.checks, .summary'` succeeds for all entry points
- Pass: New entry points use `validation_result_to_output()` helper
- Fail: Entry point outputs non-JSON or uses a different schema
- Fail: New standalone validator script created outside humaninloop_brain

**Rationale**: The structured output pattern is this project's strongest emergent convention, consistently followed across 12 entry points spanning two codebases. It enables programmatic consumption, CI integration, and compositional tooling. Codifying it prevents drift as new entry points are added.

---

#### VI. ADR Discipline

Architectural decisions MUST be documented in Architecture Decision Records.

- ADRs MUST be created for decisions affecting agent architecture, skill organization, workflow structure, or DAG infrastructure design
- ADRs MUST follow the Context/Decision/Rationale/Consequences format
- ADRs MUST be placed in `docs/decisions/` with filename `NNN-descriptive-name.md`
- ADR numbers MUST be sequential (001, 002, 003...)
- ADRs MUST include Status (Proposed, Accepted, Deprecated, Superseded)
- The ADR index at `docs/decisions/README.md` MUST be updated when ADRs are added or status changes

Current ADRs (7):
1. ADR-001: Multi-Agent Architecture
2. ADR-002: Claude Code Native Integration
3. ADR-003: Brownfield-First Design
4. ADR-004: Skill-Augmented Agents
5. ADR-005: Decoupled Agents
6. ADR-006: RFC 2119 Auto-Invocation
7. ADR-007: DAG-First Infrastructure

**Enforcement**:
- Code review for architectural changes MUST include ADR or justification for why ADR is not needed
- ADR index in `docs/decisions/README.md` MUST be kept current
- CHANGELOG.md SHOULD reference ADRs when documenting architectural changes

**Testability**:
- Pass: All files in `docs/decisions/` (except `README.md`) contain Status, Context, Decision, Rationale, Consequences sections
- Pass: ADR numbers are sequential with no gaps
- Pass: `docs/decisions/README.md` lists all ADR files
- Fail: Architectural change merged without corresponding ADR
- Fail: ADR index out of date

**Rationale**: ADRs preserve decision context for future maintainers. The 7 existing ADRs demonstrate this discipline is well-established. Without ADRs, teams cargo-cult decisions they do not understand or reverse decisions without knowing the original constraints. The DAG infrastructure redesign (ADR-007) is a prime example of a decision whose rationale must be preserved.

---

#### VII. Skill Structure Requirements

All skills MUST follow the established skill organization pattern with progressive disclosure.

- Skills MUST have a `SKILL.md` entry point file
- `SKILL.md` SHOULD use progressive disclosure: core instructions in the main file, detailed reference material in bundled files (e.g., `references/PATTERNS.md`, `references/EXAMPLES.md`)
- Skill directories MUST use kebab-case naming with category prefix (`authoring-*`, `validation-*`, `patterns-*`, `analysis-*`, `dag-*`, `using-*`, `testing-*`, `syncing-*`, `brownfield-*`)
- Skills with validation logic MUST include scripts in a `scripts/` subdirectory
- Skills MUST specify related skills with invocation guidance using RFC 2119 keywords (`REQUIRED`, `OPTIONAL`)

Current skill categories (9 categories, 25 skills):
- `analysis-*` (4), `authoring-*` (6), `brownfield-*` (1), `dag-*` (1), `patterns-*` (6), `syncing-*` (1), `testing-*` (1), `using-*` (2), `validation-*` (3)

**Enforcement**:
- Code review MUST verify skill structure (SKILL.md present, kebab-case directory name, category prefix)
- Plugin discovery validates `SKILL.md` presence
- Code review MUST verify that large skills bundle reference files rather than placing all content in SKILL.md

**Testability**:
- Pass: All skill directories contain `SKILL.md`
- Pass: All skill directory names match pattern `^[a-z]+-[a-z-]+$` (kebab-case with category prefix)
- Pass: Skills with > 300 lines of instructional content use bundled reference files
- Fail: Skill directory missing `SKILL.md`
- Fail: Skill directory name uses non-kebab-case or lacks category prefix

**Rationale**: Progressive disclosure keeps token usage efficient when skills are loaded into agent context. Category prefixes enable alphabetical grouping and quick identification of skill purpose. The previous 200-line hard limit was violated by 72% of skills (18/25); progressive disclosure with bundled reference files is the actual effective pattern.

---

#### VIII. Conventional Commits

All commits MUST follow Conventional Commits specification with scope.

- Format: `type(scope): description`
- Valid types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`
- Scope MUST identify affected plugin or area (e.g., `humaninloop`, `constitution`, `brain`, `dag`)
- Description MUST be imperative mood, lowercase, no period
- Breaking changes MUST include `BREAKING CHANGE:` footer or `!` after type
- Multi-line commit bodies SHOULD provide additional context for non-trivial changes

**Enforcement**:
- CLAUDE.md instructs AI agents to follow this convention
- Code review MUST verify commit message format
- CHANGELOG.md updates MUST reference conventional commit types

**Testability**:
- Pass: `git log --oneline -20` shows all commits matching pattern `^[a-f0-9]+ (feat|fix|docs|refactor|chore|test|ci)(\([a-z-]+\))?: .+`
- Fail: Commit message does not match the conventional commits pattern

**Rationale**: Conventional commits enable automated changelog generation, semantic versioning decisions, and clear history for debugging. The scope requirement ensures changes are traceable to specific components. Consistent adherence across the last 20+ commits demonstrates this convention is well-established.

---

#### IX. Deterministic Infrastructure

Deterministic logic MUST be implemented in Python infrastructure (`humaninloop_brain`), not in LLM agent prompts.

- Graph operations (node creation, edge validation, topological sort, cycle detection) MUST be implemented in `humaninloop_brain` using NetworkX
- Structural validation (DAG structure, node contracts, edge constraints, invariant enforcement) MUST be implemented in `humaninloop_brain` validators
- Pass lifecycle management (creation, freezing, status transitions) MUST be implemented in `humaninloop_brain` passes module
- LLM agents MUST consume deterministic infrastructure output via CLI (`hil-dag`) or Python API, not re-implement graph logic
- Shell scripts (`dag-*.sh`) MUST delegate to `hil-dag` CLI subcommands for graph operations, not implement graph logic directly

**Layer separation**:

| Layer | Location | Responsibility | MAY contain |
|-------|----------|----------------|-------------|
| Entities | `humaninloop_brain/src/humaninloop_brain/entities/` | Pydantic models, enums, type definitions | Validation logic via model validators |
| Graph | `humaninloop_brain/src/humaninloop_brain/graph/` | NetworkX operations, DAG algorithms | Topological sort, cycle detection, execution order |
| Validators | `humaninloop_brain/src/humaninloop_brain/validators/` | Structural validation, invariant checking | Violation reporting via ValidationViolation |
| Passes | `humaninloop_brain/src/humaninloop_brain/passes/` | Pass lifecycle, freezing, history | State transitions, immutability enforcement |
| CLI | `humaninloop_brain/src/humaninloop_brain/cli/` | Command-line interface, argument parsing | JSON output formatting via validation_result_to_output() |
| Catalogs | `humaninloop_brain/catalogs/` | Workflow node catalog definitions (JSON) | Node definitions, edge constraints, invariants |

**Enforcement**:
- Code review MUST verify that new graph logic is in `humaninloop_brain`, not in agent definitions or shell scripts
- Code review MUST verify shell scripts delegate to `hil-dag` CLI
- ADR-007 documents the architectural decision and MUST be referenced for context

**Testability**:
- Pass: All graph operations (sort, validate, create, freeze) are callable via `hil-dag` CLI
- Pass: Shell scripts in `plugins/humaninloop/scripts/dag-*.sh` invoke `hil-dag` subcommands
- Pass: No NetworkX or graph algorithm code exists outside `humaninloop_brain/`
- Fail: Graph logic implemented in agent markdown files or shell scripts
- Fail: Shell script implements DAG operations without delegating to `hil-dag`

**Rationale**: LLM agents produce non-deterministic output by nature. Graph operations (cycle detection, topological sort, structural validation) require deterministic, testable behavior. Separating these concerns means the infrastructure layer can be tested with 98% coverage while agents focus on judgment-based tasks (content generation, analysis, decision-making). This separation is documented in ADR-007.

---

#### X. Pydantic Entity Modeling

All domain entities in `humaninloop_brain` MUST use Pydantic frozen models with explicit type-status validation.

- Entity models MUST use `model_config = ConfigDict(frozen=True)` for immutability
- Status updates MUST create new model instances rather than mutating existing ones
- Model validators MUST enforce type-status coherence (e.g., task nodes MUST NOT have gate statuses)
- Enum types MUST be used for constrained value sets (NodeType, EdgeType, PassOutcome, TaskStatus, GateStatus, DecisionStatus, MilestoneStatus)
- `NodeContract` MUST specify `consumes` and `produces` artifact lists for each node
- `FrozenPassError` MUST be raised when code attempts to mutate a frozen DAG pass

Current entity modules (6):
- `enums.py`: 8 enum types (NodeType, EdgeType, PassOutcome, TaskStatus, GateStatus, DecisionStatus, MilestoneStatus, InvariantEnforcement)
- `nodes.py`: GraphNode, NodeContract, ArtifactConsumption, EvidenceAttachment
- `edges.py`: Edge
- `dag_pass.py`: DAGPass, ExecutionTraceEntry, HistoryContext, HistoryPass
- `catalog.py`: CatalogNodeDefinition, EdgeConstraint, SystemInvariant, NodeCatalog
- `validation.py`: ValidationResult, ValidationViolation

**Enforcement**:
- Code review MUST verify new entities use frozen Pydantic models
- Code review MUST verify type-status validators are present on models with status fields
- Tests MUST verify that mutation attempts raise `FrozenPassError` or Pydantic `ValidationError`
- Tests MUST verify type-status coherence (e.g., `GraphNode(type=NodeType.TASK, status=GateStatus.PASSED)` raises `ValueError`)

**Testability**:
- Pass: All entity models in `humaninloop_brain/src/humaninloop_brain/entities/` use `frozen=True`
- Pass: `DAGPass` mutation attempt raises `FrozenPassError`
- Pass: `GraphNode(type=NodeType.TASK, status=GateStatus.PASSED)` raises `ValueError`
- Pass: All constrained value sets use Enum types, not raw strings
- Fail: New entity model without `frozen=True`
- Fail: Code mutates an entity model in-place instead of creating a new instance
- Fail: Raw string used where an Enum type exists

**Rationale**: Immutable entities prevent accidental state corruption in DAG pass processing. When a pass is frozen (completed), its data MUST NOT change -- `FrozenPassError` enforces this invariant. Type-status validation catches category errors at construction time (a task cannot be "passed" -- only gates pass). The 81 entity tests (largest test suite) demonstrate that these constraints are well-tested and essential to correctness.

---

## Technology Stack

| Category | Choice | Version | Rationale |
|----------|--------|---------|-----------|
| Primary Content | Markdown | N/A | Universal readability, version control friendly |
| Infrastructure Language | Python | >= 3.11 | Type hints, Pydantic support, rich stdlib |
| Entity Modeling | Pydantic | >= 2.0 | Frozen models, model validators, JSON serialization |
| Graph Operations | NetworkX | >= 3.0 | Mature DAG algorithms, topological sort, cycle detection |
| Package Manager | uv | Latest | Fast, reliable Python package management for humaninloop_brain |
| Build System | hatchling | Latest | PEP 517 compliant, minimal configuration |
| Shell Scripts | Bash | POSIX-compatible | Available on all target platforms, CI integration |
| Test Framework | pytest | >= 8.0 | Fixtures, parametrization, subprocess testing |
| Coverage Tool | pytest-cov | >= 5.0 | Coverage measurement, fail-under thresholds |
| Plugin Architecture | Claude Code Plugin System | N/A | Native integration with Claude Code runtime |
| Version Control | Git | N/A | Industry standard, GitHub integration |
| GitHub Integration | `gh` CLI | N/A | Scriptable, consistent across workflows |

---

## Quality Gates

| Gate | Scope | Requirement | Command | Enforcement |
|------|-------|-------------|---------|-------------|
| Python Tests | humaninloop_brain | All 190+ tests pass | `cd humaninloop_brain && uv run pytest --tb=short` | CI automated (GAP-001) |
| Test Coverage | humaninloop_brain | >= 90% | `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` | CI automated, blocking (GAP-001) |
| Coverage Ratchet | humaninloop_brain | >= previous baseline (currently 98%) | Compare against stored baseline | CI automated (GAP-001) |
| Python Syntax | humaninloop_brain | Valid Python | `cd humaninloop_brain && uv run python -m py_compile src/humaninloop_brain/**/*.py` | CI automated (GAP-001) |
| Shell Syntax | Plugin scripts | Valid Bash | `bash -n plugins/humaninloop/scripts/*.sh` | CI automated (GAP-001) |
| JSON Schema | CLI output | Valid structured output | `hil-dag validate <input> \| jq .` | Tests |
| Commit Format | All | Conventional Commits | Pattern match on commit message | Code review |
| ADR Presence | Architectural changes | ADR exists | Manual review of `docs/decisions/` | Code review |
| Secret Scanning | All | No secrets in code | `git secrets --scan` | CI automated (GAP-003) |

**GAP-001**: GitHub Actions CI workflow does not yet exist. This is a P1 blocking gap. At minimum, the CI workflow MUST run `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` on every push and PR.

**GAP-003**: Secret scanning is not yet configured. This SHOULD be added to CI when GAP-001 is resolved.

---

## Governance

### Amendment Process

1. Propose change via PR to `.humaninloop/memory/constitution.md`
2. Document rationale for change in PR description
3. Review impact on existing code and CLAUDE.md sync artifacts
4. Obtain maintainer approval
5. Update version per semantic versioning
6. Update CLAUDE.md to reflect changes (see Synchronization section)
7. Include both constitution and CLAUDE.md in the same commit

### Version Policy

- **MAJOR**: Principle removal, incompatible redefinition, or threshold change that breaks existing compliance
- **MINOR**: New principle, significant expansion of existing principle, or new quality gate
- **PATCH**: Clarification, typo fixes, wording improvement, or updated counts/statistics

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
| Date | When approved (ISO format) |
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
| Core Principles (I-X) | Key Principles table | MUST list all 10 principles with enforcement keywords |
| Technology Stack | (embedded in guidelines) | MUST match project reality |
| Quality Gates | Quality Gates table | MUST match exactly (commands, thresholds) |
| Conventional Commits (VIII) | Commit Conventions | MUST match exactly |
| Governance | Development Workflow | MUST include amendment rules |
| Two-codebase distinction | Development Guidelines | MUST distinguish humaninloop_brain from legacy validators |

**Synchronization Process**:

When amending this constitution:

1. Update constitution version and content
2. Update CLAUDE.md to reflect changes in all mapped sections
3. Verify CLAUDE.md reflects current constitution version
4. Include both files in the same commit
5. PR description MUST note "Constitution sync: CLAUDE.md updated"

**Enforcement**:

- Code review MUST verify CLAUDE.md is updated when constitution changes
- Sync drift between files is a blocking issue for PRs that modify either file

**Rationale**: If CLAUDE.md diverges from the constitution, agents will operate with outdated or incorrect guidance, undermining the governance this constitution establishes. The v1.0.0 CLAUDE.md currently references outdated coverage thresholds (60%/80%), missing principles (IX, X), and a 200-line skill limit that no longer applies -- demonstrating why sync discipline matters.

---

## Evolution Notes

This constitution was created from brownfield analysis of the HumanInLoop Plugin Marketplace (v2.0.0 full rewrite).

**Essential Floor Status** (from codebase-analysis.md, 2026-02-18):

| Category | Status | Gap |
|----------|--------|-----|
| Security | partial | GAP-003: Add secret scanning to CI |
| Testing | present (humaninloop_brain: 98%) / absent (plugin validators) | GAP-001: Configure CI; GAP-002: Deprecate legacy validators |
| Error Handling | present | -- |
| Observability | partial (JSON stdout present, no structured logging) | Acceptable for CLI tools |

**Emergent Ceiling Patterns Codified**:

1. Structured Output Pattern (from 12 existing Python entry points)
2. ADR Discipline (from 7 existing ADRs)
3. Skill Structure Requirements (from 25 existing skills, revised to progressive disclosure)
4. Conventional Commits (from consistent commit history)
5. Deterministic Infrastructure (from humaninloop_brain architecture, ADR-007)
6. Pydantic Entity Modeling (from 22 entity models with frozen immutability)

**Key Changes from v1.0.0**:

| Aspect | v1.0.0 | v2.0.0 |
|--------|--------|--------|
| Principles | 8 (I-VIII) | 10 (I-X) |
| Coverage threshold | 60% blocking / 80% warning | 90% blocking (humaninloop_brain) |
| Skill line limit | 200 lines hard limit | Progressive disclosure (no hard limit) |
| CI/CD | "when configured" | P1 mandate |
| Plugin validators | Active, need tests | Deprecated, migrate to humaninloop_brain |
| DAG infrastructure | Not covered | Principles IX, X |
| Entity modeling | Not covered | Principle X |

See `.humaninloop/memory/evolution-roadmap.md` for improvement plan addressing gaps.

---

**Version**: 2.0.0 | **Ratified**: 2026-02-18 | **Last Amended**: 2026-02-18
