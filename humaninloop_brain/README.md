# humaninloop_brain

Deterministic DAG infrastructure for the humaninloop plugin's DAG-first execution architecture. All graph operations, validation, and lifecycle management that **can** be deterministic live here. LLM judgment stays in the agents.

## Architecture

```
User invokes command (goal declaration)
        |
Supervisor reads catalog + invariants + history
        |
DAG Assembler calls hil-dag CLI  <-- this package
        |
Supervisor executes DAG via specialist subagents
```

The package provides five layers:

| Layer | Module | Purpose |
|-------|--------|---------|
| **Entities** | `entities/` | Pydantic models for nodes, edges, DAG passes, catalogs, validation results |
| **Graph** | `graph/` | NetworkX-backed loader, subgraph views, topological sort, acyclicity guard, edge inference |
| **Validators** | `validators/` | 9-step structural validator, invariant checker, contract checker |
| **Lifecycle** | `passes/` | Pass creation, node assembly, status updates, freeze, save/load |
| **CLI** | `cli/` | `hil-dag` command with 7 subcommands producing JSON output |

## Quick Start

```bash
cd humaninloop_brain
uv sync
uv run pytest          # 262 tests, ~98% coverage
uv run hil-dag --help
```

## CLI Reference

All commands output JSON to stdout and use exit codes: `0` = success, `1` = validation failure, `2` = unexpected error.

### Create a new DAG pass

```bash
hil-dag create <workflow-id> --pass <N> --output <path>
```

```json
{"status": "success", "dag_path": "...", "pass_number": 1}
```

### Assemble a node from catalog

Adds a node, infers edges from artifact contracts, validates the result.

```bash
hil-dag assemble <dag.json> --catalog <catalog.json> --node <node-id>
```

```json
{"status": "valid", "node_added": "analyst-review", "edges_inferred": 3, "validation": {...}}
```

### Validate a DAG pass

Runs all 9 structural checks plus invariant and contract verification.

```bash
hil-dag validate <dag.json> --catalog <catalog.json>
```

```json
{"status": "valid", "checks": [...], "summary": {"total": 1, "passed": 1, "failed": 0}}
```

### Topological sort

Returns deterministic (lexicographic) execution order based on depends-on edges.

```bash
hil-dag sort <dag.json>
```

```json
{"order": ["constitution-gate", "analyst-review", "advocate-review"]}
```

### Update node status

```bash
hil-dag status <dag.json> --node <node-id> --status <new-status>
```

```json
{"status": "success", "node_id": "analyst-review", "old_status": "pending", "new_status": "completed"}
```

### Freeze a completed pass

Marks the pass as immutable with outcome metadata.

```bash
hil-dag freeze <dag.json> --outcome completed --detail "advocate-verdict-ready" --rationale "All checks passed"
```

```json
{"status": "success", "pass_frozen": true, "outcome": "completed"}
```

### Validate a node catalog

```bash
hil-dag catalog-validate <catalog.json>
```

## Core Concepts

### Node Types

| Type | Purpose | Statuses |
|------|---------|----------|
| `task` | Work that produces artifacts | pending, in-progress, completed, skipped, halted |
| `gate` | Checkpoint that produces a verdict | pending, in-progress, passed, failed, needs-revision |
| `decision` | Point where input determines the path | pending, decided |
| `milestone` | Completion marker | pending, achieved |

### Edge Types

| Type | Semantics |
|------|-----------|
| `depends-on` | Execution ordering (must form a DAG) |
| `produces` | Artifact flow (source creates what target consumes) |
| `validates` | Review relationship (gate evaluates task output) |
| `constrained-by` | Boundary enforcement |
| `informed-by` | Context flow (not a hard dependency) |

### Node Catalog

A single JSON file per workflow defining available nodes, edge constraints, and system invariants. See `catalogs/specify-catalog.json` for the `/specify` workflow catalog with 7 nodes.

### DAG-Per-Pass

Each workflow iteration produces a new immutable DAG pass. Previous passes are preserved as history with progressive summarization. The Supervisor can assemble genuinely different graphs each pass (e.g., skip enrichment, add research, add clarification).

### System Invariants

| ID | Rule | Enforcement |
|----|------|-------------|
| INV-001 | Task output must pass through gate before milestone | Assembly-time |
| INV-002 | Constitution must exist before spec task nodes | Assembly-time |
| INV-003 | validates edges must originate from gate nodes | Assembly-time |
| INV-004 | Max 5 passes per workflow invocation | Runtime |
| INV-005 | depends-on edges must be acyclic | Assembly-time |

### System Artifacts

`raw-input` and `constitution.md` are always considered available without a producing node.

## Flexibility Scenarios

The package ships with test fixtures demonstrating three assembly variations for `/specify`:

1. **Skip enrichment** (`pass-skip-enrichment.json`): User provided detailed input, constitution-gate -> analyst -> advocate
2. **Add research** (`pass-with-research.json`): Advocate found knowledge gaps, targeted-research -> analyst -> advocate
3. **Human clarification** (`pass-with-clarification.json`): Gaps require user input, human-clarification -> analyst -> advocate

## Structural Validation (9 Steps)

1. Unique node IDs
2. Edge references exist (no dangling)
3. Type-status validity
4. No self-loops
5. No duplicate edges
6. Edge endpoint constraints match catalog
7. Acyclicity on depends-on edges
8. Contract satisfiability (required artifacts produced upstream)
9. System invariant compliance

## Python API

```python
from humaninloop_brain.entities import NodeCatalog, DAGPass
from humaninloop_brain.passes.lifecycle import create_pass, add_node, freeze_pass
from humaninloop_brain.validators.structural import validate_structure
from humaninloop_brain.graph.sort import execution_order

# Load catalog
catalog = NodeCatalog.model_validate_json(Path("catalogs/specify-catalog.json").read_text())

# Create and assemble
dag = create_pass("specify-feature-auth", pass_number=1)
dag, edges = add_node(dag, "constitution-gate", catalog)
dag, edges = add_node(dag, "analyst-review", catalog)
dag, edges = add_node(dag, "advocate-review", catalog)

# Validate and sort
result = validate_structure(dag, catalog)
assert result.valid
order = execution_order(dag)  # ["analyst-review", "advocate-review", "constitution-gate"]
```

## Project Structure

```
humaninloop_brain/
├── pyproject.toml
├── catalogs/
│   └── specify-catalog.json
├── src/humaninloop_brain/
│   ├── entities/          # Pydantic models
│   │   ├── enums.py       # NodeType, EdgeType, status enums
│   │   ├── nodes.py       # GraphNode, NodeContract, ArtifactConsumption
│   │   ├── edges.py       # Edge
│   │   ├── dag_pass.py    # DAGPass, ExecutionTraceEntry, HistoryContext
│   │   ├── catalog.py     # NodeCatalog, CatalogNodeDefinition, SystemInvariant
│   │   └── validation.py  # ValidationResult, ValidationViolation
│   ├── graph/             # NetworkX operations
│   │   ├── loader.py      # load_graph() -> MultiDiGraph
│   │   ├── views.py       # Subgraph views per edge type
│   │   ├── sort.py        # Lexicographic topological sort
│   │   ├── guard.py       # Acyclicity check
│   │   └── inference.py   # Edge inference from contracts
│   ├── validators/        # Validation logic
│   │   ├── structural.py  # 9-step structural validator
│   │   ├── invariants.py  # Assembly-time invariant checker
│   │   └── contracts.py   # Artifact contract checker
│   ├── passes/
│   │   └── lifecycle.py   # Pass lifecycle management
│   └── cli/
│       └── main.py        # hil-dag CLI entry point
└── tests/
    ├── fixtures/          # 8 JSON test fixtures
    ├── test_entities/     # 81 tests
    ├── test_graph/        # 32 tests
    ├── test_validators/   # 30 tests
    ├── test_passes/       # 17 tests
    └── test_cli/          # 102 tests (unit + subprocess + E2E)
```

## Related

- **ADR-007**: [DAG-First Infrastructure](../docs/decisions/007-dag-first-infrastructure.md)
- **Architecture docs**: `docs/architecture/dag-*.md` (5 synthesis documents)
- **Context harness**: [human-in-loop-context-harness](https://github.com/deepeshBodh/human-in-loop-context-harness) (patterns borrowed from)
- **Plugin skill**: `plugins/humaninloop/skills/dag-operations/` (shell wrappers for agents)
