# Codebase Analysis

> Generated: 2026-03-05T19:30:00Z
> Mode: brownfield-setup
> Status: draft

---

## Part 1: Inventory (Factual)

### Project Identity

| Aspect | Value | Source |
|--------|-------|--------|
| Name | human-in-loop (HumanInLoop) | `CLAUDE.md`, `README.md` |
| Primary Language | Python >= 3.11 | `pyproject.toml` |
| Framework | Pydantic >= 2.0, NetworkX >= 3.0 | `pyproject.toml` |
| Package Manager | uv | `CLAUDE.md`, `uv.lock` present |
| Build System | hatchling | `pyproject.toml` |
| Entry Points | `hil-dag` CLI (`humaninloop_brain.cli.main:main`) | `pyproject.toml [project.scripts]` |
| Package Version | 0.1.0 | `humaninloop_brain/__init__.py` |
| Python Version | 3.12 (CI) | `.github/workflows/ci.yml` |

### Directory Structure

```
human-in-loop/
├── .claude-plugin/          # Marketplace manifest (marketplace.json)
├── .github/workflows/       # CI/CD (ci.yml)
├── .humaninloop/memory/     # Constitution and governance memory
├── humaninloop_brain/       # GOVERNED CODEBASE: Python package
│   ├── src/humaninloop_brain/
│   │   ├── entities/        # Pydantic models (7 modules)
│   │   ├── graph/           # NetworkX operations (5 modules)
│   │   ├── validators/      # Structural + contract + invariant validation (3 modules)
│   │   ├── passes/          # Pass lifecycle management (1 module)
│   │   └── cli/             # hil-dag CLI entry point (1 module)
│   ├── catalogs/            # JSON catalog definitions (1 file)
│   ├── tests/               # pytest test suite (27 files)
│   └── pyproject.toml       # Package configuration
├── plugins/humaninloop/     # Claude Code plugin marketplace
│   ├── agents/              # 9 agent definitions (.md)
│   ├── commands/            # 7 slash commands (.md)
│   ├── skills/              # 24 skills (SKILL.md + references)
│   ├── catalogs/            # Specify workflow catalog (.json)
│   ├── scripts/             # Shell scripts (4 files)
│   └── templates/           # Workflow templates (19 files)
├── docs/
│   ├── decisions/           # ADRs (7 records)
│   ├── architecture/        # Architecture synthesis docs
│   └── architecture/v3/     # V3 architecture design
├── CLAUDE.md                # AI agent instruction file
├── CONTRIBUTING.md          # Plugin contribution guide
├── CHANGELOG.md             # Release history
├── RELEASES.md              # Release process
├── ROADMAP.md               # Planned features
└── .pre-commit-config.yaml  # Commit linting + syntax checks
```

### Detected Patterns

#### Architecture Pattern

| Pattern | Evidence |
|---------|----------|
| **Layered Architecture** (strict unidirectional) | 5-layer hierarchy: `entities` -> `graph` -> `validators` -> `passes` -> `cli` |
| **Immutable Domain Models** (Frozen Pydantic) | Every Pydantic model uses `model_config = {"frozen": True}` |
| **CLI-as-Write-Gate** | `hil-dag` CLI is the sole write path for StrategyGraph JSON; agents invoke CLI, never write JSON directly |
| **Catalog-Driven Assembly** | Node catalog JSON defines available nodes; CLI resolves by capability tags or description; edges inferred from contracts |
| **Multi-Pass DAG** | StrategyGraph accumulates nodes/edges across passes; history entries track per-pass status; frozen entries enforce immutability |

**Layer Dependency Verification** (verified via import analysis):

```
entities       (imports only from entities submodules)
    |
  graph        (imports from: entities)
    |
validators     (imports from: entities, graph)
    |
  passes       (imports from: entities, graph)
    |
   cli         (imports from: entities, graph, passes, validators)
```

No upward imports detected. All imports are unidirectional and compliant.

#### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case | `strategy_graph.py`, `dag_pass.py` |
| Variables | snake_case | `node_types`, `seen_edges`, `pass_number` |
| Functions | snake_case with verb prefix | `load_graph()`, `check_acyclicity()`, `validate_structure()` |
| Classes | PascalCase | `StrategyGraph`, `GraphNode`, `ValidationViolation` |
| Enums | PascalCase class, lowercase values | `NodeType.task`, `EdgeType.depends_on` |
| CLI subcommands | kebab-case | `hil-dag validate`, `hil-dag catalog-validate` |
| Edge IDs | kebab-case with prefix | `inferred-depends-on-{src}-{tgt}`, `triggered-by-{src}-{tgt}-pass{n}-to-pass{m}` |
| Test files | `test_` prefix mirroring source | `test_lifecycle.py`, `test_structural.py` |

#### Error Handling Pattern

| Pattern | Evidence |
|---------|----------|
| **Custom exception types** | `FrozenEntryError(Exception)` in `passes/lifecycle.py` |
| **Pydantic model validators** | `@model_validator(mode="after")` for type-status validation and derived field enforcement in `nodes.py`, `catalog.py` |
| **Structured JSON error output** | CLI outputs `{"status": "error", "message": ...}` on failure; exit codes 0/1/2 |
| **ValidationResult/ValidationViolation** | Typed validation results with `code`, `severity`, `message`, `node_id`/`edge_id` |
| **Structured checks/summary** | CLI validation output follows `{"checks": [...], "summary": {"total", "passed", "failed", "warnings"}}` schema |
| **Top-level exception handler** | `main()` catches all exceptions, outputs JSON to stderr, returns exit code 2 |

#### Test Pattern

| Aspect | Value |
|--------|-------|
| Framework | pytest >= 8.0 |
| Location | `humaninloop_brain/tests/` |
| Naming | `test_<module>.py` mirroring source structure |
| Coverage Config | `pyproject.toml` (`[tool.coverage.run]` and `[tool.coverage.report]`) |
| Coverage Tool | pytest-cov >= 5.0 |
| Test Count | 381 tests |
| Coverage | 97% (1004 statements, 26 missed) |
| Test Structure | Unit tests per module + E2E scenario tests + spec consistency tests |
| Fixtures | `conftest.py` with `fixtures_dir` and `load_fixture` helpers |
| Test Categories | Entity validation, graph operations, validator checks, pass lifecycle, CLI commands, E2E scenarios |

### Domain Entities

| Entity | File | Field Count | Relationships |
|--------|------|-------------|---------------|
| `GraphNode` | `entities/nodes.py` | 11 | Has `NodeContract`, list of `NodeHistoryEntry`, references `NodeType` enum |
| `Edge` | `entities/edges.py` | 7 | References `EdgeType` enum, source/target node IDs |
| `StrategyGraph` | `entities/strategy_graph.py` | 9 | Contains lists of `GraphNode`, `Edge`, `PassEntry` |
| `PassEntry` | `entities/dag_pass.py` | 6 | Contained by `StrategyGraph` |
| `NodeHistoryEntry` | `entities/nodes.py` | 6 | Contained by `GraphNode`, references `EvidenceAttachment` |
| `EvidenceAttachment` | `entities/nodes.py` | 4 | Contained by `NodeHistoryEntry` |
| `NodeContract` | `entities/nodes.py` | 2 | Contained by `GraphNode`, references `ArtifactConsumption` |
| `ArtifactConsumption` | `entities/nodes.py` | 3 | Contained by `NodeContract` |
| `ExecutionTraceEntry` | `entities/dag_pass.py` | 6 | Referenced by pass execution |
| `NodeCatalog` | `entities/catalog.py` | 5 | Contains `CatalogNodeDefinition`, `EdgeConstraint`, `SystemInvariant` |
| `CatalogNodeDefinition` | `entities/catalog.py` | 14 | Contained by `NodeCatalog` |
| `EdgeConstraint` | `entities/catalog.py` | 3 | Contained by `NodeCatalog` |
| `SystemInvariant` | `entities/catalog.py` | 4 | Contained by `NodeCatalog` |
| `ValidationResult` | `entities/validation.py` | 3 | Contains `ValidationViolation` |
| `ValidationViolation` | `entities/validation.py` | 5 | Contained by `ValidationResult` |

**Enums** (11):

| Enum | Values |
|------|--------|
| `NodeType` | task, gate, decision, milestone |
| `EdgeType` | depends_on, produces, validates, constrained_by, informed_by, triggered_by |
| `PassOutcome` | completed, halted |
| `TaskStatus` | pending, in-progress, completed, skipped, halted |
| `GateLifecycleStatus` | pending, in-progress, completed, passed, failed |
| `DecisionStatus` | pending, decided |
| `MilestoneStatus` | pending, achieved |
| `InvariantEnforcement` | assembly-time, runtime |
| `InvariantSeverity` | error, warning |
| `GateVerdict` | ready, needs-revision, critical-gaps |
| `TYPE_STATUS_MAP` | Maps NodeType to its valid status enum |

### System Invariants (from Catalog)

| ID | Rule | Enforcement |
|----|------|-------------|
| INV-001 | Task output must pass through gate before milestone | Assembly-time |
| INV-002 | Constitution must exist before spec tasks execute | Assembly-time |
| INV-003 | validates edges must originate from gate nodes | Assembly-time |
| INV-004 | Maximum 5 passes per workflow invocation | Runtime |
| INV-005 | depends-on edges must form a DAG (no cycles) | Assembly-time |

### External Dependencies

| Dependency | Version | Purpose | Access Pattern |
|------------|---------|---------|----------------|
| Pydantic | >= 2.0 | Entity modeling, validation | Direct import, frozen models |
| NetworkX | >= 3.0 | Graph operations | MultiDiGraph, topological sort, path finding |
| pytest | >= 8.0 | Testing (dev) | Test runner |
| pytest-cov | >= 5.0 | Coverage (dev) | Coverage measurement |

No external services, databases, or APIs. The package is a pure library/CLI tool with no network dependencies.

### CI/CD Configuration

| Job | What It Checks | Enforcement |
|-----|----------------|-------------|
| `test` (Tests & Quality Gates) | Python syntax (brain + legacy validators), shell syntax, all tests pass, 90% coverage floor | Blocks merge |
| `commit-lint` (Conventional Commits) | Commit message format validation on PRs | Blocks merge |

### Pre-commit Hooks

| Hook | Version | Purpose |
|------|---------|---------|
| `conventional-pre-commit` | v4.0.0 | Commit message format (feat, fix, docs, refactor, chore, test, ci) |
| `shellcheck` | v0.10.0.1 | Shell script linting (severity=error) |
| `check-ast` | v5.0.0 | Python AST validity |
| `check-yaml` | v5.0.0 | YAML validity |
| `end-of-file-fixer` | v5.0.0 | Ensures newline at EOF |
| `trailing-whitespace` | v5.0.0 | Removes trailing whitespace |
| `check-added-large-files` | v5.0.0 | Blocks files > 500KB |

### Governance Artifacts

| Artifact | Status | Location |
|----------|--------|----------|
| CLAUDE.md | Present (comprehensive, v3.0.0 synced) | `/CLAUDE.md` |
| Constitution | **Referenced but not yet created** | `.humaninloop/memory/constitution.md` (target) |
| ADRs | 7 records | `docs/decisions/001-007` |
| CONTRIBUTING.md | Present | `/CONTRIBUTING.md` |
| RELEASES.md | Present | `/RELEASES.md` |
| CHANGELOG.md | Present | `/CHANGELOG.md` |
| ROADMAP.md | Present | `/ROADMAP.md` |
| CODEOWNERS | Not present | -- |
| Secret scanning | Not configured | CLAUDE.md notes GAP-003 |

### Plugin Marketplace Structure

| Category | Count | Examples |
|----------|-------|---------|
| Agents | 10 | dag-assembler, devils-advocate, principal-architect, qa-engineer, requirements-analyst, staff-engineer, state-analyst, task-architect, technical-analyst, ui-designer |
| Commands | 7 | audit, implement, plan, setup, specify, tasks, techspec (deprecated) |
| Skills | 27 | analysis-codebase, authoring-constitution, brownfield-constitution, dag-operations, patterns-entity-modeling, strategy-core, syncing-claude-md, etc. |
| Templates | 19 | codebase-analysis-template, constitution-template, spec-template, plan-template, etc. |
| Scripts | 4 | check-prerequisites.sh, common.sh, create-new-feature.sh, setup-plan.sh |
| Catalogs | 1 | specify-catalog.json |

---

## Part 2: Assessment (Judgment)

### Strengths to Preserve

1. **Strict Layer Dependency Rule**: The 5-layer hierarchy (`entities` -> `graph` -> `validators` -> `passes` -> `cli`) is perfectly enforced. Zero upward imports. This is a textbook clean architecture implementation worth codifying as a constitution principle.

2. **Frozen Pydantic Models Everywhere**: Every single Pydantic model uses `model_config = {"frozen": True}`. Combined with `model_validator` for type-status validation and derived field enforcement, this makes the domain model extremely robust against invalid state. The `FrozenEntryError` custom exception prevents writes to frozen history entries.

3. **Structured JSON Output Contract**: All 7 CLI subcommands (validate, sort, assemble, status, record, freeze, catalog-validate) produce machine-parseable JSON with consistent `checks`/`summary` schema. Exit codes are semantically meaningful (0=success, 1=validation failure, 2=runtime error). This is a strong structured output pattern.

4. **Comprehensive Test Suite**: 381 tests at 97% coverage. Tests mirror the source structure 1:1. Includes unit tests, E2E scenario tests, and spec consistency tests. Coverage has a 90% CI floor.

5. **Deterministic Edge Inference**: The `infer_edges()` algorithm deterministically computes graph edges from artifact contracts. Combined with lexicographic topological sort, execution order is reproducible across runs. This is the core "deterministic DAG" promise.

6. **Atomic File Operations**: `save_graph()` uses a write-validate-swap pattern (backup existing, write to temp, validate parse-back, atomic rename) to prevent corruption of the single-file StrategyGraph JSON.

7. **Catalog-Driven Resolution**: The two-tier resolution system (Tier 1: capability tags, Tier 2: semantic description fallback) provides principled node resolution with explicit failure modes for ambiguity.

8. **Pre-commit + CI Double Gate**: Conventional commits are enforced both locally (pre-commit hook) and in CI (commit-lint job). No single point of failure for commit format governance.

### Inconsistencies Found

| Area | Finding | Severity | Location |
|------|---------|----------|----------|
| Constitution reference | CLAUDE.md references `.humaninloop/memory/constitution.md` (v3.0.0) but the file does not exist | medium | `CLAUDE.md` line 7, `.humaninloop/memory/` |
| Package vs marketplace version | Package is v0.1.0 but marketplace is v3.0.0 | low | `__init__.py` vs `marketplace.json` |
| No linting tool configured | No ruff, flake8, pylint, or mypy configured for the Python package | medium | `pyproject.toml`, CI |
| CLI main.py length | `cli/main.py` is 656 lines -- the largest module by far; contains all 7 commands in one file | low | `humaninloop_brain/src/humaninloop_brain/cli/main.py` |
| Inline import in invariants.py | `import networkx as nx` inside function body (line 37) instead of module-level | low | `validators/invariants.py:37` |
| Inline import in lifecycle.py | `from humaninloop_brain.entities.enums import NodeType` inside function body (line 309) | low | `passes/lifecycle.py:309` |
| No type checking | No mypy or pyright configured despite extensive type hints | medium | `pyproject.toml` |

### Essential Floor Status

| Category | Status | Evidence |
|----------|--------|----------|
| Security | partial | Input validation present via Pydantic; no auth needed (CLI tool); secrets from env (`.env` in `.gitignore`); secret scanning NOT configured (GAP-003 per CLAUDE.md) |
| Testing | present | pytest configured; 381 tests pass; 97% coverage; 90% CI floor; pre-commit AST check; CI blocks on test failure |
| Error Handling | present | Custom exceptions (`FrozenEntryError`); structured `ValidationViolation` with code/severity/message; JSON error output with exit codes 0/1/2; Pydantic model validators for domain integrity |
| Observability | partial | StrategyGraph JSON serves as primary workflow observability artifact; all CLI output is JSON parseable by `jq`; NO structured logging library; NO correlation IDs in library code; NO log levels |

#### Security Assessment Details

- **Auth at boundaries**: not-applicable - This is a CLI tool/library, not a service. No network boundaries exist. Authentication is not relevant.
- **Secrets from env**: present - `.env` and `.env.*.local` are in `.gitignore`. No hardcoded secrets detected in source code. No secret scanning in CI (documented as GAP-003).
- **Input validation**: present - Comprehensive Pydantic model validation with `model_validator` decorators. Type-status maps enforce valid combinations. CLI validates all inputs (outcomes, node existence, frozen state) before operations. Edge constraint validation checks source/target node types.

#### Testing Assessment Details

- **Test framework configured**: present - pytest >= 8.0 in dev dependencies; `pyproject.toml` `[tool.pytest.ini_options]` configured; `[tool.coverage.*]` configured.
- **Test files present**: present - 27 test files across 4 test directories (`test_cli/`, `test_entities/`, `test_graph/`, `test_validators/`, `test_passes/`), totaling 5,241 lines.
- **CI runs tests**: present - GitHub Actions CI runs `uv run pytest --cov --cov-report=term --tb=short -q` with 90% coverage floor enforced.

#### Error Handling Assessment Details

- **Explicit error types**: present - `FrozenEntryError` custom exception; `ValidationViolation` with typed codes (CYCLE, DUPLICATE_NODE_ID, DANGLING_EDGE_SOURCE, INV-001 through INV-005, UNSATISFIED_CONTRACT, etc.); `ValueError` with descriptive messages for domain violations.
- **Context preservation**: present - Error messages include node IDs, edge IDs, status values, and path information. `ValidationViolation` carries `node_id` and `edge_id` for precise location. CLI propagates error context in JSON output.
- **Appropriate status codes**: present - CLI uses exit code 0 (success), 1 (validation/user error), 2 (runtime exception). JSON output includes `"status"` field with values `"valid"`, `"invalid"`, `"success"`, `"error"`, `"resolution_failed"`.

#### Observability Assessment Details

- **Structured logging**: absent - No logging library imported anywhere in source code. No `logging`, `structlog`, or similar. CLI output is structured JSON, but there is no internal logging for debugging library operations.
- **Correlation IDs**: absent - No correlation ID, request ID, or trace ID patterns in the library code. The StrategyGraph has `id` and `workflow_id` fields that serve as workflow-level identifiers, but these are domain objects, not observability primitives.
- **No PII in logs**: not-applicable - No logging exists, so no PII risk in logs. The domain model does not handle user PII.

### Recommended Constitution Focus

Based on this analysis, the constitution should:

1. **Codify the layer dependency rule as a NON-NEGOTIABLE principle** -- This is the project's architectural backbone. It is currently documented in CLAUDE.md but has no automated enforcement (no import linter in CI). The constitution should require CI enforcement.

2. **Codify frozen Pydantic models as a NON-NEGOTIABLE principle** -- Every entity uses `frozen: True` and the `FrozenEntryError` pattern. This is central to the deterministic guarantee. Constitution should mandate it for all new entities.

3. **Codify the structured JSON output contract** -- The `checks`/`summary` schema and exit code conventions are consistent across all CLI commands. This is a strong emergent pattern worth preserving.

4. **Codify the deterministic infrastructure principle** -- The two-tier system (Tier 1 strict graph-algorithmic, Tier 2 heuristic-deterministic) with catalog-driven assembly is the core architectural differentiator.

5. **Add a static analysis / type checking requirement** -- The codebase uses extensive type hints but has no mypy/pyright/ruff configured. This is a gap that should be addressed in the constitution with a roadmap item.

6. **Add secret scanning as a security requirement** -- GAP-003 from CLAUDE.md. No `git secrets --scan` or equivalent in CI.

7. **Address observability gap** -- While the CLI tool nature reduces observability needs, the constitution should establish minimum observability requirements (structured logging for debug scenarios, at minimum).

8. **Preserve the existing quality gates** -- The 90% coverage floor, conventional commits double gate, and syntax checks are all worth codifying as constitution principles.

---

## Appendix: Source Code Metrics

### Module Size Summary

| Module | Lines | Statements | Coverage |
|--------|-------|------------|----------|
| `cli/main.py` | 656 | 307 | 95% |
| `passes/lifecycle.py` | 483 | 181 | 98% |
| `validators/structural.py` | 211 | 65 | 94% |
| `validators/invariants.py` | 155 | 56 | 95% |
| `entities/catalog.py` | 148 | 87 | 100% |
| `graph/inference.py` | 131 | 50 | 100% |
| `entities/nodes.py` | 112 | 57 | 100% |
| `entities/enums.py` | 98 | 45 | 100% |
| `graph/loader.py` | 54 | 22 | 100% |
| `validators/contracts.py` | 50 | 18 | 100% |
| `graph/views.py` | 44 | 17 | 100% |
| `entities/validation.py` | 39 | 23 | 100% |
| `entities/dag_pass.py` | 37 | 18 | 100% |
| `graph/guard.py` | 36 | 14 | 100% |
| `entities/strategy_graph.py` | 28 | 16 | 100% |
| `entities/edges.py` | 19 | 11 | 100% |
| `graph/sort.py` | 19 | 8 | 100% |
| **TOTAL** | **2,394** | **1,004** | **97%** |

### Test Suite Summary

| Test Directory | Files | Lines | Focus |
|----------------|-------|-------|-------|
| `test_cli/` | 4 | 2,304 | CLI commands, E2E scenarios, spec consistency |
| `test_entities/` | 7 | 1,110 | Pydantic model validation, enum coverage |
| `test_graph/` | 5 | 622 | Graph loading, inference, sorting, guards, views |
| `test_passes/` | 1 | 610 | Lifecycle operations (create, add, update, freeze) |
| `test_validators/` | 3 | 595 | Structural, contract, and invariant validation |
| **TOTAL** | **27** | **5,241** | **381 tests** |

### Detection Method

| Aspect | Method Used |
|--------|-------------|
| Tech Stack | `pyproject.toml` inspection + CLAUDE.md cross-reference |
| Architecture | Import analysis (grep for `from humaninloop_brain` across all source files) |
| Entities | Pydantic `BaseModel` subclass inventory |
| Conventions | File sampling across all 5 layers |
| Essential Floor | Targeted grep for security/logging/error patterns + test execution |
| Layer Compliance | Full import graph verification |
