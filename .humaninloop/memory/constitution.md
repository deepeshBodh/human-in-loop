<!--
SYNC IMPACT REPORT
==================
Version change: (none) -> 3.0.0 (MAJOR: Initial brownfield constitution)

Rationale for bump:
- Initial ratification of project constitution from brownfield analysis
- Establishes 12 core principles: 4 Essential Floor (NON-NEGOTIABLE) + 8 Emergent Ceiling
- Codifies existing strong patterns discovered in codebase analysis (97% coverage, frozen models, layer dependency, structured JSON, deterministic infrastructure, catalog assembly, conventional commits, ADR discipline)
- MAJOR version chosen to align with existing CLAUDE.md version reference (v3.0.0)

Modified Sections: N/A (initial version)

Added Sections:
- Core Principles (I through XII)
- Technology Stack
- Quality Gates
- Governance
- CLAUDE.md Sync Mandate
- Evolution Notes

Removed Sections: None

Templates Alignment:
- ✅ CLAUDE.md: Already aligned at v3.0.0 (pre-existing, authored in anticipation of this constitution)
- ⚠️ plan-template.md: Review for constitution compliance
- ⚠️ spec-template.md: Review for constitution compliance

Follow-up TODOs:
- GAP-001: Configure secret scanning in CI (git-secrets or gitleaks)
- GAP-002: Configure static type checking (mypy or pyright)
- GAP-003: Add structured logging library for debug observability
- Create evolution-roadmap.md with prioritized gap cards

Previous Reports: None (initial version)
-->

# HumanInLoop Project Constitution

> **Version**: 3.0.0 | **Ratified**: 2026-03-05 | **Last Amended**: 2026-03-05
>
> **Project Type**: brownfield
>
> **Governed Codebase**: `humaninloop_brain/` -- Python package providing deterministic DAG infrastructure for workflow execution. The plugin marketplace (`plugins/`) is the consumption layer and is not governed by code-level principles, only by commit and skill structure conventions.

This constitution defines the enforceable principles, quality gates, and governance processes for the HumanInLoop project. Every principle uses RFC 2119 keywords (MUST, SHOULD, MAY, MUST NOT, SHOULD NOT) and includes Enforcement, Testability, and Rationale sections.

---

## Core Principles

### Essential Floor (NON-NEGOTIABLE)

---

### I. Security by Default (NON-NEGOTIABLE)

All code MUST follow security-first principles. The HumanInLoop project is a CLI tool and library with no network boundaries; security focuses on secret management, input validation, and dependency integrity.

- Secrets MUST be loaded from environment variables. Hardcoded secrets (API keys, tokens, passwords) MUST NOT appear in source code.
- Sensitive config files (`.env`, `.env.*.local`) MUST be listed in `.gitignore`.
- All external inputs MUST be validated before processing. For `humaninloop_brain`, Pydantic model validators (`@model_validator`) MUST enforce type-status constraints and derived field integrity.
- CI MUST run secret scanning on every push and pull request. Tool: `gitleaks` (preferred) or `git-secrets`.
- New dependencies MUST NOT introduce known high or critical vulnerabilities. Dependency audit SHOULD be run before adding new packages.

**Enforcement**:
- CI MUST run `gitleaks detect --source .` and block merge on findings (GAP-001: not yet configured -- MUST be added to `.github/workflows/ci.yml`).
- Pre-commit hook `check-ast` validates Python syntax integrity on every commit.
- Code review MUST verify no hardcoded secrets in PRs.
- Pydantic `model_validator` decorators are the enforcement mechanism for input validation in domain entities.

**Testability**:
- Pass: Zero secrets detected by `gitleaks detect --source .`; all Pydantic models have `model_validator` for inputs with domain constraints; `.env` and `.env.*.local` in `.gitignore`.
- Fail: Any secret detected in source code OR any Pydantic entity model missing input validation for constrained fields OR sensitive files not in `.gitignore`.

**Rationale**: Even CLI tools handle user-provided JSON files and catalog definitions. Input validation prevents malformed data from causing undefined behavior. Secret scanning prevents accidental credential commits that persist in git history.

---

### II. Testing Discipline (NON-NEGOTIABLE)

All production code in `humaninloop_brain` MUST have automated tests.

- New functionality MUST have accompanying tests before merge.
- Test coverage MUST be >= 90% (blocking CI gate). Current: 97%.
- Coverage MUST NOT decrease below 90%. The 90% floor is enforced as an absolute threshold, not a ratchet, because coverage is already well above the floor.
- Test files MUST follow the naming convention: `test_<module>.py`, mirroring the source structure.
- Tests MUST be organized into directories mirroring source layers: `test_entities/`, `test_graph/`, `test_validators/`, `test_passes/`, `test_cli/`.
- All tests MUST pass before merge. Zero test failures is a blocking gate.

**Enforcement**:
- CI runs `cd humaninloop_brain && uv run pytest --cov --cov-report=term --tb=short -q` on every push and PR.
- CI enforces 90% coverage floor: extracts coverage percentage from output and fails if below 90.
- Pre-commit hook `check-ast` validates Python AST integrity before commit.
- Code review MUST verify new functionality has tests.

**Testability**:
- Pass: All 381+ tests pass AND coverage >= 90% AND test files mirror source structure in named directories.
- Fail: Any test failure OR coverage < 90% OR new code without tests.

**Rationale**: The `humaninloop_brain` package provides deterministic infrastructure -- correctness is not optional. The 90% floor reflects the project's existing standard (97% actual) and prevents erosion. Tests mirror source structure so developers can locate tests by knowing the module location.

---

### III. Error Handling Standards (NON-NEGOTIABLE)

All code MUST handle errors explicitly with structured, machine-parseable output. The HumanInLoop project uses structured JSON error output, not RFC 7807 (which targets HTTP APIs).

- Custom exception types MUST be used for domain-specific errors. Existing: `FrozenEntryError` for frozen history entry writes.
- All CLI commands MUST output structured JSON on error with `{"status": "error", "message": "<description>"}` schema.
- Exit codes MUST follow the convention: 0 (success), 1 (validation/user error), 2 (runtime exception).
- `ValidationViolation` objects MUST include `code`, `severity`, `message`, and location fields (`node_id` and/or `edge_id`) for precise error identification.
- CLI validation output MUST follow the `{"checks": [...], "summary": {"total": N, "passed": N, "failed": N, "warnings": N}}` schema.
- Pydantic `ValueError` exceptions MUST include descriptive messages identifying the constraint violated.
- The top-level `main()` function MUST catch all unhandled exceptions and output JSON to stderr with exit code 2.

**Enforcement**:
- CLI output schema is validated by E2E tests in `test_cli/` that parse JSON output and verify field presence.
- Exit codes are verified by CLI tests checking `result.exit_code` against expected values.
- `ValidationViolation` schema is enforced by Pydantic model definition (fields are required).
- Code review MUST verify new CLI commands follow the structured output contract.

**Testability**:
- Pass: All CLI commands produce valid JSON output parseable by `jq`; all error paths return correct exit codes (0/1/2); all `ValidationViolation` objects include `code`, `severity`, `message`.
- Fail: Any CLI command producing non-JSON output OR wrong exit code OR `ValidationViolation` missing required fields.

**Rationale**: The structured output contract enables machine consumption by agents and scripts. Agents parse CLI output to make workflow decisions. Inconsistent output formats break the agent-CLI integration that is the project's core value proposition.

---

### IV. Observability Requirements (NON-NEGOTIABLE)

The system MUST produce sufficient information for debugging workflow execution and diagnosing failures.

- All CLI output MUST be structured JSON, parseable by `jq`.
- The `StrategyGraph` JSON file MUST serve as the primary workflow observability artifact, containing the complete execution state: nodes, edges, passes, history entries, and evidence attachments.
- CLI output MUST NOT include unstructured debug prints or log messages that corrupt JSON output.
- Structured logging with Python's `logging` module or `structlog` SHOULD be added for internal library diagnostics (GAP-003: not yet implemented). When implemented, log output MUST go to stderr to avoid corrupting structured JSON on stdout.
- `StrategyGraph` MUST include `id` and `workflow_id` fields for workflow-level identification across CLI invocations.
- PII MUST NOT appear in any output. The domain model does not handle user PII, but this constraint MUST be maintained.

**Enforcement**:
- CLI tests validate JSON parseability of all command output using `json.loads()`.
- E2E tests verify `StrategyGraph` contains expected nodes, edges, and history after operations.
- Code review MUST verify no `print()` statements in library code (only structured JSON via `json.dumps()`).
- GAP-003 tracks the addition of structured logging for internal diagnostics.

**Testability**:
- Pass: All CLI output is valid JSON; `StrategyGraph` JSON contains complete execution state after operations; zero `print()` calls in `humaninloop_brain/src/` (excluding test fixtures).
- Fail: Any non-JSON output on stdout from CLI commands OR missing execution state in `StrategyGraph` after operations.

**Rationale**: Agents consume CLI output programmatically. Non-JSON output breaks agent workflows. The `StrategyGraph` JSON file is the single source of truth for workflow state -- if it is incomplete, agents cannot make correct decisions. Logging to stderr (when implemented) preserves stdout for structured data.

---

### Emergent Ceiling (FROM CODEBASE)

---

### V. Structured Output Contract

All 7 `hil-dag` CLI subcommands MUST produce machine-parseable JSON following the established schema conventions.

- Validation commands (`validate`, `catalog-validate`) MUST output `{"checks": [...], "summary": {"total": N, "passed": N, "failed": N, "warnings": N}}`.
- Mutation commands (`assemble`, `status`, `record`, `freeze`) MUST output operation result JSON with `"status"` field.
- Query commands (`sort`) MUST output the requested data structure as JSON.
- All commands MUST use exit code 0 for success, 1 for validation/user errors, 2 for runtime exceptions.
- JSON output MUST go to stdout. Error diagnostics MUST go to stderr.
- New CLI subcommands MUST follow the same output conventions before merge.

**Enforcement**:
- E2E tests in `test_cli/test_e2e_scenarios.py` and `test_cli/test_spec_consistency.py` validate output schema for all 7 subcommands.
- CLI tests verify exit codes match expected values for success, validation failure, and runtime error paths.
- Code review MUST verify new subcommands produce conformant JSON output.

**Testability**:
- Pass: All 7 subcommands produce valid JSON matching their expected schema; exit codes are correct for all paths; output goes to stdout, errors to stderr.
- Fail: Any subcommand producing non-conformant JSON OR incorrect exit code OR mixed stdout/stderr output.

**Rationale**: Agents invoke `hil-dag` commands and parse output to drive workflow decisions. Schema consistency across all subcommands means agents can use uniform parsing logic. Breaking the schema breaks agent workflows.

---

### VI. ADR Discipline

Significant architectural decisions MUST be documented as Architecture Decision Records (ADRs) in `docs/decisions/`.

- New architectural decisions MUST have an ADR before implementation begins.
- ADRs MUST follow the numbered naming convention: `NNN-<kebab-case-title>.md` (e.g., `007-dag-first-infrastructure.md`).
- ADRs MUST include: Title, Status (proposed/accepted/deprecated/superseded), Context, Decision, Consequences.
- ADRs MUST NOT be deleted. Superseded ADRs MUST reference their replacement.
- Trivial implementation choices (library version bumps, formatting config) do not require ADRs. ADRs are for decisions that constrain future development.

**Enforcement**:
- Code review MUST verify ADR presence for PRs that introduce new architectural patterns, new layers, new external dependencies, or new integration patterns.
- `docs/decisions/README.md` MUST maintain an index of all ADRs.
- ADR presence is a code review checklist item, not a CI gate (architectural significance requires human judgment).

**Testability**:
- Pass: Every architectural change has a corresponding ADR in `docs/decisions/`; ADR follows naming convention; README index is current.
- Fail: Architectural change merged without ADR OR ADR missing required sections OR README index outdated.

**Rationale**: Architectural decisions outlive the developers who made them. Without ADRs, future maintainers cannot understand why constraints exist, leading to either cargo-culting or accidental violation. The 7 existing ADRs (001-007) demonstrate this pattern's value.

---

### VII. Skill Structure Standards

Claude Code skills in `plugins/humaninloop/skills/` MUST follow the established structure conventions.

- Every skill MUST have a `SKILL.md` file as its entry point.
- Skills MUST use progressive disclosure: core instructions in `SKILL.md`, detailed reference material in a `references/` subdirectory.
- Skill directory names MUST use kebab-case with a category prefix (e.g., `authoring-constitution`, `analysis-codebase`, `patterns-entity-modeling`).
- Skills MUST NOT duplicate content that belongs in a reference file. Large tables, examples, and templates MUST be in `references/`.
- `SKILL.md` MUST include: Overview, When to Use, When NOT to Use, and Related Skills sections.

**Enforcement**:
- Code review MUST verify new skills have `SKILL.md` with required sections.
- Code review MUST verify kebab-case naming with category prefix.
- Shell syntax check in CI validates any scripts bundled with skills: `find plugins/humaninloop -name '*.sh' -print0 | xargs -0 -n1 bash -n`.

**Testability**:
- Pass: Every skill directory has `SKILL.md` with Overview/When to Use/When NOT to Use/Related Skills; directory name is kebab-case with category prefix; no orphaned reference files.
- Fail: Skill directory missing `SKILL.md` OR `SKILL.md` missing required sections OR non-kebab-case directory name.

**Rationale**: Skills are the primary mechanism for augmenting agent capabilities. Consistent structure enables progressive disclosure -- agents read `SKILL.md` first and drill into references only when needed. Without structure, skills become monolithic instruction dumps that degrade agent performance.

---

### VIII. Conventional Commits

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) format with scope.

- Format: `type(scope): description`
- Valid types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`.
- Scope MUST identify the affected area (e.g., `humaninloop`, `brain`, `constitution`, `dag`).
- Description MUST be imperative mood, lowercase, with no trailing period.
- Breaking changes MUST include `!` after type/scope or `BREAKING CHANGE:` in the footer.
- Merge commits are exempt from format validation.

**Enforcement**:
- Pre-commit hook (`conventional-pre-commit` v4.0.0) validates format on every commit locally.
- CI job (`commit-lint`) validates all PR commits against pattern `^(feat|fix|docs|refactor|chore|test|ci)(\([a-z][a-z0-9-]*\))?!?: .+` and blocks merge on violation.
- Double gate (local + CI) ensures no single point of failure for commit format governance.

**Testability**:
- Pass: Every non-merge commit in PR matches the conventional commits regex pattern; pre-commit hook is installed and active.
- Fail: Any non-merge commit failing the pattern OR pre-commit hook not installed.

**Rationale**: Conventional commits enable automated changelog generation, semantic versioning decisions, and clear commit history. The double gate (pre-commit + CI) prevents format violations regardless of whether developers have pre-commit hooks installed.

---

### IX. Deterministic Infrastructure

All graph operations, structural validation, and workflow execution logic MUST live in `humaninloop_brain` and MUST produce deterministic results.

- Deterministic logic MUST NOT live in agent prompts. Agents MUST consume `humaninloop_brain` via the `hil-dag` CLI.
- The `hil-dag` CLI MUST be the sole write gate for `StrategyGraph` JSON files. Agents MUST NOT write or modify JSON directly.
- The system implements two determinism tiers:
  - **Tier 1 (Strict Graph-Algorithmic)**: Topological sort, cycle detection, acyclicity verification, edge inference from contracts. These operations MUST be fully deterministic -- same input always produces same output.
  - **Tier 2 (Heuristic-Deterministic)**: Catalog node resolution by capability tags or description. Resolution MUST be deterministic given the same catalog and query. Ambiguous resolution MUST fail explicitly rather than guessing.
- Lexicographic topological sort MUST be used to ensure stable execution ordering across runs.
- `save_graph()` MUST use the write-validate-swap pattern: backup existing file, write to temp, validate parse-back, atomic rename. This prevents corruption of the single-file `StrategyGraph` JSON.

**Enforcement**:
- Tests in `test_graph/test_sort.py` verify lexicographic topological sort stability.
- Tests in `test_graph/test_inference.py` verify deterministic edge inference.
- Tests in `test_cli/` verify that `save_graph()` uses atomic write pattern.
- Code review MUST reject PRs that add graph logic to agent prompts or plugin code.

**Testability**:
- Pass: Same graph input produces identical topological sort output across 100 runs; edge inference produces identical edges for identical contracts; catalog resolution fails explicitly on ambiguity; `save_graph()` produces valid JSON after atomic write.
- Fail: Non-deterministic sort order OR silent resolution of ambiguous catalog queries OR corrupted `StrategyGraph` after write failure.

**Rationale**: The core value proposition of `humaninloop_brain` is deterministic workflow execution. If agents make graph decisions via LLM prompts instead of deterministic algorithms, workflow behavior becomes unpredictable. The CLI-as-write-gate pattern ensures all mutations go through validated code paths.

---

### X. Pydantic Entity Modeling

All domain entities in `humaninloop_brain/src/humaninloop_brain/entities/` MUST use Pydantic v2 models with frozen configuration.

- All Pydantic models MUST use `model_config = {"frozen": True}`. No mutable domain models are permitted.
- Type-status validation MUST use the `TYPE_STATUS_MAP` enum mapping. Each `NodeType` has a corresponding status enum (`TaskStatus`, `GateLifecycleStatus`, `DecisionStatus`, `MilestoneStatus`), and `model_validator(mode="after")` MUST enforce valid combinations.
- Derived fields (e.g., `edge_id` computed from source, target, and type) MUST be enforced by `model_validator`, not left to callers.
- New entities MUST be added to the `entities/` layer with appropriate validators.
- Entity models MUST NOT contain business logic beyond validation. Business logic belongs in `graph/`, `validators/`, or `passes/`.

**Enforcement**:
- Tests in `test_entities/` verify frozen model behavior (modification attempts raise `ValidationError`).
- Tests verify `TYPE_STATUS_MAP` enforcement: invalid type-status combinations raise `ValueError`.
- Tests verify derived field computation matches expected values.
- Code review MUST verify new models have `model_config = {"frozen": True}` and appropriate validators.

**Testability**:
- Pass: All Pydantic models have `frozen: True`; type-status violations raise `ValueError`; derived fields are computed correctly; entity models contain no business logic.
- Fail: Any model missing `frozen: True` OR type-status mismatch not raising error OR derived field computation delegated to caller.

**Rationale**: Frozen models prevent accidental state mutation in a multi-pass DAG system where nodes are processed repeatedly. The `FrozenEntryError` pattern catches attempts to modify completed history entries. Type-status validation at the model level prevents invalid graph states from ever being constructed, which is cheaper than detecting them later.

---

### XI. Layer Dependency Rule

The `humaninloop_brain` package MUST maintain strict unidirectional import dependencies across its 5 layers.

```
entities       (no internal cross-layer imports; only entities submodules)
    |
  graph        (imports from: entities)
    |
validators     (imports from: entities, graph)
    |
  passes       (imports from: entities, graph)
    |
   cli         (imports from: entities, graph, validators, passes)
```

- No module MUST import from a layer above it in this hierarchy (e.g., `entities` MUST NOT import from `graph`; `graph` MUST NOT import from `validators`).
- `validators` and `passes` are at the same tier -- they MAY NOT import from each other. Both import from `entities` and `graph` only.
- Inline imports that violate layer direction are violations regardless of being inside function bodies.
- New layers or modules MUST be placed in the correct position in the hierarchy and documented.

**Enforcement**:
- Import analysis: `grep -r "from humaninloop_brain" humaninloop_brain/src/humaninloop_brain/` filtered by layer to detect upward imports. This SHOULD be automated in CI (GAP-002 candidate).
- Code review MUST verify all imports respect layer direction.
- The existing codebase has zero layer violations (verified in codebase analysis).

**Testability**:
- Pass: Zero upward imports detected by import analysis; all new modules placed in correct layer position.
- Fail: Any import from a lower layer to a higher layer (e.g., `entities` importing from `graph`).

**Rationale**: Unidirectional dependencies make the codebase testable in isolation -- `entities` can be tested without `graph`, `graph` without `validators`. Bidirectional imports create circular dependency chains that make isolated testing impossible and refactoring dangerous. This is the project's architectural backbone.

---

### XII. Catalog-Driven Assembly

Node assembly MUST be driven by the JSON catalog, not by hardcoded node construction in agent code.

- The node catalog (`humaninloop_brain/catalogs/`) MUST define all available node types with their contracts, capability tags, and constraints.
- Node resolution MUST use the two-tier system: Tier 1 (capability tag match) attempted first, Tier 2 (semantic description fallback) used only when Tier 1 produces no match.
- System invariants (INV-001 through INV-005) MUST be enforced at assembly-time or runtime as specified in the catalog.
- Edge constraints in the catalog MUST define valid source-target node type combinations.
- `carry_forward` gates MUST be respected: nodes MUST NOT advance past a gate that has not been completed.
- New node types MUST be added to the catalog with contracts and capability tags before they can be assembled.

**Enforcement**:
- Tests in `test_validators/test_invariants.py` verify all 5 system invariants.
- Tests in `test_cli/` verify catalog-driven assembly produces expected graph structures.
- `hil-dag catalog-validate` CLI command validates catalog integrity.
- Code review MUST verify new node types are in the catalog, not hardcoded.

**Testability**:
- Pass: All 5 system invariants (INV-001 through INV-005) pass validation; catalog-validate reports zero errors; assembly uses catalog definitions; edge constraints respected.
- Fail: Any invariant violation OR assembly bypassing catalog OR edge constraint violation OR missing catalog entry for new node type.

**Rationale**: Catalog-driven assembly separates "what nodes exist" (catalog) from "how nodes are assembled" (CLI). This enables non-developers to modify workflow structures by editing JSON catalogs without touching Python code. It also makes the set of valid workflows discoverable and auditable.

---

## Technology Stack

| Category | Choice | Version | Rationale |
|----------|--------|---------|-----------|
| Infrastructure Language | Python | >= 3.11 (CI: 3.12) | Type hints, ecosystem, Pydantic integration |
| Entity Modeling | Pydantic | >= 2.0 | Frozen models, validators, JSON serialization |
| Graph Operations | NetworkX | >= 3.0 | MultiDiGraph, topological sort, cycle detection |
| Package Manager | uv | Latest | Fast resolution, lockfile support |
| Build System | hatchling | Latest | PEP 517 compliance, script entry points |
| Test Framework | pytest | >= 8.0 | Fixtures, parametrization, plugin ecosystem |
| Coverage Tool | pytest-cov | >= 5.0 | Coverage measurement integrated with pytest |
| Commit Linting | conventional-pre-commit | v4.0.0 | Pre-commit hook for conventional commits |
| Shell Linting | shellcheck-py | v0.10.0.1 | Shell script static analysis |
| Pre-commit Hooks | pre-commit-hooks | v5.0.0 | AST check, YAML check, whitespace, EOF, large files |
| Shell Scripts | Bash | POSIX-compatible | Plugin scripts |
| Plugin Architecture | Claude Code Plugin System | N/A | Agent/skill/command delivery |
| Primary Content | Markdown | N/A | Documentation, skills, agents |
| Version Control | Git | N/A | Source control |
| GitHub Integration | `gh` CLI | N/A | GitHub operations from command line |

---

## Quality Gates

| Gate | Scope | Requirement | Command | Enforcement |
|------|-------|-------------|---------|-------------|
| Python Tests | `humaninloop_brain` | All 381+ tests pass | `cd humaninloop_brain && uv run pytest --cov --cov-report=term --tb=short -q` | CI automated, blocking |
| Test Coverage | `humaninloop_brain` | >= 90% | CI extracts coverage from pytest output; fails if < 90 | CI automated, blocking |
| Python Syntax (brain) | `humaninloop_brain` | Valid Python AST | `find src/humaninloop_brain -name '*.py' -print0 \| xargs -0 uv run python -m py_compile` | CI automated, blocking |
| Python Syntax (plugins) | `plugins/humaninloop/skills` | Valid Python AST | `find plugins/humaninloop/skills -name '*.py' -print0 \| xargs -0 python3 -m py_compile` | CI automated, blocking |
| Shell Syntax | `plugins/humaninloop` | Valid Bash | `find plugins/humaninloop -name '*.sh' -print0 \| xargs -0 -n1 bash -n` | CI automated, blocking |
| Commit Format | All | Conventional Commits | Pre-commit hook + CI `commit-lint` job (regex: `^(feat\|fix\|docs\|refactor\|chore\|test\|ci)(\([a-z][a-z0-9-]*\))?!?: .+`) | CI automated + pre-commit, blocking |
| JSON Schema | CLI output | Valid structured output | `hil-dag validate <input> \| jq .` | Tests, blocking |
| ADR Presence | Architectural changes | ADR exists in `docs/decisions/` | Manual review | Code review |
| Secret Scanning | All | No secrets in code | `gitleaks detect --source .` | GAP-001: not yet configured |
| Static Type Check | `humaninloop_brain` | Zero type errors | `mypy` or `pyright` | GAP-002: not yet configured |

---

## Governance

### Amendment Process

1. Propose change via PR to this constitution file.
2. Document rationale in PR description.
3. Review impact on existing code and governance.
4. Update version per semantic versioning (see Version Policy below).
5. Update `CLAUDE.md` to reflect all changes per the CLAUDE.md Sync Mandate.
6. Include both constitution and `CLAUDE.md` in the same commit.
7. PR description MUST note "Constitution sync: CLAUDE.md updated".

### Version Policy

| Bump | Trigger | Examples |
|------|---------|---------|
| **MAJOR** | Principle removal or incompatible redefinition | Removing a principle; lowering a NON-NEGOTIABLE threshold |
| **MINOR** | New principle added or significant expansion | Adding Principle XIII; adding 5+ rules to existing principle |
| **PATCH** | Clarification or non-semantic wording change | Fixing typos; rewording for clarity; adding examples |

### Exception Registry

Approved exceptions to constitution principles MUST be recorded in `docs/constitution-exceptions.md` (create if not exists) with:

| Field | Description |
|-------|-------------|
| Exception ID | `EX-NNN` |
| Principle | Which principle is being excepted |
| Scope | What code/area is affected |
| Justification | Why the exception is necessary |
| Approved By | Who approved (PR author + reviewer) |
| Date | When approved (ISO format) |
| Expiry | When exception should be re-evaluated |
| Tracking Issue | GitHub issue for resolution |

### Compliance Review

- Constitution compliance SHOULD be reviewed quarterly.
- Exception registry MUST be reviewed for expired exceptions quarterly.
- Quality gate thresholds SHOULD be evaluated against actual metrics annually.

---

## CLAUDE.md Synchronization

The `CLAUDE.md` file at repository root MUST remain synchronized with this constitution. It serves as the primary AI agent instruction file and MUST contain all information necessary for AI coding assistants to operate correctly.

**Mandatory Sync Artifacts**:

| Constitution Section | CLAUDE.md Section | Sync Rule |
|---------------------|-------------------|-----------|
| Core Principles (I-XII) | Key Principles table | MUST list all principles with enforcement keywords |
| Layer Import Rules (XI) | Layer Dependency Rule section | MUST replicate exact layer hierarchy |
| Technology Stack | Technology Stack table | MUST match exactly |
| Quality Gates | Quality Gates table | MUST match exactly |
| Governance | Development Workflow + Constitution Amendment | MUST include amendment and commit rules |
| Commit Conventions (VIII) | Commit Conventions section | MUST match format, types, and examples |

**Synchronization Process**:

When amending this constitution:

1. Update constitution version and content.
2. Update `CLAUDE.md` to reflect all changes per the Mandatory Sync Artifacts table.
3. Verify `CLAUDE.md` version footer matches constitution version.
4. Include both files in the same commit.
5. PR description MUST note "Constitution sync: CLAUDE.md updated".

**Enforcement**:

- Code review MUST verify `CLAUDE.md` is updated when constitution changes.
- `CLAUDE.md` MUST display the same version number as the constitution in its sync footer.
- Sync drift between files is a blocking issue for PRs that modify either file.

**Rationale**: If `CLAUDE.md` diverges from the constitution, AI agents operate with outdated or incorrect guidance, undermining the governance this constitution establishes. The CLAUDE.md is the operational interface; the constitution is the source of truth.

---

## Evolution Notes

This constitution was created from brownfield analysis of the HumanInLoop codebase on 2026-03-05.

**Essential Floor Status** (from `codebase-analysis.md`):

| Category | Status | Gap |
|----------|--------|-----|
| Security | partial | GAP-001: Secret scanning not configured in CI |
| Testing | present | None -- 381 tests, 97% coverage, 90% CI floor |
| Error Handling | present | None -- structured JSON output, custom exceptions, exit codes |
| Observability | partial | GAP-003: No structured logging library for internal diagnostics |

**Identified Gaps**:

| Gap ID | Description | Priority | Principle |
|--------|-------------|----------|-----------|
| GAP-001 | Secret scanning not configured in CI (`gitleaks` or `git-secrets`) | P1 | I. Security |
| GAP-002 | No static type checker configured (`mypy` or `pyright`) despite extensive type hints | P2 | Quality Gates |
| GAP-003 | No structured logging library for internal library diagnostics | P3 | IV. Observability |

See `.humaninloop/memory/evolution-roadmap.md` for prioritized improvement plan (create after constitution ratification).

**Version**: 3.0.0 | **Ratified**: 2026-03-05 | **Last Amended**: 2026-03-05
