# Codebase Analysis

> Generated: 2026-02-19T03:35:00Z
> Mode: setup-brownfield
> Status: draft

---

## Part 1: Inventory (Factual)

### Project Identity

| Aspect | Value | Source |
|--------|-------|--------|
| Name | HumanInLoop (human-in-loop) | `.claude-plugin/marketplace.json` |
| Primary Language | Python >= 3.11 | `humaninloop_brain/pyproject.toml` |
| Entity Modeling | Pydantic >= 2.0 (frozen models) | `humaninloop_brain/pyproject.toml` |
| Graph Operations | NetworkX >= 3.0 | `humaninloop_brain/pyproject.toml` |
| Package Manager | uv | `humaninloop_brain/uv.lock` |
| Build System | hatchling (PEP 517) | `humaninloop_brain/pyproject.toml` |
| Test Framework | pytest >= 8.0, pytest-cov >= 5.0 | `humaninloop_brain/pyproject.toml` |
| Entry Points | `hil-dag` CLI (7 subcommands) | `pyproject.toml [project.scripts]` |
| Plugin Version | 2.2.0 | `plugins/humaninloop/.claude-plugin/plugin.json` |
| Marketplace Version | 2.1.2 | `.claude-plugin/marketplace.json` |
| humaninloop_brain Version | 0.1.0 | `humaninloop_brain/pyproject.toml` |
| CI/CD | GitHub Actions | `.github/workflows/ci.yml` |

### Directory Structure

```
human-in-loop/
├── .claude-plugin/              # Marketplace-level manifest (marketplace.json)
├── .github/
│   └── workflows/
│       └── ci.yml               # Tests, coverage floor, ratchet, commit lint
├── .humaninloop/
│   └── memory/                  # Constitution, analysis, roadmap, context
├── docs/
│   ├── architecture/            # 7 synthesis docs + v3/ subdirectory (4 docs)
│   ├── decisions/               # 7 ADRs (001-007) + README.md index
│   ├── images/                  # Documentation images
│   └── internal/                # Strategy, feedback, podcast prep
├── humaninloop_brain/           # PRIMARY PYTHON PACKAGE
│   ├── catalogs/                # Workflow node catalogs (JSON)
│   │   └── specify-catalog.json
│   ├── src/humaninloop_brain/
│   │   ├── cli/                 # hil-dag CLI entry point (main.py)
│   │   ├── entities/            # Pydantic models (7 modules)
│   │   ├── graph/               # NetworkX operations (5 modules)
│   │   ├── passes/              # Pass lifecycle (1 module)
│   │   └── validators/          # Structural validation (3 modules)
│   ├── tests/                   # 381 tests across 5 suites
│   │   ├── conftest.py          # Shared fixtures
│   │   ├── fixtures/            # 8 JSON test fixtures
│   │   ├── test_cli/            # CLI integration tests (4 files)
│   │   ├── test_entities/       # Entity model tests (7 files)
│   │   ├── test_graph/          # Graph operation tests (5 files)
│   │   ├── test_passes/         # Lifecycle tests (1 file)
│   │   └── test_validators/     # Validator tests (3 files)
│   ├── pyproject.toml           # Package config, dependencies, tool config
│   ├── .coverage-baseline       # Ratchet baseline: 98%
│   └── uv.lock                  # Lockfile
├── plugins/
│   └── humaninloop/             # Claude Code plugin
│       ├── .claude-plugin/      # Plugin manifest (plugin.json)
│       ├── agents/              # 10 agent definitions (.md)
│       ├── catalogs/            # Workflow catalogs (symlink target)
│       │   └── specify-catalog.json
│       ├── commands/            # 7 slash commands (.md)
│       ├── scripts/             # 4 shell utility scripts
│       ├── skills/              # 25 skills (SKILL.md + references)
│       │   └── dag-operations/scripts/  # 7 dag-*.sh wrappers
│       └── templates/           # 21 workflow templates
├── CHANGELOG.md                 # Release history
├── CLAUDE.md                    # AI agent instructions (synced to constitution v2.0.0)
├── CONTRIBUTING.md              # Contribution guidelines
├── RELEASES.md                  # Release process
├── ROADMAP.md                   # Product roadmap
├── .pre-commit-config.yaml      # Conventional commits, shellcheck, ast check
└── .gitignore                   # Excludes .env, *.pem, venv, __pycache__
```

### Detected Patterns

#### Architecture Pattern

| Pattern | Evidence |
|---------|----------|
| DAG-first infrastructure | `humaninloop_brain/` package with entities/graph/validators/passes/cli layers; ADR-007 |
| V3 single-DAG iteration model | `StrategyGraph` entity accumulates nodes/edges across passes; `docs/architecture/v3/` |
| Three-tier agent model | Supervisor -> State Analyst + DAG Assembler -> Specialist agents; `plugins/humaninloop/agents/` |
| Layered Python package | entities -> graph -> validators -> passes -> cli (strict dependency flow) |
| Plugin marketplace | `.claude-plugin/marketplace.json`, `plugins/humaninloop/.claude-plugin/plugin.json` |
| Skill-augmented agents | 25 skills in 9 categories, loaded into agent context; RFC 2119 invocation keywords |
| Catalog-driven node assembly | `catalogs/specify-catalog.json` defines available nodes; `hil-dag assemble` selects from catalog |

#### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Skill directories | kebab-case with category prefix | `authoring-constitution`, `patterns-api-contracts` |
| Agent files | kebab-case `.md` | `devils-advocate.md`, `state-analyst.md` |
| Command files | kebab-case `.md` | `setup.md`, `specify.md`, `techspec.md` |
| Python modules | snake_case `.py` | `dag_pass.py`, `strategy_graph.py`, `lifecycle.py` |
| Python classes | PascalCase | `GraphNode`, `StrategyGraph`, `NodeCatalog` |
| Python functions | snake_case | `validate_structure`, `execution_order`, `freeze_current_pass` |
| Test files | `test_` prefix in `test_<module>/` dirs | `test_structural.py`, `test_lifecycle.py` |
| Test classes | `Test` prefix, PascalCase descriptive | `TestStep10EntryLevelImmutability` |
| Shell scripts | kebab-case `.sh` | `dag-validate.sh`, `check-prerequisites.sh` |
| ADR files | `NNN-descriptive-name.md` | `007-dag-first-infrastructure.md` |
| Template files | kebab-case `-template.md` | `constitution-template.md`, `spec-template.md` |
| Commit messages | Conventional Commits with scope | `feat(brain): add StrategyGraph model` |
| Enum values | snake_case (Python) / kebab-case (JSON) | `depends_on` / `"depends-on"` |
| Edge IDs | kebab-case pattern | `inferred-depends-on-{source}-{target}` |
| Violation codes | UPPER_SNAKE or INV-NNN | `DUPLICATE_NODE_ID`, `INV-001` |

#### Error Handling Pattern

| Pattern | Evidence |
|---------|----------|
| Structured JSON output (CLI) | All 7 `hil-dag` subcommands output JSON via `_output()` helper |
| `validation_result_to_output()` | Translates `ValidationResult` to `checks`/`summary` JSON schema |
| Exit code convention | 0=success, 1=validation failure, 2=unexpected error |
| Custom exception: `FrozenEntryError` | Raised on writes to frozen history entries (`passes/lifecycle.py`) |
| Pydantic `ValidationError` | Raised by model validators on constraint violations |
| `ValidationViolation` structured errors | `code`, `severity`, `message`, optional `node_id`/`edge_id` |
| 10-step structural validation | `validate_structure()` collects all violations before returning |
| Error context includes IDs | Node IDs, edge IDs, pass numbers, constraint details in messages |

#### Test Pattern

| Aspect | Value |
|--------|-------|
| Framework | pytest 8.x with pytest-cov 5.x |
| Location | `humaninloop_brain/tests/` |
| Naming | `test_*.py` files in `test_<module>/` directories |
| Coverage Config | `pyproject.toml` (`[tool.coverage.run]`, `[tool.coverage.report]`) |
| Fixture Pattern | JSON fixtures in `tests/fixtures/` (8 files); `conftest.py` shared fixtures |
| Test Types | Unit, subprocess integration (`subprocess.run`), E2E scenarios |
| Current Results | **381 tests**, **97% coverage** (1004 statements, 26 misses) |
| Coverage Baseline | 98% (`.coverage-baseline` file) |
| CI Enforcement | 90% floor (blocking), ratchet against baseline |

### Domain Entities

#### humaninloop_brain Pydantic Entities (v3 Architecture)

| Entity | Module | Key Fields | Notes |
|--------|--------|------------|-------|
| `NodeType` (enum) | enums.py | task, gate, decision, milestone | 4 node types |
| `EdgeType` (enum) | enums.py | depends_on, produces, validates, constrained_by, informed_by, triggered_by | 6 edge types (triggered_by added in v3) |
| `PassOutcome` (enum) | enums.py | completed, halted | |
| `TaskStatus` (enum) | enums.py | pending, in-progress, completed, skipped, halted | |
| `GateLifecycleStatus` (enum) | enums.py | pending, in-progress, completed, passed, failed | Renamed from GateStatus in v3 |
| `GateVerdict` (enum) | enums.py | ready, needs-revision, critical-gaps | New in v3 |
| `DecisionStatus` (enum) | enums.py | pending, decided | |
| `MilestoneStatus` (enum) | enums.py | pending, achieved | |
| `InvariantEnforcement` (enum) | enums.py | assembly-time, runtime | |
| `InvariantSeverity` (enum) | enums.py | error, warning | |
| `TYPE_STATUS_MAP` | enums.py | Maps NodeType -> status enum | Central type-status coherence |
| `GraphNode` | nodes.py | id, type, name, description, status, contract, agent, history, verdict, last_active_pass | v3: history[], verdict, last_active_pass derived from latest entry |
| `NodeHistoryEntry` | nodes.py | pass_number (alias "pass"), status, verdict, frozen, evidence, trace | New in v3: per-pass history |
| `NodeContract` | nodes.py | consumes, produces | Artifact dependency contracts |
| `ArtifactConsumption` | nodes.py | artifact, required, note | |
| `EvidenceAttachment` | nodes.py | id, type, description, reference | |
| `Edge` | edges.py | id, source, target, type, source_pass, target_pass, reason | v3: source_pass/target_pass for triggered_by |
| `StrategyGraph` | strategy_graph.py | id, workflow_id, schema_version, current_pass, status, passes, nodes, edges | New in v3: replaces per-pass DAGPass |
| `PassEntry` | dag_pass.py | pass_number (alias "pass"), outcome, detail, created_at, completed_at, frozen | v3: lightweight pass metadata |
| `ExecutionTraceEntry` | dag_pass.py | node_id, started_at, completed_at, verdict, agent_report_summary, artifacts_produced | |
| `CatalogNodeDefinition` | catalog.py | node_id, type, name, description, agent_type, agent, skill, contract, valid_statuses, verdict_field, verdict_values, capabilities, carry_forward, gate_type | v3: capabilities, carry_forward, gate_type |
| `EdgeConstraint` | catalog.py | valid_sources, valid_targets, note | |
| `SystemInvariant` | catalog.py | id, rule, enforcement, severity | |
| `NodeCatalog` | catalog.py | catalog_version, workflow, nodes, edge_constraints, invariants | Methods: get_node, resolve_by_capabilities, resolve_by_description |
| `ValidationResult` | validation.py | valid, phase, violations | Properties: has_errors, error_count, warning_count |
| `ValidationViolation` | validation.py | code, severity, message, node_id, edge_id | |

**Entity Count**: 11 enums, 14 model classes = 25 total entity definitions across 7 modules.

#### Plugin Entities

| Entity Type | Count | Items |
|-------------|-------|-------|
| Agents | 10 | dag-assembler, devils-advocate, plan-architect, principal-architect, requirements-analyst, state-analyst, task-architect, technical-analyst, testing-agent, ui-designer |
| Commands | 7 | audit, implement, plan, setup, specify, tasks, techspec |
| Skills | 25 | 9 categories (analysis-4, authoring-6, brownfield-1, dag-1, patterns-6, syncing-1, testing-1, using-2, validation-3) |
| Templates | 21 | Report, context, and workflow templates |
| Shell Scripts (plugin-level) | 4 | check-prerequisites.sh, common.sh, create-new-feature.sh, setup-plan.sh |
| Shell Scripts (DAG ops) | 7 | dag-assemble.sh, dag-catalog-validate.sh, dag-freeze.sh, dag-record.sh, dag-sort.sh, dag-status.sh, dag-validate.sh |
| Workflow Catalogs | 1 | specify-catalog.json (13 node definitions) |

### External Dependencies

| Dependency | Version | Purpose | Location |
|------------|---------|---------|----------|
| Pydantic | >= 2.0 | Entity model validation, frozen immutability | `humaninloop_brain/pyproject.toml` |
| NetworkX | >= 3.0 | Graph operations, topological sort, cycle detection | `humaninloop_brain/pyproject.toml` |
| pytest | >= 8.0 (dev) | Test framework | `humaninloop_brain/pyproject.toml` |
| pytest-cov | >= 5.0 (dev) | Coverage measurement | `humaninloop_brain/pyproject.toml` |
| gh CLI | N/A | GitHub operations | `CLAUDE.md` |
| Claude Code | N/A | Plugin runtime, agent dispatch | Plugin system |
| conventional-pre-commit | v4.0.0 | Commit message validation | `.pre-commit-config.yaml` |
| shellcheck-py | v0.10.0.1 | Shell script linting | `.pre-commit-config.yaml` |

### Governance Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Constitution | `.humaninloop/memory/constitution.md` | v2.0.0, ratified 2026-02-18; user requests complete rewrite |
| CLAUDE.md | `CLAUDE.md` | Synced with constitution v2.0.0 |
| CI/CD | `.github/workflows/ci.yml` | Present: tests, coverage floor (90%), ratchet (98%), commit lint |
| CONTRIBUTING.md | `CONTRIBUTING.md` | Present |
| RELEASES.md | `RELEASES.md` | Present |
| ROADMAP.md | `ROADMAP.md` | Present |
| CHANGELOG.md | `CHANGELOG.md` | Present, comprehensive |
| ADR Index | `docs/decisions/README.md` | Current, 7 ADRs indexed |
| Pre-commit hooks | `.pre-commit-config.yaml` | Conventional commits, shellcheck, ast, yaml, whitespace |
| Evolution Roadmap | `.humaninloop/memory/evolution-roadmap.md` | Exists from v1; needs refresh |
| CODEOWNERS | N/A | Absent |
| Exception Registry | `docs/constitution-exceptions.md` | Absent (not yet needed) |

### Source Code Metrics

| Metric | Value |
|--------|-------|
| Python source lines (humaninloop_brain/src) | 2,394 lines across 22 modules |
| Python test lines | Not measured (large; 381 tests) |
| Test fixtures | 8 JSON files |
| Coverage statements | 1,004 |
| Coverage misses | 26 (in lifecycle.py, invariants.py, structural.py) |
| CLI subcommands | 7 (validate, sort, assemble, status, record, freeze, catalog-validate) |

---

## Part 2: Assessment (Judgment)

### Strengths to Preserve

1. **Exceptional test coverage with CI enforcement**: 381 tests at 97% coverage with a 90% blocking CI floor and 98% ratchet baseline. Tests span unit, subprocess integration, and E2E levels with JSON fixtures for DAG scenario testing. The CI pipeline (`.github/workflows/ci.yml`) runs tests, coverage floor, ratchet, Python syntax, shell syntax, and commit lint on every push/PR. This is a model testing infrastructure.

2. **V3 single-DAG architecture with immutable history**: The `StrategyGraph` model accumulates nodes and edges across passes with per-node `NodeHistoryEntry` tracking. Frozen entries prevent mutation of completed passes via `FrozenEntryError`. This design provides workflow-level observability through the DAG JSON artifact itself, eliminating the need for separate logging infrastructure.

3. **Catalog-driven assembly with deterministic edge inference**: Node definitions live in JSON catalogs with artifact contracts (`consumes`/`produces`). `infer_edges()` automatically creates `depends_on`, `produces`, `validates`, and `informed_by` edges based on contract analysis. The `resolve_by_capabilities` and `resolve_by_description` methods provide two-tier node resolution from intent to catalog entry.

4. **10-step structural validation with 5 system invariants**: `validate_structure()` performs comprehensive validation (unique IDs, edge references, type-status, self-loops, duplicates, edge constraints, acyclicity, contracts, invariants, entry immutability). INV-001 through INV-005 enforce domain invariants at assembly time. Violations use structured `ValidationViolation` objects with codes, severity, and entity IDs.

5. **Pydantic frozen models with type-status coherence**: Every entity uses `model_config = {"frozen": True}`. The `TYPE_STATUS_MAP` and `validate_type_status` model validator ensure a task node cannot have gate statuses, a milestone cannot be "in-progress", etc. Status updates create new model instances via `model_copy()`.

6. **Consistent structured JSON output**: All CLI subcommands produce JSON via `_output()` helper. Validation results use `validation_result_to_output()` for the `checks`/`summary` schema. Exit codes follow 0/1/2 convention consistently.

7. **Strong commit discipline with CI enforcement**: Conventional commits validated by pre-commit hook (conventional-pre-commit v4.0.0) and CI job (`commit-lint`). Last 30+ commits follow `type(scope): description` format.

8. **Comprehensive ADR discipline**: 7 ADRs with Context/Decision/Rationale/Consequences structure. ADR-007 (DAG-First Infrastructure) documents the core architectural decision with clear rationale.

9. **Clean layer separation in humaninloop_brain**: Entities have no import from graph/validators/passes/cli. Graph imports only from entities. Validators import from entities and graph. Passes import from entities and graph. CLI imports from all layers. No circular dependencies.

### Inconsistencies Found

| Area | Finding | Severity | Location |
|------|---------|----------|----------|
| V2 constitution vs v3 codebase | Constitution v2.0.0 references v2-era entity names (DAGPass, HistoryContext, HistoryPass, GateStatus) that no longer exist | high | `.humaninloop/memory/constitution.md` |
| Stale entity counts | Constitution says "190 tests, 98% coverage" but current state is 381 tests, 97% coverage | medium | Constitution Principle II, Quality Gates |
| Constitution says 6 entity modules | Actually 7 modules (strategy_graph.py added in v3) | medium | Constitution Principle X |
| Constitution says 8 enum types | Actually 11 enums (GateVerdict, GateLifecycleStatus replace GateStatus; TYPE_STATUS_MAP added) | medium | Constitution Principle X |
| GAP-001 resolved | Constitution marks CI as "GAP-001: not yet configured" but CI now exists at `.github/workflows/ci.yml` | medium | Constitution Quality Gates, Principle II |
| Plugin validators count | Constitution says 5 legacy validators; actually 5 Python scripts + 1 non-validator (`check-artifacts.py`) | low | Constitution Principle V |
| Agent count | Constitution says 8 agents; actually 10 (state-analyst and dag-assembler added in v3) | low | Codebase-analysis entity catalog |
| specs/ directory missing | CLAUDE.md references `specs/` directory but it does not exist | low | `CLAUDE.md` |
| hil-dag create reference | Constitution references `hil-dag create` subcommand; actual v3 CLI has no standalone `create` (create is part of `assemble --workflow`) | low | Constitution Principle IV |
| Coverage dip | Coverage baseline is 98% but current measured coverage is 97%; ratchet would fail in CI | medium | `.coverage-baseline` vs actual |

### Essential Floor Status

| Category | Status | Evidence |
|----------|--------|----------|
| Security | partial | `.gitignore` covers `.env`, `*.pem`; no hardcoded secrets found; no secret scanning in CI |
| Testing | present | 381 tests, 97% coverage; CI with 90% floor + 98% ratchet; pre-commit hooks |
| Error Handling | present | Structured JSON output; 0/1/2 exit codes; FrozenEntryError; ValidationViolation with codes |
| Observability | partial | JSON to stdout; DAG pass JSON as workflow artifact; no structured logging; no correlation IDs |

#### Security Assessment Details

- **Auth at boundaries**: N/A -- Plugin marketplace and CLI tooling. Authentication handled by Claude Code runtime. Appropriate for project type.
- **Secrets from env**: partial -- `.gitignore` excludes `.env`, `.env.local`, `.env.*.local`, `*.pem`, `credentials`, `secrets`. No `.env.example` exists. No `git secrets` or secret scanning configured in CI.
- **Input validation**: present -- Pydantic model validators enforce all input constraints at construction time. `argparse` validates CLI arguments. Shell scripts validate argument counts. `TYPE_STATUS_MAP` prevents invalid type-status combinations.
- **Secret scanning**: absent -- Not present in CI pipeline. Pre-commit hooks do not include secret scanning. This was GAP-003 in v2 constitution and remains unresolved.

#### Testing Assessment Details

- **Test framework configured**: present -- pytest 8.x + pytest-cov 5.x in `pyproject.toml`. Coverage configured with `[tool.coverage.run]` and `[tool.coverage.report]` sections.
- **Test files present**: present -- 381 tests in 20 files across 5 test directories. 8 JSON fixtures for DAG scenario testing (normal, skip-enrichment, with-research, with-clarification, invalid-cycle, invalid-contract, invalid-endpoint, specify-catalog).
- **CI runs tests**: present -- `.github/workflows/ci.yml` runs on push to main and all PRs. Jobs: tests with coverage, Python syntax check, legacy validator syntax check, shell syntax check, coverage floor (90%), coverage ratchet (98% baseline), conventional commit lint.
- **Plugin validator tests**: absent -- 5 Python validator scripts in `plugins/humaninloop/skills/*/scripts/` have no test files. These are deprecated.

#### Error Handling Assessment Details

- **Explicit error types**: present -- `FrozenEntryError` for immutability violations. `ValueError` with descriptive messages for constraint violations. `ValidationViolation` for structured error reporting with codes and severity.
- **Context preservation**: present -- Error messages include node IDs, edge IDs, pass numbers, violation codes, and constraint details. `ValidationViolation` objects carry `node_id` and `edge_id` for traceability.
- **Appropriate exit codes**: present -- CLI consistently uses 0=success, 1=validation/expected failure, 2=unexpected error (caught in `main()` exception handler).

#### Observability Assessment Details

- **Structured output**: present -- All 7 CLI subcommands produce JSON to stdout via `_output()` helper. `validation_result_to_output()` normalizes validation results to `checks`/`summary` schema. All output parseable by `jq`.
- **DAG pass JSON as artifact**: present -- `StrategyGraph` serializes to JSON with `save_graph()` (atomic write-validate-swap). Contains node history, edge topology, pass metadata, evidence, and execution traces. This is the primary workflow observability artifact.
- **Correlation IDs**: absent -- No request/correlation ID mechanism. Evidence attachments use auto-generated IDs (`EV-{node}-{pass}-{seq}`) which provide some traceability.
- **Structured logging**: absent -- No logging framework (no `import logging` anywhere in codebase). All output is structured JSON to stdout. For a CLI tool consumed by agents, this is appropriate -- stdout JSON serves the same purpose as structured logs.
- **No PII in output**: present -- Output contains only structural data (node IDs, edge IDs, violation codes, artifact names).

### Recommended Constitution Focus

Based on this analysis, the new constitution (v3.0.0) should:

1. **Make humaninloop_brain the primary subject**: The v2 constitution treats the Python package as one of two codebases alongside "plugin validators." The v3 constitution should treat `humaninloop_brain` as the primary codebase and the plugin structure (agents, commands, skills) as the consumption layer.

2. **Reflect v3 architecture accurately**: Update all entity references to v3 names (StrategyGraph not DAGPass, GateLifecycleStatus not GateStatus, NodeHistoryEntry, PassEntry, etc.). Update counts (11 enums, 14 models, 381 tests, 7 modules, 10 agents).

3. **Remove resolved gaps**: GAP-001 (CI) is resolved -- `.github/workflows/ci.yml` exists and enforces tests, coverage floor, ratchet, syntax, and commit lint. Remove the GAP-001 annotations throughout.

4. **Codify the layer dependency rule**: The clean import hierarchy (entities -> graph -> validators -> passes -> cli) is an emergent pattern worth enforcing. No module should import "upward" in this hierarchy.

5. **Add v3-specific principles**: Catalog-driven assembly, single-DAG iteration model, and the three-tier agent model are new architectural patterns that emerged from the v3 redesign and should be governance targets.

6. **Preserve and update the testing principle**: Current state is 381 tests at 97% coverage with CI enforcement. The 90% floor and ratchet mechanism are already in CI. Update the counts and verify the baseline file.

7. **Maintain essential floor gaps**: Secret scanning (GAP-003) remains unresolved. This should be preserved as a gap in the new constitution.

8. **Update the structured output principle**: The `hil-dag` CLI now has 7 subcommands (validate, sort, assemble, status, record, freeze, catalog-validate) instead of the previously listed set. The `create` subcommand no longer exists as standalone.

9. **Acknowledge the plugin marketplace context**: Skills, agents, commands, templates, and catalogs form the consumption layer for `humaninloop_brain` deterministic infrastructure. The constitution should govern the boundary between these layers.

---

## Appendix: Detection Method

| Aspect | Method Used |
|--------|-------------|
| Tech Stack | Manual inspection of `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml` |
| Architecture | Source code reading of all 22 Python modules; ADR-007 review; v3 design doc review |
| Entities | Exhaustive Pydantic model inspection across all 7 entity modules |
| Graph Operations | Reading of all 5 graph modules (loader, views, sort, guard, inference) |
| Validators | Reading of all 3 validator modules (structural, contracts, invariants) |
| Lifecycle | Reading of passes/lifecycle.py (483 lines, 13 public functions) |
| CLI | Reading of cli/main.py (657 lines, 7 subcommand handlers + parser) |
| Tests | `uv run pytest --cov --cov-report=term --tb=short -q` (381 passed, 97% coverage, 6.07s) |
| CI/CD | Reading `.github/workflows/ci.yml` (113 lines, 2 jobs) |
| Plugin Structure | `find` traversal of `plugins/` directory tree (107 files) |
| Conventions | Commit history analysis (`git log --oneline -30`), file naming inspection |
| Essential Floor | Grep for secrets, logging imports, error patterns; `.gitignore` inspection |
| Governance | Reading of constitution v2.0.0, CLAUDE.md, CONTRIBUTING.md, all 7 ADRs |
