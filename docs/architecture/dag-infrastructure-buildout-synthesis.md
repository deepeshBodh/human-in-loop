# DAG Infrastructure Build-out — Analysis Synthesis

## Problem Statement

The DAG-first execution architecture (defined across 5 synthesis documents) requires a Python infrastructure layer before any workflow can migrate. The plugin ecosystem alone cannot support the deterministic operations needed — graph validation, invariant checking, topological sort, edge inference, schema enforcement. These operations must be testable with pytest, not dependent on LLM judgment. A standalone Python package in the same repo provides the foundation that DAG-ops agents (State Briefer, DAG Assembler) invoke through CLI entry points exposed as plugin skills.

## Context & Constraints

- **Plugin format**: Commands, agents, and skills are markdown files. The Python infrastructure is a new layer that the plugin invokes but does not contain.
- **Context harness as reference**: The `human-in-loop-context-harness` repo has battle-tested implementations (Pydantic entities, NetworkX graph loading, structural validation, subgraph views, DAG guards, topological sort). These are patterns to learn from, not constraints to adopt. The plugin domain has different needs (immutable per-pass DAGs, node contracts, agent assignments) that may diverge from context harness abstractions.
- **Deterministic > LLM judgment**: Every operation that CAN be deterministic SHOULD be deterministic. Push validation, graph operations, edge inference, and schema enforcement into testable Python. The LLM (DAG Assembler) handles judgment-heavy work (NL prompt construction, report parsing). This maximizes the testable surface area and minimizes "LLM did something weird" debugging.
- **UV for dependency management**: Users install the Python package and its dependencies (Pydantic, NetworkX) via UV.
- **DAG Assembler is the consumer**: The DAG Assembler agent invokes CLI entry points as plugin skills. The Python package exposes commands like `python -m humaninloop_brain validate pass-001.json` that return structured JSON.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Package location | Standalone project in same repo, not inside the plugin directory | Confident | Plugin ecosystem can't support all requirements. Standalone package with proper Python tooling (pyproject.toml, UV, pytest). |
| Package name | `humaninloop_brain` | Confident | User's choice. |
| Context harness relationship | Reference only — borrow patterns, not constrained by its abstractions | Confident | Plugin domain has different needs (immutable passes, contracts, agent assignments). Context harness patterns inform but don't dictate. |
| Integration model | CLI entry points called by DAG Assembler via plugin skills (scripts) | Confident | DAG Assembler invokes deterministic operations through shell commands. Structured JSON in, structured JSON out. |
| Design principle | Maximize deterministic testable surface, minimize LLM judgment surface | Confident | Operations that can be deterministic (validation, graph ops, edge inference) belong in pytest-testable Python. LLM handles judgment (prompt construction, report parsing). |
| Build-out layering | 4 layers bottom-up: entities → graph ops → validators → pass lifecycle + CLI | Confident | Natural dependency chain. Each layer is independently testable before moving to the next. |

## Scope

### Layer 1: Entities + Catalog Loader
- **Pydantic models**: DAGPass, GraphNode, Edge, Contract, ExecutionTraceEntry, PassMetadata, ValidationResult, ValidationViolation
- **JSON Schema**: Generated from Pydantic models for external validation
- **Catalog loader**: Read and validate node catalog JSON against schema

### Layer 2: Graph Loader + Operations
- **Graph loader**: DAG pass JSON → NetworkX MultiDiGraph with node/edge attributes
- **Subgraph views**: Filter by edge type (depends_on, produces, validates, constrained_by, informed_by)
- **Topological sort**: Deterministic execution ordering on depends-on edges
- **DAG guard**: Acyclicity check on depends-on edges (other edge types may cycle)
- **Edge inference**: Match consumes/produces contracts between nodes to infer edges automatically

### Layer 3: Validators
- **Structural validator**: Self-loops, duplicate edges, dangling references, endpoint type constraints, cycle detection
- **Invariant checker**: Load invariants from catalog, validate assembled DAG against them
- **Contract satisfiability**: Verify every consumed artifact is produced by an upstream node

### Layer 4: Pass Lifecycle + CLI
- **Pass management**: Create new pass, update node status, freeze pass as immutable JSON
- **CLI interface**: Entry points for DAG Assembler (assemble, validate, parse, freeze)
- **Structured I/O**: JSON input via stdin/args, JSON output to stdout

## Risks

- **Scope creep into LLM territory**: The boundary between "deterministic operation" and "judgment call" may blur. Edge inference from contracts is deterministic, but deciding WHICH node to add next is judgment. The CLI must stay on the deterministic side. If the package starts encoding assembly strategy, it recreates the rigidity the architecture is trying to escape.
- **CLI invocation overhead**: Each DAG Assembler action spawns a Python process. For a 3-node pass with 2 DAG Assembler calls per node, that's 6+ process spawns. UV and Python startup time could add latency. Mitigation: measure actual latency during PoC before optimizing.
- **Schema evolution during build-out**: The Pydantic models will evolve as the PoC reveals gaps. Early layers (entities) may need revision when later layers (validators, pass lifecycle) surface requirements. Mitigation: schema_version field from day one; accept that Layer 1 entities will get refined as Layers 2-4 are built.

## Open Questions

- **Plugin skill format for scripts**: How do script-based skills work in the plugin ecosystem? Is there an existing pattern, or does this need a new skill category?
- **UV workspace vs. standalone**: Should `humaninloop_brain` be a UV workspace member alongside the plugin, or a fully standalone package with its own pyproject.toml?
- **Test data**: The PoC needs realistic test fixtures (catalog JSON, DAG pass JSON for all 3 flexibility scenarios). Should these be hand-written first or generated from the Pydantic models?
- **Error output format**: When CLI commands fail (invariant violation, missing artifact), what's the exact JSON error schema? Should it align with the plugin's existing structured JSON output pattern (`checks`, `summary`, `issues` fields)?

## Recommended Next Steps

1. **Initialize the `humaninloop_brain` package**: Create `humaninloop_brain/` at repo root with `pyproject.toml` (UV-managed), Pydantic and NetworkX as dependencies, pytest configuration, and empty module structure matching the 4 layers.

2. **Build Layer 1 — Pydantic entities**: Define all core models (DAGPass, GraphNode, Edge, Contract, ExecutionTraceEntry, PassMetadata, ValidationResult, ValidationViolation) with type-status validation. Write the specify catalog JSON as the first test fixture. Target: all models serialize/deserialize correctly, type-status constraints enforced.

3. **Build Layer 2 — Graph loader + operations**: Implement graph loading into NetworkX, 5 subgraph views, topological sort, DAG guard, and edge inference. Test against hand-written DAG pass fixtures for all 3 flexibility scenarios from the supervisor design synthesis.

4. **Build Layer 3 — Validators**: Implement structural validator, invariant checker, and contract satisfiability checker. Test against both valid DAGs and deliberately broken DAGs (missing edges, violated invariants, unsatisfied contracts).

5. **Build Layer 4 — Pass lifecycle + CLI**: Implement pass creation/update/freeze and expose all operations as CLI entry points with structured JSON I/O. Validate end-to-end: CLI command → Python operation → JSON output.

6. **Integration test with plugin skill**: Create one plugin skill (script) that invokes a CLI entry point. Verify the DAG Assembler agent can call it and parse the output. This proves the integration model before building all skills.
