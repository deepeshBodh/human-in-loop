# Codebase Analysis

> Generated: 2026-02-18T18:50:00Z
> Mode: setup-brownfield
> Status: draft

---

## Part 1: Inventory (Factual)

### Project Identity

| Aspect | Value | Source |
|--------|-------|--------|
| Name | HumanInLoop Plugin Marketplace | `.claude-plugin/marketplace.json` |
| Primary Languages | Markdown, Python 3.12, Bash | `pyproject.toml`, file inspection |
| Framework | Claude Code Plugin System | `plugin.json` |
| Package Manager | uv (humaninloop_brain), none (plugin) | `humaninloop_brain/uv.lock` |
| Entry Points | `hil-dag` CLI, 7 slash commands, 5 Python validators | `pyproject.toml`, `commands/`, `scripts/` |
| Plugin Version | 2.0.0 | `plugin.json` |
| Marketplace Version | 2.0.0 | `marketplace.json` |
| humaninloop_brain Version | 0.1.0 | `pyproject.toml` |

### Directory Structure

```
human-in-loop/
├── .claude-plugin/           # Marketplace-level manifest
│   └── marketplace.json
├── .humaninloop/             # Governance artifacts
│   └── memory/               # Constitution, analysis, roadmap
├── docs/                     # Documentation
│   ├── architecture/         # 7 DAG synthesis documents
│   ├── decisions/            # 7 ADRs (001-007)
│   ├── images/               # Documentation images
│   └── internal/             # Strategy, feedback, podcast prep
├── humaninloop_brain/        # Python DAG infrastructure package
│   ├── catalogs/             # Workflow node catalogs (JSON)
│   ├── src/humaninloop_brain/
│   │   ├── cli/              # hil-dag CLI (main.py)
│   │   ├── entities/         # Pydantic models (6 modules)
│   │   ├── graph/            # NetworkX operations (5 modules)
│   │   ├── passes/           # Pass lifecycle (1 module)
│   │   └── validators/       # Structural validation (3 modules)
│   └── tests/                # 190 tests across 5 suites
├── plugins/                  # Plugin directory
│   └── humaninloop/          # Primary plugin
│       ├── .claude-plugin/   # Plugin manifest
│       ├── agents/           # 8 agent definitions
│       ├── commands/         # 7 slash commands
│       ├── scripts/          # 4 shell scripts
│       ├── skills/           # 25 skills
│       └── templates/        # 21 templates
├── CHANGELOG.md              # Release history
├── CLAUDE.md                 # AI agent instructions
├── CONTRIBUTING.md           # Contribution guidelines
├── RELEASES.md               # Release process
└── ROADMAP.md                # Product roadmap
```

### Detected Patterns

#### Architecture Pattern

| Pattern | Evidence |
|---------|----------|
| Plugin-based marketplace | `plugins/humaninloop/`, `.claude-plugin/marketplace.json`, `plugin.json` |
| Multi-agent workflow | 8 agents in `agents/`, 7 commands as orchestrators in `commands/` |
| Skill-augmented agents | 25 skills in `skills/`, referenced by agents via RFC 2119 keywords |
| DAG-first infrastructure | `humaninloop_brain/` package, ADR-007, 7 architecture synthesis docs |
| Layered Python package | `entities/`, `graph/`, `validators/`, `passes/`, `cli/` layers |

#### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Skill directories | kebab-case with category prefix | `authoring-constitution`, `patterns-api-contracts` |
| Agent files | kebab-case `.md` | `devils-advocate.md`, `plan-architect.md` |
| Command files | kebab-case `.md` | `setup.md`, `specify.md`, `techspec.md` |
| Python modules | snake_case `.py` | `dag_pass.py`, `lifecycle.py` |
| Python classes | PascalCase | `GraphNode`, `NodeCatalog`, `DAGPass` |
| Python functions | snake_case | `validate_structure`, `execution_order` |
| Test files | `test_` prefix in `test_<module>/` dirs | `test_structural.py`, `test_lifecycle.py` |
| Shell scripts | kebab-case `.sh` | `dag-validate.sh`, `check-prerequisites.sh` |
| ADR files | `NNN-descriptive-name.md` | `007-dag-first-infrastructure.md` |
| Template files | kebab-case `-template.md` | `constitution-template.md` |
| Commit messages | Conventional Commits with scope | `feat(humaninloop): add /techspec command` |

#### Error Handling Pattern

| Pattern | Evidence |
|---------|----------|
| Structured JSON output (Python validators) | All 5 plugin validators output `{"checks": [...], "summary": {"passed": N, "failed": M}}` |
| Structured JSON output (hil-dag CLI) | All 7 CLI subcommands output JSON to stdout |
| Exit code convention | 0=success, 1=validation failure, 2=unexpected error (CLI); 0/1 (validators) |
| `set -e` in shell scripts | `check-prerequisites.sh`, all `dag-*.sh` scripts |
| Pydantic validation errors | Model validators raise `ValueError` with descriptive messages |
| Custom exception: FrozenPassError | `lifecycle.py` for immutability enforcement |

#### Test Pattern

| Aspect | Value |
|--------|-------|
| Framework | pytest 8.x |
| Location | `humaninloop_brain/tests/` |
| Naming | `test_*.py` files in `test_<module>/` directories |
| Coverage Config | `pyproject.toml` (`[tool.coverage.run]`) |
| Coverage Tool | pytest-cov 5.x |
| Fixture Pattern | JSON fixtures in `tests/fixtures/` (8 files) |
| Test Types | Unit, integration (subprocess), E2E scenarios |
| Coverage Result | **98%** (190 tests, 609 statements, 13 misses) |

### Entity Catalog

#### Plugin Entities

| Entity Type | Count | Items |
|-------------|-------|-------|
| **Agents** | 8 | devils-advocate, plan-architect, principal-architect, requirements-analyst, task-architect, technical-analyst, testing-agent, ui-designer |
| **Commands** | 7 | audit, implement, plan, setup, specify, tasks, techspec |
| **Skills** | 25 | See skill categories table below |
| **Templates** | 21 | Various report, context, and workflow templates |
| **Python Validators** (plugin) | 5 | validate-requirements.py, validate-user-stories.py, validate-openapi.py, validate-model.py, check-artifacts.py |
| **Shell Scripts** (plugin level) | 4 | check-prerequisites.sh, common.sh, create-new-feature.sh, setup-plan.sh |
| **Shell Scripts** (DAG ops) | 7 | dag-create.sh, dag-assemble.sh, dag-validate.sh, dag-sort.sh, dag-status.sh, dag-freeze.sh, dag-catalog-validate.sh |
| **ADRs** | 7 | 001 Multi-Agent Architecture through 007 DAG-First Infrastructure |
| **Architecture Synthesis Docs** | 7 | dag-first-execution, dag-supervisor-design, dag-json-schema, dag-strategy-skills, dag-specialist-subagents, dag-infrastructure-buildout, dag-infrastructure-implementation-plan |

#### Skill Categories

| Category | Count | Skills |
|----------|-------|--------|
| analysis-* | 4 | codebase, iterative, screenshot, specifications |
| authoring-* | 6 | constitution, design-system, requirements, roadmap, technical-requirements, user-stories |
| brownfield-* | 1 | constitution |
| dag-* | 1 | operations |
| patterns-* | 6 | api-contracts, entity-modeling, flow-mapping, interface-design, technical-decisions, vertical-tdd |
| syncing-* | 1 | claude-md |
| testing-* | 1 | end-user |
| using-* | 2 | git-worktrees, github-issues |
| validation-* | 3 | constitution, plan-artifacts, task-artifacts |

#### humaninloop_brain Pydantic Entities

| Entity | Module | Key Fields |
|--------|--------|------------|
| NodeType (enum) | enums.py | task, gate, decision, milestone |
| EdgeType (enum) | enums.py | depends-on, produces, validates, constrained-by, informed-by |
| PassOutcome (enum) | enums.py | completed, halted |
| TaskStatus (enum) | enums.py | pending, in-progress, completed, skipped, halted |
| GateStatus (enum) | enums.py | pending, in-progress, passed, failed, needs-revision |
| DecisionStatus (enum) | enums.py | pending, decided |
| MilestoneStatus (enum) | enums.py | pending, achieved |
| InvariantEnforcement (enum) | enums.py | assembly-time, runtime |
| InvariantSeverity (enum) | enums.py | error, warning |
| GraphNode | nodes.py | id, type, name, description, status, contract, agent, evidence |
| NodeContract | nodes.py | consumes, produces |
| ArtifactConsumption | nodes.py | artifact, required, note |
| EvidenceAttachment | nodes.py | id, type, description, reference |
| Edge | edges.py | id, source, target, type |
| DAGPass | dag_pass.py | id, workflow_id, pass_number, nodes, edges, outcome, execution_trace, history |
| ExecutionTraceEntry | dag_pass.py | timestamp, node_id, action, details |
| HistoryContext | dag_pass.py | previous_passes, insights |
| HistoryPass | dag_pass.py | pass_number, outcome, summary |
| CatalogNodeDefinition | catalog.py | id, type, name, description, agent, skill, contract, valid_statuses |
| EdgeConstraint | catalog.py | valid_sources, valid_targets, note |
| SystemInvariant | catalog.py | id, rule, enforcement, severity |
| NodeCatalog | catalog.py | catalog_version, workflow, nodes, edge_constraints, invariants |
| ValidationResult | validation.py | valid, phase, violations |
| ValidationViolation | validation.py | code, severity, message, node_id, edge_id |

### External Dependencies

| Dependency | Version | Purpose | Location |
|------------|---------|---------|----------|
| Pydantic | >= 2.0 | Entity model validation | `humaninloop_brain/pyproject.toml` |
| NetworkX | >= 3.0 | Graph operations (DAG) | `humaninloop_brain/pyproject.toml` |
| pytest | >= 8.0 | Test framework (dev) | `humaninloop_brain/pyproject.toml` |
| pytest-cov | >= 5.0 | Test coverage (dev) | `humaninloop_brain/pyproject.toml` |
| gh CLI | N/A | GitHub operations | `CLAUDE.md` |
| Claude Code | N/A | Plugin runtime | Plugin system |

### Governance Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Constitution | `.humaninloop/memory/constitution.md` | v1.0.0, being recreated |
| CLAUDE.md | `CLAUDE.md` | Synced with constitution v1.0.0 |
| CONTRIBUTING.md | `CONTRIBUTING.md` | Present |
| RELEASES.md | `RELEASES.md` | Present |
| ROADMAP.md | `ROADMAP.md` | v2.0.0 |
| CHANGELOG.md | `CHANGELOG.md` | Present, comprehensive |
| ADR Index | `docs/decisions/README.md` | Current, 7 ADRs indexed |
| Evolution Roadmap | `.humaninloop/memory/evolution-roadmap.md` | v1.0.0 (stale) |
| CODEOWNERS | N/A | **Absent** |
| CI/CD Workflows | `.github/workflows/` | **Absent** |
| Exception Registry | `docs/constitution-exceptions.md` | **Absent** (not yet needed) |

---

## Part 2: Assessment (Judgment)

### Strengths to Preserve

1. **Consistent structured output pattern**: All 5 plugin Python validators and all 7 hil-dag CLI subcommands follow the same JSON output structure (`checks`, `summary`, `issues`). This enables programmatic consumption, CI integration, and compositional tooling. The CLI explicitly names the function `validation_result_to_output()` showing deliberate compliance with the constitution pattern.

2. **Exceptional test coverage on humaninloop_brain**: 190 tests with 98% coverage across 5 test suites (entities: 81 tests, graph: 32 tests, validators: 30 tests, passes: 17 tests, cli: 30 tests). Tests include unit, subprocess integration, and end-to-end levels. JSON fixtures test 3 flexibility scenarios (skip-enrichment, with-research, with-clarification). This is a model for the rest of the project.

3. **Comprehensive ADR discipline**: 7 ADRs document key decisions with Context/Decision/Rationale/Consequences structure. ADR index is current and maintained. ADRs cover multi-agent architecture (001), Claude Code native integration (002), brownfield-first design (003), skill-augmented agents (004), decoupled agents (005), RFC 2119 auto-invocation (006), and DAG-first infrastructure (007).

4. **Clean skill taxonomy**: 25 skills in 9 categories with consistent kebab-case naming and category prefixes (analysis-, authoring-, patterns-, validation-, etc.). Progressive disclosure via bundled reference files is the actual pattern in practice.

5. **Conventional commits discipline**: Last 20 commits all follow `type(scope): description` format. Types used: feat, fix, docs, refactor, chore. Scopes correctly identify affected areas.

6. **Pydantic-first entity modeling with frozen immutability**: All domain entities use frozen Pydantic models with model validators for type-status coherence (e.g., `validate_type_status` ensures a task node cannot have gate statuses). Status updates create new instances rather than mutating existing ones.

7. **Well-documented DAG infrastructure**: The `humaninloop_brain/README.md` is comprehensive (244 lines) covering architecture, CLI reference, core concepts, flexibility scenarios, validation steps, Python API, and project structure. The 7 architecture synthesis documents provide deep design context.

### Inconsistencies Found

| Area | Finding | Severity | Location |
|------|---------|----------|----------|
| SKILL.md line limits | 18 of 25 SKILL.md files exceed 200-line limit | high | See table below |
| No CI/CD | Constitution references CI-automated quality gates but no workflows exist | high | Root directory (no `.github/`) |
| Plugin validators untested | 5 Python validators have no test files | high | `plugins/humaninloop/skills/*/scripts/` |
| Constitution stale | v1.0.0 from 2026-01-13 does not reflect DAG infrastructure, techspec command, ui-designer agent, or grown entity counts | medium | `.humaninloop/memory/constitution.md` |
| specs/ directory missing | CLAUDE.md references `specs/` directory but it does not exist | medium | Root directory |
| Architect report template mismatch | Template is for techspec feasibility reviews, not setup analysis reports | low | `templates/architect-report-template.md` |

#### SKILL.md Line Count Details

| Skill | Lines | Exceeds 200? |
|-------|-------|--------------|
| analysis-codebase | 327 | YES |
| analysis-iterative | 210 | YES |
| analysis-screenshot | 393 | YES |
| analysis-specifications | 159 | No |
| authoring-constitution | 323 | YES |
| authoring-design-system | 305 | YES |
| authoring-requirements | 206 | YES |
| authoring-roadmap | 300 | YES |
| authoring-technical-requirements | 194 | No |
| authoring-user-stories | 180 | No |
| brownfield-constitution | 192 | No |
| dag-operations | 64 | No |
| patterns-api-contracts | 262 | YES |
| patterns-entity-modeling | 287 | YES |
| patterns-flow-mapping | 398 | YES |
| patterns-interface-design | 240 | YES |
| patterns-technical-decisions | 177 | No |
| patterns-vertical-tdd | 319 | YES |
| syncing-claude-md | 272 | YES |
| testing-end-user | 231 | YES |
| using-git-worktrees | 328 | YES |
| using-github-issues | 263 | YES |
| validation-constitution | 201 | YES |
| validation-plan-artifacts | 197 | No |
| validation-task-artifacts | 155 | No |

**Summary**: 18 of 25 skills (72%) exceed the 200-line limit. The actual effective pattern is "progressive disclosure via SKILL.md plus bundled reference files" rather than a strict 200-line limit on SKILL.md itself. The constitution should reflect actual practice.

### Essential Floor Status

| Category | Status | Evidence |
|----------|--------|----------|
| Security | partial | `.gitignore` covers `.env`, `*.pem`; no hardcoded secrets found; no secret scanning (CI absent) |
| Testing | present | humaninloop_brain: 190 tests, 98% coverage; plugin validators: 5 scripts with NO tests |
| Error Handling | present | Structured JSON output in all validators and CLI; explicit exit codes; custom exceptions |
| Observability | partial | JSON to stdout; `jq`-parseable; no structured logging; no correlation IDs |

#### Security Assessment Details

- **Auth at boundaries**: N/A -- Plugin marketplace; authentication handled by Claude Code runtime. Appropriate for project type.
- **Secrets from env**: partial -- `.gitignore` excludes `.env`, `.env.local`, `.env.*.local`, `*.pem`. No `.env.example` exists. No `git secrets` or secret scanning configured.
- **Input validation**: present -- Python validators validate file paths. Shell scripts validate argument counts. Pydantic models validate all inputs with model validators. hil-dag CLI validates subcommand arguments via argparse.
- **Secret scanning**: absent -- No CI, no pre-commit hooks, no automated scanning.

#### Testing Assessment Details

- **Test framework configured**: present -- pytest 8.x in `humaninloop_brain/pyproject.toml`. Coverage configured with `[tool.coverage.run]` and `[tool.coverage.report]`.
- **Test files present (humaninloop_brain)**: present -- 190 tests in 17 files across 5 directories. Fixtures: 8 JSON files. Test types: unit, subprocess, E2E.
- **Test coverage (humaninloop_brain)**: **98%** (609 statements, 13 misses). Misses are in CLI error paths (`main.py` lines 185-186, 194-195, 267-269, 273) and validator edge cases.
- **Plugin validator tests**: **absent** -- None of the 5 plugin validator scripts (`validate-requirements.py`, `validate-user-stories.py`, `validate-openapi.py`, `validate-model.py`, `check-artifacts.py`) have test files. This was GAP-001 in the original constitution and remains unaddressed.
- **CI runs tests**: **absent** -- No `.github/workflows/` directory exists. All testing is manual.

#### Error Handling Assessment Details

- **Explicit error types**: present -- `FrozenPassError` custom exception. `ValueError` with descriptive messages. JSON error structure in CLI (`{"status": "error", "message": "..."}`).
- **Context preservation**: present -- `ValidationViolation` includes `code`, `severity`, `message`, plus optional `node_id` and `edge_id`. Error messages include specific IDs and constraint details.
- **Appropriate exit codes**: present -- CLI: 0=success, 1=validation failure, 2=unexpected error. Validators: 0=success, 1=failure. Shell: `set -e` with stderr messages.

#### Observability Assessment Details

- **Structured output**: present -- All validators and CLI produce JSON to stdout. `jq`-parseable. Consistent `checks`/`summary` structure.
- **Correlation IDs**: absent -- No correlation mechanism. Not critical for CLI tools but relevant for DAG pass tracing.
- **No PII in output**: present -- Output contains only structural data (node IDs, edge IDs, violation codes).
- **Structured logging framework**: absent -- No logging library. Print-based output only.

### Recommended Constitution Focus

Based on this analysis, the new constitution should:

1. **Codify the structured JSON output pattern as a formal principle**: The `{"checks": [...], "summary": {"total": N, "passed": M, "failed": K}}` pattern is the project's strongest emergent convention. It is used by both legacy plugin validators and the new humaninloop_brain CLI.

2. **Establish dual testing standards**: (a) humaninloop_brain at 98% coverage with blocking CI gate, and (b) plugin validators requiring tests (currently absent) with a coverage ratchet.

3. **Reframe the skill structure principle**: Replace the 200-line SKILL.md limit (violated by 72% of skills) with a principle about progressive disclosure -- SKILL.md as entry point, bundled reference files for detail.

4. **Add CI/CD as a priority gap**: No GitHub Actions workflows exist. Constitution should mandate CI and track as critical gap.

5. **Codify the DAG-first architecture**: ADR-007 establishes the approach. Constitution should formalize the separation of concerns -- deterministic Python for graph operations, LLM judgment in agents.

6. **Preserve conventional commits and ADR discipline**: Both are well-established and consistently followed.

7. **Acknowledge two Python codebases**: Constitution should distinguish between humaninloop_brain (proper Python package, uv-managed, tested) and plugin validator scripts (legacy, untested, standalone).

---

## Appendix: Detection Method

| Aspect | Method Used |
|--------|-------------|
| Tech Stack | Manual inspection (`detect-stack.sh` reports "unknown" for this project type) |
| Architecture | Directory pattern matching, `plugin.json` inspection, ADR review |
| Entities | Pydantic model inspection in `humaninloop_brain/src/`, plugin file enumeration |
| Conventions | File sampling, commit history analysis (`git log --oneline -20`), CONTRIBUTING.md review |
| Coverage | `pytest --cov` executed against `humaninloop_brain/tests/` (190 passed, 98% coverage) |
| Essential Floor | File existence checks, code pattern inspection, `.gitignore` review |
| Governance | Direct reading of constitution, CLAUDE.md, CONTRIBUTING.md, RELEASES.md, all 7 ADRs |
