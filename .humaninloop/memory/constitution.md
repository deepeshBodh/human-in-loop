<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 -> 3.0.0 (MAJOR: Complete rewrite for v3 architecture. humaninloop_brain is now the sole governed Python codebase. Plugin validators removed from scope. Two-tier deterministic infrastructure. V3 entity model throughout.)

Modified principles:
- I. Security by Default: Removed plugin validator scope; secret scanning remains GAP-003
- II. Testing Discipline: Single codebase (humaninloop_brain only); 90% blocking floor; ratchet REMOVED; 381 tests at 97% coverage
- III. Error Handling Standards: Updated to v3 entities (FrozenEntryError, not FrozenPassError); removed references to legacy entry points
- IV. Observability Requirements: Updated CLI subcommand list (7 subcommands, no hil-dag create); StrategyGraph JSON as primary artifact
- V. Structured Output Pattern: Reduced to 7 hil-dag CLI entry points (legacy validators removed from scope)
- VI. ADR Discipline: Unchanged in substance
- VII. Skill Structure Requirements: Unchanged in substance
- VIII. Conventional Commits: Added pre-commit hook as enforcement; CI commit-lint job documented
- IX. Deterministic Infrastructure: Split into Tier 1 (strict graph-algorithmic) and Tier 2 (heuristic-deterministic); v3 layer separation with 7 entity modules
- X. Pydantic Entity Modeling: Updated to v3 entities (StrategyGraph, NodeHistoryEntry, PassEntry, GateLifecycleStatus, GateVerdict); 11 enums, 14 models, 7 modules
- XI. Layer Dependency Discipline: NEW — codifies the entities -> graph -> validators -> passes -> cli import rule
- XII. Catalog-Driven Assembly: NEW — codifies v3 single-DAG iteration model with catalog resolution and invariant enforcement

Added sections:
- Principle XI (Layer Dependency Discipline)
- Principle XII (Catalog-Driven Assembly)
- Architecture section (Three-Tier Agent Model, Single-DAG Iteration Model)

Removed sections:
- Two-codebase distinction (plugin validators removed from scope)
- All GAP-001 annotations (CI is resolved)
- Coverage ratchet (replaced by flat 90% floor)
- Plugin validator references throughout

Configuration changes:
- Coverage threshold: 90% blocking + 98% ratchet -> 90% blocking only (no ratchet)
- Quality Gates: Removed GAP-001 annotations; removed coverage ratchet gate; updated test count to 381
- Technology Stack: Added conventional-pre-commit, shellcheck-py; removed plugin validator mentions
- Entity counts: 8 enums -> 11 enums; 6 modules -> 7 modules; 12 entry points -> 7 CLI subcommands
- CLI subcommands: Removed hil-dag create (auto-bootstrapped); corrected to 7 (validate, sort, assemble, status, record, freeze, catalog-validate)
- Title: "Plugin Marketplace Constitution" -> "Project Constitution"

Templates requiring updates:
- CLAUDE.md: pending (sync required after constitution ratification)

Follow-up TODOs:
- GAP-003: Add secret scanning to CI pipeline

Previous reports:
- 2.0.0 (2026-02-18): Full rewrite reflecting DAG infrastructure, humaninloop_brain package, deprecation of legacy validators, CI mandate, 10 principles
- 1.0.0 (2026-01-13): Initial brownfield constitution with 8 principles, 2 gaps identified
-->

# HumanInLoop Project Constitution

> project_type: brownfield
> Version: 3.0.0
> Ratified: 2026-02-19
> Last Amended: 2026-02-19

This constitution establishes enforceable governance for the HumanInLoop project. Every principle includes enforcement mechanisms, testability criteria, and rationale. RFC 2119 keywords (MUST, SHOULD, MAY, MUST NOT, SHOULD NOT) define requirement levels per RFC 2119.

**Governed codebase**: `humaninloop_brain/` -- a Python package providing deterministic DAG infrastructure for workflow execution. The plugin marketplace (agents, commands, skills, templates in `plugins/`) is the consumption layer and is not directly governed by Python code quality principles, though shell scripts and structural conventions apply.

---

## Core Principles

### Essential Floor Principles

#### I. Security by Default (NON-NEGOTIABLE)

All code artifacts MUST follow security best practices appropriate to a CLI tooling and plugin repository.

- Secrets MUST NOT be committed to the repository
- `.gitignore` MUST exclude sensitive patterns: `.env`, `.env.local`, `.env.*.local`, `*.pem`, `credentials`, `secrets`
- Input validation MUST be present in all Python code before processing user-provided file paths or external data
- Shell scripts MUST validate arguments before processing
- Pydantic models MUST validate all inputs via model validators (enforced by Pydantic runtime)
- CI MUST run secret scanning on every push (GAP-003: not yet configured)

**Enforcement**:
- CI runs `git secrets --scan` or equivalent secret scanner and blocks merge on findings (GAP-003: not yet configured)
- Code review MUST verify no hardcoded secrets in PRs
- `.gitignore` patterns auditable via inspection of `.gitignore` file
- Pydantic model validators enforce input constraints at runtime
- Pre-commit hooks run `check-ast`, `check-yaml`, `check-added-large-files` (max 500KB) on every commit

**Testability**:
- Pass: `grep -rn "API_KEY\|PASSWORD\|SECRET_KEY\|PRIVATE_KEY" --include="*.py" --include="*.sh" humaninloop_brain/` returns no matches (excluding test fixtures and documentation)
- Pass: `.gitignore` contains patterns for `.env`, `.env.local`, `.env.*.local`, `*.pem`
- Pass: All Pydantic models with external input have model validators
- Fail: Any hardcoded secret detected in source files
- Fail: `.gitignore` missing required exclusion patterns

**Rationale**: Even in CLI tooling repositories, secrets can leak through example code, test fixtures, or configuration files. The `.gitignore` and scanning approach prevents accidental exposure. Pydantic validation at model boundaries catches malformed input before it propagates through the DAG infrastructure.

---

#### II. Testing Discipline (NON-NEGOTIABLE)

All Python code in `humaninloop_brain` MUST have automated tests with measurable coverage.

- Test coverage MUST NOT fall below 90% (blocking CI gate)
- Test files MUST use pytest and follow `test_*.py` naming in `test_<module>/` directories
- New functionality MUST include tests in the same PR
- Test fixtures MUST be JSON files in `tests/fixtures/` for DAG scenario testing
- Tests MUST include unit, subprocess integration, and end-to-end levels
- Tests MUST verify error paths return correct exit codes and structured output

**Enforcement**:
- CI runs `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` and blocks merge on failure
- Code review MUST verify test files accompany new `humaninloop_brain` functionality
- Coverage report generated on each PR via CI pipeline (`.github/workflows/ci.yml`)

**Testability**:
- Pass: `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` exits with code 0
- Pass: All 381+ tests pass
- Pass: Coverage >= 90%
- Fail: Coverage drops below 90%
- Fail: New functionality merged without tests

**Rationale**: The `humaninloop_brain` package is the foundation of deterministic DAG workflow execution. Its 381 tests at 97% coverage demonstrate that high coverage is achievable and sustainable. The 90% blocking threshold maintains this standard while allowing minor gaps in defensive error-path edge cases. A flat threshold (no ratchet) avoids the operational friction of baseline file management while providing a strong floor.

---

#### III. Error Handling Standards (NON-NEGOTIABLE)

All CLI tools and library code MUST handle errors explicitly with contextual information for debugging.

- Python code MUST return structured JSON output with `checks`, `summary`, and `issues` fields (see Principle V)
- Exit codes MUST follow the project convention:
  - `0` = success
  - `1` = validation failure (expected, actionable)
  - `2` = unexpected error (bug, environment issue)
- Shell scripts MUST use `set -e` or explicit error checking
- Shell scripts MUST exit with code 1 and stderr message on failure
- Error messages MUST include sufficient context: file path, node ID, edge ID, pass number, or check name as applicable
- `FrozenEntryError` MUST be raised when code attempts to modify a frozen history entry or pass entry
- `ValidationViolation` objects MUST include `code`, `severity`, `message`, and optional `node_id`/`edge_id` for traceability

**Enforcement**:
- Code review MUST verify JSON output structure in Python entry points
- Code review MUST verify exit code handling (0/1/2 convention) in all CLI tools
- Tests MUST verify error paths return correct exit codes and structured output
- Pydantic `ValidationViolation` schema enforces required fields at runtime

**Testability**:
- Pass: `hil-dag validate nonexistent.json` exits with code 2 and outputs JSON with error details
- Pass: All `hil-dag` subcommands output JSON matching the structured output schema
- Pass: `FrozenEntryError` raised when attempting to modify a frozen history entry
- Pass: `ValidationViolation` objects always include `code`, `severity`, `message`
- Fail: Any entry point returns non-JSON output or uses exit code outside {0, 1, 2}
- Fail: Error message lacks context (e.g., "validation failed" without identifying which node or check)

**Rationale**: Consistent error handling enables reliable CI integration, debugging, and downstream tool composition. The three-tier exit code convention (success/expected-failure/unexpected-error) enables shell-level orchestration. Structured violations with node/edge IDs enable programmatic error routing in DAG workflows.

---

#### IV. Observability Requirements (NON-NEGOTIABLE)

All CLI commands MUST produce machine-parseable output for integration with external tools. Observability requirements are scoped to CLI tool output, not web service logging (this project has no web services).

- `hil-dag` subcommands MUST output JSON to stdout (not stderr)
- Validation results MUST include check name, pass/fail status, and issue list
- Summary section MUST include total, passed, and failed counts
- StrategyGraph JSON MUST serve as the primary observability artifact for workflow execution, containing node history entries with evidence attachments, execution traces with timestamps, and pass metadata
- No PII or sensitive data MAY appear in output
- stderr MUST be reserved for human-readable diagnostic messages (progress indicators, warnings)

**Enforcement**:
- Code review MUST verify JSON output format for all new CLI subcommands
- Existing entry points (`hil-dag validate`, `hil-dag sort`, `hil-dag assemble`, `hil-dag status`, `hil-dag record`, `hil-dag freeze`, `hil-dag catalog-validate`) serve as reference patterns
- Tests MUST verify output is valid JSON parseable by `jq`

**Testability**:
- Pass: `hil-dag validate pass.json | jq .summary` succeeds without parsing errors
- Pass: All 7 CLI subcommand outputs can be piped to `jq .` without errors
- Pass: StrategyGraph JSON includes `nodes[].history[]` with `evidence`, `trace` fields
- Pass: Output contains only structural data (node IDs, edge IDs, violation codes) -- no PII
- Fail: Output contains unparseable data before or after JSON
- Fail: StrategyGraph JSON missing node history entries or pass metadata

**Rationale**: Structured JSON output enables CI/CD integration, composable tooling (piping commands), and trend analysis. For CLI tools (not web services), stdout JSON is the observability layer -- there are no APM dashboards or health check endpoints to configure. StrategyGraph JSON with node history entries provides workflow-level observability equivalent to structured logging in service-oriented architectures.

---

### Emergent Ceiling Principles

#### V. Structured Output Pattern

All `hil-dag` CLI entry points MUST follow the established structured output pattern for consistency and composability.

The `hil-dag` CLI has 7 subcommands that produce structured JSON:
- `validate` -- structural validation of a StrategyGraph
- `sort` -- topological sort of execution order
- `assemble` -- add or re-open a node in the StrategyGraph
- `status` -- update node status in current pass history entry
- `record` -- write evidence, trace, and status to a node's current pass history entry
- `freeze` -- freeze current pass and optionally create next pass
- `catalog-validate` -- validate a node catalog against schema and constraints

**Output schema**:
```json
{
  "checks": [
    {"check": "<name>", "passed": true, "issues": [...]}
  ],
  "summary": {"total": 1, "passed": 1, "failed": 0}
}
```

- All `hil-dag` subcommands MUST output JSON conforming to this schema (or a documented superset)
- `validation_result_to_output()` helper MUST be used for validation-result subcommands
- New CLI subcommands MUST be added to `humaninloop_brain/src/humaninloop_brain/cli/main.py`

**Enforcement**:
- Code review MUST compare new subcommands against existing implementations as reference
- Tests MUST validate output JSON schema for each subcommand
- `validation_result_to_output()` helper function MUST be used for new validation entry points

**Testability**:
- Pass: Every `hil-dag` subcommand produces JSON matching the structured output schema
- Pass: `hil-dag validate <valid_input> | jq '.checks, .summary'` succeeds for all subcommands
- Pass: New subcommands use `validation_result_to_output()` helper
- Fail: Subcommand outputs non-JSON or uses a different schema
- Fail: New CLI entry point created outside `humaninloop_brain`

**Rationale**: The structured output pattern is this project's strongest emergent convention, consistently followed across all 7 CLI subcommands. It enables programmatic consumption, CI integration, and compositional tooling. Codifying it prevents drift as new subcommands are added.

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

**Rationale**: ADRs preserve decision context for future maintainers. The 7 existing ADRs demonstrate this discipline is well-established. Without ADRs, teams cargo-cult decisions they do not understand or reverse decisions without knowing the original constraints. ADR-007 (DAG-First Infrastructure) is a prime example of a decision whose rationale must be preserved.

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

**Rationale**: Progressive disclosure keeps token usage efficient when skills are loaded into agent context. Category prefixes enable alphabetical grouping and quick identification of skill purpose. The progressive disclosure pattern with bundled reference files is the proven effective approach across all 25 skills.

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
- Pre-commit hook (`conventional-pre-commit` v4.0.0) validates commit message format on every commit
- CI job (`commit-lint` in `.github/workflows/ci.yml`) validates all PR commits against pattern `^(feat|fix|docs|refactor|chore|test|ci)(\([a-z][a-z0-9-]*\))?!?: .+`
- CLAUDE.md instructs AI agents to follow this convention
- CHANGELOG.md updates MUST reference conventional commit types

**Testability**:
- Pass: `git log --oneline -20` shows all commits matching pattern `^[a-f0-9]+ (feat|fix|docs|refactor|chore|test|ci)(\([a-z-]+\))?: .+`
- Pass: Pre-commit hook rejects malformed commit messages locally
- Pass: CI `commit-lint` job passes on PR
- Fail: Commit message does not match the conventional commits pattern
- Fail: CI `commit-lint` job fails

**Rationale**: Conventional commits enable automated changelog generation, semantic versioning decisions, and clear history for debugging. The scope requirement ensures changes are traceable to specific components. Pre-commit hooks and CI enforcement provide two layers of automated validation, catching violations before they reach the repository.

---

#### IX. Deterministic Infrastructure

Deterministic logic MUST be implemented in Python infrastructure (`humaninloop_brain`), not in LLM agent prompts. Deterministic operations are divided into two tiers based on output guarantees.

**Tier 1 -- Strict Graph-Algorithmic** (identical output for identical input):
- Topological sort (`graph/sort.py`)
- Cycle detection (`graph/guard.py`)
- Structural validation (`validators/structural.py`, `validators/contracts.py`, `validators/invariants.py`)
- Edge inference from artifact contracts (`graph/inference.py`)
- DAG assembly (add/re-open nodes, edge creation)
- Pass lifecycle (freeze, status transitions, immutability enforcement)
- Type-status coherence via `TYPE_STATUS_MAP`

**Tier 2 -- Heuristic-Deterministic** (reproducible but not guaranteed optimal):
- `resolve_by_capabilities()` -- capability tag intersection scoring
- `resolve_by_description()` -- word-overlap scoring for intent-to-catalog resolution

Both tiers MUST be implemented in `humaninloop_brain`. LLM agents MUST consume deterministic infrastructure output via CLI (`hil-dag`) or Python API, not re-implement graph logic. Shell scripts (`dag-*.sh`) MUST delegate to `hil-dag` CLI subcommands.

**Layer separation**:

| Layer | Location | Responsibility | MAY contain |
|-------|----------|----------------|-------------|
| Entities | `entities/` (7 modules) | Pydantic models, enums, type definitions | Validation logic via model validators |
| Graph | `graph/` (5 modules) | NetworkX operations, DAG algorithms | Topological sort, cycle detection, edge inference, execution order |
| Validators | `validators/` (3 modules) | Structural validation, invariant checking | Violation reporting via `ValidationViolation` |
| Passes | `passes/` (1 module) | Pass lifecycle, freezing, history | State transitions, immutability enforcement via `FrozenEntryError` |
| CLI | `cli/` (1 module) | Command-line interface, argument parsing | JSON output formatting via `validation_result_to_output()` |
| Catalogs | `catalogs/` (JSON files) | Workflow node catalog definitions | Node definitions, edge constraints, invariants, capabilities |

All locations are relative to `humaninloop_brain/src/humaninloop_brain/`.

**Enforcement**:
- Code review MUST verify that new graph logic is in `humaninloop_brain`, not in agent definitions or shell scripts
- Code review MUST verify shell scripts delegate to `hil-dag` CLI
- Code review MUST classify new deterministic operations as Tier 1 or Tier 2
- ADR-007 documents the architectural decision and MUST be referenced for context

**Testability**:
- Pass: All Tier 1 operations produce identical output for identical input across multiple runs
- Pass: All Tier 2 operations produce consistent output for identical input (same scoring, same ranking)
- Pass: Shell scripts in `plugins/humaninloop/skills/dag-operations/scripts/dag-*.sh` invoke `hil-dag` subcommands
- Pass: No NetworkX or graph algorithm code exists outside `humaninloop_brain/`
- Fail: Graph logic implemented in agent markdown files or shell scripts
- Fail: Shell script implements DAG operations without delegating to `hil-dag`
- Fail: Non-deterministic logic placed in `humaninloop_brain` without Tier 2 classification

**Rationale**: LLM agents produce non-deterministic output by nature. Graph operations (cycle detection, topological sort, structural validation) require deterministic, testable behavior. The two-tier distinction acknowledges that catalog resolution involves heuristic scoring -- it is deterministic (same input produces same output) but not provably optimal. Separating concerns means the infrastructure layer can be tested at 97% coverage while agents focus on judgment-based tasks. This separation is documented in ADR-007.

---

#### X. Pydantic Entity Modeling

All domain entities in `humaninloop_brain` MUST use Pydantic frozen models with explicit type-status validation.

- Entity models MUST use `model_config = ConfigDict(frozen=True)` (or `{"frozen": True}`) for immutability
- Status updates MUST create new model instances (via `model_copy()`) rather than mutating existing ones
- Model validators MUST enforce type-status coherence via `TYPE_STATUS_MAP` (e.g., task nodes MUST NOT have gate statuses)
- Model validators MUST enforce derived field consistency (node `status`, `verdict`, `last_active_pass` derived from latest `NodeHistoryEntry`)
- Enum types MUST be used for constrained value sets
- `FrozenEntryError` MUST be raised when code attempts to modify a frozen history entry or pass entry

**V3 entity model** (11 enums, 14 model classes across 7 modules):

| Module | Entities |
|--------|----------|
| `enums.py` | `NodeType`, `EdgeType`, `PassOutcome`, `TaskStatus`, `GateLifecycleStatus`, `GateVerdict`, `DecisionStatus`, `MilestoneStatus`, `InvariantEnforcement`, `InvariantSeverity`, `TYPE_STATUS_MAP` |
| `nodes.py` | `GraphNode`, `NodeHistoryEntry`, `NodeContract`, `ArtifactConsumption`, `EvidenceAttachment` |
| `edges.py` | `Edge` |
| `dag_pass.py` | `PassEntry`, `ExecutionTraceEntry` |
| `strategy_graph.py` | `StrategyGraph` |
| `catalog.py` | `CatalogNodeDefinition`, `NodeCatalog`, `EdgeConstraint`, `SystemInvariant` |
| `validation.py` | `ValidationResult`, `ValidationViolation` |

**Enforcement**:
- Code review MUST verify new entities use frozen Pydantic models
- Code review MUST verify type-status validators are present on models with status fields
- Code review MUST verify derived field validators are present on models with history arrays
- Tests MUST verify that mutation attempts raise appropriate errors
- Tests MUST verify type-status coherence constraints

**Testability**:
- Pass: All entity models in `humaninloop_brain/src/humaninloop_brain/entities/` use `frozen=True`
- Pass: History entry mutation attempt raises `FrozenEntryError`
- Pass: `GraphNode(type=NodeType.TASK, status="passed")` raises `ValueError` (passed is a `GateLifecycleStatus`, not valid for tasks)
- Pass: All constrained value sets use Enum types, not raw strings
- Pass: `GraphNode` with history enforces `status == history[-1].status`
- Fail: New entity model without `frozen=True`
- Fail: Code mutates an entity model in-place instead of creating a new instance
- Fail: Raw string used where an Enum type exists

**Rationale**: Immutable entities prevent accidental state corruption in StrategyGraph processing. When a pass is frozen (completed), its history entries MUST NOT change -- `FrozenEntryError` enforces this invariant. Type-status validation catches category errors at construction time (a task cannot be "passed" -- only gates pass). Derived field validation ensures top-level node fields always reflect the latest history entry, preventing stale state.

---

#### XI. Layer Dependency Discipline

The `humaninloop_brain` package MUST maintain strict unidirectional import dependencies between layers.

**Import hierarchy** (each layer MAY only import from layers above it):

```
entities       (no internal imports)
    |
  graph        (imports from: entities)
    |
validators     (imports from: entities, graph)
    |
  passes       (imports from: entities, graph)
    |
   cli         (imports from: entities, graph, validators, passes)
```

- No module MUST import from a layer below it in the hierarchy
- `entities/` MUST NOT import from `graph/`, `validators/`, `passes/`, or `cli/`
- `graph/` MUST NOT import from `validators/`, `passes/`, or `cli/`
- `validators/` MUST NOT import from `passes/` or `cli/`
- `passes/` MUST NOT import from `cli/`
- Cross-layer imports within the same tier (e.g., `validators/` importing from `passes/`) MUST NOT occur

**Enforcement**:
- Code review MUST verify import statements do not violate the hierarchy
- Tests SHOULD include an import-order check that scans `from humaninloop_brain.` imports in each module
- CI MAY run a static import analysis tool to detect violations

**Testability**:
- Pass: `grep -rn "from humaninloop_brain.graph\|from humaninloop_brain.validators\|from humaninloop_brain.passes\|from humaninloop_brain.cli" humaninloop_brain/src/humaninloop_brain/entities/` returns no matches
- Pass: `grep -rn "from humaninloop_brain.validators\|from humaninloop_brain.passes\|from humaninloop_brain.cli" humaninloop_brain/src/humaninloop_brain/graph/` returns no matches
- Pass: No circular import errors when running `python -c "import humaninloop_brain"`
- Fail: Any module imports from a layer below it in the hierarchy
- Fail: Circular import detected

**Rationale**: Unidirectional dependencies prevent circular imports, enable independent testing of each layer, and enforce separation of concerns. The current codebase already follows this pattern perfectly -- codifying it prevents regression as the package grows. When every layer depends only on layers above it, changes to lower layers (e.g., CLI output formatting) cannot break higher layers (e.g., entity validation).

---

#### XII. Catalog-Driven Assembly

Workflow node assembly MUST be driven by JSON node catalogs with capability-based resolution and system invariant enforcement.

- Node catalogs MUST define available nodes with `node_id`, `type`, `name`, `description`, `capabilities`, and `contract` (consumes/produces)
- Node catalogs MUST define edge constraints specifying valid source/target node types per edge type
- Node catalogs MUST define system invariants with `id`, `rule`, `enforcement` (assembly-time or runtime), and `severity`
- The `hil-dag assemble` command MUST resolve intent to catalog nodes using two-tier resolution:
  1. Capability tag match (primary): intersect recommendation capability tags with catalog node `capabilities` arrays
  2. Semantic description match (fallback): word-overlap scoring between intent and catalog node `description`/`name`
- Gates with `carry_forward: true` MUST auto-satisfy invariant checks across passes when previously passed
- Assembly MUST auto-resolve invariant prerequisites (e.g., adding prerequisite gate nodes when INV-002 requires constitution verification)
- The `hil-dag` CLI MUST be the sole write gate -- agents MUST NOT write StrategyGraph JSON directly

**Current system invariants**:

| Invariant | Rule | Enforcement |
|-----------|------|-------------|
| INV-001 | Every task node output must pass through a gate node | Assembly-time |
| INV-002 | Constitution must exist before specification work | Assembly-time |
| INV-003 | A `validates` edge must connect to a gate node, not a task node | Assembly-time |
| INV-004 | Maximum 5 passes per workflow before mandatory human checkpoint | Assembly-time |
| INV-005 | Frozen history entries must not be modified | Runtime |

**Enforcement**:
- `hil-dag catalog-validate` MUST validate catalog schema and constraint consistency
- `hil-dag assemble` MUST enforce all assembly-time invariants
- `hil-dag record`, `hil-dag status`, `hil-dag freeze` MUST enforce runtime invariants (frozen entry immutability)
- Tests MUST verify invariant enforcement for each INV-XXX
- Code review MUST verify new catalog entries include `capabilities` arrays

**Testability**:
- Pass: `hil-dag catalog-validate catalogs/specify-catalog.json | jq .summary.failed` returns `0`
- Pass: Assembling a task node without a validating gate triggers INV-001 violation
- Pass: `carry_forward` gate auto-satisfies on pass 2+ when passed in prior pass
- Pass: Direct JSON file writes by agents are rejected (only `hil-dag` CLI may write)
- Fail: Catalog node missing `capabilities` array
- Fail: Assembly bypasses invariant checks
- Fail: Agent writes StrategyGraph JSON directly without going through `hil-dag` CLI

**Rationale**: Catalog-driven assembly centralizes workflow definitions in declarative JSON, making them inspectable, validatable, and version-controlled independently of code. Capability-based resolution enables intent-driven assembly where the State Analyst recommends by capability tags and the DAG Assembler resolves to concrete catalog nodes. System invariants enforce structural correctness at assembly time, catching constraint violations before workflow execution begins.

---

## Architecture

### Three-Tier Agent Model

The v3 architecture uses a three-tier agent model where the Supervisor is domain-agnostic, the State Analyst and DAG Assembler own domain knowledge and graph mechanics respectively, and specialist agents focus on their domain expertise.

```
Tier 1: Supervisor (domain-agnostic dispatcher)
    |
    +-- Tier 2a: State Analyst (domain-aware recommender, reads catalog + artifacts + DAG)
    +-- Tier 2b: DAG Assembler (graph mechanic, resolves intent, assembles nodes, freezes passes)
    |
    +-- Tier 3: Domain Agents (8 specialists: requirements-analyst, devils-advocate,
        plan-architect, principal-architect, task-architect, technical-analyst,
        testing-agent, ui-designer)
```

**Knowledge distribution**:

| Agent | Knows | Does NOT Know |
|-------|-------|---------------|
| Supervisor | 4 node types, 6 edge types, pass lifecycle, gate verdicts, goal criteria | Node IDs, agent types, strategy patterns, catalog contents |
| State Analyst | Catalog, strategy skills, artifact state, DAG history, gap classification | Assembly mechanics, prompt construction, graph structure operations |
| DAG Assembler | Catalog structure, invariants, edge inference, intent resolution | Strategy patterns, artifact content, prior pass context |
| Domain Agents | Their domain expertise, skills, artifact conventions | Workflow structure, DAG mechanics, other agents' existence |

### Single-DAG Iteration Model

A single `StrategyGraph` JSON file captures the complete workflow story across multiple passes:

- **One file per workflow invocation** -- the entire history in one place
- **Nodes accumulate history** -- each pass adds a `NodeHistoryEntry`, never modifies prior entries
- **Structural edges persist** -- `depends_on`, `produces`, `validates`, `constrained_by`, `informed_by` edges created once at first assembly
- **Revision edges are explicit** -- `triggered_by` edges capture why a node re-executed, with `source_pass`, `target_pass`, and `reason` fields
- **Pass-entry immutability** -- frozen entries cannot be modified; enforced by `hil-dag` CLI via `FrozenEntryError`
- **Derived fields computed automatically** -- node `status`, `verdict`, and `last_active_pass` always equal the values from the most recent history entry

### `hil-dag` CLI Subcommands

| Command | Purpose |
|---------|---------|
| `hil-dag validate` | Structural validation (10-step) of a StrategyGraph |
| `hil-dag sort` | Topological sort producing execution order |
| `hil-dag assemble` | Add new node or re-open existing node with new history entry |
| `hil-dag status` | Update node status in current pass history entry |
| `hil-dag record` | Write evidence, trace, and status to a node's current pass history entry |
| `hil-dag freeze` | Freeze current pass entries atomically; optionally create next pass |
| `hil-dag catalog-validate` | Validate node catalog against schema and constraints |

---

## Technology Stack

| Category | Choice | Version | Rationale |
|----------|--------|---------|-----------|
| Infrastructure Language | Python | >= 3.11 | Type hints, Pydantic support, rich stdlib |
| Entity Modeling | Pydantic | >= 2.0 | Frozen models, model validators, JSON serialization |
| Graph Operations | NetworkX | >= 3.0 | Mature DAG algorithms, topological sort, cycle detection |
| Package Manager | uv | Latest | Fast, reliable Python package management |
| Build System | hatchling | Latest | PEP 517 compliant, minimal configuration |
| Shell Scripts | Bash | POSIX-compatible | Available on all target platforms, CI integration |
| Test Framework | pytest | >= 8.0 | Fixtures, parametrization, subprocess testing |
| Coverage Tool | pytest-cov | >= 5.0 | Coverage measurement, fail-under thresholds |
| Commit Linting | conventional-pre-commit | v4.0.0 | Pre-commit hook for Conventional Commits |
| Shell Linting | shellcheck-py | v0.10.0.1 | Shell script static analysis |
| Plugin Architecture | Claude Code Plugin System | N/A | Native integration with Claude Code runtime |
| Primary Content | Markdown | N/A | Universal readability, version control friendly |
| Version Control | Git | N/A | Industry standard, GitHub integration |
| GitHub Integration | `gh` CLI | N/A | Scriptable, consistent across workflows |

---

## Quality Gates

| Gate | Scope | Requirement | Command | Enforcement |
|------|-------|-------------|---------|-------------|
| Python Tests | humaninloop_brain | All 381+ tests pass | `cd humaninloop_brain && uv run pytest --tb=short` | CI automated |
| Test Coverage | humaninloop_brain | >= 90% | `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` | CI automated, blocking |
| Python Syntax | humaninloop_brain | Valid Python | `find src/humaninloop_brain -name '*.py' -print0 \| xargs -0 uv run python -m py_compile` | CI automated |
| Shell Syntax | Plugin scripts | Valid Bash | `find plugins/humaninloop -name '*.sh' -print0 \| xargs -0 -n1 bash -n` | CI automated |
| JSON Schema | CLI output | Valid structured output | `hil-dag validate <input> \| jq .` | Tests |
| Commit Format | All | Conventional Commits | Pre-commit hook + CI `commit-lint` job | CI automated + pre-commit |
| ADR Presence | Architectural changes | ADR exists | Manual review of `docs/decisions/` | Code review |
| Secret Scanning | All | No secrets in code | `git secrets --scan` | GAP-003: not yet configured |

**GAP-003**: Secret scanning is not yet configured in CI. This SHOULD be added to the CI pipeline.

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
| Core Principles (I-XII) | Key Principles table | MUST list all 12 principles with enforcement keywords |
| Technology Stack | Technology Stack table | MUST match exactly |
| Quality Gates | Quality Gates table | MUST match exactly (commands, thresholds) |
| Conventional Commits (VIII) | Commit Conventions | MUST match exactly |
| Governance | Development Workflow | MUST include amendment rules |
| Layer Dependency (XI) | Architecture guidance | MUST replicate import hierarchy |

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

**Rationale**: If CLAUDE.md diverges from the constitution, agents will operate with outdated or incorrect guidance, undermining the governance this constitution establishes.

---

## Evolution Notes

This constitution was created from brownfield analysis of the HumanInLoop project (v3.0.0 complete rewrite).

**Essential Floor Status** (from codebase-analysis.md, 2026-02-19):

| Category | Status | Gap |
|----------|--------|-----|
| Security | partial | GAP-003: Add secret scanning to CI |
| Testing | present (381 tests, 97% coverage, CI enforced) | -- |
| Error Handling | present | -- |
| Observability | present (JSON stdout, StrategyGraph artifact) | -- |

**Emergent Ceiling Patterns Codified**:

1. Structured Output Pattern (from 7 hil-dag CLI subcommands)
2. ADR Discipline (from 7 existing ADRs)
3. Skill Structure Requirements (from 25 existing skills, progressive disclosure)
4. Conventional Commits (from consistent commit history + pre-commit + CI enforcement)
5. Deterministic Infrastructure (from humaninloop_brain architecture, ADR-007, two-tier classification)
6. Pydantic Entity Modeling (from 25 entity definitions with frozen immutability, v3 model)
7. Layer Dependency Discipline (from observed clean import hierarchy)
8. Catalog-Driven Assembly (from v3 single-DAG iteration model with capability resolution)

**Key Changes from v2.0.0**:

| Aspect | v2.0.0 | v3.0.0 |
|--------|--------|--------|
| Principles | 10 (I-X) | 12 (I-XII) |
| Governed codebases | 2 (humaninloop_brain + plugin validators) | 1 (humaninloop_brain only) |
| Coverage threshold | 90% blocking + 98% ratchet | 90% blocking (no ratchet) |
| Test count | 190+ | 381+ |
| Entity modules | 6 | 7 (strategy_graph.py added) |
| Enum types | 8 | 11 (GateLifecycleStatus, GateVerdict, TYPE_STATUS_MAP added) |
| CLI subcommands | 7 (incl. create) | 7 (create removed, replaced by auto-bootstrap) |
| Deterministic tiers | 1 (undifferentiated) | 2 (strict graph-algorithmic + heuristic-deterministic) |
| CI status | GAP-001 (not configured) | Resolved (`.github/workflows/ci.yml`) |
| Agent model | Not specified | Three-tier (Supervisor, State Analyst + DAG Assembler, Domain Agents) |
| DAG model | DAG-per-pass (implied) | Single-DAG iteration (StrategyGraph) |
| Title | Plugin Marketplace Constitution | Project Constitution |

---

**Version**: 3.0.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-02-19
